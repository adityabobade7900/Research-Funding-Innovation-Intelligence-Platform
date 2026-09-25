from datetime import datetime, timezone
from typing import List, Optional, Tuple, Set
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.funding import SavedFunding, FundingOpportunity
from app.services.funding_service import FundingService
from app.core.exceptions import EntityNotFoundException


class SavedFundingService:
    """
    Manages persistent watchlist / bookmarked funding opportunities for researchers.
    Strictly isolated by user_id to enforce researcher privacy and access boundaries.
    """

    @staticmethod
    async def save_opportunity(
        user_id: int,
        opp_id: int,
        notes: Optional[str] = None,
        db: AsyncSession = None
    ) -> Tuple[SavedFunding, bool]:
        """
        Saves a funding opportunity to the researcher's persistent watchlist.
        Returns: (SavedFunding, created: bool)
        """
        # 1. Verify opportunity exists (raises EntityNotFoundException if missing)
        opp = await FundingService.get_opportunity(opp_id=opp_id, db=db)

        # 2. Check if already saved
        stmt = (
            select(SavedFunding)
            .options(
                selectinload(SavedFunding.funding_opportunity).selectinload(FundingOpportunity.domains),
                selectinload(SavedFunding.funding_opportunity).selectinload(FundingOpportunity.keywords)
            )
            .where(
                and_(
                    SavedFunding.user_id == user_id,
                    SavedFunding.funding_opportunity_id == opp_id
                )
            )
        )
        res = await db.execute(stmt)
        existing = res.scalar_one_or_none()

        if existing:
            if notes is not None:
                existing.notes = notes.strip() if notes else None
                await db.flush()
            return existing, False

        # 3. Create new saved funding record
        saved = SavedFunding(
            user_id=user_id,
            funding_opportunity_id=opp_id,
            notes=notes.strip() if notes else None,
            created_at=datetime.now(timezone.utc)
        )
        db.add(saved)
        await db.flush()

        # Re-fetch with loaded relationships
        res = await db.execute(stmt)
        saved_record = res.scalar_one()
        return saved_record, True

    @staticmethod
    async def unsave_opportunity(
        user_id: int,
        opp_id: int,
        db: AsyncSession = None
    ) -> bool:
        """
        Removes a funding opportunity from the researcher's persistent watchlist.
        Raises EntityNotFoundException if the opportunity doesn't exist or is not in watchlist.
        """
        # Verify opportunity exists
        await FundingService.get_opportunity(opp_id=opp_id, db=db)

        stmt = select(SavedFunding).where(
            and_(
                SavedFunding.user_id == user_id,
                SavedFunding.funding_opportunity_id == opp_id
            )
        )
        res = await db.execute(stmt)
        record = res.scalar_one_or_none()

        if not record:
            raise EntityNotFoundException(
                f"Funding opportunity {opp_id} is not present in your saved watchlist"
            )

        await db.delete(record)
        await db.flush()
        return True

    @staticmethod
    async def list_saved_opportunities(
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        db: AsyncSession = None
    ) -> Tuple[List[SavedFunding], int]:
        """
        Lists funding opportunities saved by the authenticated researcher.
        Ordered chronologically (most recently saved first).
        """
        query = (
            select(SavedFunding)
            .options(
                selectinload(SavedFunding.funding_opportunity).selectinload(FundingOpportunity.domains),
                selectinload(SavedFunding.funding_opportunity).selectinload(FundingOpportunity.keywords)
            )
            .where(SavedFunding.user_id == user_id)
        )

        # Count total
        count_query = select(func.count(SavedFunding.id)).where(SavedFunding.user_id == user_id)
        count_res = await db.execute(count_query)
        total = count_res.scalar() or 0

        # Query paginated items
        paginated_query = query.order_by(desc(SavedFunding.created_at)).offset(offset).limit(limit)
        items_res = await db.execute(paginated_query)
        items = list(items_res.scalars().all())

        return items, total

    @staticmethod
    async def get_saved_ids_for_user(
        user_id: int,
        db: AsyncSession = None
    ) -> Set[int]:
        """
        Fast lookup of all opportunity IDs saved by a specific user.
        """
        query = select(SavedFunding.funding_opportunity_id).where(SavedFunding.user_id == user_id)
        res = await db.execute(query)
        return set(res.scalars().all())
