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

        for r in rows:
            p_count = int(r.count)
            share_pct = round((p_count / total_corpus * 100.0), 2) if total_corpus > 0 else 0.0
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

        return AssigneesResponse(
            total_assignees=len(assignees_list),
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
