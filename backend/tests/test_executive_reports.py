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
from app.services.executive_report_service import ExecutiveReportService


@pytest.mark.asyncio
async def test_executive_dossier_synthesis_structure(client: AsyncClient):
    """
    Validates complete multi-stream dossier synthesis (Innovation, TRL, Commercialization, Grants, Patents).
    """
    async with TestingSessionLocal() as session:
        pub = Publication(
            title="Fault-Tolerant Quantum Error Correction Codes",
            authors="Dr. Qubit, Dr. Algorithm",
            doi="10.1103/prxquantum.2025.101",
            publication_date=datetime(2025, 3, 1, tzinfo=timezone.utc),
            citation_count=45,
            venue="PRX Quantum",
            primary_domain="Quantum Computing",
            source="manual",
        )
        session.add(pub)

        pat = Patent(
            patent_number="US11555666B2",
            title="Surface Code Decoder for Superconducting Quantum Processor",
            assignee="Quantum Scaling Labs",
            inventors="Dr. Qubit",
            filing_date=datetime(2023, 5, 1, tzinfo=timezone.utc),
            publication_date=datetime(2024, 11, 15, tzinfo=timezone.utc),
            patent_classification="G06N 10/70",
            technology_domain="Quantum Computing",
            citation_count=18,
            source="manual",
        )
        session.add(pat)

        funding = FundingOpportunity(
            title="NSF Quantum Leap Challenge Institutes",
            description="Multi-institutional awards for quantum computing scale-up and commercial translation.",
            funding_agency="National Science Foundation",
            funding_amount=5000000.0,
            status="open",
            application_deadline=datetime(2026, 11, 30, tzinfo=timezone.utc),
            external_id="NSF-QLCI-2026",
            source="manual",
        )
        session.add(funding)
        await session.commit()

    resp = await client.get("/api/v1/reports/dossier?domain=Quantum Computing")
    assert resp.status_code == 200
    data = resp.json()["data"]

    assert data["target_name"] == "Quantum Computing"
    assert "report_id" in data
    assert data["report_id"].startswith("DOSSIER-")
    assert "executive_summary" in data
    assert len(data["key_findings"]) >= 3

    # Check synthesis of metrics
    assert data["innovation_score"] > 30.0
    assert data["estimated_trl"] >= 4
    assert data["commercialization_readiness"] > 30.0
    assert "primary_commercial_pathway" in data

    # Check sub-signal metrics
    assert data["publication_metrics"]["total_publications"] >= 1
    assert data["patent_metrics"]["total_patents"] >= 1
    assert data["funding_metrics"]["matching_opportunities_count"] >= 1


@pytest.mark.asyncio
async def test_executive_dossier_strategic_assessment_and_roadmap(client: AsyncClient):
    """
    Validates SWOT strategic assessment quadrants and 3-phase execution roadmap.
    """
    resp = await client.get("/api/v1/reports/dossier?domain=Quantum Computing")
    assert resp.status_code == 200
    data = resp.json()["data"]

    swot = data["strategic_assessment"]
    assert len(swot["strengths"]) >= 1
    assert len(swot["risks_and_bottlenecks"]) >= 1
    assert len(swot["market_opportunities"]) >= 1
    assert len(swot["barriers_to_entry"]) >= 1

    roadmap = data["roadmap"]
    assert len(roadmap) == 3
    phase_names = [p["phase_name"] for p in roadmap]
    assert any("Foundation" in name for name in phase_names)
    assert any("Validation" in name for name in phase_names)
    assert any("Scale" in name for name in phase_names)

    # Validate action item schema in Phase 1
    p1 = roadmap[0]
    assert len(p1["actions"]) >= 1
    assert "owner_role" in p1["actions"][0]
    assert "target_timeline" in p1["actions"][0]
    assert "expected_outcome" in p1["actions"][0]


@pytest.mark.asyncio
async def test_executive_dossier_profile_scoped_isolation(client: AsyncClient):
    """
    Validates that my_profile_only scopes executive dossier strictly to the user's linked assets.
    """
    async with TestingSessionLocal() as session:
        user_exec = User(
            email="exec_researcher@mit.edu",
            hashed_password="hashed_pw_exec",
            full_name="Prof. Sarah Executive",
            role=UserRole.RESEARCHER,
            is_active=True,
        )
        session.add(user_exec)
        await session.flush()

        prof_exec = Profile(user_id=user_exec.id, institution="MIT Media Lab")
        session.add(prof_exec)
        await session.flush()

        pub = Publication(
            title="Neuromorphic Optical Synapses for Edge Computing",
            authors="Prof. Sarah Executive",
            doi="10.1038/s41565-025-001",
            publication_date=datetime(2025, 1, 15, tzinfo=timezone.utc),
            citation_count=80,
            venue="Nature Nanotechnology",
            primary_domain="Neuromorphic Engineering",
            source="manual",
        )
        session.add(pub)
        await session.flush()
        await session.execute(profile_publications.insert().values(profile_id=prof_exec.id, publication_id=pub.id))

        pat = Patent(
            patent_number="US11777888B2",
            title="Phase-Change Optical Memristor Array",
            assignee="MIT",
            inventors="Prof. Sarah Executive",
            filing_date=datetime(2023, 7, 1, tzinfo=timezone.utc),
            publication_date=datetime(2024, 10, 1, tzinfo=timezone.utc),
            patent_classification="G11C 13/00",
            technology_domain="Neuromorphic Engineering",
            citation_count=30,
            source="manual",
        )
        session.add(pat)
        await session.flush()
        await session.execute(profile_patents.insert().values(profile_id=prof_exec.id, patent_id=pat.id))
        await session.commit()

        dossier = await ExecutiveReportService.generate_dossier(profile_id=prof_exec.id, db=session)
        assert dossier.target_type == "PROFILE"
        assert dossier.target_name == "Prof. Sarah Executive"
        assert dossier.innovation_score > 40.0
        assert dossier.publication_metrics["total_publications"] == 1
        assert dossier.patent_metrics["total_patents"] == 1


@pytest.mark.asyncio
async def test_executive_dossier_empty_corpus_and_insufficient_evidence(client: AsyncClient):
    """
    Validates zero-safe handling for domains with no indexed records.
    """
    resp = await client.get("/api/v1/reports/dossier?domain=UnchartedSector999")
    assert resp.status_code == 200
    data = resp.json()["data"]

    assert data["innovation_score"] == 0.0
    assert data["commercialization_readiness"] == 0.0
    assert data["data_sufficiency"] == "INSUFFICIENT_DATA"
    assert data["primary_commercial_pathway"] == "MONITOR_AND_GATHER_EVIDENCE"


@pytest.mark.asyncio
async def test_executive_dossier_export_markdown(client: AsyncClient):
    """
    Validates formatted Markdown dossier export endpoint.
    """
    resp = await client.get("/api/v1/reports/export/markdown?domain=Quantum Computing")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/markdown")
    md_text = resp.text

    assert "# Executive Intelligence Dossier: Quantum Computing" in md_text
    assert "## 1. Executive Summary" in md_text
    assert "## 2. Key Performance Indicators" in md_text
    assert "## 3. Strategic Assessment (SWOT Synthesis)" in md_text
    assert "## 4. Prioritized Commercialization Recommendations" in md_text
    assert "## 5. Strategic Roadmap Timeline" in md_text
    assert "## 6. Governance & Compliance Notice" in md_text


@pytest.mark.asyncio
async def test_executive_dossier_export_json(client: AsyncClient):
    """
    Validates structured JSON dossier export endpoint.
    """
    resp = await client.get("/api/v1/reports/export/json?domain=Quantum Computing")
    assert resp.status_code == 200
    data = resp.json()["data"]

    assert "report_id" in data
    assert "strategic_assessment" in data
    assert "roadmap" in data


@pytest.mark.asyncio
async def test_executive_portfolio_summary_and_benchmarks(client: AsyncClient):
    """
    Validates cross-domain executive summary and portfolio benchmark leaderboard.
    """
    resp = await client.get("/api/v1/reports/summary")
    assert resp.status_code == 200
    data = resp.json()["data"]

    assert "total_domains_benchmarked" in data
    assert "portfolio_average_innovation_score" in data
    assert "portfolio_average_readiness_score" in data
    assert "dominant_pathway" in data
    assert "domain_benchmarks" in data
    assert len(data["domain_benchmarks"]) >= 1


@pytest.mark.asyncio
async def test_executive_reports_api_endpoints(client: AsyncClient):
    """
    Validates all REST endpoints under /api/v1/reports/*.
    """
    # 1. Dossier
    r1 = await client.get("/api/v1/reports/dossier")
    assert r1.status_code == 200

    # 2. Summary
    r2 = await client.get("/api/v1/reports/summary")
    assert r2.status_code == 200

    # 3. Markdown Export
    r3 = await client.get("/api/v1/reports/export/markdown")
    assert r3.status_code == 200

    # 4. JSON Export
    r4 = await client.get("/api/v1/reports/export/json")
    assert r4.status_code == 200
