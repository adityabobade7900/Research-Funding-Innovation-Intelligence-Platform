import re
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import select, func, desc, and_, or_, distinct, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patent import Patent, profile_patents
from app.schemas.patent_intelligence import (
    PatentTrendPoint,
    PatentTrendsResponse,
    TechnologyDomainItem,
    TechnologyDomainsResponse,
    AssigneeLandscapeItem,
    AssigneesResponse,
    JurisdictionItem,
    JurisdictionsResponse,
    PatentStatusItem,
    PatentStatusResponse,
    CompetitiveAssigneeItem,
    CompetitiveLandscapeResponse,
    PatentLandscapeSummary,
    InnovationMapMatrixCell,
    InnovationMapHotspot,
    InnovationMapWhitespace,
    InnovationMapResponse,
    PatentRecommendationItem,
    PatentRecommendationsResponse,
)

JURISDICTION_NAMES = {
    "US": "United States Patent and Trademark Office (USPTO)",
    "EP": "European Patent Office (EPO)",
    "WO": "World Intellectual Property Organization (WIPO/PCT)",
    "CN": "China National Intellectual Property Administration (CNIPA)",
    "JP": "Japan Patent Office (JPO)",
    "GB": "UK Intellectual Property Office (UKIPO)",
    "DE": "German Patent and Trade Mark Office (DPMA)",
    "KR": "Korean Intellectual Property Office (KIPO)",
    "IN": "Indian Patent Office (IPO)",
    "CA": "Canadian Intellectual Property Office (CIPO)",
    "FR": "National Institute of Industrial Property (INPI France)",
    "AU": "IP Australia",
}


class PatentLandscapeService:

    @staticmethod
    def _extract_jurisdiction_code(patent_number: Optional[str]) -> str:
        if not patent_number:
            return "GLOBAL"
        match = re.match(r"^([A-Za-z]{2})", patent_number.strip())
        if match:
            return match.group(1).upper()
        return "US"

    @staticmethod
    def _apply_base_filters(
        query,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        domain: Optional[str] = None,
        assignee: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        profile_id: Optional[int] = None,
    ):
        if profile_id is not None:
            query = query.join(profile_patents, Patent.id == profile_patents.c.patent_id).filter(
                profile_patents.c.profile_id == profile_id
            )

        if start_year is not None:
            query = query.filter(
                or_(
                    func.extract("year", Patent.filing_date) >= start_year,
                    func.extract("year", Patent.publication_date) >= start_year,
                )
            )

        if end_year is not None:
            query = query.filter(
                or_(
                    func.extract("year", Patent.filing_date) <= end_year,
                    func.extract("year", Patent.publication_date) <= end_year,
                )
            )

        if domain:
            query = query.filter(Patent.technology_domain.ilike(f"%{domain}%"))

        if assignee:
            query = query.filter(Patent.assignee.ilike(f"%{assignee}%"))

        if jurisdiction:
            code = jurisdiction.strip().upper()
            query = query.filter(Patent.patent_number.ilike(f"{code}%"))

        return query

    @classmethod
    async def get_trends(
        cls,
        db: AsyncSession,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        domain: Optional[str] = None,
        assignee: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        profile_id: Optional[int] = None,
    ) -> PatentTrendsResponse:
        # 1. Total patent count in scope
        count_q = select(func.count(Patent.id))
        count_q = cls._apply_base_filters(count_q, start_year, end_year, domain, assignee, jurisdiction, profile_id)
        total_patents = (await db.execute(count_q)).scalar() or 0

        # 2. Filings by year
        filing_q = select(
            func.extract("year", Patent.filing_date).label("year"),
            func.count(Patent.id).label("count"),
        ).filter(Patent.filing_date.isnot(None))
        filing_q = cls._apply_base_filters(filing_q, start_year, end_year, domain, assignee, jurisdiction, profile_id)
        filing_q = filing_q.group_by("year").order_by("year")
        filing_res = await db.execute(filing_q)
        filings_by_year = {int(r.year): int(r.count) for r in filing_res.all() if r.year is not None}

        # 3. Grants / Publications by year
        pub_q = select(
            func.extract("year", Patent.publication_date).label("year"),
            func.count(Patent.id).label("count"),
        ).filter(Patent.publication_date.isnot(None))
        pub_q = cls._apply_base_filters(pub_q, start_year, end_year, domain, assignee, jurisdiction, profile_id)
        pub_q = pub_q.group_by("year").order_by("year")
        pub_res = await db.execute(pub_q)
        grants_by_year = {int(r.year): int(r.count) for r in pub_res.all() if r.year is not None}

        all_years = sorted(list(set(filings_by_year.keys()).union(set(grants_by_year.keys()))))

        points: List[PatentTrendPoint] = []
        prev_filing_count: Optional[int] = None

        for yr in all_years:
            f_count = filings_by_year.get(yr, 0)
            g_count = grants_by_year.get(yr, 0)

            growth_rate: Optional[float] = None
            if prev_filing_count is not None and prev_filing_count > 0:
                growth_rate = round(((f_count - prev_filing_count) / prev_filing_count) * 100.0, 2)

            prev_filing_count = f_count

            points.append(
                PatentTrendPoint(
                    year=yr,
                    filings_count=f_count,
                    grants_count=g_count,
                    filing_growth_rate=growth_rate,
                )
            )

        year_range = {
            "min_year": min(all_years) if all_years else None,
            "max_year": max(all_years) if all_years else None,
        }

        return PatentTrendsResponse(
            total_patents=total_patents,
            year_range=year_range,
            points=points,
        )

    @classmethod
    async def get_technology_domains(
        cls,
        db: AsyncSession,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        domain: Optional[str] = None,
        assignee: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        min_count: int = 1,
        limit: int = 20,
        profile_id: Optional[int] = None,
    ) -> TechnologyDomainsResponse:
        # Base query for domain stats
        q = select(
            func.coalesce(Patent.technology_domain, "Unclassified").label("domain"),
            func.count(Patent.id).label("count"),
            func.sum(Patent.citation_count).label("total_citations"),
            func.avg(Patent.citation_count).label("avg_citations"),
        )
        q = cls._apply_base_filters(q, start_year, end_year, domain, assignee, jurisdiction, profile_id)
        q = q.group_by("domain").having(func.count(Patent.id) >= min_count).order_by(desc("count")).limit(limit)

        rows = (await db.execute(q)).all()

        total_q = select(func.count(Patent.id))
        total_q = cls._apply_base_filters(total_q, start_year, end_year, domain, assignee, jurisdiction, profile_id)
        total_corpus = (await db.execute(total_q)).scalar() or 0

        domains_list: List[TechnologyDomainItem] = []
        hhi_sum = 0.0

        for r in rows:
            p_count = int(r.count)
            share_pct = round((p_count / total_corpus * 100.0), 2) if total_corpus > 0 else 0.0
            hhi_sum += share_pct ** 2
            tot_cit = int(r.total_citations or 0)
            avg_cit = round(float(r.avg_citations or 0.0), 2)

            # Query top assignees in this domain
            top_ass_q = select(
                Patent.assignee,
                func.count(Patent.id).label("ass_count")
            ).filter(
                Patent.technology_domain == r.domain,
                Patent.assignee.isnot(None),
                Patent.assignee != ""
            )
            top_ass_q = cls._apply_base_filters(top_ass_q, start_year, end_year, None, assignee, jurisdiction, profile_id)
            top_ass_q = top_ass_q.group_by(Patent.assignee).order_by(desc("ass_count")).limit(3)
            top_ass_rows = (await db.execute(top_ass_q)).all()
            top_assignees = [ar.assignee for ar in top_ass_rows if ar.assignee]

            domains_list.append(
                TechnologyDomainItem(
                    domain=r.domain,
                    patent_count=p_count,
                    share_percentage=share_pct,
                    total_citations=tot_cit,
                    average_citations=avg_cit,
                    top_assignees=top_assignees,
                )
            )

        hhi_score = round(hhi_sum, 2)
        if hhi_score < 1500.0:
            concentration_level = "DIVERSIFIED"
        elif hhi_score <= 2500.0:
            concentration_level = "MODERATELY_CONCENTRATED"
        else:
            concentration_level = "HIGHLY_CONCENTRATED"

        return TechnologyDomainsResponse(
            total_domains=len(domains_list),
            concentration_index_hhi=hhi_score,
            concentration_level=concentration_level,
            domains=domains_list,
        )

    @classmethod
    async def get_assignees(
        cls,
        db: AsyncSession,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        domain: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        min_count: int = 1,
        limit: int = 20,
        profile_id: Optional[int] = None,
    ) -> AssigneesResponse:
        current_year = datetime.now(timezone.utc).year
        recent_threshold_year = current_year - 2

        q = select(
            func.coalesce(Patent.assignee, "Individual / Unassigned").label("assignee_name"),
            func.count(Patent.id).label("count"),
            func.sum(Patent.citation_count).label("total_citations"),
            func.avg(Patent.citation_count).label("avg_citations"),
            func.sum(
                case(
                    (func.extract("year", Patent.filing_date) >= recent_threshold_year, 1),
                    else_=0
                )
            ).label("recent_count")
        )
        q = cls._apply_base_filters(q, start_year, end_year, domain, None, jurisdiction, profile_id)
        q = q.group_by("assignee_name").having(func.count(Patent.id) >= min_count).order_by(desc("count")).limit(limit)

        rows = (await db.execute(q)).all()

        total_q = select(func.count(Patent.id))
        total_q = cls._apply_base_filters(total_q, start_year, end_year, domain, None, jurisdiction, profile_id)
        total_corpus = (await db.execute(total_q)).scalar() or 0

        assignees_list: List[AssigneeLandscapeItem] = []
        hhi_sum = 0.0

        for r in rows:
            p_count = int(r.count)
            share_pct = round((p_count / total_corpus * 100.0), 2) if total_corpus > 0 else 0.0
            hhi_sum += share_pct ** 2
            tot_cit = int(r.total_citations or 0)
            avg_cit = round(float(r.avg_citations or 0.0), 2)
            recent_cnt = int(r.recent_count or 0)

            # Query primary domains for this assignee
            dom_q = select(
                Patent.technology_domain,
                func.count(Patent.id).label("d_cnt")
            ).filter(
                Patent.assignee == r.assignee_name,
                Patent.technology_domain.isnot(None),
                Patent.technology_domain != ""
            )
            dom_q = cls._apply_base_filters(dom_q, start_year, end_year, domain, None, jurisdiction, profile_id)
            dom_q = dom_q.group_by(Patent.technology_domain).order_by(desc("d_cnt")).limit(3)
            dom_rows = (await db.execute(dom_q)).all()
            primary_domains = [dr.technology_domain for dr in dom_rows if dr.technology_domain]

            # Query jurisdictions for this assignee
            num_q = select(Patent.patent_number).filter(Patent.assignee == r.assignee_name)
            num_q = cls._apply_base_filters(num_q, start_year, end_year, domain, None, jurisdiction, profile_id)
            num_rows = (await db.execute(num_q)).scalars().all()
            jurisdictions = sorted(list(set(cls._extract_jurisdiction_code(p_num) for p_num in num_rows)))

            assignees_list.append(
                AssigneeLandscapeItem(
                    assignee=r.assignee_name,
                    patent_count=p_count,
                    share_percentage=share_pct,
                    total_citations=tot_cit,
                    average_citations=avg_cit,
                    recent_filings_count=recent_cnt,
                    primary_domains=primary_domains,
                    jurisdictions=jurisdictions,
                )
            )

        hhi_score = round(hhi_sum, 2)
        if hhi_score < 1500.0:
            concentration_level = "DIVERSIFIED"
        elif hhi_score <= 2500.0:
            concentration_level = "MODERATELY_CONCENTRATED"
        else:
            concentration_level = "HIGHLY_CONCENTRATED"

        return AssigneesResponse(
            total_assignees=len(assignees_list),
            assignee_concentration_hhi=hhi_score,
            concentration_level=concentration_level,
            assignees=assignees_list,
        )

    @classmethod
    async def get_jurisdictions(
        cls,
        db: AsyncSession,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        domain: Optional[str] = None,
        assignee: Optional[str] = None,
        profile_id: Optional[int] = None,
    ) -> JurisdictionsResponse:
        # Load patent numbers in scope to parse ISO country / authority prefix
        q = select(Patent.patent_number)
        q = cls._apply_base_filters(q, start_year, end_year, domain, assignee, None, profile_id)
        patent_numbers = (await db.execute(q)).scalars().all()

        total_patents = len(patent_numbers)
        counts_by_jur: Dict[str, int] = {}

        for num in patent_numbers:
            code = cls._extract_jurisdiction_code(num)
            counts_by_jur[code] = counts_by_jur.get(code, 0) + 1

        jurisdictions_list: List[JurisdictionItem] = []
        for code, count in sorted(counts_by_jur.items(), key=lambda x: x[1], reverse=True):
            share_pct = round((count / total_patents * 100.0), 2) if total_patents > 0 else 0.0
            jurisdictions_list.append(
                JurisdictionItem(
                    jurisdiction_code=code,
                    jurisdiction_name=JURISDICTION_NAMES.get(code, f"{code} Patent Authority"),
                    patent_count=count,
                    share_percentage=share_pct,
                )
            )

        return JurisdictionsResponse(
            total_jurisdictions=len(jurisdictions_list),
            jurisdictions=jurisdictions_list,
        )

    @classmethod
    async def get_status_distribution(
        cls,
        db: AsyncSession,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        domain: Optional[str] = None,
        assignee: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        profile_id: Optional[int] = None,
    ) -> PatentStatusResponse:
        q = select(Patent.patent_number, Patent.publication_date, Patent.filing_date)
        q = cls._apply_base_filters(q, start_year, end_year, domain, assignee, jurisdiction, profile_id)
        patents = (await db.execute(q)).all()

        total_patents = len(patents)
        status_counts = {"GRANTED": 0, "PENDING_APPLICATION": 0, "PUBLISHED": 0}

        for p in patents:
            num = p.patent_number.upper() if p.patent_number else ""
            if num.endswith(("B", "B1", "B2", "B3")):
                status_counts["GRANTED"] += 1
            elif num.endswith(("A", "A1", "A2", "A3")):
                status_counts["PENDING_APPLICATION"] += 1
            elif p.publication_date is not None:
                status_counts["GRANTED"] += 1
            else:
                status_counts["PUBLISHED"] += 1

        items: List[PatentStatusItem] = []
        for st_name, count in status_counts.items():
            share_pct = round((count / total_patents * 100.0), 2) if total_patents > 0 else 0.0
            items.append(
                PatentStatusItem(
                    status=st_name,
                    count=count,
                    share_percentage=share_pct,
                )
            )

        return PatentStatusResponse(
            total_patents=total_patents,
            statuses=items,
        )

    @classmethod
    async def get_competitive_landscape(
        cls,
        db: AsyncSession,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        domain: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        limit: int = 15,
        profile_id: Optional[int] = None,
    ) -> CompetitiveLandscapeResponse:
        # Load assignees response
        assignees_resp = await cls.get_assignees(
            db=db,
            start_year=start_year,
            end_year=end_year,
            domain=domain,
            jurisdiction=jurisdiction,
            min_count=1,
            limit=limit,
            profile_id=profile_id,
        )

        competitors: List[CompetitiveAssigneeItem] = []

        for ass in assignees_resp.assignees:
            p_count = ass.patent_count
            recent_cnt = ass.recent_filings_count
            velocity_pct = round((recent_cnt / p_count * 100.0), 2) if p_count > 0 else 0.0
            breadth_cnt = len(ass.primary_domains)
            avg_cit = ass.average_citations

            # Deterministic Competitive Indicator Formula
            # 1. Volume Score (0 - 100) -> 10 patents = 100
            volume_score = min(100.0, p_count * 10.0)
            # 2. Velocity Score (0 - 100) -> 100% recent filings = 100
            velocity_score = min(100.0, velocity_pct)
            # 3. Citation Score (0 - 100) -> 20 avg citations = 100
            citation_score = min(100.0, avg_cit * 5.0)
            # 4. Breadth Score (0 - 100) -> 4 distinct domains = 100
            breadth_score = min(100.0, max(1, breadth_cnt) * 25.0)

            # Composite Competitive Index (0 - 100)
            comp_index = round(
                (0.40 * volume_score) +
                (0.30 * velocity_score) +
                (0.20 * citation_score) +
                (0.10 * breadth_score),
                2
            )

            # Determine classification
            if comp_index >= 70.0 or p_count >= 8:
                classification = "DOMINANT_PORTFOLIO"
            elif velocity_pct >= 50.0 and p_count >= 2:
                classification = "HIGH_VELOCITY"
            elif breadth_cnt <= 1 and avg_cit >= 8.0:
                classification = "NICHE_SPECIALIST"
            else:
                classification = "EMERGING_APPLICANT"

            key_drivers = []
            if volume_score >= 60.0:
                key_drivers.append(f"Substantial Portfolio ({p_count} patents)")
            if velocity_pct >= 40.0:
                key_drivers.append(f"High Active Filing Rate ({velocity_pct}% recent)")
            if avg_cit >= 5.0:
                key_drivers.append(f"Strong Citation Impact ({avg_cit} avg)")
            if breadth_cnt > 1:
                key_drivers.append(f"Multi-Domain Coverage ({breadth_cnt} domains)")
            if not key_drivers:
                key_drivers.append("Foundational Intellectual Property")

            competitors.append(
                CompetitiveAssigneeItem(
                    assignee=ass.assignee,
                    patent_count=p_count,
                    domain_breadth_count=breadth_cnt,
                    recent_filing_velocity_pct=velocity_pct,
                    average_citations=avg_cit,
                    competitive_index=comp_index,
                    classification=classification,
                    primary_domains=ass.primary_domains,
                    key_drivers=key_drivers,
                )
            )

        # Sort competitors by competitive index descending
        competitors.sort(key=lambda x: x.competitive_index, reverse=True)

        return CompetitiveLandscapeResponse(
            total_competitors=len(competitors),
            assignee_concentration_hhi=assignees_resp.assignee_concentration_hhi,
            concentration_level=assignees_resp.concentration_level,
            weighting_schema={"volume": 0.40, "velocity": 0.30, "citations": 0.20, "domain_breadth": 0.10},
            competitors=competitors,
        )

    @classmethod
    async def get_landscape_summary(
        cls,
        db: AsyncSession,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        domain: Optional[str] = None,
        assignee: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        profile_id: Optional[int] = None,
    ) -> PatentLandscapeSummary:
        # 1. Total summary stats
        stat_q = select(
            func.count(Patent.id).label("total_patents"),
            func.count(distinct(Patent.assignee)).label("total_assignees"),
            func.count(distinct(Patent.technology_domain)).label("total_domains"),
            func.sum(Patent.citation_count).label("total_citations"),
            func.avg(Patent.citation_count).label("avg_citations"),
            func.min(func.extract("year", Patent.filing_date)).label("min_year"),
            func.max(func.extract("year", Patent.filing_date)).label("max_year"),
        )
        stat_q = cls._apply_base_filters(stat_q, start_year, end_year, domain, assignee, jurisdiction, profile_id)
        stat_res = (await db.execute(stat_q)).first()

        tot_p = int(stat_res.total_patents or 0) if stat_res else 0
        tot_ass = int(stat_res.total_assignees or 0) if stat_res else 0
        tot_dom = int(stat_res.total_domains or 0) if stat_res else 0
        tot_cit = int(stat_res.total_citations or 0) if stat_res else 0
        avg_cit = round(float(stat_res.avg_citations or 0.0), 2) if stat_res else 0.0
        min_yr = int(stat_res.min_year) if stat_res and stat_res.min_year is not None else None
        max_yr = int(stat_res.max_year) if stat_res and stat_res.max_year is not None else None

        # 2. Top domains
        domains_resp = await cls.get_technology_domains(
            db=db,
            start_year=start_year,
            end_year=end_year,
            domain=domain,
            assignee=assignee,
            jurisdiction=jurisdiction,
            limit=5,
            profile_id=profile_id,
        )

        # 3. Top assignees
        assignees_resp = await cls.get_assignees(
            db=db,
            start_year=start_year,
            end_year=end_year,
            domain=domain,
            jurisdiction=jurisdiction,
            limit=5,
            profile_id=profile_id,
        )

        # 4. Jurisdictions
        jurisdictions_resp = await cls.get_jurisdictions(
            db=db,
            start_year=start_year,
            end_year=end_year,
            domain=domain,
            assignee=assignee,
            profile_id=profile_id,
        )

        return PatentLandscapeSummary(
            total_patents=tot_p,
            total_assignees=tot_ass,
            total_domains=tot_dom,
            total_citations=tot_cit,
            average_citations=avg_cit,
            filing_year_range={"min_year": min_yr, "max_year": max_yr},
            top_domains=domains_resp.domains,
            top_assignees=assignees_resp.assignees,
            jurisdiction_distribution=jurisdictions_resp.jurisdictions,
        )

    @classmethod
    async def get_innovation_map(
        cls,
        db: AsyncSession,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        domain: Optional[str] = None,
        assignee: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        profile_id: Optional[int] = None,
    ) -> InnovationMapResponse:
        """
        Synthesizes multi-dimensional relationships:
        Patent -> Technology Domain -> Classification -> Assignee -> Innovation Activity.
        Generates cross-tabulation matrix, active hotspots, and whitespace candidates.
        """
        from collections import Counter

        current_year = datetime.now(timezone.utc).year
        recent_threshold_year = current_year - 2

        q = select(Patent)
        q = cls._apply_base_filters(q, start_year, end_year, domain, assignee, jurisdiction, profile_id)
        patents = (await db.execute(q)).scalars().all()

        total_patents = len(patents)
        if total_patents == 0:
            return InnovationMapResponse(
                total_patents=0,
                domains=[],
                assignees=[],
                classifications=[],
                matrix=[],
                hotspots=[],
                whitespaces=[],
            )

        domains_set = set()
        assignees_set = set()
        classifications_set = set()

        # Matrix mapping: (domain, assignee) -> list of patent numbers
        matrix_dict: Dict[Tuple[str, str], List[str]] = {}
        # Hotspot mapping: (domain, classification) -> list of patents
        hotspot_dict: Dict[Tuple[str, str], List[Patent]] = {}

        for p in patents:
            dom = p.technology_domain or "Unclassified"
            ass = p.assignee or "Individual / Unassigned"
            cls_code = p.patent_classification or "General"

            domains_set.add(dom)
            assignees_set.add(ass)
            classifications_set.add(cls_code)

            m_key = (dom, ass)
            if m_key not in matrix_dict:
                matrix_dict[m_key] = []
            matrix_dict[m_key].append(p.patent_number)

            h_key = (dom, cls_code)
            if h_key not in hotspot_dict:
                hotspot_dict[h_key] = []
            hotspot_dict[h_key].append(p)

        matrix_cells = [
            InnovationMapMatrixCell(
                domain=dom,
                assignee=ass,
                patent_count=len(p_nums),
                patent_numbers=p_nums,
            )
            for (dom, ass), p_nums in sorted(matrix_dict.items(), key=lambda x: len(x[1]), reverse=True)
        ]

        hotspots: List[InnovationMapHotspot] = []
        for (dom, cls_code), plist in hotspot_dict.items():
            cnt = len(plist)
            rec_cnt = sum(
                1 for p in plist
                if p.filing_date and hasattr(p.filing_date, "year") and p.filing_date.year >= recent_threshold_year
            )
            vel = round((rec_cnt / cnt * 100.0), 2) if cnt > 0 else 0.0

            ass_counts = Counter(p.assignee for p in plist if p.assignee)
            top_ass = [a for a, _ in ass_counts.most_common(3)]

            if cnt >= 2 and vel >= 50.0:
                act_type = "EXPANDING_CORE"
            elif vel >= 50.0:
                act_type = "HIGH_GROWTH"
            else:
                act_type = "EMERGING"

            hotspots.append(
                InnovationMapHotspot(
                    domain=dom,
                    classification=cls_code,
                    patent_count=cnt,
                    recent_count=rec_cnt,
                    velocity_score=vel,
                    top_assignees=top_ass,
                    activity_type=act_type,
                )
            )
        hotspots.sort(key=lambda h: (h.patent_count, h.velocity_score), reverse=True)

        canonical_domains = [
            "Quantum Technologies",
            "Biotechnology & Genomic Sciences",
            "Clean Energy & Sustainability",
            "Artificial Intelligence & Machine Learning",
            "Cybersecurity & Cryptography",
        ]
        whitespaces: List[InnovationMapWhitespace] = []
        for c_dom in canonical_domains:
            matched_patents = [p for p in patents if p.technology_domain and c_dom.lower() in p.technology_domain.lower()]
            if not matched_patents:
                whitespaces.append(
                    InnovationMapWhitespace(
                        domain=c_dom,
                        whitespace_reason="Zero patent disclosures currently indexed in this technology field.",
                        opportunity_level="HIGH",
                        description=f"Significant unaddressed innovation space in {c_dom} with zero competing domestic or international filings registered in current corpus.",
                    )
                )
            elif len(matched_patents) <= 1:
                whitespaces.append(
                    InnovationMapWhitespace(
                        domain=c_dom,
                        whitespace_reason=f"Sparse patent density ({len(matched_patents)} disclosure).",
                        opportunity_level="MEDIUM",
                        description=f"Emerging opportunity space in {c_dom} with minimal prior art and high potential for proprietary IP positioning.",
                    )
                )

        return InnovationMapResponse(
            total_patents=total_patents,
            domains=sorted(list(domains_set)),
            assignees=sorted(list(assignees_set)),
            classifications=sorted(list(classifications_set)),
            matrix=matrix_cells,
            hotspots=hotspots,
            whitespaces=whitespaces,
        )

    @classmethod
    async def get_profile_recommendations(
        cls,
        user_id: int,
        limit: int = 10,
        db: AsyncSession = None,
    ) -> PatentRecommendationsResponse:
        """
        Module 3 Research Intelligence Integration:
        Recommends indexed patents relevant to the researcher's domains, keywords, and interests.
        Excludes patents already linked to the researcher's profile.
        """
        from app.services.profile_service import ProfileService

        profile = await ProfileService.get_or_create_profile(user_id=user_id, db=db)

        profile_domains: List[str] = []
        if getattr(profile, "domains", None):
            profile_domains = [d.name for d in profile.domains if hasattr(d, "name") and d.name]

        profile_keywords: List[str] = []
        if getattr(profile, "keywords", None):
            profile_keywords.extend([k.keyword for k in profile.keywords if hasattr(k, "keyword") and k.keyword])
        if getattr(profile, "interests", None):
            profile_keywords.extend([i.title for i in profile.interests if hasattr(i, "title") and i.title])
        if getattr(profile, "technology_areas", None):
            profile_keywords.extend([t.name for t in profile.technology_areas if hasattr(t, "name") and t.name])
        profile_keywords = list(dict.fromkeys(profile_keywords))

        # Query all patents excluding user's own linked patents
        user_linked_q = select(profile_patents.c.patent_id).where(profile_patents.c.profile_id == profile.id)
        user_patent_ids = (await db.execute(user_linked_q)).scalars().all()

        pat_q = select(Patent)
        if user_patent_ids:
            pat_q = pat_q.where(Patent.id.notin_(user_patent_ids))
        all_patents = (await db.execute(pat_q)).scalars().all()

        recommendations: List[PatentRecommendationItem] = []

        for p in all_patents:
            matched_doms: List[str] = []
            matched_kws: List[str] = []
            score = 0.0

            # 1. Domain match (+50 exact, +25 partial)
            p_dom = (p.technology_domain or "").lower()
            for pd in profile_domains:
                pd_clean = pd.lower()
                if pd_clean in p_dom or p_dom in pd_clean:
                    matched_doms.append(pd)
                    score += 50.0
                    break

            # 2. Keyword overlap in title and abstract (+10 per matched keyword up to 30)
            text_corpus = f"{p.title or ''} {p.abstract or ''}".lower()
            for kw in profile_keywords:
                if kw and kw in text_corpus:
                    matched_kws.append(kw)
                    if len(matched_kws) <= 3:
                        score += 10.0

            # 3. Citation impact density (+ up to 20 pts)
            score += min(20.0, p.citation_count * 0.5)

            # Baseline relevance if corpus is small
            if not matched_doms and not matched_kws:
                score = max(10.0, min(30.0, p.citation_count * 1.0))
                rationale = "General cross-domain intellectual property disclosure with active citation impact."
            else:
                dom_reason = f"matches your domain '{matched_doms[0]}'" if matched_doms else "aligns with your technical focus"
                kw_reason = f"matches keywords: {', '.join(matched_kws[:3])}" if matched_kws else "provides complementary patent coverage"
                rationale = f"Highly relevant to your research profile: {dom_reason} and {kw_reason}."

            recommendations.append(
                PatentRecommendationItem(
                    patent_id=p.id,
                    patent_number=p.patent_number,
                    title=p.title,
                    abstract=p.abstract,
                    assignee=p.assignee,
                    technology_domain=p.technology_domain,
                    patent_classification=p.patent_classification,
                    citation_count=p.citation_count,
                    match_score=min(100.0, round(score, 1)),
                    matched_domains=matched_doms,
                    matched_keywords=matched_kws,
                    rationale=rationale,
                )
            )

        recommendations.sort(key=lambda r: r.match_score, reverse=True)

        return PatentRecommendationsResponse(
            total_recommendations=len(recommendations[:limit]),
            profile_domains=profile_domains,
            profile_keywords=profile_keywords,
            recommendations=recommendations[:limit],
        )
