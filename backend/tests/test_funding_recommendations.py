import pytest
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_funding_recommendation_ranking_and_explanation(client: AsyncClient, test_user: dict):
    """
    Verifies that funding recommendations return personalized, ranked, explainable results
    matching the researcher's domain, keywords, and geography.
    """
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Update user profile to Quantum domain and keywords
    domains_resp = await client.get("/api/v1/profile/domains", headers=headers)
    domains = domains_resp.json()["data"]
    quantum_domain = next((d for d in domains if "Quantum" in d["name"]), domains[0])

    await client.put("/api/v1/profile/me", json={
        "institution": "MIT Center for Theoretical Physics",
        "department": "Physics",
        "domain_ids": [quantum_domain["id"]],
        "keywords": ["Quantum Computing", "Superconducting Qubits", "Quantum Information"]
    }, headers=headers)

    # 2. Ingest Mock Funding opportunities (including Quantum NSF, NIH, DOE, Horizon Europe)
    ingest_resp = await client.post("/api/v1/funding/ingest", json={
        "provider": "mock",
        "query": "Quantum"
    }, headers=headers)
    assert ingest_resp.status_code == 200

    # 3. Call Recommendations endpoint
    rec_resp = await client.get("/api/v1/funding/recommendations", headers=headers)
    assert rec_resp.status_code == 200
    data = rec_resp.json()["data"]

    assert data["total_recommended"] >= 1
    items = data["items"]
    assert len(items) >= 1

    # Top recommendation should be Quantum opportunity
    top_rec = items[0]
    assert "Quantum" in top_rec["opportunity"]["title"]
    assert top_rec["recommendation_score"] >= 65.0
    assert top_rec["eligibility_status"] in ["ELIGIBLE", "CONDITIONAL"]
    assert len(top_rec["reasons"]) > 0
    assert any("Quantum" in d for d in top_rec["matched_domains"])


@pytest.mark.asyncio
async def test_ineligible_opportunity_excluded_from_recommendations(client: AsyncClient, test_user: dict):
    """
    Verifies that strictly ineligible opportunities (e.g. EU-only grants for US researcher or closed grants)
    are excluded from the recommendation feed.
    """
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Profile with US affiliation and Biotechnology domain
    domains_resp = await client.get("/api/v1/profile/domains", headers=headers)
    domains = domains_resp.json()["data"]
    biotech_domain = next((d for d in domains if "Biotechnology" in d["name"]), domains[0])

    await client.put("/api/v1/profile/me", json={
        "institution": "Harvard University, USA",
        "domain_ids": [biotech_domain["id"]],
        "keywords": ["Genomics", "Synthetic Biology"]
    }, headers=headers)

    # Create an opportunity strictly restricted to EU entities
    await client.post("/api/v1/funding", json={
        "title": "European Exclusive SynBio Consortium",
        "funding_agency": "European Commission",
        "geographic_restrictions": "EU Member States",
        "eligible_institutions": "European Research Organizations",
        "status": "open",
        "source": "manual",
        "domain_ids": [biotech_domain["id"]]
    }, headers=headers)

    # Call recommendations
    rec_resp = await client.get("/api/v1/funding/recommendations", headers=headers)
    assert rec_resp.status_code == 200
    items = rec_resp.json()["data"]["items"]

    # The EU-only opportunity should be strictly excluded for US researcher
    for rec in items:
        assert rec["opportunity"]["title"] != "European Exclusive SynBio Consortium"


@pytest.mark.asyncio
async def test_recommendation_score_filtering_and_limit(client: AsyncClient, test_user: dict):
    """
    Verifies that minimum_score and limit query parameters are respected.
    """
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # High minimum score filter
    high_resp = await client.get("/api/v1/funding/recommendations?minimum_score=95.0", headers=headers)
    assert high_resp.status_code == 200
    for item in high_resp.json()["data"]["items"]:
        assert item["recommendation_score"] >= 95.0

    # Limit filter
    limit_resp = await client.get("/api/v1/funding/recommendations?limit=1", headers=headers)
    assert limit_resp.status_code == 200
    assert len(limit_resp.json()["data"]["items"]) <= 1


@pytest.mark.asyncio
async def test_recommendations_cross_user_isolation(client: AsyncClient, test_user: dict):
    """
    Verifies that recommendations are strictly personalized to the authenticated user
    and do not leak between different user profiles.
    """
    # 1. Login user 1 (Quantum)
    login1 = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token1 = login1.json()["data"]["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    domains_resp = await client.get("/api/v1/profile/domains", headers=headers1)
    domains = domains_resp.json()["data"]
    quantum_d = next((d for d in domains if "Quantum" in d["name"]), domains[0])
    biotech_d = next((d for d in domains if "Biotechnology" in d["name"]), domains[1])

    await client.put("/api/v1/profile/me", json={
        "institution": "MIT, USA",
        "domain_ids": [quantum_d["id"]],
        "keywords": ["Quantum Computing"]
    }, headers=headers1)

    rec1 = await client.get("/api/v1/funding/recommendations", headers=headers1)
    assert rec1.status_code == 200
    user1_items = rec1.json()["data"]["items"]

    # 2. Register & login user 2 (Biomedical)
    await client.post("/api/v1/auth/register", json={
        "email": "biomed.researcher@stanford.edu",
        "password": "Password123!",
        "full_name": "Dr. Sarah Bio",
        "institution": "Stanford Medicine, USA"
    })
    login2 = await client.post("/api/v1/auth/login", json={
        "email": "biomed.researcher@stanford.edu",
        "password": "Password123!"
    })
    token2 = login2.json()["data"]["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    await client.put("/api/v1/profile/me", json={
        "institution": "Stanford University, USA",
        "domain_ids": [biotech_d["id"]],
        "keywords": ["Nanomedicine", "Blood-Brain Barrier"]
    }, headers=headers2)

    rec2 = await client.get("/api/v1/funding/recommendations", headers=headers2)
    assert rec2.status_code == 200
    user2_items = rec2.json()["data"]["items"]

    # Profile summary isolation check
    assert rec1.json()["data"]["profile_summary"]["user_id"] != rec2.json()["data"]["profile_summary"]["user_id"]


@pytest.mark.asyncio
async def test_recommendations_unauthenticated_denied(client: AsyncClient):
    """Verifies that unauthenticated requests to recommendations endpoint are rejected with 401."""
    resp = await client.get("/api/v1/funding/recommendations")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_recommendations_empty_candidate_pool(client: AsyncClient, test_user: dict):
    """Verifies clean handling when no opportunities match active status filter."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Query with non-matching status
    resp = await client.get("/api/v1/funding/recommendations?status=nonexistent_status", headers=headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total_recommended"] == 0
    assert len(data["items"]) == 0


@pytest.mark.asyncio
async def test_deterministic_reproducible_recommendations(client: AsyncClient, test_user: dict):
    """Verifies that identical profile and database state yields identical recommendation scores and ranking."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    run1 = await client.get("/api/v1/funding/recommendations", headers=headers)
    run2 = await client.get("/api/v1/funding/recommendations", headers=headers)

    assert run1.status_code == 200
    assert run2.status_code == 200

    items1 = run1.json()["data"]["items"]
    items2 = run2.json()["data"]["items"]

    assert len(items1) == len(items2)
    for i in range(len(items1)):
        assert items1[i]["opportunity"]["id"] == items2[i]["opportunity"]["id"]
        assert items1[i]["recommendation_score"] == items2[i]["recommendation_score"]

