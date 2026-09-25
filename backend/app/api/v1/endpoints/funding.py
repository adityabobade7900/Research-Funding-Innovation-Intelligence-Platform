from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_active_user, get_current_user_optional
from app.models.user import User
from app.schemas.funding import (
    FundingOpportunityCreate,
    FundingOpportunityUpdate,
    FundingOpportunityRead,
    FundingOpportunityListResponse,
    FundingIngestRequest,
    FundingIngestResponse,
    EligibilityEvaluationResult,
    FundingRecommendationResponse,
    SaveFundingRequest,
    SavedFundingItem,
    SavedFundingListResponse,
    SaveFundingToggleResponse,
)
from app.schemas.common import ApiResponse
from app.services.funding_service import FundingService
from app.services.funding_ingest_service import FundingIngestService
from app.services.profile_service import ProfileService
from app.services.eligibility_matcher import EligibilityMatcher
from app.services.funding_recommendation_service import FundingRecommendationService
from app.services.saved_funding_service import SavedFundingService

router = APIRouter()


@router.get("", response_model=ApiResponse[FundingOpportunityListResponse], status_code=status.HTTP_200_OK)
async def list_funding_opportunities(
    q: Optional[str] = Query(None, description="Search term for title, description, agency, program"),
    agency: Optional[str] = Query(None, description="Filter by funding agency (e.g. NSF, NIH, DARPA)"),
    domain: Optional[str] = Query(None, description="Filter by eligible research domain"),
    opportunity_type: Optional[str] = Query(None, description="Filter by opportunity type (e.g. Grant, Fellowship)"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (open, upcoming, closed, rolling)"),
    min_amount: Optional[float] = Query(None, ge=0, description="Minimum funding amount"),
    max_amount: Optional[float] = Query(None, ge=0, description="Maximum funding amount"),
    deadline_after: Optional[datetime] = Query(None, description="Filter opportunities with deadline after this date"),
    deadline_before: Optional[datetime] = Query(None, description="Filter opportunities with deadline before this date"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Searches and filters funding opportunities with multi-criteria pagination."""
    items, total = await FundingService.list_opportunities(
        search_query=q,
        agency=agency,
        domain=domain,
        opportunity_type=opportunity_type,
        status=status_filter,
        min_amount=min_amount,
        max_amount=max_amount,
        deadline_after=deadline_after,
        deadline_before=deadline_before,
        limit=limit,
        offset=offset,
        db=db
    )

    saved_ids = set()
    if current_user:
        saved_ids = await SavedFundingService.get_saved_ids_for_user(user_id=current_user.id, db=db)

    results = []
    for item in items:
        opp_read = FundingOpportunityRead.model_validate(item)
        if current_user:
            opp_read.is_saved = (item.id in saved_ids)
        results.append(opp_read)

    return ApiResponse(
        success=True,
        data=FundingOpportunityListResponse(
            items=results,
            total=total,
            limit=limit,
            offset=offset
        ),
        message="Funding opportunities retrieved successfully"
    )


@router.post("", response_model=ApiResponse[FundingOpportunityRead], status_code=status.HTTP_201_CREATED)
async def create_funding_opportunity(
    opp_in: FundingOpportunityCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Creates a new funding opportunity record with domain taxonomy and keyword tags."""
    opp = await FundingService.create_opportunity(
        user_id=current_user.id,
        opp_in=opp_in,
        db=db
    )
    return ApiResponse(
        success=True,
        data=FundingOpportunityRead.model_validate(opp),
        message="Funding opportunity indexed successfully"
    )


@router.post("/ingest", response_model=ApiResponse[FundingIngestResponse], status_code=status.HTTP_200_OK)
async def ingest_funding_opportunities(
    request: FundingIngestRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Controlled ingestion of funding opportunities from external registries (Mock, Grants.gov, NSF, Horizon Europe),
    validating, deduplicating, and persisting into the intelligence platform repository.
    """
    result = await FundingIngestService.ingest_opportunities(
        user_id=current_user.id,
        request=request,
        db=db
    )
    return ApiResponse(
        success=True,
        data=result,
        message=result.message
    )


@router.get("/recommendations", response_model=ApiResponse[FundingRecommendationResponse], status_code=status.HTTP_200_OK)
async def get_funding_recommendations(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of recommendations to return"),
    minimum_score: float = Query(0.0, ge=0.0, le=100.0, description="Minimum compatibility/recommendation score filter"),
    domain: Optional[str] = Query(None, description="Optional domain filter"),
    opportunity_type: Optional[str] = Query(None, description="Optional opportunity type filter"),
    status_filter: Optional[str] = Query("open", alias="status", description="Status filter (open, upcoming, rolling)"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generates personalized, ranked, and explainable funding recommendations for the authenticated researcher.
    Evaluates candidate opportunities against the researcher's extended profile using deterministic eligibility gating,
    domain alignment, keyword density, deadline suitability, and funding scale.
    """
    recommendations = await FundingRecommendationService.get_recommendations(
        user_id=current_user.id,
        limit=limit,
        minimum_score=minimum_score,
        domain=domain,
        opportunity_type=opportunity_type,
        status_filter=status_filter,
        db=db
    )
    return ApiResponse(
        success=True,
        data=recommendations,
        message=f"Found {len(recommendations.items)} personalized funding recommendation(s)"
    )


@router.get("/saved", response_model=ApiResponse[SavedFundingListResponse], status_code=status.HTTP_200_OK)
async def list_saved_funding_opportunities(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Lists funding opportunities saved to the authenticated researcher's watchlist."""
    items, total = await SavedFundingService.list_saved_opportunities(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
        db=db
    )
    saved_items = []
    for it in items:
        item_schema = SavedFundingItem.model_validate(it)
        item_schema.opportunity.is_saved = True
        saved_items.append(item_schema)

    return ApiResponse(
        success=True,
        data=SavedFundingListResponse(
            items=saved_items,
            total=total,
            limit=limit,
            offset=offset
        ),
        message=f"Retrieved {len(saved_items)} saved funding opportunit(ies)"
    )


@router.post("/{id}/save", response_model=ApiResponse[SaveFundingToggleResponse], status_code=status.HTTP_200_OK)
async def save_funding_opportunity(
    id: int,
    request: Optional[SaveFundingRequest] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Saves a funding opportunity to the authenticated researcher's watchlist."""
    notes = request.notes if request else None
    saved_record, created = await SavedFundingService.save_opportunity(
        user_id=current_user.id,
        opp_id=id,
        notes=notes,
        db=db
    )
    item_schema = SavedFundingItem.model_validate(saved_record)
    item_schema.opportunity.is_saved = True
    action_msg = "added to your saved watchlist" if created else "already in your saved watchlist (updated notes)"
    return ApiResponse(
        success=True,
        data=SaveFundingToggleResponse(
            saved=True,
            funding_opportunity_id=id,
            message=f"Opportunity #{id} {action_msg}",
            item=item_schema
        ),
        message=f"Opportunity #{id} {action_msg}"
    )


@router.delete("/{id}/save", response_model=ApiResponse[SaveFundingToggleResponse], status_code=status.HTTP_200_OK)
async def unsave_funding_opportunity(
    id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Removes a funding opportunity from the authenticated researcher's watchlist."""
    await SavedFundingService.unsave_opportunity(
        user_id=current_user.id,
        opp_id=id,
        db=db
    )
    return ApiResponse(
        success=True,
        data=SaveFundingToggleResponse(
            saved=False,
            funding_opportunity_id=id,
            message=f"Opportunity #{id} removed from your saved watchlist",
            item=None
        ),
        message=f"Opportunity #{id} removed from your saved watchlist"
    )


@router.get("/{id}/eligibility", response_model=ApiResponse[EligibilityEvaluationResult], status_code=status.HTTP_200_OK)
async def check_funding_eligibility(
    id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Evaluates the authenticated researcher's profile against a specific funding opportunity
    using deterministic, rule-based compatibility and returns an explainable evaluation.
    """
    profile = await ProfileService.get_extended_profile(user_id=current_user.id, db=db)
    opp = await FundingService.get_opportunity(opp_id=id, db=db)
    evaluation = EligibilityMatcher.evaluate(profile=profile, opportunity=opp)
    return ApiResponse(
        success=True,
        data=evaluation,
        message="Eligibility evaluation completed successfully"
    )


@router.get("/{id}", response_model=ApiResponse[FundingOpportunityRead], status_code=status.HTTP_200_OK)
async def get_funding_opportunity_by_id(
    id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves details of a specific funding opportunity by ID."""
    opp = await FundingService.get_opportunity(opp_id=id, db=db)
    opp_read = FundingOpportunityRead.model_validate(opp)
    if current_user:
        saved_ids = await SavedFundingService.get_saved_ids_for_user(user_id=current_user.id, db=db)
        opp_read.is_saved = (opp.id in saved_ids)
    return ApiResponse(
        success=True,
        data=opp_read,
        message="Funding opportunity details retrieved successfully"
    )


@router.put("/{id}", response_model=ApiResponse[FundingOpportunityRead], status_code=status.HTTP_200_OK)
async def update_funding_opportunity(
    id: int,
    update_in: FundingOpportunityUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Updates funding opportunity details with creator/admin authorization."""
    updated = await FundingService.update_opportunity(
        opp_id=id,
        user_id=current_user.id,
        is_admin=(current_user.is_superuser or current_user.role.value == "administrator"),
        update_in=update_in,
        db=db
    )
    return ApiResponse(
        success=True,
        data=FundingOpportunityRead.model_validate(updated),
        message="Funding opportunity updated successfully"
    )


@router.delete("/{id}", response_model=ApiResponse[dict], status_code=status.HTTP_200_OK)
async def delete_funding_opportunity(
    id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Deletes a funding opportunity with creator/admin authorization."""
    await FundingService.delete_opportunity(
        opp_id=id,
        user_id=current_user.id,
        is_admin=(current_user.is_superuser or current_user.role.value == "administrator"),
        db=db
    )
    return ApiResponse(
        success=True,
        data={"deleted": True, "id": id},
        message="Funding opportunity removed successfully"
    )
