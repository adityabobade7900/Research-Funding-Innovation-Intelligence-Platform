import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, distinct, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.publication import Publication
from app.models.patent import Patent
from app.models.funding import FundingOpportunity
from app.models.profile import Profile
from app.models.user import User
from app.schemas.executive_report import (
    RoadmapActionItem,
    RoadmapPhaseItem,
    StrategicAssessment,
    ExecutiveDossierResponse,
    DomainBenchmarkItem,
    ExecutiveDossierSummary,
)
from app.services.innovation_scoring_service import InnovationScoringService
from app.services.commercialization_service import CommercializationService
from app.services.technology_intelligence_service import TechnologyIntelligenceService


class ExecutiveReportService:
    """
    Milestone 4: Executive Intelligence & Comprehensive Dossier Engine.
    Synthesizes scientific publications, patent IP landscapes, funding pipelines,
    technology whitespaces, 5-pillar Innovation Scores, and Commercialization Readiness
    into an executive-ready strategic dossier.
    """

    @classmethod
    async def generate_dossier(
        cls,
        domain: Optional[str] = None,
        profile_id: Optional[int] = None,
        db: AsyncSession = None,
    ) -> ExecutiveDossierResponse:
        """
        Generates a comprehensive executive intelligence dossier.
        """
        report_id = f"DOSSIER-{uuid.uuid4().hex[:8].upper()}"
        generated_at = datetime.now(timezone.utc).isoformat()

        # 1. Re-use M3C Innovation Scoring & M3D Commercialization Intelligence
        innov_resp = await InnovationScoringService.calculate_innovation_score(
            domain=domain, profile_id=profile_id, db=db
        )
        comm_resp = await CommercializationService.evaluate_commercialization(
            domain=domain, profile_id=profile_id, db=db
        )
        whitespace_resp = await TechnologyIntelligenceService.detect_whitespaces(
            domain=domain, profile_id=profile_id, db=db
        )

        target_name = comm_resp.target_name
        target_type = comm_resp.target_type

        # 2. Extract Sub-Signals & Metrics
        novelty_signals = innov_resp.pillars["research_novelty"].contributing_signals
        patent_signals = innov_resp.pillars["patent_strength"].contributing_signals
        funding_signals = innov_resp.pillars["funding_relevance"].contributing_signals
        market_signals = innov_resp.pillars["market_potential"].contributing_signals

        pub_metrics = {
            "total_publications": novelty_signals.get("publication_count", 0),
            "recent_publications": novelty_signals.get("recent_publications", 0),
            "total_citations": novelty_signals.get("total_citations", 0),
            "average_citations": novelty_signals.get("average_citations", 0.0),
            "venue_count": novelty_signals.get("venue_count", 0),
            "novelty_score": innov_resp.pillars["research_novelty"].score,
        }

        pat_metrics = {
            "total_patents": patent_signals.get("patent_count", 0),
            "granted_patents": patent_signals.get("granted_patent_count", 0),
            "jurisdiction_count": patent_signals.get("jurisdiction_count", 0),
            "assignee_count": market_signals.get("assignee_count", 0),
            "patent_strength_score": innov_resp.pillars["patent_strength"].score,
        }

        total_capital = sum(f.get("funding_amount", 0.0) or 0.0 for f in comm_resp.funding_opportunities)
        fnd_metrics = {
            "matching_opportunities_count": len(comm_resp.funding_opportunities),
            "total_identified_grant_pool": total_capital,
            "funding_relevance_score": innov_resp.pillars["funding_relevance"].score,
        }

        ws_metrics = {
            "detected_whitespace_count": len(whitespace_resp.candidates),
            "top_whitespace_areas": [w.technology_area for w in whitespace_resp.candidates[:3]],
        }

        # 3. Formulate Strategic Assessment (SWOT Synthesis)
        strengths: List[str] = []
        risks: List[str] = []
        opportunities: List[str] = []
        barriers: List[str] = []

        # Strengths
        if pub_metrics["total_publications"] > 0:
            strengths.append(f"Strong academic foundation: {pub_metrics['total_publications']} indexed publications with {pub_metrics['average_citations']:.1f} avg citations.")
        if pat_metrics["granted_patents"] > 0:
            strengths.append(f"Enforceable IP position: {pat_metrics['granted_patents']} granted patents across {pat_metrics['jurisdiction_count']} international jurisdictions.")
        if innov_resp.innovation_score >= 60.0:
            strengths.append(f"High composite innovation potential: {innov_resp.innovation_score:.1f}/100 ({innov_resp.overall_classification}).")
        if not strengths:
            strengths.append("Emerging research initiative with foundational theoretical potential.")

        # Risks & Bottlenecks
        if pat_metrics["total_patents"] > 0 and pat_metrics["granted_patents"] == 0:
            risks.append("IP conversion bottleneck: Disclosures remain in pending status with no granted claims.")
        if innov_resp.trl.estimated_trl <= 3:
            risks.append("Early-stage TRL exposure: Technology requires extensive laboratory de-risking before commercial pilot readiness.")
        if pub_metrics["total_publications"] > 0 and pat_metrics["total_patents"] == 0:
            risks.append("Public forfeiture exposure: Academic publications indexed without concurrent provisional patent filings.")
        if not risks:
            risks.append("Continuous monitoring required for competitive corporate patent filings in target domain.")

        # Market Opportunities
        if len(comm_resp.funding_opportunities) > 0:
            opportunities.append(f"Non-dilutive capital pipeline: {len(comm_resp.funding_opportunities)} active grant solicitations with ${total_capital / 1000000:.1f}M in pool.")
        if whitespace_resp.candidates:
            opportunities.append(f"Uncrowded whitespace: {len(whitespace_resp.candidates)} underserved technology niches identified for first-mover advantage.")
        opportunities.append(f"Strategic pathway: Primary recommended translation avenue is {comm_resp.readiness.primary_pathway.replace('_', ' ')}.")

        # Barriers to Entry
        if pat_metrics["assignee_count"] >= 3:
            barriers.append(f"Corporate assignee density: {pat_metrics['assignee_count']} industrial competitors active in domain patent landscape.")
        barriers.append("Regulatory and quality assurance compliance timelines (e.g. ISO/FDA/CE certification pathways).")

        strategic_assessment = StrategicAssessment(
            strengths=strengths,
            risks_and_bottlenecks=risks,
            market_opportunities=opportunities,
            barriers_to_entry=barriers,
        )

        # 4. Synthesize 3-Phase Action Roadmap
        roadmap: List[RoadmapPhaseItem] = [
            RoadmapPhaseItem(
                phase_name="Phase 1: Foundation & De-risking",
                timeframe="Months 0–6",
                description="Secure intellectual property, benchmark prototype metrics, and apply for non-dilutive translational funding.",
                actions=[
                    RoadmapActionItem(
                        action="File provisional patent disclosures for recent publication discoveries.",
                        owner_role="Principal Investigator / Tech Transfer Office",
                        target_timeline="Month 2",
                        expected_outcome="Secured priority date and 12-month international filing window.",
                    ),
                    RoadmapActionItem(
                        action="Submit translational grant proposals to matched agency solicitations.",
                        owner_role="Research Director",
                        target_timeline="Month 4",
                        expected_outcome="Submitted proposals for non-dilutive prototype funding.",
                    ),
                ],
            ),
            RoadmapPhaseItem(
                phase_name="Phase 2: Validation & Partnering",
                timeframe="Months 6–18",
                description="Conduct subsystem stress-testing and initiate corporate engagement or venture formation.",
                actions=[
                    RoadmapActionItem(
                        action="Execute Joint Development Agreement (JDA) or industrial pilot demo.",
                        owner_role="Commercialization Lead / Innovation Manager",
                        target_timeline="Month 12",
                        expected_outcome="Validated performance metrics in relevant operating environment (TRL 6).",
                    ),
                    RoadmapActionItem(
                        action="Draft preliminary Bill-of-Materials (BOM) and regulatory compliance roadmap.",
                        owner_role="Engineering Lead",
                        target_timeline="Month 15",
                        expected_outcome="Quantified unit economics and compliance milestones.",
                    ),
                ],
            ),
            RoadmapPhaseItem(
                phase_name="Phase 3: Scale & Execution",
                timeframe="Months 18–36",
                description="Full commercialization execution via corporate licensing agreement or venture spinout.",
                actions=[
                    RoadmapActionItem(
                        action="Finalize exclusive IP licensing or close institutional seed venture round.",
                        owner_role="Founding CEO / TTO Director",
                        target_timeline="Month 24",
                        expected_outcome="Operational entity funded with market deployment runway.",
                    )
                ],
            ),
        ]

        # 5. Executive Narrative Summary
        exec_summary = (
            f"Strategic Intelligence Dossier for {target_name} ({target_type}). "
            f"The asset demonstrates an Innovation Score of {innov_resp.innovation_score:.1f}/100 ({innov_resp.overall_classification}) "
            f"with estimated Technology Readiness Level TRL {innov_resp.trl.estimated_trl} ({innov_resp.trl.trl_stage}). "
            f"Commercialization Readiness is scored at {comm_resp.readiness.readiness_score:.1f}/100 ({comm_resp.readiness.readiness_level}), "
            f"with the primary translation pathway prioritized as '{comm_resp.readiness.primary_pathway.replace('_', ' ')}'. "
            f"A total of {pub_metrics['total_publications']} publications and {pat_metrics['total_patents']} patent disclosures were synthesized, "
            f"supported by {len(comm_resp.funding_opportunities)} active grant matching opportunities."
        )

        key_findings = [
            f"Composite Innovation Score: {innov_resp.innovation_score:.1f} / 100 ({innov_resp.overall_classification}).",
            f"Technology Readiness: TRL {innov_resp.trl.estimated_trl} — {innov_resp.trl.trl_name}.",
            f"Commercialization Readiness: {comm_resp.readiness.readiness_score:.1f} / 100 ({comm_resp.readiness.readiness_level}).",
            f"Primary Commercial Pathway: {comm_resp.readiness.primary_pathway.replace('_', ' ')} ({comm_resp.primary_recommendation.title}).",
            f"IP Position: {pat_metrics['total_patents']} patents ({pat_metrics['granted_patents']} granted) across {pat_metrics['jurisdiction_count']} registries.",
            f"Scientific Velocity: {pub_metrics['total_publications']} publications with {pub_metrics['average_citations']:.1f} average citations.",
        ]

        top_recs = [
            {
                "recommendation_type": r.recommendation_type,
                "title": r.title,
                "priority": r.priority,
                "score": r.score,
                "confidence": r.confidence,
                "rationale": r.rationale,
                "required_next_actions": r.required_next_actions,
            }
            for r in comm_resp.recommendations[:4]
        ]

        return ExecutiveDossierResponse(
            report_id=report_id,
            generated_at=generated_at,
            target_name=target_name,
            target_type=target_type,
            executive_summary=exec_summary,
            key_findings=key_findings,
            innovation_score=innov_resp.innovation_score,
            innovation_classification=innov_resp.overall_classification,
            estimated_trl=innov_resp.trl.estimated_trl,
            trl_stage=innov_resp.trl.trl_stage,
            commercialization_readiness=comm_resp.readiness.readiness_score,
            readiness_level=comm_resp.readiness.readiness_level,
            primary_commercial_pathway=comm_resp.readiness.primary_pathway,
            publication_metrics=pub_metrics,
            patent_metrics=pat_metrics,
            funding_metrics=fnd_metrics,
            whitespace_metrics=ws_metrics,
            strategic_assessment=strategic_assessment,
            roadmap=roadmap,
            top_recommendations=top_recs,
            top_funding_opportunities=comm_resp.funding_opportunities[:5],
            data_sufficiency=comm_resp.readiness.data_sufficiency,
        )

    @classmethod
    async def generate_markdown_dossier(
        cls,
        domain: Optional[str] = None,
        profile_id: Optional[int] = None,
        db: AsyncSession = None,
    ) -> str:
        """
        Generates an executive-ready Markdown formatted dossier document.
        """
        dossier = await cls.generate_dossier(domain=domain, profile_id=profile_id, db=db)
        
        md_lines = [
            f"# Executive Intelligence Dossier: {dossier.target_name}",
            f"**Report ID**: `{dossier.report_id}` | **Generated**: {dossier.generated_at[:10]} | **Scope**: {dossier.target_type}",
            "",
            "## 1. Executive Summary",
            dossier.executive_summary,
            "",
            "## 2. Key Performance Indicators",
            f"- **Composite Innovation Score**: **{dossier.innovation_score} / 100** ({dossier.innovation_classification})",
            f"- **Technology Readiness Level**: **TRL {dossier.estimated_trl}** ({dossier.trl_stage})",
            f"- **Commercialization Readiness**: **{dossier.commercialization_readiness} / 100** ({dossier.readiness_level})",
            f"- **Primary Translation Pathway**: **{dossier.primary_commercial_pathway.replace('_', ' ')}**",
            f"- **Data Sufficiency Status**: `{dossier.data_sufficiency}`",
            "",
            "## 3. Strategic Assessment (SWOT Synthesis)",
            "### Strengths",
            *[f"- {s}" for s in dossier.strategic_assessment.strengths],
            "",
            "### Risks & Bottlenecks",
            *[f"- {r}" for r in dossier.strategic_assessment.risks_and_bottlenecks],
            "",
            "### Market Opportunities",
            *[f"- {o}" for o in dossier.strategic_assessment.market_opportunities],
            "",
            "### Barriers to Entry",
            *[f"- {b}" for b in dossier.strategic_assessment.barriers_to_entry],
            "",
            "## 4. Prioritized Commercialization Recommendations",
        ]

        for rec in dossier.top_recommendations:
            md_lines.extend([
                f"### [{rec['priority']} PRIORITY] {rec['title']} (Score: {rec['score']}/100)",
                f"**Pathway**: `{rec['recommendation_type']}` | **Confidence**: `{rec['confidence']}`",
                f"**Rationale**: {rec['rationale']}",
                "**Action Items**:",
                *[f"  - [ ] {act}" for act in rec['required_next_actions']],
                "",
            ])

        md_lines.extend([
            "## 5. Strategic Roadmap Timeline",
        ])
        for phase in dossier.roadmap:
            md_lines.extend([
                f"### {phase.phase_name} ({phase.timeframe})",
                phase.description,
                "",
                "| Action | Lead Role | Timeline | Expected Outcome |",
                "| :--- | :--- | :--- | :--- |",
            ])
            for act in phase.actions:
                md_lines.append(f"| {act.action} | {act.owner_role} | {act.target_timeline} | {act.expected_outcome} |")
            md_lines.append("")

        md_lines.extend([
            "## 6. Governance & Compliance Notice",
            f"> {dossier.governance_disclaimer}",
        ])

        return "\n".join(md_lines)

    @classmethod
    async def get_summary(
        cls,
        db: AsyncSession = None,
    ) -> ExecutiveDossierSummary:
        """
        Cross-domain benchmark matrix across all indexed technology sectors.
        """
        dom_stmt = select(distinct(Patent.technology_domain)).where(Patent.technology_domain.is_not(None)).limit(10)
        domains = list((await db.execute(dom_stmt)).scalars().all())
        if not domains:
            domains = ["Quantum Computing", "Artificial Intelligence", "Energy Storage", "Biotechnology"]

        benchmarks: List[DomainBenchmarkItem] = []
        pathway_counts: Dict[str, int] = {}
        trl_dist: Dict[str, int] = {}
        innov_sum = 0.0
        readiness_sum = 0.0

        for d in domains:
            if not d:
                continue
            dossier = await cls.generate_dossier(domain=d, db=db)
            innov_sum += dossier.innovation_score
            readiness_sum += dossier.commercialization_readiness

            pathway = dossier.primary_commercial_pathway
            pathway_counts[pathway] = pathway_counts.get(pathway, 0) + 1
            
            stage = f"TRL {dossier.estimated_trl}"
            trl_dist[stage] = trl_dist.get(stage, 0) + 1

            benchmarks.append(
                DomainBenchmarkItem(
                    domain=d,
                    innovation_score=dossier.innovation_score,
                    estimated_trl=dossier.estimated_trl,
                    commercialization_readiness=dossier.commercialization_readiness,
                    primary_pathway=pathway,
                    total_publications=dossier.publication_metrics.get("total_publications", 0),
                    total_patents=dossier.patent_metrics.get("total_patents", 0),
                    active_funding_streams=dossier.funding_metrics.get("matching_opportunities_count", 0),
                )
            )

        benchmarks.sort(key=lambda x: x.commercialization_readiness, reverse=True)
        dominant_pw = max(pathway_counts.items(), key=lambda x: x[1])[0] if pathway_counts else "RESEARCH_FOCUS"
        count = max(1, len(benchmarks))

        return ExecutiveDossierSummary(
            total_domains_benchmarked=len(benchmarks),
            portfolio_average_innovation_score=round(innov_sum / float(count), 2) if benchmarks else 0.0,
            portfolio_average_readiness_score=round(readiness_sum / float(count), 2) if benchmarks else 0.0,
            dominant_pathway=dominant_pw,
            trl_breakdown=trl_dist,
            domain_benchmarks=benchmarks,
        )
