import pytest
import pytest_asyncio
from datetime import datetime, timezone
from httpx import AsyncClient

from tests.conftest import TestingSessionLocal
from app.models.user import User, UserRole
from app.models.profile import Profile
from app.models.publication import Publication, profile_publications
from app.models.patent import Patent, profile_patents
from app.models.funding import FundingOpportunity
from app.services.trl_service import TRLService
from app.services.innovation_scoring_service import InnovationScoringService


@pytest.mark.asyncio
async def test_innovation_score_five_pillars_weights(client: AsyncClient):
    """
    Validates 5-pillar Innovation Score formula:
      Research Novelty (30%) + Patent Strength (20%) + Technology Maturity (15%) + Market Potential (20%) + Funding Relevance (15%) = 100%
    """
    async with TestingSessionLocal() as session:
        # Create test publication
        pub = Publication(
            title="Deep Learning for Quantum State Optimization",
            authors="Alice Scientist, Bob Researcher",
            abstract="Neural network optimization of multi-qubit systems with high novelty.",
            doi="10.1016/j.quantum.2025.01",
            publication_date=datetime(2025, 4, 15, tzinfo=timezone.utc),
            citation_count=24,
            venue="Nature Quantum Information",
            source="manual",
        )
        session.add(pub)

        # Create granted patent in Quantum Computing
        patent = Patent(
            patent_number="US11987654B2",
            title="Quantum Processor Architecture and Flux Control",
            abstract="Superconducting quantum circuits with low decoherence.",
            assignee="Quantum Technologies Inc",
            inventors="Alice Scientist",
            filing_date=datetime(2024, 1, 10, tzinfo=timezone.utc),
            publication_date=datetime(2025, 2, 20, tzinfo=timezone.utc),
            patent_classification="G06N 10/00",
            technology_domain="Quantum Computing",
            citation_count=18,
            source="manual",
        )
        session.add(patent)

        # Create matching funding opportunity
        funding = FundingOpportunity(
            title="NSF Quantum Computing Acceleration Program",
            description="Grants for quantum optimization and hardware architectures.",
            funding_agency="National Science Foundation",
            funding_amount=1500000.0,
            status="open",
            application_deadline=datetime(2026, 12, 31, tzinfo=timezone.utc),
            external_id="NSF-QUANTUM-2026",
            source="manual",
        )
        session.add(funding)
        await session.commit()

    resp = await client.get("/api/v1/innovation-scoring/score?domain=Quantum Computing")
    assert resp.status_code == 200
    data = resp.json()["data"]

    assert data["target_name"] == "Quantum Computing"
    assert "innovation_score" in data
    assert 0.0 <= data["innovation_score"] <= 100.0
    assert data["data_sufficiency"] in ["SUFFICIENT", "PARTIAL_EVIDENCE"]

    pillars = data["pillars"]
    assert "research_novelty" in pillars
    assert "patent_strength" in pillars
    assert "technology_maturity" in pillars
    assert "market_potential" in pillars
    assert "funding_relevance" in pillars

    # Validate exact specification weights
    assert pillars["research_novelty"]["weight"] == 0.30
    assert pillars["patent_strength"]["weight"] == 0.20
    assert pillars["technology_maturity"]["weight"] == 0.15
    assert pillars["market_potential"]["weight"] == 0.20
    assert pillars["funding_relevance"]["weight"] == 0.15

    # Check weighted sum equality
    weighted_sum = (
        pillars["research_novelty"]["weighted_score"]
        + pillars["patent_strength"]["weighted_score"]
        + pillars["technology_maturity"]["weighted_score"]
        + pillars["market_potential"]["weighted_score"]
        + pillars["funding_relevance"]["weighted_score"]
    )
    assert abs(data["innovation_score"] - round(weighted_sum, 2)) < 0.05


@pytest.mark.asyncio
async def test_trl_rule_estimation_engine_bounds():
    """
    Validates deterministic TRL 1-9 rule engine mapping across all lifecycle stages.
    """
    # 1. Early research: publications only, 0 patents
    trl_early = TRLService.estimate_trl(
        pub_count=2,
        recent_pub_count=1,
        avg_pub_citations=3.0,
        patent_count=0,
        granted_patent_count=0,
        jurisdiction_count=0,
        assignee_count=0,
    )
    assert trl_early.estimated_trl in [1, 2]
    assert trl_early.trl_stage == "Basic Research"
    assert trl_early.confidence in ["MEDIUM", "LOW"]

    # 2. Experimental proof of concept: multiple papers, high citations
    trl_poc = TRLService.estimate_trl(
        pub_count=6,
        recent_pub_count=4,
        avg_pub_citations=20.0,
        patent_count=0,
        granted_patent_count=0,
        jurisdiction_count=0,
        assignee_count=0,
    )
    assert trl_poc.estimated_trl == 3

    # 3. Lab validation: pending patent application
    trl_lab = TRLService.estimate_trl(
        pub_count=3,
        recent_pub_count=2,
        avg_pub_citations=10.0,
        patent_count=2,
        granted_patent_count=0,
        jurisdiction_count=1,
        assignee_count=1,
    )
    assert trl_lab.estimated_trl == 4
    assert trl_lab.trl_stage == "Laboratory Validation"

    # 4. Multi-jurisdiction granted patents with industrial partners
    trl_system = TRLService.estimate_trl(
        pub_count=8,
        recent_pub_count=5,
        avg_pub_citations=30.0,
        patent_count=10,
        granted_patent_count=8,
        jurisdiction_count=3,
        assignee_count=4,
        has_industrial_assignee=True,
    )
    assert trl_system.estimated_trl == 9
    assert trl_system.trl_stage == "Full Commercial / Operational Deployment"
    assert trl_system.score == 100.0
    assert trl_system.confidence == "HIGH"
    assert len(trl_system.evidence) >= 2


@pytest.mark.asyncio
async def test_research_novelty_pillar_calculation(client: AsyncClient):
    """
    Validates Research Novelty (30%) signal extraction: volume, recency ratio, citations, venue diversity.
    """
    async with TestingSessionLocal() as session:
        pub1 = Publication(
            title="Novel Generative Architectures for Protein Folding in Synthetic Biology",
            authors="Alice Scientist, Carol Bio",
            doi="10.1038/s41586-025-001",
            publication_date=datetime(2025, 6, 1, tzinfo=timezone.utc),
            citation_count=45,
            venue="Nature Biotechnology",
            source="manual",
        )
        pub2 = Publication(
            title="Cryo-EM Structural Discovery in Synthetic Biology",
            authors="David Structural, Eve Genomics",
            doi="10.1126/science.2024.002",
            publication_date=datetime(2024, 11, 15, tzinfo=timezone.utc),
            citation_count=30,
            venue="Science",
            source="manual",
        )
        session.add_all([pub1, pub2])
        await session.commit()

    resp = await client.get("/api/v1/innovation-scoring/score?domain=Synthetic Biology")
    assert resp.status_code == 200
    novelty = resp.json()["data"]["pillars"]["research_novelty"]

    assert novelty["score"] > 50.0
    assert novelty["contributing_signals"]["publication_count"] == 2
    assert novelty["contributing_signals"]["average_citations"] >= 30.0
    assert len(novelty["evidence"]) >= 2
    assert novelty["is_proxy"] is True


@pytest.mark.asyncio
async def test_patent_strength_pillar_calculation(client: AsyncClient):
    """
    Validates Patent Strength (20%) signal extraction: disclosures, grants, citations, jurisdictions.
    """
    async with TestingSessionLocal() as session:
        p1 = Patent(
            patent_number="US11223344B1",
            title="Solid-State Battery Electrolyte Matrix",
            assignee="CleanEnergy Labs",
            filing_date=datetime(2023, 5, 10, tzinfo=timezone.utc),
            publication_date=datetime(2024, 8, 12, tzinfo=timezone.utc),
            patent_classification="H01M 10/05",
            technology_domain="Energy Storage",
            citation_count=12,
            source="manual",
        )
        p2 = Patent(
            patent_number="EP3998877A1",
            title="Fast-Charging Solid-State Cathode",
            assignee="CleanEnergy Labs",
            filing_date=datetime(2024, 2, 1, tzinfo=timezone.utc),
            publication_date=datetime(2025, 3, 1, tzinfo=timezone.utc),
            patent_classification="H01M 10/05",
            technology_domain="Energy Storage",
            citation_count=8,
            source="manual",
        )
        session.add_all([p1, p2])
        await session.commit()

    resp = await client.get("/api/v1/innovation-scoring/score?domain=Energy Storage")
    assert resp.status_code == 200
    patent_pillar = resp.json()["data"]["pillars"]["patent_strength"]

    assert patent_pillar["score"] > 40.0
    assert patent_pillar["contributing_signals"]["patent_count"] == 2
    assert patent_pillar["contributing_signals"]["granted_patent_count"] >= 1
    assert patent_pillar["contributing_signals"]["jurisdiction_count"] >= 2
    assert len(patent_pillar["evidence"]) >= 2


@pytest.mark.asyncio
async def test_market_potential_and_funding_relevance_pillars(client: AsyncClient):
    """
    Validates Market Potential (20%) and Funding Relevance (15%) calculations.
    """
    async with TestingSessionLocal() as session:
        f1 = FundingOpportunity(
            title="DOE Clean Energy Advanced Battery Commercialization",
            description="Accelerating commercial adoption of solid-state storage.",
            funding_agency="Department of Energy",
            funding_amount=3000000.0,
            status="open",
            application_deadline=datetime(2026, 11, 30, tzinfo=timezone.utc),
            external_id="DOE-BATT-2026",
            source="manual",
        )
        session.add(f1)
        await session.commit()

    resp = await client.get("/api/v1/innovation-scoring/score?domain=Energy Storage")
    assert resp.status_code == 200
    data = resp.json()["data"]

    market_p = data["pillars"]["market_potential"]
    funding_p = data["pillars"]["funding_relevance"]

    assert 0.0 <= market_p["score"] <= 100.0
    assert 0.0 <= funding_p["score"] <= 100.0
    assert len(funding_p["evidence"]) >= 1


@pytest.mark.asyncio
async def test_empty_corpus_and_data_sufficiency_handling(client: AsyncClient):
    """
    Validates zero-safe handling for domains with no indexed publications or patents.
    """
    resp = await client.get("/api/v1/innovation-scoring/score?domain=NonExistentDomain12345")
    assert resp.status_code == 200
    data = resp.json()["data"]

    assert data["innovation_score"] == 0.0
    assert data["data_sufficiency"] == "INSUFFICIENT_DATA"
    assert data["overall_classification"] == "EARLY_STAGE_EXPLORATORY"
    assert data["trl"]["estimated_trl"] == 1
    assert data["trl"]["confidence"] == "LOW"


@pytest.mark.asyncio
async def test_cross_user_profile_scoped_innovation_scoring(client: AsyncClient):
    """
    Validates multi-tenant portfolio isolation: `my_profile_only=true` evaluates only the user's linked assets.
    """
    async with TestingSessionLocal() as session:
        user_a = User(
            email="innovator_a@univ.edu",
            hashed_password="hashed_pw_test",
            full_name="Dr. Innovator A",
            role=UserRole.RESEARCHER,
            is_active=True,
        )
        session.add(user_a)
        await session.flush()

        prof_a = Profile(user_id=user_a.id, institution="Tech Univ")
        session.add(prof_a)
        await session.flush()

        pub_a = Publication(
            title="Autonomous Drone Navigation Systems",
            authors="Dr. Innovator A",
            doi="10.1109/robotics.2025.101",
            publication_date=datetime(2025, 3, 1, tzinfo=timezone.utc),
            citation_count=15,
            venue="IEEE Robotics Transactions",
            source="manual",
        )
        session.add(pub_a)
        await session.flush()
        await session.execute(profile_publications.insert().values(profile_id=prof_a.id, publication_id=pub_a.id))

        pat_a = Patent(
            patent_number="US12345678B1",
            title="LiDAR Swarm Collision Avoidance",
            assignee="Tech Univ",
            inventors="Dr. Innovator A",
            filing_date=datetime(2024, 5, 1, tzinfo=timezone.utc),
            publication_date=datetime(2025, 1, 15, tzinfo=timezone.utc),
            patent_classification="B64C 39/02",
            technology_domain="Robotics",
            citation_count=5,
            source="manual",
        )
        session.add(pat_a)
        await session.flush()
        await session.execute(profile_patents.insert().values(profile_id=prof_a.id, patent_id=pat_a.id))
        await session.commit()

        # Direct service call scoping to User A's profile
        score_resp = await InnovationScoringService.calculate_innovation_score(profile_id=prof_a.id, db=session)
        assert score_resp.target_type == "PROFILE"
        assert score_resp.target_name == "Dr. Innovator A"
        assert score_resp.innovation_score > 20.0
        assert score_resp.pillars["research_novelty"].contributing_signals["publication_count"] == 1
        assert score_resp.pillars["patent_strength"].contributing_signals["patent_count"] == 1


@pytest.mark.asyncio
async def test_innovation_scoring_api_endpoints(client: AsyncClient):
    """
    Validates all REST endpoints under /api/v1/innovation-scoring/*.
    """
    async with TestingSessionLocal() as session:
        p = Patent(
            patent_number="US10999888B2",
            title="Quantum Flux Controller",
            assignee="Quantum Corp",
            technology_domain="Quantum Computing",
            patent_classification="G06N 10/00",
            citation_count=10,
            filing_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            publication_date=datetime(2024, 6, 1, tzinfo=timezone.utc),
        )
        session.add(p)
        await session.commit()

    # 1. Summary endpoint
    res_sum = await client.get("/api/v1/innovation-scoring/summary")
    assert res_sum.status_code == 200
    assert "average_innovation_score" in res_sum.json()["data"]

    # 2. TRL endpoint
    res_trl = await client.get("/api/v1/innovation-scoring/trl?domain=Quantum Computing")
    assert res_trl.status_code == 200
    assert 1 <= res_trl.json()["data"]["estimated_trl"] <= 9

    # 3. Evidence endpoint
    res_ev = await client.get("/api/v1/innovation-scoring/evidence?domain=Quantum Computing")
    assert res_ev.status_code == 200
    ev_data = res_ev.json()["data"]
    assert "trl_evidence" in ev_data
    assert "pillar_evidence" in ev_data
    assert "governance_disclaimer" in ev_data
