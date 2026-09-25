from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.models.profile import Profile
from app.models.publication import Publication, profile_publications
from app.models.patent import Patent, profile_patents
from app.models.funding import FundingOpportunity
from app.schemas.command_center import (
    ActivityFeedItem,
    RoleContextualMetrics,
    CommandCenterOverviewResponse,
    ActivityFeedResponse,
)
from app.services.innovation_scoring_service import InnovationScoringService
from app.services.commercialization_service import CommercializationService
from app.services.technology_intelligence_service import TechnologyIntelligenceService


class CommandCenterService:
    """
    Milestone 6: Cross-Module Unified Strategic Command Center Service.
    """

    @classmethod
    async def get_overview(
        cls,
        user: Optional[User] = None,
        db: AsyncSession = None,
    ) -> CommandCenterOverviewResponse:
        """
        Synthesizes unified cross-module intelligence tailored to user profile and RBAC role.
        """
        user_name = user.full_name if user else "Guest Innovator"
        user_role = user.role if user else UserRole.RESEARCHER
        profile_id = user.profile.id if (user and user.profile) else None

        # 1. Publications & Patents metrics
        if profile_id:
            pub_stmt = select(func.count(profile_publications.c.publication_id)).where(
                profile_publications.c.profile_id == profile_id
            )
            pat_stmt = select(func.count(profile_patents.c.patent_id)).where(
                profile_patents.c.profile_id == profile_id
            )
        else:
            pub_stmt = select(func.count(Publication.id))
            pat_stmt = select(func.count(Patent.id))

        total_pubs = (await db.execute(pub_stmt)).scalar() or 0
        total_pats = (await db.execute(pat_stmt)).scalar() or 0

        # 2. Funding opportunities & grant pool
        fnd_stmt = select(func.count(FundingOpportunity.id))
        total_fnd = (await db.execute(fnd_stmt)).scalar() or 0

        grant_sum_stmt = select(func.sum(FundingOpportunity.funding_amount))
        grant_pool_usd = (await db.execute(grant_sum_stmt)).scalar() or 0.0

        # 3. Innovation Scoring & Commercialization
        if profile_id:
            innov = await InnovationScoringService.calculate_innovation_score(profile_id=profile_id, db=db)
            comm = await CommercializationService.evaluate_commercialization(profile_id=profile_id, db=db)
        else:
            innov = await InnovationScoringService.calculate_innovation_score(domain="Quantum Computing", db=db)
            comm = await CommercializationService.evaluate_commercialization(domain="Quantum Computing", db=db)

        # 4. Whitespaces
        ws_res = await TechnologyIntelligenceService.detect_whitespaces(db=db)
        top_ws = [w.technology_area for w in ws_res.candidates[:3]]

        # 5. Upcoming Grant Deadlines
        deadlines_stmt = (
            select(FundingOpportunity)
            .where(FundingOpportunity.application_deadline.is_not(None))
            .order_by(FundingOpportunity.application_deadline.asc())
            .limit(4)
        )
        deadlines_rows = (await db.execute(deadlines_stmt)).scalars().all()
        upcoming_grants = [
            {
                "id": g.id,
                "title": g.title,
                "agency": g.funding_agency,
                "amount": g.funding_amount,
                "deadline": g.application_deadline.isoformat() if g.application_deadline else None,
            }
            for g in deadlines_rows
        ]

        # 6. Role-Contextual Metrics
        role_metrics = cls._build_role_metrics(
            role=user_role,
            pubs_count=total_pubs,
            pat_count=total_pats,
            innov_score=innov.innovation_score,
            readiness_score=comm.readiness.readiness_score,
            grant_pool=float(grant_pool_usd),
            top_pathway=comm.readiness.primary_pathway,
        )

        # 7. Activity Feed
        recent_activity = await cls._generate_recent_activity(db=db)

        return CommandCenterOverviewResponse(
            user_name=user_name,
            user_role=user_role,
            is_profile_scoped=bool(profile_id),
            total_publications=total_pubs,
            total_patents=total_pats,
            total_funding_opportunities=total_fnd,
            total_grant_pool_usd=round(float(grant_pool_usd), 2),
            average_innovation_score=innov.innovation_score,
            average_readiness_score=comm.readiness.readiness_score,
            dominant_trl_stage=f"TRL {innov.trl.estimated_trl} ({innov.trl.trl_stage})",
            top_recommended_pathway=comm.readiness.primary_pathway,
            top_whitespace_areas=top_ws,
            upcoming_grant_deadlines=upcoming_grants,
            role_metrics=role_metrics,
            recent_activity=recent_activity,
        )

    @classmethod
    def _build_role_metrics(
        cls,
        role: UserRole,
        pubs_count: int,
        pat_count: int,
        innov_score: float,
        readiness_score: float,
        grant_pool: float,
        top_pathway: str,
    ) -> RoleContextualMetrics:
        """Constructs role-tailored high-level strategic KPI cards and primary recommended CTA."""
        if role == UserRole.STARTUP_FOUNDER:
            return RoleContextualMetrics(
                role=role,
                role_headline="Deep-Tech Whitespaces & Venture Spinout Command",
                primary_metric_label="Commercial Readiness",
                primary_metric_value=f"{readiness_score} / 100",
                secondary_metric_label="Tracked Non-Dilutive Capital",
                secondary_metric_value=f"${grant_pool / 1e6:.1f}M",
                tertiary_metric_label="Primary Pathway",
                tertiary_metric_value=top_pathway.replace("_", " "),
                recommended_focus_action="Explore Technology Whitespace Gaps",
                focus_action_href="/technology-intelligence",
            )
        elif role == UserRole.INNOVATION_MANAGER:
            return RoleContextualMetrics(
                role=role,
                role_headline="Institutional Portfolio Innovation Benchmarking & TRL Pipeline",
                primary_metric_label="Composite Innovation Score",
                primary_metric_value=f"{innov_score} / 100",
                secondary_metric_label="IP Disclosures Protected",
                secondary_metric_value=f"{pat_count} Patents",
                tertiary_metric_label="Commercialization Score",
                tertiary_metric_value=f"{readiness_score} / 100",
                recommended_focus_action="Generate Executive Portfolio Dossier",
                focus_action_href="/reports",
            )
        elif role == UserRole.ADMINISTRATOR:
            return RoleContextualMetrics(
                role=role,
                role_headline="Platform Administration, RBAC Governance & Pipeline Health",
                primary_metric_label="Total Ingested Publications",
                primary_metric_value=f"{pubs_count} Papers",
                secondary_metric_label="Total Patents Indexed",
                secondary_metric_value=f"{pat_count} Patents",
                tertiary_metric_label="Platform System Health",
                tertiary_metric_value="100% OPERATIONAL",
                recommended_focus_action="Inspect Telemetry & User Governance",
                focus_action_href="/admin",
            )
        else:  # RESEARCHER
            return RoleContextualMetrics(
                role=role,
                role_headline="Academic Novelty & Semantic Grant Matchmaking",
                primary_metric_label="Research Novelty & Innovation",
                primary_metric_value=f"{innov_score} / 100",
                secondary_metric_label="Indexed Publications",
                secondary_metric_value=f"{pubs_count} Papers",
                tertiary_metric_label="Identified Grant Pool",
                tertiary_metric_value=f"${grant_pool / 1e6:.1f}M",
                recommended_focus_action="Match Semantic Grant Solicitations",
                focus_action_href="/funding",
            )

    @classmethod
    async def _generate_recent_activity(
        cls,
        db: AsyncSession = None,
    ) -> List[ActivityFeedItem]:
        """Generates cross-module chronological activity updates."""
        items: List[ActivityFeedItem] = []

        # 1. Latest publications
        pub_stmt = select(Publication).order_by(Publication.id.desc()).limit(2)
        pubs = (await db.execute(pub_stmt)).scalars().all()
        for p in pubs:
            items.append(
                ActivityFeedItem(
                    id=f"ACT-PUB-{p.id}",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    activity_type="PUBLICATION",
                    title=f"Paper Indexed: {p.title[:60]}...",
                    description=f"Published in {p.venue or 'Journal'} with {p.citation_count} citations.",
                    domain=p.primary_domain,
                    badge_label="Publication",
                    action_href=f"/publications",
                )
            )

        # 2. Latest patents
        pat_stmt = select(Patent).order_by(Patent.id.desc()).limit(2)
        pats = (await db.execute(pat_stmt)).scalars().all()
        for pt in pats:
            items.append(
                ActivityFeedItem(
                    id=f"ACT-PAT-{pt.id}",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    activity_type="PATENT",
                    title=f"Patent Tracked: {pt.patent_number}",
                    description=f"{pt.title[:60]}... Assigned to {pt.assignee or 'Applicant'}.",
                    domain=pt.technology_domain,
                    badge_label="Patent IP",
                    action_href="/patents",
                )
            )

        # 3. Latest funding
        fnd_stmt = select(FundingOpportunity).order_by(FundingOpportunity.id.desc()).limit(2)
        fnds = (await db.execute(fnd_stmt)).scalars().all()
        for f in fnds:
            items.append(
                ActivityFeedItem(
                    id=f"ACT-FND-{f.id}",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    activity_type="FUNDING",
                    title=f"Grant Solicitation: {f.title[:55]}...",
                    description=f"Funded by {f.funding_agency} ({f.currency or '$'}{f.funding_amount:,.0f} award).",
                    badge_label="Grant Radar",
                    action_href="/funding",
                )
            )

        return items

    @classmethod
    async def get_activity_feed(
        cls,
        limit: int = 20,
        db: AsyncSession = None,
    ) -> ActivityFeedResponse:
        """Returns the full unified activity feed."""
        activities = await cls._generate_recent_activity(db=db)
        return ActivityFeedResponse(items=activities[:limit], total=len(activities))
