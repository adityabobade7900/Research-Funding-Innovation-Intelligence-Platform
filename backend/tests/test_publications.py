import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_get_publication(client: AsyncClient, test_user: dict):
    """Verifies creating a publication and fetching it by ID and via /my endpoint."""
    # Login
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "title": "Scalable Fault-Tolerant Quantum Computation with Neutral Atoms",
        "authors": "Dr. Vance Adams, Dr. Sarah Connor",
        "abstract": "We demonstrate programmable quantum logic gates on an array of 256 neutral atoms.",
        "publication_date": "2024-03-15T00:00:00Z",
        "venue": "Nature Physics",
        "doi": "10.1038/s41567-024-0001",
        "citation_count": 42,
        "primary_domain": "Quantum Technologies",
        "keywords": ["Quantum Computing", "Neutral Atoms", "Rydberg Gates"],
        "is_primary_author": True
    }

    # Create publication
    create_resp = await client.post("/api/v1/publications", json=payload, headers=headers)
    assert create_resp.status_code == 201
    pub = create_resp.json()["data"]
    assert pub["title"] == payload["title"]
    assert pub["doi"] == "10.1038/s41567-024-0001"
    assert pub["citation_count"] == 42
    assert len(pub["keywords"]) == 3
    pub_id = pub["id"]

    # Fetch by ID
    get_resp = await client.get(f"/api/v1/publications/{pub_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["data"]["venue"] == "Nature Physics"

    # Fetch via /my
    my_resp = await client.get("/api/v1/publications/my", headers=headers)
    assert my_resp.status_code == 200
    assert my_resp.json()["data"]["total"] >= 1
    my_ids = [p["id"] for p in my_resp.json()["data"]["items"]]
    assert pub_id in my_ids


@pytest.mark.asyncio
async def test_duplicate_doi_handling(client: AsyncClient, test_user: dict):
    """
    Verifies duplicate prevention:
    - Attempting to re-add the exact same DOI to the same profile returns HTTP 409 Duplicate.
    - Adding the same DOI from another researcher's account links the existing record to their profile.
    """
    # 1. Login User A
    login_a = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token_a = login_a.json()["data"]["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    payload = {
        "title": "Quantum Circuit Synthesis with T-Count Optimization",
        "authors": "Dr. Vance Adams",
        "doi": "https://doi.org/10.1103/PhysRevA.99.012345",
        "citation_count": 15,
        "primary_domain": "Quantum Technologies"
    }

    create_a = await client.post("/api/v1/publications", json=payload, headers=headers_a)
    assert create_a.status_code == 201
    pub_id = create_a.json()["data"]["id"]
    # Verify DOI was normalized
    assert create_a.json()["data"]["doi"] == "10.1103/physreva.99.012345"

    # User A tries to add it again -> 400 Bad Request / 409 Conflict
    duplicate_a = await client.post("/api/v1/publications", json=payload, headers=headers_a)
    assert duplicate_a.status_code in (400, 409)

    # 2. Register User B and add the same DOI (co-author scenario) -> Links to existing record
    await client.post("/api/v1/auth/register", json={
        "email": "coauthor@mit.edu",
        "full_name": "Dr. Coauthor",
        "password": "SecurePassword123!",
        "role": "researcher"
    })
    login_b = await client.post("/api/v1/auth/login", json={
        "email": "coauthor@mit.edu",
        "password": "SecurePassword123!"
    })
    token_b = login_b.json()["data"]["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    create_b = await client.post("/api/v1/publications", json=payload, headers=headers_b)
    assert create_b.status_code == 201
    assert create_b.json()["data"]["id"] == pub_id  # Reused identical publication entity


@pytest.mark.asyncio
async def test_search_and_filter_publications(client: AsyncClient, test_user: dict):
    """Verifies searching by keyword and filtering by domain, venue, and year."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Add AI publication
    await client.post("/api/v1/publications", json={
        "title": "Transformer Attention Mechanisms for Genomic Sequence Prediction",
        "authors": "Dr. Deep Bio",
        "venue": "Bioinformatics Journal",
        "publication_date": "2023-06-10T00:00:00Z",
        "citation_count": 88,
        "primary_domain": "Biotechnology & Genomic Sciences",
        "keywords": ["Transformers", "Genomics"]
    }, headers=headers)

    # Search by text query
    search_resp = await client.get("/api/v1/publications?q=Genomic Sequence")
    assert search_resp.status_code == 200
    assert search_resp.json()["data"]["total"] >= 1
    assert any("Genomic Sequence" in p["title"] for p in search_resp.json()["data"]["items"])

    # Filter by domain
    domain_resp = await client.get("/api/v1/publications?domain=Biotechnology")
    assert domain_resp.status_code == 200
    assert all("Biotechnology" in p["primary_domain"] for p in domain_resp.json()["data"]["items"])

    # Filter by year
    year_resp = await client.get("/api/v1/publications?year=2023")
    assert year_resp.status_code == 200
    assert year_resp.json()["data"]["total"] >= 1


@pytest.mark.asyncio
async def test_update_and_delete_ownership_enforcement(client: AsyncClient, test_user: dict):
    """
    Verifies that only the publication owner or admin can update/delete,
    and unauthorized users are blocked with 403 Forbidden.
    """
    # 1. Login User A and create publication
    login_a = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token_a = login_a.json()["data"]["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    create_resp = await client.post("/api/v1/publications", json={
        "title": "Novel Superconducting Metamaterials for Microwave Shielding",
        "authors": "Dr. Vance Adams",
        "venue": "Physical Review Letters",
        "citation_count": 5
    }, headers=headers_a)
    pub_id = create_resp.json()["data"]["id"]

    # 2. Register User B
    await client.post("/api/v1/auth/register", json={
        "email": "unauthorized.user@domain.com",
        "full_name": "Unauthorized User",
        "password": "SecurePassword123!",
        "role": "researcher"
    })
    login_b = await client.post("/api/v1/auth/login", json={
        "email": "unauthorized.user@domain.com",
        "password": "SecurePassword123!"
    })
    token_b = login_b.json()["data"]["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User B tries to update User A's publication -> 403 Forbidden
    update_fail = await client.put(f"/api/v1/publications/{pub_id}", json={
        "title": "Hijacked Title"
    }, headers=headers_b)
    assert update_fail.status_code == 403

    # User B tries to delete User A's publication -> 403 Forbidden
    delete_fail = await client.delete(f"/api/v1/publications/{pub_id}", headers=headers_b)
    assert delete_fail.status_code == 403

    # 3. User A successfully updates
    update_success = await client.put(f"/api/v1/publications/{pub_id}", json={
        "citation_count": 12,
        "venue": "PRL (Updated)"
    }, headers=headers_a)
    assert update_success.status_code == 200
    assert update_success.json()["data"]["citation_count"] == 12

    # 4. User A successfully deletes
    delete_success = await client.delete(f"/api/v1/publications/{pub_id}", headers=headers_a)
    assert delete_success.status_code == 200

    # Confirm it's gone from /my
    my_after = await client.get("/api/v1/publications/my", headers=headers_a)
    my_ids_after = [p["id"] for p in my_after.json()["data"]["items"]]
    assert pub_id not in my_ids_after
