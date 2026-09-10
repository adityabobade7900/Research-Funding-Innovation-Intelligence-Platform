# MODULE_10_NOTIFICATIONS.md — Notification & Alert System

# Objective
Provide real-time and scheduled alerting for upcoming grant application deadlines, newly published scientific research matching user interests, newly filed competitor patents, and connector pipeline health issues.

# Official Requirements
- New funding alerts
- Patent monitoring alerts
- Emerging technology alerts
- Research trend updates
- Commercialization opportunities
- Platform notifications

# Mentor Requirements
- In-app deadline tracking alerting users to grants expiring within 30 days.
- Harvester connector failure alerts for system administrators.
- User notification preference management.
- Multi-channel dispatching (In-app, Email).

# Current Implementation
- **Current Completion:** 🟡 **PARTIALLY IMPLEMENTED (40%)**
- **Implemented:**
  - `CommandCenterService` scans funding opportunities and surfaces urgent deadline warning cards on `/dashboard`.
  - `AdminService` detects connector timeouts and surfaces pipeline failure alerts on `/admin`.
- **Missing / Not Implemented:**
  - Dedicated `notifications` table in PostgreSQL.
  - Outbound SMTP email dispatcher.
  - WebSocket push notification gateway.

# Frontend
- Visual in-app alert cards rendered in `/dashboard` (Upcoming Grant Deadlines) and `/admin` (Connector Telemetry Alerts).
- Dedicated notification center dropdown with unread badge is **PLANNED**.

# Backend
- Logic currently embedded in `backend/app/services/command_center_service.py` and `admin_service.py`.
- Dedicated router `backend/app/api/v1/endpoints/notifications.py` is **PLANNED**.

# Database
- **Status:** The `notifications` table does **NOT** exist in the current schema.
- **Planned Schema:** `id`, `user_id` (FK `users.id`), `category`, `title`, `message`, `is_read`, `created_at`.

# APIs
- Existing: `GET /api/v1/command-center/activity-feed` (includes deadline warnings).
- Planned: `GET /api/v1/notifications`, `PUT /api/v1/notifications/{id}/read`, `PUT /api/v1/notifications/read-all`.

# AI/ML
- None.

# External Data Sources
- None.

# Integration With Other Modules
- Inspects `funding_opportunities` deadlines from Module 3.
- Inspects harvester health from Module 12.

# Testing
- Tested indirectly via `backend/tests/test_command_center.py` and `test_admin.py`.
- Dedicated notification unit tests will be added upon table creation.

# Known Issues
- Users cannot dismiss or mark individual notifications as read.
- No email alerts are sent when deadlines approach.

# Missing Requirements
- Alembic migration for `notifications` table.
- Notification preference settings in profile.
- SMTP email dispatcher worker.

# Next Steps
- Implement `Notification` SQLAlchemy model and Alembic migration as first priority in [26_NEXT_STEPS.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/26_NEXT_STEPS.md).

# Evidence / File Paths
- [command_center_service.py](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/services/command_center_service.py#L80-L120)
- [admin_service.py](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/services/admin_service.py#L35-L60)
- [dashboard/page.tsx](file:///d:/Infosys%207.0/Intelligent-Research1/frontend/src/app/(dashboard)/dashboard/page.tsx)
