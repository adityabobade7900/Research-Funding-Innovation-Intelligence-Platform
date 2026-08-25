import re
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import select, func, desc, and_, or_, distinct, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patent import Patent, profile_patents
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

            summary_by_trajectory[trajectory] += 1

            growth_items.append(
                TechnologyGrowthItem(
                    technology_area=d_name,
                    technology_domain=d_name,
                    recent_period_filings=recent_count,
                    historical_period_filings=hist_count,
                    growth_rate_pct=growth_rate_pct,
                    velocity_score=velocity_score,
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
        Evaluates patent volume, applicant dispersion, filing recency, and jurisdiction breadth.
        """
        # Fetch activity and growth profiles
        activity_resp = await cls.get_technology_activity(
            start_year=start_year, end_year=end_year, domain=domain, profile_id=profile_id, db=db
        )
        growth_resp = await cls.get_technology_growth(
            start_year=start_year, end_year=end_year, domain=domain, profile_id=profile_id, db=db
        )

        growth_map = {g.technology_area: g for g in growth_resp.items}

        # Calculate benchmark average patent count across active domains
        if activity_resp.items:
            domain_benchmark = max(1.0, sum(a.patent_count for a in activity_resp.items) / float(len(activity_resp.items)))
        else:
            domain_benchmark = 5.0

        candidates: List[WhitespaceCandidateItem] = []

        for act in activity_resp.items:
            g_item = growth_map.get(act.technology_area)
            velocity = g_item.velocity_score if g_item else 0.0

            # Filter by min_activity if requested
            if min_activity is not None and act.patent_count < min_activity:
                continue

            # 1. Activity Gap Score (Lower patents relative to benchmark -> higher gap)
            vol_ratio = act.patent_count / float(domain_benchmark)
            activity_gap = max(0.0, 100.0 - min(100.0, vol_ratio * 100.0))

            # 2. Assignee Gap Score (Fewer assignees -> higher concentration/gap)
            assignee_gap = max(0.0, 100.0 - min(100.0, act.assignee_count * 25.0))

            # 3. Growth / Recency Gap Score (Low recent velocity -> higher inactivity gap)
            growth_gap = max(0.0, 100.0 - velocity)

            # 4. Coverage Gap Score (Low jurisdiction diversity -> higher geographic gap)
            jur_count = len(act.jurisdictions)
            coverage_gap = max(0.0, 100.0 - min(100.0, jur_count * 33.3))

            # Composite Whitespace Score (0.0 to 100.0)
            composite_score = round(
                (0.35 * activity_gap) + (0.25 * assignee_gap) + (0.20 * growth_gap) + (0.20 * coverage_gap),
                2,
            )

            # Evidence collection
            evidence: List[str] = []
            if act.patent_count <= 2:
                evidence.append(f"Sparse patent density ({act.patent_count} patent(s)) indexed in this technology field.")
            elif act.patent_count < domain_benchmark:
                diff_pct = round(((domain_benchmark - act.patent_count) / domain_benchmark) * 100.0, 1)
                evidence.append(f"Patent volume ({act.patent_count}) is {diff_pct}% below the active domain benchmark ({domain_benchmark:.1f} patents).")

            if act.assignee_count <= 1:
                evidence.append(f"High applicant concentration with only {act.assignee_count} distinct assignee organization recorded.")
            elif act.assignee_count <= 2:
                evidence.append(f"Limited commercial breadth with only {act.assignee_count} active applicants.")

            if act.recent_patent_count == 0:
                evidence.append("Zero patent filings detected within the recent 24-month window.")
            elif velocity < 30.0:
                evidence.append(f"Low recent filing velocity ({velocity:.1f}%), indicating decelerating IP disclosures.")

            if jur_count <= 1:
                evidence.append(f"Limited geographic coverage restricted to a single jurisdiction ({', '.join(act.jurisdictions) or 'Regional'}).")

            if act.average_citations <= 2.0:
                evidence.append(f"Low citation visibility (average {act.average_citations:.1f} citations per patent).")

            # Determine confidence
            if activity_resp.total_patents >= 8 and len(evidence) >= 3:
                confidence = "HIGH"
            elif activity_resp.total_patents >= 3 and len(evidence) >= 2:
                confidence = "MEDIUM"
            else:
                confidence = "LOW"

            # Determine whitespace type
            if composite_score >= 70.0:
                ws_type = "POTENTIAL_WHITESPACE"
            elif activity_gap >= 70.0:
                ws_type = "ACTIVITY_GAP"
            elif coverage_gap >= 70.0:
                ws_type = "LOW_COVERAGE_AREA"
            else:
                ws_type = "UNDERREPRESENTED_NICHE"

            # Adjacent technology areas for context
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
                        confidence=confidence,
                        evidence=evidence or ["Low overall patent density relative to peer technology areas."],
                        adjacent_technology_areas=adjacent_areas,
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
    async def get_summary(
        cls,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        domain: Optional[str] = None,
        profile_id: Optional[int] = None,
        db: AsyncSession = None,
    ) -> TechnologyIntelligenceSummary:
        """
        Aggregates activity, growth, and whitespace highlights into an executive summary.
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

        return TechnologyIntelligenceSummary(
            total_patents=act_resp.total_patents,
            total_technology_areas=act_resp.total_technology_areas,
            active_areas_count=act_resp.summary_by_level.get("HIGH_ACTIVITY", 0) + act_resp.summary_by_level.get("MEDIUM_ACTIVITY", 0),
            growing_areas_count=growth_resp.total_growing_areas,
            potential_whitespaces_count=ws_resp.total_candidates,
            top_active_areas=act_resp.items[:5],
            top_growing_areas=growth_resp.items[:5],
            top_whitespace_candidates=ws_resp.candidates[:5],
        )
