import pytest
from httpx import AsyncClient
from app.schemas.patent import normalize_patent_number
from app.services.providers.patent_base import NormalizedPatent
from app.services.providers.patent_providers import MockPatentProvider, patent_provider_service
from app.services.providers.base import (
    ProviderTimeoutException,
    ProviderRateLimitException,
    ProviderNotFoundException,
)


def test_patent_number_normalization():
    """Verifies that raw patent numbers are uniformly normalized to uppercase without punctuation."""
    assert normalize_patent_number("us 11,234,567-b2") == "US11234567B2"
    assert normalize_patent_number("US-10987654-B1") == "US10987654B1"
    assert normalize_patent_number(" ep 3456789 a1 ") == "EP3456789A1"
    assert normalize_patent_number("WO/2023/123456") == "WO2023123456"
    assert normalize_patent_number(None) is None
    assert normalize_patent_number("") is None


@pytest.mark.asyncio
async def test_mock_patent_provider_operations():
    """Verifies MockPatentProvider query, search, and error simulation behavior."""
    provider = MockPatentProvider()

    # 1. Fetch by number
    pat = await provider.fetch_by_number("US11234567B2")
    assert pat is not None
    assert "Neutral Atom" in pat.title
    assert pat.patent_classification == "G06N10/00"
    assert pat.citation_count == 28

    # 2. Search patents
    results = await provider.search_patents("mRNA", limit=5)
    assert len(results) >= 1
    assert "Lipid Nanoparticle" in results[0].title

    # 3. Fetch by assignee
    assignee_results = await provider.fetch_by_assignee("QuantumScape", limit=5)
    assert len(assignee_results) >= 1

    # 4. Error simulations
    timeout_provider = MockPatentProvider(simulate_timeout=True)
    with pytest.raises(ProviderTimeoutException):
        await timeout_provider.fetch_by_number("US11234567B2")

    ratelimit_provider = MockPatentProvider(simulate_rate_limit=True)
    with pytest.raises(ProviderRateLimitException):
        await ratelimit_provider.search_patents("Quantum")

    notfound_provider = MockPatentProvider(simulate_not_found=True)
    with pytest.raises(ProviderNotFoundException):
        await notfound_provider.fetch_by_number("US99999999")


@pytest.mark.asyncio
async def test_create_and_get_patent(client: AsyncClient, test_user: dict):
    """Verifies patent creation, profile linkage, and detail retrieval."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    patent_data = {
        "patent_number": "US-12345678-A1",
        "title": "Cryogenic CMOS Control Circuitry for Superconducting Qubits",
        "abstract": "Sub-Kelvin dissipation control ASIC with integrated multiplexed readout channels.",
        "assignee": "Quantum Systems Labs Inc.",
        "inventors": "Dr. Vance Adams, Dr. Sarah Connor",
        "patent_classification": "H01L39/00",
        "technology_domain": "Quantum Technologies",
        "citation_count": 12,
        "source": "manual"
    }

    create_resp = await client.post("/api/v1/patents", json=patent_data, headers=headers)
    assert create_resp.status_code == 201
    pat_id = create_resp.json()["data"]["id"]
    assert create_resp.json()["data"]["patent_number"] == "US12345678A1"

    # Get by ID
    get_resp = await client.get(f"/api/v1/patents/{pat_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["data"]["title"] == patent_data["title"]


@pytest.mark.asyncio
async def test_duplicate_patent_prevention(client: AsyncClient, test_user: dict):
    """Verifies that creating a duplicate patent identifier is rejected."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    patent_data = {
        "patent_number": "US-99887766-B2",
        "title": "Novel CRISPR-Cas Nucleases for Targeted Gene Editing",
        "assignee": "Broad Institute",
        "source": "manual"
    }

    resp1 = await client.post("/api/v1/patents", json=patent_data, headers=headers)
    assert resp1.status_code == 201

    resp2 = await client.post("/api/v1/patents", json=patent_data, headers=headers)
    assert resp2.status_code == 400


@pytest.mark.asyncio
async def test_search_and_filter_patents(client: AsyncClient, test_user: dict):
    """Verifies patent listing with full-text search, domain, and classification filters."""
    # List all
    all_resp = await client.get("/api/v1/patents")
    assert all_resp.status_code == 200
    assert "items" in all_resp.json()["data"]

    # Filter by domain
    domain_resp = await client.get("/api/v1/patents?domain=Quantum Technologies")
    assert domain_resp.status_code == 200

    # Filter by classification
    class_resp = await client.get("/api/v1/patents?classification=H01L")
    assert class_resp.status_code == 200


@pytest.mark.asyncio
async def test_update_and_delete_patent_ownership(client: AsyncClient, test_user: dict):
    """Verifies that only the patent owner or administrator can update or delete a patent."""
    # User A Login
    login_a = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token_a = login_a.json()["data"]["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User B Register & Login
    await client.post("/api/v1/auth/register", json={
        "email": "hacker@evil.org",
        "full_name": "Dr. Unauthorized",
        "password": "SecurePassword123!",
        "role": "researcher"
    })
    login_b = await client.post("/api/v1/auth/login", json={
        "email": "hacker@evil.org",
        "password": "SecurePassword123!"
    })
    token_b = login_b.json()["data"]["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A creates patent
    create_resp = await client.post("/api/v1/patents", json={
        "patent_number": "US-55443322-A",
        "title": "Photonic Waveguide Modulators on Thin-Film Lithium Niobate",
        "assignee": "Harvard SEAS"
    }, headers=headers_a)
    pat_id = create_resp.json()["data"]["id"]

    # User B tries to update -> 403 Forbidden
    update_resp = await client.put(f"/api/v1/patents/{pat_id}", json={"title": "Hacked Title"}, headers=headers_b)
    assert update_resp.status_code == 403

    # User B tries to delete -> 403 Forbidden
    delete_resp = await client.delete(f"/api/v1/patents/{pat_id}", headers=headers_b)
    assert delete_resp.status_code == 403

    # User A updates -> 200
    update_ok = await client.put(f"/api/v1/patents/{pat_id}", json={"title": "Updated Photonic Modulators"}, headers=headers_a)
    assert update_ok.status_code == 200

    # User A deletes -> 200
    del_ok = await client.delete(f"/api/v1/patents/{pat_id}", headers=headers_a)
    assert del_ok.status_code == 200


@pytest.mark.asyncio
async def test_patent_ingest_from_provider(client: AsyncClient, test_user: dict):
    """Verifies controlled patent ingestion and deduplication via Mock provider."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Ingest pre-seeded patent from mock provider
    ingest_resp = await client.post("/api/v1/patents/ingest", json={
        "patent_number": "US-11234567-B2",
        "provider": "mock"
    }, headers=headers)
    assert ingest_resp.status_code == 200
    data = ingest_resp.json()["data"]
    assert data["patent_number"] == "US11234567B2"
    assert "Neutral Atom" in data["title"]
    assert data["citation_count"] == 28

    # Repeated ingest is idempotent
    repeat_resp = await client.post("/api/v1/patents/ingest", json={
        "patent_number": "US11234567B2",
        "provider": "mock"
    }, headers=headers)
    assert repeat_resp.status_code == 200
    assert repeat_resp.json()["data"]["id"] == data["id"]

    # Check appears in /my
    my_resp = await client.get("/api/v1/patents/my", headers=headers)
    assert my_resp.status_code == 200
    assert data["id"] in [p["id"] for p in my_resp.json()["data"]["items"]]
