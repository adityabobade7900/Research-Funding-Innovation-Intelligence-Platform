from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class NormalizedFundingOpportunity(BaseModel):
    title: str
    funding_agency: str
    funding_program: Optional[str] = None
    description: Optional[str] = None
    funding_amount: Optional[float] = None
    currency: str = "USD"
    application_deadline: Optional[datetime] = None
    opportunity_type: Optional[str] = "Grant"
    eligibility_summary: Optional[str] = None
    eligible_institutions: Optional[str] = None
    geographic_restrictions: Optional[str] = None
    status: str = "open"
    source: str
    external_id: Optional[str] = None
    url: Optional[str] = None
    keywords: List[str] = []
    domain_names: List[str] = []
    raw_payload: Optional[Dict[str, Any]] = None


class BaseFundingProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique slug identifying the funding provider (e.g. 'grants_gov', 'nsf', 'horizon_europe', 'mock')."""
        pass

    @abstractmethod
    async def fetch_by_id(self, external_id: str) -> Optional[NormalizedFundingOpportunity]:
        """Fetches normalized funding opportunity by upstream provider ID."""
        pass

    @abstractmethod
    async def search_opportunities(self, query: str, limit: int = 20) -> List[NormalizedFundingOpportunity]:
        """Searches funding opportunities by keyword query."""
        pass

    @abstractmethod
    async def fetch_by_agency(self, agency_code: str, limit: int = 20) -> List[NormalizedFundingOpportunity]:
        """Fetches opportunities filtered by agency name or code."""
        pass
