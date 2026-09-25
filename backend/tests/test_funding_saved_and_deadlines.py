import pytest
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_save_and_unsave_funding_opportunity(client: AsyncClient, test_user: dict):
    """Verifies bookmarking/saving, listing, and unsaving funding opportunities with notes."""
    # 1. Login
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create funding opportunity
    deadline_date = (datetime.now(timezone.utc) + timedelta(days=45)).isoformat()
    opp_payload = {
        "title": "Quantum Photonics and Optical Computing Grant",
        "funding_agency": "Department of Energy",
        "description": "Supports research in scalable photonic quantum computing and error correction.",
        "funding_amount": 1200000.0,
        "currency": "USD",
        "application_deadline": deadline_date,
        "opportunity_type": "Grant",
        "status": "open",
        "source": "manual",
        "domain_names": ["Quantum Technologies"],
        "keywords": ["Photonics", "Quantum Computing", "Error Correction"]
    }
    create_resp = await client.post("/api/v1/funding", json=opp_payload, headers=headers)
    assert create_resp.status_code == 201
    opp_id = create_resp.json()["data"]["id"]

    # 3. Save to watchlist with custom notes
    save_resp = await client.post(
        f"/api/v1/funding/{opp_id}/save",
        json={"notes": "High priority RFP for our quantum lab proposal"},
        headers=headers
    )
    assert save_resp.status_code == 200
    save_data = save_resp.json()["data"]
    assert save_data["saved"] is True
    assert save_data["funding_opportunity_id"] == opp_id
    assert save_data["item"]["notes"] == "High priority RFP for our quantum lab proposal"
    assert save_data["item"]["opportunity"]["is_saved"] is True
    assert save_data["item"]["opportunity"]["deadline_urgency"] == "NORMAL"

    # 4. Save again (idempotent update notes)
    save_again = await client.post(
        f"/api/v1/funding/{opp_id}/save",
        json={"notes": "Updated notes: Submission deadline confirmed"},
        headers=headers
    )
    assert save_again.status_code == 200
    assert save_again.json()["data"]["item"]["notes"] == "Updated notes: Submission deadline confirmed"

    # 5. List saved opportunities
    list_saved = await client.get("/api/v1/funding/saved", headers=headers)
    assert list_saved.status_code == 200
    saved_items = list_saved.json()["data"]["items"]
    assert len(saved_items) == 1
    assert saved_items[0]["funding_opportunity_id"] == opp_id
    assert saved_items[0]["opportunity"]["title"] == opp_payload["title"]
    assert saved_items[0]["opportunity"]["is_saved"] is True
    assert saved_items[0]["opportunity"]["days_remaining"] is not None

    # 6. Verify GET /api/v1/funding/{id} reflects is_saved = True for authenticated user
    get_opp = await client.get(f"/api/v1/funding/{opp_id}", headers=headers)
    assert get_opp.status_code == 200
    assert get_opp.json()["data"]["is_saved"] is True

    # 7. Unsave opportunity
    unsave_resp = await client.delete(f"/api/v1/funding/{opp_id}/save", headers=headers)
    assert unsave_resp.status_code == 200
    assert unsave_resp.json()["data"]["saved"] is False

    # 8. Verify list is now empty
    list_after = await client.get("/api/v1/funding/saved", headers=headers)
    assert list_after.status_code == 200
    assert len(list_after.json()["data"]["items"]) == 0

    # 9. Verify GET /api/v1/funding/{id} now reflects is_saved = False
    get_opp_after = await client.get(f"/api/v1/funding/{opp_id}", headers=headers)
    assert get_opp_after.json()["data"]["is_saved"] is False


@pytest.mark.asyncio
async def test_saved_funding_user_isolation(client: AsyncClient, test_user: dict):
    """Verifies that saved watchlists are strictly isolated between researchers."""
    # User A Login
    login_a = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token_a = login_a.json()["data"]["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Register & Login User B
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "researcher_b@university.edu",
            "password": "Password123!",
            "full_name": "Dr. Gordon Freeman",
            "role": "researcher"
        }
    )
    login_b = await client.post(
        "/api/v1/auth/login",
        json={"email": "researcher_b@university.edu", "password": "Password123!"}
    )
    token_b = login_b.json()["data"]["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A creates and saves opportunity
    opp_resp = await client.post(
        "/api/v1/funding",
        json={
            "title": "Private Research Foundation Fellowship",
            "funding_agency": "Simons Foundation",
            "status": "open"
        },
        headers=headers_a
    )
    opp_id = opp_resp.json()["data"]["id"]

    # User A saves it
    await client.post(f"/api/v1/funding/{opp_id}/save", headers=headers_a)

    # User B checks their saved watchlist -> must be empty!
    b_saved = await client.get("/api/v1/funding/saved", headers=headers_b)
    assert b_saved.status_code == 200
    assert len(b_saved.json()["data"]["items"]) == 0

    # User B attempts to unsave User A's bookmark -> 404 (not in User B's watchlist)
    b_unsave = await client.delete(f"/api/v1/funding/{opp_id}/save", headers=headers_b)
    assert b_unsave.status_code == 404

    # User A still has their saved opportunity intact
    a_saved = await client.get("/api/v1/funding/saved", headers=headers_a)
    assert len(a_saved.json()["data"]["items"]) == 1


@pytest.mark.asyncio
async def test_saved_funding_error_cases(client: AsyncClient, test_user: dict):
    """Verifies proper error handling for non-existent opportunities and unauthorized calls."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Save nonexistent opportunity -> 404
    resp = await client.post("/api/v1/funding/999999/save", headers=headers)
    assert resp.status_code == 404

    # 2. Unsave nonexistent opportunity -> 404
    resp = await client.delete("/api/v1/funding/999999/save", headers=headers)
    assert resp.status_code == 404

    # 3. Unauthenticated requests -> 401
    resp = await client.get("/api/v1/funding/saved")
    assert resp.status_code == 401

    resp = await client.post("/api/v1/funding/1/save")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_deadline_calculations_and_urgency(client: AsyncClient, test_user: dict):
    """Verifies deadline tracking, days remaining, and urgency states (ROLLING, NORMAL, URGENT, CRITICAL, EXPIRED)."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    now = datetime.now(timezone.utc)

    # 1. Rolling deadline (None)
    opp1 = await client.post(
        "/api/v1/funding",
        json={"title": "Rolling Grant Opp", "funding_agency": "Agency A", "application_deadline": None},
        headers=headers
    )
    d1 = opp1.json()["data"]
    assert d1["application_deadline"] is None
    assert d1["days_remaining"] is None
    assert d1["is_expired"] is False
    assert d1["deadline_urgency"] == "ROLLING"

    # 2. Normal window (60 days out)
    opp2 = await client.post(
        "/api/v1/funding",
        json={"title": "Normal Grant Opp", "funding_agency": "Agency B", "application_deadline": (now + timedelta(days=60)).isoformat()},
        headers=headers
    )
    d2 = opp2.json()["data"]
    assert d2["days_remaining"] >= 59
    assert d2["is_expired"] is False
    assert d2["deadline_urgency"] == "NORMAL"

    # 3. Urgent window (20 days out)
    opp3 = await client.post(
        "/api/v1/funding",
        json={"title": "Urgent Grant Opp", "funding_agency": "Agency C", "application_deadline": (now + timedelta(days=20)).isoformat()},
        headers=headers
    )
    d3 = opp3.json()["data"]
    assert 14 <= d3["days_remaining"] <= 20
    assert d3["is_expired"] is False
    assert d3["deadline_urgency"] == "URGENT"

    # 4. Critical window (4 days out)
    opp4 = await client.post(
        "/api/v1/funding",
        json={"title": "Critical Grant Opp", "funding_agency": "Agency D", "application_deadline": (now + timedelta(days=4)).isoformat()},
        headers=headers
    )
    d4 = opp4.json()["data"]
    assert 0 <= d4["days_remaining"] <= 4
    assert d4["is_expired"] is False
    assert d4["deadline_urgency"] == "CRITICAL"

    # 5. Expired opportunity (10 days ago)
    opp5 = await client.post(
        "/api/v1/funding",
        json={"title": "Expired Grant Opp", "funding_agency": "Agency E", "application_deadline": (now - timedelta(days=10)).isoformat()},
        headers=headers
    )
    d5 = opp5.json()["data"]
    assert d5["days_remaining"] < 0
    assert d5["is_expired"] is True
    assert d5["deadline_urgency"] == "EXPIRED"


@pytest.mark.asyncio
async def test_recommendations_with_module_3_publication_context(client: AsyncClient, test_user: dict):
    """Verifies that Module 3 publication track records are evaluated to boost funding recommendation relevance."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Setup profile with Quantum domain and affiliation
    domains_resp = await client.get("/api/v1/profile/domains", headers=headers)
    domains = domains_resp.json()["data"]
    quantum_domain = next((d for d in domains if "Quantum" in d["name"]), domains[0])

    await client.put(
        "/api/v1/profile/me",
        json={
            "institution": "MIT Quantum Information Lab",
            "department": "Physics",
            "domain_ids": [quantum_domain["id"]],
            "keywords": ["superconducting qubits", "fault tolerance", "quantum error correction"]
        },
        headers=headers
    )

    # Ingest / create an opportunity matching quantum
    await client.post(
        "/api/v1/funding",
        json={
            "title": "Quantum Error Correction and Qubit Scaling Initiative",
            "funding_agency": "National Science Foundation",
            "funding_amount": 900000.0,
            "currency": "USD",
            "application_deadline": (datetime.now(timezone.utc) + timedelta(days=90)).isoformat(),
            "status": "open",
            "domain_names": ["Quantum Technologies"],
            "keywords": ["superconducting qubits", "fault tolerance", "quantum error correction"]
        },
        headers=headers
    )

    # Request recommendations
    rec_resp = await client.get("/api/v1/funding/recommendations", headers=headers)
    assert rec_resp.status_code == 200
    rec_data = rec_resp.json()["data"]
    assert rec_data["total_recommended"] >= 1

    top_item = rec_data["items"][0]
    assert top_item["recommendation_score"] >= 65.0
    assert any("Quantum" in r for r in top_item["reasons"])
    assert any("superconducting qubits" in kw.lower() for kw in top_item["matched_keywords"])


@pytest.mark.asyncio
async def test_eligibility_insufficient_data_and_mismatch(client: AsyncClient, test_user: dict):
    """
    Verifies that empty profile does not falsely claim ELIGIBLE (returns INSUFFICIENT_DATA),
    and incompatible domains produce INELIGIBLE.
    """
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a specialized Biotech opportunity
    opp_resp = await client.post(
        "/api/v1/funding",
        json={
            "title": "CRISPR Gene Editing and Therapeutics Award",
            "funding_agency": "National Institutes of Health",
            "domain_names": ["Biotechnology & Genomic Sciences"],
            "keywords": ["CRISPR", "Gene Editing", "Therapeutics"],
            "status": "open"
        },
        headers=headers
    )
    opp_id = opp_resp.json()["data"]["id"]

    # Researcher has no profile setup yet -> should evaluate as INSUFFICIENT_DATA
    check1 = await client.get(f"/api/v1/funding/{opp_id}/eligibility", headers=headers)
    assert check1.status_code == 200
    res1 = check1.json()["data"]
    assert res1["eligible"] is False
    assert res1["eligibility_status"] == "INSUFFICIENT_DATA"
    assert len(res1["missing_information"]) > 0

    # 2. Setup researcher in mismatched domain (Quantum Technologies)
    domains_resp = await client.get("/api/v1/profile/domains", headers=headers)
    domains = domains_resp.json()["data"]
    quantum_domain = next((d for d in domains if "Quantum" in d["name"]), domains[0])

    await client.put(
        "/api/v1/profile/me",
        json={
            "institution": "MIT Department of Physics",
            "department": "Physics",
            "domain_ids": [quantum_domain["id"]],
            "keywords": ["Quantum Computing"]
        },
        headers=headers
    )

    # Re-evaluate -> should now evaluate as strictly INELIGIBLE due to domain conflict
    check2 = await client.get(f"/api/v1/funding/{opp_id}/eligibility", headers=headers)
    assert check2.status_code == 200
    res2 = check2.json()["data"]
    print("\nRES2 DEBUG:", res2)
    assert res2["eligible"] is False
    assert res2["eligibility_status"] == "INELIGIBLE"
    assert any("mismatch" in fc.lower() for fc in res2["failed_criteria"])
