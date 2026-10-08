import enum
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Boolean, DateTime, Enum, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class NotificationType(str, enum.Enum):
    FUNDING = "FUNDING"
    PATENT = "PATENT"
    TECHNOLOGY = "TECHNOLOGY"
    RESEARCH_TREND = "RESEARCH_TREND"
    COMMERCIALIZATION = "COMMERCIALIZATION"
    PLATFORM = "PLATFORM"


class NotificationPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType, name="notification_type_enum", native_enum=False),
        nullable=False,
        index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    related_module: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    related_record_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    target_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    priority: Mapped[NotificationPriority] = mapped_column(
        Enum(NotificationPriority, name="notification_priority_enum", native_enum=False),
        default=NotificationPriority.MEDIUM,
        nullable=False
    )
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notifications", lazy="selectin")

    __table_args__ = (
        Index("ix_notifications_user_created", "user_id", "created_at"),
        Index("ix_notifications_user_is_read", "user_id", "is_read"),
        Index("ix_notifications_user_type_record", "user_id", "type", "related_record_id"),
    )
