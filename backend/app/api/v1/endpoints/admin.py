from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, require_roles
from app.models.user import User, UserRole
from app.schemas.common import ApiResponse
from app.schemas.admin import (
    AdminUserItem,
    AdminUserListResponse,
    UserRoleUpdateRequest,
    UserStatusUpdateRequest,
    PipelineTelemetryResponse,
    SystemOverviewResponse,
    AuditLogListResponse,
)
from app.services.admin_service import AdminService

router = APIRouter()


@router.get(
    "/users",
    response_model=ApiResponse[AdminUserListResponse],
    status_code=status.HTTP_200_OK,
    summary="List Platform Users",
    description="Returns all platform users with role, status, institution, and linked asset counts (Administrator only)."
)
async def list_users(
    q: Optional[str] = Query(None, description="Search query matching email or name"),
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_admin: User = Depends(require_roles([UserRole.ADMINISTRATOR])),
    db: AsyncSession = Depends(get_db),
):
    result = await AdminService.list_users(
        query=q,
        role=role,
        is_active=is_active,
        page=page,
        size=size,
        db=db,
    )
    return ApiResponse(
        data=result,
        message=f"Retrieved {len(result.items)} users (Total: {result.total})"
    )


@router.get(
    "/users/{user_id}",
    response_model=ApiResponse[AdminUserItem],
    status_code=status.HTTP_200_OK,
    summary="Get User Details",
    description="Returns detailed user information and linked profile data."
)
async def get_user_details(
    user_id: int = Path(..., ge=1, description="User ID"),
    current_admin: User = Depends(require_roles([UserRole.ADMINISTRATOR])),
    db: AsyncSession = Depends(get_db),
):
    user = await AdminService.get_user_details(user_id=user_id, db=db)
    return ApiResponse(
        data=user,
        message=f"Retrieved details for user {user.email}"
    )


@router.put(
    "/users/{user_id}/role",
    response_model=ApiResponse[AdminUserItem],
    status_code=status.HTTP_200_OK,
    summary="Update User Role",
    description="Assigns a new platform role to the user (Administrator only)."
)
async def update_user_role(
    payload: UserRoleUpdateRequest,
    user_id: int = Path(..., ge=1, description="User ID"),
    current_admin: User = Depends(require_roles([UserRole.ADMINISTRATOR])),
    db: AsyncSession = Depends(get_db),
):
    user = await AdminService.update_user_role(
        user_id=user_id,
        new_role=payload.role,
        actor_email=current_admin.email,
        db=db,
    )
    return ApiResponse(
        data=user,
        message=f"Updated role for user {user.email} to {user.role.value}"
    )


@router.put(
    "/users/{user_id}/status",
    response_model=ApiResponse[AdminUserItem],
    status_code=status.HTTP_200_OK,
    summary="Update User Active Status",
    description="Activates or deactivates a user account (Administrator only)."
)
async def update_user_status(
    payload: UserStatusUpdateRequest,
    user_id: int = Path(..., ge=1, description="User ID"),
    current_admin: User = Depends(require_roles([UserRole.ADMINISTRATOR])),
    db: AsyncSession = Depends(get_db),
):
    user = await AdminService.update_user_status(
        user_id=user_id,
        is_active=payload.is_active,
        actor_email=current_admin.email,
        db=db,
    )
    status_str = "activated" if user.is_active else "deactivated"
    return ApiResponse(
        data=user,
        message=f"Successfully {status_str} account for {user.email}"
    )


@router.get(
    "/telemetry/pipelines",
    response_model=ApiResponse[PipelineTelemetryResponse],
    status_code=status.HTTP_200_OK,
    summary="Pipeline Ingestion Telemetry",
    description="Monitors live provider connectors, response latencies, sync counters, and health states (Administrator only)."
)
async def get_pipeline_telemetry(
    current_admin: User = Depends(require_roles([UserRole.ADMINISTRATOR])),
    db: AsyncSession = Depends(get_db),
):
    result = await AdminService.get_pipeline_telemetry(db=db)
    return ApiResponse(
        data=result,
        message=f"Retrieved telemetry for {result.total_pipelines} data ingestion pipelines"
    )


@router.get(
    "/system/overview",
    response_model=ApiResponse[SystemOverviewResponse],
    status_code=status.HTTP_200_OK,
    summary="Platform Health & System Overview",
    description="Provides platform entity capacity, total grant capital, database latency, and system health status."
)
async def get_system_overview(
    current_admin: User = Depends(require_roles([UserRole.ADMINISTRATOR])),
    db: AsyncSession = Depends(get_db),
):
    result = await AdminService.get_system_overview(db=db)
    return ApiResponse(
        data=result,
        message="Retrieved platform system health and capacity overview"
    )


@router.get(
    "/audit-logs",
    response_model=ApiResponse[AuditLogListResponse],
    status_code=status.HTTP_200_OK,
    summary="Security & Administrative Audit Logs",
    description="Returns filterable security, RBAC, and ingestion audit events (Administrator only)."
)
async def get_audit_logs(
    category: Optional[str] = Query(None, description="Optional action category (AUTH, USER_MGMT, RBAC, INGESTION)"),
    limit: int = Query(50, ge=1, le=200, description="Items limit"),
    offset: int = Query(0, ge=0, description="Offset"),
    current_admin: User = Depends(require_roles([UserRole.ADMINISTRATOR])),
    db: AsyncSession = Depends(get_db),
):
    result = await AdminService.get_audit_logs(
        category=category,
        limit=limit,
        offset=offset,
        db=db,
    )
    return ApiResponse(
        data=result,
        message=f"Retrieved {len(result.items)} audit log records"
    )
