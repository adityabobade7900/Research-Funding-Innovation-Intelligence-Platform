from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Set
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.funding import FundingOpportunity
from app.models.profile import Profile
from app.schemas.funding import (
    FundingRecommendationItem,
    FundingRecommendationResponse,
    FundingOpportunityRead,
)
from app.services.profile_service import ProfileService
from app.services.eligibility_matcher import EligibilityMatcher


class FundingRecommendationService:
    """
    Deterministic, explainable, and rule-based Funding Recommendation Engine.
    Combines eligibility gating with domain alignment, keyword/interest density,
    proposal preparation window (deadline suitability), and funding scale scoring.
    """

    @classmethod
    async def get_recommendations(
        cls,
        user_id: int,
        limit: int = 10,
        minimum_score: float = 0.0,
        domain: Optional[str] = None,
        opportunity_type: Optional[str] = None,
        status_filter: Optional[str] = "open",
        db: AsyncSession = None
    ) -> FundingRecommendationResponse:
        """
        Generates personalized, ranked, and explainable funding recommendations for the authenticated researcher.
        """
        now = datetime.now(timezone.utc)

        # 1. Eagerly load user's extended profile (single batched query)
        profile = await ProfileService.get_extended_profile(user_id=user_id, db=db)

        # 2. Build candidate query with eager relationships to avoid N+1 queries
        stmt = (
            select(FundingOpportunity)
            .options(
                selectinload(FundingOpportunity.domains),
                selectinload(FundingOpportunity.keywords)
            )
        )

        filters = []
        if status_filter:
            filters.append(func.lower(FundingOpportunity.status) == status_filter.lower())
        else:
            filters.append(func.lower(FundingOpportunity.status).in_(["open", "upcoming", "rolling"]))

        if opportunity_type:
            filters.append(func.lower(FundingOpportunity.opportunity_type) == opportunity_type.lower())

        if domain:
            filters.append(
                FundingOpportunity.domains.any(
                    func.lower(FundingOpportunity.domains.property.mapper.class_.name) == domain.strip().lower()
                )
            )

        if filters:
            stmt = stmt.where(and_(*filters))

        result = await db.execute(stmt)
        candidates = list(result.scalars().all())

        # 3. Evaluate each candidate deterministically
        recommendations: List[FundingRecommendationItem] = []

        profile_domains_set = {d.name.strip().lower() for d in profile.domains if d.name}
        profile_tokens: Set[str] = set()
        for kw in profile.keywords:
            if kw.keyword:
                profile_tokens.add(kw.keyword.strip().lower())
        for intr in profile.interests:
            if intr.interest_area:
                profile_tokens.add(intr.interest_area.strip().lower())
        for ta in profile.technology_areas:
            if ta.area_name:
                profile_tokens.add(ta.area_name.strip().lower())

        for opp in candidates:
            # Step A: Gating via EligibilityMatcher
            elig = EligibilityMatcher.evaluate(profile=profile, opportunity=opp, evaluation_time=now)

            # Gating Rule: Discard strictly INELIGIBLE opportunities
            if elig.eligibility_status == "INELIGIBLE":
                continue

            # Step B: Domain Alignment Score (Max 20 pts)
            domain_score = 0.0
            opp_domains_set = {d.name.strip().lower() for d in opp.domains if d.name}
            matching_domains: List[str] = []
            if opp_domains_set and profile_domains_set:
                matching_domains = [d.title() for d in opp_domains_set.intersection(profile_domains_set)]
                if matching_domains:
                    domain_score = 20.0
            elif not opp_domains_set:
                domain_score = 10.0

            # Step C: Keyword / Thematic Density Match (Max 15 pts)
            opp_tokens: Set[str] = {k.keyword.strip().lower() for k in opp.keywords if k.keyword}
            opp_text = f"{opp.title or ''} {opp.description or ''} {opp.funding_program or ''}".lower()
            matched_kws: List[str] = []
            if profile_tokens:
                for token in profile_tokens:
                    if token in opp_tokens or (len(token) >= 3 and token in opp_text):
                        matched_kws.append(token.title())
            kw_score = min(15.0, len(matched_kws) * 5.0)

            # Step D: Deadline Suitability (Max 10 pts)
            deadline_score = 0.0
            if opp.application_deadline:
                dl = opp.application_deadline
                if dl.tzinfo is None:
                    dl = dl.replace(tzinfo=timezone.utc)
                days_left = (dl - now).days
                if 30 <= days_left <= 180:
                    deadline_score = 10.0  # Ideal window for preparation
                elif days_left > 180:
                    deadline_score = 7.0   # Good planning window
                elif 14 <= days_left < 30:
                    deadline_score = 5.0   # Tight window
                elif 0 <= days_left < 14:
                    deadline_score = 2.0   # Urgent window
            else:
                deadline_score = 8.0  # Rolling / open

            # Step E: Funding Scale (Max 5 pts)
            funding_scale_score = 3.0
            if opp.funding_amount and opp.funding_amount >= 100000.0:
                funding_scale_score = 5.0

            # Step F: Base Eligibility Compatibility (Max 50 pts)
            base_elig_score = elig.compatibility_score * 0.5

            total_rec_score = round(
                max(0.0, min(100.0, base_elig_score + domain_score + kw_score + deadline_score + funding_scale_score)),
                1
            )

            # Recommendation Reasons & Warnings
            reasons: List[str] = []
            if matching_domains:
                reasons.append(f"Direct alignment with research domain(s): {', '.join(matching_domains)}")
            if matched_kws:
                reasons.append(f"Thematic overlap on keywords: {', '.join(matched_kws[:3])}")
            if opp.funding_amount and opp.funding_amount >= 500000.0:
                reasons.append(f"High-impact funding opportunity ({opp.currency} {opp.funding_amount:,.0f})")
            if opp.application_deadline:
                reasons.append(f"Active application window with deadline on {opp.application_deadline.strftime('%Y-%m-%d')}")
            else:
                reasons.append("Rolling deadline allows flexible proposal submission")

            warnings: List[str] = list(elig.warnings)
            if elig.eligibility_status == "CONDITIONAL":
                warnings.insert(0, "Conditional match: some criteria require closer review or profile details")

            if total_rec_score >= minimum_score:
                recommendations.append(
                    FundingRecommendationItem(
                        opportunity=FundingOpportunityRead.model_validate(opp),
                        recommendation_score=total_rec_score,
                        eligibility_status=elig.eligibility_status,
                        matched_domains=matching_domains,
                        matched_keywords=matched_kws,
                        reasons=reasons,
                        warnings=warnings
                    )
                )

        # 4. Rank descending by recommendation_score
        recommendations.sort(key=lambda r: r.recommendation_score, reverse=True)

        # 5. Apply limit
        capped_items = recommendations[:limit]

        profile_summary = {
            "user_id": user_id,
            "institution": profile.institution,
            "domains": [d.name for d in profile.domains],
            "keyword_count": len(profile.keywords),
            "interest_count": len(profile.interests)
        }

        return FundingRecommendationResponse(
            total_recommended=len(recommendations),
            items=capped_items,
            profile_summary=profile_summary,
            evaluation_timestamp=now
        )
