from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import select, func, distinct, or_, desc, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.publication import Publication, profile_publications
from app.models.patent import Patent, profile_patents
from app.models.funding import FundingOpportunity
from app.models.profile import Profile
from app.models.user import User
from app.schemas.commercialization import (
    CommercializationRecommendationItem,
    CommercializationReadinessItem,
    CommercializationResponse,
    DomainCommercializationItem,
    CommercializationSummary,
    ProductizationPathwayItem,
    LicensingCandidateItem,
    LicensingPathwayItem,
    StartupCreationPathwayItem,
    PartnershipCandidateItem,
    IndustryPartnershipPathwayItem,
    CommercializationPathwaysContainer,
    CommercializationAnalysisItem,
)
from app.services.innovation_scoring_service import InnovationScoringService
from app.services.technology_intelligence_service import TechnologyIntelligenceService


DOMAIN_APPLICATION_MAP = {
    "quantum": {
        "applications": [
            "Hardware-in-the-Loop Quantum Circuit Simulation",
            "Post-Quantum Cryptographic Accelerators",
            "Combinatorial Optimization for Logistics & Finance",
            "High-Sensitivity Quantum Magnetometry & Sensing",
        ],
        "industries": ["Semiconductors", "Aerospace & Defense", "Financial Services", "Pharmaceuticals"],
        "product_concept": "Quantum Simulation & Acceleration Engine",
        "startup_concept": "Post-Quantum Cryptographic & Simulation Venture",
    },
    "energy": {
        "applications": [
            "Electric Vehicle High-Energy Density Battery Cells",
            "Grid-Scale Energy Storage Buffer Architecture",
            "Solid-State Thermal Management & Fast Charging",
            "Industrial Stationary Power Backup Systems",
        ],
        "industries": ["Automotive", "Clean Tech & Utilities", "Consumer Electronics", "Heavy Transportation"],
        "product_concept": "High-Efficiency Energy Storage Module",
        "startup_concept": "Next-Gen Energy Storage & Electrolyte Systems",
    },
    "ai": {
        "applications": [
            "Industrial Vision-Based Defect Inspection",
            "Automated Clinical Decision Support & Diagnostics",
            "Predictive Equipment Maintenance & Anomaly Detection",
            "Autonomous Agent Coordination & Workflow Optimization",
        ],
        "industries": ["Advanced Manufacturing", "Healthcare", "Enterprise IT", "Logistics & Supply Chain"],
        "product_concept": "Enterprise AI Decision & Inspection Platform",
        "startup_concept": "Domain-Specific Agentic AI Workflow Venture",
    },
    "artificial intelligence": {
        "applications": [
            "Industrial Vision-Based Defect Inspection",
            "Automated Clinical Decision Support & Diagnostics",
            "Predictive Equipment Maintenance & Anomaly Detection",
            "Autonomous Agent Coordination & Workflow Optimization",
        ],
        "industries": ["Advanced Manufacturing", "Healthcare", "Enterprise IT", "Logistics & Supply Chain"],
        "product_concept": "Enterprise AI Decision & Inspection Platform",
        "startup_concept": "Domain-Specific Agentic AI Workflow Venture",
    },
    "bio": {
        "applications": [
            "Targeted Drug Delivery Nanoparticles",
            "High-Throughput Genomic Variant Screening",
            "Point-of-Care Molecular Diagnostic Biosensors",
            "Biocatalytic Enzyme Engineering for Industrial Synthesis",
        ],
        "industries": ["Biomedical", "Biotechnology", "Agriculture", "Clinical Diagnostics"],
        "product_concept": "High-Throughput Molecular Screening Suite",
        "startup_concept": "Translational Biotherapeutics Discovery Venture",
    },
    "synthetic biology": {
        "applications": [
            "Engineered Microorganisms for Biomanufacturing",
            "Targeted Gene Editing & Therapeutic Synthesis",
            "Point-of-Care Biosensors & Environmental Diagnostics",
            "Agricultural Crop Resilience & Drought Resistance",
        ],
        "industries": ["Biotechnology", "Pharmaceuticals", "Agrigenomics", "Industrial Chemistry"],
        "product_concept": "High-Throughput Synthetic Biology Synthesis Kit",
        "startup_concept": "Engineered Biomanufacturing & Discovery Platform",
    },
    "robotics": {
        "applications": [
            "Autonomous Mobile Robotics for Warehouse Logistics",
            "Collaborative Robotic Arms for Precision Assembly",
            "Hazardous Environment Inspection UAVs",
            "Surgical Robotic Guidance & Actuation Systems",
        ],
        "industries": ["Manufacturing", "Supply Chain & Warehousing", "Healthcare", "Infrastructure"],
        "product_concept": "Intelligent Robotic Navigation & Actuation Controller",
        "startup_concept": "Autonomous Industrial Logistics & Robotics Venture",
    },
    "photonics": {
        "applications": [
            "Silicon Photonic Interconnects for Datacenter Networking",
            "Optical Co-Packaged Neural Network Accelerators",
            "Fiber-Optic Distributed Acoustic & Strain Sensing",
            "High-Power Diode Laser Material Processing",
        ],
        "industries": ["Telecommunications", "Datacenter Infrastructure", "Sensors & Instrumentation", "Defense"],
        "product_concept": "Integrated Silicon Photonic Transceiver Engine",
        "startup_concept": "Optical Interconnect & Photonic Computing Venture",
    },
    "space propulsion": {
        "applications": [
            "Small Satellite Electric Orbital Maneuvering",
            "High-Isp Deep Space Ion Engine Clusters",
            "In-Space Propellant Management & Refueling",
            "Precision CubeSat Stationkeeping Thrusters",
        ],
        "industries": ["Aerospace", "Satellite Telecommunications", "Defense", "Commercial Spaceflight"],
        "product_concept": "Electric Space Propulsion Thruster Unit",
        "startup_concept": "In-Orbit Satellite Propulsion & Logistics Venture",
    },
}


class CommercializationService:
    """
    Deterministic Commercialization Intelligence & Recommendation Engine.
    Consumes evidence from Modules 3–7 (Research Intelligence, Funding, Patent Landscape,
    Technology Intelligence, and Innovation Scoring) to formulate the four authoritative
    translation pathways: Productization, Licensing, Startup Creation, and Industry Partnership.
    """

    @classmethod
    def _resolve_domain_profile(cls, domain: Optional[str]) -> Dict[str, Any]:
        """Resolves potential application areas and industries deterministically."""
        if not domain:
            return {
                "applications": [
                    "Applied Industrial Process Optimization",
                    "Automated Sensor Data Analytics & Monitoring",
                    "Component Validation Testbed Implementation",
                ],
                "industries": ["General Technology", "Manufacturing", "Industrial Automation"],
                "product_concept": "Applied Technology System & Analytics Platform",
                "startup_concept": "Deep-Tech Commercial Translation Venture",
            }
        d_clean = domain.strip().lower()
        for k, v in DOMAIN_APPLICATION_MAP.items():
            if k in d_clean:
                return v
        return {
            "applications": [
                f"{domain} Process Optimization & Monitoring",
                f"{domain} System Integration Testbench",
                f"{domain} Industrial Workflow Automation",
            ],
            "industries": ["Industrial Technology", "Advanced Engineering", "Manufacturing"],
            "product_concept": f"Commercial {domain} Solutions Platform",
            "startup_concept": f"Innovative {domain} Translation Venture",
        }

    @classmethod
    async def evaluate_commercialization(
        cls,
        domain: Optional[str] = None,
        profile_id: Optional[int] = None,
        db: AsyncSession = None,
    ) -> CommercializationResponse:
        """
        Calculates commercialization readiness and synthesizes the four authoritative
        commercialization pathways using verifiable data from Modules 3–7.
        """
        # =========================================================
        # 1. Consume Module 7 Innovation Scoring
        # =========================================================
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

        pub_count = int(innov_resp.pillars["research_novelty"].contributing_signals.get("publication_count", 0))
        patent_count = int(innov_resp.pillars["patent_strength"].contributing_signals.get("patent_count", 0))
        granted_patent_count = int(innov_resp.pillars["patent_strength"].contributing_signals.get("granted_patent_count", 0))
        jurisdiction_count = int(innov_resp.pillars["patent_strength"].contributing_signals.get("jurisdiction_count", 0))

        # =========================================================
        # 2. Consume Module 5 Patent Assignees (Patent Owners)
        # =========================================================
        assignee_rows = []
        if patent_count > 0 or domain:
            ass_stmt = select(
                Patent.assignee,
                func.count(Patent.id).label("pat_cnt"),
                func.sum(case((Patent.publication_date.isnot(None), 1), else_=0)).label("granted_cnt")
            ).where(
                Patent.assignee.isnot(None),
                Patent.assignee != "",
                func.lower(Patent.assignee) != "unknown"
            )

            if profile_id is not None:
                ass_stmt = ass_stmt.join(profile_patents, profile_patents.c.patent_id == Patent.id)\
                                   .where(profile_patents.c.profile_id == profile_id)
            elif domain and domain.strip():
                dom_clean = domain.strip().lower()
                ass_stmt = ass_stmt.where(
                    or_(
                        func.lower(Patent.technology_domain).ilike(f"%{dom_clean}%"),
                        func.lower(Patent.title).ilike(f"%{dom_clean}%")
                    )
                )

            ass_stmt = ass_stmt.group_by(Patent.assignee).order_by(desc("pat_cnt")).limit(5)
            assignee_rows = (await db.execute(ass_stmt)).all()

        # =========================================================
        # 3. Consume Module 4 Funding Streams
        # =========================================================
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

        # =========================================================
        # 4. Consume Module 6 Whitespace & Context
        # =========================================================
        whitespace_resp = await TechnologyIntelligenceService.detect_whitespaces(
            domain=domain, profile_id=profile_id, db=db
        )
        whitespace_context = [
            f"{w.technology_area}: {w.whitespace_type.replace('_', ' ')} (Gap Score: {w.whitespace_score:.1f}/100)"
            for w in whitespace_resp.candidates[:3]
        ] if whitespace_resp.candidates else ["No critical whitespace gaps detected in target focus area."]

        # =========================================================
        # 5. Commercialization Readiness Score (0 - 100)
        # =========================================================
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

        # Domain Application Profile
        target_name = domain or "Global Technology Portfolio"
        target_type = "DOMAIN"
        if profile_id is not None:
            prof = (await db.execute(select(Profile).where(Profile.id == profile_id))).scalar_one_or_none()
            if prof:
                user = (await db.execute(select(User).where(User.id == prof.user_id))).scalar_one_or_none()
                target_name = user.full_name if user else f"Profile #{profile_id}"
                target_type = "PROFILE"

        app_profile = cls._resolve_domain_profile(domain)

        # =========================================================
        # 6. Commercialization Analysis (Problem/Application Fit)
        # =========================================================
        analysis_evidence = [
            f"Evaluated Technology Maturity: TRL {estimated_trl} ({innov_resp.trl.trl_stage}).",
            f"Innovation Index: {innov_resp.innovation_score:.1f}/100 ({innov_resp.overall_classification}).",
            f"Patent Portfolio: {patent_count} disclosure(s) ({granted_patent_count} granted).",
            f"Market Potential Proxy: {market_potential_score:.1f}/100.",
        ]
        if assignee_rows:
            analysis_evidence.append(f"Commercial Assignee Activity: {len(assignee_rows)} active competitor organization(s) indexed.")
        if funding_list:
            analysis_evidence.append(f"Active Grant Support: {len(funding_list)} matching translational funding opportunity stream(s).")

        analysis_limitations = [
            "Commercial adoption telemetry status is DATA_UNAVAILABLE; revenue and customer counts are not fabricated.",
            "Technology Readiness Level is an empirical proxy heuristic and does not constitute independent operational mission certification.",
            "Regulatory compliance certifications and management team capabilities are unmeasured and marked DATA_UNAVAILABLE.",
        ]

        comm_analysis = CommercializationAnalysisItem(
            research_topic=target_name,
            potential_application_areas=app_profile["applications"] if data_sufficiency != "INSUFFICIENT_DATA" else [],
            relevant_industries=app_profile["industries"] if data_sufficiency != "INSUFFICIENT_DATA" else [],
            problem_application_fit=(
                f"Empirical validation (TRL {estimated_trl}) and market momentum indicate potential applicability across "
                f"{', '.join(app_profile['industries'][:2])}. Specific translation requires prototype de-risking and formal validation."
                if data_sufficiency != "INSUFFICIENT_DATA"
                else "Insufficient empirical data to substantiate problem/application fit. Baseline publications or patent disclosures required."
            ),
            supporting_evidence=analysis_evidence,
            data_limitations=analysis_limitations,
            commercial_adoption_telemetry="DATA_UNAVAILABLE",
        )

        # =========================================================
        # 7. Formulate Four Canonical Commercialization Pathways
        # =========================================================

        # ---------------------------------------------------------
        # Pathway 1: PRODUCTIZATION
        # ---------------------------------------------------------
        if data_sufficiency == "INSUFFICIENT_DATA":
            pathway_prod = ProductizationPathwayItem(
                pathway="PRODUCTIZATION",
                product_concept="Insufficient Data for Productization",
                target_industry="Unspecified",
                problem_addressed="No indexed research problem or patent claims available.",
                main_use_case="None identified.",
                technology_basis="Insufficient publications and patent records.",
                required_next_steps=[
                    "Publish peer-reviewed scientific proof-of-concept papers.",
                    "Disclose technical mechanisms through provisional patent filings.",
                ],
                supporting_evidence=["Zero indexed publications or patents in target scope."],
                confidence="LOW",
                data_status="INSUFFICIENT_DATA",
                score=0.0,
                limitations="Productization cannot be evaluated without baseline research publications or patent disclosures.",
            )
        else:
            prod_score = round(min(100.0, (0.45 * trl_score) + (0.35 * market_potential_score) + (0.20 * novelty_score)), 1)
            prod_status = "AVAILABLE" if estimated_trl >= 4 else "INSUFFICIENT_DATA"
            pathway_prod = ProductizationPathwayItem(
                pathway="PRODUCTIZATION",
                product_concept=app_profile["product_concept"],
                target_industry=", ".join(app_profile["industries"][:2]),
                problem_addressed=f"Automated performance optimization and operational precision in {target_name}.",
                main_use_case=app_profile["applications"][0],
                technology_basis=f"Disclosed technical claims corresponding to TRL {estimated_trl} validation.",
                required_next_steps=[
                    "Develop rigorous bill-of-materials (BOM) and cost-of-goods-sold (COGS) model.",
                    "Establish standardized component testbench to benchmark operational repeatability.",
                    "Engage early beta adopters for real-world pilot performance feedback.",
                ],
                supporting_evidence=[
                    f"Technology Readiness: TRL {estimated_trl} ({innov_resp.trl.trl_stage}).",
                    f"Market Potential Proxy: {market_potential_score:.1f}/100.",
                    f"Patent Disclosures: {patent_count} patent(s) protecting technology basis.",
                ],
                confidence="HIGH" if estimated_trl >= 5 else "MEDIUM" if estimated_trl >= 3 else "LOW",
                data_status=prod_status,
                score=prod_score,
                limitations="Potential productization opportunity based on technical validation and application fit. Does not guarantee product-market fit or volume manufacturing.",
            )

        # ---------------------------------------------------------
        # Pathway 2: LICENSING
        # ---------------------------------------------------------
        licensing_candidates: List[LicensingCandidateItem] = []
        if patent_count == 0 or data_sufficiency == "INSUFFICIENT_DATA":
            pathway_licensing = LicensingPathwayItem(
                pathway="LICENSING",
                title="Corporate IP Out-Licensing",
                licensing_candidates=[],
                ip_ownership_basis="No patent disclosures or granted claims recorded in target scope.",
                rationale="Licensing pathway requires verified patent asset disclosures or granted claims. Currently no patent assets are indexed.",
                supporting_evidence=["Zero indexed patent disclosures in current scope.", "Out-licensing cannot be initiated without demonstrable intellectual property claims."],
                required_next_steps=[
                    "File provisional patent disclosures to establish priority rights before exploring licensing.",
                    "Conduct professional patent landscape clearance and prior art search.",
                ],
                confidence="LOW",
                data_status="INSUFFICIENT_DATA",
                score=0.0,
                limitations="Potential licensing candidate evaluation requires patent protection. Out-licensing is not viable without demonstrable patent claims.",
            )
        else:
            for row in assignee_rows:
                ass_name = row.assignee
                cnt = int(row.pat_cnt)
                gr_cnt = int(row.granted_cnt or 0)
                licensing_candidates.append(
                    LicensingCandidateItem(
                        organization=ass_name,
                        relevant_domain=target_name,
                        evidence_of_relevance=f"Assignee holds {cnt} related patent disclosure(s) ({gr_cnt} granted) in {target_name} sector.",
                        patent_count=cnt,
                        patent_relationship="Corporate Assignee / Competitor in Target Technology Domain",
                        suggested_licensing_rationale="Potential licensing candidate based on technology-domain and patent overlap. Requires direct out-licensing diligence.",
                        confidence="HIGH" if cnt >= 2 else "MEDIUM",
                        data_status="AVAILABLE",
                    )
                )

            lic_score = round(min(100.0, (patent_strength_score * 0.60 + market_potential_score * 0.40)), 1)
            lic_status = "AVAILABLE" if (patent_strength_score >= 35.0 and len(licensing_candidates) > 0) else "INSUFFICIENT_DATA"

            pathway_licensing = LicensingPathwayItem(
                pathway="LICENSING",
                title="Corporate IP Out-Licensing",
                licensing_candidates=licensing_candidates,
                ip_ownership_basis=f"Portfolio of {patent_count} patent disclosure(s) ({granted_patent_count} granted) across {jurisdiction_count} jurisdiction(s).",
                rationale=(
                    f"Established patent strength ({patent_strength_score:.1f}/100) and multi-jurisdiction disclosures enable non-dilutive monetization via corporate patent licensing."
                    if licensing_candidates else
                    "Patent disclosures exist, but no corporate assignees are currently indexed in target domain to qualify as licensing candidates."
                ),
                supporting_evidence=[
                    f"Patent Strength Proxy: {patent_strength_score:.1f}/100.",
                    f"Commercial Assignee Diversity: {len(licensing_candidates)} potential licensing candidate organization(s) identified from patent landscape.",
                    f"Technology Readiness: TRL {estimated_trl} facilitates technology transfer.",
                ],
                required_next_steps=[
                    "Prepare a Non-Confidential Technology Summary (1-pager) for corporate IP scouts.",
                    "Benchmark industry royalty rates and standard upfront licensing fee structures.",
                    "Establish non-disclosure agreements (NDA) prior to technical deep-dive demonstrations.",
                ],
                confidence="HIGH" if patent_strength_score >= 60.0 else "MEDIUM",
                data_status=lic_status,
                score=lic_score,
                limitations="Potential licensing candidates identified strictly via patent and technology domain overlap. Does not guarantee commercial licensing interest or executed agreements.",
            )

        # ---------------------------------------------------------
        # Pathway 3: STARTUP_CREATION
        # ---------------------------------------------------------
        if data_sufficiency == "INSUFFICIENT_DATA":
            pathway_startup = StartupCreationPathwayItem(
                pathway="STARTUP_CREATION",
                startup_concept="Insufficient Data for Venture Creation",
                problem="No verified problem or commercial gap recorded.",
                proposed_solution="None available.",
                target_customers="Unspecified",
                business_model_hypothesis="None",
                technology_readiness=f"TRL {estimated_trl}",
                relevant_funding=[],
                patent_ip_situation="No patent protection.",
                competitive_context="No competitive data.",
                supporting_evidence=["Insufficient research or patent records."],
                required_next_steps=["Establish fundamental scientific proof-of-concept."],
                confidence="LOW",
                data_status="INSUFFICIENT_DATA",
                score=0.0,
                limitations="Venture formation requires minimum technology maturity and defensible intellectual property.",
            )
        else:
            startup_score = round(min(100.0, (readiness_score * 0.45 + market_potential_score * 0.35 + funding_relevance_score * 0.20)), 1)
            matching_grants_txt = [
                f"{f['title']} (${f['funding_amount']/1e6:.1f}M, {f['funding_agency']})"
                for f in funding_list if f.get('funding_amount')
            ]
            if not matching_grants_txt:
                matching_grants_txt = ["Non-dilutive translational funding solicitations (e.g. SBIR/STTR, NSF, DOE)."]

            ip_situation_txt = (
                f"{patent_count} patent asset(s) ({granted_patent_count} granted) provide defensible proprietary IP."
                if patent_count > 0 else
                "Unprotected technical disclosures; provisional patent filing required prior to venture incorporation."
            )

            pathway_startup = StartupCreationPathwayItem(
                pathway="STARTUP_CREATION",
                startup_concept=app_profile["startup_concept"],
                problem=f"Current solutions in {target_name} face scalability, integration, and cost bottlenecks.",
                proposed_solution=f"High-novelty ({novelty_score:.1f}/100) technology platform offering accelerated deployment and validated performance.",
                target_customers=f"Commercial enterprises across {', '.join(app_profile['industries'][:2])} requiring high-assurance {target_name} systems.",
                business_model_hypothesis="Tiered enterprise B2B platform licensing combined with recurring maintenance and custom hardware integration services.",
                technology_readiness=f"TRL {estimated_trl} ({innov_resp.trl.trl_stage})",
                relevant_funding=matching_grants_txt[:3],
                patent_ip_situation=ip_situation_txt,
                competitive_context=f"{len(assignee_rows)} active competitor organization(s) indexed in patent landscape." if assignee_rows else "Early-stage market with low assignee concentration.",
                supporting_evidence=[
                    f"Composite Innovation Score: {innov_resp.innovation_score:.1f}/100 ({innov_resp.overall_classification}).",
                    f"Technology Readiness: TRL {estimated_trl} ({innov_resp.trl.trl_name}).",
                    f"Market Potential Proxy: {market_potential_score:.1f}/100.",
                    f"Funding Relevance: {funding_relevance_score:.1f}/100.",
                ],
                required_next_steps=[
                    "Engage Institutional Tech Transfer Office (TTO) to negotiate exclusive venture license option.",
                    "Incorporate venture entity and formalize founder equity allocation.",
                    "Conduct structured customer discovery interviews (e.g. NSF I-Corps framework).",
                    "Apply for non-dilutive federal translational funding (SBIR/STTR Phase I).",
                ],
                confidence="HIGH" if (innov_resp.innovation_score >= 60.0 and estimated_trl >= 4) else "MEDIUM",
                data_status="AVAILABLE",
                score=startup_score,
                limitations="Potential startup opportunity based on research, technology maturity, market/application and funding evidence. Does not guarantee startup success or commercial traction.",
            )

        # ---------------------------------------------------------
        # Pathway 4: INDUSTRY_PARTNERSHIP
        # ---------------------------------------------------------
        partnership_candidates: List[PartnershipCandidateItem] = []
        if data_sufficiency == "INSUFFICIENT_DATA":
            pathway_partnership = IndustryPartnershipPathwayItem(
                pathway="INDUSTRY_PARTNERSHIP",
                title="Industry Co-Development & Joint Validation",
                partnership_candidates=[],
                rationale="Insufficient technology disclosures to qualify industry partnership candidates.",
                supporting_evidence=["Zero indexed publications or patents."],
                required_next_steps=["Generate peer-reviewed publications to attract industrial R&D interest."],
                confidence="LOW",
                data_status="INSUFFICIENT_DATA",
                score=0.0,
                limitations="Potential industry partnership candidate evaluation requires baseline technological disclosures.",
            )
        else:
            for row in assignee_rows:
                ass_name = row.assignee
                cnt = int(row.pat_cnt)
                p_type = "Technology Validation / Pilot Testing" if estimated_trl in [3, 4, 5] else "Joint Commercial Integration"
                partnership_candidates.append(
                    PartnershipCandidateItem(
                        organization=ass_name,
                        partnership_type=p_type,
                        relevant_domain=target_name,
                        evidence_of_relevance=f"Active applicant in {target_name} with {cnt} patent disclosure(s).",
                        suggested_rationale="Potential industry partnership candidate for collaborative R&D or pre-commercial testing evaluation.",
                        confidence="HIGH" if cnt >= 2 else "MEDIUM",
                        data_status="AVAILABLE",
                    )
                )

            part_score = round(min(100.0, (market_potential_score * 0.50 + trl_score * 0.50)), 1)
            part_status = "AVAILABLE" if (len(partnership_candidates) > 0 or market_potential_score >= 25.0) else "INSUFFICIENT_DATA"

            pathway_partnership = IndustryPartnershipPathwayItem(
                pathway="INDUSTRY_PARTNERSHIP",
                title="Industry Co-Development & Joint Validation",
                partnership_candidates=partnership_candidates,
                rationale=(
                    f"Mid-stage technical maturity (TRL {estimated_trl}) benefits from industrial partner co-funding, real-world testbeds, and accelerated translation."
                    if partnership_candidates else
                    "Technology validation is viable, but no corporate partner organizations are currently indexed in target domain."
                ),
                supporting_evidence=[
                    f"Applied Feasibility: TRL {estimated_trl} ({innov_resp.trl.trl_name}).",
                    f"Market Interest Proxy: {market_potential_score:.1f}/100.",
                    f"Partner Ecosystem: {len(partnership_candidates)} potential industrial partnership candidate(s) indexed.",
                ],
                required_next_steps=[
                    "Execute standard Sponsored Research Agreement (SRA) or Joint Development Agreement (JDA).",
                    "Define clear IP allocation terms for foreground inventions developed under joint testing.",
                    "Co-apply for collaborative translational grants (e.g. NSF IUCRC).",
                ],
                confidence="HIGH" if len(partnership_candidates) >= 2 else "MEDIUM",
                data_status=part_status,
                score=part_score,
                limitations="Potential industry partnership candidate for further evaluation. Does not imply an existing partnership or committed agreement.",
            )

        pathways_container = CommercializationPathwaysContainer(
            productization=pathway_prod,
            licensing=pathway_licensing,
            startup_creation=pathway_startup,
            industry_partnership=pathway_partnership,
        )

        # =========================================================
        # 8. Rule-Based Advisory Action Recommendations (Backward Compatible)
        # =========================================================
        recommendations: List[CommercializationRecommendationItem] = []

        if data_sufficiency == "INSUFFICIENT_DATA":
            rec_insufficient = CommercializationRecommendationItem(
                recommendation_type="MONITOR_AND_GATHER_EVIDENCE",
                title="Populate Portfolio & Monitor Technology Field",
                priority="LOW",
                score=10.0,
                confidence="LOW",
                data_status="INSUFFICIENT_DATA",
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
            # 1. Productization / Pre-Commercial Roadmap
            if pathway_prod.score >= 40.0:
                recommendations.append(
                    CommercializationRecommendationItem(
                        recommendation_type="PRODUCTIZATION",
                        title=f"Develop {pathway_prod.product_concept} Productization Roadmap",
                        priority="HIGH" if estimated_trl >= 6 else "MEDIUM",
                        score=pathway_prod.score,
                        confidence=pathway_prod.confidence,
                        data_status=pathway_prod.data_status,
                        rationale=f"Potential productization opportunity based on technical validation (TRL {estimated_trl}) and application fit across {pathway_prod.target_industry}.",
                        supporting_evidence=pathway_prod.supporting_evidence,
                        required_next_actions=pathway_prod.required_next_steps,
                        limitations=pathway_prod.limitations,
                    )
                )

            # 2. Corporate Licensing
            if pathway_licensing.score >= 40.0 and len(pathway_licensing.licensing_candidates) > 0:
                recommendations.append(
                    CommercializationRecommendationItem(
                        recommendation_type="LICENSING",
                        title="Pursue Corporate IP Out-Licensing",
                        priority="HIGH" if patent_strength_score >= 65.0 else "MEDIUM",
                        score=pathway_licensing.score,
                        confidence=pathway_licensing.confidence,
                        data_status=pathway_licensing.data_status,
                        rationale=f"Potential licensing candidate opportunity based on patent strength ({patent_strength_score:.1f}/100) and {len(pathway_licensing.licensing_candidates)} corporate assignee candidate(s).",
                        supporting_evidence=pathway_licensing.supporting_evidence,
                        required_next_actions=pathway_licensing.required_next_steps,
                        limitations=pathway_licensing.limitations,
                    )
                )

            # 3. Startup Creation
            if pathway_startup.score >= 45.0:
                recommendations.append(
                    CommercializationRecommendationItem(
                        recommendation_type="STARTUP_CREATION",
                        title=f"Form {pathway_startup.startup_concept}",
                        priority="HIGH" if innov_resp.innovation_score >= 65.0 else "MEDIUM",
                        score=pathway_startup.score,
                        confidence=pathway_startup.confidence,
                        data_status=pathway_startup.data_status,
                        rationale=f"Potential startup opportunity based on research novelty ({novelty_score:.1f}/100), technology maturity (TRL {estimated_trl}), and funding telemetry.",
                        supporting_evidence=pathway_startup.supporting_evidence,
                        required_next_actions=pathway_startup.required_next_steps,
                        limitations=pathway_startup.limitations,
                    )
                )

            # 4. Industry Partnership
            if pathway_partnership.score >= 35.0:
                recommendations.append(
                    CommercializationRecommendationItem(
                        recommendation_type="INDUSTRY_PARTNERSHIP",
                        title="Establish Industry Co-Development Partnership",
                        priority="HIGH" if estimated_trl in [4, 5] else "MEDIUM",
                        score=pathway_partnership.score,
                        confidence=pathway_partnership.confidence,
                        data_status=pathway_partnership.data_status,
                        rationale=f"Potential industry partnership candidate for further evaluation; mid-stage maturity (TRL {estimated_trl}) benefits from joint validation.",
                        supporting_evidence=pathway_partnership.supporting_evidence,
                        required_next_actions=pathway_partnership.required_next_steps,
                        limitations=pathway_partnership.limitations,
                    )
                )

            # 5. IP Strengthening
            if patent_strength_score < 60.0 and (novelty_score >= 35.0 or estimated_trl >= 3):
                score_ip = round(min(100.0, max(20.0, 100.0 - patent_strength_score)), 1)
                recommendations.append(
                    CommercializationRecommendationItem(
                        recommendation_type="STRENGTHEN_IP",
                        title="Protect & Expand Patent Portfolio",
                        priority="HIGH" if patent_strength_score < 35.0 and novelty_score >= 50.0 else "MEDIUM",
                        score=score_ip,
                        confidence="HIGH",
                        data_status="AVAILABLE",
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

            # 6. Non-Dilutive Translational Funding
            if funding_relevance_score >= 35.0 or len(funding_list) > 0:
                opp_cnt = len(funding_list)
                recommendations.append(
                    CommercializationRecommendationItem(
                        recommendation_type="SEEK_FUNDING",
                        title="Apply for Non-Dilutive Translational Grants",
                        priority="HIGH" if opp_cnt >= 2 else "MEDIUM",
                        score=round(funding_relevance_score, 1),
                        confidence="HIGH" if opp_cnt >= 2 else "MEDIUM",
                        data_status="AVAILABLE",
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

            # 7. Prototype Validation
            if estimated_trl in [2, 3, 4] and novelty_score >= 30.0:
                recommendations.append(
                    CommercializationRecommendationItem(
                        recommendation_type="VALIDATE_TECHNOLOGY",
                        title="Conduct Rigorous Laboratory Prototype Validation",
                        priority="HIGH" if estimated_trl in [2, 3] else "MEDIUM",
                        score=round(novelty_score, 1),
                        confidence="HIGH" if data_sufficiency == "SUFFICIENT" else "MEDIUM",
                        data_status="AVAILABLE",
                        rationale=f"Fundamental concept (TRL {estimated_trl}) requires empirical laboratory benchmarking and component validation before commercial scale-up.",
                        supporting_evidence=[
                            f"Technology Readiness: TRL {estimated_trl} ({innov_resp.trl.trl_name}).",
                            f"Research Novelty: {novelty_score:.1f}/100.",
                            f"Publication Evidence: {pub_count} papers indexed.",
                        ],
                        required_next_actions=[
                            "Build standardized experimental testbench to measure operational performance against baseline.",
                            "Document statistical repeatability and error bounds across multiple testing runs.",
                            "Prepare component validation dataset to substantiate patent claims and grant applications.",
                        ],
                    )
                )

            # 8. Research Focus
            if estimated_trl <= 2:
                recommendations.append(
                    CommercializationRecommendationItem(
                        recommendation_type="RESEARCH_FOCUS",
                        title="Advance Fundamental Scientific Research",
                        priority="HIGH" if estimated_trl == 1 else "MEDIUM",
                        score=85.0 if estimated_trl == 1 else 60.0,
                        confidence="HIGH" if data_sufficiency == "SUFFICIENT" else "MEDIUM",
                        data_status="AVAILABLE",
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
            unmeasured_dimensions={
                "regulatory_feasibility": "DATA_UNAVAILABLE",
                "team_capability": "DATA_UNAVAILABLE",
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
            commercialization_analysis=comm_analysis,
            pathways=pathways_container,
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
            governance_disclaimer=(
                "Commercialization recommendations and readiness scores are empirical advisory guidelines derived from "
                "patent, research, funding, and growth metadata. They represent potential commercialization pathways for "
                "further diligence and do not constitute legal patentability opinions, freedom-to-operate guarantees, "
                "or financial investment advice."
            ),
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
