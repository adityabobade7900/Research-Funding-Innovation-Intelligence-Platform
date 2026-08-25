from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from app.services.providers.base import (
    BaseResearchProvider,
    NormalizedPublication,
    NormalizedAuthor,
    normalize_doi,
    ProviderTimeoutException,
    ProviderRateLimitException,
    ProviderNotFoundException,
)


SAMPLE_PUBLICATIONS: List[Dict[str, Any]] = [
    {
        "title": "Quantum Error Correction on Neutral Atom Arrays",
        "authors": "Dr. Vance Adams, Dr. Sarah Connor",
        "abstract": "Demonstration of fault-tolerant surface codes on a programmable Rydberg atom architecture.",
        "publication_date": datetime(2024, 2, 10, tzinfo=timezone.utc),
        "year": 2024,
        "venue": "Nature Quantum Information",
        "doi": "10.1038/s41534-024-00100-1",
        "citation_count": 58,
        "primary_domain": "Quantum Technologies",
        "keywords": ["Quantum Computing", "Neutral Atoms", "Surface Codes"],
        "source": "mock",
        "external_id": "mock-pub-001",
        "url": "https://doi.org/10.1038/s41534-024-00100-1"
    },
    {
        "title": "Transformer Attention for High-Throughput Genomic Variant Discovery",
        "authors": "Dr. Elena Vance, Dr. Liam Chen",
        "abstract": "Deep attention-based architectures for classifying non-coding regulatory elements in human genomes.",
        "publication_date": datetime(2023, 11, 15, tzinfo=timezone.utc),
        "year": 2023,
        "venue": "Genome Biology",
        "doi": "10.1186/s13059-023-03001-2",
        "citation_count": 112,
        "primary_domain": "Biotechnology & Genomic Sciences",
        "keywords": ["Genomics", "Deep Learning", "Transformers", "CRISPR"],
        "source": "mock",
        "external_id": "mock-pub-002",
        "url": "https://doi.org/10.1186/s13059-023-03001-2"
    },
    {
        "title": "Zero-Knowledge Proofs for Post-Quantum Blockchain Consensus",
        "authors": "Dr. Marcus Brody, Dr. Alan Turing",
        "abstract": "Lattice-based SNARKs achieving succinct verification under sub-millisecond execution times.",
        "publication_date": datetime(2023, 8, 20, tzinfo=timezone.utc),
        "year": 2023,
        "venue": "IEEE Transactions on Information Forensics and Security",
        "doi": "10.1109/tifs.2023.3300123",
        "citation_count": 34,
        "primary_domain": "Cybersecurity & Cryptography",
        "keywords": ["Zero-Knowledge Proofs", "Lattices", "Post-Quantum", "Cryptography"],
        "source": "mock",
        "external_id": "mock-pub-003",
        "url": "https://doi.org/10.1109/tifs.2023.3300123"
    }
]


class MockResearchProvider(BaseResearchProvider):
    def __init__(
        self,
        simulate_timeout: bool = False,
        simulate_rate_limit: bool = False,
        simulate_not_found: bool = False
    ):
        self.simulate_timeout = simulate_timeout
        self.simulate_rate_limit = simulate_rate_limit
        self.simulate_not_found = simulate_not_found
        self._publications: List[NormalizedPublication] = [
            NormalizedPublication(
                title=p["title"],
                authors=p["authors"],
                authors_list=[NormalizedAuthor(name=a.strip()) for a in p["authors"].split(",")],
                abstract=p["abstract"],
                publication_date=p["publication_date"],
                year=p["year"],
                venue=p["venue"],
                doi=normalize_doi(p["doi"]),
                citation_count=p["citation_count"],
                primary_domain=p["primary_domain"],
                keywords=p["keywords"],
                source=p["source"],
                external_id=p["external_id"],
                url=p["url"]
            )
            for p in SAMPLE_PUBLICATIONS
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

    async def fetch_by_doi(self, doi: str) -> Optional[NormalizedPublication]:
        self._check_simulation(doi)
        clean = normalize_doi(doi)
        for pub in self._publications:
            if pub.doi == clean:
                return pub
        return None

    async def search_publications(self, query: str, limit: int = 20) -> List[NormalizedPublication]:
        self._check_simulation(query)
        q_lower = query.lower()
        results = [
            p for p in self._publications
            if q_lower in p.title.lower()
            or (p.abstract and q_lower in p.abstract.lower())
            or q_lower in p.authors.lower()
            or any(q_lower in k.lower() for k in p.keywords)
        ]
        return results[:limit]

    async def fetch_by_author(self, author_identifier: str, limit: int = 20) -> List[NormalizedPublication]:
        self._check_simulation(author_identifier)
        a_lower = author_identifier.lower()
        results = [p for p in self._publications if a_lower in p.authors.lower()]
        return results[:limit]
