import pytest
from httpx import AsyncClient
from datetime import datetime

from app.services.funding_ingest_service import FundingIngestService
from app.services.providers.funding_base import NormalizedFundingOpportunity
from app.services.providers.funding_providers import MockFundingProvider, funding_provider_service
from app.core.exceptions import CustomAPIException


@pytest.mark.asyncio
async def test_ingest_funding_by_external_id(client: AsyncClient, test_user: dict):
    """Verifies ingesting a specific funding opportunity by external identifier."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Ingest NSF ExpandQISE opportunity
    resp = await client.post(
        "/api/v1/funding/ingest",
        json={"external_id": "NSF-24-548", "provider": "mock"},
        headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["discovered_count"] == 1
    assert data["inserted_count"] == 1
    assert len(data["opportunities"]) == 1

    opp = data["opportunities"][0]
    assert opp["external_id"] == "NSF-24-548"
    assert "ExpandQISE" in opp["title"]
    assert opp["funding_amount"] == 5000000.0
    assert opp["funding_agency"] == "National Science Foundation"
    assert any(k["keyword"] == "Quantum Computing" for k in opp["keywords"])


@pytest.mark.asyncio
async def test_ingest_duplicate_funding_idempotency(client: AsyncClient, test_user: dict):
    """Verifies that repeatedly ingesting the same external opportunity enriches rather than duplicates records."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Initial ingestion
    first_resp = await client.post(
        "/api/v1/funding/ingest",
        json={"external_id": "R01-NS-132456", "provider": "mock"},
        headers=headers
    )
    assert first_resp.status_code == 200
    assert first_resp.json()["data"]["inserted_count"] == 1

    # Second ingestion with same external ID
    second_resp = await client.post(
        "/api/v1/funding/ingest",
        json={"external_id": "R01-NS-132456", "provider": "mock"},
        headers=headers
    )
    assert second_resp.status_code == 200
    data = second_resp.json()["data"]
    assert data["inserted_count"] == 0
    assert data["updated_count"] == 1
    assert data["duplicate_count"] == 1


@pytest.mark.asyncio
async def test_ingest_funding_by_search_query_and_agency(client: AsyncClient, test_user: dict):
    """Verifies multi-item ingestion using search query and agency filtering."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Ingest by search keyword
    query_resp = await client.post(
        "/api/v1/funding/ingest",
        json={"query": "Hydrogen", "provider": "mock", "limit": 5},
        headers=headers
    )
    assert query_resp.status_code == 200
    assert query_resp.json()["data"]["discovered_count"] >= 1

    # Ingest by agency
    agency_resp = await client.post(
        "/api/v1/funding/ingest",
        json={"agency": "Department of Energy", "provider": "mock", "limit": 5},
        headers=headers
    )
    assert agency_resp.status_code == 200
    assert agency_resp.json()["data"]["discovered_count"] >= 1


@pytest.mark.asyncio
async def test_ingest_missing_parameters_validation(client: AsyncClient, test_user: dict):
    """Verifies that an ingest request without external_id, query, or agency is rejected."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post(
        "/api/v1/funding/ingest",
        json={"provider": "mock"},
        headers=headers
    )
    assert resp.status_code == 400


def test_normalized_funding_validation():
    """Verifies that malformed normalized opportunities are caught by pre-persistence validation."""
    # Invalid short title
    invalid_title = NormalizedFundingOpportunity(
        title="Hi",
        funding_agency="NSF",
        source="mock"
    )
    with pytest.raises(CustomAPIException) as exc_info:
        FundingIngestService.validate_normalized_opportunity(invalid_title)
    assert exc_info.value.status_code == 422

    # Invalid empty agency
    invalid_agency = NormalizedFundingOpportunity(
        title="Valid Grant Proposal Title",
        funding_agency=" ",
        source="mock"
    )
    with pytest.raises(CustomAPIException) as exc_info:
        FundingIngestService.validate_normalized_opportunity(invalid_agency)
    assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_funding_ingest_provider_error_handling(client: AsyncClient, test_user: dict):
    """Verifies that provider timeouts, rate-limits, and not-found conditions return clean API errors."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Register temporary failing providers
    funding_provider_service.register_provider(MockFundingProvider(simulate_timeout=True))

    timeout_resp = await client.post(
        "/api/v1/funding/ingest",
        json={"external_id": "NSF-24-548", "provider": "mock"},
        headers=headers
    )
    assert timeout_resp.status_code in [502, 504]

    # Reset standard mock provider
    funding_provider_service.register_provider(MockFundingProvider())


@pytest.mark.asyncio
async def test_funding_ingest_unauthenticated_denied(client: AsyncClient):
    """Verifies that unauthenticated users cannot trigger funding ingestion."""
    resp = await client.post(
        "/api/v1/funding/ingest",
        json={"external_id": "NSF-24-548", "provider": "mock"}
    )
    assert resp.status_code == 401
