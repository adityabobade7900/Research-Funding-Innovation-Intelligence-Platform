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
