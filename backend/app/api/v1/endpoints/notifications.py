from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_active_user
from app.core.exceptions import EntityNotFoundException
from app.models.user import User
from app.models.notification import NotificationType
from app.schemas.notification import (
    NotificationRead,
    NotificationListResponse,
    NotificationUnreadResponse,
    NotificationMarkReadResponse,
    NotificationMarkAllReadResponse,
    NotificationScanResult,
)
from app.schemas.common import ApiResponse
from app.services.notification_service import NotificationService

router = APIRouter()


@router.get("", response_model=ApiResponse[NotificationListResponse], status_code=status.HTTP_200_OK)
async def list_notifications(
    type_filter: Optional[NotificationType] = Query(None, alias="type", description="Filter by notification type"),
    is_read: Optional[bool] = Query(None, description="Filter by read/unread status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves paginated notifications for the authenticated user.
    Enforces user isolation and supports filtering by category and read status.
    """
    items, total, unread_count = await NotificationService.list_notifications(
        user_id=current_user.id,
        notification_type=type_filter,
        is_read=is_read,
        limit=limit,
        offset=offset,
        db=db
    )
    return ApiResponse(
        success=True,
        data=NotificationListResponse(
            items=[NotificationRead.model_validate(n) for n in items],
            total=total,
            unread_count=unread_count
        ),
        message="Notifications retrieved successfully"
    )


@router.get("/unread", response_model=ApiResponse[NotificationUnreadResponse], status_code=status.HTTP_200_OK)
async def get_unread_count(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns the current count of unread notifications for the authenticated user.
    """
    count = await NotificationService.get_unread_count(user_id=current_user.id, db=db)
    return ApiResponse(
        success=True,
        data=NotificationUnreadResponse(unread_count=count),
        message="Unread notification count retrieved successfully"
    )


@router.patch("/read-all", response_model=ApiResponse[NotificationMarkAllReadResponse], status_code=status.HTTP_200_OK)
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Marks all notifications belonging to the authenticated user as read.
    """
    count = await NotificationService.mark_all_as_read(user_id=current_user.id, db=db)
    return ApiResponse(
        success=True,
        data=NotificationMarkAllReadResponse(
            updated_count=count,
            message=f"Marked {count} notification(s) as read"
        ),
        message=f"Marked {count} notification(s) as read"
    )


@router.post("/scan", response_model=ApiResponse[NotificationScanResult], status_code=status.HTTP_200_OK)
async def scan_and_generate_alerts(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Proactively scans platform intelligence modules (M3, M4, M5, M6, M8, Platform)
    and generates relevant, deduplicated notifications for the authenticated user.
    """
    alerts = await NotificationService.generate_alerts_for_user(user=current_user, db=db)
    return ApiResponse(
        success=True,
        data=NotificationScanResult(
            scanned_modules=["funding", "patents", "technology", "research", "commercialization", "platform"],
            generated_count=len(alerts),
            notifications=[NotificationRead.model_validate(a) for a in alerts]
        ),
        message=f"Alert scan completed. Generated {len(alerts)} new notification(s)."
    )


@router.get("/{id}", response_model=ApiResponse[NotificationRead], status_code=status.HTTP_200_OK)
async def get_notification(
    id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves a single notification by ID.
    Strictly enforces current user ownership to prevent IDOR vulnerabilities.
    """
    notification = await NotificationService.get_notification(
        notification_id=id,
        user_id=current_user.id,
        db=db
    )
    if not notification:
        raise EntityNotFoundException(message=f"Notification with id {id} not found")

    return ApiResponse(
        success=True,
        data=NotificationRead.model_validate(notification),
        message="Notification retrieved successfully"
    )


@router.patch("/{id}/read", response_model=ApiResponse[NotificationMarkReadResponse], status_code=status.HTTP_200_OK)
async def mark_notification_as_read(
    id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Marks a specific notification as read.
    Enforces user ownership to prevent unauthorized state modifications.
    """
    notification = await NotificationService.mark_as_read(
        notification_id=id,
        user_id=current_user.id,
        db=db
    )
    if not notification:
        raise EntityNotFoundException(message=f"Notification with id {id} not found")

    return ApiResponse(
        success=True,
        data=NotificationMarkReadResponse(
            id=notification.id,
            is_read=notification.is_read
        ),
        message="Notification marked as read successfully"
    )
