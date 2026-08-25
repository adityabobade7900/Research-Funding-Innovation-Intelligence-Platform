import pytest
import pytest_asyncio
from datetime import datetime, timezone
from httpx import AsyncClient

from tests.conftest import TestingSessionLocal
from app.models.patent import Patent, profile_patents
from app.models.user import User, UserRole
from app.models.profile import Profile
from app.core.security import get_password_hash


@pytest_asyncio.fixture
async def tech_patent_corpus():
    """
    Creates a rich deterministic patent corpus for technology intelligence and whitespace testing.
    """
    patents_data = [
        # Quantum Computing (High Activity, High Growth)
        {
            "patent_number": "US10111222B2",
            "title": "Superconducting Qubit Coupler for Fault-Tolerant Quantum Processor",
            "assignee": "IBM Corporation",
            "technology_domain": "Quantum Computing",
            "patent_classification": "G06N 10/00",
            "citation_count": 28,
            "filing_date": datetime(2021, 3, 15, tzinfo=timezone.utc),
            "publication_date": datetime(2022, 9, 20, tzinfo=timezone.utc),
        },
        {
            "patent_number": "US10333444B2",
            "title": "Quantum Error Mitigation in Multi-Qubit Systems",
            "assignee": "IBM Corporation",
            "technology_domain": "Quantum Computing",
            "patent_classification": "G06N 10/00",
            "citation_count": 14,
            "filing_date": datetime(2024, 1, 10, tzinfo=timezone.utc),
            "publication_date": datetime(2024, 4, 5, tzinfo=timezone.utc),
        },
        {
            "patent_number": "US10555666B2",
            "title": "Cryogenic Control Circuitry for Scalable Quantum Computing",
            "assignee": "Google LLC",
            "technology_domain": "Quantum Computing",
            "patent_classification": "G06N 10/00",
            "citation_count": 32,
            "filing_date": datetime(2024, 6, 12, tzinfo=timezone.utc),
            "publication_date": datetime(2024, 11, 30, tzinfo=timezone.utc),
        },
        # Artificial Intelligence (High Activity, Steady Growth)
        {
            "patent_number": "US11223344A1",
            "title": "Sparse Mixture-of-Experts Neural Network Architecture",
            "assignee": "Google LLC",
            "technology_domain": "Artificial Intelligence",
            "patent_classification": "G06N 3/08",
            "citation_count": 45,
            "filing_date": datetime(2024, 8, 20, tzinfo=timezone.utc),
            "publication_date": datetime(2025, 2, 15, tzinfo=timezone.utc),
        },
        {
            "patent_number": "US11445566B2",
            "title": "Reinforcement Learning with Transformer Policy Representation",
            "assignee": "Microsoft Corporation",
            "technology_domain": "Artificial Intelligence",
            "patent_classification": "G06N 3/00",
            "citation_count": 19,
            "filing_date": datetime(2022, 11, 5, tzinfo=timezone.utc),
            "publication_date": datetime(2023, 8, 14, tzinfo=timezone.utc),
        },
        {
            "patent_number": "EP3789012A1",
            "title": "Self-Supervised Visual Representation Learning System",
            "assignee": "DeepMind Technologies",
            "technology_domain": "Artificial Intelligence",
            "patent_classification": "G06N 3/08",
            "citation_count": 8,
            "filing_date": datetime(2023, 4, 18, tzinfo=timezone.utc),
            "publication_date": datetime(2024, 10, 22, tzinfo=timezone.utc),
        },
        # Biotechnology / Genomics (Moderate Activity)
        {
            "patent_number": "WO2023112233A1",
            "title": "Engineered Cas12 Nucleases for Targeted Epigenome Editing",
            "assignee": "Broad Institute",
            "technology_domain": "Biotechnology",
            "patent_classification": "C12N 15/113",
            "citation_count": 60,
            "filing_date": datetime(2023, 2, 14, tzinfo=timezone.utc),
            "publication_date": datetime(2023, 8, 17, tzinfo=timezone.utc),
        },
        {
            "patent_number": "US11889900B2",
            "title": "Lipid Nanoparticle Formulations for mRNA Delivery",
            "assignee": "ModernaTX",
            "technology_domain": "Biotechnology",
            "patent_classification": "A61K 9/51",
            "citation_count": 42,
            "filing_date": datetime(2021, 5, 30, tzinfo=timezone.utc),
            "publication_date": datetime(2022, 12, 10, tzinfo=timezone.utc),
        },
        # Clean Energy / Solid State Batteries (Low Activity / Whitespace Candidate)
        {
            "patent_number": "US10999888A1",
            "title": "Solid Electrolyte Interface for High-Capacity Lithium-Metal Battery",
            "assignee": "QuantumScape",
            "technology_domain": "Clean Energy",
            "patent_classification": "H01M 10/0562",
            "citation_count": 3,
            "filing_date": datetime(2020, 9, 10, tzinfo=timezone.utc),
            "publication_date": datetime(2021, 3, 25, tzinfo=timezone.utc),
        },
        # Synthetic Biology (Sparse / Single Patent Whitespace Gap)
        {
            "patent_number": "US10777888A1",
            "title": "Microbial Bioreactor for Carbon Dioxide Bio-Fixation",
            "assignee": "Ginkgo Bioworks",
            "technology_domain": "Synthetic Biology",
            "patent_classification": "C12P 7/18",
            "citation_count": 1,
            "filing_date": datetime(2019, 7, 10, tzinfo=timezone.utc),
            "publication_date": datetime(2020, 1, 20, tzinfo=timezone.utc),
        },
    ]

    async with TestingSessionLocal() as session:
        created_patents = []
        for p_data in patents_data:
            patent = Patent(
                patent_number=p_data["patent_number"],
                title=p_data["title"],
                assignee=p_data["assignee"],
                technology_domain=p_data["technology_domain"],
                patent_classification=p_data["patent_classification"],
                citation_count=p_data["citation_count"],
                filing_date=p_data["filing_date"],
                publication_date=p_data["publication_date"],
                source="test_registry",
            )
            session.add(patent)
            created_patents.append(patent)
        await session.commit()

        # Re-query
        for p in created_patents:
            await session.refresh(p)

    return created_patents


@pytest.mark.asyncio
async def test_technology_intelligence_summary(client: AsyncClient, tech_patent_corpus):
    """
    Verifies /summary endpoint returns comprehensive aggregated technology intelligence.
    """
    response = await client.get("/api/v1/technology-intelligence/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    summary = data["data"]

    assert summary["total_patents"] >= 10
    assert summary["total_technology_areas"] >= 4
    assert summary["active_areas_count"] >= 2
    assert summary["potential_whitespaces_count"] >= 1
    assert len(summary["top_active_areas"]) > 0
    assert len(summary["top_growing_areas"]) > 0
    assert "methodology_disclaimer" in summary


@pytest.mark.asyncio
async def test_technology_activity_analytics(client: AsyncClient, tech_patent_corpus):
    """
    Verifies /activity calculates counts, recent filings, grant counts, assignees, and activity levels.
    """
    response = await client.get("/api/v1/technology-intelligence/activity")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    res_data = data["data"]

    assert res_data["total_patents"] >= 10
    items = res_data["items"]
    assert len(items) >= 4

    # Check Quantum Computing activity
    qc = next((i for i in items if i["technology_domain"] == "Quantum Computing"), None)
    assert qc is not None
    assert qc["patent_count"] == 3
    assert qc["recent_patent_count"] == 2
    assert qc["assignee_count"] == 2  # IBM, Google
    assert qc["activity_level"] == "MEDIUM_ACTIVITY"
    assert "US" in qc["jurisdictions"]

    # Check Synthetic Biology (Low activity)
    sb = next((i for i in items if i["technology_domain"] == "Synthetic Biology"), None)
    assert sb is not None
    assert sb["patent_count"] == 1
    assert sb["activity_level"] == "LOW_ACTIVITY"
    assert sb["assignee_count"] == 1


@pytest.mark.asyncio
async def test_technology_growth_trajectories(client: AsyncClient, tech_patent_corpus):
    """
    Verifies /growth deterministic velocity score and trajectory classification.
    """
    response = await client.get("/api/v1/technology-intelligence/growth")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    growth_data = data["data"]

    assert "summary_by_trajectory" in growth_data
    items = growth_data["items"]

    # Quantum Computing has 2 filings in recent window (2024), 1 in 2021
    qc = next((i for i in items if i["technology_domain"] == "Quantum Computing"), None)
    assert qc is not None
    assert qc["recent_period_filings"] == 2
    assert qc["historical_period_filings"] == 1
    assert qc["velocity_score"] > 50.0
    assert qc["growth_trajectory"] in ("RAPID_ACCELERATION", "STEADY_GROWTH")

    # Synthetic Biology has 0 recent filings
    sb = next((i for i in items if i["technology_domain"] == "Synthetic Biology"), None)
    assert sb is not None
    assert sb["recent_period_filings"] == 0
    assert sb["velocity_score"] == 0.0
    assert sb["growth_trajectory"] == "EMERGING_SPARSE"


@pytest.mark.asyncio
async def test_technology_coverage_density(client: AsyncClient, tech_patent_corpus):
    """
    Verifies /coverage calculates density score based on volume, assignees, jurisdictions, and classification.
    """
    response = await client.get("/api/v1/technology-intelligence/coverage")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    cov_data = data["data"]

    items = cov_data["items"]
    assert len(items) >= 4

    for item in items:
        assert 0.0 <= item["coverage_density_score"] <= 100.0
        assert item["coverage_level"] in ("HIGH_COVERAGE", "MODERATE_COVERAGE", "SPARSE_COVERAGE")


@pytest.mark.asyncio
async def test_whitespace_discovery_detection(client: AsyncClient, tech_patent_corpus):
    """
    Verifies /whitespace identifies activity gaps, generates evidence, confidence ratings, and adjacent areas.
    """
    response = await client.get("/api/v1/technology-intelligence/whitespace?whitespace_threshold=40.0")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    ws_data = data["data"]

    candidates = ws_data["candidates"]
    assert len(candidates) >= 1

    # Synthetic Biology or Clean Energy should be detected due to low activity and single assignee
    sb = next((c for c in candidates if c["technology_domain"] == "Synthetic Biology"), None)
    assert sb is not None
    assert sb["whitespace_score"] >= 60.0
    assert sb["activity_gap_score"] >= 50.0
    assert sb["assignee_gap_score"] >= 50.0
    assert len(sb["evidence"]) >= 2
    assert sb["confidence"] in ("HIGH", "MEDIUM", "LOW")
    assert "methodology_disclaimer" in sb
    assert isinstance(sb["adjacent_technology_areas"], list)


@pytest.mark.asyncio
async def test_whitespace_threshold_and_filters(client: AsyncClient, tech_patent_corpus):
    """
    Verifies filtering whitespace candidates by technology domain, start_year, and threshold.
    """
    # High threshold (e.g. 95)
    resp_high = await client.get("/api/v1/technology-intelligence/whitespace?whitespace_threshold=95.0")
    assert resp_high.status_code == 200
    data_high = resp_high.json()["data"]
    assert data_high["total_candidates"] <= 2

    # Domain filter
    resp_dom = await client.get("/api/v1/technology-intelligence/whitespace?domain=Synthetic Biology")
    assert resp_dom.status_code == 200
    data_dom = resp_dom.json()["data"]
    assert all(c["technology_domain"] == "Synthetic Biology" for c in data_dom["candidates"])


@pytest.mark.asyncio
async def test_empty_corpus_and_insufficient_data(client: AsyncClient):
    """
    Verifies graceful behavior when no patents match filters (empty dataset).
    """
    resp_act = await client.get("/api/v1/technology-intelligence/activity?domain=NonExistentDomain123")
    assert resp_act.status_code == 200
    data_act = resp_act.json()["data"]
    assert data_act["total_patents"] == 0
    assert len(data_act["items"]) == 0

    resp_growth = await client.get("/api/v1/technology-intelligence/growth?domain=NonExistentDomain123")
    assert resp_growth.status_code == 200
    data_growth = resp_growth.json()["data"]
    assert len(data_growth["items"]) == 0
    assert data_growth["total_growing_areas"] == 0

    resp_ws = await client.get("/api/v1/technology-intelligence/whitespace?domain=NonExistentDomain123")
    assert resp_ws.status_code == 200
    data_ws = resp_ws.json()["data"]
    assert data_ws["total_candidates"] == 0


@pytest.mark.asyncio
async def test_cross_user_profile_scoped_technology_intelligence(client: AsyncClient, tech_patent_corpus):
    """
    Verifies multi-tenant profile scoping isolates user portfolio from general corpus.
    """
    async with TestingSessionLocal() as session:
        # Create User A and Profile A
        user_a = User(
            email="tech_user_a@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Dr. Alice Tech",
            role=UserRole.RESEARCHER,
        )
        session.add(user_a)
        await session.commit()
        await session.refresh(user_a)

        profile_a = Profile(user_id=user_a.id, institution="MIT Technology Institute")
        session.add(profile_a)
        await session.commit()
        await session.refresh(profile_a)

        # Link only the Synthetic Biology patent to Profile A
        sb_patent = next(p for p in tech_patent_corpus if p.technology_domain == "Synthetic Biology")
        await session.execute(
            profile_patents.insert().values(profile_id=profile_a.id, patent_id=sb_patent.id)
        )
        await session.commit()

    # Login User A
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "tech_user_a@example.com", "password": "password123"}
    )
    assert login_res.status_code == 200
    token_a = login_res.json()["data"]["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Request profile-scoped activity
    resp = await client.get(
        "/api/v1/technology-intelligence/activity?my_profile_only=true",
        headers=headers_a
    )
    assert resp.status_code == 200
    act_data = resp.json()["data"]
    assert act_data["total_patents"] == 1
    assert len(act_data["items"]) == 1
    assert act_data["items"][0]["technology_domain"] == "Synthetic Biology"
