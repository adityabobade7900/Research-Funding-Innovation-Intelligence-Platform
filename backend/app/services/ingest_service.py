from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.publication import Publication, PublicationKeyword, profile_publications
from app.models.profile import Profile
from app.schemas.publication import PublicationIngestRequest
from app.services.providers.base import (
    NormalizedPublication,
    normalize_doi,
    ProviderException,
    ProviderTimeoutException,
    ProviderRateLimitException,
    ProviderNotFoundException,
)
from app.services.providers.service import research_provider_service
from app.services.profile_service import ProfileService
from app.services.publication_service import PublicationService
from app.core.exceptions import (
    EntityNotFoundException,
    CustomAPIException,
    PermissionDeniedException
)


class IngestService:
    @staticmethod
    def validate_normalized_publication(norm: NormalizedPublication) -> NormalizedPublication:
        """Validates normalized publication fields before database persistence."""
        if not norm.title or len(norm.title.strip()) < 2:
            raise CustomAPIException(
                status_code=422,
                code="VALIDATION_ERROR",
                message="Normalized publication title is missing or too short"
            )
        if not norm.authors or len(norm.authors.strip()) < 1:
            norm.authors = "Unknown Author"

        if norm.citation_count < 0:
            norm.citation_count = 0

        return norm

    @staticmethod
    async def persist_normalized_publication(
        user_id: int,
        norm_pub: NormalizedPublication,
        is_primary_author: bool,
        db: AsyncSession
    ) -> Publication:
        """
        Deduplicates against existing database records (by DOI or source+external_id),
        updates richer metadata if available, persists new entries, and links to user profile.
        """
        # Ensure user's profile exists
        profile = await ProfileService.get_or_create_profile(user_id, db)

        # Validate
        norm_pub = IngestService.validate_normalized_publication(norm_pub)

        # 1. Deduplication by DOI
        existing_pub: Optional[Publication] = None
        if norm_pub.doi:
            clean_doi = normalize_doi(norm_pub.doi)
            doi_res = await db.execute(
                select(Publication).where(func.lower(Publication.doi) == clean_doi.lower())
            )
            existing_pub = doi_res.scalar_one_or_none()

        # 2. Deduplication by source + external_id
        if not existing_pub and norm_pub.external_id and norm_pub.source != "manual":
            ext_res = await db.execute(
                select(Publication).where(
                    and_(
                        Publication.source == norm_pub.source,
                        Publication.external_id == norm_pub.external_id
                    )
                )
            )
            existing_pub = ext_res.scalar_one_or_none()

        if existing_pub:
            # Metadata enrichment
            if norm_pub.citation_count > existing_pub.citation_count:
                existing_pub.citation_count = norm_pub.citation_count
            if not existing_pub.abstract and norm_pub.abstract:
                existing_pub.abstract = norm_pub.abstract
            if not existing_pub.venue and norm_pub.venue:
                existing_pub.venue = norm_pub.venue
            if not existing_pub.primary_domain and norm_pub.primary_domain:
                existing_pub.primary_domain = norm_pub.primary_domain
            if not existing_pub.url and norm_pub.url:
                existing_pub.url = norm_pub.url

            # Idempotent profile linkage
            assoc_res = await db.execute(
                select(profile_publications).where(
                    and_(
                        profile_publications.c.profile_id == profile.id,
                        profile_publications.c.publication_id == existing_pub.id
                    )
                )
            )
            if not assoc_res.first():
                await db.execute(
                    profile_publications.insert().values(
                        profile_id=profile.id,
                        publication_id=existing_pub.id,
                        is_primary_author=is_primary_author,
                        created_at=datetime.now(timezone.utc)
                    )
                )

            await db.flush()
            return await PublicationService.get_publication(existing_pub.id, db)

        # 3. Create new publication
        new_pub = Publication(
            title=norm_pub.title.strip(),
            authors=norm_pub.authors.strip(),
            abstract=norm_pub.abstract,
            publication_date=norm_pub.publication_date,
            venue=norm_pub.venue,
            doi=norm_pub.doi,
            citation_count=norm_pub.citation_count,
            primary_domain=norm_pub.primary_domain,
            source=norm_pub.source,
            external_id=norm_pub.external_id,
            url=norm_pub.url,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(new_pub)
        await db.flush()

        # Add Keywords
        if norm_pub.keywords:
            seen = set()
            for kw in norm_pub.keywords:
                clean_kw = kw.strip()
                if clean_kw and clean_kw.lower() not in seen:
                    seen.add(clean_kw.lower())
                    db.add(PublicationKeyword(publication_id=new_pub.id, keyword=clean_kw))

        # Associate with profile
        await db.execute(
            profile_publications.insert().values(
                profile_id=profile.id,
                publication_id=new_pub.id,
                is_primary_author=is_primary_author,
                created_at=datetime.now(timezone.utc)
            )
        )

        await db.flush()
        return await PublicationService.get_publication(new_pub.id, db)

    @staticmethod
    async def ingest_publications(
        user_id: int,
        request: PublicationIngestRequest,
        db: AsyncSession
    ) -> Tuple[List[Publication], str]:
        """
        Executes controlled ingestion from upstream research data providers (OpenAlex, Crossref, Semantic Scholar, Mock)
        and associates ingested publications with the requesting user's research profile.
        """
        results: List[Publication] = []

        try:
            # Case 1: Ingest single DOI
            if request.doi:
                clean_doi = normalize_doi(request.doi)
                if not clean_doi:
                    raise CustomAPIException(
                        status_code=400,
                        code="INVALID_DOI",
                        message=f"Provided DOI '{request.doi}' is invalid"
                    )

                norm_pub = await research_provider_service.fetch_by_doi(
                    doi=clean_doi,
                    preferred_provider=request.provider
                )
                if not norm_pub:
                    raise EntityNotFoundException(
                        message=f"Publication with DOI '{clean_doi}' could not be resolved from external providers"
                    )

                pub = await IngestService.persist_normalized_publication(
                    user_id=user_id,
                    norm_pub=norm_pub,
                    is_primary_author=True,
                    db=db
                )
                return [pub], "Publication ingested and linked to profile successfully"

            # Case 2: Ingest by author identifier
            elif request.author_id:
                provider_name = request.provider or "openalex"
                norm_pubs = await research_provider_service.fetch_author_publications(
                    author_identifier=request.author_id,
                    provider_name=provider_name,
                    limit=request.limit
                )
                if not norm_pubs:
                    return [], f"No publications found for author identifier '{request.author_id}' in {provider_name}"

                for item in norm_pubs:
                    pub = await IngestService.persist_normalized_publication(
                        user_id=user_id,
                        norm_pub=item,
                        is_primary_author=True,
                        db=db
                    )
                    results.append(pub)

                return results, f"Successfully ingested {len(results)} publication(s) for author"

            # Case 3: Ingest by search query
            elif request.query:
                provider_name = request.provider or "openalex"
                norm_pubs = await research_provider_service.search_publications(
                    query=request.query,
                    provider_name=provider_name,
                    limit=request.limit
                )
                if not norm_pubs:
                    return [], f"No publications found matching '{request.query}' in {provider_name}"

                for item in norm_pubs:
                    pub = await IngestService.persist_normalized_publication(
                        user_id=user_id,
                        norm_pub=item,
                        is_primary_author=False,
                        db=db
                    )
                    results.append(pub)

                return results, f"Successfully ingested {len(results)} publication(s) matching search query"

            else:
                raise CustomAPIException(
                    status_code=400,
                    code="INVALID_INGEST_PARAMS",
                    message="Must specify at least one of: 'doi', 'query', or 'author_id'"
                )

        except (ProviderTimeoutException, ProviderRateLimitException, ProviderNotFoundException) as pe:
            raise CustomAPIException(
                status_code=pe.status_code or 502,
                code="PROVIDER_ERROR",
                message=pe.message,
                details={"provider": pe.provider_name}
            )
        except ProviderException as pe:
            raise CustomAPIException(
                status_code=pe.status_code or 502,
                code="PROVIDER_ERROR",
                message=pe.message,
                details={"provider": pe.provider_name}
            )
