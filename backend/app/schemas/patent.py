import re
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


def normalize_patent_number(raw_num: Optional[str]) -> Optional[str]:
    """Normalizes patent numbers to canonical uppercase alphanumeric format without spaces, commas, or dashes."""
    if not raw_num or not isinstance(raw_num, str):
        return None
    # Remove whitespace, commas, slashes, and dashes, then uppercase
    clean = re.sub(r"[\s,\-\/\.]", "", raw_num).strip().upper()
    return clean or None


class PatentBase(BaseModel):
    patent_number: str = Field(..., min_length=3, max_length=100)
    title: str = Field(..., min_length=2, max_length=500)
    abstract: Optional[str] = None
    assignee: Optional[str] = Field(None, max_length=255)
    inventors: Optional[str] = None
    filing_date: Optional[datetime] = None
    publication_date: Optional[datetime] = None
    patent_classification: Optional[str] = Field(None, max_length=100)
    technology_domain: Optional[str] = Field(None, max_length=150)
    citation_count: int = Field(0, ge=0)
    source: str = Field("manual", max_length=50)
    external_id: Optional[str] = Field(None, max_length=255)
    url: Optional[str] = Field(None, max_length=500)

    @field_validator("patent_number", mode="before")
    @classmethod
    def clean_patent_number(cls, v: Optional[str]) -> Optional[str]:
        return normalize_patent_number(v)


class PatentCreate(PatentBase):
    pass


class PatentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=500)
    abstract: Optional[str] = None
    assignee: Optional[str] = Field(None, max_length=255)
    inventors: Optional[str] = None
    filing_date: Optional[datetime] = None
    publication_date: Optional[datetime] = None
    patent_classification: Optional[str] = Field(None, max_length=100)
    technology_domain: Optional[str] = Field(None, max_length=150)
    citation_count: Optional[int] = Field(None, ge=0)
    source: Optional[str] = Field(None, max_length=50)
    external_id: Optional[str] = Field(None, max_length=255)
    url: Optional[str] = Field(None, max_length=500)


class PatentRead(PatentBase):
    id: int
    is_bookmarked: Optional[bool] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PatentListResponse(BaseModel):
    items: List[PatentRead]
    total: int
    limit: int
    offset: int


class PatentIngestRequest(BaseModel):
    patent_number: str = Field(..., min_length=3, max_length=100)
    provider: Optional[str] = Field(None, max_length=50)
