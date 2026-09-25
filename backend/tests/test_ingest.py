import pytest
from httpx import AsyncClient
from app.services.providers.service import research_provider_service
from app.services.providers.mock_provider import MockResearchProvider


@pytest.mark.asyncio
async def test_ingest_publication_by_doi(client: AsyncClient, test_user: dict):
    """Verifies controlled single publication ingestion by DOI via Mock provider."""
    # Login
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "doi": "10.1038/s41534-024-00100-1",
        "provider": "mock"
    }

    # Ingest
    ingest_resp = await client.post("/api/v1/publications/ingest", json=payload, headers=headers)
    assert ingest_resp.status_code == 200
    data = ingest_resp.json()["data"]
    assert data["ingested_count"] == 1
    assert len(data["publications"]) == 1
    pub = data["publications"][0]
    assert pub["title"] == "Quantum Error Correction on Neutral Atom Arrays"
    assert pub["doi"] == "10.1038/s41534-024-00100-1"
    assert pub["source"] == "mock"
    assert len(pub["keywords"]) == 3

    # Check that publication appears in user's /my list
    my_resp = await client.get("/api/v1/publications/my", headers=headers)
    assert my_resp.status_code == 200
    my_pub_ids = [p["id"] for p in my_resp.json()["data"]["items"]]
    assert pub["id"] in my_pub_ids


@pytest.mark.asyncio
async def test_ingest_duplicate_doi_idempotency(client: AsyncClient, test_user: dict):
    """Verifies that repeatedly ingesting the exact same DOI is idempotent and does not create duplicate records."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "doi": "https://doi.org/10.1186/s13059-023-03001-2",
        "provider": "mock"
    }

    # First Ingest
    first_resp = await client.post("/api/v1/publications/ingest", json=payload, headers=headers)
    assert first_resp.status_code == 200
    pub_id_1 = first_resp.json()["data"]["publications"][0]["id"]

    # Second Ingest (identical DOI)
    second_resp = await client.post("/api/v1/publications/ingest", json=payload, headers=headers)
    assert second_resp.status_code == 200
    pub_id_2 = second_resp.json()["data"]["publications"][0]["id"]

    assert pub_id_1 == pub_id_2  # Identical entity reused cleanly


@pytest.mark.asyncio
async def test_ingest_by_search_query_and_author(client: AsyncClient, test_user: dict):
    """Verifies search query and author identifier controlled ingestion."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Ingest by Query
    query_resp = await client.post("/api/v1/publications/ingest", json={
        "query": "Zero-Knowledge Proofs",
        "provider": "mock",
        "limit": 5
    }, headers=headers)
    assert query_resp.status_code == 200
    q_data = query_resp.json()["data"]
    assert q_data["ingested_count"] >= 1
    assert any("Zero-Knowledge" in p["title"] for p in q_data["publications"])

    # 2. Ingest by Author
    author_resp = await client.post("/api/v1/publications/ingest", json={
        "author_id": "Elena Vance",
        "provider": "mock",
        "limit": 5
    }, headers=headers)
    assert author_resp.status_code == 200
    a_data = author_resp.json()["data"]
    assert a_data["ingested_count"] >= 1


@pytest.mark.asyncio
async def test_cross_user_ingestion_and_profile_isolation(client: AsyncClient, test_user: dict):
    """
    Verifies that User A and User B can both ingest the same DOI,
    creating individual profile links without modifying or leaking each other's profiles.
    """
    # User A Login
    login_a = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token_a = login_a.json()["data"]["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User B Register & Login
    await client.post("/api/v1/auth/register", json={
        "email": "user.collab@institution.edu",
        "full_name": "Dr. Collab User",
        "password": "SecurePassword123!",
        "role": "researcher"
    })
    login_b = await client.post("/api/v1/auth/login", json={
        "email": "user.collab@institution.edu",
        "password": "SecurePassword123!"
    })
    token_b = login_b.json()["data"]["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    target_doi = "10.1038/s41534-024-00100-1"

    # User A Ingests DOI
    resp_a = await client.post("/api/v1/publications/ingest", json={"doi": target_doi, "provider": "mock"}, headers=headers_a)
    assert resp_a.status_code == 200
    pub_a_id = resp_a.json()["data"]["publications"][0]["id"]

    # User B Ingests same DOI
    resp_b = await client.post("/api/v1/publications/ingest", json={"doi": target_doi, "provider": "mock"}, headers=headers_b)
    assert resp_b.status_code == 200
    pub_b_id = resp_b.json()["data"]["publications"][0]["id"]

    assert pub_a_id == pub_b_id

    # Check both users have it in their respective /my lists
    my_a = await client.get("/api/v1/publications/my", headers=headers_a)
    my_b = await client.get("/api/v1/publications/my", headers=headers_b)
    assert pub_a_id in [p["id"] for p in my_a.json()["data"]["items"]]
    assert pub_b_id in [p["id"] for p in my_b.json()["data"]["items"]]


@pytest.mark.asyncio
async def test_ingest_provider_error_handling(client: AsyncClient, test_user: dict):
    """Verifies that provider errors (not found, timeout, rate limit) are gracefully handled."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Non-existent DOI
    not_found_resp = await client.post("/api/v1/publications/ingest", json={
        "doi": "10.9999/nonexistent.doi.12345",
        "provider": "mock"
    }, headers=headers)
    assert not_found_resp.status_code == 404

    # 2. Timeout simulation
    timeout_mock = MockResearchProvider(simulate_timeout=True)
    research_provider_service.register_provider(timeout_mock)

    timeout_resp = await client.post("/api/v1/publications/ingest", json={
        "doi": "10.1038/sample",
        "provider": "mock"
    }, headers=headers)
    assert timeout_resp.status_code in (502, 504)

    # 3. Rate limit simulation
    ratelimit_mock = MockResearchProvider(simulate_rate_limit=True)
    research_provider_service.register_provider(ratelimit_mock)

    ratelimit_resp = await client.post("/api/v1/publications/ingest", json={
        "query": "Quantum",
        "provider": "mock"
    }, headers=headers)
    assert ratelimit_resp.status_code in (429, 502)

    # Restore default mock provider
    research_provider_service.register_provider(MockResearchProvider())


@pytest.mark.asyncio
async def test_ingest_unauthenticated_denied(client: AsyncClient):
    """Verifies that unauthenticated requests to ingest publications are rejected with 401."""
    resp = await client.post("/api/v1/publications/ingest", json={"doi": "10.1038/s41534-024-00100-1"})
    assert resp.status_code == 401
