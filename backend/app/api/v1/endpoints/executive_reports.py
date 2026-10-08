from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, Query, status, Response, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_db, get_current_user_optional, get_current_active_user
from app.models.user import User
from app.models.profile import Profile
from app.schemas.common import ApiResponse
from app.schemas.executive_report import (
    ExecutiveDossierResponse,
    ExecutiveDossierSummary,
    DomainBenchmarkItem,
)
from app.schemas.report_export import (
    ReportType,
    ReportFilterParams,
    ReportTypesResponse,
    ReportPreviewResponse,
)
from app.services.executive_report_service import ExecutiveReportService
from app.services.report_export_service import ReportExportService

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


# =========================================================================
# MODULE 11: REPORTS & EXPORT SYSTEM ENDPOINTS
# =========================================================================

@router.get(
    "/types",
    response_model=ApiResponse[ReportTypesResponse],
    status_code=status.HTTP_200_OK,
    summary="List Supported Report Types",
    description="Returns metadata and supported filters for all platform report categories (Funding, Patent, Research Trend, Innovation Intelligence, Commercialization)."
)
async def get_report_types():
    """Returns the official catalog of supported report types and their filter parameters."""
    catalog = ReportExportService.get_supported_report_types()
    return ApiResponse(
        data=catalog,
        message="Supported report types retrieved successfully"
    )


@router.post(
    "/preview",
    response_model=ApiResponse[ReportPreviewResponse],
    status_code=status.HTTP_200_OK,
    summary="Preview Filtered Report Data",
    description="Processes backend filters and returns structured preview metrics, narrative summary, and table records before export."
)
async def preview_report(
    filters: ReportFilterParams = Body(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Generates real-time report data and summary based on applied filters."""
    preview_data = await ReportExportService.gather_report_data(
        filters=filters,
        user=current_user,
        db=db,
    )
    return ApiResponse(
        data=preview_data,
        message=f"Report preview generated successfully for {filters.report_type.value}"
    )


@router.post(
    "/export/pdf",
    response_class=Response,
    status_code=status.HTTP_200_OK,
    summary="Export Report as Formatted PDF Document",
    description="Generates a professional, print-ready PDF with cover, executive summary, factor breakdown, formatted tables, and governance notice."
)
async def export_report_pdf(
    filters: ReportFilterParams = Body(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Generates and downloads a formatted PDF report using ReportLab."""
    report_data = await ReportExportService.gather_report_data(
        filters=filters,
        user=current_user,
        db=db,
    )
    pdf_bytes = ReportExportService.generate_pdf(report_data=report_data)

    safe_title = filters.report_type.value.lower()
    filename = f"Intelligence_Report_{safe_title}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "application/pdf"
        }
    )


@router.post(
    "/export/excel",
    response_class=Response,
    status_code=status.HTTP_200_OK,
    summary="Export Report as Structured Excel (.xlsx) Workbook",
    description="Generates a multi-sheet, structured Excel workbook using openpyxl with styles, formatted numbers, dates, and dedicated analysis sheets."
)
async def export_report_excel(
    filters: ReportFilterParams = Body(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Generates and downloads a structured .xlsx Excel workbook using openpyxl."""
    report_data = await ReportExportService.gather_report_data(
        filters=filters,
        user=current_user,
        db=db,
    )
    excel_bytes = ReportExportService.generate_excel(report_data=report_data)

    safe_title = filters.report_type.value.lower()
    filename = f"Intelligence_Report_{safe_title}.xlsx"

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        }
    )


# =========================================================================
# PRESERVED EXISTING EXECUTIVE DOSSIER ENDPOINTS (BACKWARD COMPATIBLE)
# =========================================================================

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
