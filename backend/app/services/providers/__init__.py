from app.services.providers.base import (
    BaseResearchProvider,
    NormalizedPublication,
    NormalizedAuthor,
    normalize_doi,
    ProviderException,
    ProviderTimeoutException,
    ProviderRateLimitException,
    ProviderNotFoundException,
)
from app.services.providers.openalex import OpenAlexProvider
from app.services.providers.crossref import CrossrefProvider
from app.services.providers.semantic_scholar import SemanticScholarProvider
from app.services.providers.mock_provider import MockResearchProvider
from app.services.providers.service import ResearchProviderService, research_provider_service

from app.services.providers.patent_base import BasePatentProvider, NormalizedPatent
from app.services.providers.patent_providers import (
    GooglePatentsProvider,
    LensPatentProvider,
    USPTOPatentProvider,
    MockPatentProvider,
    PatentProviderService,
    patent_provider_service
)

from app.services.providers.funding_base import BaseFundingProvider, NormalizedFundingOpportunity
from app.services.providers.funding_providers import (
    GrantsGovProvider,
    NSFFundingProvider,
    HorizonEuropeProvider,
    MockFundingProvider,
    FundingProviderService,
    funding_provider_service
)

__all__ = [
    "BaseResearchProvider",
    "NormalizedPublication",
    "NormalizedAuthor",
    "normalize_doi",
    "ProviderException",
    "ProviderTimeoutException",
    "ProviderRateLimitException",
    "ProviderNotFoundException",
    "OpenAlexProvider",
    "CrossrefProvider",
    "SemanticScholarProvider",
    "MockResearchProvider",
    "ResearchProviderService",
    "research_provider_service",
    "BasePatentProvider",
    "NormalizedPatent",
    "GooglePatentsProvider",
    "LensPatentProvider",
    "USPTOPatentProvider",
    "MockPatentProvider",
    "PatentProviderService",
    "patent_provider_service",
    "BaseFundingProvider",
    "NormalizedFundingOpportunity",
    "GrantsGovProvider",
    "NSFFundingProvider",
    "HorizonEuropeProvider",
    "MockFundingProvider",
    "FundingProviderService",
    "funding_provider_service",
]
