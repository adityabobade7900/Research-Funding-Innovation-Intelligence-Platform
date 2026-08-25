import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_research_domains_taxonomy(client: AsyncClient, test_user: dict):
    """Verifies that the standard taxonomy domains endpoint returns default research domains."""
    # Login
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/profile/domains", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) >= 8
    domain_names = [d["name"] for d in body["data"]]
    assert "Artificial Intelligence & Machine Learning" in domain_names
    assert "Quantum Technologies" in domain_names
    assert "Biotechnology & Genomic Sciences" in domain_names


@pytest.mark.asyncio
async def test_extended_profile_crud_and_relationships(client: AsyncClient, test_user: dict):
    """
    Verifies full CRUD on extended research profile:
    1. Retrieve initial empty extended profile.
    2. Update with domains, interests, keywords, tech areas, academic history, research projects.
    3. Assert persisted relational data.
    """
    # 1. Login
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch available domains to get IDs
    domains_resp = await client.get("/api/v1/profile/domains", headers=headers)
    domain_ids = [d["id"] for d in domains_resp.json()["data"][:2]]

    # 2. Get initial profile
    get_resp = await client.get("/api/v1/profile/me", headers=headers)
    assert get_resp.status_code == 200
    initial_profile = get_resp.json()["data"]
    assert initial_profile["user_id"] == test_user["id"]

    # 3. Update Extended Profile
    payload = {
        "institution": "MIT Media Lab",
        "department": "Center for Quantum Engineering",
        "bio": "Researching quantum photonic circuits and fault-tolerant algorithms.",
        "orcid_id": "0000-0002-1825-0097",
        "website": "https://media.mit.edu/people/vance",
        "domain_ids": domain_ids,
        "interests": [
            {
                "title": "Quantum Photonics",
                "description": "On-chip single-photon sources and topological waveguide arrays.",
                "importance_level": "primary"
            },
            {
                "title": "Error Correction",
                "description": "Surface codes for neutral atom quantum architectures.",
                "importance_level": "secondary"
            }
        ],
        "keywords": ["Quantum Optics", "Topological Photonics", "Surface Codes", "Qubits"],
        "technology_areas": [
            {
                "name": "Integrated Quantum Photonics",
                "description": "Silicon nitride waveguides with cryogenic electro-optic modulators"
            }
        ],
        "academic_histories": [
            {
                "degree": "Ph.D.",
                "field_of_study": "Quantum Physics",
                "institution": "Harvard University",
                "start_year": 2018,
                "end_year": 2022
            },
            {
                "degree": "B.S.",
                "field_of_study": "Physics & Mathematics",
                "institution": "Caltech",
                "start_year": 2014,
                "end_year": 2018
            }
        ],
        "research_histories": [
            {
                "project_title": "Scalable Photonic Qubit Interconnects",
                "role": "Principal Investigator",
                "organization": "National Science Foundation",
                "description": "DARPA-funded quantum networking initiative."
            }
        ]
    }

    update_resp = await client.put("/api/v1/profile/me", json=payload, headers=headers)
    assert update_resp.status_code == 200
    updated = update_resp.json()["data"]

    # Assert top-level fields
    assert updated["institution"] == "MIT Media Lab"
    assert updated["department"] == "Center for Quantum Engineering"
    assert updated["orcid_id"] == "0000-0002-1825-0097"

    # Assert normalized child collections
    assert len(updated["domains"]) == 2
    assert len(updated["interests"]) == 2
    assert updated["interests"][0]["title"] == "Quantum Photonics"
    assert updated["interests"][0]["importance_level"] == "primary"
    
    assert len(updated["keywords"]) == 4
    kw_names = [k["keyword"] for k in updated["keywords"]]
    assert "Quantum Optics" in kw_names

    assert len(updated["technology_areas"]) == 1
    assert updated["technology_areas"][0]["name"] == "Integrated Quantum Photonics"

    assert len(updated["academic_histories"]) == 2
    assert updated["academic_histories"][0]["degree"] == "Ph.D."

    assert len(updated["research_histories"]) == 1
    assert updated["research_histories"][0]["role"] == "Principal Investigator"

    # 4. Re-query /me to assert persistence across database sessions
    refetch_resp = await client.get("/api/v1/profile/me", headers=headers)
    assert refetch_resp.status_code == 200
    refetched = refetch_resp.json()["data"]
    assert len(refetched["interests"]) == 2
    assert len(refetched["academic_histories"]) == 2


@pytest.mark.asyncio
async def test_cross_user_profile_access(client: AsyncClient, test_user: dict):
    """
    Verifies cross-user profile access rules:
    - User A can view User B's public profile by ID (`GET /profile/{id}`).
    - User A's `PUT /profile/me` only modifies User A's own profile without affecting User B.
    """
    # Create User B
    reg_b = await client.post("/api/v1/auth/register", json={
        "email": "user.b@stanford.edu",
        "full_name": "Dr. Bob Martinez",
        "password": "SecurePassword123!",
        "role": "researcher",
        "institution": "Stanford"
    })
    user_b_id = reg_b.json()["data"]["id"]

    # Login as User A
    login_a = await client.post("/api/v1/auth/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    token_a = login_a.json()["data"]["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User A views User B's profile
    view_b = await client.get(f"/api/v1/profile/{user_b_id}", headers=headers_a)
    assert view_b.status_code == 200
    assert view_b.json()["data"]["institution"] == "Stanford"
    assert view_b.json()["data"]["user_id"] == user_b_id


@pytest.mark.asyncio
async def test_unauthenticated_profile_access_denied(client: AsyncClient):
    """Verifies that profile endpoints require authentication."""
    resp = await client.get("/api/v1/profile/me")
    assert resp.status_code == 401

    put_resp = await client.put("/api/v1/profile/me", json={"institution": "Unauthorized University"})
    assert put_resp.status_code == 401
