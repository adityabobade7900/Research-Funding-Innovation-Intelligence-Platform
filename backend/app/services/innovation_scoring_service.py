from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import select, func, distinct, and_, or_, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.publication import Publication, profile_publications
from app.models.patent import Patent, profile_patents
from app.models.funding import FundingOpportunity
from app.models.profile import Profile
from app.models.user import User
from app.schemas.innovation_scoring import (
    PillarScoreItem,
    TRLEstimationItem,
    InnovationScoreResponse,
    DomainInnovationItem,
    InnovationScoringSummary,
)
from app.services.trl_service import TRLService
from app.services.technology_intelligence_service import TechnologyIntelligenceService


class InnovationScoringService:
    """
    Deterministic Multi-Factor Innovation Scoring Engine.
    Combines the 5 canonical specification pillars:
      1. Research Novelty (30%)
      2. Patent Strength (20%)
      3. Technology Maturity / TRL (15%)
      4. Market Potential (20%)
      5. Funding Relevance (15%)
    """

    @classmethod
    async def calculate_innovation_score(
        cls,
        domain: Optional[str] = None,
        profile_id: Optional[int] = None,
        db: AsyncSession = None,
    ) -> InnovationScoreResponse:
        """
        Calculates the comprehensive 5-pillar Innovation Score for a researcher profile or technology domain.
        """
        current_year = datetime.now(timezone.utc).year
        recent_pub_year = current_year - 3
        recent_patent_year = current_year - 2

        # ---------------------------------------------------------
        # 1. Gather Publication Evidence (Research Novelty)
        # ---------------------------------------------------------
        pub_stmt = select(
            func.count(Publication.id).label("total_pubs"),
            func.sum(case((func.extract("year", Publication.publication_date) >= recent_pub_year, 1), else_=0)).label("recent_pubs"),
            func.coalesce(func.sum(Publication.citation_count), 0).label("total_citations"),
            func.coalesce(func.avg(Publication.citation_count), 0.0).label("avg_citations"),
            func.count(distinct(func.lower(func.coalesce(Publication.venue, "Unknown")))).label("venue_count"),
        )
        if profile_id is not None:
            pub_stmt = pub_stmt.join(profile_publications, profile_publications.c.publication_id == Publication.id)\
                               .where(profile_publications.c.profile_id == profile_id)
        if domain and domain.strip():
            dom_clean = domain.strip().lower()
            pub_stmt = pub_stmt.where(
                or_(
                    func.lower(Publication.primary_domain).ilike(f"%{dom_clean}%"),
                    func.lower(Publication.title).ilike(f"%{dom_clean}%"),
                    func.lower(Publication.abstract).ilike(f"%{dom_clean}%"),
                )
            )

        pub_row = (await db.execute(pub_stmt)).one()
        pub_count = int(pub_row.total_pubs or 0)
        recent_pub_count = int(pub_row.recent_pubs or 0)
        total_pub_citations = int(pub_row.total_citations or 0)
        avg_pub_citations = round(float(pub_row.avg_citations or 0.0), 2)
        venue_count = int(pub_row.venue_count or 0)

        # ---------------------------------------------------------
        # 2. Gather Patent Evidence (Patent Strength)
        # ---------------------------------------------------------
        patent_stmt = select(
            func.count(Patent.id).label("total_patents"),
            func.sum(case((Patent.patent_number.ilike("%B%"), 1), else_=0)).label("granted_patents"),
            func.sum(case((func.extract("year", Patent.filing_date) >= recent_patent_year, 1), else_=0)).label("recent_patents"),
            func.coalesce(func.sum(Patent.citation_count), 0).label("total_citations"),
            func.coalesce(func.avg(Patent.citation_count), 0.0).label("avg_citations"),
            func.count(distinct(func.lower(func.coalesce(Patent.assignee, "Individual")))).label("assignee_count"),
            func.count(distinct(Patent.patent_classification)).label("classification_count"),
        )
        if profile_id is not None:
            patent_stmt = patent_stmt.join(profile_patents, profile_patents.c.patent_id == Patent.id)\
                                     .where(profile_patents.c.profile_id == profile_id)
        if domain and domain.strip():
            dom_clean = domain.strip().lower()
            patent_stmt = patent_stmt.where(func.lower(Patent.technology_domain) == dom_clean)

        patent_row = (await db.execute(patent_stmt)).one()
        patent_count = int(patent_row.total_patents or 0)
        granted_patent_count = int(patent_row.granted_patents or 0)
        recent_patent_count = int(patent_row.recent_patents or 0)
        total_patent_citations = int(patent_row.total_citations or 0)
        avg_patent_citations = round(float(patent_row.avg_citations or 0.0), 2)
        assignee_count = int(patent_row.assignee_count or 0)
        classification_count = int(patent_row.classification_count or 0)

        # Fetch distinct jurisdictions
        jur_stmt = select(Patent.patent_number).limit(50)
        if profile_id is not None:
            jur_stmt = jur_stmt.join(profile_patents, profile_patents.c.patent_id == Patent.id)\
                               .where(profile_patents.c.profile_id == profile_id)
        if domain and domain.strip():
            jur_stmt = jur_stmt.where(func.lower(Patent.technology_domain) == domain.strip().lower())

        jur_rows = (await db.execute(jur_stmt)).scalars().all()
        jurisdictions = set()
        has_industrial_assignee = False
        for p_num in jur_rows:
            if p_num:
                jurisdictions.add(TechnologyIntelligenceService._extract_jurisdiction_code(p_num))

        if assignee_count >= 2 or any(k in str(jur_rows).lower() for k in ["corp", "inc", "ltd", "gmbh", "technologies", "llc"]):
            has_industrial_assignee = True

        jurisdiction_count = len(jurisdictions)

        # ---------------------------------------------------------
        # 3. Gather Funding Evidence (Funding Relevance)
        # ---------------------------------------------------------
        funding_stmt = select(
            func.count(FundingOpportunity.id).label("total_opps"),
            func.count(distinct(func.lower(FundingOpportunity.funding_agency))).label("agency_count"),
            func.coalesce(func.avg(FundingOpportunity.funding_amount), 0.0).label("avg_funding"),
        ).where(func.lower(FundingOpportunity.status).in_(["open", "upcoming", "rolling", "active"]))

        if domain and domain.strip():
            dom_clean = domain.strip().lower()
            funding_stmt = funding_stmt.where(
                or_(
                    func.lower(FundingOpportunity.title).ilike(f"%{dom_clean}%"),
                    func.lower(FundingOpportunity.description).ilike(f"%{dom_clean}%"),
                )
            )

        funding_row = (await db.execute(funding_stmt)).one()
        funding_opp_count = int(funding_row.total_opps or 0)
        funding_agency_count = int(funding_row.agency_count or 0)

        # ---------------------------------------------------------
        # 4. Gather Market Velocity Evidence (Market Potential)
        # ---------------------------------------------------------
        growth_resp = await TechnologyIntelligenceService.get_technology_growth(
            domain=domain, profile_id=profile_id, db=db
        )
        if growth_resp.items:
            avg_velocity = sum(g.velocity_score for g in growth_resp.items) / float(len(growth_resp.items))
            growing_areas_count = growth_resp.total_growing_areas
        else:
            avg_velocity = 20.0 if patent_count > 0 else 0.0
            growing_areas_count = 0

        # =========================================================
        # PILLAR 1: Research Novelty (Weight 30%)
        # =========================================================
        novelty_evidence: List[str] = []
        recent_pub_ratio = (recent_pub_count / float(max(1, pub_count))) if pub_count > 0 else 0.0
        
        vol_novelty = min(100.0, pub_count * 12.5)
        rec_novelty = min(100.0, recent_pub_ratio * 100.0)
        cit_novelty = min(100.0, avg_pub_citations * 5.0)
        div_novelty = min(100.0, max(1, venue_count) * 20.0)

        novelty_score = round(
            (0.25 * vol_novelty) + (0.30 * rec_novelty) + (0.25 * cit_novelty) + (0.20 * div_novelty),
            2
        ) if pub_count > 0 else 0.0

        if pub_count > 0:
            novelty_evidence.append(f"{pub_count} peer-reviewed research publication(s) indexed with {recent_pub_count} recent papers (last 36 months).")
            novelty_evidence.append(f"Citation velocity averaging {avg_pub_citations:.1f} citations per publication ({total_pub_citations} total citations).")
            if venue_count >= 2:
                novelty_evidence.append(f"Broad dissemination across {venue_count} distinct academic journals/venues.")
        else:
            novelty_evidence.append("No indexed research publications found in target scope.")

        novelty_pillar = PillarScoreItem(
            pillar_name="Research Novelty",
            score=novelty_score,
            weight=0.30,
            weighted_score=round(novelty_score * 0.30, 2),
            is_proxy=True,
            confidence="HIGH" if pub_count >= 5 else "MEDIUM" if pub_count >= 2 else "LOW",
            contributing_signals={
                "publication_count": pub_count,
                "recent_publication_count": recent_pub_count,
                "recent_publication_ratio": round(recent_pub_ratio, 2),
                "average_citations": avg_pub_citations,
                "venue_diversity_count": venue_count,
            },
            evidence=novelty_evidence,
            methodology_notes="Empirical Research Novelty Proxy calculated from publication volume, recency ratio, citation impact density, and venue diversity."
        )

        # =========================================================
        # PILLAR 2: Patent Strength (Weight 20%)
        # =========================================================
        patent_evidence: List[str] = []
        grant_ratio = (granted_patent_count / float(max(1, patent_count))) if patent_count > 0 else 0.0

        vol_patent = min(100.0, patent_count * 15.0)
        grt_patent = min(100.0, grant_ratio * 100.0)
        cit_patent = min(100.0, avg_patent_citations * 5.0)
        jur_patent = min(100.0, max(1, jurisdiction_count) * 33.3)

        patent_strength_score = round(
            (0.30 * vol_patent) + (0.30 * grt_patent) + (0.20 * cit_patent) + (0.20 * jur_patent),
            2
        ) if patent_count > 0 else 0.0

        if patent_count > 0:
            patent_evidence.append(f"Patent portfolio of {patent_count} disclosure(s) with {granted_patent_count} granted patent(s).")
            patent_evidence.append(f"International protection across {jurisdiction_count} jurisdiction authority codes ({', '.join(jurisdictions) or 'Regional'}).")
            if avg_patent_citations > 0:
                patent_evidence.append(f"Cumulative citation impact of {total_patent_citations} citations (average {avg_patent_citations:.1f} per patent).")
        else:
            patent_evidence.append("No patent disclosures or IP filings registered in target scope.")

        patent_pillar = PillarScoreItem(
            pillar_name="Patent Strength",
            score=patent_strength_score,
            weight=0.20,
            weighted_score=round(patent_strength_score * 0.20, 2),
            is_proxy=True,
            confidence="HIGH" if patent_count >= 4 else "MEDIUM" if patent_count >= 1 else "LOW",
            contributing_signals={
                "patent_count": patent_count,
                "granted_patent_count": granted_patent_count,
                "grant_conversion_rate": round(grant_ratio, 2),
                "jurisdiction_count": jurisdiction_count,
                "average_citations": avg_patent_citations,
                "classification_count": classification_count,
            },
            evidence=patent_evidence,
            methodology_notes="Empirical Patent Strength Proxy calculated from patent volume, grant conversion rate, citation density, and international jurisdiction coverage."
        )

        # =========================================================
        # PILLAR 3: Technology Maturity / TRL (Weight 15%)
        # =========================================================
        trl_item = TRLService.estimate_trl(
            pub_count=pub_count,
            recent_pub_count=recent_pub_count,
            avg_pub_citations=avg_pub_citations,
            patent_count=patent_count,
            granted_patent_count=granted_patent_count,
            jurisdiction_count=jurisdiction_count,
            assignee_count=assignee_count,
            has_industrial_assignee=has_industrial_assignee,
            active_funding_count=funding_opp_count,
        )

        trl_pillar = PillarScoreItem(
            pillar_name="Technology Maturity",
            score=trl_item.score,
            weight=0.15,
            weighted_score=round(trl_item.score * 0.15, 2),
            is_proxy=True,
            confidence=trl_item.confidence,
            contributing_signals={
                "estimated_trl": trl_item.estimated_trl,
                "trl_stage": trl_item.trl_stage,
                "trl_name": trl_item.trl_name,
                "granted_patents": granted_patent_count,
                "publications_count": pub_count,
            },
            evidence=trl_item.evidence,
            methodology_notes="Empirical Technology Maturity Score normalized from 9-stage Technology Readiness Level (TRL) rule evaluation engine."
        )

        # =========================================================
        # PILLAR 4: Market Potential (Weight 20%)
        # =========================================================
        market_evidence: List[str] = []
        vel_market = min(100.0, avg_velocity)
        ass_market = min(100.0, assignee_count * 25.0)
        dom_market = min(100.0, (patent_count + pub_count) * 8.0)

        market_score = round(
            (0.35 * vel_market) + (0.35 * ass_market) + (0.30 * dom_market),
            2
        ) if (patent_count + pub_count) > 0 else 0.0

        if (patent_count + pub_count) > 0:
            market_evidence.append(f"Domain filing velocity of {avg_velocity:.1f}% in target technology area.")
            if assignee_count >= 2:
                market_evidence.append(f"Commercial competition indicated by {assignee_count} distinct active applicants/organizations.")
            if growing_areas_count > 0:
                market_evidence.append(f"Aligned with {growing_areas_count} accelerating high-growth technology subfields.")
        else:
            market_evidence.append("Insufficient empirical market velocity data recorded.")

        market_pillar = PillarScoreItem(
            pillar_name="Market Potential",
            score=market_score,
            weight=0.20,
            weighted_score=round(market_score * 0.20, 2),
            is_proxy=True,
            confidence="HIGH" if assignee_count >= 3 else "MEDIUM" if (patent_count + pub_count) >= 3 else "LOW",
            contributing_signals={
                "velocity_score": round(avg_velocity, 2),
                "assignee_count": assignee_count,
                "growing_subfields_count": growing_areas_count,
                "combined_ip_portfolio": patent_count + pub_count,
            },
            evidence=market_evidence,
            methodology_notes="Empirical Market Potential Proxy derived from patent filing velocity, commercial assignee competition density, and domain expansion rates."
        )

        # =========================================================
        # PILLAR 5: Funding Relevance (Weight 15%)
        # =========================================================
        funding_evidence: List[str] = []
        opp_score = min(100.0, funding_opp_count * 20.0)
        agency_score = min(100.0, funding_agency_count * 25.0)
        match_score = 80.0 if funding_opp_count >= 3 else 50.0 if funding_opp_count >= 1 else 0.0

        funding_score = round(
            (0.40 * opp_score) + (0.35 * match_score) + (0.25 * agency_score),
            2
        ) if funding_opp_count > 0 else 0.0

        if funding_opp_count > 0:
            funding_evidence.append(f"{funding_opp_count} active funding opportunity streams matching target research domain.")
            funding_evidence.append(f"Sponsored across {funding_agency_count} distinct grant funding agencies.")
        else:
            funding_evidence.append("No active matching funding opportunities currently indexed for this domain.")

        funding_pillar = PillarScoreItem(
            pillar_name="Funding Relevance",
            score=funding_score,
            weight=0.15,
            weighted_score=round(funding_score * 0.15, 2),
            is_proxy=True,
            confidence="HIGH" if funding_opp_count >= 3 else "MEDIUM" if funding_opp_count >= 1 else "LOW",
            contributing_signals={
                "matching_opportunities_count": funding_opp_count,
                "funding_agency_count": funding_agency_count,
                "opportunity_density_score": opp_score,
            },
            evidence=funding_evidence,
            methodology_notes="Empirical Funding Relevance Score calculated from active funding grant volume, sponsor agency breadth, and research taxonomy compatibility."
        )

        # =========================================================
        # Composite Innovation Score & Synthesis
        # =========================================================
        composite_score = round(
            novelty_pillar.weighted_score
            + patent_pillar.weighted_score
            + trl_pillar.weighted_score
            + market_pillar.weighted_score
            + funding_pillar.weighted_score,
            2
        )
        composite_score = min(100.0, max(0.0, composite_score))

        # Overall Classification
        if composite_score >= 75.0:
            classification = "BREAKTHROUGH_INNOVATION"
        elif composite_score >= 60.0:
            classification = "HIGH_POTENTIAL"
        elif composite_score >= 40.0:
            classification = "DEVELOPING_CAPABILITY"
        else:
            classification = "EARLY_STAGE_EXPLORATORY"

        # Data Sufficiency Evaluation
        total_records = pub_count + patent_count
        if total_records >= 4 and pub_count >= 1 and patent_count >= 1:
            data_sufficiency = "SUFFICIENT"
        elif total_records >= 1:
            data_sufficiency = "PARTIAL_EVIDENCE"
        else:
            data_sufficiency = "INSUFFICIENT_DATA"

        # Key strengths and growth areas
        pillars_sorted = sorted(
            [novelty_pillar, patent_pillar, trl_pillar, market_pillar, funding_pillar],
            key=lambda p: p.score,
            reverse=True
        )
        key_strengths = [
            f"{p.pillar_name}: {p.score:.1f}/100 — {p.evidence[0]}"
            for p in pillars_sorted if p.score >= 50.0
        ]
        areas_for_growth = [
            f"{p.pillar_name}: {p.score:.1f}/100 — {p.evidence[-1]}"
            for p in reversed(pillars_sorted) if p.score < 50.0
        ]

        target_name = domain or "Global Technology Portfolio"
        target_type = "DOMAIN"
        if profile_id is not None:
            prof = (await db.execute(select(Profile).where(Profile.id == profile_id))).scalar_one_or_none()
            if prof:
                user = (await db.execute(select(User).where(User.id == prof.user_id))).scalar_one_or_none()
                target_name = user.full_name if user else f"Profile #{profile_id}"
                target_type = "PROFILE"

        return InnovationScoreResponse(
            target_name=target_name,
            target_type=target_type,
            innovation_score=composite_score,
            overall_classification=classification,
            data_sufficiency=data_sufficiency,
            pillars={
                "research_novelty": novelty_pillar,
                "patent_strength": patent_pillar,
                "technology_maturity": trl_pillar,
                "market_potential": market_pillar,
                "funding_relevance": funding_pillar,
            },
            trl=trl_item,
            key_strengths=key_strengths or ["Early-stage exploration across emerging research concepts."],
            areas_for_growth=areas_for_growth or ["Continue expanding multi-jurisdiction patent disclosures."],
        )

    @classmethod
    async def get_summary(
        cls,
        db: AsyncSession = None,
    ) -> InnovationScoringSummary:
        """
        Aggregates innovation scoring statistics across all major indexed technology domains.
        """
        # Fetch distinct technology domains from patents
        dom_stmt = select(distinct(Patent.technology_domain)).where(Patent.technology_domain.is_not(None)).limit(10)
        domains = (await db.execute(dom_stmt)).scalars().all()

        domain_items: List[DomainInnovationItem] = []
        trl_dist: Dict[str, int] = {}
        class_dist: Dict[str, int] = {
            "BREAKTHROUGH_INNOVATION": 0,
            "HIGH_POTENTIAL": 0,
            "DEVELOPING_CAPABILITY": 0,
            "EARLY_STAGE_EXPLORATORY": 0,
        }

        total_score_sum = 0.0

        for d in domains:
            if not d:
                continue
            score_resp = await cls.calculate_innovation_score(domain=d, db=db)
            total_score_sum += score_resp.innovation_score

            trl_stage_key = f"TRL {score_resp.trl.estimated_trl} ({score_resp.trl.trl_stage})"
            trl_dist[trl_stage_key] = trl_dist.get(trl_stage_key, 0) + 1
            class_dist[score_resp.overall_classification] = class_dist.get(score_resp.overall_classification, 0) + 1

            # Count publications and patents in this domain
            p_cnt = (await db.execute(select(func.count(Patent.id)).where(Patent.technology_domain == d))).scalar() or 0
            pub_cnt = (await db.execute(select(func.count(Publication.id)).where(
                or_(
                    func.lower(Publication.title).ilike(f"%{d.lower()}%"),
                    func.lower(Publication.abstract).ilike(f"%{d.lower()}%"),
                )
            ))).scalar() or 0

            domain_items.append(
                DomainInnovationItem(
                    domain=d,
                    innovation_score=score_resp.innovation_score,
                    estimated_trl=score_resp.trl.estimated_trl,
                    data_sufficiency=score_resp.data_sufficiency,
                    publication_count=p_cnt,
                    patent_count=pub_cnt,
                )
            )

        domain_items.sort(key=lambda x: x.innovation_score, reverse=True)
        avg_score = round(total_score_sum / float(max(1, len(domain_items))), 2) if domain_items else 0.0

        return InnovationScoringSummary(
            total_evaluations=len(domain_items),
            average_innovation_score=avg_score,
            trl_distribution=trl_dist,
            classification_distribution=class_dist,
            top_innovating_domains=domain_items,
        )
