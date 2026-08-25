from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, Query, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_db, get_current_user_optional
from app.models.user import User
from app.models.profile import Profile
from app.schemas.common import ApiResponse
from app.schemas.executive_report import (
    ExecutiveDossierResponse,
    ExecutiveDossierSummary,
    DomainBenchmarkItem,
)
from app.services.executive_report_service import ExecutiveReportService

router = APIRouter()


async def _resolve_profile_id(
    my_profile_only: bool,
    current_user: Optional[User],
    db: AsyncSession
) -> Optional[int]:
    """Helper to resolve profile_id if my_profile_only is requested and user is authenticated."""
    if not my_profile_only or not current_user:
        return None

    stmt = select(Profile.id).where(Profile.user_id == current_user.id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


@router.get(
    "/dossier",
    response_model=ApiResponse[ExecutiveDossierResponse],
    status_code=status.HTTP_200_OK,
    summary="Generate Executive Intelligence Dossier",
    description="Synthesizes scientific publications, patent IP landscape, grant funding, whitespaces, 5-pillar Innovation Scores, and Commercialization Readiness into an executive strategic dossier."
)
async def get_executive_dossier(
    domain: Optional[str] = Query(None, description="Optional technology domain filter"),
    my_profile_only: bool = Query(False, description="Scope evaluation exclusively to authenticated user's portfolio"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    result = await ExecutiveReportService.generate_dossier(
        domain=domain,
        profile_id=profile_id,
        db=db,
    )
    return ApiResponse(
        data=result,
        message=f"Generated executive intelligence dossier for {result.target_name} ({result.report_id})"
    )


@router.get(
    "/summary",
    response_model=ApiResponse[ExecutiveDossierSummary],
    status_code=status.HTTP_200_OK,
    summary="Executive Portfolio Summary & Benchmark Matrix",
    description="Cross-domain portfolio summary of average innovation scores, commercialization readiness, and sector benchmarks."
)
async def get_executive_summary(
    db: AsyncSession = Depends(get_db),
):
    result = await ExecutiveReportService.get_summary(db=db)
    return ApiResponse(
        data=result,
        message="Retrieved executive portfolio benchmark summary"
    )


@router.get(
    "/export/markdown",
    response_class=Response,
    status_code=status.HTTP_200_OK,
    summary="Export Dossier as Markdown Document",
    description="Exports the complete executive intelligence dossier formatted as a GitHub-flavored Markdown report."
)
async def export_dossier_markdown(
    domain: Optional[str] = Query(None, description="Optional technology domain filter"),
    my_profile_only: bool = Query(False, description="Scope evaluation exclusively to authenticated user's portfolio"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    md_content = await ExecutiveReportService.generate_markdown_dossier(
        domain=domain,
        profile_id=profile_id,
        db=db,
    )
    return Response(
        content=md_content,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="Executive_Dossier_{domain or "Portfolio"}.md"'}
    )


@router.get(
    "/export/json",
    response_model=ApiResponse[ExecutiveDossierResponse],
    status_code=status.HTTP_200_OK,
    summary="Export Structured Dossier JSON",
    description="Returns the full structured JSON payload of the synthesized dossier for automated system ingestion."
)
async def export_dossier_json(
    domain: Optional[str] = Query(None, description="Optional technology domain filter"),
    my_profile_only: bool = Query(False, description="Scope evaluation exclusively to authenticated user's portfolio"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    result = await ExecutiveReportService.generate_dossier(
        domain=domain,
        profile_id=profile_id,
        db=db,
    )
    return ApiResponse(
        data=result,
        message="Exported structured dossier JSON payload"
    )
