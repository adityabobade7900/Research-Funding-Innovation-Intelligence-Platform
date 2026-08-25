from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# --- Research Domains ---
class ResearchDomainBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None


class ResearchDomainCreate(ResearchDomainBase):
    pass


class ResearchDomainRead(ResearchDomainBase):
    id: int

    model_config = {"from_attributes": True}


# --- Research Interests ---
class ResearchInterestBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    importance_level: str = Field("primary", max_length=50)


class ResearchInterestCreate(ResearchInterestBase):
    pass


class ResearchInterestRead(ResearchInterestBase):
    id: int
    profile_id: int

    model_config = {"from_attributes": True}


# --- Profile Keywords ---
class ProfileKeywordCreate(BaseModel):
    keyword: str = Field(..., min_length=1, max_length=100)


class ProfileKeywordRead(BaseModel):
    id: int
    profile_id: int
    keyword: str

    model_config = {"from_attributes": True}


# --- Technology Areas ---
class TechnologyAreaBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = None


class TechnologyAreaCreate(TechnologyAreaBase):
    pass


class TechnologyAreaRead(TechnologyAreaBase):
    id: int
    profile_id: int

    model_config = {"from_attributes": True}


# --- Academic History ---
class AcademicHistoryBase(BaseModel):
    degree: str = Field(..., min_length=1, max_length=100)
    field_of_study: str = Field(..., min_length=1, max_length=150)
    institution: str = Field(..., min_length=1, max_length=255)
    start_year: Optional[int] = Field(None, ge=1900, le=2100)
    end_year: Optional[int] = Field(None, ge=1900, le=2100)


class AcademicHistoryCreate(AcademicHistoryBase):
    pass


class AcademicHistoryRead(AcademicHistoryBase):
    id: int
    profile_id: int

    model_config = {"from_attributes": True}


# --- Research History ---
class ResearchHistoryBase(BaseModel):
    project_title: str = Field(..., min_length=2, max_length=255)
    role: str = Field(..., min_length=2, max_length=100)
    organization: str = Field(..., min_length=2, max_length=255)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    description: Optional[str] = None


class ResearchHistoryCreate(ResearchHistoryBase):
    pass


class ResearchHistoryRead(ResearchHistoryBase):
    id: int
    profile_id: int

    model_config = {"from_attributes": True}


# --- Comprehensive Extended Profile View ---
class ExtendedProfileRead(BaseModel):
    id: int
    user_id: int
    institution: Optional[str] = None
    department: Optional[str] = None
    bio: Optional[str] = None
    orcid_id: Optional[str] = None
    website: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    domains: List[ResearchDomainRead] = []
    interests: List[ResearchInterestRead] = []
    keywords: List[ProfileKeywordRead] = []
    technology_areas: List[TechnologyAreaRead] = []
    academic_histories: List[AcademicHistoryRead] = []
    research_histories: List[ResearchHistoryRead] = []

    model_config = {"from_attributes": True}


# --- Profile Update Request ---
class ExtendedProfileUpdate(BaseModel):
    institution: Optional[str] = Field(None, max_length=255)
    department: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = Field(None, max_length=2000)
    orcid_id: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=255)
    domain_ids: Optional[List[int]] = None
    interests: Optional[List[ResearchInterestCreate]] = None
    keywords: Optional[List[str]] = None
    technology_areas: Optional[List[TechnologyAreaCreate]] = None
    academic_histories: Optional[List[AcademicHistoryCreate]] = None
    research_histories: Optional[List[ResearchHistoryCreate]] = None
