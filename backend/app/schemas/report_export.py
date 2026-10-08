import enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ReportType(str, enum.Enum):
    FUNDING = "FUNDING"
    PATENT = "PATENT"
    RESEARCH_TREND = "RESEARCH_TREND"
    INNOVATION_INTELLIGENCE = "INNOVATION_INTELLIGENCE"
    COMMERCIALIZATION = "COMMERCIALIZATION"
    EXECUTIVE_DOSSIER = "EXECUTIVE_DOSSIER"


class ReportFilterParams(BaseModel):
    report_type: ReportType = ReportType.FUNDING
    domain: Optional[str] = Field(None, description="Research or Technology Domain")
    technology: Optional[str] = Field(None, description="Specific Technology Area")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    start_year: Optional[int] = Field(None, ge=1990, le=2050, description="Start year filter")
    end_year: Optional[int] = Field(None, ge=1990, le=2050, description="End year filter")
    agency: Optional[str] = Field(None, description="Funding agency filter")
    funding_type: Optional[str] = Field(None, description="Grant / Fellowship / Contract")
    min_amount: Optional[float] = Field(None, ge=0, description="Minimum funding amount")
    max_amount: Optional[float] = Field(None, ge=0, description="Maximum funding amount")
    assignee: Optional[str] = Field(None, description="Patent applicant / assignee organization")
    technology_stage: Optional[str] = Field(None, description="EMERGING, DEVELOPING, MATURE, DECLINING")
    my_profile_only: bool = Field(False, description="Scope to authenticated user portfolio")


class ReportTypeItem(BaseModel):
    id: ReportType
    name: str
    description: str
    source_module: str
    supported_filters: List[str]


class ReportTypesResponse(BaseModel):
    report_types: List[ReportTypeItem]


class ReportFactorItem(BaseModel):
    factor_name: str
    weight_pct: float
    score: float
    status: str
    description: str
    signals: Dict[str, Any] = Field(default_factory=dict)


class ReportPreviewResponse(BaseModel):
    report_type: ReportType
    title: str
    generated_at: str
    applied_filters: Dict[str, Any]
    total_records: int
    metrics: Dict[str, Any] = Field(default_factory=dict)
    summary_text: str
    table_headers: List[str]
    table_rows: List[List[Any]]
    factors: Optional[List[ReportFactorItem]] = None
    recommendations: Optional[List[str]] = None
    data_limitations: Optional[str] = None
