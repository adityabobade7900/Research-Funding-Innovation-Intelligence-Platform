from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class PublicationKeywordBase(BaseModel):
    keyword: str = Field(..., min_length=1, max_length=100)


class PublicationKeywordCreate(PublicationKeywordBase):
    pass


class PublicationKeywordRead(PublicationKeywordBase):
    id: int
    publication_id: int

    model_config = {"from_attributes": True}


class PublicationBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=500)
    authors: str = Field(..., min_length=1)
    abstract: Optional[str] = None
    publication_date: Optional[datetime] = None
    venue: Optional[str] = Field(None, max_length=255)
    doi: Optional[str] = Field(None, max_length=255)
    citation_count: int = Field(0, ge=0)
    primary_domain: Optional[str] = Field(None, max_length=150)
    source: str = Field("manual", max_length=50)
    external_id: Optional[str] = Field(None, max_length=255)
    url: Optional[str] = Field(None, max_length=500)

    @field_validator("doi", mode="before")
    @classmethod
    def clean_doi(cls, v: Optional[str]) -> Optional[str]:
        if v:
            clean = v.strip().lower()
            # Normalize common DOI prefixes
            for prefix in ["https://doi.org/", "http://doi.org/", "doi:", "https://dx.doi.org/", "http://dx.doi.org/"]:
                if clean.startswith(prefix):
                    clean = clean[len(prefix):]
            return clean.strip().rstrip(".,;/") or None
        return None


class PublicationCreate(PublicationBase):
    keywords: Optional[List[str]] = None
    is_primary_author: bool = True


class PublicationUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=500)
    authors: Optional[str] = Field(None, min_length=1)
    abstract: Optional[str] = None
    publication_date: Optional[datetime] = None
    venue: Optional[str] = Field(None, max_length=255)
    doi: Optional[str] = Field(None, max_length=255)
    citation_count: Optional[int] = Field(None, ge=0)
    primary_domain: Optional[str] = Field(None, max_length=150)
    source: Optional[str] = Field(None, max_length=50)
    external_id: Optional[str] = Field(None, max_length=255)
    url: Optional[str] = Field(None, max_length=500)
    keywords: Optional[List[str]] = None


class PublicationRead(PublicationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    keywords: List[PublicationKeywordRead] = []

    model_config = {"from_attributes": True}


class PublicationListResponse(BaseModel):
    items: List[PublicationRead]
    total: int
    limit: int
    offset: int


# --- Controlled Ingestion Schemas ---
class PublicationIngestRequest(BaseModel):
    doi: Optional[str] = None
    query: Optional[str] = None
    author_id: Optional[str] = None
    provider: Optional[str] = None
    limit: int = Field(5, ge=1, le=20)


class PublicationIngestResponse(BaseModel):
    ingested_count: int
    publications: List[PublicationRead]
    message: str
