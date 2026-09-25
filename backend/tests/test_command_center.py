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
from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_command_center_unauthenticated_overview(client: AsyncClient):
    """
    Validates that unauthenticated users safely receive a global guest overview.
    """
    resp = await client.get("/api/v1/command-center/overview")
    assert resp.status_code == 200
    data = resp.json()["data"]

    assert data["user_name"] == "Guest Innovator"
    assert data["is_profile_scoped"] is False
    assert "role_metrics" in data
    assert "dominant_trl_stage" in data
    assert "upcoming_grant_deadlines" in data


@pytest.mark.asyncio
async def test_command_center_researcher_role_metrics(client: AsyncClient):
    """
    Validates researcher role-tailored metrics focusing on academic novelty and grant matchmaking.
    """
    async with TestingSessionLocal() as session:
        user = User(
            email="researcher_cc@mit.edu",
            hashed_password="pw",
            full_name="Prof. Researcher",
            role=UserRole.RESEARCHER,
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        token = create_access_token({"sub": str(user.id), "email": user.email})

    resp = await client.get(
        "/api/v1/command-center/overview",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()["data"]

    assert data["user_name"] == "Prof. Researcher"
    assert data["user_role"] == "researcher"
    assert "Novelty" in data["role_metrics"]["primary_metric_label"]
    assert "/funding" in data["role_metrics"]["focus_action_href"]


@pytest.mark.asyncio
async def test_command_center_startup_founder_role_metrics(client: AsyncClient):
    """
    Validates startup founder role-tailored metrics focusing on whitespaces and commercial readiness.
    """
    async with TestingSessionLocal() as session:
        founder = User(
            email="founder_cc@deeptech.io",
            hashed_password="pw",
            full_name="Alex Founder",
            role=UserRole.STARTUP_FOUNDER,
            is_active=True,
        )
        session.add(founder)
        await session.commit()
        await session.refresh(founder)

        token = create_access_token({"sub": str(founder.id), "email": founder.email})

    resp = await client.get(
        "/api/v1/command-center/overview",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()["data"]

    assert data["user_role"] == "startup_founder"
    assert "Commercial Readiness" in data["role_metrics"]["primary_metric_label"]
    assert "/technology-intelligence" in data["role_metrics"]["focus_action_href"]


@pytest.mark.asyncio
async def test_command_center_innovation_manager_role_metrics(client: AsyncClient):
    """
    Validates innovation manager role-tailored metrics focusing on portfolio benchmarking.
    """
    async with TestingSessionLocal() as session:
        manager = User(
            email="manager_cc@stanford.edu",
            hashed_password="pw",
            full_name="Maria Manager",
            role=UserRole.INNOVATION_MANAGER,
            is_active=True,
        )
        session.add(manager)
        await session.commit()
        await session.refresh(manager)

        token = create_access_token({"sub": str(manager.id), "email": manager.email})

    resp = await client.get(
        "/api/v1/command-center/overview",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()["data"]

    assert data["user_role"] == "innovation_manager"
    assert "Portfolio" in data["role_metrics"]["role_headline"]
    assert "/reports" in data["role_metrics"]["focus_action_href"]


@pytest.mark.asyncio
async def test_command_center_admin_role_metrics(client: AsyncClient):
    """
    Validates administrator role-tailored metrics focusing on telemetry and governance.
    """
    async with TestingSessionLocal() as session:
        admin = User(
            email="admin_cc@platform.gov",
            hashed_password="pw",
            full_name="Admin Chief",
            role=UserRole.ADMINISTRATOR,
            is_active=True,
        )
        session.add(admin)
        await session.commit()
        await session.refresh(admin)

        token = create_access_token({"sub": str(admin.id), "email": admin.email})

    resp = await client.get(
        "/api/v1/command-center/overview",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()["data"]

    assert data["user_role"] == "administrator"
    assert "Administration" in data["role_metrics"]["role_headline"]
    assert "/admin" in data["role_metrics"]["focus_action_href"]


@pytest.mark.asyncio
async def test_command_center_profile_scoped_isolation(client: AsyncClient):
    """
    Validates that a user with linked assets receives profile-scoped counts.
    """
    async with TestingSessionLocal() as session:
        user = User(
            email="scoped_cc@oxford.ac.uk",
            hashed_password="pw",
            full_name="Dr. Scoped Oxford",
            role=UserRole.RESEARCHER,
            is_active=True,
        )
        session.add(user)
        await session.flush()

        prof = Profile(user_id=user.id, institution="Oxford Quantum Lab")
        session.add(prof)
        await session.flush()

        pub = Publication(
            title="Silicon Photonic Neural Matrix Multipliers",
            authors="Dr. Scoped Oxford",
            doi="10.1038/s41586-025-001",
            publication_date=datetime(2025, 2, 1, tzinfo=timezone.utc),
            citation_count=25,
            primary_domain="Photonics",
            source="manual",
        )
        session.add(pub)
        await session.flush()
        await session.execute(profile_publications.insert().values(profile_id=prof.id, publication_id=pub.id))

        pat = Patent(
            patent_number="US11999888B2",
            title="Co-Packaged Optical Transceiver Substrate",
            assignee="Oxford Quantum",
            inventors="Dr. Scoped Oxford",
            filing_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            publication_date=datetime(2024, 6, 1, tzinfo=timezone.utc),
            patent_classification="G02B 6/12",
            technology_domain="Photonics",
            citation_count=10,
            source="manual",
        )
        session.add(pat)
        await session.flush()
        await session.execute(profile_patents.insert().values(profile_id=prof.id, patent_id=pat.id))
        await session.commit()

        token = create_access_token({"sub": str(user.id), "email": user.email})

    resp = await client.get(
        "/api/v1/command-center/overview",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()["data"]

    assert data["is_profile_scoped"] is True
    assert data["total_publications"] == 1
    assert data["total_patents"] == 1


@pytest.mark.asyncio
async def test_command_center_activity_feed_multi_stream(client: AsyncClient):
    """
    Validates cross-module activity feed API.
    """
    resp = await client.get("/api/v1/command-center/activity-feed")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_command_center_upcoming_grant_deadlines(client: AsyncClient):
    """
    Validates upcoming grant funding deadlines.
    """
    async with TestingSessionLocal() as session:
        fnd = FundingOpportunity(
            title="ARPA-E High Energy Advanced Storage",
            funding_agency="ARPA-E",
            funding_amount=3500000.0,
            status="open",
            application_deadline=datetime(2026, 12, 31, tzinfo=timezone.utc),
            external_id="ARPA-E-HE-2026",
            source="manual",
        )
        session.add(fnd)
        await session.commit()

    resp = await client.get("/api/v1/command-center/overview")
    assert resp.status_code == 200
    data = resp.json()["data"]

    assert len(data["upcoming_grant_deadlines"]) >= 1
    grant = data["upcoming_grant_deadlines"][0]
    assert "title" in grant
    assert "agency" in grant
