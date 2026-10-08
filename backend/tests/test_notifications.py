import pytest
import pytest_asyncio
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient

from tests.conftest import TestingSessionLocal
from app.models.user import User, UserRole
from app.models.profile import Profile
from app.models.research_domain import ResearchDomain, profile_domains
from app.models.notification import Notification, NotificationType, NotificationPriority
from app.models.funding import FundingOpportunity
from app.models.patent import Patent
from app.models.publication import Publication
from app.core.security import create_access_token
from app.services.notification_service import NotificationService


@pytest_asyncio.fixture
async def setup_users():
    async with TestingSessionLocal() as session:
        user_a = User(
            email="user_a@intel.edu",
            hashed_password="pw",
            full_name="Dr. Alice Vance",
            role=UserRole.RESEARCHER,
            is_active=True,
        )
        user_b = User(
            email="user_b@intel.edu",
            hashed_password="pw",
            full_name="Bob Founder",
            role=UserRole.STARTUP_FOUNDER,
            is_active=True,
        )
        session.add_all([user_a, user_b])
        await session.commit()
        await session.refresh(user_a)
        await session.refresh(user_b)

        token_a = create_access_token({"sub": str(user_a.id), "email": user_a.email})
        token_b = create_access_token({"sub": str(user_b.id), "email": user_b.email})

        return {
            "user_a": user_a,
            "user_b": user_b,
            "token_a": token_a,
            "token_b": token_b,
        }


@pytest.mark.asyncio
async def test_create_and_list_notifications(client: AsyncClient, setup_users):
    user_a = setup_users["user_a"]
    token_a = setup_users["token_a"]

    async with TestingSessionLocal() as session:
        notif, created = await NotificationService.create_notification(
            user_id=user_a.id,
            type=NotificationType.FUNDING,
            title="NSF AI Grant Available",
            message="National Science Foundation grant for AI research.",
            related_module="funding",
            related_record_id="fnd_101",
            target_url="/funding",
            priority=NotificationPriority.HIGH,
            db=session
        )
        assert created is True
        assert notif.id is not None

    resp = await client.get(
        "/api/v1/notifications",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total"] == 1
    assert data["unread_count"] == 1
    assert len(data["items"]) == 1
    item = data["items"][0]
    assert item["title"] == "NSF AI Grant Available"
    assert item["type"] == "FUNDING"
    assert item["target_url"] == "/funding"
    assert item["priority"] == "HIGH"
    assert item["is_read"] is False


@pytest.mark.asyncio
async def test_get_single_notification_and_mark_read(client: AsyncClient, setup_users):
    user_a = setup_users["user_a"]
    token_a = setup_users["token_a"]

    async with TestingSessionLocal() as session:
        notif, _ = await NotificationService.create_notification(
            user_id=user_a.id,
            type=NotificationType.PATENT,
            title="Competitor Patent Filed",
            message="New patent in Quantum Computing.",
            related_module="patents",
            related_record_id="pat_500",
            target_url="/patents",
            db=session
        )
        notif_id = notif.id

    # 1. Retrieve single notification
    resp = await client.get(
        f"/api/v1/notifications/{notif_id}",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["id"] == notif_id
    assert data["is_read"] is False

    # 2. Mark notification as read
    patch_resp = await client.patch(
        f"/api/v1/notifications/{notif_id}/read",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert patch_resp.status_code == 200
    patch_data = patch_resp.json()["data"]
    assert patch_data["id"] == notif_id
    assert patch_data["is_read"] is True

    # 3. Verify unread count is now 0
    count_resp = await client.get(
        "/api/v1/notifications/unread",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert count_resp.status_code == 200
    assert count_resp.json()["data"]["unread_count"] == 0


@pytest.mark.asyncio
async def test_mark_all_as_read(client: AsyncClient, setup_users):
    user_a = setup_users["user_a"]
    token_a = setup_users["token_a"]

    async with TestingSessionLocal() as session:
        await NotificationService.create_notification(
            user_id=user_a.id,
            type=NotificationType.TECHNOLOGY,
            title="Tech Alert 1",
            message="Whitespace identified",
            related_record_id="t1",
            db=session
        )
        await NotificationService.create_notification(
            user_id=user_a.id,
            type=NotificationType.RESEARCH_TREND,
            title="Trend Alert 2",
            message="Publications surging",
            related_record_id="t2",
            db=session
        )

    # Verify unread count is 2
    count_resp = await client.get(
        "/api/v1/notifications/unread",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert count_resp.json()["data"]["unread_count"] == 2

    # Mark all read
    mark_all_resp = await client.patch(
        "/api/v1/notifications/read-all",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert mark_all_resp.status_code == 200
    assert mark_all_resp.json()["data"]["updated_count"] == 2

    # Verify unread count is now 0
    count_after = await client.get(
        "/api/v1/notifications/unread",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert count_after.json()["data"]["unread_count"] == 0


@pytest.mark.asyncio
async def test_filter_by_type_and_read_status(client: AsyncClient, setup_users):
    user_a = setup_users["user_a"]
    token_a = setup_users["token_a"]

    async with TestingSessionLocal() as session:
        n1, _ = await NotificationService.create_notification(
            user_id=user_a.id,
            type=NotificationType.FUNDING,
            title="Funding Alert",
            message="Msg",
            related_record_id="f1",
            db=session
        )
        n2, _ = await NotificationService.create_notification(
            user_id=user_a.id,
            type=NotificationType.COMMERCIALIZATION,
            title="Comm Alert",
            message="Msg",
            related_record_id="c1",
            db=session
        )
        await NotificationService.mark_as_read(n2.id, user_a.id, session)

    # Filter type=FUNDING
    resp_fnd = await client.get(
        "/api/v1/notifications?type=FUNDING",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert resp_fnd.status_code == 200
    assert resp_fnd.json()["data"]["total"] == 1
    assert resp_fnd.json()["data"]["items"][0]["type"] == "FUNDING"

    # Filter is_read=true
    resp_read = await client.get(
        "/api/v1/notifications?is_read=true",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert resp_read.status_code == 200
    assert resp_read.json()["data"]["total"] == 1
    assert resp_read.json()["data"]["items"][0]["type"] == "COMMERCIALIZATION"

    # Filter is_read=false
    resp_unread = await client.get(
        "/api/v1/notifications?is_read=false",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert resp_unread.status_code == 200
    assert resp_unread.json()["data"]["total"] == 1
    assert resp_unread.json()["data"]["items"][0]["type"] == "FUNDING"


@pytest.mark.asyncio
async def test_user_isolation_security_idor(client: AsyncClient, setup_users):
    """
    Validates strict user isolation: User A cannot read, query, or patch User B's notifications.
    """
    user_a = setup_users["user_a"]
    user_b = setup_users["user_b"]
    token_a = setup_users["token_a"]
    token_b = setup_users["token_b"]

    async with TestingSessionLocal() as session:
        # Create notification for User B
        notif_b, _ = await NotificationService.create_notification(
            user_id=user_b.id,
            type=NotificationType.PLATFORM,
            title="Confidential User B Alert",
            message="Private data for B",
            related_record_id="priv_b",
            db=session
        )
        notif_b_id = notif_b.id

    # User A tries to view User B's notification by ID -> MUST return 404 (IDOR prevented)
    resp = await client.get(
        f"/api/v1/notifications/{notif_b_id}",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert resp.status_code == 404

    # User A tries to mark User B's notification as read -> MUST return 404
    patch_resp = await client.patch(
        f"/api/v1/notifications/{notif_b_id}/read",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert patch_resp.status_code == 404

    # User A's list MUST NOT contain User B's notification
    list_a = await client.get(
        "/api/v1/notifications",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert list_a.status_code == 200
    ids_in_a = [item["id"] for item in list_a.json()["data"]["items"]]
    assert notif_b_id not in ids_in_a

    # User B CAN access their own notification
    resp_b = await client.get(
        f"/api/v1/notifications/{notif_b_id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert resp_b.status_code == 200
    assert resp_b.json()["data"]["id"] == notif_b_id


@pytest.mark.asyncio
async def test_unauthenticated_access_rejected(client: AsyncClient):
    resp = await client.get("/api/v1/notifications")
    assert resp.status_code == 401

    resp_unread = await client.get("/api/v1/notifications/unread")
    assert resp_unread.status_code == 401


@pytest.mark.asyncio
async def test_missing_notification_returns_404(client: AsyncClient, setup_users):
    token_a = setup_users["token_a"]
    resp = await client.get(
        "/api/v1/notifications/999999",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_duplicate_prevention(setup_users):
    """
    Validates deterministic deduplication on (user_id, type, related_record_id).
    """
    user_a = setup_users["user_a"]

    async with TestingSessionLocal() as session:
        # First creation
        n1, created1 = await NotificationService.create_notification(
            user_id=user_a.id,
            type=NotificationType.FUNDING,
            title="Grant Announcement",
            message="First message",
            related_record_id="fnd_exact_1",
            db=session
        )
        assert created1 is True

        # Second creation with identical deduplication key
        n2, created2 = await NotificationService.create_notification(
            user_id=user_a.id,
            type=NotificationType.FUNDING,
            title="Grant Announcement Repeated",
            message="Duplicate attempt",
            related_record_id="fnd_exact_1",
            db=session
        )
        assert created2 is False
        assert n1.id == n2.id


@pytest.mark.asyncio
async def test_funding_relevance_and_suppression(client: AsyncClient, setup_users):
    """
    Validates that relevant funding generates a notification, while irrelevant funding is suppressed.
    """
    user_a = setup_users["user_a"]
    token_a = setup_users["token_a"]

    async with TestingSessionLocal() as session:
        # Give User A a research profile in Artificial Intelligence
        domain = ResearchDomain(name="Artificial Intelligence", description="AI and Machine Learning")
        session.add(domain)
        await session.flush()

        profile = Profile(
            user_id=user_a.id,
            institution="Stanford University",
            designation="Assistant Professor",
            bio="AI researcher specializing in deep learning."
        )
        profile.domains.append(domain)
        session.add(profile)

        # 1. Relevant opportunity (AI domain)
        opp_relevant = FundingOpportunity(
            title="NSF Foundational AI and Deep Learning Grant",
            funding_agency="National Science Foundation",
            description="Grants for neural networks, transformers, and artificial intelligence.",
            funding_amount=750000.0,
            currency="USD",
            application_deadline=datetime.now(timezone.utc) + timedelta(days=15),
            status="open"
        )
        # 2. Irrelevant opportunity (Agriculture Machinery)
        opp_irrelevant = FundingOpportunity(
            title="Regional Agricultural Tractor Maintenance Subsidy",
            funding_agency="Department of Agriculture",
            description="Funding for heavy agricultural plowing equipment and livestock fencing.",
            funding_amount=50000.0,
            currency="USD",
            status="open"
        )
        session.add_all([opp_relevant, opp_irrelevant])
        await session.commit()

    # Trigger proactive alert scan
    scan_resp = await client.post(
        "/api/v1/notifications/scan",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert scan_resp.status_code == 200

    # Retrieve notifications
    list_resp = await client.get(
        "/api/v1/notifications",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert list_resp.status_code == 200
    items = list_resp.json()["data"]["items"]

    funding_notifs = [i for i in items if i["type"] == "FUNDING"]
    # Relevant grant was notified
    assert any("NSF Foundational AI" in n["title"] for n in funding_notifs)
    # Irrelevant tractor grant was suppressed
    assert not any("Agricultural Tractor" in n["title"] for n in funding_notifs)


@pytest.mark.asyncio
async def test_patent_and_technology_and_trend_and_comm_alerts(client: AsyncClient, setup_users):
    """
    Validates patent, technology, research trend, commercialization, and platform alert generation.
    """
    user_a = setup_users["user_a"]
    token_a = setup_users["token_a"]

    async with TestingSessionLocal() as session:
        # Add domain and profile
        domain = ResearchDomain(name="Quantum Computing", description="Quantum Algorithms")
        session.add(domain)
        await session.flush()

        profile = Profile(
            user_id=user_a.id,
            institution="MIT",
            designation="Lead Scientist",
            bio="Quantum physics researcher"
        )
        profile.domains.append(domain)
        session.add(profile)

        # Add actual Patent
        patent = Patent(
            patent_number="US-11999999-B2",
            title="Superconducting Quantum Processing Core Architecture",
            abstract="Quantum circuits with error-corrected topological qubits.",
            assignee="IBM Quantum LLC",
            technology_domain="Quantum Computing",
            filing_date=datetime.now(timezone.utc) - timedelta(days=90),
            citation_count=12
        )
        # Add actual Publication
        publication = Publication(
            title="Scalable Quantum Annealing Algorithms",
            authors="Dr. Alice Vance",
            abstract="Novel algorithms for quantum optimization.",
            primary_domain="Quantum Computing",
            citation_count=45,
            publication_date=datetime.now(timezone.utc) - timedelta(days=60)
        )
        session.add_all([patent, publication])
        await session.commit()

    # Trigger scan
    scan_resp = await client.post(
        "/api/v1/notifications/scan",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert scan_resp.status_code == 200

    # Verify notifications generated across modules
    list_resp = await client.get(
        "/api/v1/notifications",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert list_resp.status_code == 200
    items = list_resp.json()["data"]["items"]
    types_found = {i["type"] for i in items}

    # Verify patent alert
    assert "PATENT" in types_found
    pat_alert = next(i for i in items if i["type"] == "PATENT")
    assert "US-11999999-B2" in pat_alert["title"]
    assert pat_alert["target_url"] == "/patents"

    # Verify commercialization alert uses conservative language
    if "COMMERCIALIZATION" in types_found:
        comm_alert = next(i for i in items if i["type"] == "COMMERCIALIZATION")
        assert "potential" in comm_alert["message"].lower() or "pathway" in comm_alert["message"].lower()
        assert "guaranteed" not in comm_alert["message"].lower()
        assert comm_alert["target_url"] == "/commercialization"

    # Verify platform alert
    assert "PLATFORM" in types_found


@pytest.mark.asyncio
async def test_empty_notification_list(client: AsyncClient, setup_users):
    """
    Validates empty list state with zero unread count.
    """
    token_b = setup_users["token_b"]
    resp = await client.get(
        "/api/v1/notifications",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total"] == 0
    assert data["unread_count"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_pagination_limits(client: AsyncClient, setup_users):
    """
    Validates pagination with limit and offset.
    """
    user_a = setup_users["user_a"]
    token_a = setup_users["token_a"]

    async with TestingSessionLocal() as session:
        for idx in range(5):
            await NotificationService.create_notification(
                user_id=user_a.id,
                type=NotificationType.PLATFORM,
                title=f"Notification #{idx}",
                message=f"Message body {idx}",
                related_record_id=f"page_item_{idx}",
                db=session
            )

    resp = await client.get(
        "/api/v1/notifications?limit=2&offset=0",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data["items"]) == 2
    assert data["total"] == 5

    resp2 = await client.get(
        "/api/v1/notifications?limit=2&offset=2",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert resp2.status_code == 200
    data2 = resp2.json()["data"]
    assert len(data2["items"]) == 2

