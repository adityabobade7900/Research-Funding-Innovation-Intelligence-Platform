from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from app.schemas.patent import normalize_patent_number


class NormalizedPatent(BaseModel):
    patent_number: str
    title: str
    abstract: Optional[str] = None
    assignee: Optional[str] = None
    inventors: Optional[str] = None
    filing_date: Optional[datetime] = None
    publication_date: Optional[datetime] = None
    patent_classification: Optional[str] = None
    technology_domain: Optional[str] = None
    citation_count: int = 0
    source: str
    external_id: Optional[str] = None
    url: Optional[str] = None
    raw_payload: Optional[Dict[str, Any]] = None

    @field_validator("patent_number", mode="before")
    @classmethod
    def clean_number(cls, v: Optional[str]) -> Optional[str]:
        return normalize_patent_number(v)


class BasePatentProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique slug identifying the patent provider (e.g. 'google_patents', 'lens', 'uspto', 'mock')."""
        pass

    @abstractmethod
    async def fetch_by_number(self, patent_number: str) -> Optional[NormalizedPatent]:
        """Fetches normalized patent data by patent number."""
        pass

    @abstractmethod
    async def search_patents(self, query: str, limit: int = 20) -> List[NormalizedPatent]:
        """Searches patents by text query."""
        pass

    @abstractmethod
    async def fetch_by_assignee(self, assignee: str, limit: int = 20) -> List[NormalizedPatent]:
        """Fetches patents by assignee organization."""
        pass
