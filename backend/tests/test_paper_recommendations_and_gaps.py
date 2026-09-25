import pytest
from httpx import AsyncClient
from sqlalchemy import select
from app.models.research_domain import ResearchDomain, ProfileKeyword
from app.models.profile import Profile
from tests.conftest import TestingSessionLocal


# =====================================================================
# PART 1: Profile-Based Paper Recommendations Tests
# =====================================================================

@pytest.mark.asyncio
async def test_recommendations_1_authenticated_researcher_gets_recommendations(client: AsyncClient, test_user: dict):
    """1. authenticated researcher gets recommendations & unauthenticated gets 401."""
    # Unauthenticated request -> 401
    unauth_resp = await client.get("/api/v1/publications/recommendations")
    assert unauth_resp.status_code == 401

    # Authenticated login
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Request recommendations as authenticated user
    rec_resp = await client.get("/api/v1/publications/recommendations", headers=headers)
    assert rec_resp.status_code == 200
    data = rec_resp.json()["data"]
    assert "recommendations" in data
    assert "total_recommended" in data


@pytest.mark.asyncio
async def test_recommendations_2_and_3_domain_and_keywords_affect_ranking(client: AsyncClient, test_user: dict):
    """2 & 3. profile keywords and domain matching affect ranking deterministically."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Configure researcher profile with domain and keyword
    async with TestingSessionLocal() as session:
        dom = ResearchDomain(name="Quantum Technologies", description="Quantum Info")
        session.add(dom)
        await session.flush()

        from app.models.research_domain import profile_domains
        prof_res = await session.execute(
            select(Profile).where(Profile.user_id == test_user["id"])
        )
        prof = prof_res.scalar_one_or_none()
        if not prof:
            prof = Profile(user_id=test_user["id"])
            session.add(prof)
            await session.flush()

        await session.execute(
            profile_domains.insert().values(profile_id=prof.id, domain_id=dom.id)
        )
        session.add(ProfileKeyword(profile_id=prof.id, keyword="surface codes"))
        await session.commit()

    # Add candidate papers directly to DB
    from app.models.publication import Publication, PublicationKeyword
    async with TestingSessionLocal() as session:
        # Candidate 1: Matches domain AND keyword -> Highest relevance
        cand1 = Publication(
            title="High-Fidelity Surface Codes on Neutral Atom Qubits",
            authors="External Author A",
            abstract="Experimental demonstration of distance-3 surface codes with real-time syndrome measurement.",
            primary_domain="Quantum Technologies",
            doi="10.1038/rec-cand-1",
            citation_count=50,
        )
        session.add(cand1)
        await session.flush()
        session.add(PublicationKeyword(publication_id=cand1.id, keyword="surface codes"))

        # Candidate 2: Matches domain ONLY -> Moderate relevance
        cand2 = Publication(
            title="Quantum Cryptography Protocols in Satellite Networks",
            authors="External Author B",
            abstract="Entanglement distribution between low-earth-orbit satellites and ground optical receivers.",
            primary_domain="Quantum Technologies",
            doi="10.1038/rec-cand-2",
            citation_count=10,
        )
        session.add(cand2)
        await session.flush()
        session.add(PublicationKeyword(publication_id=cand2.id, keyword="cryptography"))

        # Candidate 3: Unrelated domain -> Lowest / zero relevance
        cand3 = Publication(
            title="Structural Stability of Geotechnical Embankments",
            authors="External Author C",
            abstract="Soil mechanics and slope stability analysis for civil infrastructure.",
            primary_domain="Civil Engineering",
            doi="10.1038/rec-cand-3",
            citation_count=5,
        )
        session.add(cand3)
        await session.commit()

    rec_resp = await client.get("/api/v1/publications/recommendations?min_score=0.0", headers=headers)
    assert rec_resp.status_code == 200
    items = rec_resp.json()["data"]["recommendations"]

    rec_map = {r["publication_id"]: r for r in items}
    assert cand1.id in rec_map
    assert cand2.id in rec_map

    # Candidate 1 (Domain + Keyword) must outscore Candidate 2 (Domain only)
    assert rec_map[cand1.id]["relevance_score"] > rec_map[cand2.id]["relevance_score"]
    # Candidate 1 reasons must include both domain and keyword
    cand1_reasons = " ".join(rec_map[cand1.id]["reasons"])
    assert "Quantum Technologies" in cand1_reasons
    assert "surface codes" in cand1_reasons


@pytest.mark.asyncio
async def test_recommendations_4_user_own_papers_are_excluded(client: AsyncClient, test_user: dict):
    """4. user's own papers are excluded from recommendations."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Researcher creates a paper authored by themselves
    own_pub = {
        "title": "My Authored Breakthrough In Quantum Computing",
        "authors": test_user["full_name"],
        "abstract": "We describe our personal laboratory findings in quantum technologies.",
        "primary_domain": "Quantum Technologies",
        "keywords": ["Quantum Computing"],
        "is_primary_author": True
    }
    create_resp = await client.post("/api/v1/publications", json=own_pub, headers=headers)
    assert create_resp.status_code == 201
    own_id = create_resp.json()["data"]["id"]

    rec_resp = await client.get("/api/v1/publications/recommendations?min_score=0.0", headers=headers)
    assert rec_resp.status_code == 200
    recommended_ids = [r["publication_id"] for r in rec_resp.json()["data"]["recommendations"]]
    assert own_id not in recommended_ids


@pytest.mark.asyncio
async def test_recommendations_5_incomplete_profile_handled_correctly(client: AsyncClient, test_user: dict):
    """5. incomplete profile handled correctly with advisory warning."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    rec_resp = await client.get("/api/v1/publications/recommendations", headers=headers)
    assert rec_resp.status_code == 200
    data = rec_resp.json()["data"]
    assert "recommendations" in data
    # Incomplete profile returns warning string if missing domains or keywords
    assert data["profile_completeness_warning"] is not None
    assert "profile" in data["profile_completeness_warning"].lower()


@pytest.mark.asyncio
async def test_recommendations_6_no_available_papers_handled_correctly(client: AsyncClient, test_user: dict):
    """6. high minimum threshold with no matching papers handled cleanly without crash."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Request with unattainable score threshold
    rec_resp = await client.get("/api/v1/publications/recommendations?min_score=99.9", headers=headers)
    assert rec_resp.status_code == 200
    data = rec_resp.json()["data"]
    assert data["total_recommended"] == 0
    assert data["recommendations"] == []


# =====================================================================
# PART 2: Macro-Corpus Research Gap Discovery Tests
# =====================================================================

@pytest.mark.asyncio
async def test_research_gaps_1_endpoint_works(client: AsyncClient):
    """1. gaps endpoint works and returns standard ApiResponse structure."""
    resp = await client.get("/api/v1/research-intelligence/gaps")
    assert resp.status_code == 200
    json_data = resp.json()
    assert json_data["success"] is True
    assert "total_gaps" in json_data["data"]
    assert "status" in json_data["data"]
    assert "gaps" in json_data["data"]


@pytest.mark.asyncio
async def test_research_gaps_2_insufficient_corpus_handled_correctly(client: AsyncClient):
    """2. insufficient corpus (< 2 papers in domain) handled correctly without inventing gaps."""
    resp = await client.get("/api/v1/research-intelligence/gaps?domain=NonExistentDomainXYZ")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["status"] == "INSUFFICIENT_DATA"
    assert data["total_gaps"] == 0
    assert "insufficient publications" in data["message"].lower()
    assert "minimum 2 required" in data["message"].lower()


@pytest.mark.asyncio
async def test_research_gaps_3_evidence_is_returned(client: AsyncClient, test_user: dict):
    """3. evidence is returned explaining limitations and future directions."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    p1 = {
        "title": "Cryogenic Optical Control for Neutral Atom Quantum Processors",
        "authors": "Dr. Alice Physicist",
        "abstract": (
            "Neutral atom processors offer high coherence. "
            "Our experimental setup achieves 99.1% fidelity using two-photon optical transitions. "
            "However, the system is severely constrained by optical crosstalk and thermal decoherence in the trap cavity. "
            "Future research will investigate 3D cryogenic shielding and optical cavity stabilization."
        ),
        "primary_domain": "Quantum Technologies",
        "keywords": ["Neutral Atoms", "Optical Control"],
        "is_primary_author": True
    }
    p2 = {
        "title": "Dual-Species Neutral Atom Quantum Error Correction",
        "authors": "Dr. Bob Physicist",
        "abstract": (
            "We demonstrate dual-species Rydberg arrays with real-time syndrome extraction. "
            "The physical error rate is reduced below fault-tolerant thresholds. "
            "A key limitation is the atom loss rate during non-destructive optical imaging. "
            "Future work will explore continuous atom replenishment and logical shuttling."
        ),
        "primary_domain": "Quantum Technologies",
        "keywords": ["Neutral Atoms", "Surface Codes"],
        "is_primary_author": True
    }
    await client.post("/api/v1/publications", json=p1, headers=headers)
    await client.post("/api/v1/publications", json=p2, headers=headers)

    resp = await client.get("/api/v1/research-intelligence/gaps?domain=Quantum%20Technologies")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["status"] == "SUCCESS"
    assert data["total_gaps"] >= 1
    top_gap = data["gaps"][0]
    assert len(top_gap["evidence"]) > 20
    assert "constrained by" in top_gap["evidence"].lower() or "limitation" in top_gap["evidence"].lower()


@pytest.mark.asyncio
async def test_research_gaps_4_supporting_publication_ids_are_valid(client: AsyncClient):
    """4. supporting publication IDs are valid and point to existing publications."""
    resp = await client.get("/api/v1/research-intelligence/gaps?domain=Quantum%20Technologies")
    assert resp.status_code == 200
    data = resp.json()["data"]
    if data["total_gaps"] > 0:
        pub_ids = data["gaps"][0]["supporting_publications"]
        assert len(pub_ids) > 0
        # Verify each publication ID can be retrieved via publication API
        for pid in pub_ids:
            pub_resp = await client.get(f"/api/v1/publications/{pid}")
            assert pub_resp.status_code == 200
            assert pub_resp.json()["data"]["id"] == pid


@pytest.mark.asyncio
async def test_research_gaps_5_no_fabricated_gap_is_returned(client: AsyncClient):
    """5. no fabricated gap is returned for topics completely absent from the corpus."""
    resp = await client.get("/api/v1/research-intelligence/gaps")
    assert resp.status_code == 200
    data = resp.json()["data"]
    for gap in data["gaps"]:
        # Verify confidence is grounded and evidence count is >= 2
        assert gap["evidence_count"] >= 2
        assert 0.0 <= gap["confidence"] <= 1.0
        assert len(gap["supporting_keywords"]) > 0


@pytest.mark.asyncio
async def test_research_gaps_6_authentication_and_authorization(client: AsyncClient, test_user: dict):
    """6. research gaps endpoint works seamlessly for both authenticated and ecosystem researchers."""
    # 1. Open ecosystem query
    resp_anon = await client.get("/api/v1/research-intelligence/gaps")
    assert resp_anon.status_code == 200

    # 2. Authenticated researcher query
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    resp_auth = await client.get("/api/v1/research-intelligence/gaps", headers=headers)
    assert resp_auth.status_code == 200
    assert resp_auth.json()["success"] is True
