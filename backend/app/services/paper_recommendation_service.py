import logging
from typing import List, Optional, Set, Tuple
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import Profile
from app.models.publication import Publication
from app.schemas.publication import (
    PublicationRecommendationItem,
    PublicationRecommendationsResponse
)
from app.services.profile_service import ProfileService

logger = logging.getLogger(__name__)


class PaperRecommendationService:
    """
    Deterministic, explainable, and rule-based Research Paper Recommendation Engine.
    Computes multi-factor relevance scores between the authenticated researcher's
    academic profile and unassociated catalog publications.
    """

    WEIGHT_DOMAIN: float = 40.0
    WEIGHT_KEYWORDS_INTERESTS: float = 30.0
    WEIGHT_TECH_AREAS: float = 15.0
    WEIGHT_HISTORY: float = 10.0
    WEIGHT_CITATION: float = 5.0

    @classmethod
    async def get_recommendations(
        cls,
        user_id: int,
        limit: int = 10,
        min_score: float = 20.0,
        db: AsyncSession = None
    ) -> PublicationRecommendationsResponse:
        """
        Generates personalized, ranked, and explainable paper recommendations
        for the authenticated researcher. Excludes papers already in their portfolio.
        """
        # 1. Fetch user's profile with all research taxonomy relationships
        profile = await ProfileService.get_or_create_profile(user_id=user_id, db=db)

        # Preload all related collections on profile
        profile_stmt = (
            select(Profile)
            .options(
                selectinload(Profile.domains),
                selectinload(Profile.interests),
                selectinload(Profile.keywords),
                selectinload(Profile.technology_areas),
                selectinload(Profile.academic_histories),
                selectinload(Profile.research_histories),
                selectinload(Profile.publications)
            )
            .where(Profile.id == profile.id)
        )
        res = await db.execute(profile_stmt)
        full_profile = res.scalar_one_or_none() or profile

        # Extract existing publication IDs to exclude
        existing_pub_ids: Set[int] = {p.id for p in full_profile.publications} if full_profile.publications else set()

        # Check for profile completeness
        has_domains = bool(full_profile.domains)
        has_keywords = bool(full_profile.keywords)
        has_interests = bool(full_profile.interests)
        has_tech = bool(full_profile.technology_areas)

        profile_warning: Optional[str] = None
        if not (has_domains or has_keywords or has_interests or has_tech):
            profile_warning = (
                "Your research profile does not currently have specified domains, keywords, or interests. "
                "Update your profile to receive fully personalized paper recommendations."
            )

        # 2. Query candidate publications (excluding already associated papers)
        pub_stmt = select(Publication).options(selectinload(Publication.keywords))
        pub_res = await db.execute(pub_stmt)
        all_pubs = list(pub_res.scalars().all())

        candidate_pubs = [p for p in all_pubs if p.id not in existing_pub_ids]

        if not candidate_pubs:
            return PublicationRecommendationsResponse(
                total_recommended=0,
                recommendations=[],
                profile_completeness_warning=profile_warning
            )

        # 3. Profile Term Extraction
        profile_domain_names = [d.name.lower().strip() for d in full_profile.domains if d.name]
        profile_keywords = [k.keyword.lower().strip() for k in full_profile.keywords if k.keyword]
        profile_interests = [i.title.lower().strip() for i in full_profile.interests if i.title]
        profile_tech_areas = [t.name.lower().strip() for t in full_profile.technology_areas if t.name]
        profile_history_terms = []
        for a in full_profile.academic_histories:
            if a.field_of_study:
                profile_history_terms.append(a.field_of_study.lower().strip())
        for r in full_profile.research_histories:
            if r.project_title:
                profile_history_terms.append(r.project_title.lower().strip())

        scored_items: List[PublicationRecommendationItem] = []

        # 4. Score Candidate Publications
        for pub in candidate_pubs:
            reasons: List[str] = []
            score = 0.0

            pub_domain = (pub.primary_domain or "").lower().strip()
            pub_title = pub.title.lower()
            pub_abstract = (pub.abstract or "").lower()
            pub_keywords = [k.keyword.lower().strip() for k in pub.keywords] if pub.keywords else []
            pub_text_blob = f"{pub_title} {pub_abstract} {' '.join(pub_keywords)}"

            # A. Research Domain Match (Weight: 40 pts)
            domain_matched = False
            for d_name in profile_domain_names:
                if pub_domain and (pub_domain == d_name):
                    score += cls.WEIGHT_DOMAIN
                    reasons.append(f"Direct match with your research domain: '{pub.primary_domain}'")
                    domain_matched = True
                    break
                elif pub_domain and (d_name in pub_domain or pub_domain in d_name):
                    score += (cls.WEIGHT_DOMAIN * 0.6)
                    reasons.append(f"Partial match with research domain: '{pub.primary_domain}'")
                    domain_matched = True
                    break

            # B. Keywords & Research Interests Match (Weight: 30 pts)
            kw_pts = 0.0
            matched_kws: Set[str] = set()
            for kw in (profile_keywords + profile_interests):
                if kw in matched_kws:
                    continue
                # Check against pub keywords or pub text blob
                if any(kw == pk or kw in pk for pk in pub_keywords) or kw in pub_title:
                    matched_kws.add(kw)
                    kw_pts += 15.0
                    reasons.append(f"Matches profile keyword/interest: '{kw}'")
                elif kw in pub_abstract and len(kw) > 3:
                    matched_kws.add(kw)
                    kw_pts += 7.5
                    reasons.append(f"Related to profile topic: '{kw}' in abstract")
                if kw_pts >= cls.WEIGHT_KEYWORDS_INTERESTS:
                    break
            score += min(cls.WEIGHT_KEYWORDS_INTERESTS, kw_pts)

            # C. Technology Areas Match (Weight: 15 pts)
            tech_pts = 0.0
            for tech in profile_tech_areas:
                if tech in pub_text_blob:
                    tech_pts += 7.5
                    reasons.append(f"Aligns with technology area: '{tech}'")
                if tech_pts >= cls.WEIGHT_TECH_AREAS:
                    break
            score += min(cls.WEIGHT_TECH_AREAS, tech_pts)

            # D. Academic / Research History Match (Weight: 10 pts)
            hist_pts = 0.0
            for h_term in profile_history_terms:
                if h_term and h_term in pub_text_blob:
                    hist_pts += 5.0
                    reasons.append(f"Aligns with background in: '{h_term}'")
                if hist_pts >= cls.WEIGHT_HISTORY:
                    break
            score += min(cls.WEIGHT_HISTORY, hist_pts)

            # E. Citation Momentum (Weight: 5 pts)
            if pub.citation_count > 0:
                cite_pts = min(cls.WEIGHT_CITATION, round((pub.citation_count / 30.0) * cls.WEIGHT_CITATION, 1))
                score += cite_pts
                if pub.citation_count >= 20:
                    reasons.append(f"High academic impact ({pub.citation_count} citations)")

            # Graceful fallback for empty profiles
            if not reasons:
                if pub.citation_count > 0:
                    score = min(35.0, 15.0 + (pub.citation_count * 0.5))
                    reasons.append("Featured publication in global catalog")
                else:
                    score = 15.0
                    reasons.append("Recent indexed publication in catalog")

            final_score = min(100.0, round(score, 1))

            if final_score >= min_score or not (has_domains or has_keywords):
                year_val = pub.publication_date.year if pub.publication_date else None
                scored_items.append(
                    PublicationRecommendationItem(
                        publication_id=pub.id,
                        title=pub.title,
                        authors=pub.authors,
                        venue=pub.venue,
                        year=year_val,
                        doi=pub.doi,
                        primary_domain=pub.primary_domain,
                        citation_count=pub.citation_count,
                        relevance_score=final_score,
                        reasons=reasons[:4]
                    )
                )

        # 5. Rank Descending by relevance_score, then citation_count
        scored_items.sort(key=lambda x: (x.relevance_score, x.citation_count), reverse=True)
        top_items = scored_items[:limit]

        return PublicationRecommendationsResponse(
            total_recommended=len(scored_items),
            recommendations=top_items,
            profile_completeness_warning=profile_warning
        )
