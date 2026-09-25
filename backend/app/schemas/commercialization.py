from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# -------------------------------------------------------------
# Structured 4-Pathway Commercialization Models
# -------------------------------------------------------------

class ProductizationPathwayItem(BaseModel):
    pathway: str = Field(default="PRODUCTIZATION")
    product_concept: str = Field(..., description="Actionable product or service concept derived from research/patents")
    target_industry: str = Field(..., description="Target industrial sector or user community")
    problem_addressed: str = Field(..., description="Concrete industrial/market problem solved")
    main_use_case: str = Field(..., description="Primary real-world deployment scenario")
    technology_basis: str = Field(..., description="Scientific mechanism or patent disclosure basis")
    required_next_steps: List[str] = Field(default_factory=list, description="Immediate engineering and translation milestones")
    supporting_evidence: List[str] = Field(default_factory=list, description="Empirical evidence supporting productization viability")
    confidence: str = Field(default="MEDIUM", description="Confidence level: HIGH, MEDIUM, LOW")
    data_status: str = Field(default="AVAILABLE", description="AVAILABLE, INSUFFICIENT_DATA, DATA_UNAVAILABLE")
    score: float = Field(default=0.0, ge=0.0, le=100.0, description="Qualification/fit score (0-100)")
    limitations: str = Field(
        default="Productization concept based on technical disclosures and application fit. Does not guarantee product-market fit or manufacturing scalability."
    )


class LicensingCandidateItem(BaseModel):
    organization: str = Field(..., description="Potential licensing candidate organization name from patent landscape")
    relevant_domain: str = Field(..., description="Technology domain or classification of mutual overlap")
    evidence_of_relevance: str = Field(..., description="Factual evidence of assignee activity and domain alignment")
    patent_count: int = Field(default=0, description="Number of related patents held by this organization in the domain")
    patent_relationship: str = Field(..., description="Relationship to evaluated technology (e.g. competitor, adjacent assignee, portfolio owner)")
    suggested_licensing_rationale: str = Field(..., description="Conservative licensing rationale (e.g. potential licensing candidate based on domain/patent overlap)")
    confidence: str = Field(default="MEDIUM", description="Confidence level: HIGH, MEDIUM, LOW")
    data_status: str = Field(default="AVAILABLE", description="AVAILABLE, INSUFFICIENT_DATA, DATA_UNAVAILABLE")


class LicensingPathwayItem(BaseModel):
    pathway: str = Field(default="LICENSING")
    title: str = Field(default="Corporate IP Out-Licensing")
    licensing_candidates: List[LicensingCandidateItem] = Field(default_factory=list, description="Identified potential corporate licensing candidates from patent owners")
    ip_ownership_basis: str = Field(..., description="Status of patent claims and exclusivity basis")
    rationale: str = Field(..., description="Strategic explanation for exploring licensing")
    supporting_evidence: List[str] = Field(default_factory=list, description="Empirical patent metrics and competitive evidence")
    required_next_steps: List[str] = Field(default_factory=list, description="Prescribed next licensing steps")
    confidence: str = Field(default="MEDIUM", description="Confidence level: HIGH, MEDIUM, LOW")
    data_status: str = Field(default="AVAILABLE", description="AVAILABLE, INSUFFICIENT_DATA, DATA_UNAVAILABLE")
    score: float = Field(default=0.0, ge=0.0, le=100.0, description="Licensing viability score (0-100)")
    limitations: str = Field(
        default="Licensing candidates identified strictly via patent and technology domain overlap. Does not guarantee commercial licensing interest or executed agreements."
    )


class StartupCreationPathwayItem(BaseModel):
    pathway: str = Field(default="STARTUP_CREATION")
    startup_concept: str = Field(..., description="Venture concept hypothesis")
    problem: str = Field(..., description="Unaddressed problem or market pain point")
    proposed_solution: str = Field(..., description="Proposed technology solution and differentiation")
    target_customers: str = Field(..., description="Initial customer segment or early-adopter profile")
    business_model_hypothesis: str = Field(..., description="Preliminary business model hypothesis")
    technology_readiness: str = Field(..., description="Current TRL stage and technical de-risking status")
    relevant_funding: List[str] = Field(default_factory=list, description="Matching non-dilutive grant programs for startup spinout")
    patent_ip_situation: str = Field(..., description="Patent ownership and protection status for the venture")
    competitive_context: str = Field(..., description="Competitive landscape overview from assignee density")
    supporting_evidence: List[str] = Field(default_factory=list, description="Empirical metrics supporting venture viability")
    required_next_steps: List[str] = Field(default_factory=list, description="Actionable venture formation roadmap")
    confidence: str = Field(default="MEDIUM", description="Confidence level: HIGH, MEDIUM, LOW")
    data_status: str = Field(default="AVAILABLE", description="AVAILABLE, INSUFFICIENT_DATA, DATA_UNAVAILABLE")
    score: float = Field(default=0.0, ge=0.0, le=100.0, description="Startup opportunity fit score (0-100)")
    limitations: str = Field(
        default="Potential startup opportunity based on research novelty, TRL, and funding telemetry. Does not guarantee venture success, commercial traction, or external financing."
    )


class PartnershipCandidateItem(BaseModel):
    organization: str = Field(..., description="Potential industry partnership candidate name")
    partnership_type: str = Field(..., description="Collaboration type: Technology Validation, Pilot Project, Research Collaboration, Product Integration, Industry Testing, or Technology Transfer")
    relevant_domain: str = Field(..., description="Shared technology domain or application field")
    evidence_of_relevance: str = Field(..., description="Factual basis for partnership relevance")
    suggested_rationale: str = Field(..., description="Conservative explanation of why this organization is a potential candidate")
    confidence: str = Field(default="MEDIUM", description="Confidence level: HIGH, MEDIUM, LOW")
    data_status: str = Field(default="AVAILABLE", description="AVAILABLE, INSUFFICIENT_DATA, DATA_UNAVAILABLE")


class IndustryPartnershipPathwayItem(BaseModel):
    pathway: str = Field(default="INDUSTRY_PARTNERSHIP")
    title: str = Field(default="Industry Co-Development & Joint Validation")
    partnership_candidates: List[PartnershipCandidateItem] = Field(default_factory=list, description="Identified potential industry partners from patent and research ecosystem")
    rationale: str = Field(..., description="Strategic rationale for collaborative development")
    supporting_evidence: List[str] = Field(default_factory=list, description="Empirical data points supporting joint development")
    required_next_steps: List[str] = Field(default_factory=list, description="Recommended next partnership steps")
    confidence: str = Field(default="MEDIUM", description="Confidence level: HIGH, MEDIUM, LOW")
    data_status: str = Field(default="AVAILABLE", description="AVAILABLE, INSUFFICIENT_DATA, DATA_UNAVAILABLE")
    score: float = Field(default=0.0, ge=0.0, le=100.0, description="Partnership feasibility score (0-100)")
    limitations: str = Field(
        default="Potential industry partnership candidate identified for further evaluation. Does not imply an existing partnership, formal endorsement, or committed agreement."
    )


class CommercializationPathwaysContainer(BaseModel):
    productization: ProductizationPathwayItem
    licensing: LicensingPathwayItem
    startup_creation: StartupCreationPathwayItem
    industry_partnership: IndustryPartnershipPathwayItem


class CommercializationAnalysisItem(BaseModel):
    research_topic: str = Field(..., description="Evaluated research/technology focus area")
    potential_application_areas: List[str] = Field(default_factory=list, description="Identified potential real-world application domains")
    relevant_industries: List[str] = Field(default_factory=list, description="Relevant commercial and industrial sectors")
    problem_application_fit: str = Field(..., description="Analytical synthesis of problem/application fit")
    supporting_evidence: List[str] = Field(default_factory=list, description="Empirical evidence supporting application suitability")
    data_limitations: List[str] = Field(default_factory=list, description="Documented data limitations and unmeasured factors")
    commercial_adoption_telemetry: str = Field(default="DATA_UNAVAILABLE", description="Adoption status telemetry: always DATA_UNAVAILABLE")


# -------------------------------------------------------------
# Core Recommendation and Readiness Models
# -------------------------------------------------------------

class CommercializationRecommendationItem(BaseModel):
    recommendation_type: str = Field(
        ...,
        description="Category: PRODUCTIZATION, LICENSING, STARTUP_CREATION, INDUSTRY_PARTNERSHIP, RESEARCH_FOCUS, VALIDATE_TECHNOLOGY, STRENGTHEN_IP, SEEK_FUNDING, MONITOR_AND_GATHER_EVIDENCE"
    )
    title: str = Field(..., description="Actionable recommendation title")
    priority: str = Field(..., description="Priority: HIGH, MEDIUM, LOW")
    score: float = Field(..., ge=0.0, le=100.0, description="Recommendation fit/relevance score (0-100)")
    confidence: str = Field(..., description="Confidence: HIGH, MEDIUM, LOW")
    data_status: str = Field(default="AVAILABLE", description="AVAILABLE, INSUFFICIENT_DATA, DATA_UNAVAILABLE")
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
    unmeasured_dimensions: Dict[str, str] = Field(
        default_factory=lambda: {
            "regulatory_feasibility": "DATA_UNAVAILABLE",
            "team_capability": "DATA_UNAVAILABLE",
        },
        description="Unmeasured dimensions with explicit data unavailability status"
    )
    data_sufficiency: str = Field(..., description="Evidence sufficiency: SUFFICIENT, PARTIAL_EVIDENCE, INSUFFICIENT_DATA")
    primary_pathway: str = Field(..., description="Primary suggested commercialization pathway")


class CommercializationResponse(BaseModel):
    target_name: str = Field(..., description="Evaluated profile name or technology domain")
    target_type: str = Field(..., description="Target type: PROFILE or DOMAIN")
    readiness: CommercializationReadinessItem = Field(..., description="Commercialization readiness breakdown")
    primary_recommendation: CommercializationRecommendationItem = Field(..., description="Top prioritized primary recommendation")
    recommendations: List[CommercializationRecommendationItem] = Field(default_factory=list, description="All prioritized commercialization recommendations")
    commercialization_analysis: Optional[CommercializationAnalysisItem] = Field(default=None, description="Detailed problem/application fit analysis")
    pathways: Optional[CommercializationPathwaysContainer] = Field(default=None, description="The four canonical commercialization pathways")
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
