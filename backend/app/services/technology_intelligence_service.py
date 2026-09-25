import re
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import select, func, desc, and_, or_, distinct, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patent import Patent, profile_patents
from app.models.publication import Publication, profile_publications
from app.models.research_domain import TechnologyArea
from app.schemas.technology_intelligence import (
    TechnologyActivityItem,
    TechnologyActivityResponse,
    TechnologyGrowthItem,
    TechnologyGrowthResponse,
    TechnologyCoverageItem,
    TechnologyCoverageResponse,
    WhitespaceCandidateItem,
    WhitespaceDiscoveryResponse,
    TechnologyIntelligenceSummary,
    MaturityIndicatorBreakdown,
    TechnologyMaturityItem,
    TechnologyMaturityResponse,
    AdoptionTrackingItem,
    AdoptionTrackingResponse,
    EmergingTechnologyItem,
    EmergingTechnologyResponse,
    CompetitiveTechnologyItem,
    CompetitiveTechnologyResponse,
)


class TechnologyIntelligenceService:
    """
    Deterministic Technology Intelligence and Whitespace Discovery Service.
    Performs fast SQL-level aggregations and multi-signal heuristics on patent metadata,
    domains, classifications, assignees, jurisdictions, and filing timelines.
    """

    @staticmethod
    def _extract_jurisdiction_code(patent_number: Optional[str]) -> str:
        if not patent_number:
            return "GLOBAL"
        match = re.match(r"^([A-Za-z]{2})", patent_number.strip())
        if match:
            return match.group(1).upper()
        return "US"

    @staticmethod
    def _calculate_cagr(start_val: float, end_val: float, num_years: int) -> Tuple[Optional[float], str]:
        """
        Calculates multi-year Compound Annual Growth Rate (CAGR) safely:
        CAGR = (Ending Value / Beginning Value) ^ (1 / Number of Years) - 1
        Safely handles baseline zero, negative, or single-year data without division by zero.
        """
        if num_years < 1:
            return None, "INSUFFICIENT_DATA"
        if start_val <= 0:
            return None, "BASELINE_ZERO"
        if end_val < 0:
            return None, "INVALID_VALUE"
        try:
            cagr = ((float(end_val) / float(start_val)) ** (1.0 / float(num_years)) - 1.0) * 100.0
            return round(cagr, 2), "COMPUTED"
        except Exception:
            return None, "ERROR"

    @classmethod
    def _apply_pub_filters(
        cls,
        query,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        domain: Optional[str] = None,
        profile_id: Optional[int] = None,
    ):
        if profile_id is not None:
            query = query.join(profile_publications, profile_publications.c.publication_id == Publication.id).where(
                profile_publications.c.profile_id == profile_id
            )
        if start_year is not None:
            query = query.where(func.extract("year", Publication.publication_date) >= start_year)
        if end_year is not None:
            query = query.where(func.extract("year", Publication.publication_date) <= end_year)
        if domain and domain.strip():
            dom = domain.strip().lower()
            query = query.where(func.lower(Publication.primary_domain) == dom)
        return query

    @classmethod
    def _apply_base_filters(
        cls,
        query,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        domain: Optional[str] = None,
        technology_area: Optional[str] = None,
        classification: Optional[str] = None,
        keyword: Optional[str] = None,
        profile_id: Optional[int] = None,
    ):
        if profile_id is not None:
            query = query.join(profile_patents, profile_patents.c.patent_id == Patent.id).where(
                profile_patents.c.profile_id == profile_id
            )

        if start_year is not None:
            query = query.where(
                or_(
                    func.extract("year", Patent.filing_date) >= start_year,
                    and_(Patent.filing_date.is_(None), func.extract("year", Patent.publication_date) >= start_year),
                )
            )

        if end_year is not None:
            query = query.where(
                or_(
                    func.extract("year", Patent.filing_date) <= end_year,
                    and_(Patent.filing_date.is_(None), func.extract("year", Patent.publication_date) <= end_year),
                )
            )

        if domain and domain.strip():
            dom = domain.strip().lower()
            query = query.where(func.lower(Patent.technology_domain) == dom)

        if technology_area and technology_area.strip():
            tech_clean = technology_area.strip().lower()
            query = query.where(
                or_(
                    func.lower(Patent.technology_domain).ilike(f"%{tech_clean}%"),
                    func.lower(Patent.title).ilike(f"%{tech_clean}%"),
                    func.lower(Patent.abstract).ilike(f"%{tech_clean}%"),
                )
            )

        if classification and classification.strip():
            cls_clean = classification.strip().upper()
            query = query.where(func.upper(Patent.patent_classification).ilike(f"%{cls_clean}%"))

        if keyword and keyword.strip():
            kw_clean = keyword.strip().lower()
            query = query.where(
                or_(
                    func.lower(Patent.title).ilike(f"%{kw_clean}%"),
                    func.lower(Patent.abstract).ilike(f"%{kw_clean}%"),
                    func.lower(Patent.technology_domain).ilike(f"%{kw_clean}%"),
                )
            )

        return query

    @classmethod
    async def get_technology_activity(
        cls,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        domain: Optional[str] = None,
        technology_area: Optional[str] = None,
        classification: Optional[str] = None,
        keyword: Optional[str] = None,
        profile_id: Optional[int] = None,
        db: AsyncSession = None,
    ) -> TechnologyActivityResponse:
        """
        Calculates structured technology activity metrics grouped by technology domain/area.
        """
        current_year = datetime.now(timezone.utc).year
        recent_threshold_year = current_year - 2

        # 1. Total corpus count
        total_stmt = select(func.count(Patent.id))
        total_stmt = cls._apply_base_filters(
            total_stmt, start_year, end_year, domain, technology_area, classification, keyword, profile_id
        )
        total_patents = (await db.execute(total_stmt)).scalar() or 0

        if total_patents == 0:
            return TechnologyActivityResponse(
                items=[],
                total_patents=0,
                total_technology_areas=0,
                summary_by_level={"HIGH_ACTIVITY": 0, "MEDIUM_ACTIVITY": 0, "LOW_ACTIVITY": 0},
                timeframe_analyzed={"start_year": start_year, "end_year": end_year},
            )

        # 2. Main group aggregation by technology_domain
        domain_col = func.coalesce(Patent.technology_domain, "General / Cross-Disciplinary").label("domain_name")
        recent_case = case((func.extract("year", Patent.filing_date) >= recent_threshold_year, 1), else_=0)
        grant_case = case(
            (
                or_(
                    Patent.patent_number.ilike("%B%"),
                    and_(Patent.publication_date.is_not(None), Patent.filing_date.is_not(None)),
                ),
                1,
            ),
            else_=0,
        )

        agg_stmt = (
            select(
                domain_col,
                func.count(Patent.id).label("patent_count"),
                func.sum(recent_case).label("recent_patent_count"),
                func.count(Patent.filing_date).label("filing_count"),
                func.sum(grant_case).label("grant_count"),
                func.coalesce(func.sum(Patent.citation_count), 0).label("citation_count"),
                func.coalesce(func.avg(Patent.citation_count), 0.0).label("avg_citations"),
                func.count(distinct(func.lower(func.coalesce(Patent.assignee, "Individual")))).label("assignee_count"),
            )
            .group_by(domain_col)
            .order_by(desc("patent_count"))
        )
        agg_stmt = cls._apply_base_filters(
            agg_stmt, start_year, end_year, domain, technology_area, classification, keyword, profile_id
        )

        rows = (await db.execute(agg_stmt)).all()

        items: List[TechnologyActivityItem] = []
        summary_by_level = {"HIGH_ACTIVITY": 0, "MEDIUM_ACTIVITY": 0, "LOW_ACTIVITY": 0}

        for row in rows:
            p_count = int(row.patent_count or 0)
            rec_count = int(row.recent_patent_count or 0)
            fil_count = int(row.filing_count or p_count)
            grt_count = int(row.grant_count or 0)
            cite_count = int(row.citation_count or 0)
            avg_cite = round(float(row.avg_citations or 0.0), 2)
            ass_count = int(row.assignee_count or 0)
            dom_name = str(row.domain_name)

            # Determine activity level
            if p_count >= 10 or ass_count >= 5:
                act_level = "HIGH_ACTIVITY"
            elif p_count >= 3:
                act_level = "MEDIUM_ACTIVITY"
            else:
                act_level = "LOW_ACTIVITY"

            summary_by_level[act_level] += 1

            # Fetch representative classification and jurisdictions for this domain
            meta_stmt = (
                select(
                    Patent.patent_classification,
                    Patent.patent_number,
                )
                .where(func.coalesce(Patent.technology_domain, "General / Cross-Disciplinary") == dom_name)
                .limit(20)
            )
            if profile_id is not None:
                meta_stmt = meta_stmt.join(profile_patents, profile_patents.c.patent_id == Patent.id).where(
                    profile_patents.c.profile_id == profile_id
                )

            meta_rows = (await db.execute(meta_stmt)).all()
            primary_cls = None
            jurisdictions_set = set()
            for m in meta_rows:
                if m.patent_classification and not primary_cls:
                    primary_cls = m.patent_classification
                if m.patent_number:
                    jurisdictions_set.add(cls._extract_jurisdiction_code(m.patent_number))

            items.append(
                TechnologyActivityItem(
                    technology_area=dom_name,
                    technology_domain=dom_name,
                    classification_code=primary_cls,
                    patent_count=p_count,
                    recent_patent_count=rec_count,
                    filing_count=fil_count,
                    grant_count=grt_count,
                    citation_count=cite_count,
                    average_citations=avg_cite,
                    assignee_count=ass_count,
                    jurisdictions=sorted(list(jurisdictions_set)),
                    activity_level=act_level,
                )
            )

        return TechnologyActivityResponse(
            items=items,
            total_patents=total_patents,
            total_technology_areas=len(items),
            summary_by_level=summary_by_level,
            timeframe_analyzed={"start_year": start_year, "end_year": end_year},
        )

    @classmethod
    async def get_technology_growth(
        cls,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        domain: Optional[str] = None,
        profile_id: Optional[int] = None,
        db: AsyncSession = None,
    ) -> TechnologyGrowthResponse:
        """
        Calculates deterministic technology growth and velocity rates comparing recent window to historical window.
        """
        current_year = datetime.now(timezone.utc).year
        recent_split_year = current_year - 2

        # 1. Fetch domain-level patent years
        domain_col = func.coalesce(Patent.technology_domain, "General / Cross-Disciplinary").label("domain_name")
        year_col = func.coalesce(
            func.extract("year", Patent.filing_date),
            func.extract("year", Patent.publication_date),
        ).label("p_year")

        stmt = (
            select(
                domain_col,
                year_col,
                func.count(Patent.id).label("count"),
            )
            .where(year_col.is_not(None))
            .group_by(domain_col, year_col)
            .order_by(domain_col, year_col)
        )
        stmt = cls._apply_base_filters(
            stmt, start_year=start_year, end_year=end_year, domain=domain, profile_id=profile_id
        )

        rows = (await db.execute(stmt)).all()

        # Group counts by domain and year
        domain_years: Dict[str, Dict[int, int]] = {}
        for r in rows:
            d_name = str(r.domain_name)
            yr = int(r.p_year)
            cnt = int(r.count)
            if d_name not in domain_years:
                domain_years[d_name] = {}
            domain_years[d_name][yr] = cnt

        growth_items: List[TechnologyGrowthItem] = []
        summary_by_trajectory = {
            "RAPID_ACCELERATION": 0,
            "STEADY_GROWTH": 0,
            "MATURE_STABLE": 0,
            "DECLINING": 0,
            "EMERGING_SPARSE": 0,
        }

        for d_name, yr_map in domain_years.items():
            recent_count = sum(c for y, c in yr_map.items() if y >= recent_split_year)
            hist_years = [y for y in yr_map.keys() if y < recent_split_year]
            hist_count = sum(yr_map[y] for y in hist_years)
            total_count = recent_count + hist_count

            # Annualized historical rate
            hist_span = max(1, len(hist_years)) if hist_years else 1
            hist_annual = hist_count / float(hist_span)
            recent_annual = recent_count / 2.0

            # Growth rate calculation
            if hist_count > 0:
                growth_rate_pct = round(((recent_annual - hist_annual) / hist_annual) * 100.0, 2)
            else:
                growth_rate_pct = None  # Baseline year / emerging area with no historical baseline

            # Velocity score: proportion of portfolio filed recently (0 to 100)
            velocity_score = round(min(100.0, (recent_count / float(max(1, total_count))) * 100.0), 2)

            # Growth trajectory classification
            if velocity_score >= 60.0 and recent_count >= 2:
                trajectory = "RAPID_ACCELERATION"
            elif growth_rate_pct is not None and growth_rate_pct > 15.0 and velocity_score >= 30.0:
                trajectory = "STEADY_GROWTH"
            elif total_count >= 4 and 15.0 <= velocity_score <= 45.0:
                trajectory = "MATURE_STABLE"
            elif total_count <= 2:
                trajectory = "EMERGING_SPARSE"
            elif growth_rate_pct is not None and growth_rate_pct < -20.0:
                trajectory = "DECLINING"
            else:
                trajectory = "EMERGING_SPARSE"

            # Multi-year CAGR calculation
            if len(yr_map) >= 2:
                sorted_years = sorted(yr_map.keys())
                min_yr = sorted_years[0]
                max_yr = sorted_years[-1]
                year_span = max_yr - min_yr
                cagr_val, cagr_stat = cls._calculate_cagr(yr_map[min_yr], yr_map[max_yr], year_span)
            elif len(yr_map) == 1:
                cagr_val, cagr_stat = None, "INSUFFICIENT_DATA"
            else:
                cagr_val, cagr_stat = None, "INSUFFICIENT_DATA"

            summary_by_trajectory[trajectory] += 1

            growth_items.append(
                TechnologyGrowthItem(
                    technology_area=d_name,
                    technology_domain=d_name,
                    recent_period_filings=recent_count,
                    historical_period_filings=hist_count,
                    growth_rate_pct=growth_rate_pct,
                    velocity_score=velocity_score,
                    cagr_pct=cagr_val,
                    cagr_status=cagr_stat,
                    growth_trajectory=trajectory,
                )
            )

        # Sort by velocity and recent filings descending
        growth_items.sort(key=lambda x: (x.velocity_score, x.recent_period_filings), reverse=True)

        return TechnologyGrowthResponse(
            items=growth_items,
            total_growing_areas=sum(1 for g in growth_items if g.growth_trajectory in ("RAPID_ACCELERATION", "STEADY_GROWTH")),
            summary_by_trajectory=summary_by_trajectory,
            timeframe_analyzed={"start_year": start_year, "end_year": end_year},
        )

    @classmethod
    async def get_technology_coverage(
        cls,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        domain: Optional[str] = None,
        profile_id: Optional[int] = None,
        db: AsyncSession = None,
    ) -> TechnologyCoverageResponse:
        """
        Calculates multi-dimensional coverage density across patents, assignees, jurisdictions, and classifications.
        """
        activity_resp = await cls.get_technology_activity(
            start_year=start_year, end_year=end_year, domain=domain, profile_id=profile_id, db=db
        )

        coverage_items: List[TechnologyCoverageItem] = []
        summary_by_level = {"HIGH_COVERAGE": 0, "MODERATE_COVERAGE": 0, "SPARSE_COVERAGE": 0}

        for act in activity_resp.items:
            vol_score = min(100.0, act.patent_count * 10.0)
            ass_score = min(100.0, act.assignee_count * 20.0)
            jur_score = min(100.0, len(act.jurisdictions) * 25.0)
            cls_count = 1 if act.classification_code else 0
            cls_score = min(100.0, cls_count * 50.0)

            density_score = round(
                (0.35 * vol_score) + (0.30 * ass_score) + (0.20 * jur_score) + (0.15 * cls_score),
                2,
            )

            if density_score >= 65.0:
                cov_level = "HIGH_COVERAGE"
            elif density_score >= 35.0:
                cov_level = "MODERATE_COVERAGE"
            else:
                cov_level = "SPARSE_COVERAGE"

            summary_by_level[cov_level] += 1

            coverage_items.append(
                TechnologyCoverageItem(
                    technology_area=act.technology_area,
                    technology_domain=act.technology_domain,
                    patent_count=act.patent_count,
                    assignee_count=act.assignee_count,
                    jurisdiction_count=len(act.jurisdictions),
                    classification_count=cls_count,
                    coverage_density_score=density_score,
                    coverage_level=cov_level,
                )
            )

        coverage_items.sort(key=lambda x: x.coverage_density_score, reverse=True)

        return TechnologyCoverageResponse(
            items=coverage_items,
            total_areas=len(coverage_items),
            summary_by_level=summary_by_level,
        )

    @classmethod
    async def detect_whitespaces(
        cls,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        domain: Optional[str] = None,
        min_activity: Optional[int] = None,
        whitespace_threshold: float = 45.0,
        profile_id: Optional[int] = None,
        db: AsyncSession = None,
    ) -> WhitespaceDiscoveryResponse:
        """
        Deterministic multi-signal whitespace and activity gap detector.
        Evaluates publication momentum (Module 3) vs. patent saturation (Module 5),
        applicant dispersion, filing recency, and jurisdiction breadth.
        """
        # Fetch patent activity and growth profiles
        activity_resp = await cls.get_technology_activity(
            start_year=start_year, end_year=end_year, domain=domain, profile_id=profile_id, db=db
        )
        growth_resp = await cls.get_technology_growth(
            start_year=start_year, end_year=end_year, domain=domain, profile_id=profile_id, db=db
        )
        growth_map = {g.technology_area: g for g in growth_resp.items}

        # Fetch publication counts from Module 3 (Publication)
        pub_stmt = select(
            func.coalesce(Publication.primary_domain, "General / Cross-Disciplinary").label("d_name"),
            func.count(Publication.id).label("pub_count")
        ).group_by("d_name")
        pub_stmt = cls._apply_pub_filters(pub_stmt, start_year, end_year, domain, profile_id)
        pub_rows = (await db.execute(pub_stmt)).all()
        pub_map: Dict[str, int] = {str(r.d_name): int(r.pub_count or 0) for r in pub_rows}

        # Benchmarks
        domain_benchmark = max(1.0, sum(a.patent_count for a in activity_resp.items) / float(len(activity_resp.items))) if activity_resp.items else 5.0
        pub_benchmark = max(1.0, sum(pub_map.values()) / float(max(1, len(pub_map)))) if pub_map else 2.0

        candidates: List[WhitespaceCandidateItem] = []

        # 1. Process domains with patent activity
        for act in activity_resp.items:
            g_item = growth_map.get(act.technology_area)
            velocity = g_item.velocity_score if g_item else 0.0

            if min_activity is not None and act.patent_count < min_activity:
                continue

            pub_count = pub_map.get(act.technology_area, 0)
            if act.patent_count == 0:
                r2p_ratio = None
                patent_note = "No patent records identified for this technology domain."
            else:
                r2p_ratio = round(pub_count / float(act.patent_count), 2)
                patent_note = None

            pub_density = round(min(100.0, (pub_count / float(pub_benchmark)) * 50.0), 2)
            pat_density = round(min(100.0, (act.patent_count / float(domain_benchmark)) * 50.0), 2)

            # Component gap scores
            vol_ratio = act.patent_count / float(domain_benchmark)
            activity_gap = max(0.0, 100.0 - min(100.0, vol_ratio * 100.0))
            assignee_gap = max(0.0, 100.0 - min(100.0, act.assignee_count * 25.0))
            growth_gap = max(0.0, 100.0 - velocity)
            jur_count = len(act.jurisdictions)
            coverage_gap = max(0.0, 100.0 - min(100.0, jur_count * 33.3))

            # Composite Whitespace Score factoring research momentum
            base_score = (0.35 * activity_gap) + (0.25 * assignee_gap) + (0.20 * growth_gap) + (0.20 * coverage_gap)
            if pub_count > 0 and r2p_ratio is not None and r2p_ratio >= 1.0:
                composite_score = round(min(100.0, base_score + (pub_density * 0.15)), 2)
            else:
                composite_score = round(base_score, 2)

            evidence: List[str] = []
            if pub_count > 0:
                evidence.append(f"Research publication base: {pub_count} paper(s) indexed in academic literature.")
                if act.patent_count == 0:
                    evidence.append("No patent records identified for this technology domain.")
                elif r2p_ratio is not None and r2p_ratio >= 1.0:
                    evidence.append(f"Research-to-patent ratio is {r2p_ratio:.1f}x, indicating scientific publication activity outpaces patent disclosures.")
            if act.patent_count == 0:
                evidence.append("No patent records identified for this technology domain (unpatented academic frontier).")
            elif act.patent_count <= 2:
                evidence.append(f"Sparse patent density ({act.patent_count} patent(s)) indexed in this technology field.")
            elif act.patent_count < domain_benchmark:
                diff_pct = round(((domain_benchmark - act.patent_count) / domain_benchmark) * 100.0, 1)
                evidence.append(f"Patent volume ({act.patent_count}) is {diff_pct}% below domain benchmark ({domain_benchmark:.1f} patents).")

            if act.assignee_count <= 1:
                evidence.append(f"High applicant concentration with only {act.assignee_count} distinct assignee organization recorded.")
            if act.recent_patent_count == 0:
                evidence.append("Zero patent filings detected within the recent 24-month window.")
            elif velocity < 30.0:
                evidence.append(f"Low recent filing velocity ({velocity:.1f}%), indicating decelerating IP disclosures.")
            if jur_count <= 1:
                evidence.append(f"Limited geographic coverage restricted to a single jurisdiction ({', '.join(act.jurisdictions) or 'Regional'}).")

            if (pub_count >= 2 and act.patent_count <= 1) or (activity_resp.total_patents >= 8 and len(evidence) >= 3):
                confidence = "HIGH"
            elif activity_resp.total_patents >= 3 and len(evidence) >= 2:
                confidence = "MEDIUM"
            else:
                confidence = "LOW"

            if composite_score >= 70.0:
                ws_type = "POTENTIAL_WHITESPACE"
            elif activity_gap >= 70.0:
                ws_type = "ACTIVITY_GAP"
            elif coverage_gap >= 70.0:
                ws_type = "LOW_COVERAGE_AREA"
            else:
                ws_type = "UNDERREPRESENTED_NICHE"

            adjacent_areas = [
                a.technology_area
                for a in activity_resp.items
                if a.technology_area != act.technology_area and a.activity_level == "HIGH_ACTIVITY"
            ][:3]

            if composite_score >= whitespace_threshold:
                candidates.append(
                    WhitespaceCandidateItem(
                        technology_area=act.technology_area,
                        technology_domain=act.technology_domain,
                        classification_code=act.classification_code,
                        whitespace_type=ws_type,
                        whitespace_score=composite_score,
                        activity_gap_score=round(activity_gap, 2),
                        assignee_gap_score=round(assignee_gap, 2),
                        growth_gap_score=round(growth_gap, 2),
                        coverage_gap_score=round(coverage_gap, 2),
                        publication_count=pub_count,
                        patent_count=act.patent_count,
                        research_to_patent_ratio=r2p_ratio,
                        patent_status_note=patent_note,
                        publication_density_score=pub_density,
                        patent_density_score=pat_density,
                        confidence=confidence,
                        evidence=evidence or ["Low overall patent density relative to peer technology areas."],
                        adjacent_technology_areas=adjacent_areas,
                    )
                )

        # 2. Process publication-only domains (High research, Zero patents = prime whitespace!)
        pat_domains = {a.technology_area.lower() for a in activity_resp.items}
        for p_dom, p_cnt in pub_map.items():
            if p_dom.lower() not in pat_domains:
                if min_activity is not None and min_activity > 0:
                    continue
                pub_density = round(min(100.0, (p_cnt / float(pub_benchmark)) * 75.0), 2)
                composite_score = round(min(100.0, 75.0 + (pub_density * 0.25)), 2)
                r2p = None  # Explicitly null: Never fabricate 1.0x when patent_count == 0
                patent_note = "No patent records identified for this technology domain."
                ev = [
                    f"Active scientific research foundation ({p_cnt} publication(s)) with zero corresponding patent disclosures.",
                    "No patent records identified for this technology domain.",
                    "Potential under-patented research area with significant academic discovery momentum and uncontested IP space.",
                ]
                if composite_score >= whitespace_threshold:
                    candidates.append(
                        WhitespaceCandidateItem(
                            technology_area=p_dom,
                            technology_domain=p_dom,
                            classification_code=None,
                            whitespace_type="POTENTIAL_WHITESPACE",
                            whitespace_score=composite_score,
                            activity_gap_score=100.0,
                            assignee_gap_score=100.0,
                            growth_gap_score=100.0,
                            coverage_gap_score=100.0,
                            publication_count=p_cnt,
                            patent_count=0,
                            research_to_patent_ratio=r2p,
                            patent_status_note=patent_note,
                            publication_density_score=pub_density,
                            patent_density_score=0.0,
                            confidence="HIGH" if p_cnt >= 2 else "MEDIUM",
                            evidence=ev,
                            adjacent_technology_areas=[],
                        )
                    )

        candidates.sort(key=lambda x: x.whitespace_score, reverse=True)

        return WhitespaceDiscoveryResponse(
            candidates=candidates,
            total_candidates=len(candidates),
            domain_filter=domain,
            threshold_used=whitespace_threshold,
        )

    @classmethod
    async def get_technology_maturity(
        cls,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        domain: Optional[str] = None,
        profile_id: Optional[int] = None,
        db: AsyncSession = None,
    ) -> TechnologyMaturityResponse:
        """
        Calculates deterministic technology maturity using the mentor-defined 6-indicator model:
        1. Research Growth (25%)
        2. Patent Growth (25%)
        3. Research Activity (15%)
        4. Patent Activity (15%)
        5. Organization Participation (10%) - Based strictly on registered applicant organizations (assignees)
        6. Technology / Application Diversity (10%)
        Total: 100%
        """
        current_year = datetime.now(timezone.utc).year
        recent_split_year = current_year - 2

        # 1. Collect all distinct domains across Publication and Patent
        pub_stmt = select(distinct(Publication.primary_domain)).where(Publication.primary_domain.is_not(None))
        pub_stmt = cls._apply_pub_filters(pub_stmt, start_year, end_year, domain, profile_id)
        pub_domains = [str(d) for d in (await db.execute(pub_stmt)).scalars().all() if d]

        pat_stmt = select(distinct(Patent.technology_domain)).where(Patent.technology_domain.is_not(None))
        pat_stmt = cls._apply_base_filters(pat_stmt, start_year, end_year, domain, profile_id=profile_id)
        pat_domains = [str(d) for d in (await db.execute(pat_stmt)).scalars().all() if d]

        domain_set = set(pub_domains + pat_domains)
        if domain and domain.strip():
            target_clean = domain.strip().lower()
            all_domains = sorted([d for d in domain_set if d.strip().lower() == target_clean or target_clean in d.strip().lower()])
            if not all_domains:
                all_domains = [domain.strip()]
        else:
            all_domains = sorted(list(domain_set))

        if not all_domains:
            return TechnologyMaturityResponse(
                items=[],
                total_domains_analyzed=0,
                summary_by_stage={"EMERGING": 0, "DEVELOPING": 0, "MATURE": 0, "DECLINING": 0, "INSUFFICIENT_DATA": 0},
            )

        items: List[TechnologyMaturityItem] = []
        summary_by_stage = {"EMERGING": 0, "DEVELOPING": 0, "MATURE": 0, "DECLINING": 0, "INSUFFICIENT_DATA": 0}

        for dom in all_domains:
            # Publications in domain
            p_agg_stmt = select(
                func.count(Publication.id).label("count"),
                func.coalesce(func.avg(Publication.citation_count), 0.0).label("avg_citations"),
                func.count(distinct(Publication.venue)).label("venue_count"),
            ).where(func.lower(Publication.primary_domain) == dom.lower())
            p_agg_stmt = cls._apply_pub_filters(p_agg_stmt, start_year, end_year, None, profile_id)
            p_agg = (await db.execute(p_agg_stmt)).one()
            pub_count = int(p_agg.count or 0)
            avg_pub_citations = round(float(p_agg.avg_citations or 0.0), 2)
            venue_count = int(p_agg.venue_count or 0)

            # Publication years
            p_yr_stmt = select(
                func.extract("year", Publication.publication_date).label("yr"),
                func.count(Publication.id).label("cnt"),
            ).where(
                func.lower(Publication.primary_domain) == dom.lower(),
                Publication.publication_date.is_not(None)
            ).group_by("yr").order_by("yr")
            p_yr_stmt = cls._apply_pub_filters(p_yr_stmt, start_year, end_year, None, profile_id)
            p_yr_rows = (await db.execute(p_yr_stmt)).all()
            pub_years = {int(r.yr): int(r.cnt) for r in p_yr_rows if r.yr is not None}

            # Patents in domain
            grant_case = case(
                (or_(Patent.patent_number.ilike("%B%"), and_(Patent.publication_date.is_not(None), Patent.filing_date.is_not(None))), 1),
                else_=0
            )
            pt_agg_stmt = select(
                func.count(Patent.id).label("count"),
                func.sum(grant_case).label("grant_count"),
                func.coalesce(func.avg(Patent.citation_count), 0.0).label("avg_citations"),
                func.count(distinct(func.lower(func.coalesce(Patent.assignee, "Individual")))).label("assignee_count"),
                func.count(distinct(Patent.patent_classification)).label("classification_count"),
            ).where(func.lower(Patent.technology_domain) == dom.lower())
            pt_agg_stmt = cls._apply_base_filters(pt_agg_stmt, start_year, end_year, None, profile_id=profile_id)
            pt_agg = (await db.execute(pt_agg_stmt)).one()
            pat_count = int(pt_agg.count or 0)
            grant_count = int(pt_agg.grant_count or 0)
            avg_pat_citations = round(float(pt_agg.avg_citations or 0.0), 2)
            assignee_count = int(pt_agg.assignee_count or 0)
            classification_count = int(pt_agg.classification_count or 0)

            # Patent years
            p_yr_col = func.coalesce(func.extract("year", Patent.filing_date), func.extract("year", Patent.publication_date))
            pt_yr_stmt = select(
                p_yr_col.label("yr"),
                func.count(Patent.id).label("cnt"),
            ).where(
                func.lower(Patent.technology_domain) == dom.lower(),
                p_yr_col.is_not(None)
            ).group_by("yr").order_by("yr")
            pt_yr_stmt = cls._apply_base_filters(pt_yr_stmt, start_year, end_year, None, profile_id=profile_id)
            pt_yr_rows = (await db.execute(pt_yr_stmt)).all()
            pat_years = {int(r.yr): int(r.cnt) for r in pt_yr_rows if r.yr is not None}

            # Jurisdictions
            jur_stmt = select(Patent.patent_number).where(func.lower(Patent.technology_domain) == dom.lower())
            jur_stmt = cls._apply_base_filters(jur_stmt, start_year, end_year, None, profile_id=profile_id)
            jur_rows = (await db.execute(jur_stmt)).scalars().all()
            jurisdictions = {cls._extract_jurisdiction_code(p) for p in jur_rows if p}
            jurisdiction_count = len(jurisdictions)

            # Evaluate Longitudinal Depth
            all_active_years = sorted(list(set(pub_years.keys()) | set(pat_years.keys())))
            distinct_active_years = len(all_active_years)

            # Indicator 1: Research Growth (25%)
            recent_pubs = sum(cnt for yr, cnt in pub_years.items() if yr >= recent_split_year)
            hist_pub_years = [y for y in pub_years.keys() if y < recent_split_year]
            hist_pubs = sum(pub_years[y] for y in hist_pub_years)
            if hist_pubs > 0:
                hist_annual = hist_pubs / float(max(1, len(hist_pub_years)))
                recent_annual = recent_pubs / 2.0
                res_growth_pct = round(((recent_annual - hist_annual) / hist_annual) * 100.0, 2)
                res_growth_score = max(0.0, min(100.0, 50.0 + (res_growth_pct * 0.5)))
            elif recent_pubs > 0:
                res_growth_pct = None
                res_growth_score = 75.0
            else:
                res_growth_pct = None
                res_growth_score = 0.0

            if len(pub_years) >= 2:
                s_py = sorted(pub_years.keys())
                res_cagr, _ = cls._calculate_cagr(pub_years[s_py[0]], pub_years[s_py[-1]], s_py[-1] - s_py[0])
            else:
                res_cagr = None

            # Indicator 2: Patent Growth (25%)
            recent_pats = sum(cnt for yr, cnt in pat_years.items() if yr >= recent_split_year)
            hist_pat_years = [y for y in pat_years.keys() if y < recent_split_year]
            hist_pats = sum(pat_years[y] for y in hist_pat_years)
            velocity_score = (recent_pats / float(max(1, pat_count))) * 100.0
            if hist_pats > 0:
                hist_annual = hist_pats / float(max(1, len(hist_pat_years)))
                recent_annual = recent_pats / 2.0
                pat_growth_pct = round(((recent_annual - hist_annual) / hist_annual) * 100.0, 2)
                norm_pat_growth = max(0.0, min(100.0, 50.0 + (pat_growth_pct * 0.5)))
            elif recent_pats > 0:
                pat_growth_pct = None
                norm_pat_growth = 75.0
            else:
                pat_growth_pct = None
                norm_pat_growth = 0.0

            pat_growth_score = round(min(100.0, (0.5 * velocity_score) + (0.5 * norm_pat_growth)), 2)

            if len(pat_years) >= 2:
                s_ty = sorted(pat_years.keys())
                pat_cagr, _ = cls._calculate_cagr(pat_years[s_ty[0]], pat_years[s_ty[-1]], s_ty[-1] - s_ty[0])
            else:
                pat_cagr = None

            # Indicator 3: Research Activity (15%)
            pub_vol = min(100.0, pub_count * 25.0)
            pub_rec = min(100.0, (recent_pubs / float(max(1, pub_count))) * 100.0) if pub_count > 0 else 0.0
            pub_cit = min(100.0, avg_pub_citations * 5.0)
            res_activity_score = round((0.40 * pub_vol) + (0.35 * pub_rec) + (0.25 * pub_cit), 2)

            # Indicator 4: Patent Activity (15%)
            pat_vol = min(100.0, pat_count * 25.0)
            pat_grt = min(100.0, (grant_count / float(max(1, pat_count))) * 100.0) if pat_count > 0 else 0.0
            pat_cit = min(100.0, avg_pat_citations * 5.0)
            pat_activity_score = round((0.40 * pat_vol) + (0.35 * pat_grt) + (0.25 * pat_cit), 2)

            # Indicator 5: Organization Participation (10%)
            # Mentor rule: Based on actual identifiable organizations/institutions (patent assignees).
            # Academic journals/conferences (venues) are excluded from organization count.
            org_score = round(min(100.0, assignee_count * 30.0), 2)

            # Indicator 6: Technology / Application Diversity (10%)
            div_score = round(min(100.0, (classification_count * 30.0) + (jurisdiction_count * 20.0)), 2)

            # Weighted composite score
            maturity_score = round(
                (0.25 * res_growth_score)
                + (0.25 * pat_growth_score)
                + (0.15 * res_activity_score)
                + (0.15 * pat_activity_score)
                + (0.10 * org_score)
                + (0.10 * div_score),
                2,
            )

            # Stage Determination & Insufficient Historical Data Handling
            if pub_count == 0 and pat_count == 0:
                stage = "INSUFFICIENT_DATA"
                growth_status = "INSUFFICIENT_DATA"
            elif distinct_active_years < 2:
                # Principle: Absence of multi-year historical trend != DECLINING.
                # A single historical year cannot establish a CAGR or longitudinal trend.
                stage = "INSUFFICIENT_DATA"
                growth_status = "INSUFFICIENT_DATA"
            else:
                growth_status = "COMPUTED"
                # Strict Mentor Rule: Technology CANNOT be MATURE unless maturity_score >= 60.0
                # AND both research activity and patent activity are solidly established (>= 40.0)
                # AND growth is slower or relatively stable (mentor specification: "growth becoming slower or relatively stable")
                if (
                    maturity_score >= 60.0
                    and res_activity_score >= 40.0
                    and pat_activity_score >= 40.0
                    and (res_growth_score < 70.0 or (res_growth_pct is not None and res_growth_pct <= 35.0))
                ):
                    stage = "MATURE"
                # Declining requires confirmed multi-year contraction across an established historical base
                # (A sparse total of 1-3 records with no recent activity is INSUFFICIENT_DATA, not an established industry decline)
                elif (pub_count + pat_count >= 4 or (hist_pubs + hist_pats >= 4)) and (
                    (
                        (res_growth_pct is not None and res_growth_pct < -20.0)
                        and (pat_growth_pct is not None and pat_growth_pct < -20.0)
                        and res_growth_score < 35.0
                        and pat_growth_score < 35.0
                    )
                    or (recent_pubs == 0 and recent_pats == 0 and (hist_pubs + hist_pats >= 4))
                ):
                    stage = "DECLINING"
                # Emerging requires high growth momentum on early-stage footprint
                elif (res_growth_score >= 50.0 or pat_growth_score >= 50.0 or velocity_score >= 50.0) and (
                    maturity_score < 45.0 or (pub_count + pat_count <= 6)
                ):
                    stage = "EMERGING"
                elif pub_count + pat_count < 4 and recent_pubs == 0 and recent_pats == 0:
                    stage = "INSUFFICIENT_DATA"
                else:
                    stage = "DEVELOPING"

            summary_by_stage[stage] = summary_by_stage.get(stage, 0) + 1

            evidence = [
                f"Research activity: {pub_count} publication(s) ({recent_pubs} recent), avg citations: {avg_pub_citations:.1f}.",
                f"Patent activity: {pat_count} disclosure(s) ({recent_pats} recent, {grant_count} granted), avg citations: {avg_pat_citations:.1f}.",
                f"Organization participation: {assignee_count} distinct assignee applicant organization(s). (Academic venues: {venue_count}, excluded from organization metrics).",
                f"Coverage diversity: {classification_count} patent classification code(s) across {jurisdiction_count} jurisdiction(s).",
                f"Market adoption status: DATA_UNAVAILABLE (R&D momentum precedes market sales).",
            ]
            if distinct_active_years < 2:
                evidence.append(
                    f"Longitudinal depth note: Only {distinct_active_years} historical year(s) indexed ({', '.join(str(y) for y in all_active_years) or 'None'}). Growth status marked INSUFFICIENT_DATA."
                )

            if stage == "INSUFFICIENT_DATA":
                summary_text = (
                    f"{dom} is classified as {stage} (Maturity Score: {maturity_score:.1f}/100). "
                    f"Only {distinct_active_years} historical year(s) of activity are indexed ({', '.join(str(y) for y in all_active_years) or 'None'}), "
                    f"which is insufficient to establish a multi-year growth or decline trajectory. "
                    f"{assignee_count} assignee organization(s) participate. Commercial adoption telemetry remains unindexed."
                )
            else:
                summary_text = (
                    f"{dom} is classified in the {stage} stage (Maturity Score: {maturity_score:.1f}/100). "
                    f"Research Growth is {res_growth_score:.1f}/100 and Patent Growth is {pat_growth_score:.1f}/100 across {distinct_active_years} active years. "
                    f"{assignee_count} assignee organization(s) participate (publication institution affiliations unindexed). "
                    f"Commercial adoption evidence remains unindexed, maintaining strict separation between scientific/IP disclosures and enterprise deployment."
                )

            indicators = MaturityIndicatorBreakdown(
                research_growth_score=res_growth_score,
                patent_growth_score=pat_growth_score,
                research_activity_score=res_activity_score,
                patent_activity_score=pat_activity_score,
                organization_participation_score=org_score,
                technology_diversity_score=div_score,
                research_cagr=res_cagr,
                patent_cagr=pat_cagr,
                growth_status=growth_status,
            )

            items.append(
                TechnologyMaturityItem(
                    technology_domain=dom,
                    maturity_score=maturity_score,
                    stage=stage,
                    publication_count=pub_count,
                    patent_count=pat_count,
                    recent_publication_count=recent_pubs,
                    recent_patent_count=recent_pats,
                    assignee_count=assignee_count,
                    venue_count=venue_count,
                    indicators=indicators,
                    explainability_summary=summary_text,
                    evidence=evidence,
                )
            )

        items.sort(key=lambda x: x.maturity_score, reverse=True)

        return TechnologyMaturityResponse(
            items=items,
            total_domains_analyzed=len(items),
            summary_by_stage=summary_by_stage,
        )

    @classmethod
    async def get_technology_adoption(
        cls,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        domain: Optional[str] = None,
        profile_id: Optional[int] = None,
        db: AsyncSession = None,
    ) -> AdoptionTrackingResponse:
        """
        Tracks technology adoption status, strictly isolating market/enterprise adoption
        from research publication and patent activity.
        """
        mat_resp = await cls.get_technology_maturity(
            start_year=start_year, end_year=end_year, domain=domain, profile_id=profile_id, db=db
        )
        items: List[AdoptionTrackingItem] = []
        for m in mat_resp.items:
            res_lvl = "HIGH" if m.publication_count >= 3 else "MODERATE" if m.publication_count >= 1 else "LOW"
            pat_lvl = "HIGH" if m.patent_count >= 3 else "MODERATE" if m.patent_count >= 1 else "LOW"
            items.append(
                AdoptionTrackingItem(
                    technology_domain=m.technology_domain,
                    adoption_status="DATA_UNAVAILABLE",
                    adoption_score=None,
                    commercial_evidence_available=False,
                    research_activity_level=res_lvl,
                    patent_activity_level=pat_lvl,
                    disclaimer="Technology adoption tracking is strictly separate from scientific publication and patent activity. R&D disclosures precede commercial adoption and do not guarantee market penetration.",
                    notes="No verified enterprise sales or commercial telemetry records indexed in local database for this domain. Adoption status marked DATA_UNAVAILABLE.",
                )
            )
        return AdoptionTrackingResponse(
            items=items,
            total_domains=len(items),
        )

    @classmethod
    async def get_emerging_technologies(
        cls,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        domain: Optional[str] = None,
        profile_id: Optional[int] = None,
        db: AsyncSession = None,
    ) -> EmergingTechnologyResponse:
        """
        Identifies and ranks emerging technology candidates using multi-signal momentum:
        recent filing acceleration, research velocity, and organizational expansion.
        """
        mat_resp = await cls.get_technology_maturity(
            start_year=start_year, end_year=end_year, domain=domain, profile_id=profile_id, db=db
        )
        candidates: List[EmergingTechnologyItem] = []
        for m in mat_resp.items:
            vel = (m.recent_patent_count / float(max(1, m.patent_count))) * 100.0 if m.patent_count > 0 else 50.0
            res_growth = m.indicators.research_growth_score
            saturation_penalty = min(50.0, (m.publication_count + m.patent_count) * 4.0)

            emerge_score = round(
                max(0.0, min(100.0, (0.35 * vel) + (0.35 * res_growth) + (0.20 * m.indicators.organization_participation_score) + (0.10 * (100.0 - saturation_penalty)))),
                2,
            )

            signals = []
            if vel >= 50.0:
                signals.append(f"High patent filing velocity ({vel:.1f}% recently filed).")
            if res_growth >= 60.0:
                signals.append(f"Strong research publication expansion ({res_growth:.1f}/100 growth score).")
            if m.assignee_count >= 1:
                signals.append(f"{m.assignee_count} active applicant organization(s) entering domain.")
            if m.stage == "EMERGING":
                signals.append("Classified in early emergence stage with low cumulative saturation.")

            candidates.append(
                EmergingTechnologyItem(
                    technology_domain=m.technology_domain,
                    emerging_score=emerge_score,
                    growth_trajectory="RAPID_ACCELERATION" if emerge_score >= 65.0 else "STEADY_GROWTH" if emerge_score >= 45.0 else "EMERGING_SPARSE",
                    research_growth_pct=m.indicators.research_cagr,
                    patent_velocity_score=round(vel, 2),
                    publication_count=m.publication_count,
                    patent_count=m.patent_count,
                    organization_count=m.assignee_count + m.venue_count,
                    key_signals=signals or ["Early stage technology exploration detected."],
                    rationale=f"{m.technology_domain} exhibits emergence score of {emerge_score:.1f}/100 driven by recent publication momentum and IP disclosures.",
                )
            )
        candidates.sort(key=lambda x: x.emerging_score, reverse=True)
        return EmergingTechnologyResponse(
            candidates=candidates,
            total_candidates=len(candidates),
        )

    @classmethod
    async def get_competitive_technology_monitoring(
        cls,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        domain: Optional[str] = None,
        profile_id: Optional[int] = None,
        db: AsyncSession = None,
    ) -> CompetitiveTechnologyResponse:
        """
        Monitors competitor concentration, top applicants, and jurisdiction breadth per domain.
        Reuses Module 5 patent intelligence metrics.
        """
        mat_resp = await cls.get_technology_maturity(
            start_year=start_year, end_year=end_year, domain=domain, profile_id=profile_id, db=db
        )
        items: List[CompetitiveTechnologyItem] = []
        for m in mat_resp.items:
            # Query assignees for this domain
            p_stmt = select(
                func.coalesce(Patent.assignee, "Individual / Unassigned").label("ass_name"),
                func.count(Patent.id).label("cnt"),
                func.coalesce(func.sum(Patent.citation_count), 0).label("cites"),
            ).where(func.lower(Patent.technology_domain) == m.technology_domain.lower())
            p_stmt = cls._apply_base_filters(p_stmt, start_year, end_year, None, profile_id=profile_id)
            p_stmt = p_stmt.group_by("ass_name").order_by(desc("cnt"))
            p_rows = (await db.execute(p_stmt)).all()

            total_domain_pats = sum(int(r.cnt) for r in p_rows) or 1
            top_assignees = []
            hhi = 0.0
            for r in p_rows[:5]:
                cnt = int(r.cnt)
                share = (cnt / float(total_domain_pats)) * 100.0
                hhi += (share ** 2)
                top_assignees.append({
                    "assignee": str(r.ass_name),
                    "patent_count": cnt,
                    "share_pct": round(share, 2),
                    "citations": int(r.cites or 0),
                })
            for r in p_rows[5:]:
                share = (int(r.cnt) / float(total_domain_pats)) * 100.0
                hhi += (share ** 2)

            hhi = round(hhi, 2)
            if hhi < 1500.0:
                tier = "UNCONCENTRATED"
            elif hhi <= 2500.0:
                tier = "MODERATELY_CONCENTRATED"
            else:
                tier = "HIGHLY_CONCENTRATED"

            vol_score = min(100.0, total_domain_pats * 20.0)
            ass_score = min(100.0, len(p_rows) * 25.0)
            comp_idx = round((0.60 * vol_score) + (0.40 * ass_score), 2)

            jur_stmt = select(Patent.patent_number).where(func.lower(Patent.technology_domain) == m.technology_domain.lower())
            jur_stmt = cls._apply_base_filters(jur_stmt, start_year, end_year, None, profile_id=profile_id)
            jur_rows = (await db.execute(jur_stmt)).scalars().all()
            jurisdictions = sorted(list({cls._extract_jurisdiction_code(p) for p in jur_rows if p}))

            items.append(
                CompetitiveTechnologyItem(
                    technology_domain=m.technology_domain,
                    assignee_count=len(p_rows),
                    top_assignees=top_assignees,
                    assignee_concentration_hhi=hhi,
                    concentration_tier=tier,
                    composite_competitive_index=comp_idx,
                    dominant_jurisdictions=jurisdictions,
                )
            )
        items.sort(key=lambda x: x.composite_competitive_index, reverse=True)
        return CompetitiveTechnologyResponse(
            items=items,
            total_domains=len(items),
        )

    @classmethod
    async def get_summary(
        cls,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        domain: Optional[str] = None,
        profile_id: Optional[int] = None,
        db: AsyncSession = None,
    ) -> TechnologyIntelligenceSummary:
        """
        Aggregates activity, growth, whitespace, maturity, and emergence highlights into an executive summary.
        """
        act_resp = await cls.get_technology_activity(
            start_year=start_year, end_year=end_year, domain=domain, profile_id=profile_id, db=db
        )
        growth_resp = await cls.get_technology_growth(
            start_year=start_year, end_year=end_year, domain=domain, profile_id=profile_id, db=db
        )
        ws_resp = await cls.detect_whitespaces(
            start_year=start_year, end_year=end_year, domain=domain, profile_id=profile_id, db=db
        )
        mat_resp = await cls.get_technology_maturity(
            start_year=start_year, end_year=end_year, domain=domain, profile_id=profile_id, db=db
        )
        emerge_resp = await cls.get_emerging_technologies(
            start_year=start_year, end_year=end_year, domain=domain, profile_id=profile_id, db=db
        )

        return TechnologyIntelligenceSummary(
            total_patents=act_resp.total_patents,
            total_technology_areas=act_resp.total_technology_areas,
            active_areas_count=act_resp.summary_by_level.get("HIGH_ACTIVITY", 0) + act_resp.summary_by_level.get("MEDIUM_ACTIVITY", 0),
            growing_areas_count=growth_resp.total_growing_areas,
            potential_whitespaces_count=ws_resp.total_candidates,
            top_active_areas=act_resp.items[:5],
            top_growing_areas=growth_resp.items[:5],
            top_whitespace_candidates=ws_resp.candidates[:5],
            top_maturing_areas=mat_resp.items[:5],
            top_emerging_candidates=emerge_resp.candidates[:5],
        )
