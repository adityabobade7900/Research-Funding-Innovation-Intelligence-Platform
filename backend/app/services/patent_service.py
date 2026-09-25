from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patent import Patent, profile_patents
from app.models.profile import Profile
from app.schemas.patent import PatentCreate, PatentUpdate, normalize_patent_number
from app.services.profile_service import ProfileService
from app.services.providers.patent_base import NormalizedPatent
from app.services.providers.patent_providers import patent_provider_service
from app.services.providers.base import (
    ProviderException,
    ProviderTimeoutException,
    ProviderRateLimitException,
    ProviderNotFoundException,
)
from app.core.exceptions import (
    EntityNotFoundException,
    DuplicateEntityException,
    PermissionDeniedException,
    CustomAPIException
)


class PatentService:
    @staticmethod
    async def create_patent(
        user_id: int,
        patent_in: PatentCreate,
        db: AsyncSession
    ) -> Patent:
        """Creates a new patent record and links it to the requesting researcher's profile."""
        profile = await ProfileService.get_or_create_profile(user_id=user_id, db=db)
        clean_num = normalize_patent_number(patent_in.patent_number)
        if not clean_num:
            raise CustomAPIException(status_code=400, code="INVALID_PATENT_NUMBER", message="Patent number cannot be empty")

        # Duplicate check
        dup_res = await db.execute(
            select(Patent).where(func.lower(Patent.patent_number) == clean_num.lower())
        )
        if dup_res.scalar_one_or_none():
            raise DuplicateEntityException(f"Patent with identifier '{clean_num}' already exists")

        new_patent = Patent(
            patent_number=clean_num,
            title=patent_in.title.strip(),
            abstract=patent_in.abstract,
            assignee=patent_in.assignee,
            inventors=patent_in.inventors,
            filing_date=patent_in.filing_date,
            publication_date=patent_in.publication_date,
            patent_classification=patent_in.patent_classification,
            technology_domain=patent_in.technology_domain,
            citation_count=patent_in.citation_count,
            source=patent_in.source,
            external_id=patent_in.external_id,
            url=patent_in.url,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(new_patent)
        await db.flush()

        # Link to profile
        await db.execute(
            profile_patents.insert().values(
                profile_id=profile.id,
                patent_id=new_patent.id,
                created_at=datetime.now(timezone.utc)
            )
        )
        await db.flush()
        return new_patent

    @staticmethod
    async def get_patent(patent_id: int, db: AsyncSession) -> Patent:
        """Retrieves a patent by ID."""
        res = await db.execute(select(Patent).where(Patent.id == patent_id))
        pat = res.scalar_one_or_none()
        if not pat:
            raise EntityNotFoundException(f"Patent with ID {patent_id} was not found")
        return pat

    @staticmethod
    async def list_patents(
        search_query: Optional[str] = None,
        domain: Optional[str] = None,
        classification: Optional[str] = None,
        assignee: Optional[str] = None,
        year: Optional[int] = None,
        profile_id: Optional[int] = None,
        limit: int = 20,
        offset: int = 0,
        db: AsyncSession = None
    ) -> Tuple[List[Patent], int]:
        """Lists and filters indexed patents with pagination."""
        query = select(Patent)

        if profile_id is not None:
            query = query.join(profile_patents, Patent.id == profile_patents.c.patent_id)\
                         .where(profile_patents.c.profile_id == profile_id)

        conditions = []
        if search_query:
            sq = f"%{search_query.strip().lower()}%"
            conditions.append(
                or_(
                    func.lower(Patent.title).like(sq),
                    func.lower(Patent.abstract).like(sq),
                    func.lower(Patent.patent_number).like(sq),
                    func.lower(Patent.assignee).like(sq),
                    func.lower(Patent.inventors).like(sq)
                )
            )

        if domain:
            conditions.append(func.lower(Patent.technology_domain) == domain.strip().lower())

        if classification:
            cq = f"%{classification.strip().lower()}%"
            conditions.append(func.lower(Patent.patent_classification).like(cq))

        if assignee:
            aq = f"%{assignee.strip().lower()}%"
            conditions.append(func.lower(Patent.assignee).like(aq))

        if year:
            conditions.append(
                or_(
                    func.extract("year", Patent.publication_date) == year,
                    func.extract("year", Patent.filing_date) == year
                )
            )

        if conditions:
            query = query.where(and_(*conditions))

        # Total count
        count_subquery = query.with_only_columns(func.count(Patent.id)).order_by(None)
        total_res = await db.execute(count_subquery)
        total = total_res.scalar() or 0

        # Fetch page ordered by citation count desc, then date desc
        query = query.order_by(desc(Patent.citation_count), desc(Patent.publication_date)).offset(offset).limit(limit)
        res = await db.execute(query)
        items = list(res.scalars().all())

        return items, total

    @staticmethod
    async def update_patent(
        patent_id: int,
        user_id: int,
        is_admin: bool,
        update_in: PatentUpdate,
        db: AsyncSession
    ) -> Patent:
        """Updates patent details with ownership/admin authorization."""
        patent = await PatentService.get_patent(patent_id=patent_id, db=db)
        profile = await ProfileService.get_or_create_profile(user_id=user_id, db=db)

        if not is_admin:
            assoc_res = await db.execute(
                select(profile_patents).where(
                    and_(
                        profile_patents.c.profile_id == profile.id,
                        profile_patents.c.patent_id == patent.id
                    )
                )
            )
            if not assoc_res.first():
                raise PermissionDeniedException("You do not have permission to update this patent")

        update_dict = update_in.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(patent, field, value)

        patent.updated_at = datetime.now(timezone.utc)
        await db.flush()
        return patent

    @staticmethod
    async def delete_patent(
        patent_id: int,
        user_id: int,
        is_admin: bool,
        db: AsyncSession
    ) -> None:
        """Dissociates or deletes patent with ownership/admin authorization."""
        patent = await PatentService.get_patent(patent_id=patent_id, db=db)
        profile = await ProfileService.get_or_create_profile(user_id=user_id, db=db)

        if not is_admin:
            assoc_res = await db.execute(
                select(profile_patents).where(
                    and_(
                        profile_patents.c.profile_id == profile.id,
                        profile_patents.c.patent_id == patent.id
                    )
                )
            )
            if not assoc_res.first():
                raise PermissionDeniedException("You do not have permission to modify this patent")

            # Dissociate profile
            await db.execute(
                profile_patents.delete().where(
                    and_(
                        profile_patents.c.profile_id == profile.id,
                        profile_patents.c.patent_id == patent.id
                    )
                )
            )
        else:
            await db.delete(patent)

        await db.flush()

    @staticmethod
    async def ingest_patent(
        user_id: int,
        patent_number: str,
        provider_name: Optional[str] = None,
        db: AsyncSession = None
    ) -> Patent:
        """
        Controlled patent ingestion from patent data providers (Mock, Google Patents, Lens, USPTO).
        Deduplicates against existing database records and associates with user profile.
        """
        profile = await ProfileService.get_or_create_profile(user_id=user_id, db=db)
        clean_num = normalize_patent_number(patent_number)
        if not clean_num:
            raise CustomAPIException(status_code=400, code="INVALID_PATENT_NUMBER", message="Patent number cannot be empty")

        try:
            norm_pat = await patent_provider_service.fetch_by_number(
                patent_number=clean_num,
                preferred_provider=provider_name
            )
        except (ProviderTimeoutException, ProviderRateLimitException, ProviderNotFoundException) as pe:
            raise CustomAPIException(status_code=pe.status_code or 502, code="PROVIDER_ERROR", message=pe.message)
        except ProviderException as pe:
            raise CustomAPIException(status_code=pe.status_code or 502, code="PROVIDER_ERROR", message=pe.message)

        if not norm_pat:
            raise EntityNotFoundException(f"Patent with identifier '{clean_num}' was not found in patent providers")

        # Check existing by patent_number
        existing_res = await db.execute(
            select(Patent).where(func.lower(Patent.patent_number) == clean_num.lower())
        )
        existing_pat = existing_res.scalar_one_or_none()

        if existing_pat:
            # Metadata enrichment
            if norm_pat.citation_count > existing_pat.citation_count:
                existing_pat.citation_count = norm_pat.citation_count
            if not existing_pat.abstract and norm_pat.abstract:
                existing_pat.abstract = norm_pat.abstract
            if not existing_pat.assignee and norm_pat.assignee:
                existing_pat.assignee = norm_pat.assignee
            if not existing_pat.url and norm_pat.url:
                existing_pat.url = norm_pat.url

            # Link to profile if missing
            assoc_res = await db.execute(
                select(profile_patents).where(
                    and_(
                        profile_patents.c.profile_id == profile.id,
                        profile_patents.c.patent_id == existing_pat.id
                    )
                )
            )
            if not assoc_res.first():
                await db.execute(
                    profile_patents.insert().values(
                        profile_id=profile.id,
                        patent_id=existing_pat.id,
                        created_at=datetime.now(timezone.utc)
                    )
                )
            await db.flush()
            return existing_pat

        # Create new patent
        new_pat = Patent(
            patent_number=norm_pat.patent_number,
            title=norm_pat.title,
            abstract=norm_pat.abstract,
            assignee=norm_pat.assignee,
            inventors=norm_pat.inventors,
            filing_date=norm_pat.filing_date,
            publication_date=norm_pat.publication_date,
            patent_classification=norm_pat.patent_classification,
            technology_domain=norm_pat.technology_domain,
            citation_count=norm_pat.citation_count,
            source=norm_pat.source,
            external_id=norm_pat.external_id,
            url=norm_pat.url,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(new_pat)
        await db.flush()

        # Link to profile
        await db.execute(
            profile_patents.insert().values(
                profile_id=profile.id,
                patent_id=new_pat.id,
                created_at=datetime.now(timezone.utc)
            )
        )
        await db.flush()
        return new_pat

    @staticmethod
    async def bookmark_patent(
        patent_id: int,
        user_id: int,
        db: AsyncSession
    ) -> bool:
        """Links an existing patent to the requesting user's researcher profile."""
        patent = await PatentService.get_patent(patent_id=patent_id, db=db)
        profile = await ProfileService.get_or_create_profile(user_id=user_id, db=db)

        # Check existing linkage
        assoc_res = await db.execute(
            select(profile_patents).where(
                and_(
                    profile_patents.c.profile_id == profile.id,
                    profile_patents.c.patent_id == patent.id
                )
            )
        )
        if not assoc_res.first():
            await db.execute(
                profile_patents.insert().values(
                    profile_id=profile.id,
                    patent_id=patent.id,
                    created_at=datetime.now(timezone.utc)
                )
            )
            await db.flush()
        return True

    @staticmethod
    async def remove_bookmark(
        patent_id: int,
        user_id: int,
        db: AsyncSession
    ) -> bool:
        """Removes patent linkage from the requesting user's researcher profile."""
        patent = await PatentService.get_patent(patent_id=patent_id, db=db)
        profile = await ProfileService.get_or_create_profile(user_id=user_id, db=db)

        await db.execute(
            profile_patents.delete().where(
                and_(
                    profile_patents.c.profile_id == profile.id,
                    profile_patents.c.patent_id == patent.id
                )
            )
        )
        await db.flush()
        return True

    @staticmethod
    async def is_patent_bookmarked(
        patent_id: int,
        user_id: int,
        db: AsyncSession
    ) -> bool:
        """Checks if a patent is linked to the user's profile."""
        profile = await ProfileService.get_or_create_profile(user_id=user_id, db=db)
        assoc_res = await db.execute(
            select(profile_patents).where(
                and_(
                    profile_patents.c.profile_id == profile.id,
                    profile_patents.c.patent_id == patent_id
                )
            )
        )
        return assoc_res.first() is not None
