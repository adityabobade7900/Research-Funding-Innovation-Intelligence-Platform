from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import select, func, or_, and_, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.publication import Publication, PublicationKeyword, profile_publications
from app.models.profile import Profile
from app.schemas.publication import PublicationCreate, PublicationUpdate
from app.core.exceptions import (
    EntityNotFoundException,
    PermissionDeniedException,
    DuplicateEntityException
)


class PublicationService:
    @staticmethod
    async def create_publication(
        user_id: int,
        pub_in: PublicationCreate,
        db: AsyncSession
    ) -> Publication:
        """
        Creates a new publication or links an existing one (by DOI/external_id),
        and associates it with the researcher's profile.
        """
        # Fetch user's profile
        profile_res = await db.execute(select(Profile).where(Profile.user_id == user_id))
        profile = profile_res.scalar_one_or_none()
        if not profile:
            profile = Profile(user_id=user_id)
            db.add(profile)
            await db.flush()
            await db.refresh(profile)

        # Check for existing publication by DOI or (source, external_id)
        existing_pub: Optional[Publication] = None
        if pub_in.doi:
            doi_res = await db.execute(
                select(Publication)
                .options(selectinload(Publication.keywords), selectinload(Publication.profiles))
                .where(func.lower(Publication.doi) == pub_in.doi.lower())
            )
            existing_pub = doi_res.scalar_one_or_none()

        if not existing_pub and pub_in.external_id and pub_in.source != "manual":
            ext_res = await db.execute(
                select(Publication)
                .options(selectinload(Publication.keywords), selectinload(Publication.profiles))
                .where(
                    and_(
                        Publication.source == pub_in.source,
                        Publication.external_id == pub_in.external_id
                    )
                )
            )
            existing_pub = ext_res.scalar_one_or_none()

        if existing_pub:
            # Check if already associated with this profile
            assoc_res = await db.execute(
                select(profile_publications).where(
                    and_(
                        profile_publications.c.profile_id == profile.id,
                        profile_publications.c.publication_id == existing_pub.id
                    )
                )
            )
            if assoc_res.first():
                raise DuplicateEntityException(
                    message=f"Publication with DOI '{pub_in.doi}' is already in your research profile"
                )

            # Link existing publication to profile
            await db.execute(
                profile_publications.insert().values(
                    profile_id=profile.id,
                    publication_id=existing_pub.id,
                    is_primary_author=pub_in.is_primary_author,
                    created_at=datetime.now(timezone.utc)
                )
            )
            if pub_in.citation_count > existing_pub.citation_count:
                existing_pub.citation_count = pub_in.citation_count
            await db.flush()
            await db.refresh(existing_pub)
            return existing_pub

        # Create new publication
        new_pub = Publication(
            title=pub_in.title,
            authors=pub_in.authors,
            abstract=pub_in.abstract,
            publication_date=pub_in.publication_date,
            venue=pub_in.venue,
            doi=pub_in.doi,
            citation_count=pub_in.citation_count,
            primary_domain=pub_in.primary_domain,
            source=pub_in.source,
            external_id=pub_in.external_id,
            url=pub_in.url,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(new_pub)
        await db.flush()

        # Add Keywords directly
        if pub_in.keywords:
            seen = set()
            for kw in pub_in.keywords:
                clean_kw = kw.strip()
                if clean_kw and clean_kw.lower() not in seen:
                    seen.add(clean_kw.lower())
                    db.add(PublicationKeyword(publication_id=new_pub.id, keyword=clean_kw))

        # Associate with profile
        await db.execute(
            profile_publications.insert().values(
                profile_id=profile.id,
                publication_id=new_pub.id,
                is_primary_author=pub_in.is_primary_author,
                created_at=datetime.now(timezone.utc)
            )
        )

        await db.flush()
        return await PublicationService.get_publication(new_pub.id, db)

    @staticmethod
    async def get_publication(pub_id: int, db: AsyncSession) -> Publication:
        """Retrieves a single publication by ID with pre-loaded keywords and profiles."""
        result = await db.execute(
            select(Publication)
            .options(
                selectinload(Publication.keywords),
                selectinload(Publication.profiles)
            )
            .where(Publication.id == pub_id)
        )
        pub = result.scalar_one_or_none()
        if not pub:
            raise EntityNotFoundException(message=f"Publication with ID {pub_id} not found")
        return pub

    @staticmethod
    async def list_publications(
        search_query: Optional[str] = None,
        domain: Optional[str] = None,
        venue: Optional[str] = None,
        year: Optional[int] = None,
        author: Optional[str] = None,
        profile_id: Optional[int] = None,
        limit: int = 20,
        offset: int = 0,
        db: AsyncSession = None
    ) -> Tuple[List[Publication], int]:
        """Searches and filters publications with pagination support."""
        stmt = select(Publication).options(selectinload(Publication.keywords))
        count_stmt = select(func.count(Publication.id))

        conditions = []

        if profile_id is not None:
            stmt = stmt.join(profile_publications, Publication.id == profile_publications.c.publication_id)
            count_stmt = count_stmt.join(profile_publications, Publication.id == profile_publications.c.publication_id)
            conditions.append(profile_publications.c.profile_id == profile_id)

        if search_query:
            term = f"%{search_query.strip()}%"
            # Search in title, abstract, authors, venue, or keywords
            search_cond = or_(
                Publication.title.ilike(term),
                Publication.abstract.ilike(term),
                Publication.authors.ilike(term),
                Publication.venue.ilike(term)
            )
            conditions.append(search_cond)

        if domain:
            conditions.append(Publication.primary_domain.ilike(f"%{domain.strip()}%"))

        if venue:
            conditions.append(Publication.venue.ilike(f"%{venue.strip()}%"))

        if author:
            conditions.append(Publication.authors.ilike(f"%{author.strip()}%"))

        if year:
            # Match publication_date year
            conditions.append(
                and_(
                    Publication.publication_date >= datetime(year, 1, 1, tzinfo=timezone.utc),
                    Publication.publication_date <= datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
                )
            )

        if conditions:
            stmt = stmt.where(and_(*conditions))
            count_stmt = count_stmt.where(and_(*conditions))

        # Count total matches
        total_res = await db.execute(count_stmt)
        total = total_res.scalar() or 0

        # Execute paginated query ordered by citation count desc, publication_date desc
        stmt = stmt.order_by(Publication.citation_count.desc(), Publication.publication_date.desc().nullslast())
        stmt = stmt.limit(limit).offset(offset)
        res = await db.execute(stmt)
        items = list(res.scalars().all())

        return items, total

    @staticmethod
    async def update_publication(
        pub_id: int,
        user_id: int,
        is_admin: bool,
        update_in: PublicationUpdate,
        db: AsyncSession
    ) -> Publication:
        """Updates publication information with strict ownership/admin enforcement."""
        pub = await PublicationService.get_publication(pub_id, db)

        # Check ownership unless admin
        if not is_admin:
            profile_res = await db.execute(select(Profile).where(Profile.user_id == user_id))
            profile = profile_res.scalar_one_or_none()
            if not profile:
                raise PermissionDeniedException(message="User has no associated profile")

            assoc_res = await db.execute(
                select(profile_publications).where(
                    and_(
                        profile_publications.c.profile_id == profile.id,
                        profile_publications.c.publication_id == pub.id
                    )
                )
            )
            if not assoc_res.first():
                raise PermissionDeniedException(message="You do not have permission to edit this publication")

        # Update scalar fields
        if update_in.title is not None:
            pub.title = update_in.title
        if update_in.authors is not None:
            pub.authors = update_in.authors
        if update_in.abstract is not None:
            pub.abstract = update_in.abstract
        if update_in.publication_date is not None:
            pub.publication_date = update_in.publication_date
        if update_in.venue is not None:
            pub.venue = update_in.venue
        if update_in.doi is not None:
            pub.doi = update_in.doi
        if update_in.citation_count is not None:
            pub.citation_count = update_in.citation_count
        if update_in.primary_domain is not None:
            pub.primary_domain = update_in.primary_domain
        if update_in.source is not None:
            pub.source = update_in.source
        if update_in.external_id is not None:
            pub.external_id = update_in.external_id
        if update_in.url is not None:
            pub.url = update_in.url

        # Update keywords
        if update_in.keywords is not None:
            pub.keywords.clear()
            seen = set()
            for kw in update_in.keywords:
                clean_kw = kw.strip()
                if clean_kw and clean_kw.lower() not in seen:
                    seen.add(clean_kw.lower())
                    pub.keywords.append(
                        PublicationKeyword(publication_id=pub.id, keyword=clean_kw)
                    )

        pub.updated_at = datetime.now(timezone.utc)
        await db.flush()
        await db.refresh(pub)
        return pub

    @staticmethod
    async def delete_publication(
        pub_id: int,
        user_id: int,
        is_admin: bool,
        db: AsyncSession
    ) -> bool:
        """Dissociates a publication from the researcher profile or deletes it if orphaned."""
        pub = await PublicationService.get_publication(pub_id, db)

        profile_res = await db.execute(select(Profile).where(Profile.user_id == user_id))
        profile = profile_res.scalar_one_or_none()

        if not is_admin:
            if not profile:
                raise PermissionDeniedException(message="User has no associated profile")

            assoc_res = await db.execute(
                select(profile_publications).where(
                    and_(
                        profile_publications.c.profile_id == profile.id,
                        profile_publications.c.publication_id == pub.id
                    )
                )
            )
            if not assoc_res.first():
                raise PermissionDeniedException(message="You do not have permission to delete this publication")

        # Check remaining profile associations
        assoc_res = await db.execute(
            select(func.count()).select_from(profile_publications).where(
                profile_publications.c.publication_id == pub.id
            )
        )
        total_assocs = assoc_res.scalar() or 0

        if is_admin or total_assocs <= 1:
            await db.delete(pub)
        else:
            if profile:
                pub.profiles = [p for p in pub.profiles if p.id != profile.id]

        await db.flush()
        return True
