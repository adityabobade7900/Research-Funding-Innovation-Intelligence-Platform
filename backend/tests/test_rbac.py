import pytest
from httpx import AsyncClient
from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_rbac_unauthenticated_access_denied(client: AsyncClient):
    """Verifies unauthenticated requests to protected endpoints return 401."""
    resp = await client.get("/api/v1/auth/test/researcher-only")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_rbac_all_four_roles(client: AsyncClient):
    """
    Verifies that:
    1. Researcher can access researcher endpoint, but NOT founder, manager, or admin endpoints.
    2. Startup Founder can access founder endpoint, but NOT researcher, manager, or admin endpoints.
    3. Innovation Manager can access manager endpoint, but NOT researcher, founder, or admin endpoints.
    4. Administrator can access admin endpoint.
    """
    roles_data = [
        ("researcher@test.com", "researcher", "/api/v1/auth/test/researcher-only"),
        ("founder@test.com", "startup_founder", "/api/v1/auth/test/founder-only"),
        ("manager@test.com", "innovation_manager", "/api/v1/auth/test/manager-only"),
        ("admin@test.com", "administrator", "/api/v1/auth/test/admin-only"),
    ]

    tokens = {}
    # Register all 4 users
    for email, role, _ in roles_data:
        reg_resp = await client.post("/api/v1/auth/register", json={
            "email": email,
            "full_name": f"User {role}",
            "password": "Password123!",
            "role": role
        })
        assert reg_resp.status_code == 201
        user_id = reg_resp.json()["data"]["id"]
        
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": email,
            "password": "Password123!"
        })
        assert login_resp.status_code == 200
        tokens[role] = login_resp.json()["data"]["access_token"]

    # 1. Test Researcher Access
    res_headers = {"Authorization": f"Bearer {tokens['researcher']}"}
    assert (await client.get("/api/v1/auth/test/researcher-only", headers=res_headers)).status_code == 200
    assert (await client.get("/api/v1/auth/test/founder-only", headers=res_headers)).status_code == 403
    assert (await client.get("/api/v1/auth/test/manager-only", headers=res_headers)).status_code == 403
    assert (await client.get("/api/v1/auth/test/admin-only", headers=res_headers)).status_code == 403

    # 2. Test Founder Access
    fnd_headers = {"Authorization": f"Bearer {tokens['startup_founder']}"}
    assert (await client.get("/api/v1/auth/test/founder-only", headers=fnd_headers)).status_code == 200
    assert (await client.get("/api/v1/auth/test/researcher-only", headers=fnd_headers)).status_code == 403
    assert (await client.get("/api/v1/auth/test/manager-only", headers=fnd_headers)).status_code == 403
    assert (await client.get("/api/v1/auth/test/admin-only", headers=fnd_headers)).status_code == 403

    # 3. Test Innovation Manager Access
    mgr_headers = {"Authorization": f"Bearer {tokens['innovation_manager']}"}
    assert (await client.get("/api/v1/auth/test/manager-only", headers=mgr_headers)).status_code == 200
    assert (await client.get("/api/v1/auth/test/researcher-only", headers=mgr_headers)).status_code == 403
    assert (await client.get("/api/v1/auth/test/founder-only", headers=mgr_headers)).status_code == 403
    assert (await client.get("/api/v1/auth/test/admin-only", headers=mgr_headers)).status_code == 403

    # 4. Test Administrator Access
    adm_headers = {"Authorization": f"Bearer {tokens['administrator']}"}
    assert (await client.get("/api/v1/auth/test/admin-only", headers=adm_headers)).status_code == 200
