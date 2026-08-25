from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.schemas.patent import (
    PatentCreate,
    PatentUpdate,
    PatentRead,
    PatentListResponse,
    PatentIngestRequest,
)
from app.schemas.common import ApiResponse
from app.services.patent_service import PatentService
from app.services.profile_service import ProfileService

router = APIRouter()


@router.get("", response_model=ApiResponse[PatentListResponse], status_code=status.HTTP_200_OK)
async def list_patents(
    q: Optional[str] = Query(None, description="Search term for title, abstract, patent number, assignee, inventors"),
    domain: Optional[str] = Query(None, description="Filter by technology domain"),
    classification: Optional[str] = Query(None, description="Filter by patent classification (IPC/CPC)"),
    assignee: Optional[str] = Query(None, description="Filter by assignee organization"),
    year: Optional[int] = Query(None, description="Filter by publication or filing year"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Searches and filters indexed patents with pagination."""
    items, total = await PatentService.list_patents(
        search_query=q,
        domain=domain,
        classification=classification,
        assignee=assignee,
        year=year,
        limit=limit,
        offset=offset,
        db=db
    )
    return ApiResponse(
        success=True,
        data=PatentListResponse(
            items=[PatentRead.model_validate(p) for p in items],
            total=total,
            limit=limit,
            offset=offset
        ),
        message="Patents retrieved successfully"
    )


@router.post("", response_model=ApiResponse[PatentRead], status_code=status.HTTP_201_CREATED)
async def create_patent(
    patent_in: PatentCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Creates a new patent record and links it to the requesting researcher's profile."""
    pat = await PatentService.create_patent(
        user_id=current_user.id,
        patent_in=patent_in,
        db=db
    )
    return ApiResponse(
        success=True,
        data=PatentRead.model_validate(pat),
        message="Patent created and linked to profile successfully"
    )


@router.post("/ingest", response_model=ApiResponse[PatentRead], status_code=status.HTTP_200_OK)
async def ingest_patent(
    request: PatentIngestRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Ingests patent metadata from external patent providers and links it to the caller's profile."""
    pat = await PatentService.ingest_patent(
        user_id=current_user.id,
        patent_number=request.patent_number,
        provider_name=request.provider,
        db=db
    )
    return ApiResponse(
        success=True,
        data=PatentRead.model_validate(pat),
        message="Patent ingested and linked to profile successfully"
    )


@router.get("/my", response_model=ApiResponse[PatentListResponse], status_code=status.HTTP_200_OK)
async def get_my_patents(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves all patents linked to the currently authenticated researcher's profile."""
    profile = await ProfileService.get_or_create_profile(user_id=current_user.id, db=db)
    items, total = await PatentService.list_patents(
        profile_id=profile.id,
        limit=limit,
        offset=offset,
        db=db
    )
    return ApiResponse(
        success=True,
        data=PatentListResponse(
            items=[PatentRead.model_validate(p) for p in items],
            total=total,
            limit=limit,
            offset=offset
        ),
        message="User patents retrieved successfully"
    )


@router.get("/{id}", response_model=ApiResponse[PatentRead], status_code=status.HTTP_200_OK)
async def get_patent_by_id(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves details of a specific patent by ID."""
    pat = await PatentService.get_patent(patent_id=id, db=db)
    return ApiResponse(
        success=True,
        data=PatentRead.model_validate(pat),
        message="Patent details retrieved successfully"
    )


@router.put("/{id}", response_model=ApiResponse[PatentRead], status_code=status.HTTP_200_OK)
async def update_patent(
    id: int,
    update_in: PatentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Updates patent details with ownership/admin authorization."""
    updated = await PatentService.update_patent(
        patent_id=id,
        user_id=current_user.id,
        is_admin=(current_user.is_superuser or current_user.role.value == "administrator"),
        update_in=update_in,
        db=db
    )
    return ApiResponse(
        success=True,
        data=PatentRead.model_validate(updated),
        message="Patent updated successfully"
    )


@router.delete("/{id}", response_model=ApiResponse[dict], status_code=status.HTTP_200_OK)
async def delete_patent(
    id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Dissociates or deletes patent with ownership/admin authorization."""
    await PatentService.delete_patent(
        patent_id=id,
        user_id=current_user.id,
        is_admin=(current_user.is_superuser or current_user.role.value == "administrator"),
        db=db
    )
    return ApiResponse(
        success=True,
        data={"deleted": True, "id": id},
        message="Patent removed successfully"
    )
