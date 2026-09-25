from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.schemas.research_profile import (
    ExtendedProfileRead,
    ExtendedProfileUpdate,
    ResearchDomainRead
)
from app.schemas.common import ApiResponse
from app.services.profile_service import ProfileService

router = APIRouter()


@router.get("/domains", response_model=ApiResponse[List[ResearchDomainRead]], status_code=status.HTTP_200_OK)
async def get_research_domains(db: AsyncSession = Depends(get_db)):
    """Retrieves all standard research taxonomy domains."""
    domains = await ProfileService.get_all_domains(db)
    return ApiResponse(
        success=True,
        data=[ResearchDomainRead.model_validate(d) for d in domains],
        message="Research domains retrieved successfully"
    )


@router.get("/me", response_model=ApiResponse[ExtendedProfileRead], status_code=status.HTTP_200_OK)
async def get_my_extended_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves the full extended research profile for the currently authenticated user."""
    profile = await ProfileService.get_extended_profile(user_id=current_user.id, db=db)
    return ApiResponse(
        success=True,
        data=ExtendedProfileRead.model_validate(profile),
        message="Extended profile retrieved successfully"
    )


@router.put("/me", response_model=ApiResponse[ExtendedProfileRead], status_code=status.HTTP_200_OK)
async def update_my_extended_profile(
    update_in: ExtendedProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Updates the extended research profile for the currently authenticated user with ownership enforcement."""
    updated_profile = await ProfileService.update_extended_profile(
        user_id=current_user.id,
        update_in=update_in,
        db=db
    )
    return ApiResponse(
        success=True,
        data=ExtendedProfileRead.model_validate(updated_profile),
        message="Extended research profile updated successfully"
    )


@router.get("/{user_id}", response_model=ApiResponse[ExtendedProfileRead], status_code=status.HTTP_200_OK)
async def get_user_profile_by_id(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves the extended profile of a specific user by their ID."""
    profile = await ProfileService.get_extended_profile(user_id=user_id, db=db)
    return ApiResponse(
        success=True,
        data=ExtendedProfileRead.model_validate(profile),
        message="User profile retrieved successfully"
    )
