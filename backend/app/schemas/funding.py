from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field, computed_field, AliasChoices
from app.schemas.research_profile import ResearchDomainRead


class FundingKeywordBase(BaseModel):
    keyword: str = Field(..., min_length=1, max_length=100)


class FundingKeywordCreate(FundingKeywordBase):
    pass


class FundingKeywordRead(FundingKeywordBase):
    id: int
    funding_opportunity_id: int

    model_config = {"from_attributes": True}


class FundingOpportunityBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=500)
    funding_agency: str = Field(..., min_length=2, max_length=255)
    funding_program: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    funding_amount: Optional[float] = Field(None, ge=0)
    currency: str = Field("USD", max_length=10)
    application_deadline: Optional[datetime] = None
    opportunity_type: Optional[str] = Field(None, max_length=100)
    eligibility_summary: Optional[str] = None
    eligible_institutions: Optional[str] = Field(None, max_length=255)
    geographic_restrictions: Optional[str] = Field(None, max_length=255)
    status: str = Field("open", max_length=50)
    source: str = Field("manual", max_length=50)
    external_id: Optional[str] = Field(None, max_length=255)
    url: Optional[str] = Field(None, max_length=500)


class FundingOpportunityCreate(FundingOpportunityBase):
    domain_ids: Optional[List[int]] = None
    domain_names: Optional[List[str]] = None
    keywords: Optional[List[str]] = None


class FundingOpportunityUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=500)
    funding_agency: Optional[str] = Field(None, min_length=2, max_length=255)
    funding_program: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    funding_amount: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=10)
    application_deadline: Optional[datetime] = None
    opportunity_type: Optional[str] = Field(None, max_length=100)
    eligibility_summary: Optional[str] = None
    eligible_institutions: Optional[str] = Field(None, max_length=255)
    geographic_restrictions: Optional[str] = Field(None, max_length=255)
    status: Optional[str] = Field(None, max_length=50)
    source: Optional[str] = Field(None, max_length=50)
    external_id: Optional[str] = Field(None, max_length=255)
    url: Optional[str] = Field(None, max_length=500)
    domain_ids: Optional[List[int]] = None
    keywords: Optional[List[str]] = None


class FundingOpportunityRead(FundingOpportunityBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by_user_id: Optional[int] = None
    domains: List[ResearchDomainRead] = []
    keywords: List[FundingKeywordRead] = []
    is_saved: Optional[bool] = None

    @computed_field
    @property
    def days_remaining(self) -> Optional[int]:
        if not self.application_deadline:
            return None
        now = datetime.now(timezone.utc)
        dl = self.application_deadline
        if dl.tzinfo is None:
            dl = dl.replace(tzinfo=timezone.utc)
        return (dl - now).days

    @computed_field
    @property
    def is_expired(self) -> bool:
        if not self.application_deadline:
            return False
        now = datetime.now(timezone.utc)
        dl = self.application_deadline
        if dl.tzinfo is None:
            dl = dl.replace(tzinfo=timezone.utc)
        return dl < now

    @computed_field
    @property
    def deadline_urgency(self) -> str:
        if not self.application_deadline:
            return "ROLLING"
        now = datetime.now(timezone.utc)
        dl = self.application_deadline
        if dl.tzinfo is None:
            dl = dl.replace(tzinfo=timezone.utc)
        if dl < now:
            return "EXPIRED"
        days = (dl - now).days
        if days <= 7:
            return "CRITICAL"
        elif days <= 30:
            return "URGENT"
        return "NORMAL"

    model_config = {"from_attributes": True}


class FundingOpportunityListResponse(BaseModel):
    items: List[FundingOpportunityRead]
    total: int
    limit: int
    offset: int


# --- Saved Funding / Watchlist Schemas ---
class SaveFundingRequest(BaseModel):
    notes: Optional[str] = Field(None, max_length=500)


class SavedFundingItem(BaseModel):
    id: int
    user_id: int
    funding_opportunity_id: int
    notes: Optional[str] = None
    created_at: datetime
    opportunity: FundingOpportunityRead = Field(validation_alias=AliasChoices("funding_opportunity", "opportunity"))

    model_config = {"from_attributes": True}


class SavedFundingListResponse(BaseModel):
    items: List[SavedFundingItem]
    total: int
    limit: int
    offset: int


class SaveFundingToggleResponse(BaseModel):
    saved: bool
    funding_opportunity_id: int
    message: str
    item: Optional[SavedFundingItem] = None


# --- Controlled Ingestion Schemas ---
class FundingIngestRequest(BaseModel):
    external_id: Optional[str] = Field(None, description="Direct provider RFP/grant identifier")
    query: Optional[str] = Field(None, description="Search keyword query")
    agency: Optional[str] = Field(None, description="Agency name or code")
    provider: Optional[str] = Field("mock", description="Provider slug (mock, grants_gov, nsf, horizon_europe)")
    limit: int = Field(5, ge=1, le=20, description="Safe maximum ingestion limit")


class FundingIngestResponse(BaseModel):
    discovered_count: int
    inserted_count: int
    updated_count: int
    duplicate_count: int
    validation_failures_count: int
    opportunities: List[FundingOpportunityRead]
    message: str


# --- Deterministic Eligibility Evaluation Schemas ---
class EligibilityEvaluationResult(BaseModel):
    opportunity_id: int
    opportunity_title: str
    eligible: bool
    eligibility_status: str = Field(..., description="ELIGIBLE | INELIGIBLE | INSUFFICIENT_DATA | CONDITIONAL")
    compatibility_score: float = Field(..., ge=0.0, le=100.0, description="Deterministic match score out of 100")
    matched_criteria: List[str] = []
    failed_criteria: List[str] = []
    warnings: List[str] = []
    missing_information: List[str] = []
    reasons: List[str] = []


# --- Explainable Funding Recommendation Schemas ---
class FundingRecommendationItem(BaseModel):
    opportunity: FundingOpportunityRead
    recommendation_score: float = Field(..., ge=0.0, le=100.0, description="Ranked compatibility score")
    eligibility_status: str
    matched_domains: List[str] = []
    matched_keywords: List[str] = []
    reasons: List[str] = []
    warnings: List[str] = []


class FundingRecommendationResponse(BaseModel):
    total_recommended: int
    items: List[FundingRecommendationItem]
    profile_summary: dict = {}
    evaluation_timestamp: datetime

