from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Integer, Boolean, DateTime, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.profile import Profile


# Association Table between Profile and Publication
profile_publications = Table(
    "profile_publications",
    Base.metadata,
    Column("profile_id", Integer, ForeignKey("profiles.id", ondelete="CASCADE"), primary_key=True),
    Column("publication_id", Integer, ForeignKey("publications.id", ondelete="CASCADE"), primary_key=True),
    Column("is_primary_author", Boolean, default=False, nullable=False),
    Column(
        "created_at",
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    ),
)


class Publication(Base):
    __tablename__ = "publications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), index=True, nullable=False)
    authors: Mapped[str] = mapped_column(Text, nullable=False)
    abstract: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    publication_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    venue: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    doi: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    citation_count: Mapped[int] = mapped_column(Integer, default=0, index=True, nullable=False)
    primary_domain: Mapped[Optional[str]] = mapped_column(String(150), index=True, nullable=True)
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
    keywords: Mapped[List["PublicationKeyword"]] = relationship(
        "PublicationKeyword",
        back_populates="publication",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    profiles: Mapped[List["Profile"]] = relationship(
        "Profile",
        secondary=profile_publications,
        back_populates="publications",
        lazy="selectin"
    )


class PublicationKeyword(Base):
    __tablename__ = "publication_keywords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    publication_id: Mapped[int] = mapped_column(Integer, ForeignKey("publications.id", ondelete="CASCADE"), nullable=False, index=True)
    keyword: Mapped[str] = mapped_column(String(100), index=True, nullable=False)

    # Relationships
    publication: Mapped["Publication"] = relationship("Publication", back_populates="keywords")
