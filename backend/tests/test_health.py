import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Verifies that the root landing endpoint returns 200 OK and welcome payload."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert data["docs"] == "/docs"
    assert data["api_v1"] == "/api/v1"


@pytest.mark.asyncio
async def test_health_check_endpoint(client: AsyncClient):
    """Verifies that the health check endpoint verifies API and database status."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "online"
    assert body["data"]["database"] == "healthy"
