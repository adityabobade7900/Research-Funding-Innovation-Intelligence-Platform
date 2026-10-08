import io
import math
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.funding import FundingOpportunity
from app.models.patent import Patent
from app.models.publication import Publication
from app.models.profile import Profile
from app.models.user import User
from app.schemas.report_export import (
    ReportType,
    ReportFilterParams,
    ReportTypeItem,
    ReportTypesResponse,
    ReportFactorItem,
    ReportPreviewResponse,
)
from app.services.innovation_scoring_service import InnovationScoringService
from app.services.commercialization_service import CommercializationService
from app.services.technology_intelligence_service import TechnologyIntelligenceService
from app.services.research_trend_service import ResearchTrendService
from app.services.executive_report_service import ExecutiveReportService


class ReportExportService:
    """
    Dedicated Service for Module 11: Reports & Export System.
    Handles data aggregation, filtering, preview generation,
    professional PDF generation (ReportLab), and structured Excel export (openpyxl).
    """

    @classmethod
    def get_supported_report_types(cls) -> ReportTypesResponse:
        """Returns metadata for all supported report types and applicable filters."""
        types = [
            ReportTypeItem(
                id=ReportType.FUNDING,
                name="Funding Intelligence Report",
                description="Analysis of active research grant solicitations, funding agencies, award amounts, deadlines, and eligibility criteria.",
                source_module="Module 4 (Funding Intelligence)",
                supported_filters=["domain", "agency", "funding_type", "min_amount", "max_amount", "start_date", "end_date"]
            ),
            ReportTypeItem(
                id=ReportType.PATENT,
                name="Patent Landscape Report",
                description="Comprehensive IP disclosure analysis covering assignees, classifications, filing dates, citations, and technological clusters.",
                source_module="Module 5 (Patent Landscape Analysis)",
                supported_filters=["domain", "assignee", "start_year", "end_year"]
            ),
            ReportTypeItem(
                id=ReportType.RESEARCH_TREND,
                name="Research Trend Intelligence Report",
                description="Scientific publication momentum, accelerating keyword velocity, publication growth rates, and emerging thematic hotspots.",
                source_module="Module 3 (Research Intelligence)",
                supported_filters=["domain", "technology", "start_year", "end_year"]
            ),
            ReportTypeItem(
                id=ReportType.INNOVATION_INTELLIGENCE,
                name="Innovation Intelligence & 5-Pillar Report",
                description="Rigorous evaluation of Innovation Score across the 5 verified pillars (Novelty 30%, Patent Strength 20%, Technology Maturity 15%, Market Potential 20%, Funding Relevance 15%) and estimated TRL.",
                source_module="Modules 5, 6, 7 (Innovation Scoring & TRL)",
                supported_filters=["domain", "technology_stage", "my_profile_only"]
            ),
            ReportTypeItem(
                id=ReportType.COMMERCIALIZATION,
                name="Commercialization Pathways & Readiness Report",
                description="Conservative strategic evaluation of commercial readiness across 4 pathways (Productization, Licensing, Startup Spinout, Industry Partnership) with empirical IP and market signals.",
                source_module="Module 8 (Commercialization Recommendation)",
                supported_filters=["domain", "my_profile_only"]
            ),
            ReportTypeItem(
                id=ReportType.EXECUTIVE_DOSSIER,
                name="Executive Strategic Dossier",
                description="Synthesized strategic portfolio dossier combining SWOT assessment, phase-based technology roadmap, and cross-module benchmarks.",
                source_module="Module 9 (Dashboard & Strategic Dossier)",
                supported_filters=["domain", "my_profile_only"]
            ),
        ]
        return ReportTypesResponse(report_types=types)

    @classmethod
    async def gather_report_data(
        cls,
        filters: ReportFilterParams,
        user: Optional[User] = None,
        db: AsyncSession = None,
    ) -> ReportPreviewResponse:
        """
        Retrieves real platform data, applies backend filters, and generates a structured report payload.
        """
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        applied_filters: Dict[str, Any] = {}
        if filters.domain: applied_filters["Domain"] = filters.domain
        if filters.technology: applied_filters["Technology"] = filters.technology
        if filters.agency: applied_filters["Agency"] = filters.agency
        if filters.funding_type: applied_filters["Funding Type"] = filters.funding_type
        if filters.min_amount is not None: applied_filters["Min Amount"] = f"${filters.min_amount:,.0f}"
        if filters.max_amount is not None: applied_filters["Max Amount"] = f"${filters.max_amount:,.0f}"
        if filters.assignee: applied_filters["Assignee"] = filters.assignee
        if filters.start_year: applied_filters["Start Year"] = filters.start_year
        if filters.end_year: applied_filters["End Year"] = filters.end_year
        if filters.technology_stage: applied_filters["Stage"] = filters.technology_stage
        if filters.my_profile_only: applied_filters["Scope"] = "Authenticated Profile Only"

        # Resolve profile_id if scoped
        profile_id = None
        if filters.my_profile_only and user:
            prof_res = await db.execute(select(Profile.id).where(Profile.user_id == user.id))
            profile_id = prof_res.scalar_one_or_none()

        report_type = filters.report_type

        # =========================================================================
        # 1. FUNDING REPORT
        # =========================================================================
        if report_type == ReportType.FUNDING:
            query = select(FundingOpportunity)
            clauses = []
            if filters.domain:
                dom_clean = filters.domain.strip().lower()
                clauses.append(or_(
                    FundingOpportunity.description.ilike(f"%{dom_clean}%"),
                    FundingOpportunity.title.ilike(f"%{dom_clean}%")
                ))
            if filters.agency:
                clauses.append(FundingOpportunity.funding_agency.ilike(f"%{filters.agency.strip()}%"))
            if filters.funding_type:
                clauses.append(FundingOpportunity.opportunity_type.ilike(f"%{filters.funding_type.strip()}%"))
            if filters.min_amount is not None:
                clauses.append(FundingOpportunity.funding_amount >= filters.min_amount)
            if filters.max_amount is not None:
                clauses.append(FundingOpportunity.funding_amount <= filters.max_amount)
            if filters.start_date:
                try:
                    s_dt = datetime.fromisoformat(filters.start_date.replace("Z", "+00:00"))
                    clauses.append(FundingOpportunity.application_deadline >= s_dt)
                except Exception:
                    pass
            if filters.end_date:
                try:
                    e_dt = datetime.fromisoformat(filters.end_date.replace("Z", "+00:00"))
                    clauses.append(FundingOpportunity.application_deadline <= e_dt)
                except Exception:
                    pass

            if clauses:
                query = query.where(and_(*clauses))
            query = query.order_by(FundingOpportunity.application_deadline.asc().nulls_last()).limit(100)

            opps = (await db.execute(query)).scalars().all()
            total_grant_pool = sum(o.funding_amount or 0.0 for o in opps)
            avg_award = total_grant_pool / max(1, len(opps))
            upcoming_count = sum(1 for o in opps if o.application_deadline and o.application_deadline > datetime.now(timezone.utc))

            table_headers = ["Opportunity Title", "Agency", "Award Pool", "Deadline", "Opportunity Type", "Status"]
            table_rows = [
                [
                    o.title[:65],
                    o.funding_agency,
                    f"{o.currency or '$'}{o.funding_amount:,.0f}" if o.funding_amount else "N/A",
                    o.application_deadline.strftime("%Y-%m-%d") if o.application_deadline else "Rolling",
                    o.opportunity_type or "Grant",
                    o.status.upper()
                ]
                for o in opps
            ]

            if len(opps) == 0:
                summary = "No matching records found for the applied filter criteria. Identified 0 active research grant solicitations."
            else:
                summary = (
                    f"Identified {len(opps)} active research grant solicitations representing an aggregated funding "
                    f"pool of ${total_grant_pool:,.2f} USD. Average award sizing is ${avg_award:,.2f} USD across "
                    f"{len(set(o.funding_agency for o in opps))} distinct sponsoring organizations."
                )

            metrics = {
                "Total Opportunities": len(opps),
                "Total Grant Pool": f"${total_grant_pool:,.0f}",
                "Average Award Size": f"${avg_award:,.0f}",
                "Active / Open Solicitations": upcoming_count,
            }

            return ReportPreviewResponse(
                report_type=ReportType.FUNDING,
                title="Funding Intelligence & Grant Pipeline Report",
                generated_at=now_str,
                applied_filters=applied_filters,
                total_records=len(opps),
                metrics=metrics,
                summary_text=summary,
                table_headers=table_headers,
                table_rows=table_rows,
                recommendations=[
                    "Prioritize grant applications closing within the next 30 days.",
                    "Align technical proposal novelty with agency-specific solicitation focus areas."
                ],
                data_limitations="Award allocations reflect maximum indicated pools and remain subject to peer review."
            )

        # =========================================================================
        # 2. PATENT REPORT
        # =========================================================================
        elif report_type == ReportType.PATENT:
            query = select(Patent)
            clauses = []
            if filters.domain:
                query = query.where(Patent.technology_domain.ilike(f"%{filters.domain.strip()}%"))
            if filters.assignee:
                query = query.where(Patent.assignee.ilike(f"%{filters.assignee.strip()}%"))
            if filters.start_year:
                query = query.where(func.extract("year", Patent.filing_date) >= filters.start_year)
            if filters.end_year:
                query = query.where(func.extract("year", Patent.filing_date) <= filters.end_year)

            query = query.order_by(Patent.filing_date.desc().nulls_last(), Patent.id.desc()).limit(100)
            patents = (await db.execute(query)).scalars().all()

            distinct_assignees = set(p.assignee for p in patents if p.assignee)
            total_citations = sum(p.citation_count for p in patents)
            avg_citations = total_citations / max(1, len(patents))

            table_headers = ["Patent Number", "Title", "Assignee / Applicant", "Filing Date", "Domain", "Citations"]
            table_rows = [
                [
                    p.patent_number,
                    p.title[:65],
                    p.assignee or "Applicant Disclosed",
                    p.filing_date.strftime("%Y-%m-%d") if p.filing_date else "N/A",
                    p.technology_domain or "General",
                    p.citation_count
                ]
                for p in patents
            ]

            if len(patents) == 0:
                summary = "No matching records found for the applied filter criteria. Tracked 0 patent disclosures in selected category."
            else:
                summary = (
                    f"Tracked {len(patents)} patent disclosures across {len(distinct_assignees)} distinct organizations. "
                    f"Average forward citation velocity is {avg_citations:.1f} citations per patent, indicating sustained "
                    f"technological relevance in monitored classification areas."
                )

            metrics = {
                "Total Tracked Patents": len(patents),
                "Distinct Assignees": len(distinct_assignees),
                "Total Citations": total_citations,
                "Average Citation Depth": f"{avg_citations:.1f}",
            }

            return ReportPreviewResponse(
                report_type=ReportType.PATENT,
                title="Patent Landscape & Intellectual Property Report",
                generated_at=now_str,
                applied_filters=applied_filters,
                total_records=len(patents),
                metrics=metrics,
                summary_text=summary,
                table_headers=table_headers,
                table_rows=table_rows,
                recommendations=[
                    "Monitor high-citation competitor portfolios for potential IP freedom-to-operate clearances.",
                    "Identify whitespace gaps with low assignee concentration for defensive patent filings."
                ],
                data_limitations="Forward citations reflect indexed patent offices and may lag recent filings by 12-18 months."
            )

        # =========================================================================
        # 3. RESEARCH TREND REPORT
        # =========================================================================
        elif report_type == ReportType.RESEARCH_TREND:
            topics_resp = await ResearchTrendService.get_emerging_topics(
                domain=filters.domain,
                profile_id=profile_id,
                db=db
            )
            items = topics_resp.topics if topics_resp else []

            table_headers = ["Thematic Keyword", "Recent Count", "Historical Count", "Growth Rate", "Velocity Score", "Momentum Status"]
            table_rows = [
                [
                    it.topic,
                    str(it.recent_count),
                    str(it.historical_count),
                    f"+{it.growth_rate:.1f}%" if it.growth_rate is not None and it.growth_rate >= 0 else (f"{it.growth_rate:.1f}%" if it.growth_rate is not None else "N/A"),
                    f"{it.velocity_score:.1f}",
                    it.status
                ]
                for it in items
            ]

            total_pubs = sum(it.recent_count + it.historical_count for it in items)
            avg_velocity = sum(it.velocity_score for it in items) / max(1, len(items))

            summary = (
                f"Synthesized research trend velocity across {len(items)} monitored academic research topics. "
                f"Average velocity score stands at {avg_velocity:.1f} with {total_pubs} total publications "
                f"indexed across recent and historical evaluation windows."
            )

            metrics = {
                "Monitored Research Topics": len(items),
                "Total Publications Indexed": total_pubs,
                "Average Topic Velocity": f"{avg_velocity:.1f}",
                "Primary Accelerating Topic": items[0].topic if items else "N/A",
            }

            return ReportPreviewResponse(
                report_type=ReportType.RESEARCH_TREND,
                title="Research Trend Intelligence & Literature Momentum Report",
                generated_at=now_str,
                applied_filters=applied_filters,
                total_records=len(items),
                metrics=metrics,
                summary_text=summary,
                table_headers=table_headers,
                table_rows=table_rows,
                recommendations=[
                    "Target accelerating topic keywords in upcoming peer-reviewed publications and conference submissions.",
                    "Form interdisciplinary collaborations around topics with sustained positive multi-year growth."
                ],
                data_limitations="Literature trends rely on indexed scientific metadata and preprint archives."
            )

        # =========================================================================
        # 4. INNOVATION INTELLIGENCE REPORT (5-Pillar Score Breakdown)
        # =========================================================================
        elif report_type == ReportType.INNOVATION_INTELLIGENCE:
            target_domain = filters.domain or "Quantum Computing"
            innov = await InnovationScoringService.calculate_innovation_score(
                domain=target_domain,
                profile_id=profile_id,
                db=db
            )
            whitespaces = await TechnologyIntelligenceService.detect_whitespaces(
                domain=target_domain,
                profile_id=profile_id,
                db=db
            )

            # Strict Mentor Requirement: Must explain the 5 contributing factors with official weights!
            factors: List[ReportFactorItem] = [
                ReportFactorItem(
                    factor_name="Research Novelty",
                    weight_pct=30.0,
                    score=innov.pillars["research_novelty"].score,
                    status=innov.pillars["research_novelty"].data_status,
                    description="Academic novelty, publication density, citation velocity, and venue diversity.",
                    signals=innov.pillars["research_novelty"].contributing_signals
                ),
                ReportFactorItem(
                    factor_name="Patent Strength",
                    weight_pct=20.0,
                    score=innov.pillars["patent_strength"].score,
                    status=innov.pillars["patent_strength"].data_status,
                    description="Protected patent disclosures, grant ratios, jurisdiction reach, and claims coverage.",
                    signals=innov.pillars["patent_strength"].contributing_signals
                ),
                ReportFactorItem(
                    factor_name="Technology Maturity",
                    weight_pct=15.0,
                    score=innov.pillars["technology_maturity"].score,
                    status=innov.pillars["technology_maturity"].data_status,
                    description="6-indicator maturity assessment across research growth, patent growth, organizations, and diversity.",
                    signals=innov.pillars["technology_maturity"].contributing_signals
                ),
                ReportFactorItem(
                    factor_name="Market Potential",
                    weight_pct=20.0,
                    score=innov.pillars["market_potential"].score,
                    status=innov.pillars["market_potential"].data_status,
                    description="Commercial assignee concentration (HHI), addressable whitespace gaps, and industrial demand.",
                    signals=innov.pillars["market_potential"].contributing_signals
                ),
                ReportFactorItem(
                    factor_name="Funding Relevance",
                    weight_pct=15.0,
                    score=innov.pillars["funding_relevance"].score,
                    status=innov.pillars["funding_relevance"].data_status,
                    description="Matching open grant pool, sponsor diversity, and non-dilutive capital availability.",
                    signals=innov.pillars["funding_relevance"].contributing_signals
                ),
            ]

            table_headers = ["Pillar Factor", "Weight (%)", "Normalized Score (0-100)", "Weighted Contribution", "Status", "Primary Evidence"]
            table_rows = [
                [
                    f.factor_name,
                    f"{f.weight_pct:.0f}%",
                    f"{f.score:.1f}",
                    f"{(f.score * (f.weight_pct / 100.0)):.2f}",
                    f.status,
                    f.description
                ]
                for f in factors
            ]

            summary = (
                f"Evaluated Innovation Score for '{innov.target_name or target_domain}' is {innov.innovation_score:.1f} / 100 "
                f"({innov.overall_classification.replace('_', ' ')}). Technology Readiness Level is estimated at TRL {innov.trl.estimated_trl} "
                f"({innov.trl.trl_stage}). Evaluation combines 30% Novelty, 20% Patent Strength, 15% Tech Maturity, "
                f"20% Market Potential, and 15% Funding Relevance."
            )

            metrics = {
                "Composite Innovation Score": f"{innov.innovation_score:.1f} / 100",
                "Estimated Readiness": f"TRL {innov.trl.estimated_trl}",
                "TRL Classification": innov.trl.trl_stage,
                "Whitespace Opportunities": len(whitespaces.candidates),
            }

            return ReportPreviewResponse(
                report_type=ReportType.INNOVATION_INTELLIGENCE,
                title="Innovation Intelligence & 5-Pillar Score Factor Report",
                generated_at=now_str,
                applied_filters=applied_filters,
                total_records=5,
                metrics=metrics,
                summary_text=summary,
                table_headers=table_headers,
                table_rows=table_rows,
                factors=factors,
                recommendations=[
                    "Leverage existing patent strength to apply for high-value federal non-dilutive translation grants.",
                    f"Advance prototype validation from TRL {innov.trl.estimated_trl} toward demonstrated operational feasibility."
                ],
                data_limitations="Scores use normalized multi-source signals. Incomplete disclosures default conservatively to INSUFFICIENT_DATA status."
            )

        # =========================================================================
        # 5. COMMERCIALIZATION REPORT
        # =========================================================================
        elif report_type == ReportType.COMMERCIALIZATION:
            target_domain = filters.domain or "Quantum Computing"
            comm = await CommercializationService.evaluate_commercialization(
                domain=target_domain,
                profile_id=profile_id,
                db=db
            )

            readiness = comm.readiness
            pathways = comm.pathways

            prod_concept = pathways.productization.product_concept[:60] if pathways and pathways.productization else "N/A"
            prod_status = pathways.productization.data_status if pathways and pathways.productization else "INSUFFICIENT_DATA"
            prod_ind = pathways.productization.target_industry if pathways and pathways.productization else "N/A"

            lic_status = pathways.licensing.data_status if pathways and pathways.licensing else "INSUFFICIENT_DATA"
            lic_count = len(pathways.licensing.licensing_candidates) if pathways and pathways.licensing else 0

            startup_status = pathways.startup_creation.data_status if pathways and pathways.startup_creation else "INSUFFICIENT_DATA"
            startup_concept = pathways.startup_creation.startup_concept[:60] if pathways and pathways.startup_creation else "N/A"

            partner_status = pathways.industry_partnership.data_status if pathways and pathways.industry_partnership else "INSUFFICIENT_DATA"
            partner_count = len(pathways.industry_partnership.partnership_candidates) if pathways and pathways.industry_partnership else 0

            table_headers = ["Commercial Pathway", "Feasibility Status", "Readiness Score", "Primary Concept", "Target Industry"]
            table_rows = [
                [
                    "Productization",
                    prod_status,
                    f"{readiness.readiness_score:.1f} / 100",
                    prod_concept,
                    prod_ind
                ],
                [
                    "Licensing",
                    lic_status,
                    f"{readiness.readiness_score:.1f} / 100",
                    f"{lic_count} potential industrial licensee(s) identified",
                    "Advanced Technology & IP"
                ],
                [
                    "Startup Spinout",
                    startup_status,
                    f"{readiness.readiness_score:.1f} / 100",
                    startup_concept,
                    "Deep-Tech Venture"
                ],
                [
                    "Industry Partnership",
                    partner_status,
                    f"{readiness.readiness_score:.1f} / 100",
                    f"{partner_count} potential co-development partner(s)",
                    "Public-Private Consortium"
                ],
            ]

            summary = (
                f"Commercial readiness assessment for '{comm.target_name}' produced an overall readiness score of "
                f"{readiness.readiness_score:.1f} / 100 ({readiness.readiness_level.replace('_', ' ')}). The primary recommended strategic pathway "
                f"is a potential {readiness.primary_pathway.lower().replace('_', ' ')} based on empirical IP maturity, "
                f"available grants, and industry demand signals."
            )

            metrics = {
                "Commercial Readiness Score": f"{readiness.readiness_score:.1f} / 100",
                "Primary Pathway": readiness.primary_pathway.replace("_", " "),
                "Readiness Stage": readiness.readiness_level.replace("_", " "),
                "Identified Capital Pool": f"${sum(f.get('funding_amount', 0.0) or 0.0 for f in comm.funding_opportunities):,.0f}",
            }

            return ReportPreviewResponse(
                report_type=ReportType.COMMERCIALIZATION,
                title="Commercialization Pathways & Readiness Assessment Report",
                generated_at=now_str,
                applied_filters=applied_filters,
                total_records=4,
                metrics=metrics,
                summary_text=summary,
                table_headers=table_headers,
                table_rows=table_rows,
                recommendations=[
                    f"Pursue an initial exploratory {readiness.primary_pathway.lower().replace('_', ' ')} pathway.",
                    "Engage prospective industrial partners for confidential non-disclosure technical briefings."
                ],
                data_limitations="All commercial assessments represent potential advisory pathways and do not guarantee market investment or commercial viability."
            )

        # =========================================================================
        # 6. EXECUTIVE DOSSIER REPORT
        # =========================================================================
        else:
            target_domain = filters.domain or "Quantum Computing"
            dossier = await ExecutiveReportService.generate_dossier(
                domain=target_domain,
                profile_id=profile_id,
                db=db
            )

            table_headers = ["Strategic Pillar", "Metric Key", "Measured Value", "Status"]
            table_rows = [
                ["Innovation Scoring", "5-Pillar Score", f"{dossier.innovation_score:.1f} / 100", dossier.innovation_classification],
                ["Technology Readiness", "Estimated TRL", f"TRL {dossier.estimated_trl}", dossier.trl_stage],
                ["Commercialization", "Readiness Score", f"{dossier.commercialization_readiness:.1f} / 100", dossier.readiness_level],
                ["Primary Pathway", "Strategy", dossier.primary_commercial_pathway.replace("_", " "), "RECOMMENDED"],
                ["Publications", "Total Indexed", str(dossier.publication_metrics.get("total_publications", 0)), "VERIFIED"],
                ["Patents", "Total Disclosures", str(dossier.patent_metrics.get("total_patents", 0)), "VERIFIED"],
                ["Grant Funding", "Identified Pool", f"${dossier.funding_metrics.get('total_identified_grant_pool', 0.0):,.0f}", "AVAILABLE"],
            ]

            metrics = {
                "Composite Innovation": f"{dossier.innovation_score:.1f} / 100",
                "Estimated Readiness": f"TRL {dossier.estimated_trl}",
                "Commercial Readiness": f"{dossier.commercialization_readiness:.1f} / 100",
                "Primary Pathway": dossier.primary_commercial_pathway.replace("_", " "),
            }

            return ReportPreviewResponse(
                report_type=ReportType.EXECUTIVE_DOSSIER,
                title="Executive Strategic Intelligence Dossier",
                generated_at=now_str,
                applied_filters=applied_filters,
                total_records=len(table_rows),
                metrics=metrics,
                summary_text=dossier.executive_summary,
                table_headers=table_headers,
                table_rows=table_rows,
                recommendations=[r.get("recommendation", "") for r in dossier.top_recommendations[:3] if isinstance(r, dict)],
                data_limitations=dossier.governance_disclaimer
            )

    @classmethod
    def generate_pdf(cls, report_data: ReportPreviewResponse) -> bytes:
        """
        Generates a professional, beautifully styled PDF document using ReportLab.
        Includes cover header, executive summary, metrics cards table, factor breakdown,
        data table with auto-wrapped text, recommendations, and compliance footer.
        """
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
            HRFlowable,
            KeepTogether,
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        primary_color = colors.HexColor("#0f172a") # Slate 900
        accent_color = colors.HexColor("#2563eb")  # Blue 600
        muted_color = colors.HexColor("#64748b")   # Slate 500
        border_color = colors.HexColor("#e2e8f0")  # Slate 200
        bg_card = colors.HexColor("#f8fafc")       # Slate 50

        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=18,
            leading=22,
            textColor=primary_color,
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            textColor=muted_color,
            spaceAfter=8
        )
        section_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=12,
            leading=15,
            textColor=primary_color,
            spaceBefore=10,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'ReportBody',
            parent=styles['Normal'],
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#334155")
        )
        table_cell_style = ParagraphStyle(
            'TableCell',
            parent=styles['Normal'],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#1e293b")
        )
        table_hdr_style = ParagraphStyle(
            'TableHdr',
            parent=styles['Normal'],
            fontSize=8,
            leading=10,
            textColor=colors.white,
            fontName="Helvetica-Bold"
        )

        elements = []

        # 1. Header & Platform Title
        elements.append(Paragraph("<b>RESEARCH FUNDING & INNOVATION INTELLIGENCE PLATFORM</b>", subtitle_style))
        elements.append(Paragraph(report_data.title, title_style))
        filters_str = ", ".join(f"{k}: {v}" for k, v in report_data.applied_filters.items()) if report_data.applied_filters else "Standard Baseline (No extra filters)"
        elements.append(Paragraph(f"<b>Generated:</b> {report_data.generated_at} &nbsp;|&nbsp; <b>Filters:</b> {filters_str}", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=accent_color, spaceAfter=8))

        # 2. Key Metrics Summary Grid
        if report_data.metrics:
            metric_items = list(report_data.metrics.items())
            # Layout as 2x2 or 4x1 table
            metric_data = []
            row = []
            for k, v in metric_items:
                row.append(Paragraph(f"<b>{k}</b><br/><font size='10' color='#2563eb'><b>{v}</b></font>", body_style))
                if len(row) == 4:
                    metric_data.append(row)
                    row = []
            if row:
                while len(row) < 4:
                    row.append(Paragraph("", body_style))
                metric_data.append(row)

            m_table = Table(metric_data, colWidths=[135, 135, 135, 135])
            m_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), bg_card),
                ('BOX', (0, 0), (-1, -1), 0.5, border_color),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(m_table)
            elements.append(Spacer(1, 8))

        # 3. Executive Summary
        elements.append(Paragraph("<b>Executive Summary</b>", section_style))
        elements.append(Paragraph(report_data.summary_text, body_style))
        elements.append(Spacer(1, 8))

        # 4. Innovation Factors Breakdown (Specifically for Innovation Intelligence)
        if report_data.factors:
            elements.append(Paragraph("<b>Innovation Score Factor Contribution (Official Weights)</b>", section_style))
            factor_table_data = [
                [
                    Paragraph("Factor / Pillar", table_hdr_style),
                    Paragraph("Weight", table_hdr_style),
                    Paragraph("Score (0-100)", table_hdr_style),
                    Paragraph("Contribution", table_hdr_style),
                    Paragraph("Status", table_hdr_style),
                    Paragraph("Description", table_hdr_style),
                ]
            ]
            for f in report_data.factors:
                contrib = f.score * (f.weight_pct / 100.0)
                factor_table_data.append([
                    Paragraph(f"<b>{f.factor_name}</b>", table_cell_style),
                    Paragraph(f"{f.weight_pct:.0f}%", table_cell_style),
                    Paragraph(f"{f.score:.1f}", table_cell_style),
                    Paragraph(f"{contrib:.2f}", table_cell_style),
                    Paragraph(f.status, table_cell_style),
                    Paragraph(f.description, table_cell_style),
                ])

            f_table = Table(factor_table_data, colWidths=[100, 45, 65, 65, 75, 190])
            f_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), primary_color),
                ('BOX', (0, 0), (-1, -1), 0.5, border_color),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, bg_card]),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(f_table)
            elements.append(Spacer(1, 10))

        # 5. Main Records Table
        elements.append(Paragraph(f"<b>Detailed Findings & Empirical Records ({report_data.total_records} Records)</b>", section_style))
        if report_data.table_rows:
            hdr_cells = [Paragraph(f"<b>{h}</b>", table_hdr_style) for h in report_data.table_headers]
            grid_data = [hdr_cells]

            # Limit preview rows to 40 in PDF to maintain optimal page budget
            display_rows = report_data.table_rows[:40]
            col_count = len(report_data.table_headers)
            col_width = 540.0 / float(col_count)

            for r in display_rows:
                row_cells = [Paragraph(str(val), table_cell_style) for val in r]
                grid_data.append(row_cells)

            r_table = Table(grid_data, colWidths=[col_width] * col_count)
            r_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), primary_color),
                ('BOX', (0, 0), (-1, -1), 0.5, border_color),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, bg_card]),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(r_table)
            if len(report_data.table_rows) > 40:
                elements.append(Spacer(1, 4))
                elements.append(Paragraph(f"<i>Displaying first 40 of {report_data.total_records} records. Complete dataset available in Excel export.</i>", subtitle_style))
        else:
            elements.append(Paragraph("<i>No records identified matching the requested criteria.</i>", body_style))

        elements.append(Spacer(1, 8))

        # 6. Strategic Recommendations
        if report_data.recommendations:
            elements.append(Paragraph("<b>Strategic Next Steps & Recommendations</b>", section_style))
            for rec in report_data.recommendations:
                elements.append(Paragraph(f"• {rec}", body_style))
            elements.append(Spacer(1, 8))

        # 7. Compliance & Data Limitations Footer
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=border_color, spaceAfter=4))
        disclaimer = report_data.data_limitations or (
            "This report is an automated intelligence synthesis provided for strategic research and translation decision support. "
            "It does not constitute legal freedom-to-operate advice or binding financial valuation."
        )
        elements.append(Paragraph(f"<font size='7' color='#64748b'><b>Governance Notice:</b> {disclaimer}</font>", body_style))

        doc.build(elements)
        return buffer.getvalue()

    @classmethod
    def generate_excel(cls, report_data: ReportPreviewResponse) -> bytes:
        """
        Generates a structured, professional .xlsx workbook using openpyxl.
        Features styled headers, explicit column widths, numeric formatting,
        and dedicated sheets for Summary, Data, and Factors.
        """
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter

        wb = openpyxl.Workbook()

        # Styles
        hdr_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        hdr_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
        title_font = Font(name="Calibri", size=14, bold=True, color="0F172A")
        sub_font = Font(name="Calibri", size=10, italic=True, color="64748B")
        bold_font = Font(name="Calibri", size=11, bold=True)
        thin_border = Border(
            left=Side(style='thin', color='E2E8F0'),
            right=Side(style='thin', color='E2E8F0'),
            top=Side(style='thin', color='E2E8F0'),
            bottom=Side(style='thin', color='E2E8F0')
        )

        # -------------------------------------------------------------
        # SHEET 1: Summary & Metrics
        # -------------------------------------------------------------
        ws_sum = wb.active
        ws_sum.title = "Summary & Metrics"

        ws_sum.cell(row=1, column=1, value="RESEARCH FUNDING & INNOVATION INTELLIGENCE PLATFORM").font = sub_font
        ws_sum.cell(row=2, column=1, value=report_data.title).font = title_font
        ws_sum.cell(row=3, column=1, value=f"Generated: {report_data.generated_at}").font = sub_font

        # Metadata & Applied Filters
        ws_sum.cell(row=5, column=1, value="Report Category:").font = bold_font
        ws_sum.cell(row=5, column=2, value=str(report_data.report_type))
        ws_sum.cell(row=6, column=1, value="Total Records:").font = bold_font
        ws_sum.cell(row=6, column=2, value=report_data.total_records)

        r_curr = 8
        ws_sum.cell(row=r_curr, column=1, value="Applied Filter").font = hdr_font
        ws_sum.cell(row=r_curr, column=1).fill = hdr_fill
        ws_sum.cell(row=r_curr, column=2, value="Configured Value").font = hdr_font
        ws_sum.cell(row=r_curr, column=2).fill = hdr_fill

        r_curr += 1
        if report_data.applied_filters:
            for k, v in report_data.applied_filters.items():
                ws_sum.cell(row=r_curr, column=1, value=k)
                ws_sum.cell(row=r_curr, column=2, value=str(v))
                r_curr += 1
        else:
            ws_sum.cell(row=r_curr, column=1, value="Filters")
            ws_sum.cell(row=r_curr, column=2, value="None (Full Dataset)")
            r_curr += 1

        r_curr += 1
        ws_sum.cell(row=r_curr, column=1, value="Key Metric").font = hdr_font
        ws_sum.cell(row=r_curr, column=1).fill = hdr_fill
        ws_sum.cell(row=r_curr, column=2, value="Measured Outcome").font = hdr_font
        ws_sum.cell(row=r_curr, column=2).fill = hdr_fill

        r_curr += 1
        for mk, mv in report_data.metrics.items():
            ws_sum.cell(row=r_curr, column=1, value=mk)
            ws_sum.cell(row=r_curr, column=2, value=str(mv))
            r_curr += 1

        r_curr += 2
        ws_sum.cell(row=r_curr, column=1, value="Executive Narrative Summary:").font = bold_font
        r_curr += 1
        ws_sum.cell(row=r_curr, column=1, value=report_data.summary_text)

        # -------------------------------------------------------------
        # SHEET 2: Data Records
        # -------------------------------------------------------------
        ws_data = wb.create_sheet(title="Data Records")

        # Table Headers
        for col_idx, h in enumerate(report_data.table_headers, start=1):
            cell = ws_data.cell(row=1, column=col_idx, value=h)
            cell.font = hdr_font
            cell.fill = hdr_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")

        # Table Rows
        for row_idx, r in enumerate(report_data.table_rows, start=2):
            for col_idx, val in enumerate(r, start=1):
                cell = ws_data.cell(row=row_idx, column=col_idx, value=val)
                cell.border = thin_border
                if isinstance(val, (int, float)):
                    cell.alignment = Alignment(horizontal="right")
                else:
                    cell.alignment = Alignment(horizontal="left")

        # -------------------------------------------------------------
        # SHEET 3: Innovation Factor Breakdown (if applicable)
        # -------------------------------------------------------------
        if report_data.factors:
            ws_factors = wb.create_sheet(title="5-Pillar Score Factors")
            f_headers = ["Pillar Factor", "Weight (%)", "Normalized Score (0-100)", "Weighted Contribution", "Status", "Factor Description"]
            for col_idx, fh in enumerate(f_headers, start=1):
                cell = ws_factors.cell(row=1, column=col_idx, value=fh)
                cell.font = hdr_font
                cell.fill = hdr_fill

            for r_idx, f in enumerate(report_data.factors, start=2):
                contrib = f.score * (f.weight_pct / 100.0)
                ws_factors.cell(row=r_idx, column=1, value=f.factor_name).font = bold_font
                ws_factors.cell(row=r_idx, column=2, value=f.weight_pct)
                ws_factors.cell(row=r_idx, column=3, value=f.score)
                ws_factors.cell(row=r_idx, column=4, value=round(contrib, 2))
                ws_factors.cell(row=r_idx, column=5, value=f.status)
                ws_factors.cell(row=r_idx, column=6, value=f.description)
                for c in range(1, 7):
                    ws_factors.cell(row=r_idx, column=c).border = thin_border

        # Auto-adjust column widths across all sheets
        for sheet in wb.worksheets:
            for col in sheet.columns:
                max_len = 0
                col_letter = get_column_letter(col[0].column)
                for cell in col:
                    val_str = str(cell.value or '')
                    if '\n' in val_str:
                        val_str = val_str.split('\n')[0]
                    max_len = max(max_len, len(val_str))
                sheet.column_dimensions[col_letter].width = min(50, max(12, max_len + 3))

        buf = io.BytesIO()
        wb.save(buf)
        return buf.getvalue()
