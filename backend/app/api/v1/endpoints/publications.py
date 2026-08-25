from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.schemas.publication import (
    PublicationCreate,
    PublicationUpdate,
    PublicationRead,
    PublicationListResponse,
    PublicationIngestRequest,
    PublicationIngestResponse,
)
from app.schemas.common import ApiResponse
from app.services.publication_service import PublicationService
from app.services.profile_service import ProfileService
from app.services.ingest_service import IngestService

router = APIRouter()


@router.get("", response_model=ApiResponse[PublicationListResponse], status_code=status.HTTP_200_OK)
async def list_publications(
    q: Optional[str] = Query(None, description="Search term for title, abstract, authors, venue"),
    domain: Optional[str] = Query(None, description="Filter by primary research domain"),
    venue: Optional[str] = Query(None, description="Filter by publication venue or journal"),
    year: Optional[int] = Query(None, description="Filter by publication year"),
    author: Optional[str] = Query(None, description="Filter by author name"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Searches and filters indexed publications with pagination."""
    items, total = await PublicationService.list_publications(
        search_query=q,
        domain=domain,
        venue=venue,
        year=year,
        author=author,
        limit=limit,
        offset=offset,
        db=db
    )
    return ApiResponse(
        success=True,
        data=PublicationListResponse(
            items=[PublicationRead.model_validate(p) for p in items],
            total=total,
            limit=limit,
            offset=offset
        ),
        message="Publications retrieved successfully"
    )


@router.post("", response_model=ApiResponse[PublicationRead], status_code=status.HTTP_201_CREATED)
async def create_publication(
    pub_in: PublicationCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Creates a new publication or links existing record, associating it with the current user's profile."""
    pub = await PublicationService.create_publication(
        user_id=current_user.id,
        pub_in=pub_in,
        db=db
    )
    return ApiResponse(
        success=True,
        data=PublicationRead.model_validate(pub),
        message="Publication created and associated with profile successfully"
    )


@router.post("/ingest", response_model=ApiResponse[PublicationIngestResponse], status_code=status.HTTP_200_OK)
async def ingest_publications(
    request: PublicationIngestRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Executes controlled ingestion from upstream research providers (OpenAlex, Crossref, Semantic Scholar, Mock)
    and associates ingested publications with the authenticated researcher's profile.
    """
    pubs, message = await IngestService.ingest_publications(
        user_id=current_user.id,
        request=request,
        db=db
    )
    return ApiResponse(
        success=True,
        data=PublicationIngestResponse(
            ingested_count=len(pubs),
            publications=[PublicationRead.model_validate(p) for p in pubs],
            message=message
        ),
        message=message
    )


@router.get("/my", response_model=ApiResponse[PublicationListResponse], status_code=status.HTTP_200_OK)
async def get_my_publications(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves all publications linked to the currently authenticated user's profile."""
    profile = await ProfileService.get_or_create_profile(user_id=current_user.id, db=db)
    items, total = await PublicationService.list_publications(
        profile_id=profile.id,
        limit=limit,
        offset=offset,
        db=db
    )
    return ApiResponse(
        success=True,
        data=PublicationListResponse(
            items=[PublicationRead.model_validate(p) for p in items],
            total=total,
            limit=limit,
            offset=offset
        ),
        message="User publications retrieved successfully"
    )


@router.get("/{id}", response_model=ApiResponse[PublicationRead], status_code=status.HTTP_200_OK)
async def get_publication_by_id(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves details of a specific publication by ID."""
    pub = await PublicationService.get_publication(pub_id=id, db=db)
    return ApiResponse(
        success=True,
        data=PublicationRead.model_validate(pub),
        message="Publication details retrieved successfully"
    )


@router.put("/{id}", response_model=ApiResponse[PublicationRead], status_code=status.HTTP_200_OK)
async def update_publication(
    id: int,
    update_in: PublicationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Updates a publication with strict ownership and authorization checks."""
    updated = await PublicationService.update_publication(
        pub_id=id,
        user_id=current_user.id,
        is_admin=(current_user.is_superuser or current_user.role.value == "administrator"),
        update_in=update_in,
        db=db
    )
    return ApiResponse(
        success=True,
        data=PublicationRead.model_validate(updated),
        message="Publication updated successfully"
    )


@router.delete("/{id}", response_model=ApiResponse[dict], status_code=status.HTTP_200_OK)
async def delete_publication(
    id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Dissociates or deletes a publication with ownership enforcement."""
    await PublicationService.delete_publication(
        pub_id=id,
        user_id=current_user.id,
        is_admin=(current_user.is_superuser or current_user.role.value == "administrator"),
        db=db
    )
    return ApiResponse(
        success=True,
        data={"deleted": True, "id": id},
        message="Publication removed successfully"
    )
