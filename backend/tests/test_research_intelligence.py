import pytest
import pytest_asyncio
from datetime import datetime, timezone
from httpx import AsyncClient


@pytest_asyncio.fixture
async def seed_intelligence_corpus(client: AsyncClient, test_user: dict):
    """Helper fixture to seed a rich, known multi-year publication corpus."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    sample_pubs = [
        # Quantum Technologies
        {
            "title": "Superconducting Qubit Coherence at Millikelvin Temperatures",
            "authors": "Dr. Elena Vance, Dr. Gordon Freeman",
            "publication_date": "2023-04-15T00:00:00Z",
            "venue": "Physical Review Letters",
            "doi": "10.1103/PhysRevLett.130.123456",
            "citation_count": 45,
            "primary_domain": "Quantum Technologies",
            "keywords": ["Quantum Computing", "Superconducting Qubits", "Coherence"]
        },
        {
            "title": "Quantum Error Mitigation on Noisy Intermediate-Scale Quantum Processors",
            "authors": "Dr. Elena Vance",
            "publication_date": "2024-06-20T00:00:00Z",
            "venue": "Nature Quantum Information",
            "doi": "10.1038/s41534-024-00123-4",
            "citation_count": 80,
            "primary_domain": "Quantum Technologies",
            "keywords": ["Quantum Computing", "Error Mitigation", "NISQ"]
        },
        {
            "title": "Fault-Tolerant Quantum Logic Gates via Surface Codes",
            "authors": "Dr. Elena Vance, Dr. Alice Smith",
            "publication_date": "2025-02-10T00:00:00Z",
            "venue": "IEEE Transactions on Quantum Engineering",
            "doi": "10.1109/TQE.2025.1001",
            "citation_count": 120,
            "primary_domain": "Quantum Technologies",
            "keywords": ["Quantum Computing", "Fault Tolerance", "Surface Codes", "Quantum Logic"]
        },
        {
            "title": "Scalable Optical Interconnects for Distributed Quantum Computers",
            "authors": "Dr. Elena Vance",
            "publication_date": "2026-01-15T00:00:00Z",
            "venue": "Science Advances",
            "doi": "10.1126/sciadv.2026.002",
            "citation_count": 15,
            "primary_domain": "Quantum Technologies",
            "keywords": ["Quantum Computing", "Optical Interconnects", "Distributed Quantum"]
        },
        # Biotechnology
        {
            "title": "CRISPR-Cas12 Targeted Epigenome Editing in Mammalian Cells",
            "authors": "Dr. Sarah Bio, Dr. Robert Chen",
            "publication_date": "2024-03-10T00:00:00Z",
            "venue": "Cell Genomics",
            "doi": "10.1016/j.cellgen.2024.01",
            "citation_count": 60,
            "primary_domain": "Biotechnology & Genomic Sciences",
            "keywords": ["CRISPR", "Epigenomics", "Gene Therapy"]
        },
        {
            "title": "Lipid Nanoparticle Delivery of Base Editors Across the Blood-Brain Barrier",
            "authors": "Dr. Sarah Bio",
            "publication_date": "2025-08-22T00:00:00Z",
            "venue": "Nature Biotechnology",
            "doi": "10.1038/s41587-025-0987-6",
            "citation_count": 95,
            "primary_domain": "Biotechnology & Genomic Sciences",
            "keywords": ["Nanomedicine", "Blood-Brain Barrier", "Base Editing", "Lipid Nanoparticles"]
        },
        {
            "title": "In Vivo Base Editing for Neurodegenerative Disease Prevention",
            "authors": "Dr. Sarah Bio",
            "publication_date": "2026-03-01T00:00:00Z",
            "venue": "The Lancet Neurology",
            "doi": "10.1016/S1474-4422(26)0011",
            "citation_count": 10,
            "primary_domain": "Biotechnology & Genomic Sciences",
            "keywords": ["Gene Therapy", "Nanomedicine", "Neurodegeneration"]
        }
    ]

    for p in sample_pubs:
        await client.post("/api/v1/publications", json=p, headers=headers)

    return headers


@pytest.mark.asyncio
async def test_publication_trends_and_growth_rate(client: AsyncClient, seed_intelligence_corpus: dict):
    """Verifies publication aggregation by year and Year-over-Year (YoY) growth rate calculations."""
    headers = seed_intelligence_corpus

    resp = await client.get("/api/v1/research-intelligence/trends/publications", headers=headers)
    assert resp.status_code == 200
    data = resp.json()["data"]

    assert data["total_publications"] >= 7
    points = data["points"]
    assert len(points) >= 4  # 2023, 2024, 2025, 2026

    # Verify chronological ascending order
    years = [p["year"] for p in points]
    assert years == sorted(years)

    # Verify YoY growth computation exists for later years
    for i in range(1, len(points)):
        prev = points[i-1]["publication_count"]
        curr = points[i]["publication_count"]
        expected_growth = round(((curr - prev) / prev) * 100.0, 1)
        assert points[i]["growth_rate"] == expected_growth


@pytest.mark.asyncio
async def test_domain_trends_and_distribution(client: AsyncClient, seed_intelligence_corpus: dict):
    """Verifies domain publication trajectories, average citation rates, and share percentages."""
    headers = seed_intelligence_corpus

    resp = await client.get("/api/v1/research-intelligence/trends/domains", headers=headers)
    assert resp.status_code == 200
    data = resp.json()["data"]

    assert data["total_domains"] >= 2
    domains = {d["domain"]: d for d in data["domains"]}

    assert "Quantum Technologies" in domains
    quantum = domains["Quantum Technologies"]
    assert quantum["total_publications"] >= 4
    assert quantum["average_citations"] > 0.0

    # Verify yearly distribution share percentages are valid (0 to 100)
    for point in quantum["yearly_distribution"]:
        assert 0.0 <= point["share_percentage"] <= 100.0


@pytest.mark.asyncio
async def test_keyword_trends_and_filtering(client: AsyncClient, seed_intelligence_corpus: dict):
    """Verifies keyword frequency over time and domain scoping."""
    headers = seed_intelligence_corpus

    resp = await client.get("/api/v1/research-intelligence/trends/keywords?min_count=2", headers=headers)
    assert resp.status_code == 200
    data = resp.json()["data"]

    assert data["total_keywords"] >= 1
    kws = {k["keyword"].lower(): k for k in data["keywords"]}
    assert "quantum computing" in kws
    assert kws["quantum computing"]["total_occurrences"] >= 4

    # Filter keywords by specific domain
    bio_resp = await client.get(
        "/api/v1/research-intelligence/trends/keywords",
        params={"domain": "Biotechnology & Genomic Sciences"},
        headers=headers
    )
    assert bio_resp.status_code == 200
    bio_kws = [k["keyword"].lower() for k in bio_resp.json()["data"]["keywords"]]
    assert any("gene therapy" in k or "nanomedicine" in k for k in bio_kws)


@pytest.mark.asyncio
async def test_citation_statistics_and_median(client: AsyncClient, seed_intelligence_corpus: dict):
    """Verifies total, average, median citations, citations by year, and top-cited publications list."""
    headers = seed_intelligence_corpus

    resp = await client.get("/api/v1/research-intelligence/trends/citations", headers=headers)
    assert resp.status_code == 200
    data = resp.json()["data"]

    assert data["total_publications"] >= 7
    assert data["total_citations"] >= (45 + 80 + 120 + 15 + 60 + 95 + 10)
    assert data["average_citations"] > 0.0
    assert data["median_citations"] > 0.0
    assert data["max_citations"] >= 120

    # Verify top cited publications are sorted descending by citation_count
    top_pubs = data["top_cited_publications"]
    assert len(top_pubs) >= 1
    for i in range(len(top_pubs) - 1):
        assert top_pubs[i]["citation_count"] >= top_pubs[i+1]["citation_count"]

    # Verify citations by year structure
    assert len(data["citations_by_year"]) >= 4


@pytest.mark.asyncio
async def test_emerging_topics_statistical_velocity(client: AsyncClient, seed_intelligence_corpus: dict):
    """Verifies statistical velocity model for identifying accelerating and emerging topics."""
    headers = seed_intelligence_corpus

    resp = await client.get("/api/v1/research-intelligence/emerging-topics?recent_years=2&min_count=1", headers=headers)
    assert resp.status_code == 200
    data = resp.json()["data"]

    assert data["total_emerging"] >= 1
    topics = data["topics"]

    # Check top velocity topic properties
    top_topic = topics[0]
    assert top_topic["velocity_score"] > 0.0
    assert top_topic["status"] in ["EMERGING", "ESTABLISHED_GROWING", "STABLE"]
    assert len(top_topic["reasons"]) > 0


@pytest.mark.asyncio
async def test_research_hotspots_calculation(client: AsyncClient, seed_intelligence_corpus: dict):
    """Verifies deterministic hotspot scoring combining volume, growth, and citation density."""
    headers = seed_intelligence_corpus

    resp = await client.get("/api/v1/research-intelligence/hotspots", headers=headers)
    assert resp.status_code == 200
    data = resp.json()["data"]

    assert data["total_hotspots"] >= 1
    hotspots = data["hotspots"]

    top_hotspot = hotspots[0]
    assert top_hotspot["hotspot_score"] >= 0.0
    assert top_hotspot["classification"] in ["CRITICAL_HOTSPOT", "HIGH_ACTIVITY", "MODERATE_ACTIVITY", "EMERGING_NICHE"]
    assert len(top_hotspot["key_drivers"]) > 0


@pytest.mark.asyncio
async def test_date_filtering_and_empty_corpus(client: AsyncClient, seed_intelligence_corpus: dict):
    """Verifies that start_year and end_year filters constrain calculations and handle empty ranges safely."""
    headers = seed_intelligence_corpus

    # Window from 2024 to 2025
    filtered_resp = await client.get("/api/v1/research-intelligence/trends/publications?start_year=2024&end_year=2025", headers=headers)
    assert filtered_resp.status_code == 200
    data = filtered_resp.json()["data"]
    years = [p["year"] for p in data["points"]]
    for yr in years:
        assert 2024 <= yr <= 2025

    # Non-existent future range
    empty_resp = await client.get("/api/v1/research-intelligence/trends/publications?start_year=2090&end_year=2100", headers=headers)
    assert empty_resp.status_code == 200
    assert empty_resp.json()["data"]["total_publications"] == 0
    assert len(empty_resp.json()["data"]["points"]) == 0


@pytest.mark.asyncio
async def test_cross_user_profile_scoped_trends(client: AsyncClient, seed_intelligence_corpus: dict):
    """
    Verifies that my_profile_only=True scopes metrics to the authenticated user's portfolio
    and maintains isolation between researchers.
    """
    # 1. First user already created and owns publications from seed_intelligence_corpus
    user1_headers = seed_intelligence_corpus

    u1_resp = await client.get("/api/v1/research-intelligence/trends/publications?my_profile_only=true", headers=user1_headers)
    assert u1_resp.status_code == 200
    u1_pubs = u1_resp.json()["data"]["total_publications"]
    assert u1_pubs >= 7

    # 2. Register fresh second user with no publications
    await client.post("/api/v1/auth/register", json={
        "email": "dr.blank@cambridge.ac.uk",
        "password": "Password123!",
        "full_name": "Dr. Blank Researcher",
        "institution": "University of Cambridge"
    })
    login2 = await client.post("/api/v1/auth/login", json={
        "email": "dr.blank@cambridge.ac.uk",
        "password": "Password123!"
    })
    user2_token = login2.json()["data"]["access_token"]
    user2_headers = {"Authorization": f"Bearer {user2_token}"}

    u2_resp = await client.get("/api/v1/research-intelligence/trends/publications?my_profile_only=true", headers=user2_headers)
    assert u2_resp.status_code == 200
    # Second user has 0 publications in their own profile
    assert u2_resp.json()["data"]["total_publications"] == 0
