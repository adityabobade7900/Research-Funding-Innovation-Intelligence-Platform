import pytest
from httpx import AsyncClient
from datetime import datetime, timezone, timedelta

from app.models.profile import Profile
from app.models.research_domain import ResearchDomain, ResearchInterest, ProfileKeyword
from app.models.funding import FundingOpportunity, FundingKeyword
from app.services.eligibility_matcher import EligibilityMatcher


@pytest.mark.asyncio
async def test_eligibility_matching_domain_and_keywords(client: AsyncClient, test_user: dict):
    """Verifies that matching research domain and keywords produce a positive eligibility match with high compatibility score."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Update user profile to have Quantum domain and keywords
    domains_resp = await client.get("/api/v1/profile/domains", headers=headers)
    domains = domains_resp.json()["data"]
    quantum_domain = next((d for d in domains if "Quantum" in d["name"]), domains[0])

    await client.put("/api/v1/profile/me", json={
        "institution": "MIT Center for Theoretical Physics",
        "department": "Physics",
        "domain_ids": [quantum_domain["id"]],
        "keywords": ["Quantum Computing", "Superconducting Qubits", "Quantum Information"]
    }, headers=headers)

    # 2. Ingest or create Quantum Funding Opportunity
    ingest_resp = await client.post("/api/v1/funding/ingest", json={
        "external_id": "NSF-24-548",
        "provider": "mock"
    }, headers=headers)
    assert ingest_resp.status_code == 200
    opp_id = ingest_resp.json()["data"]["opportunities"][0]["id"]

    # 3. Check eligibility via REST API
    elig_resp = await client.get(f"/api/v1/funding/{opp_id}/eligibility", headers=headers)
    assert elig_resp.status_code == 200
    result = elig_resp.json()["data"]

    assert result["eligible"] is True
    assert result["eligibility_status"] == "ELIGIBLE"
    assert result["compatibility_score"] >= 70.0
    assert any("Quantum Technologies" in m for m in result["matched_criteria"])
    assert any("Thematic keyword" in m for m in result["matched_criteria"])
    assert len(result["failed_criteria"]) == 0


@pytest.mark.asyncio
async def test_eligibility_domain_mismatch_fails(client: AsyncClient, test_user: dict):
    """Verifies that a researcher in an unrelated domain is flagged as ineligible with clear mismatch reasons."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Set profile domain strictly to Biotechnology
    domains_resp = await client.get("/api/v1/profile/domains", headers=headers)
    domains = domains_resp.json()["data"]
    biotech_domain = next((d for d in domains if "Biotechnology" in d["name"]), domains[0])

    await client.put("/api/v1/profile/me", json={
        "institution": "Harvard Medical School",
        "domain_ids": [biotech_domain["id"]],
        "keywords": ["CRISPR", "Gene Therapy", "Genomics"]
    }, headers=headers)

    # Ingest Quantum Funding Opportunity (which targets Quantum Technologies)
    ingest_resp = await client.post("/api/v1/funding/ingest", json={
        "external_id": "NSF-24-548",
        "provider": "mock"
    }, headers=headers)
    opp_id = ingest_resp.json()["data"]["opportunities"][0]["id"]

    # Check eligibility
    elig_resp = await client.get(f"/api/v1/funding/{opp_id}/eligibility", headers=headers)
    assert elig_resp.status_code == 200
    result = elig_resp.json()["data"]

    assert result["eligible"] is False
    assert result["eligibility_status"] == "INELIGIBLE"
    assert any("Research domain mismatch" in f for f in result["failed_criteria"])


@pytest.mark.asyncio
async def test_eligibility_geographic_mismatch(client: AsyncClient, test_user: dict):
    """Verifies geographic restriction mismatch detection between US opportunities and European affiliations."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Set profile with European affiliation
    await client.put("/api/v1/profile/me", json={
        "institution": "Max Planck Institute of Quantum Optics, Germany",
        "domain_ids": [],
        "keywords": []
    }, headers=headers)

    # Opportunity with strict US restriction
    create_resp = await client.post("/api/v1/funding", json={
        "title": "US Defense Microelectronics Grant",
        "funding_agency": "DARPA",
        "geographic_restrictions": "United States",
        "eligible_institutions": "US Universities & National Labs",
        "status": "open",
        "source": "manual"
    }, headers=headers)
    opp_id = create_resp.json()["data"]["id"]

    # Check eligibility
    elig_resp = await client.get(f"/api/v1/funding/{opp_id}/eligibility", headers=headers)
    assert elig_resp.status_code == 200
    result = elig_resp.json()["data"]

    assert result["eligible"] is False
    assert any("Geographic restriction mismatch" in f for f in result["failed_criteria"])


@pytest.mark.asyncio
async def test_eligibility_expired_or_closed_opportunity(client: AsyncClient, test_user: dict):
    """Verifies that expired deadlines or closed status trigger hard ineligibility."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Opportunity with expired deadline in the past
    past_deadline = (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()
    create_resp = await client.post("/api/v1/funding", json={
        "title": "Historical 2023 Clean Fusion Award",
        "funding_agency": "Department of Energy",
        "application_deadline": past_deadline,
        "status": "closed",
        "source": "manual"
    }, headers=headers)
    opp_id = create_resp.json()["data"]["id"]

    elig_resp = await client.get(f"/api/v1/funding/{opp_id}/eligibility", headers=headers)
    assert elig_resp.status_code == 200
    result = elig_resp.json()["data"]

    assert result["eligible"] is False
    assert result["eligibility_status"] == "INELIGIBLE"
    assert any("closed" in f.lower() or "deadline" in f.lower() for f in result["failed_criteria"])


def test_matcher_insufficient_information_not_failure():
    """Unit test verifying that missing profile data yields INSUFFICIENT_DATA and warnings without false negative failures."""
    empty_profile = Profile(id=1, user_id=1)
    # Profile has no domains, no keywords, no institution

    open_opportunity = FundingOpportunity(
        id=99,
        title="Interdisciplinary Exploratory Research Grant",
        funding_agency="National Science Foundation",
        geographic_restrictions="United States",
        eligible_institutions="Universities",
        status="open"
    )

    result = EligibilityMatcher.evaluate(profile=empty_profile, opportunity=open_opportunity)

    assert result.eligibility_status == "INSUFFICIENT_DATA"
    assert len(result.missing_information) >= 2
    assert len(result.warnings) >= 1
    assert any("institution" in m.lower() for m in result.missing_information)


@pytest.mark.asyncio
async def test_eligibility_unauthenticated_denied(client: AsyncClient):
    """Verifies that unauthenticated requests to the eligibility endpoint return 401 Unauthorized."""
    resp = await client.get("/api/v1/funding/1/eligibility")
    assert resp.status_code == 401
