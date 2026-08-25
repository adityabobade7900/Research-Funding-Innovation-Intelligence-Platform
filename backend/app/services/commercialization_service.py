from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import select, func, distinct, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.publication import Publication
from app.models.patent import Patent
from app.models.funding import FundingOpportunity
from app.models.profile import Profile
from app.models.user import User
from app.schemas.commercialization import (
    CommercializationRecommendationItem,
    CommercializationReadinessItem,
    CommercializationResponse,
    DomainCommercializationItem,
    CommercializationSummary,
)
from app.services.innovation_scoring_service import InnovationScoringService
from app.services.technology_intelligence_service import TechnologyIntelligenceService


class CommercializationService:
    """
    Deterministic Commercialization Intelligence & Recommendation Engine.
    Synthesizes Innovation Score 5-pillar signals (TRL, Patent Strength, Market Potential proxy,
    Funding Relevance, Research Novelty) to compute Commercialization Readiness and formulate
    prioritized, explainable commercialization pathways.
    """

    @classmethod
    async def evaluate_commercialization(
        cls,
        domain: Optional[str] = None,
        profile_id: Optional[int] = None,
        db: AsyncSession = None,
    ) -> CommercializationResponse:
        """
        Calculates commercialization readiness and generates explainable, multi-factor commercialization recommendations.
        """
        # 1. Re-use Innovation Scoring 5-Pillar evaluation (M3C)
        innov_resp = await InnovationScoringService.calculate_innovation_score(
            domain=domain,
            profile_id=profile_id,
            db=db,
        )

        trl_score = innov_resp.pillars["technology_maturity"].score
        patent_strength_score = innov_resp.pillars["patent_strength"].score
        market_potential_score = innov_resp.pillars["market_potential"].score
        funding_relevance_score = innov_resp.pillars["funding_relevance"].score
        novelty_score = innov_resp.pillars["research_novelty"].score

        estimated_trl = innov_resp.trl.estimated_trl
        data_sufficiency = innov_resp.data_sufficiency

        # ---------------------------------------------------------
        # 2. Commercialization Readiness Score (0 - 100)
        # ---------------------------------------------------------
        # Formula: 30% TRL + 25% Patent Strength + 20% Market + 15% Funding + 10% Novelty
        readiness_score = round(
            (0.30 * trl_score)
            + (0.25 * patent_strength_score)
            + (0.20 * market_potential_score)
            + (0.15 * funding_relevance_score)
            + (0.10 * novelty_score),
            2
        ) if data_sufficiency != "INSUFFICIENT_DATA" else 0.0

        readiness_score = min(100.0, max(0.0, readiness_score))

        if readiness_score >= 70.0:
            readiness_level = "HIGH_COMMERCIAL_READINESS"
        elif readiness_score >= 45.0:
            readiness_level = "MODERATE_COMMERCIAL_READINESS"
        elif readiness_score >= 25.0:
            readiness_level = "EARLY_DEVELOPMENT"
        else:
            readiness_level = "BASIC_RESEARCH_STAGE"

        # ---------------------------------------------------------
        # 3. Generate Rule-Based Commercialization Recommendations
        # ---------------------------------------------------------
        recommendations: List[CommercializationRecommendationItem] = []

        if data_sufficiency == "INSUFFICIENT_DATA":
            rec_insufficient = CommercializationRecommendationItem(
                recommendation_type="MONITOR_AND_GATHER_EVIDENCE",
                title="Populate Portfolio & Monitor Technology Field",
                priority="LOW",
                score=10.0,
                confidence="LOW",
                rationale="Insufficient publication and patent records indexed for this target scope.",
                supporting_evidence=["Zero indexed publications or patent disclosures available for analysis."],
                required_next_actions=[
                    "Link existing peer-reviewed publications and patent numbers to researcher profile.",
                    "Ingest external research identifiers (DOI, ORCID, Patent Numbers) to unlock commercialization signals.",
                ],
            )
            recommendations.append(rec_insufficient)
            primary_pathway = "MONITOR_AND_GATHER_EVIDENCE"
        else:
            # Pathway 1: STARTUP_SPINOUT (New Venture Formation)
            if innov_resp.innovation_score >= 65.0 and estimated_trl >= 5 and market_potential_score >= 50.0:
                score_spinout = round(min(100.0, (readiness_score * 0.55 + market_potential_score * 0.45)), 1)
                recommendations.append(
                    CommercializationRecommendationItem(
                        recommendation_type="STARTUP_SPINOUT",
                        title="Form Spinout / Venture Entity",
                        priority="HIGH" if readiness_score >= 65.0 else "MEDIUM",
                        score=score_spinout,
                        confidence="HIGH" if innov_resp.trl.confidence == "HIGH" else "MEDIUM",
                        rationale=f"Strong Innovation Score ({innov_resp.innovation_score:.1f}/100) and validated Technology Readiness (TRL {estimated_trl}) with robust market velocity indicate prime conditions for an independent spinout.",
                        supporting_evidence=[
                            f"Innovation Score: {innov_resp.innovation_score:.1f}/100 ({innov_resp.overall_classification}).",
                            f"Technology Maturity: TRL {estimated_trl} ({innov_resp.trl.trl_stage}).",
                            f"Market Potential Proxy: {market_potential_score:.1f}/100.",
                            f"Patent Strength Proxy: {patent_strength_score:.1f}/100.",
                        ],
                        required_next_actions=[
                            "Engage Institutional Tech Transfer Office (TTO) to negotiate exclusive intellectual property option/license.",
                            "Incorporate venture entity and formalize founder equity allocation.",
                            "Conduct structured customer discovery interviews (e.g. NSF I-Corps framework).",
                            "Prepare seed investor pitch deck emphasizing technical de-risking milestones.",
                        ],
                    )
                )

            # Pathway 2: LICENSING (Corporate IP Out-Licensing)
            if patent_strength_score >= 45.0 and estimated_trl >= 4:
                score_licensing = round(min(100.0, (patent_strength_score * 0.60 + market_potential_score * 0.40)), 1)
                recommendations.append(
                    CommercializationRecommendationItem(
                        recommendation_type="LICENSING",
                        title="Pursue Corporate IP Out-Licensing",
                        priority="HIGH" if patent_strength_score >= 65.0 else "MEDIUM",
                        score=score_licensing,
                        confidence="HIGH" if patent_strength_score >= 60.0 else "MEDIUM",
                        rationale=f"Established patent portfolio strength ({patent_strength_score:.1f}/100) and multi-jurisdiction disclosures enable non-dilutive monetization via corporate patent licensing.",
                        supporting_evidence=[
                            f"Patent Strength Proxy: {patent_strength_score:.1f}/100 with granted claims.",
                            f"Technology Readiness: TRL {estimated_trl} facilitates technology transfer.",
                            f"Commercial Assignee Competition: {innov_resp.pillars['patent_strength'].contributing_signals.get('jurisdiction_count', 1)} international jurisdictions covered.",
                        ],
                        required_next_actions=[
                            "Prepare a Non-Confidential Technology Summary (1-pager) for corporate IP scouts.",
                            "Identify prospective commercial licensees from competitive landscape assignees.",
                            "Benchmark industry royalty rates and standard upfront licensing fee structures.",
                            "Establish non-disclosure agreements (NDA) prior to technical deep-dive demonstrations.",
                        ],
                    )
                )

            # Pathway 3: COMMERCIALIZATION_PREPARATION (Pre-Commercial Roadmap)
            if estimated_trl >= 5 or readiness_score >= 50.0:
                recommendations.append(
                    CommercializationRecommendationItem(
                        recommendation_type="COMMERCIALIZATION_PREPARATION",
                        title="Develop Pre-Commercial Execution Roadmap",
                        priority="HIGH" if estimated_trl >= 6 else "MEDIUM",
                        score=round(readiness_score, 1),
                        confidence="HIGH" if data_sufficiency == "SUFFICIENT" else "MEDIUM",
                        rationale=f"Technology validation (TRL {estimated_trl}) has progressed beyond basic research; commercialization requires structured manufacturing, regulatory, and pricing roadmaps.",
                        supporting_evidence=[
                            f"Commercialization Readiness Score: {readiness_score:.1f}/100 ({readiness_level}).",
                            f"Technology Stage: {innov_resp.trl.trl_stage}.",
                            f"Market Velocity: {market_potential_score:.1f}/100.",
                        ],
                        required_next_actions=[
                            "Formulate regulatory compliance roadmap (e.g. ISO 9001, FDA 510(k), CE mark, or FCC certifications).",
                            "Develop preliminary Bill-of-Materials (BOM) and cost-of-goods-sold (COGS) model.",
                            "Secure pilot testing commitments with initial beta customers or industry testing partners.",
                        ],
                    )
                )

            # Pathway 4: INDUSTRY_COLLABORATION (Joint Development / Sponsored R&D)
            if estimated_trl in [3, 4, 5, 6] or market_potential_score >= 35.0:
                score_ind = round(min(100.0, (market_potential_score * 0.50 + trl_score * 0.50)), 1)
                recommendations.append(
                    CommercializationRecommendationItem(
                        recommendation_type="INDUSTRY_COLLABORATION",
                        title="Establish Industry Co-Development Partnership",
                        priority="HIGH" if estimated_trl in [4, 5] else "MEDIUM",
                        score=score_ind,
                        confidence="HIGH" if data_sufficiency == "SUFFICIENT" else "MEDIUM",
                        rationale=f"Mid-stage technical maturity (TRL {estimated_trl}) benefits from industrial partner co-funding, real-world testbeds, and accelerated translation.",
                        supporting_evidence=[
                            f"Applied Feasibility: TRL {estimated_trl} ({innov_resp.trl.trl_name}).",
                            f"Market Interest Proxy: {market_potential_score:.1f}/100.",
                            f"Research Novelty: {novelty_score:.1f}/100.",
                        ],
                        required_next_actions=[
                            "Execute standard Sponsored Research Agreement (SRA) or Joint Development Agreement (JDA).",
                            "Define clear IP allocation terms for foreground inventions developed under joint testing.",
                            "Co-apply for collaborative translational grants (e.g. NSF Industry-University Cooperative Research Centers).",
                        ],
                    )
                )

            # Pathway 5: STRENGTHEN_IP (Patent Portfolio Expansion)
            if patent_strength_score < 60.0 and (novelty_score >= 35.0 or estimated_trl >= 3):
                score_ip = round(min(100.0, max(20.0, 100.0 - patent_strength_score)), 1)
                recommendations.append(
                    CommercializationRecommendationItem(
                        recommendation_type="STRENGTHEN_IP",
                        title="Protect & Expand Patent Portfolio",
                        priority="HIGH" if patent_strength_score < 35.0 and novelty_score >= 50.0 else "MEDIUM",
                        score=score_ip,
                        confidence="HIGH",
                        rationale=f"High research novelty ({novelty_score:.1f}/100) with moderate patent strength ({patent_strength_score:.1f}/100) exposes discoveries to public forfeiture without timely patent filings.",
                        supporting_evidence=[
                            f"Current Patent Strength: {patent_strength_score:.1f}/100.",
                            f"Research Publication Novelty: {novelty_score:.1f}/100.",
                            "Protection gap: Disclosures require broader international patent coverage.",
                        ],
                        required_next_actions=[
                            "File provisional patent applications before submitting peer-reviewed conference or journal manuscripts.",
                            "Conduct professional patent landscape clearance and prior art searches.",
                            "Evaluate PCT international patent filings for key foreign markets (EP, JP, CN, WO).",
                        ],
                    )
                )

            # Pathway 6: SEEK_FUNDING (Translational / Grant Funding)
            if funding_relevance_score >= 35.0 or innov_resp.pillars["funding_relevance"].contributing_signals.get("matching_opportunities_count", 0) > 0:
                opp_cnt = innov_resp.pillars["funding_relevance"].contributing_signals.get("matching_opportunities_count", 0)
                recommendations.append(
                    CommercializationRecommendationItem(
                        recommendation_type="SEEK_FUNDING",
                        title="Apply for Non-Dilutive Translational Grants",
                        priority="HIGH" if opp_cnt >= 2 else "MEDIUM",
                        score=round(funding_relevance_score, 1),
                        confidence="HIGH" if opp_cnt >= 2 else "MEDIUM",
                        rationale=f"{opp_cnt} matching active funding opportunity stream(s) provide non-dilutive capital to fund technical de-risking and prototype validation.",
                        supporting_evidence=[
                            f"Funding Relevance Score: {funding_relevance_score:.1f}/100.",
                            f"{opp_cnt} active grant opportunity stream(s) matched.",
                            f"Technology Stage: TRL {estimated_trl} eligible for translational solicitations.",
                        ],
                        required_next_actions=[
                            "Review upcoming submission deadlines for matched translational solicitations.",
                            "Tailor proposal specific aims toward commercial milestones (prototype demonstration, field trials).",
                            "Secure industrial letters of support (LOS) to strengthen grant competitiveness.",
                        ],
                    )
                )

            # Pathway 7: VALIDATE_TECHNOLOGY (Laboratory Prototype Validation)
            if estimated_trl in [2, 3, 4] and novelty_score >= 30.0:
                recommendations.append(
                    CommercializationRecommendationItem(
                        recommendation_type="VALIDATE_TECHNOLOGY",
                        title="Conduct Rigorous Laboratory Prototype Validation",
                        priority="HIGH" if estimated_trl in [2, 3] else "MEDIUM",
                        score=round(novelty_score, 1),
                        confidence="HIGH" if data_sufficiency == "SUFFICIENT" else "MEDIUM",
                        rationale=f"Fundamental concept (TRL {estimated_trl}) requires empirical laboratory benchmarking and component validation before commercial scale-up.",
                        supporting_evidence=[
                            f"Technology Readiness: TRL {estimated_trl} ({innov_resp.trl.trl_name}).",
                            f"Research Novelty: {novelty_score:.1f}/100.",
                            f"Publication Evidence: {innov_resp.pillars['research_novelty'].contributing_signals.get('publication_count', 0)} papers indexed.",
                        ],
                        required_next_actions=[
                            "Build standardized experimental testbench to measure operational performance against baseline.",
                            "Document statistical repeatability and error bounds across multiple testing runs.",
                            "Prepare component validation dataset to substantiate patent claims and grant applications.",
                        ],
                    )
                )

            # Pathway 8: RESEARCH_FOCUS (Fundamental Scientific Discovery)
            if estimated_trl <= 2:
                recommendations.append(
                    CommercializationRecommendationItem(
                        recommendation_type="RESEARCH_FOCUS",
                        title="Advance Fundamental Scientific Research",
                        priority="HIGH" if estimated_trl == 1 else "MEDIUM",
                        score=85.0 if estimated_trl == 1 else 60.0,
                        confidence="HIGH" if data_sufficiency == "SUFFICIENT" else "MEDIUM",
                        rationale="Technology is in early theoretical formulation; priority is establishing core scientific proof-of-concept.",
                        supporting_evidence=[
                            f"Current Stage: TRL {estimated_trl} ({innov_resp.trl.trl_stage}).",
                            "Empirical laboratory component validation is in progress.",
                        ],
                        required_next_actions=[
                            "Complete peer-reviewed journal publications detailing foundational mechanisms.",
                            "Seek basic research grants from scientific foundations (e.g. NSF CAREER, NIH R01).",
                        ],
                    )
                )

            # Sort recommendations by score descending
            recommendations.sort(key=lambda r: (0 if r.priority == "HIGH" else 1 if r.priority == "MEDIUM" else 2, -r.score))
            primary_pathway = recommendations[0].recommendation_type if recommendations else "RESEARCH_FOCUS"

        # ---------------------------------------------------------
        # 4. Fetch Integrated Funding Context
        # ---------------------------------------------------------
        funding_query = select(FundingOpportunity).where(
            func.lower(FundingOpportunity.status).in_(["open", "upcoming", "rolling", "active"])
        )
        if domain and domain.strip():
            dom_clean = domain.strip().lower()
            funding_query = funding_query.where(
                or_(
                    func.lower(FundingOpportunity.title).ilike(f"%{dom_clean}%"),
                    func.lower(FundingOpportunity.description).ilike(f"%{dom_clean}%"),
                )
            )
        funding_query = funding_query.limit(5)
        funding_records = (await db.execute(funding_query)).scalars().all()

        funding_list = [
            {
                "id": f.id,
                "title": f.title,
                "funding_agency": f.funding_agency,
                "funding_amount": f.funding_amount,
                "currency": f.currency,
                "application_deadline": f.application_deadline.isoformat() if f.application_deadline else None,
                "status": f.status,
            }
            for f in funding_records
        ]

        # ---------------------------------------------------------
        # 5. Fetch Integrated Whitespace / Tech Intelligence Context
        # ---------------------------------------------------------
        whitespace_resp = await TechnologyIntelligenceService.detect_whitespaces(
            domain=domain, profile_id=profile_id, db=db
        )
        whitespace_context = [
            f"{w.technology_area}: {w.whitespace_type.replace('_', ' ')} (Gap Score: {w.whitespace_score:.1f}/100)"
            for w in whitespace_resp.candidates[:3]
        ] if whitespace_resp.candidates else ["No critical whitespace gaps detected in target focus area."]

        target_name = domain or "Global Technology Portfolio"
        target_type = "DOMAIN"
        if profile_id is not None:
            prof = (await db.execute(select(Profile).where(Profile.id == profile_id))).scalar_one_or_none()
            if prof:
                user = (await db.execute(select(User).where(User.id == prof.user_id))).scalar_one_or_none()
                target_name = user.full_name if user else f"Profile #{profile_id}"
                target_type = "PROFILE"

        readiness_item = CommercializationReadinessItem(
            readiness_score=readiness_score,
            readiness_level=readiness_level,
            dimensions={
                "technology_maturity": trl_score,
                "patent_strength": patent_strength_score,
                "market_potential": market_potential_score,
                "funding_relevance": funding_relevance_score,
                "research_novelty": novelty_score,
            },
            data_sufficiency=data_sufficiency,
            primary_pathway=primary_pathway,
        )

        return CommercializationResponse(
            target_name=target_name,
            target_type=target_type,
            readiness=readiness_item,
            primary_recommendation=recommendations[0],
            recommendations=recommendations,
            innovation_context={
                "innovation_score": innov_resp.innovation_score,
                "overall_classification": innov_resp.overall_classification,
                "estimated_trl": estimated_trl,
                "trl_stage": innov_resp.trl.trl_stage,
                "pillars": {
                    k: {"score": v.score, "weight": v.weight, "weighted_score": v.weighted_score}
                    for k, v in innov_resp.pillars.items()
                },
            },
            funding_opportunities=funding_list,
            whitespace_context=whitespace_context,
        )

    @classmethod
    async def get_summary(
        cls,
        db: AsyncSession = None,
    ) -> CommercializationSummary:
        """
        Cross-domain summary of commercialization readiness and pathway distribution.
        """
        dom_stmt = select(distinct(Patent.technology_domain)).where(Patent.technology_domain.is_not(None)).limit(10)
        domains = (await db.execute(dom_stmt)).scalars().all()

        domain_items: List[DomainCommercializationItem] = []
        readiness_dist: Dict[str, int] = {
            "HIGH_COMMERCIAL_READINESS": 0,
            "MODERATE_COMMERCIAL_READINESS": 0,
            "EARLY_DEVELOPMENT": 0,
            "BASIC_RESEARCH_STAGE": 0,
        }
        pathway_dist: Dict[str, int] = {}
        total_readiness_sum = 0.0

        for d in domains:
            if not d:
                continue
            comm_resp = await cls.evaluate_commercialization(domain=d, db=db)
            total_readiness_sum += comm_resp.readiness.readiness_score

            readiness_dist[comm_resp.readiness.readiness_level] = readiness_dist.get(comm_resp.readiness.readiness_level, 0) + 1
            pathway_dist[comm_resp.readiness.primary_pathway] = pathway_dist.get(comm_resp.readiness.primary_pathway, 0) + 1

            domain_items.append(
                DomainCommercializationItem(
                    domain=d,
                    readiness_score=comm_resp.readiness.readiness_score,
                    readiness_level=comm_resp.readiness.readiness_level,
                    primary_pathway=comm_resp.readiness.primary_pathway,
                    estimated_trl=comm_resp.innovation_context.get("estimated_trl", 1),
                    innovation_score=comm_resp.innovation_context.get("innovation_score", 0.0),
                    recommendation_count=len(comm_resp.recommendations),
                )
            )

        domain_items.sort(key=lambda x: x.readiness_score, reverse=True)
        avg_readiness = round(total_readiness_sum / float(max(1, len(domain_items))), 2) if domain_items else 0.0

        return CommercializationSummary(
            total_evaluations=len(domain_items),
            average_readiness_score=avg_readiness,
            readiness_distribution=readiness_dist,
            pathway_distribution=pathway_dist,
            top_commercial_prospects=domain_items,
        )
