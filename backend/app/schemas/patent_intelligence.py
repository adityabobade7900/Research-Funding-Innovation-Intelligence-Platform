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
    assignee_concentration_hhi: float = Field(0.0, description="Herfindahl-Hirschman Index for Assignee concentration (0-10000)")
    concentration_level: str = Field("DIVERSIFIED", description="DIVERSIFIED | MODERATELY_CONCENTRATED | HIGHLY_CONCENTRATED")
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
    assignee_concentration_hhi: float = Field(0.0, description="Herfindahl-Hirschman Index for Assignee concentration (0-10000)")
    concentration_level: str = Field("DIVERSIFIED", description="DIVERSIFIED | MODERATELY_CONCENTRATED | HIGHLY_CONCENTRATED")
    weighting_schema: Dict[str, float] = Field(
        default_factory=lambda: {"volume": 0.40, "velocity": 0.30, "citations": 0.20, "domain_breadth": 0.10},
        description="Weighting breakdown for Composite Competitive Index"
    )
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


# --- Real Machine Learning Patent Clustering ---
class PatentClusterMember(BaseModel):
    patent_id: int
    patent_number: str
    title: str
    assignee: Optional[str] = None
    technology_domain: Optional[str] = None
    patent_classification: Optional[str] = None
    citation_count: int = 0
    distance_to_centroid: Optional[float] = None
    explanation: str


class PatentClusterItem(BaseModel):
    cluster_id: int
    cluster_name: str
    technology_domain: str
    patent_count: int
    share_percentage: float
    dominant_terms: List[str]
    average_citations: float
    representative_patents: List[PatentClusterMember]
    description: str


class PatentClusteringResponse(BaseModel):
    total_patents: int
    total_clusters: int
    algorithm: str = Field("TF-IDF Vectorization + K-Means Clustering", description="Applied ML clustering algorithm")
    k_requested: Optional[int] = None
    clusters: List[PatentClusterItem]
    disclaimer: str = "Unsupervised machine learning clustering based on scikit-learn TF-IDF text representations and K-Means centroid optimization."


# --- Innovation Mapping ---
class InnovationMapMatrixCell(BaseModel):
    domain: str
    assignee: str
    patent_count: int
    patent_numbers: List[str] = []


class InnovationMapHotspot(BaseModel):
    domain: str
    classification: str
    patent_count: int
    recent_count: int
    velocity_score: float
    top_assignees: List[str] = []
    activity_type: str = "EXPANDING_CORE"  # EXPANDING_CORE | HIGH_GROWTH | EMERGING


class InnovationMapWhitespace(BaseModel):
    domain: str
    whitespace_reason: str
    opportunity_level: str = "HIGH"  # HIGH | MEDIUM | MODERATE
    description: str


class InnovationMapResponse(BaseModel):
    total_patents: int
    domains: List[str]
    assignees: List[str]
    classifications: List[str]
    matrix: List[InnovationMapMatrixCell]
    hotspots: List[InnovationMapHotspot]
    whitespaces: List[InnovationMapWhitespace]


# --- Module 3 Profile-Based Patent Recommendations ---
class PatentRecommendationItem(BaseModel):
    patent_id: int
    patent_number: str
    title: str
    abstract: Optional[str] = None
    assignee: Optional[str] = None
    technology_domain: Optional[str] = None
    patent_classification: Optional[str] = None
    citation_count: int = 0
    match_score: float = Field(..., ge=0.0, le=100.0)
    matched_domains: List[str] = []
    matched_keywords: List[str] = []
    rationale: str


class PatentRecommendationsResponse(BaseModel):
    total_recommendations: int
    profile_domains: List[str] = []
    profile_keywords: List[str] = []
    recommendations: List[PatentRecommendationItem]
