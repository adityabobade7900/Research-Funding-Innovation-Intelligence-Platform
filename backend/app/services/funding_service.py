from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.funding import FundingOpportunity, FundingKeyword, funding_opportunity_domains
from app.models.research_domain import ResearchDomain
from app.schemas.funding import FundingOpportunityCreate, FundingOpportunityUpdate
from app.core.exceptions import (
    EntityNotFoundException,
    DuplicateEntityException,
    PermissionDeniedException,
    CustomAPIException
)


class FundingService:
    @staticmethod
    async def create_opportunity(
        user_id: int,
        opp_in: FundingOpportunityCreate,
        db: AsyncSession
    ) -> FundingOpportunity:
        """Creates a new funding opportunity with domain linking, keywords, and deduplication."""
        # 1. Deduplication by source + external_id
        if opp_in.external_id and opp_in.source != "manual":
            dup_ext = await db.execute(
                select(FundingOpportunity).where(
                    and_(
                        FundingOpportunity.source == opp_in.source,
                        FundingOpportunity.external_id == opp_in.external_id
                    )
                )
            )
            if dup_ext.scalar_one_or_none():
                raise DuplicateEntityException(
                    f"Funding opportunity with external ID '{opp_in.external_id}' from source '{opp_in.source}' already exists"
                )

        # 2. Deduplication by normalized URL
        if opp_in.url:
            clean_url = opp_in.url.strip().lower()
            dup_url = await db.execute(
                select(FundingOpportunity).where(func.lower(FundingOpportunity.url) == clean_url)
            )
            if dup_url.scalar_one_or_none():
                raise DuplicateEntityException(f"Funding opportunity with URL '{opp_in.url}' already exists")

        new_opp = FundingOpportunity(
            title=opp_in.title.strip(),
            funding_agency=opp_in.funding_agency.strip(),
            funding_program=opp_in.funding_program.strip() if opp_in.funding_program else None,
            description=opp_in.description,
            funding_amount=opp_in.funding_amount,
            currency=opp_in.currency.upper() if opp_in.currency else "USD",
            application_deadline=opp_in.application_deadline,
            opportunity_type=opp_in.opportunity_type,
            eligibility_summary=opp_in.eligibility_summary,
            eligible_institutions=opp_in.eligible_institutions,
            geographic_restrictions=opp_in.geographic_restrictions,
            status=opp_in.status.lower() if opp_in.status else "open",
            source=opp_in.source.lower() if opp_in.source else "manual",
            external_id=opp_in.external_id,
            url=opp_in.url,
            created_by_user_id=user_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(new_opp)
        await db.flush()

        # Link Domains
        linked_domain_ids = set(opp_in.domain_ids or [])
        if opp_in.domain_names:
            for d_name in opp_in.domain_names:
                clean_d = d_name.strip()
                if not clean_d:
                    continue
                d_res = await db.execute(
                    select(ResearchDomain).where(func.lower(ResearchDomain.name) == clean_d.lower())
                )
                domain_obj = d_res.scalar_one_or_none()
                if not domain_obj:
                    domain_obj = ResearchDomain(name=clean_d, description=f"{clean_d} research domain")
                    db.add(domain_obj)
                    await db.flush()
                linked_domain_ids.add(domain_obj.id)

        for d_id in linked_domain_ids:
            await db.execute(
                funding_opportunity_domains.insert().values(
                    funding_opportunity_id=new_opp.id,
                    domain_id=d_id
                )
            )

        # Link Keywords
        if opp_in.keywords:
            seen_kw = set()
            for kw in opp_in.keywords:
                clean_kw = kw.strip()
                if clean_kw and clean_kw.lower() not in seen_kw:
                    seen_kw.add(clean_kw.lower())
                    db.add(FundingKeyword(funding_opportunity_id=new_opp.id, keyword=clean_kw))

        await db.flush()
        return await FundingService.get_opportunity(new_opp.id, db)

    @staticmethod
    async def get_opportunity(opp_id: int, db: AsyncSession) -> FundingOpportunity:
        """Retrieves a funding opportunity by ID."""
        res = await db.execute(
            select(FundingOpportunity)
            .options(
                selectinload(FundingOpportunity.domains),
                selectinload(FundingOpportunity.keywords)
            )
            .where(FundingOpportunity.id == opp_id)
        )
        opp = res.scalar_one_or_none()
        if not opp:
            raise EntityNotFoundException(f"Funding opportunity with ID {opp_id} was not found")
        return opp

    @staticmethod
    async def list_opportunities(
        search_query: Optional[str] = None,
        agency: Optional[str] = None,
        domain: Optional[str] = None,
        opportunity_type: Optional[str] = None,
        status: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        deadline_after: Optional[datetime] = None,
        deadline_before: Optional[datetime] = None,
        limit: int = 20,
        offset: int = 0,
        db: AsyncSession = None
    ) -> Tuple[List[FundingOpportunity], int]:
        """Lists and filters indexed funding opportunities with pagination."""
        query = select(FundingOpportunity).options(
            selectinload(FundingOpportunity.domains),
            selectinload(FundingOpportunity.keywords)
        )

        conditions = []

        if search_query:
            sq = f"%{search_query.strip().lower()}%"
            conditions.append(
                or_(
                    func.lower(FundingOpportunity.title).like(sq),
                    func.lower(FundingOpportunity.description).like(sq),
                    func.lower(FundingOpportunity.funding_agency).like(sq),
                    func.lower(FundingOpportunity.funding_program).like(sq),
                    func.lower(FundingOpportunity.eligibility_summary).like(sq)
                )
            )

        if agency:
            conditions.append(func.lower(FundingOpportunity.funding_agency).like(f"%{agency.strip().lower()}%"))

        if domain:
            # Filter via joined research domain
            query = query.join(funding_opportunity_domains, FundingOpportunity.id == funding_opportunity_domains.c.funding_opportunity_id)\
                         .join(ResearchDomain, funding_opportunity_domains.c.domain_id == ResearchDomain.id)
            conditions.append(func.lower(ResearchDomain.name) == domain.strip().lower())

        if opportunity_type:
            conditions.append(func.lower(FundingOpportunity.opportunity_type) == opportunity_type.strip().lower())

        if status:
            conditions.append(func.lower(FundingOpportunity.status) == status.strip().lower())

        if min_amount is not None:
            conditions.append(FundingOpportunity.funding_amount >= min_amount)

        if max_amount is not None:
            conditions.append(FundingOpportunity.funding_amount <= max_amount)

        if deadline_after:
            conditions.append(FundingOpportunity.application_deadline >= deadline_after)

        if deadline_before:
            conditions.append(FundingOpportunity.application_deadline <= deadline_before)

        if conditions:
            query = query.where(and_(*conditions))

        # Total count
        count_subquery = query.with_only_columns(func.count(FundingOpportunity.id.distinct())).order_by(None)
        total_res = await db.execute(count_subquery)
        total = total_res.scalar() or 0

        # Ordered by application_deadline asc nulls last, then created_at desc
        query = query.distinct().order_by(
            asc(FundingOpportunity.application_deadline).nulls_last(),
            desc(FundingOpportunity.created_at)
        ).offset(offset).limit(limit)

        res = await db.execute(query)
        items = list(res.scalars().all())

        return items, total

    @staticmethod
    async def update_opportunity(
        opp_id: int,
        user_id: int,
        is_admin: bool,
        update_in: FundingOpportunityUpdate,
        db: AsyncSession
    ) -> FundingOpportunity:
        """Updates a funding opportunity with ownership/admin authorization."""
        opp = await FundingService.get_opportunity(opp_id=opp_id, db=db)

        if not is_admin and opp.created_by_user_id != user_id:
            raise PermissionDeniedException("You do not have permission to update this funding opportunity")

        update_dict = update_in.model_dump(exclude_unset=True, exclude={"domain_ids", "keywords"})
        for field, value in update_dict.items():
            setattr(opp, field, value)

        # Update domains if provided
        if update_in.domain_ids is not None:
            await db.execute(
                funding_opportunity_domains.delete().where(
                    funding_opportunity_domains.c.funding_opportunity_id == opp.id
                )
            )
            for d_id in update_in.domain_ids:
                await db.execute(
                    funding_opportunity_domains.insert().values(
                        funding_opportunity_id=opp.id,
                        domain_id=d_id
                    )
                )

        # Update keywords if provided
        if update_in.keywords is not None:
            await db.execute(
                FundingKeyword.__table__.delete().where(
                    FundingKeyword.funding_opportunity_id == opp.id
                )
            )
            seen_kw = set()
            for kw in update_in.keywords:
                clean_kw = kw.strip()
                if clean_kw and clean_kw.lower() not in seen_kw:
                    seen_kw.add(clean_kw.lower())
                    db.add(FundingKeyword(funding_opportunity_id=opp.id, keyword=clean_kw))

        opp.updated_at = datetime.now(timezone.utc)
        await db.flush()
        return await FundingService.get_opportunity(opp.id, db)

    @staticmethod
    async def delete_opportunity(
        opp_id: int,
        user_id: int,
        is_admin: bool,
        db: AsyncSession
    ) -> None:
        """Deletes a funding opportunity with admin/creator authorization."""
        opp = await FundingService.get_opportunity(opp_id=opp_id, db=db)

        if not is_admin and opp.created_by_user_id != user_id:
            raise PermissionDeniedException("You do not have permission to delete this funding opportunity")

        await db.delete(opp)
        await db.flush()
