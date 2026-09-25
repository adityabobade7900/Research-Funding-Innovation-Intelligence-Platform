import math
import statistics
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import select, func, and_, or_, desc, asc, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.publication import Publication, PublicationKeyword, profile_publications
from app.models.profile import Profile
from app.schemas.research_intelligence import (
    PublicationTrendPoint,
    PublicationTrendsResponse,
    DomainYearPoint,
    DomainTrendItem,
    DomainTrendsResponse,
    KeywordYearPoint,
    KeywordTrendItem,
    KeywordTrendsResponse,
    TopCitedPublicationSummary,
    CitationYearPoint,
    CitationStatisticsResponse,
    EmergingTopicItem,
    EmergingTopicsResponse,
    ResearchHotspotItem,
    ResearchHotspotsResponse,
)


class ResearchTrendService:
    """
    Deterministic, data-driven Research Trend Intelligence Service.
    Performs fast SQL-level aggregations and statistical analysis on scientific publications,
    domains, keywords, and citations.
    """

    @classmethod
    async def get_publication_trends(
        cls,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        domain: Optional[str] = None,
        keyword: Optional[str] = None,
        profile_id: Optional[int] = None,
        db: AsyncSession = None
    ) -> PublicationTrendsResponse:
        """Calculates publication volume and Year-over-Year (YoY) growth over time."""
        year_col = extract("year", Publication.publication_date).label("pub_year")

        stmt = select(
            year_col,
            func.count(Publication.id).label("pub_count")
        ).where(Publication.publication_date.is_not(None))

        if profile_id is not None:
            stmt = stmt.join(profile_publications, profile_publications.c.publication_id == Publication.id)\
                       .where(profile_publications.c.profile_id == profile_id)

        if domain:
            dom_clean = domain.strip().lower()
            stmt = stmt.where(
                or_(
                    func.lower(Publication.primary_domain) == dom_clean,
                    Publication.primary_domain.ilike(f"%{dom_clean}%")
                )
            )

        if keyword:
            stmt = stmt.join(PublicationKeyword, PublicationKeyword.publication_id == Publication.id)\
                       .where(func.lower(PublicationKeyword.keyword) == keyword.strip().lower())

        if start_year:
            stmt = stmt.where(extract("year", Publication.publication_date) >= start_year)
        if end_year:
            stmt = stmt.where(extract("year", Publication.publication_date) <= end_year)

        stmt = stmt.group_by(year_col).order_by(year_col.asc())

        res = await db.execute(stmt)
        rows = res.all()

        points: List[PublicationTrendPoint] = []
        total_pubs = 0
        prev_count: Optional[int] = None

        min_year: Optional[int] = None
        max_year: Optional[int] = None

        for row in rows:
            yr = int(row[0]) if row[0] is not None else None
            if yr is None:
                continue
            cnt = int(row[1])
            total_pubs += cnt

            if min_year is None or yr < min_year:
                min_year = yr
            if max_year is None or yr > max_year:
                max_year = yr

            growth: Optional[float] = None
            if prev_count is not None and prev_count > 0:
                growth = round(((cnt - prev_count) / prev_count) * 100.0, 1)
            elif prev_count is not None and prev_count == 0:
                growth = 100.0 if cnt > 0 else 0.0

            points.append(PublicationTrendPoint(
                year=yr,
                publication_count=cnt,
                growth_rate=growth
            ))
            prev_count = cnt

        return PublicationTrendsResponse(
            total_publications=total_pubs,
            year_range={"min_year": min_year, "max_year": max_year},
            points=points
        )

    @classmethod
    async def get_domain_trends(
        cls,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        min_count: int = 1,
        limit: int = 15,
        profile_id: Optional[int] = None,
        db: AsyncSession = None
    ) -> DomainTrendsResponse:
        """Analyzes publication trajectories, citation rates, and yearly share by research domain."""
        year_col = extract("year", Publication.publication_date).label("pub_year")

        # 1. Total publications per year for share calculation
        total_yearly_stmt = select(
            year_col,
            func.count(Publication.id)
        ).where(Publication.publication_date.is_not(None))

        if profile_id is not None:
            total_yearly_stmt = total_yearly_stmt.join(profile_publications, profile_publications.c.publication_id == Publication.id)\
                                                 .where(profile_publications.c.profile_id == profile_id)

        if start_year:
            total_yearly_stmt = total_yearly_stmt.where(extract("year", Publication.publication_date) >= start_year)
        if end_year:
            total_yearly_stmt = total_yearly_stmt.where(extract("year", Publication.publication_date) <= end_year)

        total_yearly_stmt = total_yearly_stmt.group_by(year_col)
        tot_res = await db.execute(total_yearly_stmt)
        yearly_totals = {int(r[0]): int(r[1]) for r in tot_res.all() if r[0] is not None}

        # 2. Aggregation by domain and year
        stmt = select(
            Publication.primary_domain,
            year_col,
            func.count(Publication.id).label("count"),
            func.avg(Publication.citation_count).label("avg_citations")
        ).where(
            and_(
                Publication.primary_domain.is_not(None),
                Publication.publication_date.is_not(None)
            )
        )

        if profile_id is not None:
            stmt = stmt.join(profile_publications, profile_publications.c.publication_id == Publication.id)\
                       .where(profile_publications.c.profile_id == profile_id)

        if start_year:
            stmt = stmt.where(extract("year", Publication.publication_date) >= start_year)
        if end_year:
            stmt = stmt.where(extract("year", Publication.publication_date) <= end_year)

        stmt = stmt.group_by(Publication.primary_domain, year_col).order_by(Publication.primary_domain.asc(), year_col.asc())

        res = await db.execute(stmt)
        rows = res.all()

        domain_map: Dict[str, Dict[str, Any]] = {}
        for r in rows:
            dom = r[0]
            if not dom:
                continue
            yr = int(r[1]) if r[1] is not None else None
            if yr is None:
                continue
            cnt = int(r[2])
            avg_cit = float(r[3]) if r[3] is not None else 0.0

            if dom not in domain_map:
                domain_map[dom] = {
                    "domain": dom,
                    "total_publications": 0,
                    "weighted_cit_sum": 0.0,
                    "yearly": []
                }

            tot_year = yearly_totals.get(yr, cnt)
            share = round((cnt / tot_year) * 100.0, 1) if tot_year > 0 else 0.0

            domain_map[dom]["total_publications"] += cnt
            domain_map[dom]["weighted_cit_sum"] += avg_cit * cnt
            domain_map[dom]["yearly"].append(DomainYearPoint(year=yr, count=cnt, share_percentage=share))

        # Filter by min_count and sort by total_publications desc
        items: List[DomainTrendItem] = []
        for dom, d_data in domain_map.items():
            if d_data["total_publications"] >= min_count:
                avg_citations = round(d_data["weighted_cit_sum"] / d_data["total_publications"], 1) if d_data["total_publications"] > 0 else 0.0
                items.append(DomainTrendItem(
                    domain=dom,
                    total_publications=d_data["total_publications"],
                    average_citations=avg_citations,
                    yearly_distribution=d_data["yearly"]
                ))

        items.sort(key=lambda x: x.total_publications, reverse=True)
        return DomainTrendsResponse(
            total_domains=len(items),
            domains=items[:limit]
        )

    @classmethod
    async def get_keyword_trends(
        cls,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        domain: Optional[str] = None,
        min_count: int = 1,
        limit: int = 20,
        profile_id: Optional[int] = None,
        db: AsyncSession = None
    ) -> KeywordTrendsResponse:
        """Aggregates keyword frequencies over time to track rising and steady topics."""
        now_year = datetime.now(timezone.utc).year
        recent_threshold_year = now_year - 2

        year_col = extract("year", Publication.publication_date).label("pub_year")
        kw_col = func.lower(PublicationKeyword.keyword).label("clean_kw")

        stmt = select(
            kw_col,
            year_col,
            func.count(Publication.id).label("count")
        ).join(Publication, Publication.id == PublicationKeyword.publication_id)\
         .where(Publication.publication_date.is_not(None))

        if profile_id is not None:
            stmt = stmt.join(profile_publications, profile_publications.c.publication_id == Publication.id)\
                       .where(profile_publications.c.profile_id == profile_id)

        if domain:
            dom_clean = domain.strip().lower()
            stmt = stmt.where(
                or_(
                    func.lower(Publication.primary_domain) == dom_clean,
                    Publication.primary_domain.ilike(f"%{dom_clean}%")
                )
            )

        if start_year:
            stmt = stmt.where(extract("year", Publication.publication_date) >= start_year)
        if end_year:
            stmt = stmt.where(extract("year", Publication.publication_date) <= end_year)

        stmt = stmt.group_by(kw_col, year_col).order_by(kw_col.asc(), year_col.asc())

        res = await db.execute(stmt)
        rows = res.all()

        kw_map: Dict[str, Dict[str, Any]] = {}
        for r in rows:
            kw = r[0]
            if not kw:
                continue
            yr = int(r[1]) if r[1] is not None else None
            if yr is None:
                continue
            cnt = int(r[2])

            if kw not in kw_map:
                kw_map[kw] = {
                    "keyword": kw.title(),
                    "total_occurrences": 0,
                    "recent_count": 0,
                    "yearly": []
                }

            kw_map[kw]["total_occurrences"] += cnt
            if yr >= recent_threshold_year:
                kw_map[kw]["recent_count"] += cnt
            kw_map[kw]["yearly"].append(KeywordYearPoint(year=yr, count=cnt))

        items: List[KeywordTrendItem] = []
        for kw, k_data in kw_map.items():
            if k_data["total_occurrences"] >= min_count:
                items.append(KeywordTrendItem(
                    keyword=k_data["keyword"],
                    total_occurrences=k_data["total_occurrences"],
                    recent_count=k_data["recent_count"],
                    yearly_distribution=k_data["yearly"]
                ))

        items.sort(key=lambda x: x.total_occurrences, reverse=True)
        return KeywordTrendsResponse(
            total_keywords=len(items),
            keywords=items[:limit]
        )

    @classmethod
    async def get_citation_statistics(
        cls,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        domain: Optional[str] = None,
        profile_id: Optional[int] = None,
        db: AsyncSession = None
    ) -> CitationStatisticsResponse:
        """Computes statistical citation analytics including total, average, median, and yearly metrics."""
        # 1. Overall stats query
        base_stmt = select(
            Publication.id,
            Publication.title,
            Publication.citation_count,
            Publication.publication_date,
            Publication.venue,
            Publication.primary_domain,
            Publication.doi
        )

        if profile_id is not None:
            base_stmt = base_stmt.join(profile_publications, profile_publications.c.publication_id == Publication.id)\
                                 .where(profile_publications.c.profile_id == profile_id)

        if domain:
            dom_clean = domain.strip().lower()
            base_stmt = base_stmt.where(
                or_(
                    func.lower(Publication.primary_domain) == dom_clean,
                    Publication.primary_domain.ilike(f"%{dom_clean}%")
                )
            )

        if start_year:
            base_stmt = base_stmt.where(extract("year", Publication.publication_date) >= start_year)
        if end_year:
            base_stmt = base_stmt.where(extract("year", Publication.publication_date) <= end_year)

        res = await db.execute(base_stmt)
        all_pubs = res.all()

        total_pubs = len(all_pubs)
        if total_pubs == 0:
            return CitationStatisticsResponse(
                total_publications=0,
                total_citations=0,
                average_citations=0.0,
                median_citations=0.0,
                max_citations=0,
                citations_by_year=[],
                top_cited_publications=[]
            )

        citations_list = [int(p[2]) for p in all_pubs]
        total_citations = sum(citations_list)
        avg_citations = round(statistics.mean(citations_list), 1)
        med_citations = round(float(statistics.median(citations_list)), 1)
        max_citations = max(citations_list)

        # 2. Yearly breakdown query
        year_col = extract("year", Publication.publication_date).label("pub_year")
        yearly_stmt = select(
            year_col,
            func.sum(Publication.citation_count).label("total_cit"),
            func.avg(Publication.citation_count).label("avg_cit"),
            func.count(Publication.id).label("pub_count")
        ).where(Publication.publication_date.is_not(None))

        if profile_id is not None:
            yearly_stmt = yearly_stmt.join(profile_publications, profile_publications.c.publication_id == Publication.id)\
                                     .where(profile_publications.c.profile_id == profile_id)

        if domain:
            dom_clean = domain.strip().lower()
            yearly_stmt = yearly_stmt.where(
                or_(
                    func.lower(Publication.primary_domain) == dom_clean,
                    Publication.primary_domain.ilike(f"%{dom_clean}%")
                )
            )

        if start_year:
            yearly_stmt = yearly_stmt.where(extract("year", Publication.publication_date) >= start_year)
        if end_year:
            yearly_stmt = yearly_stmt.where(extract("year", Publication.publication_date) <= end_year)

        yearly_stmt = yearly_stmt.group_by(year_col).order_by(year_col.asc())
        yr_res = await db.execute(yearly_stmt)

        citations_by_year = [
            CitationYearPoint(
                year=int(r[0]),
                total_citations=int(r[1]) if r[1] is not None else 0,
                average_citations=round(float(r[2]), 1) if r[2] is not None else 0.0,
                publication_count=int(r[3])
            )
            for r in yr_res.all() if r[0] is not None
        ]

        # 3. Top cited publications
        sorted_pubs = sorted(all_pubs, key=lambda p: int(p[2]), reverse=True)[:10]
        top_cited = [
            TopCitedPublicationSummary(
                id=p[0],
                title=p[1],
                citation_count=p[2],
                publication_date=p[3],
                venue=p[4],
                primary_domain=p[5],
                doi=p[6]
            )
            for p in sorted_pubs
        ]

        return CitationStatisticsResponse(
            total_publications=total_pubs,
            total_citations=total_citations,
            average_citations=avg_citations,
            median_citations=med_citations,
            max_citations=max_citations,
            citations_by_year=citations_by_year,
            top_cited_publications=top_cited
        )

    @classmethod
    async def get_emerging_topics(
        cls,
        recent_years: int = 2,
        min_count: int = 2,
        domain: Optional[str] = None,
        limit: int = 20,
        profile_id: Optional[int] = None,
        db: AsyncSession = None
    ) -> EmergingTopicsResponse:
        """
        Detects rapidly emerging keywords and research topics using a transparent statistical velocity model.
        Compares publication volume in recent window vs. historical baseline.
        """
        now_year = datetime.now(timezone.utc).year
        recent_start_year = now_year - (recent_years - 1)

        year_col = extract("year", Publication.publication_date).label("pub_year")
        kw_col = func.lower(PublicationKeyword.keyword).label("clean_kw")

        stmt = select(
            kw_col,
            year_col,
            func.count(Publication.id).label("count")
        ).join(Publication, Publication.id == PublicationKeyword.publication_id)\
         .where(Publication.publication_date.is_not(None))

        if profile_id is not None:
            stmt = stmt.join(profile_publications, profile_publications.c.publication_id == Publication.id)\
                       .where(profile_publications.c.profile_id == profile_id)

        if domain:
            dom_clean = domain.strip().lower()
            stmt = stmt.where(
                or_(
                    func.lower(Publication.primary_domain) == dom_clean,
                    Publication.primary_domain.ilike(f"%{dom_clean}%")
                )
            )

        stmt = stmt.group_by(kw_col, year_col)
        res = await db.execute(stmt)
        rows = res.all()

        topic_stats: Dict[str, Dict[str, Any]] = {}
        for r in rows:
            kw = r[0]
            if not kw:
                continue
            yr = int(r[1]) if r[1] is not None else None
            if yr is None:
                continue
            cnt = int(r[2])

            if kw not in topic_stats:
                topic_stats[kw] = {"recent": 0, "historical": 0, "years": set()}

            topic_stats[kw]["years"].add(yr)
            if yr >= recent_start_year:
                topic_stats[kw]["recent"] += cnt
            else:
                topic_stats[kw]["historical"] += cnt

        topics: List[EmergingTopicItem] = []
        for kw, stat in topic_stats.items():
            r_cnt = stat["recent"]
            h_cnt = stat["historical"]

            if r_cnt < min_count:
                continue

            # Statistical Velocity Calculation
            # Formula: Velocity = (R / (R + H + 1)) * (1 + (R / max(1, H_avg))) * 10
            h_avg = h_cnt / max(1.0, float(len(stat["years"]) - 1))
            growth_rate: Optional[float] = None
            if h_cnt > 0:
                growth_rate = round(((r_cnt - h_avg) / h_avg) * 100.0, 1)

            recent_ratio = r_cnt / (r_cnt + h_cnt + 1)
            growth_multiplier = 1.0 + min(5.0, r_cnt / max(1.0, h_avg))
            velocity_score = round(recent_ratio * growth_multiplier * 10.0, 1)

            reasons: List[str] = []
            if h_cnt == 0:
                status = "EMERGING"
                reasons.append(f"Novel topic: {r_cnt} publications in recent window ({recent_start_year}–{now_year}) with zero prior baseline")
            elif r_cnt > h_cnt:
                status = "EMERGING"
                reasons.append(f"Accelerating topic: {r_cnt} recent publications exceeds historical cumulative count ({h_cnt})")
            elif r_cnt >= 3 and h_cnt >= 3:
                status = "ESTABLISHED_GROWING"
                reasons.append(f"Established high-volume topic: sustained publication volume across {len(stat['years'])} active years")
            else:
                status = "STABLE"
                reasons.append(f"Stable interest: {r_cnt} recent vs {h_cnt} historical publications")

            topics.append(EmergingTopicItem(
                topic=kw.title(),
                recent_count=r_cnt,
                historical_count=h_cnt,
                growth_rate=growth_rate,
                velocity_score=velocity_score,
                status=status,
                reasons=reasons
            ))

        topics.sort(key=lambda t: t.velocity_score, reverse=True)
        return EmergingTopicsResponse(
            evaluation_window={
                "recent_start_year": recent_start_year,
                "current_year": now_year,
                "recent_window_length_years": recent_years
            },
            total_emerging=len(topics),
            topics=topics[:limit]
        )

    @classmethod
    async def get_research_hotspots(
        cls,
        recent_years: int = 2,
        limit: int = 15,
        profile_id: Optional[int] = None,
        db: AsyncSession = None
    ) -> ResearchHotspotsResponse:
        """
        Calculates deterministic Research Hotspots combining publication volume, recent YoY growth,
        and citation impact across both research domains and major topics.
        """
        now = datetime.now(timezone.utc)
        now_year = now.year
        recent_start_year = now_year - (recent_years - 1)

        year_col = extract("year", Publication.publication_date).label("pub_year")

        # 1. Domain-level metrics
        domain_stmt = select(
            Publication.primary_domain,
            year_col,
            func.count(Publication.id).label("count"),
            func.sum(Publication.citation_count).label("total_cit"),
            func.avg(Publication.citation_count).label("avg_cit")
        ).where(
            and_(
                Publication.primary_domain.is_not(None),
                Publication.publication_date.is_not(None)
            )
        )

        if profile_id is not None:
            domain_stmt = domain_stmt.join(profile_publications, profile_publications.c.publication_id == Publication.id)\
                                     .where(profile_publications.c.profile_id == profile_id)

        domain_stmt = domain_stmt.group_by(Publication.primary_domain, year_col)
        d_res = await db.execute(domain_stmt)
        d_rows = d_res.all()

        domain_agg: Dict[str, Dict[str, Any]] = {}
        for r in d_rows:
            dom = r[0]
            if not dom:
                continue
            yr = int(r[1]) if r[1] is not None else None
            if yr is None:
                continue
            cnt = int(r[2])
            tot_cit = int(r[3]) if r[3] is not None else 0
            avg_cit = float(r[4]) if r[4] is not None else 0.0

            if dom not in domain_agg:
                domain_agg[dom] = {
                    "total_pubs": 0,
                    "recent_pubs": 0,
                    "historical_pubs": 0,
                    "total_cit": 0,
                    "weighted_avg_cit": 0.0
                }

            domain_agg[dom]["total_pubs"] += cnt
            domain_agg[dom]["total_cit"] += tot_cit
            domain_agg[dom]["weighted_avg_cit"] += avg_cit * cnt
            if yr >= recent_start_year:
                domain_agg[dom]["recent_pubs"] += cnt
            else:
                domain_agg[dom]["historical_pubs"] += cnt

        hotspots: List[ResearchHotspotItem] = []

        for dom, d_data in domain_agg.items():
            tot_p = d_data["total_pubs"]
            rec_p = d_data["recent_pubs"]
            hist_p = d_data["historical_pubs"]
            tot_cit = d_data["total_cit"]
            avg_cit = round(d_data["weighted_avg_cit"] / tot_p, 1) if tot_p > 0 else 0.0

            # YoY Recent Growth
            growth_rate: Optional[float] = None
            if hist_p > 0:
                growth_rate = round(((rec_p - hist_p) / hist_p) * 100.0, 1)

            # Hotspot Score Formula (0 to 100):
            # Volume Score (Max 40 pts) = min(40, tot_p * 5)
            vol_score = min(40.0, tot_p * 5.0)
            # Growth Score (Max 35 pts) = min(35, max(0, (growth_rate or 50.0) * 0.35))
            growth_score = min(35.0, max(0.0, (growth_rate if growth_rate is not None else 50.0) * 0.35))
            # Citation Score (Max 25 pts) = min(25, avg_cit * 2.5)
            cit_score = min(25.0, avg_cit * 2.5)

            hotspot_score = round(min(100.0, vol_score + growth_score + cit_score), 1)

            if hotspot_score >= 70.0:
                classification = "CRITICAL_HOTSPOT"
            elif hotspot_score >= 45.0:
                classification = "HIGH_ACTIVITY"
            elif hotspot_score >= 20.0:
                classification = "MODERATE_ACTIVITY"
            else:
                classification = "EMERGING_NICHE"

            key_drivers = [
                f"{tot_p} indexed publications ({rec_p} in recent window)",
                f"{tot_cit} total citations across domain (avg {avg_cit} per paper)"
            ]
            if growth_rate is not None:
                key_drivers.append(f"{growth_rate}% growth trajectory relative to historical baseline")

            hotspots.append(ResearchHotspotItem(
                domain_or_topic=dom,
                category="domain",
                publication_count=tot_p,
                recent_growth_rate=growth_rate,
                citation_count=tot_cit,
                average_citations=avg_cit,
                hotspot_score=hotspot_score,
                classification=classification,
                key_drivers=key_drivers
            ))

        hotspots.sort(key=lambda h: h.hotspot_score, reverse=True)
        return ResearchHotspotsResponse(
            total_hotspots=len(hotspots),
            evaluation_timestamp=now,
            hotspots=hotspots[:limit]
        )
