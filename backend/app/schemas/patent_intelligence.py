from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# --- Patent Trends ---
class PatentTrendPoint(BaseModel):
    year: int
    filings_count: int
    grants_count: int
    filing_growth_rate: Optional[float] = Field(None, description="Year-over-Year filing growth percentage")


class PatentTrendsResponse(BaseModel):
    total_patents: int
    year_range: Dict[str, Optional[int]]
    points: List[PatentTrendPoint]


# --- Technology Domains & Concentration ---
class TechnologyDomainItem(BaseModel):
    domain: str
    patent_count: int
    share_percentage: float
    total_citations: int
    average_citations: float
    top_assignees: List[str] = []


class TechnologyDomainsResponse(BaseModel):
    total_domains: int
    concentration_index_hhi: float = Field(..., description="Herfindahl-Hirschman Index (0-10000)")
    concentration_level: str = Field(..., description="DIVERSIFIED | MODERATELY_CONCENTRATED | HIGHLY_CONCENTRATED")
    domains: List[TechnologyDomainItem]


# --- Assignees & Top Patent Holders ---
class AssigneeLandscapeItem(BaseModel):
    assignee: str
    patent_count: int
    share_percentage: float
    total_citations: int
    average_citations: float
    recent_filings_count: int
    primary_domains: List[str] = []
    jurisdictions: List[str] = []


class AssigneesResponse(BaseModel):
    total_assignees: int
    assignees: List[AssigneeLandscapeItem]


# --- Jurisdictions ---
class JurisdictionItem(BaseModel):
    jurisdiction_code: str
    jurisdiction_name: str
    patent_count: int
    share_percentage: float


class JurisdictionsResponse(BaseModel):
    total_jurisdictions: int
    jurisdictions: List[JurisdictionItem]


# --- Patent Status ---
class PatentStatusItem(BaseModel):
    status: str
    count: int
    share_percentage: float


class PatentStatusResponse(BaseModel):
    total_patents: int
    statuses: List[PatentStatusItem]


# --- Competitive Landscape Indicators ---
class CompetitiveAssigneeItem(BaseModel):
    assignee: str
    patent_count: int
    domain_breadth_count: int
    recent_filing_velocity_pct: float
    average_citations: float
    competitive_index: float = Field(..., ge=0.0, le=100.0)
    classification: str = Field(..., description="DOMINANT_PORTFOLIO | HIGH_VELOCITY | NICHE_SPECIALIST | EMERGING_APPLICANT")
    primary_domains: List[str] = []
    key_drivers: List[str] = []


class CompetitiveLandscapeResponse(BaseModel):
    total_competitors: int
    methodology_disclaimer: str = Field(
        "Structured Patent Landscape Indicator based on patent metadata and filing activity. Does not represent full commercial market viability.",
        description="Transparency disclaimer"
    )
    competitors: List[CompetitiveAssigneeItem]


# --- Comprehensive Landscape Overview ---
class PatentLandscapeSummary(BaseModel):
    total_patents: int
    total_assignees: int
    total_domains: int
    total_citations: int
    average_citations: float
    filing_year_range: Dict[str, Optional[int]]
    top_domains: List[TechnologyDomainItem]
    top_assignees: List[AssigneeLandscapeItem]
    jurisdiction_distribution: List[JurisdictionItem]
