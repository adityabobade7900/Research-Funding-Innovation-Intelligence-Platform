from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


# --- Provider Custom Exceptions ---
class ProviderException(Exception):
    """Base exception for all external provider errors."""
    def __init__(self, message: str, provider_name: str, status_code: Optional[int] = None, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.provider_name = provider_name
        self.status_code = status_code
        self.details = details


class ProviderTimeoutException(ProviderException):
    """Raised when an external provider request exceeds the timeout threshold."""
    def __init__(self, provider_name: str, timeout_seconds: float):
        super().__init__(
            message=f"Request to provider '{provider_name}' timed out after {timeout_seconds}s",
            provider_name=provider_name,
            status_code=504
        )


class ProviderRateLimitException(ProviderException):
    """Raised when an external provider responds with HTTP 429 Too Many Requests."""
    def __init__(self, provider_name: str, retry_after: Optional[int] = None):
        super().__init__(
            message=f"Rate limit exceeded for provider '{provider_name}'",
            provider_name=provider_name,
            status_code=429,
            details={"retry_after": retry_after}
        )


class ProviderNotFoundException(ProviderException):
    """Raised when a specific requested entity is not indexed in the provider."""
    def __init__(self, provider_name: str, identifier: str):
        super().__init__(
            message=f"Entity '{identifier}' not found in provider '{provider_name}'",
            provider_name=provider_name,
            status_code=404
        )


# --- Helper Functions ---
def normalize_doi(raw_doi: Optional[str]) -> Optional[str]:
    """Standardizes DOI format by stripping prefixes and converting to lowercase."""
    if not raw_doi or not isinstance(raw_doi, str):
        return None
    clean = raw_doi.strip().lower()
    for prefix in ["https://doi.org/", "http://doi.org/", "doi:", "https://dx.doi.org/", "http://dx.doi.org/"]:
        if clean.startswith(prefix):
            clean = clean[len(prefix):]
    clean = clean.strip().rstrip(".,;/")
    return clean or None


# --- Normalized Publication Data Model ---
class NormalizedAuthor(BaseModel):
    name: str
    orcid: Optional[str] = None
    affiliation: Optional[str] = None


class NormalizedPublication(BaseModel):
    title: str
    authors: str
    authors_list: List[NormalizedAuthor] = []
    abstract: Optional[str] = None
    publication_date: Optional[datetime] = None
    year: Optional[int] = None
    venue: Optional[str] = None
    doi: Optional[str] = None
    citation_count: int = 0
    primary_domain: Optional[str] = None
    keywords: List[str] = []
    source: str
    external_id: Optional[str] = None
    url: Optional[str] = None
    raw_payload: Optional[Dict[str, Any]] = None

    @field_validator("doi", mode="before")
    @classmethod
    def clean_doi(cls, v: Optional[str]) -> Optional[str]:
        return normalize_doi(v)


# --- Base Provider Interface ---
class BaseResearchProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique slug identifying the provider (e.g., 'openalex', 'crossref', 'semanticscholar')."""
        pass

    @abstractmethod
    async def fetch_by_doi(self, doi: str) -> Optional[NormalizedPublication]:
        """Fetches a normalized publication by DOI."""
        pass

    @abstractmethod
    async def search_publications(self, query: str, limit: int = 20) -> List[NormalizedPublication]:
        """Searches publications by text query."""
        pass

    @abstractmethod
    async def fetch_by_author(self, author_identifier: str, limit: int = 20) -> List[NormalizedPublication]:
        """Fetches publications for a specific author name or provider author ID."""
        pass
