import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_and_update_profile(client: AsyncClient, test_user: dict):
    """Verifies getting profile via /me and updating fields with validation."""
    # 1. Login
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get /me
    me_resp = await client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    me_data = me_resp.json()["data"]
    assert me_data["email"] == test_user["email"]

    # 3. Update profile fields
    update_payload = {
        "full_name": "Dr. Elena Vance, Ph.D.",
        "profile": {
            "institution": "Stanford University",
            "department": "Applied Physics",
            "bio": "Leading research in quantum optics and photonics.",
            "orcid_id": "0000-0002-1825-0097",
            "website": "https://physics.stanford.edu/vance"
        }
    }
    update_resp = await client.put("/api/v1/auth/me", json=update_payload, headers=headers)
    assert update_resp.status_code == 200
    updated_data = update_resp.json()["data"]
    assert updated_data["full_name"] == "Dr. Elena Vance, Ph.D."
    assert updated_data["profile"]["institution"] == "Stanford University"
    assert updated_data["profile"]["department"] == "Applied Physics"
    assert updated_data["profile"]["bio"] == "Leading research in quantum optics and photonics."
    assert updated_data["profile"]["orcid_id"] == "0000-0002-1825-0097"

    # 4. Re-fetch /me to assert persistence
    refetch_resp = await client.get("/api/v1/auth/me", headers=headers)
    assert refetch_resp.status_code == 200
    refetched_data = refetch_resp.json()["data"]
    assert refetched_data["profile"]["institution"] == "Stanford University"
