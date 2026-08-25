import pytest
from datetime import datetime, timezone

from app.services.providers.base import (
    normalize_doi,
    NormalizedPublication,
    ProviderTimeoutException,
    ProviderRateLimitException,
    ProviderNotFoundException,
    ProviderException,
)
from app.services.providers.openalex import OpenAlexProvider
from app.services.providers.crossref import CrossrefProvider
from app.services.providers.semantic_scholar import SemanticScholarProvider
from app.services.providers.mock_provider import MockResearchProvider
from app.services.providers.service import ResearchProviderService


def test_doi_normalization():
    """Verifies that various raw DOI formats are uniformly normalized."""
    assert normalize_doi("https://doi.org/10.1038/s41586-020-2649-2") == "10.1038/s41586-020-2649-2"
    assert normalize_doi("http://doi.org/10.1038/S41586-020-2649-2") == "10.1038/s41586-020-2649-2"
    assert normalize_doi("doi:10.1103/PhysRevLett.120.010501.") == "10.1103/physrevlett.120.010501"
    assert normalize_doi(" 10.1016/j.cell.2021.05.001 ") == "10.1016/j.cell.2021.05.001"
    assert normalize_doi(None) is None
    assert normalize_doi("") is None


def test_openalex_payload_normalization():
    """Verifies parsing and abstract reconstruction of raw OpenAlex JSON payloads."""
    provider = OpenAlexProvider()

    raw_payload = {
        "id": "https://openalex.org/W2741809807",
        "doi": "https://doi.org/10.1038/s41586-021-03819-2",
        "title": "Highly accurate protein structure prediction with AlphaFold",
        "publication_year": 2021,
        "publication_date": "2021-07-15",
        "cited_by_count": 18450,
        "abstract_inverted_index": {
            "Proteins": [0],
            "are": [1],
            "essential": [2],
            "to": [3],
            "life.": [4]
        },
        "authorships": [
            {
                "author": {"display_name": "John Jumper", "orcid": "https://orcid.org/0000-0001-6103-6882"},
                "institutions": [{"display_name": "DeepMind"}]
            },
            {
                "author": {"display_name": "Demis Hassabis"},
                "institutions": [{"display_name": "DeepMind"}]
            }
        ],
        "primary_location": {
            "source": {"display_name": "Nature"},
            "landing_page_url": "https://www.nature.com/articles/s41586-021-03819-2"
        },
        "primary_topic": {
            "domain": {"display_name": "Biotechnology & Genomic Sciences"}
        },
        "concepts": [
            {"display_name": "Protein structure", "score": 0.85},
            {"display_name": "AlphaFold", "score": 0.92},
            {"display_name": "Low relevance topic", "score": 0.1}
        ]
    }

    norm = provider.normalize_work(raw_payload)

    assert norm.title == "Highly accurate protein structure prediction with AlphaFold"
    assert norm.doi == "10.1038/s41586-021-03819-2"
    assert norm.abstract == "Proteins are essential to life."
    assert norm.authors == "John Jumper, Demis Hassabis"
    assert len(norm.authors_list) == 2
    assert norm.authors_list[0].affiliation == "DeepMind"
    assert norm.venue == "Nature"
    assert norm.citation_count == 18450
    assert norm.primary_domain == "Biotechnology & Genomic Sciences"
    assert "Protein structure" in norm.keywords
    assert "AlphaFold" in norm.keywords
    assert "Low relevance topic" not in norm.keywords
    assert norm.source == "openalex"
    assert norm.external_id == "W2741809807"


def test_crossref_payload_normalization():
    """Verifies parsing of raw Crossref work payloads with JATS tag cleaning."""
    provider = CrossrefProvider()

    raw_payload = {
        "DOI": "10.1103/PhysRevLett.122.010501",
        "title": ["Quantum Advantage with Shallow Circuits"],
        "container-title": ["Physical Review Letters"],
        "author": [
            {"given": "Sergey", "family": "Bravyi", "affiliation": [{"name": "IBM Quantum"}]},
            {"given": "David", "family": "Gosset"}
        ],
        "published-print": {"date-parts": [[2019, 1, 4]]},
        "is-referenced-by-count": 210,
        "abstract": "<jats:p>We prove an unconditional separation between quantum and classical circuits.</jats:p>",
        "subject": ["Physics", "Quantum Physics"],
        "URL": "https://doi.org/10.1103/PhysRevLett.122.010501"
    }

    norm = provider.normalize_work(raw_payload)

    assert norm.title == "Quantum Advantage with Shallow Circuits"
    assert norm.doi == "10.1103/physrevlett.122.010501"
    assert norm.authors == "Sergey Bravyi, David Gosset"
    assert norm.venue == "Physical Review Letters"
    assert norm.citation_count == 210
    assert norm.year == 2019
    assert norm.abstract == "We prove an unconditional separation between quantum and classical circuits."
    assert "Quantum Physics" in norm.keywords
    assert norm.source == "crossref"


def test_semantic_scholar_payload_normalization():
    """Verifies parsing of Semantic Scholar Graph API paper objects."""
    provider = SemanticScholarProvider()

    raw_payload = {
        "paperId": "649def34f8be52c8b66281af98ae772c99cf93e5",
        "title": "Attention Is All You Need",
        "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks.",
        "year": 2017,
        "publicationDate": "2017-06-12",
        "venue": "NeurIPS",
        "citationCount": 98000,
        "externalIds": {"DOI": "10.5555/3295222.3295349", "CorpusId": 13756489},
        "authors": [{"name": "Ashish Vaswani"}, {"name": "Noam Shazeer"}],
        "s2FieldsOfStudy": [{"category": "Computer Science"}, {"category": "Artificial Intelligence"}],
        "url": "https://www.semanticscholar.org/paper/649def34f8be52c8b66281af98ae772c99cf93e5"
    }

    norm = provider.normalize_work(raw_payload)

    assert norm.title == "Attention Is All You Need"
    assert norm.doi == "10.5555/3295222.3295349"
    assert norm.authors == "Ashish Vaswani, Noam Shazeer"
    assert norm.venue == "NeurIPS"
    assert norm.citation_count == 98000
    assert norm.primary_domain == "Computer Science"
    assert "Artificial Intelligence" in norm.keywords
    assert norm.source == "semanticscholar"
    assert norm.external_id == "649def34f8be52c8b66281af98ae772c99cf93e5"


def test_missing_fields_safe_handling():
    """Verifies that missing, partial, or malformed provider objects normalize safely without crashing."""
    openalex = OpenAlexProvider()
    crossref = CrossrefProvider()
    s2 = SemanticScholarProvider()

    # Empty dictionary
    norm_oa = openalex.normalize_work({})
    assert norm_oa.title == "Untitled Publication"
    assert norm_oa.authors == "Unknown Author"
    assert norm_oa.citation_count == 0
    assert norm_oa.keywords == []

    norm_cr = crossref.normalize_work({})
    assert norm_cr.title == "Untitled Publication"
    assert norm_cr.authors == "Unknown Author"
    assert norm_cr.citation_count == 0

    norm_s2 = s2.normalize_work({})
    assert norm_s2.title == "Untitled Publication"
    assert norm_s2.authors == "Unknown Author"
    assert norm_s2.citation_count == 0


@pytest.mark.asyncio
async def test_mock_provider_retrieval_and_search():
    """Verifies deterministic querying and searching via MockResearchProvider."""
    provider = MockResearchProvider()

    # 1. Fetch by DOI
    pub = await provider.fetch_by_doi("10.1038/s41534-024-00100-1")
    assert pub is not None
    assert pub.title == "Quantum Error Correction on Neutral Atom Arrays"
    assert pub.citation_count == 58

    # 2. Search publications
    results = await provider.search_publications("Genomic", limit=10)
    assert len(results) >= 1
    assert "Genomic Variant Discovery" in results[0].title

    # 3. Fetch by Author
    author_pubs = await provider.fetch_by_author("Vance Adams")
    assert len(author_pubs) >= 1


@pytest.mark.asyncio
async def test_mock_provider_error_simulations():
    """Verifies exception handling for timeout, rate limiting, and missing entities."""
    timeout_provider = MockResearchProvider(simulate_timeout=True)
    with pytest.raises(ProviderTimeoutException) as exc_timeout:
        await timeout_provider.fetch_by_doi("10.1038/sample")
    assert exc_timeout.value.status_code == 504

    rate_limit_provider = MockResearchProvider(simulate_rate_limit=True)
    with pytest.raises(ProviderRateLimitException) as exc_ratelimit:
        await rate_limit_provider.search_publications("Quantum")
    assert exc_ratelimit.value.status_code == 429

    not_found_provider = MockResearchProvider(simulate_not_found=True)
    with pytest.raises(ProviderNotFoundException) as exc_notfound:
        await not_found_provider.fetch_by_doi("10.1038/nonexistent")
    assert exc_notfound.value.status_code == 404


@pytest.mark.asyncio
async def test_provider_service_orchestration_and_cascade():
    """Verifies provider registry, preferred provider lookup, and graceful fallback."""
    service = ResearchProviderService()

    # Register deterministic mock provider as primary test target
    mock = MockResearchProvider()
    service.register_provider(mock)

    # 1. List available providers
    available = service.list_available_providers()
    assert "openalex" in available
    assert "crossref" in available
    assert "semanticscholar" in available
    assert "mock" in available

    # 2. Query valid provider
    prov = service.get_provider("mock")
    assert prov.name == "mock"

    # 3. Query invalid provider -> raises ProviderException
    with pytest.raises(ProviderException):
        service.get_provider("unsupported_provider_slug")

    # 4. Fetch DOI via service cascade
    pub = await service.fetch_by_doi("10.1186/s13059-023-03001-2", preferred_provider="mock")
    assert pub is not None
    assert pub.title == "Transformer Attention for High-Throughput Genomic Variant Discovery"
