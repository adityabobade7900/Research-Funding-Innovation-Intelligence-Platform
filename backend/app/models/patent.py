from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.profile import Profile


# Association Table between Profile and Patent
profile_patents = Table(
    "profile_patents",
    Base.metadata,
    Column("profile_id", Integer, ForeignKey("profiles.id", ondelete="CASCADE"), primary_key=True),
    Column("patent_id", Integer, ForeignKey("patents.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "created_at",
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    ),
)


class Patent(Base):
    __tablename__ = "patents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    patent_number: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(500), index=True, nullable=False)
    abstract: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    assignee: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    inventors: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    filing_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    publication_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    patent_classification: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    technology_domain: Mapped[Optional[str]] = mapped_column(String(150), index=True, nullable=True)
    citation_count: Mapped[int] = mapped_column(Integer, default=0, index=True, nullable=False)
    source: Mapped[str] = mapped_column(String(50), default="manual", index=True, nullable=False)
    external_id: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    profiles: Mapped[List["Profile"]] = relationship(
        "Profile",
        secondary=profile_patents,
        back_populates="patents",
        lazy="selectin"
    )
