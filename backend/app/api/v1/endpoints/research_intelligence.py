from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user_optional, get_current_active_user
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.research_intelligence import (
    PublicationTrendsResponse,
    DomainTrendsResponse,
    KeywordTrendsResponse,
    CitationStatisticsResponse,
    EmergingTopicsResponse,
    ResearchHotspotsResponse,
    ResearchGapsResponse,
)
from app.services.research_trend_service import ResearchTrendService
from app.services.research_gap_service import ResearchGapService
from app.services.profile_service import ProfileService

router = APIRouter()


async def _resolve_profile_id(
    my_profile_only: bool,
    current_user: Optional[User],
    db: AsyncSession
) -> Optional[int]:
    if not my_profile_only:
        return None
    if not current_user:
        return None
    profile = await ProfileService.get_or_create_profile(current_user.id, db)
    return profile.id


@router.get("/trends/publications", response_model=ApiResponse[PublicationTrendsResponse], status_code=status.HTTP_200_OK)
async def get_publication_trends(
    start_year: Optional[int] = Query(None, description="Start year filter"),
    end_year: Optional[int] = Query(None, description="End year filter"),
    domain: Optional[str] = Query(None, description="Filter by research domain"),
    keyword: Optional[str] = Query(None, description="Filter by keyword"),
    my_profile_only: bool = Query(False, description="Scope metrics to authenticated user's publications only"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Computes publication volume trajectories and Year-over-Year (YoY) growth rates
    across the entire scientific corpus or isolated to the user's research portfolio.
    """
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    trends = await ResearchTrendService.get_publication_trends(
        start_year=start_year,
        end_year=end_year,
        domain=domain,
        keyword=keyword,
        profile_id=profile_id,
        db=db
    )
    return ApiResponse(
        success=True,
        data=trends,
        message="Publication trends calculated successfully"
    )


@router.get("/trends/domains", response_model=ApiResponse[DomainTrendsResponse], status_code=status.HTTP_200_OK)
async def get_domain_trends(
    start_year: Optional[int] = Query(None, description="Start year filter"),
    end_year: Optional[int] = Query(None, description="End year filter"),
    min_count: int = Query(1, ge=1, description="Minimum publication count per domain"),
    limit: int = Query(15, ge=1, le=50),
    my_profile_only: bool = Query(False, description="Scope metrics to authenticated user's publications only"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyzes domain market shares, yearly distribution, and average citation density
    across active research taxonomy areas.
    """
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    domains = await ResearchTrendService.get_domain_trends(
        start_year=start_year,
        end_year=end_year,
        min_count=min_count,
        limit=limit,
        profile_id=profile_id,
        db=db
    )
    return ApiResponse(
        success=True,
        data=domains,
        message="Domain trends calculated successfully"
    )


@router.get("/trends/keywords", response_model=ApiResponse[KeywordTrendsResponse], status_code=status.HTTP_200_OK)
async def get_keyword_trends(
    start_year: Optional[int] = Query(None, description="Start year filter"),
    end_year: Optional[int] = Query(None, description="End year filter"),
    domain: Optional[str] = Query(None, description="Filter keywords within specific research domain"),
    min_count: int = Query(1, ge=1, description="Minimum occurrences threshold"),
    limit: int = Query(20, ge=1, le=100),
    my_profile_only: bool = Query(False, description="Scope metrics to authenticated user's publications only"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Identifies high-frequency and sustained keyword trajectories over time.
    """
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    keywords = await ResearchTrendService.get_keyword_trends(
        start_year=start_year,
        end_year=end_year,
        domain=domain,
        min_count=min_count,
        limit=limit,
        profile_id=profile_id,
        db=db
    )
    return ApiResponse(
        success=True,
        data=keywords,
        message="Keyword trends calculated successfully"
    )


@router.get("/trends/citations", response_model=ApiResponse[CitationStatisticsResponse], status_code=status.HTTP_200_OK)
async def get_citation_statistics(
    start_year: Optional[int] = Query(None, description="Start year filter"),
    end_year: Optional[int] = Query(None, description="End year filter"),
    domain: Optional[str] = Query(None, description="Filter by research domain"),
    my_profile_only: bool = Query(False, description="Scope metrics to authenticated user's publications only"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculates statistical citation metrics (total, mean, median, max) and top cited papers.
    """
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    stats = await ResearchTrendService.get_citation_statistics(
        start_year=start_year,
        end_year=end_year,
        domain=domain,
        profile_id=profile_id,
        db=db
    )
    return ApiResponse(
        success=True,
        data=stats,
        message="Citation statistics calculated successfully"
    )


@router.get("/emerging-topics", response_model=ApiResponse[EmergingTopicsResponse], status_code=status.HTTP_200_OK)
async def get_emerging_topics(
    recent_years: int = Query(2, ge=1, le=5, description="Length of recent evaluation window in years"),
    min_count: int = Query(2, ge=1, description="Minimum publication count in recent window"),
    domain: Optional[str] = Query(None, description="Filter within specific research domain"),
    limit: int = Query(20, ge=1, le=50),
    my_profile_only: bool = Query(False, description="Scope to authenticated user's publications only"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Detects rapidly emerging scientific keywords and topics using statistical velocity models
    comparing recent acceleration against historical baseline activity.
    """
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    topics = await ResearchTrendService.get_emerging_topics(
        recent_years=recent_years,
        min_count=min_count,
        domain=domain,
        limit=limit,
        profile_id=profile_id,
        db=db
    )
    return ApiResponse(
        success=True,
        data=topics,
        message=f"Identified {len(topics.topics)} emerging research topic(s)"
    )


@router.get("/hotspots", response_model=ApiResponse[ResearchHotspotsResponse], status_code=status.HTTP_200_OK)
async def get_research_hotspots(
    recent_years: int = Query(2, ge=1, le=5, description="Recent activity window in years"),
    limit: int = Query(15, ge=1, le=50),
    my_profile_only: bool = Query(False, description="Scope to authenticated user's publications only"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Computes deterministic Research Hotspots combining publication volume, recent YoY growth,
    and citation impact across active domains.
    """
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    hotspots = await ResearchTrendService.get_research_hotspots(
        recent_years=recent_years,
        limit=limit,
        profile_id=profile_id,
        db=db
    )
    return ApiResponse(
        success=True,
        data=hotspots,
        message=f"Calculated {len(hotspots.hotspots)} research hotspot(s)"
    )


@router.get("/gaps", response_model=ApiResponse[ResearchGapsResponse], status_code=status.HTTP_200_OK)
async def get_research_gaps(
    domain: Optional[str] = Query(None, description="Optional domain filter"),
    min_confidence: float = Query(0.6, ge=0.0, le=1.0, description="Minimum confidence threshold"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of gaps to return"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Synthesizes and discovers macro-corpus research gaps across indexed publications.
    Identifies convergent limitations, bottlenecks, and unaddressed future directions.
    Returns INSUFFICIENT_DATA status if corpus size is below minimum threshold (2 publications).
    """
    gaps_resp = await ResearchGapService.get_research_gaps(
        domain=domain,
        min_confidence=min_confidence,
        limit=limit,
        db=db
    )
    return ApiResponse(
        success=True,
        data=gaps_resp,
        message=gaps_resp.message
    )

