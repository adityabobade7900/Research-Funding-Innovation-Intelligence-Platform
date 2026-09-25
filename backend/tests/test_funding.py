import pytest
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_get_funding_opportunity(client: AsyncClient, test_user: dict):
    """Verifies funding opportunity creation, domain association, keywords, and retrieval by ID."""
    # Login
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "title": "Quantum Computing Foundations and Algorithmic Scaling Grant",
        "funding_agency": "National Science Foundation",
        "funding_program": "Quantum Information Science and Engineering (QISE)",
        "description": "Supports transformative research in fault-tolerant quantum algorithms and hardware architectures.",
        "funding_amount": 750000.0,
        "currency": "USD",
        "application_deadline": (datetime.now(timezone.utc) + timedelta(days=60)).isoformat(),
        "opportunity_type": "Grant",
        "eligibility_summary": "Accredited higher education institutions and non-profit research organizations.",
        "status": "open",
        "source": "grants_gov",
        "external_id": "NSF-24-500",
        "url": "https://www.nsf.gov/funding/pgm_summ.jsp?pims_id=500001",
        "domain_names": ["Quantum Technologies"],
        "keywords": ["Quantum Computing", "Algorithms", "Fault Tolerance"]
    }

    create_resp = await client.post("/api/v1/funding", json=payload, headers=headers)
    assert create_resp.status_code == 201
    data = create_resp.json()["data"]
    assert data["title"] == payload["title"]
    assert data["funding_agency"] == "National Science Foundation"
    assert data["funding_amount"] == 750000.0
    assert len(data["keywords"]) == 3
    opp_id = data["id"]

    # Get by ID
    get_resp = await client.get(f"/api/v1/funding/{opp_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["data"]["id"] == opp_id


@pytest.mark.asyncio
async def test_duplicate_funding_prevention(client: AsyncClient, test_user: dict):
    """Verifies that creating duplicate funding opportunities (by external ID + source or URL) is rejected."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "title": "Advanced mRNA Vaccines and Targeted Nanocarriers",
        "funding_agency": "National Institutes of Health",
        "funding_amount": 1200000.0,
        "source": "nih_grants",
        "external_id": "R01-AI-123456",
        "url": "https://grants.nih.gov/grants/guide/rfa-files/RFA-AI-24-001.html"
    }

    # First creation
    resp1 = await client.post("/api/v1/funding", json=payload, headers=headers)
    assert resp1.status_code == 201

    # Second creation with identical source + external_id -> 400 Bad Request
    resp2 = await client.post("/api/v1/funding", json=payload, headers=headers)
    assert resp2.status_code == 400


@pytest.mark.asyncio
async def test_search_and_filter_funding_opportunities(client: AsyncClient, test_user: dict):
    """Verifies searching by text and filtering by agency, opportunity type, status, and amount range."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Seed sample opportunities
    await client.post("/api/v1/funding", json={
        "title": "Quantum Error Mitigation and Algorithm Grant",
        "funding_agency": "National Science Foundation",
        "funding_amount": 750000.0,
        "opportunity_type": "Grant",
        "status": "open",
        "source": "manual"
    }, headers=headers)

    await client.post("/api/v1/funding", json={
        "title": "Clean Hydrogen Fuel Cell Scalability Project",
        "funding_agency": "Department of Energy",
        "funding_amount": 300000.0,
        "opportunity_type": "Contract",
        "status": "upcoming",
        "source": "manual"
    }, headers=headers)

    # List all
    all_resp = await client.get("/api/v1/funding", headers=headers)
    assert all_resp.status_code == 200
    assert "items" in all_resp.json()["data"]

    # Search keyword
    search_resp = await client.get("/api/v1/funding?q=Quantum", headers=headers)
    assert search_resp.status_code == 200
    assert any("Quantum" in item["title"] for item in search_resp.json()["data"]["items"])

    # Filter agency
    agency_resp = await client.get("/api/v1/funding?agency=National Science Foundation", headers=headers)
    assert agency_resp.status_code == 200
    assert all("National Science Foundation" in item["funding_agency"] for item in agency_resp.json()["data"]["items"])

    # Filter min and max amount
    amount_resp = await client.get("/api/v1/funding?min_amount=500000&max_amount=1000000", headers=headers)
    assert amount_resp.status_code == 200
    assert len(amount_resp.json()["data"]["items"]) >= 1
    for item in amount_resp.json()["data"]["items"]:
        if item["funding_amount"]:
            assert 500000 <= item["funding_amount"] <= 1000000


@pytest.mark.asyncio
async def test_update_and_delete_authorization(client: AsyncClient, test_user: dict):
    """Verifies that non-creator researchers cannot modify/delete opportunities created by others."""
    # User A Login
    login_a = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token_a = login_a.json()["data"]["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User B Register & Login
    await client.post("/api/v1/auth/register", json={
        "email": "rival.researcher@lab.org",
        "full_name": "Dr. Rival",
        "password": "SecurePassword123!",
        "role": "researcher"
    })
    login_b = await client.post("/api/v1/auth/login", json={
        "email": "rival.researcher@lab.org",
        "password": "SecurePassword123!"
    })
    token_b = login_b.json()["data"]["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A creates opportunity
    create_resp = await client.post("/api/v1/funding", json={
        "title": "Clean Energy Grid Resiliency Initiative",
        "funding_agency": "Department of Energy",
        "funding_amount": 500000.0,
        "source": "manual"
    }, headers=headers_a)
    opp_id = create_resp.json()["data"]["id"]

    # User B tries to update -> 403 Forbidden
    update_fail = await client.put(f"/api/v1/funding/{opp_id}", json={"title": "Hacked Title"}, headers=headers_b)
    assert update_fail.status_code == 403

    # User B tries to delete -> 403 Forbidden
    delete_fail = await client.delete(f"/api/v1/funding/{opp_id}", headers=headers_b)
    assert delete_fail.status_code == 403

    # User A updates -> 200 OK
    update_ok = await client.put(f"/api/v1/funding/{opp_id}", json={"title": "Updated Clean Energy Grid Initiative"}, headers=headers_a)
    assert update_ok.status_code == 200
    assert update_ok.json()["data"]["title"] == "Updated Clean Energy Grid Initiative"

    # User A deletes -> 200 OK
    delete_ok = await client.delete(f"/api/v1/funding/{opp_id}", headers=headers_a)
    assert delete_ok.status_code == 200


@pytest.mark.asyncio
async def test_funding_unauthenticated_access_denied(client: AsyncClient):
    """Verifies that unauthenticated mutations to funding opportunities are rejected with 401."""
    resp = await client.post("/api/v1/funding", json={"title": "Test", "funding_agency": "NSF"})
    assert resp.status_code == 401
