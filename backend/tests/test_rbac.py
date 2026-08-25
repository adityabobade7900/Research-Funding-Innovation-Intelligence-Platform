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
    1. Researcher, Startup Founder, and Innovation Manager register via public endpoint.
    2. Attempting to register as Administrator via public endpoint is rejected (403).
    3. Administrator provisioned through backend/operator mechanism can log in.
    4. Researcher can access researcher endpoint, but NOT founder, manager, or admin endpoints.
    5. Startup Founder can access founder endpoint, but NOT researcher, manager, or admin endpoints.
    6. Innovation Manager can access manager endpoint, but NOT researcher, founder, or admin endpoints.
    7. Administrator can access admin endpoint.
    """
    from app.models.user import User, UserRole
    from app.core.security import get_password_hash
    from tests.conftest import TestingSessionLocal

    public_roles = [
        ("researcher@test.com", "researcher", "/api/v1/auth/test/researcher-only"),
        ("founder@test.com", "startup_founder", "/api/v1/auth/test/founder-only"),
        ("manager@test.com", "innovation_manager", "/api/v1/auth/test/manager-only"),
    ]

    tokens = {}
    # 1. Register 3 public roles
    for email, role, _ in public_roles:
        reg_resp = await client.post("/api/v1/auth/register", json={
            "email": email,
            "full_name": f"User {role}",
            "password": "Password123!",
            "role": role
        })
        assert reg_resp.status_code == 201
        
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": email,
            "password": "Password123!"
        })
        assert login_resp.status_code == 200
        tokens[role] = login_resp.json()["data"]["access_token"]

    # 2. Verify that public self-registration with role=administrator is strictly rejected (403)
    admin_reg_attempt = await client.post("/api/v1/auth/register", json={
        "email": "hacker.admin@test.com",
        "full_name": "Hacker Trying Admin",
        "password": "Password123!",
        "role": "administrator"
    })
    assert admin_reg_attempt.status_code == 403
    assert "administrator" in admin_reg_attempt.json()["error"]["message"].lower()

    # 3. Provision Administrator account via backend DB/operator mechanism
    async with TestingSessionLocal() as session:
        admin_user = User(
            email="admin@test.com",
            hashed_password=get_password_hash("AdminPassword123!"),
            full_name="Platform Administrator",
            role=UserRole.ADMINISTRATOR,
            is_active=True,
            is_superuser=True
        )
        session.add(admin_user)
        await session.commit()

    # 4. Administrator logs in normally and receives token
    admin_login = await client.post("/api/v1/auth/login", json={
        "email": "admin@test.com",
        "password": "AdminPassword123!"
    })
    assert admin_login.status_code == 200
    tokens["administrator"] = admin_login.json()["data"]["access_token"]

    # 5. Test Researcher Access
    res_headers = {"Authorization": f"Bearer {tokens['researcher']}"}
    assert (await client.get("/api/v1/auth/test/researcher-only", headers=res_headers)).status_code == 200
    assert (await client.get("/api/v1/auth/test/founder-only", headers=res_headers)).status_code == 403
    assert (await client.get("/api/v1/auth/test/manager-only", headers=res_headers)).status_code == 403
    assert (await client.get("/api/v1/auth/test/admin-only", headers=res_headers)).status_code == 403

    # 6. Test Founder Access
    fnd_headers = {"Authorization": f"Bearer {tokens['startup_founder']}"}
    assert (await client.get("/api/v1/auth/test/founder-only", headers=fnd_headers)).status_code == 200
    assert (await client.get("/api/v1/auth/test/researcher-only", headers=fnd_headers)).status_code == 403
    assert (await client.get("/api/v1/auth/test/manager-only", headers=fnd_headers)).status_code == 403
    assert (await client.get("/api/v1/auth/test/admin-only", headers=fnd_headers)).status_code == 403

    # 7. Test Innovation Manager Access
    mgr_headers = {"Authorization": f"Bearer {tokens['innovation_manager']}"}
    assert (await client.get("/api/v1/auth/test/manager-only", headers=mgr_headers)).status_code == 200
    assert (await client.get("/api/v1/auth/test/researcher-only", headers=mgr_headers)).status_code == 403
    assert (await client.get("/api/v1/auth/test/founder-only", headers=mgr_headers)).status_code == 403
    assert (await client.get("/api/v1/auth/test/admin-only", headers=mgr_headers)).status_code == 403

    # 8. Test Administrator Access
    adm_headers = {"Authorization": f"Bearer {tokens['administrator']}"}
    assert (await client.get("/api/v1/auth/test/admin-only", headers=adm_headers)).status_code == 200
