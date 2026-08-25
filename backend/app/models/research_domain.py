from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Integer, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.profile import Profile


# Association Table for Many-to-Many relationship between Profile and ResearchDomain
profile_domains = Table(
    "profile_domains",
    Base.metadata,
    Column("profile_id", Integer, ForeignKey("profiles.id", ondelete="CASCADE"), primary_key=True),
    Column("domain_id", Integer, ForeignKey("research_domains.id", ondelete="CASCADE"), primary_key=True),
)


class ResearchDomain(Base):
    __tablename__ = "research_domains"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    profiles: Mapped[List["Profile"]] = relationship(
        "Profile",
        secondary=profile_domains,
        back_populates="domains",
        lazy="selectin"
    )


class ResearchInterest(Base):
    __tablename__ = "research_interests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    importance_level: Mapped[str] = mapped_column(String(50), default="primary", nullable=False)

    # Relationships
    profile: Mapped["Profile"] = relationship("Profile", back_populates="interests")


class ProfileKeyword(Base):
    __tablename__ = "profile_keywords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    keyword: Mapped[str] = mapped_column(String(100), index=True, nullable=False)

    # Relationships
    profile: Mapped["Profile"] = relationship("Profile", back_populates="keywords")


class TechnologyArea(Base):
    __tablename__ = "technology_areas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    profile: Mapped["Profile"] = relationship("Profile", back_populates="technology_areas")
