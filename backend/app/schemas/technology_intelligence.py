from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class TechnologyActivityItem(BaseModel):
    technology_area: str = Field(..., description="Technology area or classified field name")
    technology_domain: str = Field(..., description="Broader technology domain")
    classification_code: Optional[str] = Field(None, description="Primary IPC/CPC classification code if available")
    patent_count: int = Field(..., description="Total patents indexed in this technology area")
    recent_patent_count: int = Field(0, description="Filings within the last 24-month window")
    filing_count: int = Field(..., description="Total recorded filings")
    grant_count: int = Field(0, description="Total granted patents")
    citation_count: int = Field(0, description="Cumulative citations received")
    average_citations: float = Field(0.0, description="Average citations per patent")
    assignee_count: int = Field(0, description="Distinct assignees/applicants operating in this area")
    jurisdictions: List[str] = Field(default_factory=list, description="List of active jurisdiction authority codes")
    activity_level: str = Field(..., description="Activity classification: HIGH_ACTIVITY, MEDIUM_ACTIVITY, LOW_ACTIVITY")


class TechnologyActivityResponse(BaseModel):
    items: List[TechnologyActivityItem]
    total_patents: int
    total_technology_areas: int
    summary_by_level: Dict[str, int] = Field(default_factory=dict)
    timeframe_analyzed: Dict[str, Optional[int]] = Field(default_factory=dict)


class TechnologyGrowthItem(BaseModel):
    technology_area: str
    technology_domain: str
    recent_period_filings: int = Field(..., description="Filings in recent window (last 2 years)")
    historical_period_filings: int = Field(..., description="Filings in baseline historical window")
    growth_rate_pct: Optional[float] = Field(None, description="Percentage growth rate between periods; None if historical base is zero")
    velocity_score: float = Field(..., description="Recent activity velocity score (0 to 100)")
    cagr_pct: Optional[float] = Field(None, description="Compound Annual Growth Rate percentage where multi-year data exists")
    cagr_status: str = Field("COMPUTED", description="Status of CAGR: COMPUTED, INSUFFICIENT_DATA, or BASELINE_ZERO")
    growth_trajectory: str = Field(..., description="Trajectory: RAPID_ACCELERATION, STEADY_GROWTH, MATURE_STABLE, DECLINING, EMERGING_SPARSE")


class TechnologyGrowthResponse(BaseModel):
    items: List[TechnologyGrowthItem]
    total_growing_areas: int
    summary_by_trajectory: Dict[str, int] = Field(default_factory=dict)
    timeframe_analyzed: Dict[str, Optional[int]] = Field(default_factory=dict)


class TechnologyCoverageItem(BaseModel):
    technology_area: str
    technology_domain: str
    patent_count: int
    assignee_count: int
    jurisdiction_count: int
    classification_count: int
    coverage_density_score: float = Field(..., description="Multi-signal coverage density score (0 to 100)")
    coverage_level: str = Field(..., description="Coverage level: HIGH_COVERAGE, MODERATE_COVERAGE, SPARSE_COVERAGE")


class TechnologyCoverageResponse(BaseModel):
    items: List[TechnologyCoverageItem]
    total_areas: int
    summary_by_level: Dict[str, int] = Field(default_factory=dict)


class WhitespaceCandidateItem(BaseModel):
    technology_area: str = Field(..., description="Candidate technology area name")
    technology_domain: str = Field(..., description="Broader domain context")
    classification_code: Optional[str] = Field(None, description="Primary IPC/CPC classification code")
    whitespace_type: str = Field(..., description="Classification: POTENTIAL_WHITESPACE, ACTIVITY_GAP, LOW_COVERAGE_AREA, UNDERREPRESENTED_NICHE")
    whitespace_score: float = Field(..., description="Deterministic gap score (0 to 100; higher score indicates larger activity gap)")
    activity_gap_score: float = Field(..., description="Gap component based on patent volume relative to domain benchmark (0-100)")
    assignee_gap_score: float = Field(..., description="Gap component based on low applicant density/diversity (0-100)")
    growth_gap_score: float = Field(..., description="Gap component based on lack of recent filing activity (0-100)")
    coverage_gap_score: float = Field(..., description="Gap component based on geographic and classification sparseness (0-100)")
    publication_count: int = Field(0, description="Scientific publications count (Module 3)")
    patent_count: int = Field(0, description="Patent disclosures count (Module 5)")
    research_to_patent_ratio: Optional[float] = Field(None, description="Ratio of scientific publications to patent disclosures; None if zero patents")
    patent_status_note: Optional[str] = Field(None, description="Explicit note on patent presence, e.g. 'No patent records identified for this technology domain.'")
    publication_density_score: float = Field(0.0, description="Normalized research publication density score (0-100)")
    patent_density_score: float = Field(0.0, description="Normalized patent filing density score (0-100)")
    confidence: str = Field(..., description="Statistical confidence: HIGH, MEDIUM, LOW")
    evidence: List[str] = Field(..., description="Explainable factual evidence supporting whitespace identification")
    adjacent_technology_areas: List[str] = Field(default_factory=list, description="Related or neighboring active technology areas for context")
    methodology_disclaimer: str = Field(
        default="Potential Whitespace Indicator based on publication vs. patent density gaps. Does not constitute an assessment of freedom-to-operate, patentability, or commercial viability."
    )


class WhitespaceDiscoveryResponse(BaseModel):
    candidates: List[WhitespaceCandidateItem]
    total_candidates: int
    domain_filter: Optional[str] = None
    threshold_used: float
    methodology_disclaimer: str = Field(
        default="Potential Whitespace Indicator based on publication vs. patent density gaps. Does not constitute an assessment of freedom-to-operate, patentability, or commercial viability."
    )


class MaturityIndicatorBreakdown(BaseModel):
    research_growth_score: float = Field(..., description="Research publication growth over time (Weight: 25%)")
    patent_growth_score: float = Field(..., description="Patent filing growth and velocity over time (Weight: 25%)")
    research_activity_score: float = Field(..., description="Cumulative research publication volume & citations (Weight: 15%)")
    patent_activity_score: float = Field(..., description="Cumulative patent disclosure volume & grants (Weight: 15%)")
    organization_participation_score: float = Field(..., description="Breadth of participating assignees & institutions (Weight: 10%)")
    technology_diversity_score: float = Field(..., description="Diversity across classifications & jurisdictions (Weight: 10%)")
    research_cagr: Optional[float] = Field(None, description="Multi-year research publication CAGR %")
    patent_cagr: Optional[float] = Field(None, description="Multi-year patent filing CAGR %")
    growth_status: str = Field(
        "COMPUTED",
        description="Growth trend status: COMPUTED, INSUFFICIENT_DATA"
    )
    weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "research_growth": 0.25,
            "patent_growth": 0.25,
            "research_activity": 0.15,
            "patent_activity": 0.15,
            "organization_participation": 0.10,
            "technology_diversity": 0.10,
        }
    )


class TechnologyMaturityItem(BaseModel):
    technology_domain: str = Field(..., description="Technology domain evaluated")
    maturity_score: float = Field(..., description="Normalized weighted maturity score (0 to 100)")
    stage: str = Field(..., description="Technology stage: EMERGING, DEVELOPING, MATURE, DECLINING, INSUFFICIENT_DATA")
    publication_count: int = Field(0, description="Total publications indexed")
    patent_count: int = Field(0, description="Total patents indexed")
    recent_publication_count: int = Field(0, description="Publications in recent 36-month window")
    recent_patent_count: int = Field(0, description="Patents in recent 24-month window")
    assignee_count: int = Field(0, description="Distinct assignees/applicants operating")
    venue_count: int = Field(0, description="Distinct academic publication venues")
    indicators: MaturityIndicatorBreakdown
    explainability_summary: str = Field(..., description="Human-readable justification for maturity score and stage")
    evidence: List[str] = Field(default_factory=list, description="Structured factual evidence points")


class TechnologyMaturityResponse(BaseModel):
    items: List[TechnologyMaturityItem]
    total_domains_analyzed: int
    summary_by_stage: Dict[str, int] = Field(default_factory=dict)
    weighting_schema: Dict[str, float] = Field(
        default_factory=lambda: {
            "research_growth": 0.25,
            "patent_growth": 0.25,
            "research_activity": 0.15,
            "patent_activity": 0.15,
            "organization_participation": 0.10,
            "technology_diversity": 0.10,
        }
    )
    methodology_notes: str = Field(
        default="Mentor-defined Technology Maturity Model: Research Growth (25%), Patent Growth (25%), Research Activity (15%), Patent Activity (15%), Organization Participation (10%), Technology/Application Diversity (10%)."
    )


class AdoptionTrackingItem(BaseModel):
    technology_domain: str
    adoption_status: str = Field(
        "DATA_UNAVAILABLE",
        description="Market adoption status: DATA_UNAVAILABLE, EARLY_PILOT, COMMERCIAL_SCALE"
    )
    adoption_score: Optional[float] = Field(None, description="Enterprise/market adoption score if telemetry exists")
    commercial_evidence_available: bool = Field(False, description="Flag indicating if market telemetry is indexed")
    research_activity_level: str
    patent_activity_level: str
    disclaimer: str = Field(
        default="Technology adoption tracking is strictly separate from scientific publication and patent activity. R&D disclosures precede commercial adoption and do not guarantee market penetration."
    )
    notes: str = Field(
        default="No verified commercial sales or enterprise deployment records indexed for this technology domain in local repository."
    )


class AdoptionTrackingResponse(BaseModel):
    items: List[AdoptionTrackingItem]
    total_domains: int
    disclaimer: str = Field(
        default="Technology adoption tracking is strictly separate from scientific publication and patent activity."
    )


class EmergingTechnologyItem(BaseModel):
    technology_domain: str
    emerging_score: float = Field(..., description="Emergence momentum score (0 to 100)")
    growth_trajectory: str = Field(..., description="Growth trajectory classification")
    research_growth_pct: Optional[float] = Field(None, description="Research publication growth rate %")
    patent_velocity_score: float = Field(..., description="Recent patent filing velocity %")
    publication_count: int
    patent_count: int
    organization_count: int
    key_signals: List[str] = Field(default_factory=list)
    rationale: str = Field(..., description="Explainable rationale for emergence classification")


class EmergingTechnologyResponse(BaseModel):
    candidates: List[EmergingTechnologyItem]
    total_candidates: int


class CompetitiveTechnologyItem(BaseModel):
    technology_domain: str
    assignee_count: int
    top_assignees: List[Dict[str, Any]] = Field(default_factory=list)
    assignee_concentration_hhi: float = Field(..., description="Herfindahl-Hirschman Index for assignees in domain")
    concentration_tier: str = Field(..., description="UNCONCENTRATED, MODERATELY_CONCENTRATED, HIGHLY_CONCENTRATED")
    composite_competitive_index: float = Field(..., description="Composite Competitive Index (0 to 100)")
    dominant_jurisdictions: List[str] = Field(default_factory=list)


class CompetitiveTechnologyResponse(BaseModel):
    items: List[CompetitiveTechnologyItem]
    total_domains: int


class TechnologyIntelligenceSummary(BaseModel):
    total_patents: int
    total_technology_areas: int
    active_areas_count: int
    growing_areas_count: int
    potential_whitespaces_count: int
    top_active_areas: List[TechnologyActivityItem] = Field(default_factory=list)
    top_growing_areas: List[TechnologyGrowthItem] = Field(default_factory=list)
    top_whitespace_candidates: List[WhitespaceCandidateItem] = Field(default_factory=list)
    top_maturing_areas: List[TechnologyMaturityItem] = Field(default_factory=list)
    top_emerging_candidates: List[EmergingTechnologyItem] = Field(default_factory=list)
    methodology_disclaimer: str = Field(
        default="Technology Intelligence metrics and Whitespace indicators are structured metadata aggregations. They do not constitute legal opinions, patentability assessments, or guaranteed commercial opportunity predictions."
    )
