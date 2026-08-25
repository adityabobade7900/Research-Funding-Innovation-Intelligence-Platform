import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user_with_profile(client: AsyncClient):
    """Verifies user registration automatically creates an initial profile."""
    payload = {
        "email": "dr.vance@mit.edu",
        "full_name": "Dr. Elena Vance",
        "password": "SecurePassword123!",
        "role": "researcher",
        "institution": "MIT",
        "department": "Quantum Physics"
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["email"] == "dr.vance@mit.edu"
    assert body["data"]["role"] == "researcher"
    assert body["data"]["profile"] is not None
    assert body["data"]["profile"]["institution"] == "MIT"
    assert body["data"]["profile"]["department"] == "Quantum Physics"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user: dict):
    """Verifies that registering with an existing email returns 400 Bad Request."""
    payload = {
        "email": test_user["email"],
        "full_name": "Another User",
        "password": "AnotherPassword123!",
        "role": "researcher"
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "DUPLICATE_RESOURCE"


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user: dict):
    """Verifies successful login returns access token and persistent refresh token."""
    payload = {
        "email": test_user["email"],
        "password": test_user["password"]
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "access_token" in body["data"]
    assert "refresh_token" in body["data"]
    assert body["data"]["user"]["email"] == test_user["email"]


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, test_user: dict):
    """Verifies that incorrect credentials return 401 Unauthorized."""
    payload = {
        "email": test_user["email"],
        "password": "WrongPassword!"
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "AUTHENTICATION_FAILED"


@pytest.mark.asyncio
async def test_refresh_token_rotation_lifecycle(client: AsyncClient, test_user: dict):
    """
    Verifies full persistent refresh token rotation:
    1. Login to get initial refresh token T1.
    2. Call /refresh with T1 -> succeeds and returns new refresh token T2.
    3. Call /refresh with T1 again -> fails with 401 (T1 revoked).
    4. Call /refresh with T2 -> succeeds and returns new refresh token T3.
    """
    # 1. Login to get T1
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    assert login_resp.status_code == 200
    t1 = login_resp.json()["data"]["refresh_token"]

    # 2. Refresh using T1 -> Generates T2
    refresh1_resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": t1})
    assert refresh1_resp.status_code == 200
    t2 = refresh1_resp.json()["data"]["refresh_token"]
    assert t2 != t1

    # 3. Attempt to reuse old T1 -> MUST FAIL with 401
    reuse_resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": t1})
    assert reuse_resp.status_code == 401
    assert reuse_resp.json()["error"]["code"] == "AUTHENTICATION_FAILED"

    # 4. Refresh using active T2 -> Generates T3
    refresh2_resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": t2})
    assert refresh2_resp.status_code == 200
    t3 = refresh2_resp.json()["data"]["refresh_token"]
    assert t3 != t2


@pytest.mark.asyncio
async def test_logout_revocation(client: AsyncClient, test_user: dict):
    """
    Verifies that calling /logout explicitly revokes the persistent refresh token,
    and subsequent /refresh calls with that token fail.
    """
    # 1. Login to get access token and refresh token
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    assert login_resp.status_code == 200
    access_token = login_resp.json()["data"]["access_token"]
    refresh_token = login_resp.json()["data"]["refresh_token"]

    # 2. Call /logout with Authorization header and refresh_token
    headers = {"Authorization": f"Bearer {access_token}"}
    logout_resp = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
        headers=headers
    )
    assert logout_resp.status_code == 200
    assert logout_resp.json()["data"]["revoked"] is True

    # 3. Attempt to refresh with the revoked token -> MUST FAIL with 401
    refresh_resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert refresh_resp.status_code == 401
    assert refresh_resp.json()["error"]["code"] == "AUTHENTICATION_FAILED"


@pytest.mark.asyncio
async def test_register_with_phone_designation_country(client: AsyncClient):
    """Verifies user registration with new optional fields (phone, designation, country)."""
    payload = {
        "email": "dr.curie@radium.org",
        "full_name": "Dr. Marie Curie",
        "password": "SecurePassword123!",
        "phone": "+33 1 42 34 56 78",
        "role": "researcher",
        "institution": "University of Paris",
        "department": "Faculty of Sciences",
        "designation": "Director of Research",
        "country": "France"
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["phone"] == "+33 1 42 34 56 78"
    assert body["data"]["profile"]["designation"] == "Director of Research"
    assert body["data"]["profile"]["country"] == "France"


@pytest.mark.asyncio
async def test_register_malformed_email(client: AsyncClient):
    """Verifies that registration rejects malformed email addresses with 422."""
    payload = {
        "email": "not-a-valid-email",
        "full_name": "Invalid User",
        "password": "SecurePassword123!",
        "role": "researcher"
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient):
    """Verifies that registration rejects passwords shorter than 8 characters."""
    payload = {
        "email": "weak.pass@test.com",
        "full_name": "Weak Pass User",
        "password": "short",
        "role": "researcher"
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_missing_required_fields(client: AsyncClient):
    """Verifies that registration rejects payloads missing required fields."""
    # Missing full_name
    r1 = await client.post("/api/v1/auth/register", json={"email": "a@b.com", "password": "Password123!"})
    assert r1.status_code == 422

    # Missing email
    r2 = await client.post("/api/v1/auth/register", json={"full_name": "User", "password": "Password123!"})
    assert r2.status_code == 422

    # Missing password
    r3 = await client.post("/api/v1/auth/register", json={"full_name": "User", "email": "a@b.com"})
    assert r3.status_code == 422


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Verifies that logging in with a non-existent email returns 401."""
    payload = {
        "email": "ghost.user.999@nonexistent.edu",
        "password": "SomePassword123!"
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_FAILED"


@pytest.mark.asyncio
async def test_login_blank_credentials(client: AsyncClient):
    """Verifies that login with empty/blank credentials fails validation with 422."""
    response = await client.post("/api/v1/auth/login", json={"email": "a@b.com", "password": ""})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_deactivated_user(client: AsyncClient):
    """Verifies that deactivated users cannot log in (401)."""
    from app.models.user import User, UserRole
    from app.core.security import get_password_hash
    from tests.conftest import TestingSessionLocal

    async with TestingSessionLocal() as session:
        deactivated = User(
            email="inactive.user@test.edu",
            hashed_password=get_password_hash("Password123!"),
            full_name="Inactive User",
            role=UserRole.RESEARCHER,
            is_active=False,
            is_superuser=False
        )
        session.add(deactivated)
        await session.commit()

    response = await client.post("/api/v1/auth/login", json={
        "email": "inactive.user@test.edu",
        "password": "Password123!"
    })
    assert response.status_code == 401
    assert "deactivated" in response.json()["error"]["message"].lower()


@pytest.mark.asyncio
async def test_jwt_missing_token_access_denied(client: AsyncClient):
    """Verifies accessing protected /auth/me without a token returns 401."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_jwt_malformed_token_access_denied(client: AsyncClient):
    """Verifies accessing protected endpoint with a garbage token returns 401."""
    headers = {"Authorization": "Bearer not.a.valid.jwt.token"}
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_jwt_expired_token_access_denied(client: AsyncClient, test_user: dict):
    """Verifies that an expired JWT is rejected with 401."""
    from datetime import timedelta
    from app.core.security import create_access_token

    expired_token = create_access_token(
        data={"sub": str(test_user["id"]), "role": "researcher"},
        expires_delta=timedelta(seconds=-10)
    )
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_jwt_invalid_signature_access_denied(client: AsyncClient, test_user: dict):
    """Verifies that a JWT signed with an untrusted secret is rejected."""
    from jose import jwt
    from datetime import datetime, timezone, timedelta

    untrusted_token = jwt.encode(
        {"sub": str(test_user["id"]), "role": "researcher", "exp": datetime.now(timezone.utc) + timedelta(minutes=10)},
        "wrong-secret-key-12345678901234567890",
        algorithm="HS256"
    )
    headers = {"Authorization": f"Bearer {untrusted_token}"}
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_register_public_allowed_roles(client: AsyncClient):
    """Verifies that public registration permits researcher, startup_founder, and innovation_manager."""
    for role in ["researcher", "startup_founder", "innovation_manager"]:
        payload = {
            "email": f"public.{role}@university.edu",
            "full_name": f"User {role}",
            "password": "SecurePassword123!",
            "role": role,
            "institution": "University R&D"
        }
        res = await client.post("/api/v1/auth/register", json=payload)
        assert res.status_code == 201
        assert res.json()["data"]["role"] == role


@pytest.mark.asyncio
async def test_register_administrator_role_forbidden(client: AsyncClient):
    """Verifies that attempting public self-registration with role=administrator is blocked (403)."""
    payload = {
        "email": "hacker.admin@evil.org",
        "full_name": "Unauthorized Admin",
        "password": "Password123!",
        "role": "administrator"
    }
    res = await client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "PERMISSION_DENIED"


