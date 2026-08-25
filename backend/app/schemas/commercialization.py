from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CommercializationRecommendationItem(BaseModel):
    recommendation_type: str = Field(
        ...,
        description="Category: RESEARCH_FOCUS, VALIDATE_TECHNOLOGY, STRENGTHEN_IP, SEEK_FUNDING, INDUSTRY_COLLABORATION, LICENSING, COMMERCIALIZATION_PREPARATION, STARTUP_SPINOUT, MONITOR_AND_GATHER_EVIDENCE"
    )
    title: str = Field(..., description="Actionable recommendation title")
    priority: str = Field(..., description="Priority: HIGH, MEDIUM, LOW")
    score: float = Field(..., ge=0.0, le=100.0, description="Recommendation fit/relevance score (0-100)")
    confidence: str = Field(..., description="Confidence: HIGH, MEDIUM, LOW")
    rationale: str = Field(..., description="Explainable reason why this recommendation was triggered")
    supporting_evidence: List[str] = Field(default_factory=list, description="Concrete empirical data points supporting the recommendation")
    required_next_actions: List[str] = Field(default_factory=list, description="Prescribed next implementation actions")
    limitations: str = Field(
        default="Advisory recommendation based on indexed research publications, patent disclosures, and funding metadata. Does not guarantee market viability or venture success."
    )


class CommercializationReadinessItem(BaseModel):
    readiness_score: float = Field(..., ge=0.0, le=100.0, description="Composite Commercialization Readiness Score (0-100)")
    readiness_level: str = Field(
        ...,
        description="Level: HIGH_COMMERCIAL_READINESS, MODERATE_COMMERCIAL_READINESS, EARLY_DEVELOPMENT, BASIC_RESEARCH_STAGE"
    )
    dimensions: Dict[str, float] = Field(
        ...,
        description="Dimensional sub-scores: technology_maturity, patent_strength, market_potential, funding_relevance, research_novelty"
    )
    data_sufficiency: str = Field(..., description="Evidence sufficiency: SUFFICIENT, PARTIAL_EVIDENCE, INSUFFICIENT_DATA")
    primary_pathway: str = Field(..., description="Primary suggested commercialization pathway")


class CommercializationResponse(BaseModel):
    target_name: str = Field(..., description="Evaluated profile name or technology domain")
    target_type: str = Field(..., description="Target type: PROFILE or DOMAIN")
    readiness: CommercializationReadinessItem = Field(..., description="Commercialization readiness breakdown")
    primary_recommendation: CommercializationRecommendationItem = Field(..., description="Top prioritized primary recommendation")
    recommendations: List[CommercializationRecommendationItem] = Field(default_factory=list, description="All prioritized commercialization recommendations")
    innovation_context: Dict[str, Any] = Field(default_factory=dict, description="Innovation Score and 5-pillar context")
    funding_opportunities: List[Dict[str, Any]] = Field(default_factory=list, description="Top matching active funding opportunities")
    whitespace_context: List[str] = Field(default_factory=list, description="Relevant whitespace gap indicators or adjacent fields")
    governance_disclaimer: str = Field(
        default="Commercialization recommendations and readiness scores are empirical advisory guidelines derived from patent, research, funding, and growth metadata. They do not constitute legal patentability opinions, freedom-to-operate guarantees, or financial investment advice."
    )


class DomainCommercializationItem(BaseModel):
    domain: str
    readiness_score: float
    readiness_level: str
    primary_pathway: str
    estimated_trl: int
    innovation_score: float
    recommendation_count: int


class CommercializationSummary(BaseModel):
    total_evaluations: int
    average_readiness_score: float
    readiness_distribution: Dict[str, int] = Field(default_factory=dict)
    pathway_distribution: Dict[str, int] = Field(default_factory=dict)
    top_commercial_prospects: List[DomainCommercializationItem] = Field(default_factory=list)
    governance_disclaimer: str = Field(
        default="Commercialization recommendations and readiness scores are empirical advisory guidelines derived from patent, research, funding, and growth metadata. They do not constitute legal patentability opinions, freedom-to-operate guarantees, or financial investment advice."
    )
