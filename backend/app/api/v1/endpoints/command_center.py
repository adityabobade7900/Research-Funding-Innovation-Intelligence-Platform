from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user_optional
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.command_center import (
    CommandCenterOverviewResponse,
    ActivityFeedResponse,
)
from app.services.command_center_service import CommandCenterService

router = APIRouter()


@router.get(
    "/overview",
    response_model=ApiResponse[CommandCenterOverviewResponse],
    status_code=status.HTTP_200_OK,
    summary="Command Center Unified Overview",
    description="Returns cross-module strategic rollups, role-contextual KPI cards, whitespace alerts, and grant deadlines."
)
async def get_command_center_overview(
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    result = await CommandCenterService.get_overview(user=current_user, db=db)
    return ApiResponse(
        data=result,
        message=f"Retrieved unified command center intelligence for {result.user_name} ({result.user_role.value})"
    )


@router.get(
    "/activity-feed",
    response_model=ApiResponse[ActivityFeedResponse],
    status_code=status.HTTP_200_OK,
    summary="Cross-Module Activity Feed",
    description="Returns real-time activity updates across publications, patent disclosures, and grant funding pipelines."
)
async def get_activity_feed(
    limit: int = Query(20, ge=1, le=100, description="Items limit"),
    db: AsyncSession = Depends(get_db),
):
    result = await CommandCenterService.get_activity_feed(limit=limit, db=db)
    return ApiResponse(
        data=result,
        message=f"Retrieved {len(result.items)} activity updates"
    )
