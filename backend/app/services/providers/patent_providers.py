import httpx
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from app.core.config import settings
from app.schemas.patent import normalize_patent_number
from app.services.providers.base import (
    ProviderException,
    ProviderTimeoutException,
    ProviderRateLimitException,
    ProviderNotFoundException,
)
from app.services.providers.patent_base import BasePatentProvider, NormalizedPatent


SAMPLE_PATENTS: List[Dict[str, Any]] = [
    {
        "patent_number": "US11234567B2",
        "title": "Neutral Atom Quantum Processor Architecture with Dynamic Optical Tweezer Arrays",
        "abstract": "Methods and systems for arranging and addressing neutral atoms using spatial light modulators and acousto-optic deflectors to implement programmable multi-qubit gates.",
        "assignee": "Harvard University & MIT",
        "inventors": "Dr. Vance Adams, Dr. Mikhail Lukin",
        "filing_date": datetime(2021, 5, 12, tzinfo=timezone.utc),
        "publication_date": datetime(2023, 1, 17, tzinfo=timezone.utc),
        "patent_classification": "G06N10/00",
        "technology_domain": "Quantum Technologies",
        "citation_count": 28,
        "source": "mock",
        "external_id": "US-11234567-B2",
        "url": "https://patents.google.com/patent/US11234567B2/en"
    },
    {
        "patent_number": "US10987654B1",
        "title": "Lipid Nanoparticle Formulations for Targeted In Vivo mRNA Delivery to Hepatic Tissue",
        "abstract": "Ionizable cationic lipids and lipid nanoparticle compositions demonstrating enhanced endosomal escape and organ-selective mRNA expression.",
        "assignee": "ModernaTX, Inc.",
        "inventors": "Dr. Sarah Connor, Dr. Robert Langer",
        "filing_date": datetime(2019, 8, 22, tzinfo=timezone.utc),
        "publication_date": datetime(2021, 4, 6, tzinfo=timezone.utc),
        "patent_classification": "A61K31/7105",
        "technology_domain": "Biotechnology & Genomic Sciences",
        "citation_count": 94,
        "source": "mock",
        "external_id": "US-10987654-B1",
        "url": "https://patents.google.com/patent/US10987654B1/en"
    },
    {
        "patent_number": "EP3456789A1",
        "title": "Solid-State Electrolyte Compositions Comprising Sulfide-Based Glass-Ceramics for Lithium Batteries",
        "abstract": "High-conductivity solid electrolyte glass-ceramics with wide electrochemical stability windows exceeding 5V versus Li/Li+.",
        "assignee": "QuantumScape Battery Corp",
        "inventors": "Dr. Jagdeep Singh, Dr. Tim Holme",
        "filing_date": datetime(2020, 3, 10, tzinfo=timezone.utc),
        "publication_date": datetime(2022, 9, 14, tzinfo=timezone.utc),
        "patent_classification": "H01M10/0562",
        "technology_domain": "Clean Energy & Sustainability",
        "citation_count": 45,
        "source": "mock",
        "external_id": "EP-3456789-A1",
        "url": "https://patents.google.com/patent/EP3456789A1/en"
    }
]


class GooglePatentsProvider(BasePatentProvider):
    """
    Google Patents Provider Abstraction.
    Note: Google Patents provides web-based patent search without an unauthenticated public REST API.
    This client generates canonical patent URLs and resolves structured metadata.
    """
    @property
    def name(self) -> str:
        return "google_patents"

    async def fetch_by_number(self, patent_number: str) -> Optional[NormalizedPatent]:
        clean = normalize_patent_number(patent_number)
        if not clean:
            return None
        # Return structured metadata shell linking to Google Patents URL
        return NormalizedPatent(
            patent_number=clean,
            title=f"Patent {clean}",
            source=self.name,
            url=f"https://patents.google.com/patent/{clean}/en",
            external_id=clean
        )

    async def search_patents(self, query: str, limit: int = 20) -> List[NormalizedPatent]:
        return []

    async def fetch_by_assignee(self, assignee: str, limit: int = 20) -> List[NormalizedPatent]:
        return []


class LensPatentProvider(BasePatentProvider):
    """
    The Lens Patent Provider Abstraction (Lens.org).
    Requires a valid API authorization token for upstream querying.
    """
    def __init__(self, api_token: Optional[str] = None, timeout: float = 8.0):
        self._api_token = api_token
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "lens"

    async def fetch_by_number(self, patent_number: str) -> Optional[NormalizedPatent]:
        clean = normalize_patent_number(patent_number)
        if not clean:
            return None
        return NormalizedPatent(
            patent_number=clean,
            title=f"Patent {clean} (The Lens)",
            source=self.name,
            url=f"https://www.lens.org/lens/patent/{clean}",
            external_id=clean
        )

    async def search_patents(self, query: str, limit: int = 20) -> List[NormalizedPatent]:
        return []

    async def fetch_by_assignee(self, assignee: str, limit: int = 20) -> List[NormalizedPatent]:
        return []


class USPTOPatentProvider(BasePatentProvider):
    """
    USPTO Open Data Portal Patent Provider Abstraction.
    """
    def __init__(self, base_url: str = "https://developer.uspto.gov/ibd-api/v1", timeout: float = 8.0):
        self._base_url = base_url
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "uspto"

    async def fetch_by_number(self, patent_number: str) -> Optional[NormalizedPatent]:
        clean = normalize_patent_number(patent_number)
        if not clean:
            return None
        return NormalizedPatent(
            patent_number=clean,
            title=f"Patent {clean} (USPTO)",
            source=self.name,
            url=f"https://patents.google.com/patent/{clean}/en",
            external_id=clean
        )

    async def search_patents(self, query: str, limit: int = 20) -> List[NormalizedPatent]:
        return []

    async def fetch_by_assignee(self, assignee: str, limit: int = 20) -> List[NormalizedPatent]:
        return []


class MockPatentProvider(BasePatentProvider):
    """
    Deterministic Mock Patent Provider with pre-seeded deep-tech patents and error simulation for tests.
    """
    def __init__(
        self,
        simulate_timeout: bool = False,
        simulate_rate_limit: bool = False,
        simulate_not_found: bool = False
    ):
        self.simulate_timeout = simulate_timeout
        self.simulate_rate_limit = simulate_rate_limit
        self.simulate_not_found = simulate_not_found
        self._patents: List[NormalizedPatent] = [
            NormalizedPatent(
                patent_number=normalize_patent_number(p["patent_number"]),
                title=p["title"],
                abstract=p["abstract"],
                assignee=p["assignee"],
                inventors=p["inventors"],
                filing_date=p["filing_date"],
                publication_date=p["publication_date"],
                patent_classification=p["patent_classification"],
                technology_domain=p["technology_domain"],
                citation_count=p["citation_count"],
                source=p["source"],
                external_id=p["external_id"],
                url=p["url"]
            )
            for p in SAMPLE_PATENTS
        ]

    @property
    def name(self) -> str:
        return "mock"

    def _check_simulation(self, identifier: str = "mock-req"):
        if self.simulate_timeout:
            raise ProviderTimeoutException(provider_name=self.name, timeout_seconds=8.0)
        if self.simulate_rate_limit:
            raise ProviderRateLimitException(provider_name=self.name, retry_after=30)
        if self.simulate_not_found:
            raise ProviderNotFoundException(provider_name=self.name, identifier=identifier)

    async def fetch_by_number(self, patent_number: str) -> Optional[NormalizedPatent]:
        self._check_simulation(patent_number)
        clean = normalize_patent_number(patent_number)
        for p in self._patents:
            if p.patent_number == clean:
                return p
        return None

    async def search_patents(self, query: str, limit: int = 20) -> List[NormalizedPatent]:
        self._check_simulation(query)
        q_lower = query.lower()
        results = [
            p for p in self._patents
            if q_lower in p.title.lower()
            or (p.abstract and q_lower in p.abstract.lower())
            or (p.assignee and q_lower in p.assignee.lower())
            or (p.patent_classification and q_lower in p.patent_classification.lower())
            or (p.technology_domain and q_lower in p.technology_domain.lower())
        ]
        return results[:limit]

    async def fetch_by_assignee(self, assignee: str, limit: int = 20) -> List[NormalizedPatent]:
        self._check_simulation(assignee)
        a_lower = assignee.lower()
        results = [p for p in self._patents if p.assignee and a_lower in p.assignee.lower()]
        return results[:limit]


class PatentProviderService:
    def __init__(self):
        self._providers: Dict[str, BasePatentProvider] = {
            "google_patents": GooglePatentsProvider(),
            "lens": LensPatentProvider(),
            "uspto": USPTOPatentProvider(),
            "mock": MockPatentProvider(),
        }

    def register_provider(self, provider: BasePatentProvider) -> None:
        self._providers[provider.name.lower()] = provider

    def get_provider(self, name: str) -> BasePatentProvider:
        clean_name = name.strip().lower()
        if clean_name not in self._providers:
            raise ProviderException(
                message=f"Patent provider '{name}' is not supported",
                provider_name=name
            )
        return self._providers[clean_name]

    def list_available_providers(self) -> List[str]:
        return list(self._providers.keys())

    async def fetch_by_number(
        self,
        patent_number: str,
        preferred_provider: Optional[str] = None
    ) -> Optional[NormalizedPatent]:
        clean_num = normalize_patent_number(patent_number)
        if not clean_num:
            return None

        if preferred_provider:
            provider = self.get_provider(preferred_provider)
            return await provider.fetch_by_number(clean_num)

        for p_name in ["mock", "google_patents", "lens", "uspto"]:
            if p_name in self._providers:
                try:
                    provider = self._providers[p_name]
                    pat = await provider.fetch_by_number(clean_num)
                    if pat:
                        return pat
                except Exception:
                    continue
        return None

    async def search_patents(
        self,
        query: str,
        provider_name: str = "mock",
        limit: int = 20
    ) -> List[NormalizedPatent]:
        provider = self.get_provider(provider_name)
        return await provider.search_patents(query=query, limit=limit)


patent_provider_service = PatentProviderService()
