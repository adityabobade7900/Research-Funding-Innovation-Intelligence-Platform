import pytest
import pytest_asyncio
from httpx import AsyncClient

from tests.conftest import TestingSessionLocal
from app.models.user import User, UserRole
from app.models.profile import Profile
from app.core.security import create_access_token
from app.services.admin_service import AdminService


@pytest.mark.asyncio
async def test_admin_unauthenticated_and_non_admin_forbidden(client: AsyncClient):
    """
    Validates RBAC governance: unauthenticated requests and non-admin roles are rejected with 401/403.
    """
    # 1. Unauthenticated request
    r_unauth = await client.get("/api/v1/admin/users")
    assert r_unauth.status_code in [401, 403]

    # 2. Researcher authenticated request
    async with TestingSessionLocal() as session:
        researcher = User(
            email="regular_researcher@mit.edu",
            hashed_password="hashed_pw_test",
            full_name="Dr. Regular",
            role=UserRole.RESEARCHER,
            is_active=True,
        )
        session.add(researcher)
        await session.commit()
        await session.refresh(researcher)

        token = create_access_token({"sub": str(researcher.id), "email": researcher.email})

    r_forbidden = await client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r_forbidden.status_code == 403


@pytest.mark.asyncio
async def test_admin_list_users_with_role_and_search_filters(client: AsyncClient):
    """
    Validates user listing, pagination, role filtering, and search keyword matching.
    """
    async with TestingSessionLocal() as session:
        admin_user = User(
            email="super_admin@platform.gov",
            hashed_password="hashed_pw_admin",
            full_name="Platform Administrator",
            role=UserRole.ADMINISTRATOR,
            is_active=True,
            is_superuser=True,
        )
        u1 = User(
            email="quantum_researcher@lab.org",
            hashed_password="hashed_pw_u1",
            full_name="Dr. Alice Quantum",
            role=UserRole.RESEARCHER,
            is_active=True,
        )
        u2 = User(
            email="founder_bob@startup.io",
            hashed_password="hashed_pw_u2",
            full_name="Bob Founder",
            role=UserRole.STARTUP_FOUNDER,
            is_active=True,
        )
        session.add_all([admin_user, u1, u2])
        await session.commit()
        await session.refresh(admin_user)

        admin_token = create_access_token({"sub": str(admin_user.id), "email": admin_user.email})

    headers = {"Authorization": f"Bearer {admin_token}"}

    # Query all
    res = await client.get("/api/v1/admin/users", headers=headers)
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["total"] >= 3
    assert len(data["items"]) >= 3
    assert "role_counts" in data

    # Query with filter role=startup_founder
    res_founder = await client.get("/api/v1/admin/users?role=startup_founder", headers=headers)
    assert res_founder.status_code == 200
    founder_items = res_founder.json()["data"]["items"]
    assert all(item["role"] == "startup_founder" for item in founder_items)

    # Query with search keyword
    res_search = await client.get("/api/v1/admin/users?q=Alice", headers=headers)
    assert res_search.status_code == 200
    assert any("Alice" in item["full_name"] for item in res_search.json()["data"]["items"])


@pytest.mark.asyncio
async def test_admin_get_user_details(client: AsyncClient):
    """
    Validates retrieving full user details and profile metadata.
    """
    async with TestingSessionLocal() as session:
        admin_user = User(
            email="admin_inspect@platform.gov",
            hashed_password="hashed_pw_admin",
            full_name="Admin Inspect",
            role=UserRole.ADMINISTRATOR,
            is_active=True,
        )
        target_user = User(
            email="target_user@institution.edu",
            hashed_password="hashed_pw_target",
            full_name="Target Professor",
            role=UserRole.RESEARCHER,
            is_active=True,
        )
        session.add_all([admin_user, target_user])
        await session.commit()
        await session.refresh(admin_user)
        await session.refresh(target_user)

        prof = Profile(user_id=target_user.id, institution="Stanford University")
        session.add(prof)
        await session.commit()

        token = create_access_token({"sub": str(admin_user.id), "email": admin_user.email})

    res = await client.get(
        f"/api/v1/admin/users/{target_user.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["email"] == "target_user@institution.edu"
    assert data["institution"] == "Stanford University"


@pytest.mark.asyncio
async def test_admin_update_user_role_and_audit_event(client: AsyncClient):
    """
    Validates dynamic RBAC role modification and automated security audit event logging.
    """
    async with TestingSessionLocal() as session:
        admin_user = User(
            email="role_admin@platform.gov",
            hashed_password="hashed_pw_admin",
            full_name="Role Admin",
            role=UserRole.ADMINISTRATOR,
            is_active=True,
        )
        test_user = User(
            email="role_target@platform.gov",
            hashed_password="hashed_pw_user",
            full_name="Role Target",
            role=UserRole.RESEARCHER,
            is_active=True,
        )
        session.add_all([admin_user, test_user])
        await session.commit()
        await session.refresh(admin_user)
        await session.refresh(test_user)

        token = create_access_token({"sub": str(admin_user.id), "email": admin_user.email})

    headers = {"Authorization": f"Bearer {token}"}
    payload = {"role": "innovation_manager"}

    res = await client.put(f"/api/v1/admin/users/{test_user.id}/role", json=payload, headers=headers)
    assert res.status_code == 200
    assert res.json()["data"]["role"] == "innovation_manager"

    # Verify audit log recorded this role change
    res_audit = await client.get("/api/v1/admin/audit-logs?category=RBAC", headers=headers)
    assert res_audit.status_code == 200
    audit_items = res_audit.json()["data"]["items"]
    assert any("innovation_manager" in a["action_detail"] for a in audit_items)


@pytest.mark.asyncio
async def test_admin_update_user_status_deactivation(client: AsyncClient):
    """
    Validates account deactivation and reactivation workflows.
    """
    async with TestingSessionLocal() as session:
        admin_user = User(
            email="status_admin@platform.gov",
            hashed_password="hashed_pw_admin",
            full_name="Status Admin",
            role=UserRole.ADMINISTRATOR,
            is_active=True,
        )
        test_user = User(
            email="deactivate_target@platform.gov",
            hashed_password="hashed_pw_user",
            full_name="Deactivate Target",
            role=UserRole.RESEARCHER,
            is_active=True,
        )
        session.add_all([admin_user, test_user])
        await session.commit()
        await session.refresh(admin_user)
        await session.refresh(test_user)

        token = create_access_token({"sub": str(admin_user.id), "email": admin_user.email})

    headers = {"Authorization": f"Bearer {token}"}
    
    # Deactivate
    res_deact = await client.put(f"/api/v1/admin/users/{test_user.id}/status", json={"is_active": False}, headers=headers)
    assert res_deact.status_code == 200
    assert res_deact.json()["data"]["is_active"] is False

    # Reactivate
    res_act = await client.put(f"/api/v1/admin/users/{test_user.id}/status", json={"is_active": True}, headers=headers)
    assert res_act.status_code == 200
    assert res_act.json()["data"]["is_active"] is True


@pytest.mark.asyncio
async def test_admin_pipeline_telemetry_monitoring(client: AsyncClient):
    """
    Validates external pipeline telemetry: status, latencies, and sync stats across OpenAlex, USPTO, Grants.gov, etc.
    """
    async with TestingSessionLocal() as session:
        admin_user = User(
            email="telemetry_admin@platform.gov",
            hashed_password="hashed_pw_admin",
            full_name="Telemetry Admin",
            role=UserRole.ADMINISTRATOR,
            is_active=True,
        )
        session.add(admin_user)
        await session.commit()
        await session.refresh(admin_user)

        token = create_access_token({"sub": str(admin_user.id), "email": admin_user.email})

    res = await client.get("/api/v1/admin/telemetry/pipelines", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()["data"]

    assert data["total_pipelines"] >= 6
    assert data["active_pipelines"] >= 6
    assert len(data["pipelines"]) >= 6

    providers = [p["provider_name"] for p in data["pipelines"]]
    assert "openalex" in providers
    assert "uspto" in providers
    assert "grants_gov" in providers
    assert all(p["latency_ms"] > 0.0 for p in data["pipelines"])


@pytest.mark.asyncio
async def test_admin_system_overview_capacity_metrics(client: AsyncClient):
    """
    Validates platform capacity, entity counts, grant capital, and database health metrics.
    """
    async with TestingSessionLocal() as session:
        admin_user = User(
            email="overview_admin@platform.gov",
            hashed_password="hashed_pw_admin",
            full_name="Overview Admin",
            role=UserRole.ADMINISTRATOR,
            is_active=True,
        )
        session.add(admin_user)
        await session.commit()
        await session.refresh(admin_user)

        token = create_access_token({"sub": str(admin_user.id), "email": admin_user.email})

    res = await client.get("/api/v1/admin/system/overview", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()["data"]

    assert data["total_users"] >= 1
    assert data["database_status"] == "HEALTHY"
    assert data["migration_head"] == "f8e9f392e6c3"
    assert "role_distribution" in data


@pytest.mark.asyncio
async def test_admin_audit_logs_category_filtering(client: AsyncClient):
    """
    Validates security and administrative audit event logging and category filtering.
    """
    async with TestingSessionLocal() as session:
        admin_user = User(
            email="audit_admin@platform.gov",
            hashed_password="hashed_pw_admin",
            full_name="Audit Admin",
            role=UserRole.ADMINISTRATOR,
            is_active=True,
        )
        session.add(admin_user)
        await session.commit()
        await session.refresh(admin_user)

        token = create_access_token({"sub": str(admin_user.id), "email": admin_user.email})

    # Record test event
    AdminService.record_audit_event(
        actor_email="audit_admin@platform.gov",
        actor_role="administrator",
        action_category="INGESTION",
        action_detail="Manual trigger for OpenAlex publication sync",
        target_resource="OpenAlexPipeline",
    )

    res = await client.get("/api/v1/admin/audit-logs?category=INGESTION", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["total"] >= 1
    assert any(item["action_category"] == "INGESTION" for item in data["items"])
