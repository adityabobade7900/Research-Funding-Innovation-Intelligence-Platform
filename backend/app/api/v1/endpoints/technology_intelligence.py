from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user_optional
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.technology_intelligence import (
    TechnologyActivityResponse,
    TechnologyGrowthResponse,
    TechnologyCoverageResponse,
    WhitespaceDiscoveryResponse,
    TechnologyIntelligenceSummary,
    TechnologyMaturityResponse,
    AdoptionTrackingResponse,
    EmergingTechnologyResponse,
    CompetitiveTechnologyResponse,
)
from app.services.technology_intelligence_service import TechnologyIntelligenceService
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


@router.get("/summary", response_model=ApiResponse[TechnologyIntelligenceSummary], status_code=status.HTTP_200_OK)
async def get_technology_intelligence_summary(
    start_year: Optional[int] = Query(None, description="Start year filter"),
    end_year: Optional[int] = Query(None, description="End year filter"),
    domain: Optional[str] = Query(None, description="Filter by technology domain"),
    my_profile_only: bool = Query(False, description="Scope to authenticated user's portfolio"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns executive summary of technology intelligence, active fields, growth trajectories, and top whitespace candidates.
    """
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    summary = await TechnologyIntelligenceService.get_summary(
        db=db,
        start_year=start_year,
        end_year=end_year,
        domain=domain,
        profile_id=profile_id,
    )
    return ApiResponse(
        success=True,
        data=summary,
        message="Technology intelligence summary retrieved successfully."
    )


@router.get("/activity", response_model=ApiResponse[TechnologyActivityResponse], status_code=status.HTTP_200_OK)
async def get_technology_activity(
    start_year: Optional[int] = Query(None, description="Start year filter"),
    end_year: Optional[int] = Query(None, description="End year filter"),
    domain: Optional[str] = Query(None, description="Filter by technology domain"),
    technology_area: Optional[str] = Query(None, description="Filter by technology area / subfield"),
    classification: Optional[str] = Query(None, description="Filter by IPC/CPC classification code"),
    keyword: Optional[str] = Query(None, description="Filter by keyword in title/abstract/domain"),
    my_profile_only: bool = Query(False, description="Scope to authenticated user's portfolio"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns structured activity metrics and classification levels (HIGH_ACTIVITY, MEDIUM_ACTIVITY, LOW_ACTIVITY) across technology areas.
    """
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    result = await TechnologyIntelligenceService.get_technology_activity(
        db=db,
        start_year=start_year,
        end_year=end_year,
        domain=domain,
        technology_area=technology_area,
        classification=classification,
        keyword=keyword,
        profile_id=profile_id,
    )
    return ApiResponse(
        success=True,
        data=result,
        message="Technology activity analytics retrieved successfully."
    )


@router.get("/growth", response_model=ApiResponse[TechnologyGrowthResponse], status_code=status.HTTP_200_OK)
async def get_technology_growth(
    start_year: Optional[int] = Query(None, description="Start year filter"),
    end_year: Optional[int] = Query(None, description="End year filter"),
    domain: Optional[str] = Query(None, description="Filter by technology domain"),
    my_profile_only: bool = Query(False, description="Scope to authenticated user's portfolio"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns deterministic technology growth rates, velocity scores, and trajectory classifications.
    """
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    result = await TechnologyIntelligenceService.get_technology_growth(
        db=db,
        start_year=start_year,
        end_year=end_year,
        domain=domain,
        profile_id=profile_id,
    )
    return ApiResponse(
        success=True,
        data=result,
        message="Technology growth analytics retrieved successfully."
    )


@router.get("/coverage", response_model=ApiResponse[TechnologyCoverageResponse], status_code=status.HTTP_200_OK)
async def get_technology_coverage(
    start_year: Optional[int] = Query(None, description="Start year filter"),
    end_year: Optional[int] = Query(None, description="End year filter"),
    domain: Optional[str] = Query(None, description="Filter by technology domain"),
    my_profile_only: bool = Query(False, description="Scope to authenticated user's portfolio"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns multi-signal coverage density scores and coverage levels (HIGH_COVERAGE, MODERATE_COVERAGE, SPARSE_COVERAGE).
    """
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    result = await TechnologyIntelligenceService.get_technology_coverage(
        db=db,
        start_year=start_year,
        end_year=end_year,
        domain=domain,
        profile_id=profile_id,
    )
    return ApiResponse(
        success=True,
        data=result,
        message="Technology coverage analytics retrieved successfully."
    )


@router.get("/whitespace", response_model=ApiResponse[WhitespaceDiscoveryResponse], status_code=status.HTTP_200_OK)
async def detect_potential_whitespaces(
    start_year: Optional[int] = Query(None, description="Start year filter"),
    end_year: Optional[int] = Query(None, description="End year filter"),
    domain: Optional[str] = Query(None, description="Filter by technology domain"),
    min_activity: Optional[int] = Query(None, description="Minimum patent activity filter"),
    whitespace_threshold: float = Query(45.0, description="Minimum composite whitespace score threshold (0-100)"),
    my_profile_only: bool = Query(False, description="Scope to authenticated user's portfolio"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Identifies potential patent whitespace areas and activity gaps using multi-signal heuristics with explainable evidence and confidence ratings.
    """
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    result = await TechnologyIntelligenceService.detect_whitespaces(
        db=db,
        start_year=start_year,
        end_year=end_year,
        domain=domain,
        min_activity=min_activity,
        whitespace_threshold=whitespace_threshold,
        profile_id=profile_id,
    )
    return ApiResponse(
        success=True,
        data=result,
        message="Potential patent whitespaces detected successfully."
    )


@router.get("/maturity", response_model=ApiResponse[TechnologyMaturityResponse], status_code=status.HTTP_200_OK)
async def get_technology_maturity(
    start_year: Optional[int] = Query(None, description="Start year filter"),
    end_year: Optional[int] = Query(None, description="End year filter"),
    domain: Optional[str] = Query(None, description="Filter by technology domain"),
    my_profile_only: bool = Query(False, description="Scope to authenticated user's portfolio"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Evaluates technology maturity across 6 mentor-defined indicators:
    Research Growth (25%), Patent Growth (25%), Research Activity (15%), Patent Activity (15%),
    Organization Participation (10%), and Technology/Application Diversity (10%).
    Returns stage classification (EMERGING, DEVELOPING, MATURE, DECLINING) and explainable justification.
    """
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    result = await TechnologyIntelligenceService.get_technology_maturity(
        db=db,
        start_year=start_year,
        end_year=end_year,
        domain=domain,
        profile_id=profile_id,
    )
    return ApiResponse(
        success=True,
        data=result,
        message="Technology maturity intelligence retrieved successfully."
    )


@router.get("/adoption", response_model=ApiResponse[AdoptionTrackingResponse], status_code=status.HTTP_200_OK)
async def get_technology_adoption(
    start_year: Optional[int] = Query(None, description="Start year filter"),
    end_year: Optional[int] = Query(None, description="End year filter"),
    domain: Optional[str] = Query(None, description="Filter by technology domain"),
    my_profile_only: bool = Query(False, description="Scope to authenticated user's portfolio"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Tracks technology adoption status, strictly isolating commercial/market deployment telemetry
    from scientific research and patent disclosures.
    """
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    result = await TechnologyIntelligenceService.get_technology_adoption(
        db=db,
        start_year=start_year,
        end_year=end_year,
        domain=domain,
        profile_id=profile_id,
    )
    return ApiResponse(
        success=True,
        data=result,
        message="Technology adoption tracking retrieved successfully."
    )


@router.get("/emerging", response_model=ApiResponse[EmergingTechnologyResponse], status_code=status.HTTP_200_OK)
async def get_emerging_technologies(
    start_year: Optional[int] = Query(None, description="Start year filter"),
    end_year: Optional[int] = Query(None, description="End year filter"),
    domain: Optional[str] = Query(None, description="Filter by technology domain"),
    my_profile_only: bool = Query(False, description="Scope to authenticated user's portfolio"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Identifies and ranks fast-moving emerging technologies driven by publication acceleration,
    patent velocity, and organizational momentum.
    """
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    result = await TechnologyIntelligenceService.get_emerging_technologies(
        db=db,
        start_year=start_year,
        end_year=end_year,
        domain=domain,
        profile_id=profile_id,
    )
    return ApiResponse(
        success=True,
        data=result,
        message="Emerging technology candidates retrieved successfully."
    )


@router.get("/competitive", response_model=ApiResponse[CompetitiveTechnologyResponse], status_code=status.HTTP_200_OK)
async def get_competitive_technology_monitoring(
    start_year: Optional[int] = Query(None, description="Start year filter"),
    end_year: Optional[int] = Query(None, description="End year filter"),
    domain: Optional[str] = Query(None, description="Filter by technology domain"),
    my_profile_only: bool = Query(False, description="Scope to authenticated user's portfolio"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Monitors competitive concentration (HHI), top assignees, and jurisdiction coverage per technology domain.
    """
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    result = await TechnologyIntelligenceService.get_competitive_technology_monitoring(
        db=db,
        start_year=start_year,
        end_year=end_year,
        domain=domain,
        profile_id=profile_id,
    )
    return ApiResponse(
        success=True,
        data=result,
        message="Competitive technology monitoring retrieved successfully."
    )
