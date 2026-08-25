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
async def sample_patent_corpus():
    """
    Creates a rich deterministic patent corpus across multiple years, domains, assignees, and jurisdictions.
    """
    patents_data = [
        # Quantum Computing - IBM (US)
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
            "filing_date": datetime(2023, 1, 10, tzinfo=timezone.utc),
            "publication_date": datetime(2024, 4, 5, tzinfo=timezone.utc),
        },
        # Quantum Computing - Google (US)
        {
            "patent_number": "US10555666B2",
            "title": "Cryogenic Control Circuitry for Scalable Quantum Computing",
            "assignee": "Google LLC",
            "technology_domain": "Quantum Computing",
            "patent_classification": "G06N 10/00",
            "citation_count": 32,
            "filing_date": datetime(2022, 6, 12, tzinfo=timezone.utc),
            "publication_date": datetime(2023, 11, 30, tzinfo=timezone.utc),
        },
        # Artificial Intelligence - Google (US)
        {
            "patent_number": "US11223344A1",
            "title": "Sparse Mixture-of-Experts Neural Network Transformer Architecture",
            "assignee": "Google LLC",
            "technology_domain": "Artificial Intelligence",
            "patent_classification": "G06N 3/08",
            "citation_count": 45,
            "filing_date": datetime(2023, 8, 20, tzinfo=timezone.utc),
            "publication_date": datetime(2024, 2, 15, tzinfo=timezone.utc),
        },
        # Biotechnology - MIT (EP)
        {
            "patent_number": "EP3888999B1",
            "title": "Engineered Cas12 Nucleases for High-Fidelity Gene Editing",
            "assignee": "Massachusetts Institute of Technology",
            "technology_domain": "Biotechnology",
            "patent_classification": "C12N 15/113",
            "citation_count": 50,
            "filing_date": datetime(2020, 5, 10, tzinfo=timezone.utc),
            "publication_date": datetime(2021, 8, 14, tzinfo=timezone.utc),
        },
        # Biotechnology - Stanford (WO)
        {
            "patent_number": "WO2023055667A1",
            "title": "Targeted Lipid Nanoparticle Delivery for Therapeutic mRNA",
            "assignee": "Stanford University",
            "technology_domain": "Biotechnology",
            "patent_classification": "A61K 9/51",
            "citation_count": 18,
            "filing_date": datetime(2023, 2, 18, tzinfo=timezone.utc),
            "publication_date": datetime(2023, 9, 25, tzinfo=timezone.utc),
        },
        # Clean Energy - Siemens (EP)
        {
            "patent_number": "EP3999111A1",
            "title": "Direct Air Capture Contactor with Optimized Sorbent Regeneration",
            "assignee": "Siemens Energy",
            "technology_domain": "Clean Energy",
            "patent_classification": "B01D 53/04",
            "citation_count": 8,
            "filing_date": datetime(2022, 11, 5, tzinfo=timezone.utc),
            "publication_date": datetime(2023, 6, 18, tzinfo=timezone.utc),
        },
    ]

    async with TestingSessionLocal() as session:
        created_patents = []
        for p_dict in patents_data:
            p = Patent(
                patent_number=p_dict["patent_number"],
                title=p_dict["title"],
                assignee=p_dict["assignee"],
                technology_domain=p_dict["technology_domain"],
                patent_classification=p_dict["patent_classification"],
                citation_count=p_dict["citation_count"],
                filing_date=p_dict["filing_date"],
                publication_date=p_dict["publication_date"],
                source="manual",
            )
            session.add(p)
            created_patents.append(p)

        await session.commit()
        for p in created_patents:
            await session.refresh(p)
        return created_patents


@pytest.mark.asyncio
async def test_patent_landscape_summary(client: AsyncClient, sample_patent_corpus):
    """
    Validates top-level summary analytics across the entire patent landscape.
    """
    response = await client.get("/api/v1/patent-intelligence/landscape")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True

    summary = res_data["data"]
    assert summary["total_patents"] == 7
    assert summary["total_assignees"] >= 4
    assert summary["total_domains"] == 4
    assert summary["total_citations"] == (28 + 14 + 32 + 45 + 50 + 18 + 8)
    assert summary["average_citations"] > 0
    assert summary["filing_year_range"]["min_year"] == 2020
    assert summary["filing_year_range"]["max_year"] == 2023
    assert len(summary["top_domains"]) > 0
    assert len(summary["top_assignees"]) > 0
    assert len(summary["jurisdiction_distribution"]) > 0


@pytest.mark.asyncio
async def test_patent_trends_and_growth_rate(client: AsyncClient, sample_patent_corpus):
    """
    Validates filing and grant yearly trajectories and YoY growth calculations.
    """
    response = await client.get("/api/v1/patent-intelligence/trends")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True

    data = res_data["data"]
    assert data["total_patents"] == 7
    points = {p["year"]: p for p in data["points"]}

    # 2020: 1 filing (MIT)
    assert points[2020]["filings_count"] == 1
    assert points[2020]["filing_growth_rate"] is None

    # 2021: 1 filing (IBM)
    assert points[2021]["filings_count"] == 1
    assert points[2021]["filing_growth_rate"] == 0.0

    # 2022: 2 filings (Google, Siemens)
    assert points[2022]["filings_count"] == 2
    assert points[2022]["filing_growth_rate"] == 100.0

    # 2023: 3 filings (IBM, Google, Stanford)
    assert points[2023]["filings_count"] == 3
    assert points[2023]["filing_growth_rate"] == 50.0


@pytest.mark.asyncio
async def test_technology_domains_and_concentration_hhi(client: AsyncClient, sample_patent_corpus):
    """
    Validates domain breakdown, share percentages, and Herfindahl-Hirschman Index (HHI).
    """
    response = await client.get("/api/v1/patent-intelligence/technology-domains")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True

    data = res_data["data"]
    assert data["total_domains"] == 4
    assert data["concentration_level"] in ["DIVERSIFIED", "MODERATELY_CONCENTRATED", "HIGHLY_CONCENTRATED"]
    assert data["concentration_index_hhi"] > 0

    domains_map = {d["domain"]: d for d in data["domains"]}
    # Quantum Computing: 3 / 7 = ~42.86%
    assert domains_map["Quantum Computing"]["patent_count"] == 3
    assert domains_map["Quantum Computing"]["share_percentage"] == round(3 / 7 * 100.0, 2)
    assert "IBM Corporation" in domains_map["Quantum Computing"]["top_assignees"]
    assert "Google LLC" in domains_map["Quantum Computing"]["top_assignees"]

    # Biotechnology: 2 / 7 = ~28.57%
    assert domains_map["Biotechnology"]["patent_count"] == 2


@pytest.mark.asyncio
async def test_assignees_landscape_ranking(client: AsyncClient, sample_patent_corpus):
    """
    Validates assignee ranking, primary domains, and jurisdiction coverage.
    """
    response = await client.get("/api/v1/patent-intelligence/assignees")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True

    data = res_data["data"]
    assignees_map = {a["assignee"]: a for a in data["assignees"]}

    # Google: 2 patents (1 AI, 1 Quantum), US jurisdiction
    assert "Google LLC" in assignees_map
    google = assignees_map["Google LLC"]
    assert google["patent_count"] == 2
    assert "US" in google["jurisdictions"]
    assert len(google["primary_domains"]) >= 1

    # IBM: 2 patents (Quantum), US jurisdiction
    assert "IBM Corporation" in assignees_map
    ibm = assignees_map["IBM Corporation"]
    assert ibm["patent_count"] == 2
    assert "US" in ibm["jurisdictions"]

    # MIT: 1 patent, EP jurisdiction
    assert "Massachusetts Institute of Technology" in assignees_map
    mit = assignees_map["Massachusetts Institute of Technology"]
    assert "EP" in mit["jurisdictions"]


@pytest.mark.asyncio
async def test_jurisdiction_and_status_distribution(client: AsyncClient, sample_patent_corpus):
    """
    Validates authority code extraction (US, EP, WO) and status categorization.
    """
    # 1. Jurisdictions
    jur_resp = await client.get("/api/v1/patent-intelligence/jurisdictions")
    assert jur_resp.status_code == 200
    jur_data = jur_resp.json()["data"]
    jur_map = {j["jurisdiction_code"]: j for j in jur_data["jurisdictions"]}

    assert "US" in jur_map
    assert jur_map["US"]["patent_count"] == 4  # 2 IBM + 2 Google
    assert "EP" in jur_map
    assert jur_map["EP"]["patent_count"] == 2  # MIT + Siemens
    assert "WO" in jur_map
    assert jur_map["WO"]["patent_count"] == 1  # Stanford

    # 2. Status distribution
    status_resp = await client.get("/api/v1/patent-intelligence/status")
    assert status_resp.status_code == 200
    status_data = status_resp.json()["data"]
    status_map = {s["status"]: s for s in status_data["statuses"]}

    assert status_map["GRANTED"]["count"] > 0
    assert status_map["PENDING_APPLICATION"]["count"] > 0


@pytest.mark.asyncio
async def test_competitive_landscape_indicators(client: AsyncClient, sample_patent_corpus):
    """
    Validates competitive indicator calculations, composite scoring, and classifications.
    """
    response = await client.get("/api/v1/patent-intelligence/competitive-landscape")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True

    data = res_data["data"]
    assert "methodology_disclaimer" in data
    assert len(data["competitors"]) >= 4

    comp_map = {c["assignee"]: c for c in data["competitors"]}
    google = comp_map["Google LLC"]
    assert google["competitive_index"] > 0.0
    assert google["competitive_index"] <= 100.0
    assert google["domain_breadth_count"] >= 2
    assert len(google["key_drivers"]) > 0


@pytest.mark.asyncio
async def test_filtering_and_empty_dataset_handling(client: AsyncClient, sample_patent_corpus):
    """
    Validates domain filtering, date range filtering, and empty dataset graceful handling.
    """
    # 1. Filter by domain = 'Quantum Computing'
    q_resp = await client.get("/api/v1/patent-intelligence/trends?domain=Quantum")
    assert q_resp.status_code == 200
    assert q_resp.json()["data"]["total_patents"] == 3

    # 2. Filter by date range = 2023 to 2024
    d_resp = await client.get("/api/v1/patent-intelligence/trends?start_year=2023&end_year=2024")
    assert d_resp.status_code == 200
    assert d_resp.json()["data"]["total_patents"] >= 3

    # 3. Empty filter matching nothing
    empty_resp = await client.get("/api/v1/patent-intelligence/landscape?domain=NonExistentDomainXYZ")
    assert empty_resp.status_code == 200
    empty_data = empty_resp.json()["data"]
    assert empty_data["total_patents"] == 0
    assert empty_data["total_assignees"] == 0
    assert empty_data["top_domains"] == []


@pytest.mark.asyncio
async def test_cross_user_profile_scoped_landscape(client: AsyncClient, sample_patent_corpus):
    """
    Validates that `my_profile_only=True` strictly scopes intelligence to the authenticated researcher's linked patents.
    """
    async with TestingSessionLocal() as session:
        # Create Researcher User A
        user_a = User(
            email="patent_researcher_a@test.com",
            hashed_password=get_password_hash("password123"),
            full_name="Dr. Alice Patent",
            role=UserRole.RESEARCHER,
            is_active=True,
        )
        session.add(user_a)
        await session.commit()
        await session.refresh(user_a)

        profile_a = Profile(user_id=user_a.id, institution="MIT Labs")
        session.add(profile_a)
        await session.commit()
        await session.refresh(profile_a)

        # Link ONLY the MIT patent (EP3888999B1) to Profile A
        mit_patent = next(p for p in sample_patent_corpus if p.patent_number == "EP3888999B1")
        await session.execute(
            profile_patents.insert().values(
                profile_id=profile_a.id,
                patent_id=mit_patent.id
            )
        )
        await session.commit()

    # Login as User A
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "patent_researcher_a@test.com", "password": "password123"}
    )
    assert login_res.status_code == 200
    token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Global landscape request -> returns all 7 patents
    global_res = await client.get("/api/v1/patent-intelligence/landscape", headers=headers)
    assert global_res.status_code == 200
    assert global_res.json()["data"]["total_patents"] == 7

    # 2. Scoped landscape request -> returns ONLY 1 patent (Biotechnology, MIT)
    scoped_res = await client.get("/api/v1/patent-intelligence/landscape?my_profile_only=true", headers=headers)
    assert scoped_res.status_code == 200
    scoped_data = scoped_res.json()["data"]
    assert scoped_data["total_patents"] == 1
    assert scoped_data["total_assignees"] == 1
    assert scoped_data["top_domains"][0]["domain"] == "Biotechnology"
    assert scoped_data["top_assignees"][0]["assignee"] == "Massachusetts Institute of Technology"
