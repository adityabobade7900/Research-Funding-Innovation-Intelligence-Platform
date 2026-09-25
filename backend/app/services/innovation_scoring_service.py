from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import select, func, distinct, and_, or_, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.publication import Publication, profile_publications
from app.models.patent import Patent, profile_patents
from app.models.funding import FundingOpportunity
from app.models.profile import Profile
from app.models.user import User
from app.models.research_domain import ResearchDomain, ResearchInterest, ProfileKeyword, profile_domains
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
      3. Technology Maturity / TRL (15%) - Integrates Module 6 Technology Maturity & NASA/DoD TRL
      4. Market Potential (20%) - Decoupled from publication volume; uses patent velocity and assignee density
      5. Funding Relevance (15%) - Isolated to researcher profile domains/interests; includes missing-data policy
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
                    func.lower(Publication.primary_domain) == dom_clean,
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
            patent_stmt = patent_stmt.where(
                or_(
                    func.lower(Patent.technology_domain) == dom_clean,
                    func.lower(Patent.technology_domain).ilike(f"%{dom_clean}%"),
                    func.lower(Patent.title).ilike(f"%{dom_clean}%"),
                    func.lower(Patent.abstract).ilike(f"%{dom_clean}%"),
                )
            )

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
            dom_clean = domain.strip().lower()
            jur_stmt = jur_stmt.where(
                or_(
                    func.lower(Patent.technology_domain) == dom_clean,
                    func.lower(Patent.technology_domain).ilike(f"%{dom_clean}%"),
                )
            )

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
        # Profile Terms & Blank Profile Resolution
        # ---------------------------------------------------------
        profile_terms: List[str] = []
        is_blank_profile = False

        if profile_id is not None:
            # 1. Registered research domains
            d_stmt = select(ResearchDomain.name)\
                .join(profile_domains, profile_domains.c.domain_id == ResearchDomain.id)\
                .where(profile_domains.c.profile_id == profile_id)
            p_domains = (await db.execute(d_stmt)).scalars().all()
            profile_terms.extend([d.strip() for d in p_domains if d and d.strip()])

            # 2. Registered interests
            i_stmt = select(ResearchInterest.title).where(ResearchInterest.profile_id == profile_id)
            p_interests = (await db.execute(i_stmt)).scalars().all()
            profile_terms.extend([i.strip() for i in p_interests if i and i.strip()])

            # 3. Registered keywords
            k_stmt = select(ProfileKeyword.keyword).where(ProfileKeyword.profile_id == profile_id)
            p_keywords = (await db.execute(k_stmt)).scalars().all()
            profile_terms.extend([k.strip() for k in p_keywords if k and k.strip()])

            # 4. Publication primary domains
            pub_dom_stmt = select(distinct(Publication.primary_domain))\
                .join(profile_publications, profile_publications.c.publication_id == Publication.id)\
                .where(profile_publications.c.profile_id == profile_id, Publication.primary_domain.is_not(None))
            p_pub_doms = (await db.execute(pub_dom_stmt)).scalars().all()
            profile_terms.extend([pd.strip() for pd in p_pub_doms if pd and pd.strip()])

            # 5. Patent technology domains
            pat_dom_stmt = select(distinct(Patent.technology_domain))\
                .join(profile_patents, profile_patents.c.patent_id == Patent.id)\
                .where(profile_patents.c.profile_id == profile_id, Patent.technology_domain.is_not(None))
            p_pat_doms = (await db.execute(pat_dom_stmt)).scalars().all()
            profile_terms.extend([ptd.strip() for ptd in p_pat_doms if ptd and ptd.strip()])

            profile_terms = list(dict.fromkeys(profile_terms))
            if not profile_terms and pub_count == 0 and patent_count == 0:
                is_blank_profile = True

        # ---------------------------------------------------------
        # 3. Gather Funding Evidence (Funding Relevance & Isolation)
        # ---------------------------------------------------------
        funding_opp_count = 0
        funding_agency_count = 0
        funding_is_unindexed = False

        if profile_id is not None:
            if is_blank_profile:
                funding_opp_count = 0
                funding_agency_count = 0
            elif profile_terms:
                funding_stmt = select(
                    func.count(FundingOpportunity.id).label("total_opps"),
                    func.count(distinct(func.lower(FundingOpportunity.funding_agency))).label("agency_count"),
                    func.coalesce(func.avg(FundingOpportunity.funding_amount), 0.0).label("avg_funding"),
                ).where(func.lower(FundingOpportunity.status).in_(["open", "upcoming", "rolling", "active"]))

                term_clauses = []
                for term in profile_terms[:10]:
                    t_clean = term.lower()
                    term_clauses.append(func.lower(FundingOpportunity.title).ilike(f"%{t_clean}%"))
                    term_clauses.append(func.lower(FundingOpportunity.description).ilike(f"%{t_clean}%"))

                funding_stmt = funding_stmt.where(or_(*term_clauses))
                funding_row = (await db.execute(funding_stmt)).one()
                funding_opp_count = int(funding_row.total_opps or 0)
                funding_agency_count = int(funding_row.agency_count or 0)
                if funding_opp_count == 0:
                    funding_is_unindexed = True
            else:
                funding_opp_count = 0
                funding_is_unindexed = True
        elif domain and domain.strip():
            dom_clean = domain.strip().lower()
            funding_stmt = select(
                func.count(FundingOpportunity.id).label("total_opps"),
                func.count(distinct(func.lower(FundingOpportunity.funding_agency))).label("agency_count"),
                func.coalesce(func.avg(FundingOpportunity.funding_amount), 0.0).label("avg_funding"),
            ).where(func.lower(FundingOpportunity.status).in_(["open", "upcoming", "rolling", "active"]))\
             .where(
                 or_(
                     func.lower(FundingOpportunity.title).ilike(f"%{dom_clean}%"),
                     func.lower(FundingOpportunity.description).ilike(f"%{dom_clean}%"),
                 )
             )
            funding_row = (await db.execute(funding_stmt)).one()
            funding_opp_count = int(funding_row.total_opps or 0)
            funding_agency_count = int(funding_row.agency_count or 0)
            if funding_opp_count == 0:
                funding_is_unindexed = True
        else:
            # Global portfolio scope
            if pub_count == 0 and patent_count == 0:
                funding_opp_count = 0
                funding_agency_count = 0
                funding_is_unindexed = True
            else:
                funding_stmt = select(
                    func.count(FundingOpportunity.id).label("total_opps"),
                    func.count(distinct(func.lower(FundingOpportunity.funding_agency))).label("agency_count"),
                    func.coalesce(func.avg(FundingOpportunity.funding_amount), 0.0).label("avg_funding"),
                ).where(func.lower(FundingOpportunity.status).in_(["open", "upcoming", "rolling", "active"]))
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
            novelty_data_status = "AVAILABLE"
        else:
            novelty_evidence.append("No indexed research publications found in target scope.")
            novelty_data_status = "INSUFFICIENT_DATA"

        novelty_pillar = PillarScoreItem(
            pillar_name="Research Novelty",
            score=novelty_score,
            weight=0.30,
            weighted_score=round(novelty_score * 0.30, 2),
            is_proxy=True,
            confidence="HIGH" if pub_count >= 5 else "MEDIUM" if pub_count >= 2 else "LOW",
            data_status=novelty_data_status,
            normalization_method="Bounded multi-metric linear proxy (25% volume, 30% recency ratio, 25% citation impact, 20% venue diversity) scaled to 0-100",
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
            patent_data_status = "AVAILABLE"
        else:
            patent_evidence.append("No patent disclosures or IP filings registered in target scope.")
            patent_data_status = "INSUFFICIENT_DATA"

        patent_pillar = PillarScoreItem(
            pillar_name="Patent Strength",
            score=patent_strength_score,
            weight=0.20,
            weighted_score=round(patent_strength_score * 0.20, 2),
            is_proxy=True,
            confidence="HIGH" if patent_count >= 4 else "MEDIUM" if patent_count >= 1 else "LOW",
            data_status=patent_data_status,
            normalization_method="Bounded multi-metric linear proxy (30% volume, 30% grant conversion, 20% citations, 20% international jurisdictions) scaled to 0-100",
            contributing_signals={
                "patent_count": patent_count,
                "granted_patent_count": granted_patent_count,
                "grant_conversion_rate": round(grant_ratio, 2),
                "jurisdiction_count": jurisdiction_count,
                "average_citations": avg_patent_citations,
                "classification_count": classification_count,
                "assignee_count": assignee_count,
            },
            evidence=patent_evidence,
            methodology_notes="Empirical Patent Strength Proxy calculated from patent volume, grant conversion rate, citation density, and international jurisdiction coverage."
        )

        # =========================================================
        # PILLAR 3: Technology Maturity / TRL (Weight 15%)
        # Module 6 Integration: 50% Module 6 Maturity + 50% TRL Score
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
        trl_norm_score = trl_item.score

        # Query Module 6 verified Technology Maturity Model
        m6_maturity_score = 0.0
        m6_stage = "INSUFFICIENT_DATA"
        m6_evidence: List[str] = []

        try:
            m6_maturity_resp = await TechnologyIntelligenceService.get_technology_maturity(
                domain=domain,
                profile_id=profile_id,
                db=db,
            )
            if m6_maturity_resp.items:
                m6_target = m6_maturity_resp.items[0]
                m6_maturity_score = m6_target.maturity_score
                m6_stage = m6_target.stage
                m6_evidence = m6_target.evidence
        except Exception:
            m6_maturity_score = trl_norm_score
            m6_stage = trl_item.trl_stage

        # Deterministic 50/50 blend: (0.50 * Module 6 Maturity) + (0.50 * TRL Normalized Score)
        if (pub_count + patent_count) > 0:
            tech_maturity_score = round(
                (0.50 * m6_maturity_score) + (0.50 * trl_norm_score),
                2
            )
            tech_maturity_data_status = "AVAILABLE"
        else:
            tech_maturity_score = 0.0
            tech_maturity_data_status = "INSUFFICIENT_DATA"

        tech_maturity_score = min(100.0, max(0.0, tech_maturity_score))

        maturity_evidence = [
            f"Module 6 Technology Maturity: {m6_maturity_score:.1f}/100 (Lifecycle Stage: {m6_stage}).",
            f"NASA/DoD Technology Readiness: TRL {trl_item.estimated_trl} ({trl_item.trl_stage}, {trl_norm_score:.1f}/100).",
        ]
        if m6_evidence:
            maturity_evidence.append(m6_evidence[0])
        if trl_item.evidence:
            maturity_evidence.append(trl_item.evidence[0])

        trl_pillar = PillarScoreItem(
            pillar_name="Technology Maturity",
            score=tech_maturity_score,
            weight=0.15,
            weighted_score=round(tech_maturity_score * 0.15, 2),
            is_proxy=True,
            confidence=trl_item.confidence,
            data_status=tech_maturity_data_status,
            normalization_method="Deterministic 50/50 blend: (0.50 * Module 6 Maturity Score) + (0.50 * (TRL / 9.0 * 100))",
            contributing_signals={
                "module6_maturity_score": m6_maturity_score,
                "module6_lifecycle_stage": m6_stage,
                "estimated_trl": trl_item.estimated_trl,
                "trl_normalized_score": trl_norm_score,
                "blend_formulation": "50% Module 6 Maturity + 50% TRL Readiness Score",
                "blend_rationale": "A transparent implementation choice used to integrate Module 6 maturity with the required NASA/DoD TRL-derived readiness signal.",
                "granted_patents": granted_patent_count,
                "publications_count": pub_count,
            },
            evidence=maturity_evidence,
            methodology_notes="The 50/50 blend is a transparent implementation choice used to integrate Module 6 maturity with the required NASA/DoD TRL-derived readiness signal. The overall Technology Maturity pillar weight is exactly 15%."
        )

        # =========================================================
        # PILLAR 4: Market Potential (Weight 20%)
        # Decoupled from publication volume; uses Module 6 growth velocity and assignee density
        # =========================================================
        market_evidence: List[str] = []
        vel_market = min(100.0, avg_velocity)
        ass_market = min(100.0, assignee_count * 25.0)
        mom_market = min(100.0, (patent_count * 12.0) + (jurisdiction_count * 20.0))

        if patent_count > 0 or avg_velocity > 0:
            market_score = round(
                (0.35 * vel_market) + (0.35 * ass_market) + (0.30 * mom_market),
                2
            )
            market_data_status = "AVAILABLE"
            market_confidence = "HIGH" if assignee_count >= 3 else "MEDIUM" if patent_count >= 2 else "LOW"
            market_evidence.append(f"Module 6 growth velocity of {avg_velocity:.1f}% across target technology domain.")
            if assignee_count >= 1:
                market_evidence.append(f"Commercial competition indicated by {assignee_count} distinct active applicants/organizations.")
            if jurisdiction_count >= 1:
                market_evidence.append(f"Commercial protection breadth across {jurisdiction_count} international patent jurisdiction(s).")
            market_evidence.append("Commercial adoption telemetry status: DATA_UNAVAILABLE; proxy indicators used (filing velocity, applicant diversity, jurisdiction momentum).")
        else:
            market_score = 0.0
            market_data_status = "INSUFFICIENT_DATA"
            market_confidence = "LOW"
            market_evidence.append("Insufficient empirical patent filing momentum or commercial competition data recorded.")
            market_evidence.append("Commercial adoption telemetry status: DATA_UNAVAILABLE (no commercial sales telemetry).")

        market_pillar = PillarScoreItem(
            pillar_name="Market Potential",
            score=market_score,
            weight=0.20,
            weighted_score=round(market_score * 0.20, 2),
            is_proxy=True,
            confidence=market_confidence,
            data_status=market_data_status,
            normalization_method="Linear weighted multi-factor proxy (35% Module 6 growth velocity, 35% commercial assignee competition density, 30% patent momentum/jurisdiction breadth); commercial adoption telemetry is DATA_UNAVAILABLE.",
            contributing_signals={
                "velocity_score": round(avg_velocity, 2),
                "module6_growth_velocity": round(avg_velocity, 2),
                "assignee_count": assignee_count,
                "growing_subfields_count": growing_areas_count,
                "patent_count": patent_count,
                "jurisdiction_count": jurisdiction_count,
                "commercial_adoption_telemetry": "DATA_UNAVAILABLE",
            },
            evidence=market_evidence,
            methodology_notes="Empirical Market Potential Proxy derived from Module 6 technology growth velocity (35%), commercial assignee competition density (35%), and jurisdiction breadth (30%). Commercial adoption telemetry is currently DATA_UNAVAILABLE and is not fabricated."
        )

        # =========================================================
        # PILLAR 5: Funding Relevance (Weight 15%)
        # Includes deterministic missing-data policy and profile isolation
        # =========================================================
        funding_evidence: List[str] = []
        if is_blank_profile:
            funding_score = 0.0
            funding_data_status = "INSUFFICIENT_DATA"
            funding_confidence = "LOW"
            funding_evidence.append("Blank researcher profile: No registered research domains, keywords, or linked research assets to evaluate funding relevance.")
            funding_methodology = "Blank researcher profile evaluated. Global funding grants are strictly isolated and not attributed to unlinked profiles."
        elif funding_is_unindexed or (funding_opp_count == 0 and (domain or profile_terms)):
            if (pub_count + patent_count) > 0:
                # Active research portfolio but unindexed funding: Neutral baseline proxy 50.0 applied, explicitly documented
                funding_score = 50.0
                funding_data_status = "DATA_UNAVAILABLE"
                funding_confidence = "LOW"
                target_desc = f"researcher domains ({', '.join(profile_terms[:3])})" if profile_id else f"domain '{domain}'"
                funding_evidence.append(f"No indexed funding opportunities currently match {target_desc}.")
                funding_evidence.append("Neutral baseline proxy (50.0) applied due to unindexed funding telemetry. This represents an unweighted baseline proxy and does not constitute measured funding relevance.")
                funding_methodology = "Deterministic missing-data policy: Neutral baseline proxy score of 50.0 applied when funding opportunities for a specific taxonomy are unindexed. Does not represent measured funding relevance."
            else:
                funding_score = 0.0
                funding_data_status = "INSUFFICIENT_DATA"
                funding_confidence = "LOW"
                funding_evidence.append("No active research publications, patents, or funding opportunities recorded in current scope.")
                funding_methodology = "Baseline empirical evaluation: Sparse or empty portfolio recorded."
        elif funding_opp_count > 0:
            opp_score = min(100.0, funding_opp_count * 20.0)
            agency_score = min(100.0, funding_agency_count * 25.0)
            match_score = 80.0 if funding_opp_count >= 3 else 50.0 if funding_opp_count >= 1 else 0.0

            funding_score = round(
                (0.40 * opp_score) + (0.35 * match_score) + (0.25 * agency_score),
                2
            )
            funding_data_status = "AVAILABLE"
            funding_confidence = "HIGH" if funding_opp_count >= 3 else "MEDIUM"
            funding_evidence.append(f"{funding_opp_count} active funding opportunity streams matching target scope.")
            funding_evidence.append(f"Sponsored across {funding_agency_count} distinct grant funding agencies.")
            funding_methodology = "Empirical Funding Relevance Score calculated from active funding grant volume, sponsor agency breadth, and research taxonomy compatibility."
        else:
            funding_score = 0.0
            funding_data_status = "INSUFFICIENT_DATA"
            funding_confidence = "LOW"
            funding_evidence.append("No active funding opportunities recorded in current scope.")
            funding_methodology = "Baseline empirical evaluation: Sparse funding portfolio recorded."

        funding_pillar = PillarScoreItem(
            pillar_name="Funding Relevance",
            score=funding_score,
            weight=0.15,
            weighted_score=round(funding_score * 0.15, 2),
            is_proxy=True,
            confidence=funding_confidence,
            data_status=funding_data_status,
            normalization_method="Multi-factor linear scaling (40% opportunity volume, 35% taxonomy match quality, 25% agency diversity) bounded to 0-100; neutral proxy (50.0) applied when unindexed.",
            contributing_signals={
                "matching_opportunities_count": funding_opp_count,
                "funding_agency_count": funding_agency_count,
                "data_status": funding_data_status,
                "is_neutral_proxy": (funding_data_status == "DATA_UNAVAILABLE"),
            },
            evidence=funding_evidence,
            methodology_notes=funding_methodology
        )

        # =========================================================
        # Composite Innovation Score & Synthesis
        # =========================================================
        if (pub_count + patent_count) > 0:
            composite_score = round(
                novelty_pillar.weighted_score
                + patent_pillar.weighted_score
                + trl_pillar.weighted_score
                + market_pillar.weighted_score
                + funding_pillar.weighted_score,
                2
            )
            composite_score = min(100.0, max(0.0, composite_score))
        else:
            composite_score = 0.0

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
        # Fetch distinct technology domains from both patents and publications
        pat_dom_stmt = select(distinct(Patent.technology_domain)).where(Patent.technology_domain.is_not(None))
        pub_dom_stmt = select(distinct(Publication.primary_domain)).where(Publication.primary_domain.is_not(None))
        pat_domains = (await db.execute(pat_dom_stmt)).scalars().all()
        pub_domains = (await db.execute(pub_dom_stmt)).scalars().all()
        raw_domains = list(pat_domains) + list(pub_domains)
        domains = sorted(list(set(d.strip() for d in raw_domains if d and d.strip())))[:12]

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
            p_cnt = (await db.execute(select(func.count(Patent.id)).where(func.lower(Patent.technology_domain) == d.lower()))).scalar() or 0
            pub_cnt = (await db.execute(select(func.count(Publication.id)).where(
                or_(
                    func.lower(Publication.primary_domain) == d.lower(),
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
                    publication_count=pub_cnt,
                    patent_count=p_cnt,
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
