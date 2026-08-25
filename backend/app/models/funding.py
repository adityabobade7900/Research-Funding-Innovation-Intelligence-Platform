from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Integer, Float, DateTime, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.research_domain import ResearchDomain
    from app.models.user import User


# Many-to-Many Association Table between FundingOpportunity and ResearchDomain
funding_opportunity_domains = Table(
    "funding_opportunity_domains",
    Base.metadata,
    Column("funding_opportunity_id", Integer, ForeignKey("funding_opportunities.id", ondelete="CASCADE"), primary_key=True),
    Column("domain_id", Integer, ForeignKey("research_domains.id", ondelete="CASCADE"), primary_key=True),
)


class FundingKeyword(Base):
    __tablename__ = "funding_keywords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    funding_opportunity_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("funding_opportunities.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    keyword: Mapped[str] = mapped_column(String(100), index=True, nullable=False)

    # Relationships
    funding_opportunity: Mapped["FundingOpportunity"] = relationship(
        "FundingOpportunity",
        back_populates="keywords"
    )


class FundingOpportunity(Base):
    __tablename__ = "funding_opportunities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), index=True, nullable=False)
    funding_agency: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    funding_program: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    funding_amount: Mapped[Optional[float]] = mapped_column(Float, index=True, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    application_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    opportunity_type: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    eligibility_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    eligible_institutions: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    geographic_restrictions: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="open", index=True, nullable=False)
    source: Mapped[str] = mapped_column(String(50), default="manual", index=True, nullable=False)
    external_id: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_by_user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

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
    domains: Mapped[List["ResearchDomain"]] = relationship(
        "ResearchDomain",
        secondary=funding_opportunity_domains,
        lazy="selectin"
    )
    keywords: Mapped[List["FundingKeyword"]] = relationship(
        "FundingKeyword",
        back_populates="funding_opportunity",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    creator: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[created_by_user_id],
        lazy="selectin"
    )
