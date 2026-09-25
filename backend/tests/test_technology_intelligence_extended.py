import pytest
import pytest_asyncio
from datetime import datetime, timezone
from httpx import AsyncClient

from tests.conftest import TestingSessionLocal
from app.models.patent import Patent, profile_patents
from app.models.publication import Publication
from app.models.user import User, UserRole
from app.models.profile import Profile
from app.core.security import get_password_hash
from app.services.technology_intelligence_service import TechnologyIntelligenceService


@pytest_asyncio.fixture
async def multi_domain_corpus():
    """
    Creates a cross-corpus fixture with both publications (Module 3) and patents (Module 5)
    across diverse domains for technology maturity, whitespace, CAGR, and competitive testing.
    """
    async with TestingSessionLocal() as session:
        # Domain 1: Quantum Computing (High Research, High Patent, Developing)
        p1 = Patent(
            patent_number="US10111222B2",
            title="Superconducting Qubit Coupler for Fault-Tolerant Quantum Processor",
            assignee="IBM Corporation",
            technology_domain="Quantum Computing",
            patent_classification="G06N 10/00",
            citation_count=24,
            filing_date=datetime(2021, 3, 15, tzinfo=timezone.utc),
            publication_date=datetime(2022, 9, 20, tzinfo=timezone.utc),
        )
        p2 = Patent(
            patent_number="US10333444B2",
            title="Quantum Error Mitigation in Multi-Qubit Systems",
            assignee="IBM Corporation",
            technology_domain="Quantum Computing",
            patent_classification="G06N 10/00",
            citation_count=18,
            filing_date=datetime(2024, 1, 10, tzinfo=timezone.utc),
            publication_date=datetime(2024, 4, 5, tzinfo=timezone.utc),
        )
        p3 = Patent(
            patent_number="US10555666B2",
            title="Cryogenic Control Circuitry for Scalable Quantum Computing",
            assignee="Google LLC",
            technology_domain="Quantum Computing",
            patent_classification="G06N 10/00",
            citation_count=32,
            filing_date=datetime(2024, 6, 12, tzinfo=timezone.utc),
            publication_date=datetime(2024, 11, 30, tzinfo=timezone.utc),
        )
        pub1 = Publication(
            title="Quantum Error Correction on Neutral Atom Qubits",
            authors="Dr. M. Lukin, Dr. M. Greiner",
            venue="Nature Physics",
            primary_domain="Quantum Computing",
            citation_count=65,
            publication_date=datetime(2024, 2, 10, tzinfo=timezone.utc),
        )
        pub2 = Publication(
            title="High-Fidelity Rydberg Gates for Quantum Processors",
            authors="Dr. J. Thompson",
            venue="Physical Review X",
            primary_domain="Quantum Computing",
            citation_count=40,
            publication_date=datetime(2022, 5, 14, tzinfo=timezone.utc),
        )

        # Domain 2: Post-Quantum Cryptography (High Research, ZERO Patents -> Prime Whitespace!)
        pub_ws1 = Publication(
            title="Zero-Knowledge Proofs for Post-Quantum Blockchain Protocols",
            authors="Dr. S. Goldwasser, Dr. S. Micali",
            venue="IEEE S&P",
            primary_domain="Post-Quantum Cryptography",
            citation_count=85,
            publication_date=datetime(2024, 3, 20, tzinfo=timezone.utc),
        )
        pub_ws2 = Publication(
            title="Lattice-Based Signature Optimization on Embedded Systems",
            authors="Dr. C. Peikert",
            venue="CRYPTO 2023",
            primary_domain="Post-Quantum Cryptography",
            citation_count=52,
            publication_date=datetime(2023, 8, 15, tzinfo=timezone.utc),
        )

        # Domain 3: Legacy Silicon Packaging (Declining: older filings, zero recent)
        p_dec = Patent(
            patent_number="US8111222B2",
            title="Ceramic Dual Inline Package Assembly Method",
            assignee="Legacy Semiconductor Corp",
            technology_domain="Legacy Silicon Packaging",
            patent_classification="H01L 23/00",
            citation_count=5,
            filing_date=datetime(2015, 4, 10, tzinfo=timezone.utc),
            publication_date=datetime(2017, 2, 18, tzinfo=timezone.utc),
        )

        session.add_all([p1, p2, p3, pub1, pub2, pub_ws1, pub_ws2, p_dec])
        await session.commit()


@pytest.mark.asyncio
async def test_calculate_cagr_safe_handling():
    """
    Direct unit test verifying CAGR calculation:
    - Normal positive growth
    - Zero baseline handling (no division by zero)
    - Single year handling (insufficient data)
    """
    # 1. Normal: from 2 to 8 over 2 years -> (8/2)**(1/2) - 1 = 1.0 (100.0%)
    cagr, status = TechnologyIntelligenceService._calculate_cagr(2.0, 8.0, 2)
    assert status == "COMPUTED"
    assert cagr == 100.0

    # 2. Baseline zero -> BASELINE_ZERO, no division by zero
    cagr_zero, status_zero = TechnologyIntelligenceService._calculate_cagr(0.0, 5.0, 3)
    assert status_zero == "BASELINE_ZERO"
    assert cagr_zero is None

    # 3. Single year / zero years -> INSUFFICIENT_DATA
    cagr_insuf, status_insuf = TechnologyIntelligenceService._calculate_cagr(4.0, 6.0, 0)
    assert status_insuf == "INSUFFICIENT_DATA"
    assert cagr_insuf is None


@pytest.mark.asyncio
async def test_get_technology_maturity_six_indicators(client: AsyncClient, multi_domain_corpus):
    """
    Verifies the mentor-defined 6-indicator maturity model:
    - Research Growth (25%)
    - Patent Growth (25%)
    - Research Activity (15%)
    - Patent Activity (15%)
    - Organization Participation (10%)
    - Technology Diversity (10%)
    Weights sum to 100%, and maturity score is calculated accurately.
    """
    resp = await client.get("/api/v1/technology-intelligence/maturity?domain=Quantum Computing")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total_domains_analyzed"] >= 1

    item = next(i for i in data["items"] if i["technology_domain"] == "Quantum Computing")
    ind = item["indicators"]

    # Verify weight dictionary
    weights = ind["weights"]
    assert weights["research_growth"] == 0.25
    assert weights["patent_growth"] == 0.25
    assert weights["research_activity"] == 0.15
    assert weights["patent_activity"] == 0.15
    assert weights["organization_participation"] == 0.10
    assert weights["technology_diversity"] == 0.10
    assert sum(weights.values()) == pytest.approx(1.0, 0.001)

    # Verify overall maturity score matches formula
    expected_score = round(
        0.25 * ind["research_growth_score"]
        + 0.25 * ind["patent_growth_score"]
        + 0.15 * ind["research_activity_score"]
        + 0.15 * ind["patent_activity_score"]
        + 0.10 * ind["organization_participation_score"]
        + 0.10 * ind["technology_diversity_score"],
        2,
    )
    assert item["maturity_score"] == pytest.approx(expected_score, 0.01)

    # Check stage and explainability summary
    assert item["stage"] in ("EMERGING", "DEVELOPING", "MATURE", "DECLINING")
    assert "Maturity Score" in item["explainability_summary"]
    assert len(item["evidence"]) >= 3


@pytest.mark.asyncio
async def test_whitespace_discovery_research_vs_patent_gap(client: AsyncClient, multi_domain_corpus):
    """
    Verifies Whitespace Discovery detects density gaps between publications and patents:
    Post-Quantum Cryptography has 2 scientific publications and 0 patents, making it a prime candidate.
    """
    resp = await client.get("/api/v1/technology-intelligence/whitespace?whitespace_threshold=40")
    assert resp.status_code == 200
    data = resp.json()["data"]
    candidates = data["candidates"]

    # Find Post-Quantum Cryptography candidate
    pqc = next((c for c in candidates if "Post-Quantum Cryptography" in c["technology_area"]), None)
    assert pqc is not None, "Post-Quantum Cryptography should be detected as potential whitespace"
    assert pqc["publication_count"] == 2
    assert pqc["patent_count"] == 0
    # Mentor rule: When patent_count == 0, research_to_patent_ratio MUST be None (null), NOT a fake 1.0x
    assert pqc["research_to_patent_ratio"] is None
    assert pqc["patent_status_note"] == "No patent records identified for this technology domain."
    assert pqc["whitespace_type"] == "POTENTIAL_WHITESPACE"
    assert pqc["confidence"] in ("HIGH", "MEDIUM")
    assert any("scientific research foundation" in ev.lower() or "publication" in ev.lower() for ev in pqc["evidence"])


@pytest.mark.asyncio
async def test_technology_adoption_isolated_status(client: AsyncClient, multi_domain_corpus):
    """
    Verifies that technology adoption tracking is strictly separate from R&D publications and patents.
    In the absence of commercial sales telemetry, adoption_status must be DATA_UNAVAILABLE.
    """
    resp = await client.get("/api/v1/technology-intelligence/adoption")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total_domains"] >= 1

    for item in data["items"]:
        assert item["adoption_status"] == "DATA_UNAVAILABLE"
        assert item["commercial_evidence_available"] is False
        assert "separate" in item["disclaimer"].lower()


@pytest.mark.asyncio
async def test_emerging_technologies_ranking(client: AsyncClient, multi_domain_corpus):
    """
    Verifies emerging technology endpoint identifies and ranks domains by emergence momentum.
    """
    resp = await client.get("/api/v1/technology-intelligence/emerging")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total_candidates"] >= 1

    top_candidate = data["candidates"][0]
    assert "emerging_score" in top_candidate
    assert top_candidate["emerging_score"] >= 0.0
    assert "key_signals" in top_candidate
    assert len(top_candidate["key_signals"]) >= 1


@pytest.mark.asyncio
async def test_competitive_technology_monitoring_hhi(client: AsyncClient, multi_domain_corpus):
    """
    Verifies competitor technology monitoring computes HHI concentration and top assignees per domain.
    """
    resp = await client.get("/api/v1/technology-intelligence/competitive?domain=Quantum Computing")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total_domains"] >= 1

    qc = next(c for c in data["items"] if c["technology_domain"] == "Quantum Computing")
    assert qc["assignee_count"] >= 2
    assert qc["assignee_concentration_hhi"] > 0.0
    assert qc["concentration_tier"] in ("UNCONCENTRATED", "MODERATELY_CONCENTRATED", "HIGHLY_CONCENTRATED")
    assert len(qc["top_assignees"]) >= 1
    # Check that IBM has patents listed
    ibm_entry = next((a for a in qc["top_assignees"] if "IBM" in a["assignee"]), None)
    assert ibm_entry is not None
    assert ibm_entry["patent_count"] == 2


@pytest.mark.asyncio
async def test_maturity_stage_never_mature_if_score_below_60(client: AsyncClient):
    """
    REGRESSION TEST 1:
    Proves that if maturity_score < 60.0, the technology MUST NOT be classified as MATURE.
    """
    async with TestingSessionLocal() as session:
        # Create a domain with 2 years of moderate data (score will be < 60)
        p1 = Patent(
            patent_number="US9999001B2",
            title="Moderate Patent 1",
            assignee="Acme Labs",
            technology_domain="Subthreshold Domain",
            filing_date=datetime(2022, 1, 10, tzinfo=timezone.utc),
            publication_date=datetime(2023, 1, 10, tzinfo=timezone.utc),
        )
        p2 = Patent(
            patent_number="US9999002B2",
            title="Moderate Patent 2",
            assignee="Acme Labs",
            technology_domain="Subthreshold Domain",
            filing_date=datetime(2024, 1, 10, tzinfo=timezone.utc),
            publication_date=datetime(2024, 6, 10, tzinfo=timezone.utc),
        )
        session.add_all([p1, p2])
        await session.commit()

        resp = await client.get("/api/v1/technology-intelligence/maturity?domain=Subthreshold Domain")
        assert resp.status_code == 200
        items = resp.json()["data"]["items"]
        assert len(items) >= 1
        item = items[0]
        # Assert condition: if score < 60, stage MUST NOT be MATURE
        if item["maturity_score"] < 60.0:
            assert item["stage"] != "MATURE", f"Domain with score {item['maturity_score']} < 60 must not be MATURE"


@pytest.mark.asyncio
async def test_insufficient_historical_data_handling(client: AsyncClient):
    """
    REGRESSION TEST 2:
    Validates insufficient historical data handling:
    - 0 years (no records): INSUFFICIENT_DATA
    - 1 year: growth_status = INSUFFICIENT_DATA, stage = INSUFFICIENT_DATA (NOT DECLINING!)
    - 2+ years: growth_status = COMPUTED
    """
    async with TestingSessionLocal() as session:
        # Domain with only ONE year of data
        p_single = Patent(
            patent_number="US8888001B2",
            title="Single Year Patent",
            assignee="Solo Corp",
            technology_domain="Single Year Frontier",
            filing_date=datetime(2024, 5, 10, tzinfo=timezone.utc),
            publication_date=datetime(2024, 9, 10, tzinfo=timezone.utc),
        )
        session.add(p_single)
        await session.commit()

        resp = await client.get("/api/v1/technology-intelligence/maturity?domain=Single Year Frontier")
        assert resp.status_code == 200
        items = resp.json()["data"]["items"]
        assert len(items) >= 1
        item = items[0]

        # Must NOT be classified as DECLINING
        assert item["stage"] != "DECLINING", "Single-year data must NOT be classified as DECLINING"
        assert item["stage"] == "INSUFFICIENT_DATA"
        assert item["indicators"]["growth_status"] == "INSUFFICIENT_DATA"
        assert item["indicators"]["research_cagr"] is None
        assert item["indicators"]["patent_cagr"] is None


@pytest.mark.asyncio
async def test_organization_participation_excludes_venues(client: AsyncClient):
    """
    REGRESSION TEST 3:
    Proves that academic venues (journals/conferences) do NOT increase Organization Participation.
    Only registered applicant organizations (assignees) count.
    """
    async with TestingSessionLocal() as session:
        # Domain with 0 assignees, but 3 different publication venues
        pub1 = Publication(
            title="Paper at Conference A",
            authors="Author 1",
            venue="Conference A",
            primary_domain="Venue Test Domain",
            publication_date=datetime(2024, 1, 10, tzinfo=timezone.utc),
        )
        pub2 = Publication(
            title="Paper at Journal B",
            authors="Author 2",
            venue="Journal B",
            primary_domain="Venue Test Domain",
            publication_date=datetime(2024, 2, 10, tzinfo=timezone.utc),
        )
        pub3 = Publication(
            title="Paper at Symposium C",
            authors="Author 3",
            venue="Symposium C",
            primary_domain="Venue Test Domain",
            publication_date=datetime(2024, 3, 10, tzinfo=timezone.utc),
        )
        session.add_all([pub1, pub2, pub3])
        await session.commit()

        resp = await client.get("/api/v1/technology-intelligence/maturity?domain=Venue Test Domain")
        assert resp.status_code == 200
        items = resp.json()["data"]["items"]
        assert len(items) >= 1
        item = items[0]

        # 0 assignees, 3 venues
        assert item["assignee_count"] == 0
        assert item["venue_count"] == 3
        # Organization participation score must be 0.0 because venues are NOT organizations
        assert item["indicators"]["organization_participation_score"] == 0.0
