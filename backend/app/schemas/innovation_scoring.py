from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class PillarScoreItem(BaseModel):
    pillar_name: str = Field(..., description="Name of the innovation pillar")
    score: float = Field(..., ge=0.0, le=100.0, description="Normalized pillar score (0-100)")
    weight: float = Field(..., ge=0.0, le=1.0, description="Specification weight for this pillar")
    weighted_score: float = Field(..., ge=0.0, le=100.0, description="Weighted contribution to overall score")
    is_proxy: bool = Field(True, description="Indicates whether this pillar uses an empirical proxy calculation")
    confidence: str = Field(..., description="Confidence level: HIGH, MEDIUM, LOW")
    contributing_signals: Dict[str, Any] = Field(default_factory=dict, description="Key metrics and signal values evaluated")
    evidence: List[str] = Field(default_factory=list, description="Concrete factual evidence supporting the pillar score")
    methodology_notes: str = Field(..., description="Methodology details and explanation of proxy formulation")


class TRLEstimationItem(BaseModel):
    estimated_trl: int = Field(..., ge=1, le=9, description="Estimated Technology Readiness Level (1 to 9)")
    trl_stage: str = Field(..., description="TRL stage category: Basic Research (1-3), Laboratory Validation (4-6), Operational Demonstration (7-9)")
    trl_name: str = Field(..., description="Standard description of the estimated TRL level")
    score: float = Field(..., ge=0.0, le=100.0, description="Normalized TRL score (0 to 100)")
    confidence: str = Field(..., description="Statistical confidence: HIGH, MEDIUM, LOW")
    evidence: List[str] = Field(default_factory=list, description="Factual evidence items supporting the TRL level")
    limitations_and_assumptions: str = Field(
        default="Empirical heuristic estimate based on indexed research publications, patent disclosures, grant status, and assignee profiles. Does not constitute an official certification."
    )


class InnovationScoreResponse(BaseModel):
    target_name: str = Field(..., description="Target name evaluated (Profile name or Domain/Focus area)")
    target_type: str = Field(..., description="Evaluation scope: PROFILE or DOMAIN")
    innovation_score: float = Field(..., ge=0.0, le=100.0, description="Composite Multi-Factor Innovation Score (0 to 100)")
    overall_classification: str = Field(..., description="Classification: BREAKTHROUGH_INNOVATION, HIGH_POTENTIAL, DEVELOPING_CAPABILITY, EARLY_STAGE_EXPLORATORY")
    data_sufficiency: str = Field(..., description="Evidence sufficiency: SUFFICIENT, PARTIAL_EVIDENCE, INSUFFICIENT_DATA")
    pillars: Dict[str, PillarScoreItem] = Field(..., description="Detailed score breakdown across the five pillars")
    trl: TRLEstimationItem = Field(..., description="Estimated Technology Readiness Level evaluation")
    key_strengths: List[str] = Field(default_factory=list, description="Top positive drivers and competitive advantages")
    areas_for_growth: List[str] = Field(default_factory=list, description="Identified areas for capability enhancement or IP expansion")
    governance_disclaimer: str = Field(
        default="The Innovation Score is an explainable composite index based on empirical research, patent, market velocity, and funding metadata. It does not constitute a legal patentability opinion, freedom-to-operate assessment, or guaranteed commercial viability prediction."
    )


class DomainInnovationItem(BaseModel):
    domain: str
    innovation_score: float
    estimated_trl: int
    data_sufficiency: str
    publication_count: int
    patent_count: int


class InnovationScoringSummary(BaseModel):
    total_evaluations: int
    average_innovation_score: float
    trl_distribution: Dict[str, int] = Field(default_factory=dict)
    classification_distribution: Dict[str, int] = Field(default_factory=dict)
    top_innovating_domains: List[DomainInnovationItem] = Field(default_factory=list)
    governance_disclaimer: str = Field(
        default="The Innovation Score is an explainable composite index based on empirical research, patent, market velocity, and funding metadata. It does not constitute a legal patentability opinion, freedom-to-operate assessment, or guaranteed commercial viability prediction."
    )
