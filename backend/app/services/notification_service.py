import logging
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy import select, func, update, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User, UserRole
from app.models.profile import Profile
from app.models.notification import Notification, NotificationType, NotificationPriority
from app.models.funding import FundingOpportunity
from app.models.patent import Patent
from app.models.publication import Publication
from app.services.eligibility_matcher import EligibilityMatcher
from app.services.technology_intelligence_service import TechnologyIntelligenceService
from app.services.research_trend_service import ResearchTrendService
from app.services.commercialization_service import CommercializationService

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Dedicated Service for Module 10: Notification & Alert System.
    Provides persistence, deduplication, user isolation, and multi-module event scanning.
    """

    @classmethod
    async def create_notification(
        cls,
        user_id: int,
        type: NotificationType,
        title: str,
        message: str,
        related_module: Optional[str] = None,
        related_record_id: Optional[str] = None,
        target_url: Optional[str] = None,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        db: AsyncSession = None,
    ) -> Tuple[Notification, bool]:
        """
        Creates a notification with deterministic deduplication check.
        Returns (notification, was_created).
        """
        # Deduplication check: user_id + type + related_record_id
        if related_record_id:
            dedup_stmt = select(Notification).where(
                Notification.user_id == user_id,
                Notification.type == type,
                Notification.related_record_id == str(related_record_id)
            )
            existing = (await db.execute(dedup_stmt)).scalars().first()
            if existing:
                return existing, False

        notification = Notification(
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            related_module=related_module,
            related_record_id=str(related_record_id) if related_record_id is not None else None,
            target_url=target_url,
            priority=priority,
            is_read=False,
            created_at=datetime.now(timezone.utc)
        )
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        return notification, True

    @classmethod
    async def list_notifications(
        cls,
        user_id: int,
        notification_type: Optional[NotificationType] = None,
        is_read: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
        db: AsyncSession = None,
    ) -> Tuple[List[Notification], int, int]:
        """
        Lists notifications for a specific user with filtering and pagination.
        Enforces user ownership.
        Returns (items, total_matching, unread_count_overall).
        """
        base_filters = [Notification.user_id == user_id]
        if notification_type:
            base_filters.append(Notification.type == notification_type)
        if is_read is not None:
            base_filters.append(Notification.is_read == is_read)

        # Count total matching query
        count_stmt = select(func.count(Notification.id)).where(and_(*base_filters))
        total_matching = (await db.execute(count_stmt)).scalar() or 0

        # Overall unread count for user
        unread_stmt = select(func.count(Notification.id)).where(
            Notification.user_id == user_id,
            Notification.is_read == False
        )
        unread_count = (await db.execute(unread_stmt)).scalar() or 0

        # Fetch paginated items
        items_stmt = (
            select(Notification)
            .where(and_(*base_filters))
            .order_by(Notification.created_at.desc(), Notification.id.desc())
            .limit(limit)
            .offset(offset)
        )
        items = (await db.execute(items_stmt)).scalars().all()
        return list(items), total_matching, unread_count

    @classmethod
    async def get_unread_count(
        cls,
        user_id: int,
        db: AsyncSession = None,
    ) -> int:
        """Counts unread notifications for a specific user."""
        stmt = select(func.count(Notification.id)).where(
            Notification.user_id == user_id,
            Notification.is_read == False
        )
        return (await db.execute(stmt)).scalar() or 0

    @classmethod
    async def get_notification(
        cls,
        notification_id: int,
        user_id: int,
        db: AsyncSession = None,
    ) -> Optional[Notification]:
        """
        Retrieves a single notification by ID.
        Strict IDOR prevention: ensures notification belongs to user_id.
        """
        stmt = select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id
        )
        return (await db.execute(stmt)).scalars().first()

    @classmethod
    async def mark_as_read(
        cls,
        notification_id: int,
        user_id: int,
        db: AsyncSession = None,
    ) -> Optional[Notification]:
        """
        Marks a single notification as read if owned by the user.
        """
        notification = await cls.get_notification(notification_id=notification_id, user_id=user_id, db=db)
        if not notification:
            return None

        if not notification.is_read:
            notification.is_read = True
            await db.commit()
            await db.refresh(notification)

        return notification

    @classmethod
    async def mark_all_as_read(
        cls,
        user_id: int,
        db: AsyncSession = None,
    ) -> int:
        """
        Marks all notifications for a specific user as read.
        Returns count of updated notifications.
        """
        update_stmt = (
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
            .values(is_read=True)
        )
        res = await db.execute(update_stmt)
        await db.commit()
        return res.rowcount or 0

    @classmethod
    async def generate_alerts_for_user(
        cls,
        user: User,
        db: AsyncSession = None,
    ) -> List[Notification]:
        """
        Scans platform intelligence (M3, M4, M5, M6, M8) and creates
        traceable, relevant notifications for the user with duplicate prevention.
        """
        created_alerts: List[Notification] = []

        # 1. Extract user profile context
        profile_stmt = (
            select(Profile)
            .where(Profile.user_id == user.id)
            .options(
                selectinload(Profile.domains),
                selectinload(Profile.interests),
                selectinload(Profile.keywords),
            )
        )
        profile = (await db.execute(profile_stmt)).scalars().first()

        user_domains = [d.name.lower() for d in profile.domains] if profile and profile.domains else []
        user_keywords = [k.keyword.lower() for k in profile.keywords] if profile and profile.keywords else []
        user_interests = [i.interest.lower() for i in profile.interests] if profile and profile.interests else []

        # Fallback if profile has no domains: default domain hint
        primary_domain = user_domains[0] if user_domains else "artificial intelligence"

        # -------------------------------------------------------------
        # MODULE 4: FUNDING INTELLIGENCE NOTIFICATIONS
        # -------------------------------------------------------------
        try:
            fnd_stmt = select(FundingOpportunity).where(FundingOpportunity.status == "open")
            opportunities = (await db.execute(fnd_stmt)).scalars().all()

            for opp in opportunities:
                # Check relevance via EligibilityMatcher or domain/keyword match
                is_relevant = False
                match_score = 0.0

                if profile:
                    try:
                        eval_res = EligibilityMatcher.evaluate(profile=profile, opportunity=opp)
                        if eval_res.overall_score >= 35.0:
                            is_relevant = True
                            match_score = eval_res.overall_score
                    except Exception as e:
                        logger.warning(f"Eligibility evaluation error: {e}")

                # Keyword/Domain direct match check if matcher was inconclusive
                if not is_relevant:
                    opp_text = f"{opp.title} {opp.description or ''} {opp.funding_agency}".lower()
                    domain_matches = any(dom in opp_text for dom in user_domains)
                    keyword_matches = any(kw in opp_text for kw in user_keywords or user_interests)
                    if domain_matches or keyword_matches:
                        is_relevant = True
                        match_score = 65.0

                if is_relevant:
                    # Check urgency
                    days_remaining = None
                    if opp.application_deadline:
                        now = datetime.now(timezone.utc)
                        dl = opp.application_deadline
                        if dl.tzinfo is None:
                            dl = dl.replace(tzinfo=timezone.utc)
                        days_remaining = (dl - now).days

                    if days_remaining is not None and 0 <= days_remaining <= 30:
                        priority = NotificationPriority.HIGH
                        title = f"Upcoming Grant Deadline: {opp.title[:55]}"
                        msg = (
                            f"Grant opportunity from {opp.funding_agency} has a deadline in {days_remaining} day(s). "
                            f"Total award: {opp.currency or '$'}{opp.funding_amount:,.0f}."
                        )
                    else:
                        priority = NotificationPriority.MEDIUM
                        title = f"New Funding Opportunity: {opp.title[:55]}"
                        msg = (
                            f"Identified matching grant solicitation by {opp.funding_agency} relevant to your profile. "
                            f"Estimated award: {opp.currency or '$'}{opp.funding_amount:,.0f}."
                        )

                    notif, created = await cls.create_notification(
                        user_id=user.id,
                        type=NotificationType.FUNDING,
                        title=title,
                        message=msg,
                        related_module="funding",
                        related_record_id=f"fnd_{opp.id}",
                        target_url="/funding",
                        priority=priority,
                        db=db,
                    )
                    if created:
                        created_alerts.append(notif)
        except Exception as e:
            logger.error(f"Error scanning funding notifications: {e}")

        # -------------------------------------------------------------
        # MODULE 5: PATENT LANDSCAPE ALERTS
        # -------------------------------------------------------------
        try:
            pat_stmt = select(Patent).order_by(Patent.id.desc()).limit(20)
            patents = (await db.execute(pat_stmt)).scalars().all()

            for pat in patents:
                # Relevance check: patent domain or text matches user domain/keywords
                pat_domain = (pat.technology_domain or "").lower()
                pat_text = f"{pat.title} {pat.abstract or ''}".lower()

                domain_matched = any(d in pat_domain or d in pat_text for d in user_domains)
                keyword_matched = any(k in pat_text for k in user_keywords)

                if domain_matched or keyword_matched:
                    title = f"Patent Activity: {pat.patent_number}"
                    msg = (
                        f"Patent disclosure '{pat.title[:65]}' filed by {pat.assignee or 'Applicant'} "
                        f"in domain {pat.technology_domain or 'General'}. Citation count: {pat.citation_count}."
                    )
                    notif, created = await cls.create_notification(
                        user_id=user.id,
                        type=NotificationType.PATENT,
                        title=title,
                        message=msg,
                        related_module="patents",
                        related_record_id=f"pat_{pat.id}",
                        target_url="/patents",
                        priority=NotificationPriority.MEDIUM,
                        db=db,
                    )
                    if created:
                        created_alerts.append(notif)
        except Exception as e:
            logger.error(f"Error scanning patent notifications: {e}")

        # -------------------------------------------------------------
        # MODULE 6: EMERGING TECHNOLOGY ALERTS
        # -------------------------------------------------------------
        try:
            ws_res = await TechnologyIntelligenceService.detect_whitespaces(db=db)
            if ws_res and ws_res.candidates:
                for candidate in ws_res.candidates[:3]:
                    c_domain = candidate.technology_area.lower()
                    # Check relevance
                    if any(d in c_domain for d in user_domains) or len(user_domains) == 0:
                        # Conservative wording
                        title = f"Emerging Technology Signal: {candidate.technology_area}"
                        msg = (
                            f"{candidate.technology_area} is exhibiting early whitespace and development momentum "
                            f"(innovation index: {candidate.innovation_score:.1f}, patents tracked: {candidate.patent_count}). "
                            f"Based on latest available patent and literature indicators."
                        )
                        notif, created = await cls.create_notification(
                            user_id=user.id,
                            type=NotificationType.TECHNOLOGY,
                            title=title,
                            message=msg,
                            related_module="technology_intelligence",
                            related_record_id=f"tech_{candidate.technology_area.lower().replace(' ', '_')}",
                            target_url="/technology-intelligence",
                            priority=NotificationPriority.HIGH if candidate.innovation_score > 60 else NotificationPriority.MEDIUM,
                            db=db,
                        )
                        if created:
                            created_alerts.append(notif)
        except Exception as e:
            logger.error(f"Error scanning technology notifications: {e}")

        # -------------------------------------------------------------
        # MODULE 3: RESEARCH TREND ALERTS
        # -------------------------------------------------------------
        try:
            profile_id = profile.id if profile else None
            topics_resp = await ResearchTrendService.get_emerging_topics(profile_id=profile_id, db=db)
            if topics_resp and topics_resp.items:
                for topic in topics_resp.items[:3]:
                    # Conservative wording
                    title = f"Research Trend Acceleration: {topic.keyword}"
                    msg = (
                        f"Research activity around '{topic.keyword}' has increased with {topic.publication_count} "
                        f"indexed publication(s) and a velocity score of {topic.velocity_score:.1f}."
                    )
                    notif, created = await cls.create_notification(
                        user_id=user.id,
                        type=NotificationType.RESEARCH_TREND,
                        title=title,
                        message=msg,
                        related_module="research_intelligence",
                        related_record_id=f"trend_{topic.keyword.lower().replace(' ', '_')}",
                        target_url="/research-intelligence",
                        priority=NotificationPriority.MEDIUM,
                        db=db,
                    )
                    if created:
                        created_alerts.append(notif)
        except Exception as e:
            logger.error(f"Error scanning research trend notifications: {e}")

        # -------------------------------------------------------------
        # MODULE 8: COMMERCIALIZATION ALERTS
        # -------------------------------------------------------------
        try:
            domain_arg = primary_domain.title()
            comm_eval = await CommercializationService.evaluate_commercialization(
                domain=domain_arg,
                profile_id=profile.id if profile else None,
                db=db
            )
            if comm_eval and comm_eval.readiness:
                pathway_raw = comm_eval.readiness.primary_pathway
                pathway_title = pathway_raw.replace("_", " ").title()
                score = comm_eval.readiness.readiness_score

                # Strictly conservative wording
                title = f"Commercialization Opportunity: {pathway_title}"
                msg = (
                    f"A potential {pathway_raw.lower().replace('_', ' ')} pathway has been identified for your research "
                    f"domain with a readiness score of {score:.1f}/100. Based on evaluated IP maturity and market indicators."
                )
                notif, created = await cls.create_notification(
                    user_id=user.id,
                    type=NotificationType.COMMERCIALIZATION,
                    title=title,
                    message=msg,
                    related_module="commercialization",
                    related_record_id=f"comm_{user.id}_{pathway_raw.lower()}",
                    target_url="/commercialization",
                    priority=NotificationPriority.HIGH if score >= 60 else NotificationPriority.MEDIUM,
                    db=db,
                )
                if created:
                    created_alerts.append(notif)
        except Exception as e:
            logger.error(f"Error scanning commercialization notifications: {e}")

        # -------------------------------------------------------------
        # PLATFORM NOTIFICATION: Profile Guidance / System Status
        # -------------------------------------------------------------
        try:
            if not profile or not profile.domains:
                title = "Platform Notification: Setup Research Profile"
                msg = (
                    "Complete your Research Profile and select your research domains to enable automated semantic "
                    "matching for grants, patents, and technology whitespaces."
                )
                notif, created = await cls.create_notification(
                    user_id=user.id,
                    type=NotificationType.PLATFORM,
                    title=title,
                    message=msg,
                    related_module="platform",
                    related_record_id=f"plat_{user.id}_profile_prompt",
                    target_url="/profile",
                    priority=NotificationPriority.MEDIUM,
                    db=db,
                )
                if created:
                    created_alerts.append(notif)
            else:
                title = "Platform Notification: Workspace Synced"
                msg = f"Your intelligence feed is active. Domain tracking active for: {', '.join([d.name for d in profile.domains][:3])}."
                notif, created = await cls.create_notification(
                    user_id=user.id,
                    type=NotificationType.PLATFORM,
                    title=title,
                    message=msg,
                    related_module="platform",
                    related_record_id=f"plat_{user.id}_workspace_synced",
                    target_url="/dashboard",
                    priority=NotificationPriority.LOW,
                    db=db,
                )
                if created:
                    created_alerts.append(notif)
        except Exception as e:
            logger.error(f"Error scanning platform notifications: {e}")

        return created_alerts
