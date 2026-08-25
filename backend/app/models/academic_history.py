from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.profile import Profile


class AcademicHistory(Base):
    __tablename__ = "academic_histories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    degree: Mapped[str] = mapped_column(String(100), nullable=False)
    field_of_study: Mapped[str] = mapped_column(String(150), nullable=False)
    institution: Mapped[str] = mapped_column(String(255), nullable=False)
    start_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    end_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    profile: Mapped["Profile"] = relationship("Profile", back_populates="academic_histories")


class ResearchHistory(Base):
    __tablename__ = "research_histories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    project_title: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(100), nullable=False)
    organization: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    profile: Mapped["Profile"] = relationship("Profile", back_populates="research_histories")
