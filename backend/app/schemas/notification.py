from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.notification import NotificationType, NotificationPriority


class NotificationCreate(BaseModel):
    type: NotificationType
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    related_module: Optional[str] = Field(None, max_length=50)
    related_record_id: Optional[str] = Field(None, max_length=100)
    target_url: Optional[str] = Field(None, max_length=255)
    priority: NotificationPriority = NotificationPriority.MEDIUM


class NotificationRead(BaseModel):
    id: int
    user_id: int
    type: NotificationType
    title: str
    message: str
    related_module: Optional[str] = None
    related_record_id: Optional[str] = None
    target_url: Optional[str] = None
    priority: NotificationPriority
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    items: List[NotificationRead]
    total: int
    unread_count: int


class NotificationUnreadResponse(BaseModel):
    unread_count: int


class NotificationMarkReadResponse(BaseModel):
    id: int
    is_read: bool


class NotificationMarkAllReadResponse(BaseModel):
    updated_count: int
    message: str


class NotificationScanResult(BaseModel):
    scanned_modules: List[str]
    generated_count: int
    notifications: List[NotificationRead]
