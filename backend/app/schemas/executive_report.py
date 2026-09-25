from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class RoadmapActionItem(BaseModel):
    action: str
    owner_role: str
    target_timeline: str
    expected_outcome: str


class RoadmapPhaseItem(BaseModel):
    phase_name: str
    timeframe: str
    description: str
    actions: List[RoadmapActionItem] = Field(default_factory=list)


class StrategicAssessment(BaseModel):
    strengths: List[str] = Field(default_factory=list, description="Verified institutional/scientific advantages")
    risks_and_bottlenecks: List[str] = Field(default_factory=list, description="Critical technology, IP, or funding risks")
    market_opportunities: List[str] = Field(default_factory=list, description="Commercial whitespace or grant funding streams")
    barriers_to_entry: List[str] = Field(default_factory=list, description="Regulatory, patent thicket, or TRL barriers")


class ExecutiveDossierResponse(BaseModel):
    report_id: str = Field(..., description="Unique generated report identifier")
    generated_at: str = Field(..., description="ISO timestamp of dossier generation")
    target_name: str = Field(..., description="Profile name or Technology Domain evaluated")
    target_type: str = Field(..., description="PROFILE or DOMAIN")
    executive_summary: str = Field(..., description="High-level narrative synthesis of all intelligence pillars")
    key_findings: List[str] = Field(default_factory=list, description="Core analytical highlights across research, IP, and grants")
    
    # Pillar High-Level Metrics
    innovation_score: float = Field(..., ge=0.0, le=100.0)
    innovation_classification: str
    estimated_trl: int = Field(..., ge=1, le=9)
    trl_stage: str
    commercialization_readiness: float = Field(..., ge=0.0, le=100.0)
    readiness_level: str
    primary_commercial_pathway: str
    
    # Statistical Aggregates
    publication_metrics: Dict[str, Any] = Field(default_factory=dict)
    patent_metrics: Dict[str, Any] = Field(default_factory=dict)
    funding_metrics: Dict[str, Any] = Field(default_factory=dict)
    whitespace_metrics: Dict[str, Any] = Field(default_factory=dict)
    
    # Strategic & Action Synthesis
    strategic_assessment: StrategicAssessment
    roadmap: List[RoadmapPhaseItem] = Field(default_factory=list)
    top_recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    top_funding_opportunities: List[Dict[str, Any]] = Field(default_factory=list)
    
    data_sufficiency: str
    governance_disclaimer: str = Field(
        default="This Executive Intelligence Dossier is an automated synthesis of empirical publication, patent, grant, and growth metadata. It provides strategic advisory decision support and does not constitute a legal freedom-to-operate opinion, binding valuation, or guaranteed commercial success forecast."
    )


class DomainBenchmarkItem(BaseModel):
    domain: str
    innovation_score: float
    estimated_trl: int
    commercialization_readiness: float
    primary_pathway: str
    total_publications: int
    total_patents: int
    active_funding_streams: int


class ExecutiveDossierSummary(BaseModel):
    total_domains_benchmarked: int
    portfolio_average_innovation_score: float
    portfolio_average_readiness_score: float
    dominant_pathway: str
    trl_breakdown: Dict[str, int] = Field(default_factory=dict)
    domain_benchmarks: List[DomainBenchmarkItem] = Field(default_factory=list)
    governance_disclaimer: str = Field(
        default="This Executive Intelligence Dossier is an automated synthesis of empirical publication, patent, grant, and growth metadata. It provides strategic advisory decision support and does not constitute a legal freedom-to-operate opinion, binding valuation, or guaranteed commercial success forecast."
    )
