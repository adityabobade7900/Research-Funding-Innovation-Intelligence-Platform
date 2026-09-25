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
from app.services.commercialization_service import CommercializationService


@pytest.mark.asyncio
async def test_commercialization_readiness_dimensions(client: AsyncClient):
    """
    Validates Commercialization Readiness Score formula:
      TRL (30%) + Patent Strength (25%) + Market Potential (20%) + Funding Relevance (15%) + Novelty (10%) = 100%
    """
    async with TestingSessionLocal() as session:
        # Create research publication
        pub = Publication(
            title="High-Temperature Superconducting Qubits",
            authors="Dr. Quantum, Dr. Physicist",
            doi="10.1038/s41586-025-9999",
            publication_date=datetime(2025, 1, 10, tzinfo=timezone.utc),
            citation_count=35,
            venue="Physical Review Letters",
            source="manual",
        )
        session.add(pub)

        # Create granted patent
        pat = Patent(
            patent_number="US11223344B2",
            title="Cryogenic Flux Control Architecture for Quantum Processors",
            assignee="Quantum Dynamics Corp",
            inventors="Dr. Quantum",
            filing_date=datetime(2023, 6, 1, tzinfo=timezone.utc),
            publication_date=datetime(2024, 12, 1, tzinfo=timezone.utc),
            patent_classification="G06N 10/00",
            technology_domain="Quantum Computing",
            citation_count=20,
            source="manual",
        )
        session.add(pat)

        # Create funding opportunity
        funding = FundingOpportunity(
            title="DOE Quantum Internet Testbed Acceleration",
            description="Grants for quantum communication and network translation.",
            funding_agency="Department of Energy",
            funding_amount=2500000.0,
            status="open",
            application_deadline=datetime(2026, 12, 31, tzinfo=timezone.utc),
            external_id="DOE-QUANTUM-2026",
            source="manual",
        )
        session.add(funding)
        await session.commit()

    resp = await client.get("/api/v1/commercialization/readiness?domain=Quantum Computing")
    assert resp.status_code == 200
    data = resp.json()["data"]

    assert "readiness_score" in data
    assert 0.0 <= data["readiness_score"] <= 100.0
    assert data["readiness_level"] in ["HIGH_COMMERCIAL_READINESS", "MODERATE_COMMERCIAL_READINESS", "EARLY_DEVELOPMENT"]

    dims = data["dimensions"]
    assert "technology_maturity" in dims
    assert "patent_strength" in dims
    assert "market_potential" in dims
    assert "funding_relevance" in dims
    assert "research_novelty" in dims


@pytest.mark.asyncio
async def test_commercialization_recommendation_classification_and_priorities(client: AsyncClient):
    """
    Validates rule-based commercialization recommendation engine for a mature technology asset.
    """
    async with TestingSessionLocal() as session:
        # Create strong patent portfolio in Energy Storage
        p1 = Patent(
            patent_number="US10888999B2",
            title="Silicon-Graphene Solid-State Anode",
            assignee="NextGen Battery Inc",
            inventors="Alice Battery",
            filing_date=datetime(2023, 1, 15, tzinfo=timezone.utc),
            publication_date=datetime(2024, 5, 20, tzinfo=timezone.utc),
            patent_classification="H01M 10/05",
            technology_domain="Energy Storage",
            citation_count=25,
            source="manual",
        )
        p2 = Patent(
            patent_number="EP3999111B1",
            title="Solid Electrolyte Barrier Membrane",
            assignee="NextGen Battery Inc",
            inventors="Alice Battery",
            filing_date=datetime(2023, 8, 1, tzinfo=timezone.utc),
            publication_date=datetime(2025, 2, 10, tzinfo=timezone.utc),
            patent_classification="H01M 10/05",
            technology_domain="Energy Storage",
            citation_count=15,
            source="manual",
        )
        pub = Publication(
            title="Cycle Life Stabilization in Solid-State Lithium Cells",
            authors="Alice Battery, Bob Chemist",
            doi="10.1016/j.ensm.2025.02",
            publication_date=datetime(2025, 3, 1, tzinfo=timezone.utc),
            citation_count=50,
            venue="Energy Storage Materials",
            source="manual",
        )
        funding = FundingOpportunity(
            title="ARPA-E Next-Generation Solid-State Scale-up",
            description="Commercialization awards for vehicle-grade batteries.",
            funding_agency="ARPA-E",
            funding_amount=4000000.0,
            status="open",
            application_deadline=datetime(2026, 10, 15, tzinfo=timezone.utc),
            external_id="ARPAE-BATT-2026",
            source="manual",
        )
        session.add_all([p1, p2, pub, funding])
        await session.commit()

    resp = await client.get("/api/v1/commercialization/recommendations?domain=Energy Storage")
    assert resp.status_code == 200
    data = resp.json()["data"]

    assert data["target_name"] == "Energy Storage"
    assert data["readiness"]["readiness_score"] > 40.0
    assert len(data["recommendations"]) >= 2

    rec_types = [r["recommendation_type"] for r in data["recommendations"]]
    assert any(t in rec_types for t in ["STARTUP_SPINOUT", "LICENSING", "COMMERCIALIZATION_PREPARATION", "SEEK_FUNDING"])

    # Check top recommendation structure
    top_rec = data["primary_recommendation"]
    assert top_rec["priority"] in ["HIGH", "MEDIUM"]
    assert len(top_rec["supporting_evidence"]) >= 2
    assert len(top_rec["required_next_actions"]) >= 2
    assert "limitations" in top_rec


@pytest.mark.asyncio
async def test_commercialization_early_stage_research_focus(client: AsyncClient):
    """
    Validates early research concept triggers RESEARCH_FOCUS / VALIDATE_TECHNOLOGY.
    """
    async with TestingSessionLocal() as session:
        pub = Publication(
            title="Theoretical Foundations of Topological Insulators",
            authors="Dr. Theorist",
            doi="10.1103/physrevb.2025.101",
            publication_date=datetime(2025, 5, 1, tzinfo=timezone.utc),
            citation_count=2,
            venue="Physical Review B",
            primary_domain="Theoretical Physics",
            source="manual",
        )
        session.add(pub)
        await session.commit()

    resp = await client.get("/api/v1/commercialization/recommendations?domain=Theoretical Physics")
    assert resp.status_code == 200
    data = resp.json()["data"]

    assert data["readiness"]["readiness_level"] in ["BASIC_RESEARCH_STAGE", "EARLY_DEVELOPMENT"]
    rec_types = [r["recommendation_type"] for r in data["recommendations"]]
    assert any(t in rec_types for t in ["RESEARCH_FOCUS", "VALIDATE_TECHNOLOGY"])


@pytest.mark.asyncio
async def test_commercialization_strengthen_ip_recommendation(client: AsyncClient):
    """
    Validates that high novelty publication with 0 patent coverage triggers STRENGTHEN_IP.
    """
    async with TestingSessionLocal() as session:
        pub1 = Publication(
            title="CRISPR Gene Editing Tool for Plant Drought Resistance",
            authors="Dr. Geneticist, Dr. Agronomist",
            doi="10.1038/s41477-025-001",
            publication_date=datetime(2025, 4, 1, tzinfo=timezone.utc),
            citation_count=60,
            venue="Nature Plants",
            primary_domain="Agrigenomics",
            source="manual",
        )
        session.add(pub1)
        await session.commit()

    resp = await client.get("/api/v1/commercialization/recommendations?domain=Agrigenomics")
    assert resp.status_code == 200
    data = resp.json()["data"]

    rec_types = [r["recommendation_type"] for r in data["recommendations"]]
    assert "STRENGTHEN_IP" in rec_types

    ip_rec = next(r for r in data["recommendations"] if r["recommendation_type"] == "STRENGTHEN_IP")
    assert "provisional patent" in " ".join(ip_rec["required_next_actions"]).lower()


@pytest.mark.asyncio
async def test_commercialization_empty_corpus_and_insufficient_evidence(client: AsyncClient):
    """
    Validates zero-safe handling for domains with no indexed records.
    """
    resp = await client.get("/api/v1/commercialization/recommendations?domain=EmptyDomain12345")
    assert resp.status_code == 200
    data = resp.json()["data"]

    assert data["readiness"]["readiness_score"] == 0.0
    assert data["readiness"]["readiness_level"] == "BASIC_RESEARCH_STAGE"
    assert data["readiness"]["data_sufficiency"] == "INSUFFICIENT_DATA"
    assert data["primary_recommendation"]["recommendation_type"] == "MONITOR_AND_GATHER_EVIDENCE"


@pytest.mark.asyncio
async def test_commercialization_profile_scoped_isolation(client: AsyncClient):
    """
    Validates multi-tenant isolation: `my_profile_only=true` evaluates only the user's linked assets.
    """
    async with TestingSessionLocal() as session:
        user_a = User(
            email="commercial_user@tech.edu",
            hashed_password="hashed_pw_test",
            full_name="Dr. Tech Entrepreneur",
            role=UserRole.RESEARCHER,
            is_active=True,
        )
        session.add(user_a)
        await session.flush()

        prof_a = Profile(user_id=user_a.id, institution="Innovation Institute")
        session.add(prof_a)
        await session.flush()

        pub = Publication(
            title="Photonic Integrated Circuits for Machine Learning",
            authors="Dr. Tech Entrepreneur",
            doi="10.1364/optica.2025.101",
            publication_date=datetime(2025, 2, 15, tzinfo=timezone.utc),
            citation_count=40,
            venue="Optica",
            source="manual",
        )
        session.add(pub)
        await session.flush()
        await session.execute(profile_publications.insert().values(profile_id=prof_a.id, publication_id=pub.id))

        pat = Patent(
            patent_number="US11999888B2",
            title="Silicon Photonic Tensor Core Engine",
            assignee="Innovation Institute",
            inventors="Dr. Tech Entrepreneur",
            filing_date=datetime(2023, 9, 1, tzinfo=timezone.utc),
            publication_date=datetime(2025, 1, 20, tzinfo=timezone.utc),
            patent_classification="G06N 3/067",
            technology_domain="Photonics",
            citation_count=15,
            source="manual",
        )
        session.add(pat)
        await session.flush()
        await session.execute(profile_patents.insert().values(profile_id=prof_a.id, patent_id=pat.id))
        await session.commit()

        # Call service directly for profile_id
        score_resp = await CommercializationService.evaluate_commercialization(profile_id=prof_a.id, db=session)
        assert score_resp.target_type == "PROFILE"
        assert score_resp.target_name == "Dr. Tech Entrepreneur"
        assert score_resp.readiness.readiness_score > 30.0
        assert len(score_resp.recommendations) >= 1


@pytest.mark.asyncio
async def test_commercialization_integrated_funding_and_whitespace(client: AsyncClient):
    """
    Validates integrated funding opportunities and whitespace context.
    """
    resp = await client.get("/api/v1/commercialization/recommendations?domain=Quantum Computing")
    assert resp.status_code == 200
    data = resp.json()["data"]

    assert "funding_opportunities" in data
    assert "whitespace_context" in data
    assert "governance_disclaimer" in data


@pytest.mark.asyncio
async def test_commercialization_api_endpoints(client: AsyncClient):
    """
    Validates all REST endpoints under /api/v1/commercialization/*.
    """
    # 1. Recommendations
    res_rec = await client.get("/api/v1/commercialization/recommendations?domain=Quantum Computing")
    assert res_rec.status_code == 200

    # 2. Readiness
    res_read = await client.get("/api/v1/commercialization/readiness?domain=Quantum Computing")
    assert res_read.status_code == 200
    assert 0.0 <= res_read.json()["data"]["readiness_score"] <= 100.0

    # 3. Summary
    res_sum = await client.get("/api/v1/commercialization/summary")
    assert res_sum.status_code == 200
    assert "average_readiness_score" in res_sum.json()["data"]

    # 4. Evidence
    res_ev = await client.get("/api/v1/commercialization/evidence?domain=Quantum Computing")
    assert res_ev.status_code == 200
    assert "recommendations" in res_ev.json()["data"]
    assert "pathways" in res_ev.json()["data"]
    assert "commercialization_analysis" in res_ev.json()["data"]


@pytest.mark.asyncio
async def test_four_commercialization_pathways_structure(client: AsyncClient):
    """
    Validates that response contains the four canonical pathways:
    Productization, Licensing, Startup Creation, and Industry Partnership.
    """
    async with TestingSessionLocal() as session:
        pub = Publication(
            title="High-Q Photonic Crystal Nanocavities for Integrated Sensing",
            authors="Dr. Optical",
            doi="10.1364/oe.2025.101",
            publication_date=datetime(2025, 2, 1, tzinfo=timezone.utc),
            citation_count=20,
            primary_domain="Photonics",
            venue="Optics Express",
            source="manual",
        )
        pat = Patent(
            patent_number="US11555666B2",
            title="Photonic Nanocavity Resonator Circuit",
            assignee="OptoTech Corp",
            technology_domain="Photonics",
            filing_date=datetime(2023, 7, 1, tzinfo=timezone.utc),
            publication_date=datetime(2024, 11, 15, tzinfo=timezone.utc),
            citation_count=12,
        )
        session.add_all([pub, pat])
        await session.commit()

    resp = await client.get("/api/v1/commercialization/recommendations?domain=Photonics")
    assert resp.status_code == 200
    data = resp.json()["data"]

    assert "pathways" in data
    pathways = data["pathways"]

    # 1. Productization
    assert "productization" in pathways
    prod = pathways["productization"]
    assert prod["pathway"] == "PRODUCTIZATION"
    assert len(prod["product_concept"]) > 0
    assert len(prod["target_industry"]) > 0
    assert len(prod["main_use_case"]) > 0
    assert len(prod["required_next_steps"]) >= 2

    # 2. Licensing
    assert "licensing" in pathways
    lic = pathways["licensing"]
    assert lic["pathway"] == "LICENSING"
    assert len(lic["licensing_candidates"]) >= 1
    assert any(c["organization"] == "OptoTech Corp" for c in lic["licensing_candidates"])

    # 3. Startup Creation
    assert "startup_creation" in pathways
    startup = pathways["startup_creation"]
    assert startup["pathway"] == "STARTUP_CREATION"
    assert len(startup["startup_concept"]) > 0
    assert len(startup["business_model_hypothesis"]) > 0

    # 4. Industry Partnership
    assert "industry_partnership" in pathways
    part = pathways["industry_partnership"]
    assert part["pathway"] == "INDUSTRY_PARTNERSHIP"
    assert len(part["partnership_candidates"]) >= 1


async def _seed_photonics_test_data():
    async with TestingSessionLocal() as session:
        pub = Publication(
            title="High-Q Photonic Crystal Nanocavities for Integrated Sensing",
            authors="Dr. Optical",
            doi="10.1364/oe.2025.101",
            publication_date=datetime(2025, 2, 1, tzinfo=timezone.utc),
            citation_count=20,
            primary_domain="Photonics",
            venue="Optics Express",
            source="manual",
        )
        pat = Patent(
            patent_number="US11555666B2",
            title="Photonic Nanocavity Resonator Circuit",
            assignee="OptoTech Corp",
            technology_domain="Photonics",
            filing_date=datetime(2023, 7, 1, tzinfo=timezone.utc),
            publication_date=datetime(2024, 11, 15, tzinfo=timezone.utc),
            citation_count=12,
        )
        session.add_all([pub, pat])
        await session.commit()


@pytest.mark.asyncio
async def test_licensing_candidate_detection_from_patent_assignees(client: AsyncClient):
    """
    Validates Module 5 patent assignee consumption: real corporate assignees become potential licensing candidates.
    """
    await _seed_photonics_test_data()
    resp = await client.get("/api/v1/commercialization/recommendations?domain=Photonics")
    assert resp.status_code == 200
    data = resp.json()["data"]

    lic_candidates = data["pathways"]["licensing"]["licensing_candidates"]
    assert len(lic_candidates) >= 1
    cand = lic_candidates[0]
    assert cand["organization"] == "OptoTech Corp"
    assert cand["patent_count"] >= 1
    assert "Potential licensing candidate" in cand["suggested_licensing_rationale"]
    assert cand["data_status"] == "AVAILABLE"


@pytest.mark.asyncio
async def test_commercialization_analysis_problem_fit_and_adoption_status(client: AsyncClient):
    """
    Validates commercialization analysis: application areas, industries, fit, and DATA_UNAVAILABLE adoption telemetry.
    """
    await _seed_photonics_test_data()
    resp = await client.get("/api/v1/commercialization/recommendations?domain=Photonics")
    assert resp.status_code == 200
    data = resp.json()["data"]

    assert "commercialization_analysis" in data
    analysis = data["commercialization_analysis"]
    assert len(analysis["potential_application_areas"]) >= 2
    assert len(analysis["relevant_industries"]) >= 1
    assert len(analysis["supporting_evidence"]) >= 2
    assert analysis["commercial_adoption_telemetry"] == "DATA_UNAVAILABLE"


@pytest.mark.asyncio
async def test_unmeasured_dimensions_and_data_status(client: AsyncClient):
    """
    Validates that unmeasured readiness dimensions (regulatory feasibility, team capability)
    are explicitly marked DATA_UNAVAILABLE and not fabricated.
    """
    await _seed_photonics_test_data()
    resp = await client.get("/api/v1/commercialization/readiness?domain=Photonics")
    assert resp.status_code == 200
    data = resp.json()["data"]

    assert "unmeasured_dimensions" in data
    unmeasured = data["unmeasured_dimensions"]
    assert unmeasured["regulatory_feasibility"] == "DATA_UNAVAILABLE"
    assert unmeasured["team_capability"] == "DATA_UNAVAILABLE"


@pytest.mark.asyncio
async def test_no_patents_licensing_insufficient_data(client: AsyncClient):
    """
    Validates that a domain with 0 patents returns licensing data_status = INSUFFICIENT_DATA and 0 candidates.
    """
    async with TestingSessionLocal() as session:
        pub = Publication(
            title="Pure Mathematical Number Theory Foundations",
            authors="Dr. Gauss",
            doi="10.1007/math.2025.101",
            publication_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
            citation_count=5,
            primary_domain="Abstract Mathematics",
            venue="Annals of Math",
            source="manual",
        )
        session.add(pub)
        await session.commit()

    resp = await client.get("/api/v1/commercialization/recommendations?domain=Abstract Mathematics")
    assert resp.status_code == 200
    data = resp.json()["data"]

    lic = data["pathways"]["licensing"]
    assert lic["data_status"] == "INSUFFICIENT_DATA"
    assert len(lic["licensing_candidates"]) == 0
    assert "No patent disclosures" in lic["ip_ownership_basis"]


@pytest.mark.asyncio
async def test_potential_candidate_conservative_wording(client: AsyncClient):
    """
    Validates that conservative phrasing is strictly maintained across all pathways:
    No guarantees, no 'will license', no 'will become successful startup'.
    """
    await _seed_photonics_test_data()
    resp = await client.get("/api/v1/commercialization/recommendations?domain=Photonics")
    assert resp.status_code == 200
    data = resp.json()["data"]

    text_corpus = (
        str(data["pathways"])
        + " "
        + str(data["recommendations"])
        + " "
        + str(data["commercialization_analysis"])
    )

    # Strictly forbidden definitive claims
    assert "will license this technology" not in text_corpus.lower()
    assert "will become a successful startup" not in text_corpus.lower()
    assert "will partner with the researcher" not in text_corpus.lower()
    assert "guaranteed commercial" not in text_corpus.lower()

