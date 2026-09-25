from typing import Dict, List, Optional
from app.services.providers.base import (
    BaseResearchProvider,
    NormalizedPublication,
    ProviderException,
    normalize_doi,
)
from app.services.providers.openalex import OpenAlexProvider
from app.services.providers.crossref import CrossrefProvider
from app.services.providers.semantic_scholar import SemanticScholarProvider
from app.services.providers.mock_provider import MockResearchProvider


class ResearchProviderService:
    def __init__(self):
        self._providers: Dict[str, BaseResearchProvider] = {
            "openalex": OpenAlexProvider(),
            "crossref": CrossrefProvider(),
            "semanticscholar": SemanticScholarProvider(),
            "mock": MockResearchProvider(),
        }

    def register_provider(self, provider: BaseResearchProvider) -> None:
        """Registers or overrides an external provider instance."""
        self._providers[provider.name.lower()] = provider

    def get_provider(self, name: str) -> BaseResearchProvider:
        """Retrieves a provider by slug."""
        clean_name = name.strip().lower()
        if clean_name not in self._providers:
            raise ProviderException(
                message=f"Research provider '{name}' is not supported",
                provider_name=name
            )
        return self._providers[clean_name]

    def list_available_providers(self) -> List[str]:
        """Returns list of registered provider names."""
        return list(self._providers.keys())

    async def fetch_by_doi(
        self,
        doi: str,
        preferred_provider: Optional[str] = None
    ) -> Optional[NormalizedPublication]:
        """
        Fetches publication metadata by DOI. If a preferred provider is explicitly specified,
        it is queried directly. Otherwise providers are queried in priority order:
        openalex -> crossref -> semanticscholar.
        """
        clean_doi = normalize_doi(doi)
        if not clean_doi:
            return None

        # If a specific provider is explicitly requested, query it directly
        if preferred_provider:
            provider = self.get_provider(preferred_provider)
            return await provider.fetch_by_doi(clean_doi)

        # Otherwise cascade across providers
        for p_name in ["openalex", "crossref", "semanticscholar", "mock"]:
            if p_name in self._providers:
                try:
                    provider = self._providers[p_name]
                    pub = await provider.fetch_by_doi(clean_doi)
                    if pub:
                        return pub
                except Exception:
                    continue

        return None

    async def search_publications(
        self,
        query: str,
        provider_name: str = "openalex",
        limit: int = 20
    ) -> List[NormalizedPublication]:
        """Searches publications using the specified external provider."""
        provider = self.get_provider(provider_name)
        return await provider.search_publications(query=query, limit=limit)

    async def fetch_author_publications(
        self,
        author_identifier: str,
        provider_name: str = "openalex",
        limit: int = 20
    ) -> List[NormalizedPublication]:
        """Fetches publications by author ID/name from the specified provider."""
        provider = self.get_provider(provider_name)
        return await provider.fetch_by_author(author_identifier=author_identifier, limit=limit)


# Global singleton provider service
research_provider_service = ResearchProviderService()
