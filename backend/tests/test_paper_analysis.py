import pytest
from httpx import AsyncClient
from unittest.mock import patch

from app.core.exceptions import ProviderServiceException
from app.services.paper_analysis_service import MockPaperAnalyzer, PaperAnalysisService


@pytest.mark.asyncio
async def test_successful_paper_analysis(client: AsyncClient, test_user: dict):
    """
    Verifies successful AI paper analysis extracting all 5 mentor-required facets:
    1. Problem Statement
    2. Methodology
    3. Findings / Contributions
    4. Limitations
    5. Future Research Directions
    """
    # 1. Login
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create rich publication
    payload = {
        "title": "Dual-Species Neutral Atom Surface Codes",
        "authors": "Dr. Vance Adams, Dr. Sarah Connor",
        "abstract": (
            "Fault-tolerant quantum computing requires quantum error correction codes with physical error "
            "rates below threshold, yet scaling 2D Rydberg atom arrays remains hindered by laser phase noise "
            "and two-qubit gate cross-talk. In this work, we propose and demonstrate a dual-species neutral atom "
            "architecture implementing a distance-3 surface code with real-time syndrome extraction. Our methodology "
            "employs optical tweezers to dynamically rearrange rubidium-87 and cesium-133 atoms, minimizing optical "
            "crosstalk while executing transversal Clifford gates. We demonstrate an error detection threshold "
            "reduction of 34% with an average two-qubit gate fidelity of 99.4%, outperforming baseline planar geometries. "
            "However, our system is constrained by atom loss rates during cyclic re-cooling and non-destructive "
            "readout latency exceeding 150 microseconds. Future research will explore 3D optical lattices, continuous "
            "atom replenishment techniques, and fault-tolerant logical qubit shuttling across interconnected atomic modules."
        ),
        "venue": "Nature Quantum Information",
        "doi": "10.1038/s41534-024-00100-x",
        "citation_count": 58,
        "primary_domain": "Quantum Technologies",
        "keywords": ["Quantum Computing", "Neutral Atoms", "Surface Codes"],
        "is_primary_author": True
    }

    create_resp = await client.post("/api/v1/publications", json=payload, headers=headers)
    assert create_resp.status_code == 201
    pub_id = create_resp.json()["data"]["id"]

    # 3. Analyze publication via POST
    analyze_resp = await client.post(f"/api/v1/publications/{pub_id}/analyze", json={}, headers=headers)
    assert analyze_resp.status_code == 200
    data = analyze_resp.json()["data"]

    # 4. Verify all 5 facets
    assert data["publication_id"] == pub_id
    assert data["title"] == payload["title"]
    assert len(data["problem_statement"]) > 20
    assert "fault-tolerant" in data["problem_statement"].lower() or "hindered by" in data["problem_statement"].lower()

    assert len(data["methodology"]) > 20
    assert "optical tweezers" in data["methodology"].lower() or "propose" in data["methodology"].lower()

    assert len(data["findings_contributions"]) > 20
    assert "demonstrate" in data["findings_contributions"].lower() or "reduction" in data["findings_contributions"].lower()

    assert len(data["limitations"]) > 20
    assert "constrained by" in data["limitations"].lower() or "atom loss" in data["limitations"].lower()

    assert len(data["future_research_directions"]) > 20
    assert "future research" in data["future_research_directions"].lower() or "3d optical lattices" in data["future_research_directions"].lower()

    # Verify metadata
    assert data["confidence_score"] >= 0.70
    assert data["analysis_source"] == "title_and_abstract"
    assert data["provider"] == "nlp-heuristic-analyzer"
    assert len(data["key_insights"]) >= 2

    # 5. Verify GET endpoint retrieves consistent analysis
    get_resp = await client.get(f"/api/v1/publications/{pub_id}/analyze", headers=headers)
    assert get_resp.status_code == 200
    get_data = get_resp.json()["data"]
    assert get_data["publication_id"] == pub_id
    assert get_data["problem_statement"] == data["problem_statement"]


@pytest.mark.asyncio
async def test_paper_analysis_publication_not_found(client: AsyncClient, test_user: dict):
    """Verifies that requesting analysis for a non-existent publication returns HTTP 404."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/publications/999999/analyze", json={}, headers=headers)
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_paper_analysis_unauthorized(client: AsyncClient):
    """Verifies that unauthenticated requests to analyze are rejected with HTTP 401."""
    resp = await client.post("/api/v1/publications/1/analyze", json={})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_paper_analysis_insufficient_content(client: AsyncClient, test_user: dict):
    """
    Verifies that publications with missing or inadequate abstract content (< 10 words)
    are rejected with HTTP 422 INSUFFICIENT_CONTENT.
    """
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Publication with insufficient abstract (only 3 words)
    payload = {
        "title": "Brief Abstract Paper",
        "authors": "Dr. Minimalist",
        "abstract": "Too brief abstract.",
        "venue": "Brief Journal",
        "doi": "10.1038/brief-001",
        "citation_count": 0,
        "keywords": ["Short"],
        "is_primary_author": True
    }
    create_resp = await client.post("/api/v1/publications", json=payload, headers=headers)
    assert create_resp.status_code == 201
    pub_id = create_resp.json()["data"]["id"]

    resp = await client.post(f"/api/v1/publications/{pub_id}/analyze", json={}, headers=headers)
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "INSUFFICIENT_CONTENT"


@pytest.mark.asyncio
async def test_paper_analysis_provider_failure(client: AsyncClient, test_user: dict):
    """Verifies that upstream provider failures return HTTP 502 PROVIDER_ERROR."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "title": "Quantum Fault Tolerance Studies",
        "authors": "Dr. Researcher",
        "abstract": "A complete scientific abstract describing extensive quantum fault tolerance studies across many benchmarks.",
        "venue": "Quantum Review",
        "doi": "10.1038/quantum-fail-001",
        "citation_count": 10,
        "keywords": ["Quantum"],
        "is_primary_author": True
    }
    create_resp = await client.post("/api/v1/publications", json=payload, headers=headers)
    assert create_resp.status_code == 201
    pub_id = create_resp.json()["data"]["id"]

    failing_analyzer = MockPaperAnalyzer(simulate_failure=True)

    with patch.object(
        PaperAnalysisService,
        "analyze_publication",
        side_effect=ProviderServiceException("Simulated upstream AI provider failure")
    ):
        resp = await client.post(f"/api/v1/publications/{pub_id}/analyze", json={}, headers=headers)
        assert resp.status_code == 502
        assert resp.json()["error"]["code"] == "PROVIDER_ERROR"


@pytest.mark.asyncio
async def test_structured_five_facet_response_validation(client: AsyncClient, test_user: dict):
    """
    Verifies that the response strictly satisfies the required five-facet contract
    and handles papers where limitations and future work must not be hallucinated.
    """
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Abstract with clear problem, method, and results, but no explicit limitations or future directions
    payload = {
        "title": "High-Efficiency Perovskite Solar Cells",
        "authors": "Dr. Solar Innovator",
        "abstract": (
            "Commercial solar cells face efficiency limitations due to thermal energy loss at bandgap boundaries. "
            "We propose and synthesize a novel tandem perovskite-silicon cell utilizing atomic layer deposition. "
            "Experimental measurements demonstrate a record power conversion efficiency of 32.8% under standard test conditions."
        ),
        "venue": "Energy & Environmental Science",
        "doi": "10.1039/solar-perov-001",
        "citation_count": 25,
        "primary_domain": "Clean Energy",
        "keywords": ["Perovskite", "Solar Cells", "Photovoltaics"],
        "is_primary_author": True
    }
    create_resp = await client.post("/api/v1/publications", json=payload, headers=headers)
    assert create_resp.status_code == 201
    pub_id = create_resp.json()["data"]["id"]

    resp = await client.post(f"/api/v1/publications/{pub_id}/analyze", json={}, headers=headers)
    assert resp.status_code == 200
    data = resp.json()["data"]

    # Verify Problem, Method, Findings
    assert "commercial solar cells" in data["problem_statement"].lower()
    assert "tandem perovskite-silicon" in data["methodology"].lower()
    assert "32.8%" in data["findings_contributions"]

    # Verify Limitations & Future Work are handled transparently without hallucination
    assert "explicit limitations were not stated" in data["limitations"].lower()
    assert "future research directions were not explicitly delineated" in data["future_research_directions"].lower()
