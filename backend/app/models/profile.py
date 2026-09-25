from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.research_domain import ResearchDomain, ResearchInterest, ProfileKeyword, TechnologyArea
    from app.models.academic_history import AcademicHistory, ResearchHistory
    from app.models.publication import Publication
    from app.models.patent import Patent


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    institution: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    designation: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    orcid_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

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
    user: Mapped["User"] = relationship("User", back_populates="profile")
    
    domains: Mapped[List["ResearchDomain"]] = relationship(
        "ResearchDomain",
        secondary="profile_domains",
        back_populates="profiles",
        lazy="selectin"
    )
    interests: Mapped[List["ResearchInterest"]] = relationship(
        "ResearchInterest",
        back_populates="profile",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    keywords: Mapped[List["ProfileKeyword"]] = relationship(
        "ProfileKeyword",
        back_populates="profile",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    technology_areas: Mapped[List["TechnologyArea"]] = relationship(
        "TechnologyArea",
        back_populates="profile",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    academic_histories: Mapped[List["AcademicHistory"]] = relationship(
        "AcademicHistory",
        back_populates="profile",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    research_histories: Mapped[List["ResearchHistory"]] = relationship(
        "ResearchHistory",
        back_populates="profile",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    publications: Mapped[List["Publication"]] = relationship(
        "Publication",
        secondary="profile_publications",
        back_populates="profiles",
        lazy="selectin"
    )
    patents: Mapped[List["Patent"]] = relationship(
        "Patent",
        secondary="profile_patents",
        back_populates="profiles",
        lazy="selectin"
    )
