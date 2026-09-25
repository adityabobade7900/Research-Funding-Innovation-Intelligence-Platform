from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user_optional, get_current_active_user
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.patent_intelligence import (
    PatentTrendsResponse,
    TechnologyDomainsResponse,
    AssigneesResponse,
    JurisdictionsResponse,
    PatentStatusResponse,
    CompetitiveLandscapeResponse,
    PatentLandscapeSummary,
    PatentClusteringResponse,
    InnovationMapResponse,
    PatentRecommendationsResponse,
)
from app.services.patent_landscape_service import PatentLandscapeService
from app.services.patent_clustering_service import PatentClusteringService
from app.services.profile_service import ProfileService

router = APIRouter()


async def _resolve_profile_id(
    my_profile_only: bool,
    current_user: Optional[User],
    db: AsyncSession
) -> Optional[int]:
    if not my_profile_only or not current_user:
        return None
    profile = await ProfileService.get_or_create_profile(current_user.id, db)
    return profile.id


@router.get("/landscape", response_model=ApiResponse[PatentLandscapeSummary], status_code=status.HTTP_200_OK)
async def get_patent_landscape_summary(
    start_year: Optional[int] = Query(None, description="Start year filter (filing or publication)"),
    end_year: Optional[int] = Query(None, description="End year filter"),
    domain: Optional[str] = Query(None, description="Filter by technology domain"),
    assignee: Optional[str] = Query(None, description="Filter by patent assignee"),
    jurisdiction: Optional[str] = Query(None, description="Filter by 2-letter jurisdiction authority (e.g. US, EP, WO)"),
    my_profile_only: bool = Query(False, description="Scope landscape to authenticated user's portfolio only"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Computes top-level patent landscape summary statistics, top domains,
    leading assignees, and jurisdiction distribution.
    """
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    summary = await PatentLandscapeService.get_landscape_summary(
        db=db,
        start_year=start_year,
        end_year=end_year,
        domain=domain,
        assignee=assignee,
        jurisdiction=jurisdiction,
        profile_id=profile_id,
    )
    return ApiResponse(
        success=True,
        data=summary,
        message="Patent landscape summary computed successfully"
    )


@router.get("/trends", response_model=ApiResponse[PatentTrendsResponse], status_code=status.HTTP_200_OK)
async def get_patent_trends(
    start_year: Optional[int] = Query(None, description="Start year filter"),
    end_year: Optional[int] = Query(None, description="End year filter"),
    domain: Optional[str] = Query(None, description="Filter by technology domain"),
    assignee: Optional[str] = Query(None, description="Filter by assignee"),
    jurisdiction: Optional[str] = Query(None, description="Filter by jurisdiction code"),
    my_profile_only: bool = Query(False, description="Scope trends to authenticated user's portfolio only"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculates yearly patent filing volume, grant volume, and Year-over-Year (YoY) growth rates.
    """
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    trends = await PatentLandscapeService.get_trends(
        db=db,
        start_year=start_year,
        end_year=end_year,
        domain=domain,
        assignee=assignee,
        jurisdiction=jurisdiction,
        profile_id=profile_id,
    )
    return ApiResponse(
        success=True,
        data=trends,
        message="Patent filing and grant trends computed successfully"
    )


@router.get("/technology-domains", response_model=ApiResponse[TechnologyDomainsResponse], status_code=status.HTTP_200_OK)
async def get_technology_domains(
    start_year: Optional[int] = Query(None, description="Start year filter"),
    end_year: Optional[int] = Query(None, description="End year filter"),
    domain: Optional[str] = Query(None, description="Filter by technology domain"),
    assignee: Optional[str] = Query(None, description="Filter by assignee"),
    jurisdiction: Optional[str] = Query(None, description="Filter by jurisdiction code"),
    min_count: int = Query(1, ge=1, description="Minimum patent threshold per domain"),
    limit: int = Query(20, ge=1, le=100, description="Max domains to return"),
    my_profile_only: bool = Query(False, description="Scope to authenticated user's portfolio only"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyzes technology domain market share, citation impact, and calculates
    the Herfindahl-Hirschman Concentration Index (HHI).
    """
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    domains_data = await PatentLandscapeService.get_technology_domains(
        db=db,
        start_year=start_year,
        end_year=end_year,
        domain=domain,
        assignee=assignee,
        jurisdiction=jurisdiction,
        min_count=min_count,
        limit=limit,
        profile_id=profile_id,
    )
    return ApiResponse(
        success=True,
        data=domains_data,
        message="Technology domain distribution and concentration index computed successfully"
    )


@router.get("/assignees", response_model=ApiResponse[AssigneesResponse], status_code=status.HTTP_200_OK)
async def get_assignees(
    start_year: Optional[int] = Query(None, description="Start year filter"),
    end_year: Optional[int] = Query(None, description="End year filter"),
    domain: Optional[str] = Query(None, description="Filter by technology domain"),
    jurisdiction: Optional[str] = Query(None, description="Filter by jurisdiction code"),
    min_count: int = Query(1, ge=1, description="Minimum patent threshold per assignee"),
    limit: int = Query(20, ge=1, le=100, description="Max assignees to return"),
    my_profile_only: bool = Query(False, description="Scope to authenticated user's portfolio only"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Ranks top patent holders/assignees with patent volume, citation impact,
    recent filing velocity, and primary technology domains.
    """
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    assignees_data = await PatentLandscapeService.get_assignees(
        db=db,
        start_year=start_year,
        end_year=end_year,
        domain=domain,
        jurisdiction=jurisdiction,
        min_count=min_count,
        limit=limit,
        profile_id=profile_id,
    )
    return ApiResponse(
        success=True,
        data=assignees_data,
        message="Patent assignee landscape computed successfully"
    )


@router.get("/jurisdictions", response_model=ApiResponse[JurisdictionsResponse], status_code=status.HTTP_200_OK)
async def get_jurisdictions(
    start_year: Optional[int] = Query(None, description="Start year filter"),
    end_year: Optional[int] = Query(None, description="End year filter"),
    domain: Optional[str] = Query(None, description="Filter by technology domain"),
    assignee: Optional[str] = Query(None, description="Filter by assignee"),
    my_profile_only: bool = Query(False, description="Scope to authenticated user's portfolio only"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Evaluates global jurisdiction distribution across patent authorities (USPTO, EPO, WIPO, CNIPA, JPO, etc.).
    """
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    jurisdictions_data = await PatentLandscapeService.get_jurisdictions(
        db=db,
        start_year=start_year,
        end_year=end_year,
        domain=domain,
        assignee=assignee,
        profile_id=profile_id,
    )
    return ApiResponse(
        success=True,
        data=jurisdictions_data,
        message="Patent jurisdiction distribution computed successfully"
    )


@router.get("/status", response_model=ApiResponse[PatentStatusResponse], status_code=status.HTTP_200_OK)
async def get_status_distribution(
    start_year: Optional[int] = Query(None, description="Start year filter"),
    end_year: Optional[int] = Query(None, description="End year filter"),
    domain: Optional[str] = Query(None, description="Filter by technology domain"),
    assignee: Optional[str] = Query(None, description="Filter by assignee"),
    jurisdiction: Optional[str] = Query(None, description="Filter by jurisdiction code"),
    my_profile_only: bool = Query(False, description="Scope to authenticated user's portfolio only"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyzes patent lifecycle status distribution (Granted, Pending Application, Published).
    """
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    status_data = await PatentLandscapeService.get_status_distribution(
        db=db,
        start_year=start_year,
        end_year=end_year,
        domain=domain,
        assignee=assignee,
        jurisdiction=jurisdiction,
        profile_id=profile_id,
    )
    return ApiResponse(
        success=True,
        data=status_data,
        message="Patent status distribution computed successfully"
    )


@router.get("/competitive-landscape", response_model=ApiResponse[CompetitiveLandscapeResponse], status_code=status.HTTP_200_OK)
async def get_competitive_landscape(
    start_year: Optional[int] = Query(None, description="Start year filter"),
    end_year: Optional[int] = Query(None, description="End year filter"),
    domain: Optional[str] = Query(None, description="Filter by technology domain"),
    jurisdiction: Optional[str] = Query(None, description="Filter by jurisdiction code"),
    limit: int = Query(15, ge=1, le=50, description="Max competitors to analyze"),
    my_profile_only: bool = Query(False, description="Scope to authenticated user's portfolio only"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculates structured competitive patent landscape indicators (volume, velocity, domain breadth, citation impact).
    """
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    comp_data = await PatentLandscapeService.get_competitive_landscape(
        db=db,
        start_year=start_year,
        end_year=end_year,
        domain=domain,
        jurisdiction=jurisdiction,
        limit=limit,
        profile_id=profile_id,
    )
    return ApiResponse(
        success=True,
        data=comp_data,
        message="Patent competitive landscape indicators computed successfully"
    )


@router.get("/clusters", response_model=ApiResponse[PatentClusteringResponse], status_code=status.HTTP_200_OK)
async def get_patent_clusters(
    start_year: Optional[int] = Query(None, description="Start year filter"),
    end_year: Optional[int] = Query(None, description="End year filter"),
    domain: Optional[str] = Query(None, description="Filter by technology domain"),
    classification: Optional[str] = Query(None, description="Filter by patent classification (IPC/CPC)"),
    assignee: Optional[str] = Query(None, description="Filter by assignee organization"),
    jurisdiction: Optional[str] = Query(None, description="Filter by jurisdiction code"),
    k: Optional[int] = Query(None, ge=1, le=20, description="Optional target number of clusters"),
    my_profile_only: bool = Query(False, description="Scope clustering to authenticated user's portfolio only"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Executes real machine learning clustering (TF-IDF vectorization + K-Means centroid optimization)
    over patent metadata, returning explainable cluster centroids, dominant technical terms, and member proximity.
    """
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    cluster_data = await PatentClusteringService.cluster_patents(
        db=db,
        start_year=start_year,
        end_year=end_year,
        domain=domain,
        classification=classification,
        assignee=assignee,
        jurisdiction=jurisdiction,
        k=k,
        profile_id=profile_id,
    )
    return ApiResponse(
        success=True,
        data=cluster_data,
        message="Machine learning patent clustering computed successfully"
    )


@router.get("/innovation-map", response_model=ApiResponse[InnovationMapResponse], status_code=status.HTTP_200_OK)
async def get_innovation_map(
    start_year: Optional[int] = Query(None, description="Start year filter"),
    end_year: Optional[int] = Query(None, description="End year filter"),
    domain: Optional[str] = Query(None, description="Filter by technology domain"),
    assignee: Optional[str] = Query(None, description="Filter by assignee organization"),
    jurisdiction: Optional[str] = Query(None, description="Filter by jurisdiction code"),
    my_profile_only: bool = Query(False, description="Scope innovation map to authenticated user's portfolio only"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Synthesizes multi-dimensional innovation mappings across domains, assignees, classifications, and hotspots.
    """
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    map_data = await PatentLandscapeService.get_innovation_map(
        db=db,
        start_year=start_year,
        end_year=end_year,
        domain=domain,
        assignee=assignee,
        jurisdiction=jurisdiction,
        profile_id=profile_id,
    )
    return ApiResponse(
        success=True,
        data=map_data,
        message="Patent innovation mapping synthesized successfully"
    )


@router.get("/recommendations", response_model=ApiResponse[PatentRecommendationsResponse], status_code=status.HTTP_200_OK)
async def get_profile_patent_recommendations(
    limit: int = Query(10, ge=1, le=50, description="Max patent recommendations to return"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Module 3 Upstream Integration:
    Delivers explainable patent recommendations tailored to the authenticated researcher's profile
    domains, research interests, and publication track record.
    """
    recs = await PatentLandscapeService.get_profile_recommendations(
        user_id=current_user.id,
        limit=limit,
        db=db
    )
    return ApiResponse(
        success=True,
        data=recs,
        message="Profile-based patent recommendations generated successfully"
    )
