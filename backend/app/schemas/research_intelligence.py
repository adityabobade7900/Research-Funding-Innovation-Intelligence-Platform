from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# --- Publication Trends ---
class PublicationTrendPoint(BaseModel):
    year: int
    publication_count: int
    growth_rate: Optional[float] = Field(None, description="Year-over-Year growth percentage")


class PublicationTrendsResponse(BaseModel):
    total_publications: int
    year_range: Dict[str, Optional[int]]
    points: List[PublicationTrendPoint]


# --- Domain Trends ---
class DomainYearPoint(BaseModel):
    year: int
    count: int
    share_percentage: float


class DomainTrendItem(BaseModel):
    domain: str
    total_publications: int
    average_citations: float
    yearly_distribution: List[DomainYearPoint]


class DomainTrendsResponse(BaseModel):
    total_domains: int
    domains: List[DomainTrendItem]


# --- Keyword Trends ---
class KeywordYearPoint(BaseModel):
    year: int
    count: int


class KeywordTrendItem(BaseModel):
    keyword: str
    total_occurrences: int
    recent_count: int
    yearly_distribution: List[KeywordYearPoint]


class KeywordTrendsResponse(BaseModel):
    total_keywords: int
    keywords: List[KeywordTrendItem]


# --- Citation Analytics ---
class TopCitedPublicationSummary(BaseModel):
    id: int
    title: str
    citation_count: int
    publication_date: Optional[datetime] = None
    venue: Optional[str] = None
    primary_domain: Optional[str] = None
    doi: Optional[str] = None


class CitationYearPoint(BaseModel):
    year: int
    total_citations: int
    average_citations: float
    publication_count: int


class CitationStatisticsResponse(BaseModel):
    total_publications: int
    total_citations: int
    average_citations: float
    median_citations: float
    max_citations: int
    citations_by_year: List[CitationYearPoint]
    top_cited_publications: List[TopCitedPublicationSummary]


# --- Emerging Topics ---
class EmergingTopicItem(BaseModel):
    topic: str
    recent_count: int
    historical_count: int
    growth_rate: Optional[float]
    velocity_score: float
    status: str = Field(..., description="EMERGING | ESTABLISHED_GROWING | STABLE")
    reasons: List[str] = []


class EmergingTopicsResponse(BaseModel):
    evaluation_window: Dict[str, Any]
    total_emerging: int
    topics: List[EmergingTopicItem]


# --- Research Hotspots ---
class ResearchHotspotItem(BaseModel):
    domain_or_topic: str
    category: str = Field(..., description="domain | keyword")
    publication_count: int
    recent_growth_rate: Optional[float]
    citation_count: int
    average_citations: float
    hotspot_score: float = Field(..., ge=0.0, le=100.0)
    classification: str = Field(..., description="CRITICAL_HOTSPOT | HIGH_ACTIVITY | MODERATE_ACTIVITY | EMERGING_NICHE")
    key_drivers: List[str] = []


class ResearchHotspotsResponse(BaseModel):
    total_hotspots: int
    evaluation_timestamp: datetime
    hotspots: List[ResearchHotspotItem]
