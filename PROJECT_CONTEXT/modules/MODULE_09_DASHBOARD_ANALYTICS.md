# MODULE_09_DASHBOARD_ANALYTICS.md — Dashboard & Analytics System

# Objective
Provide role-tailored analytical dashboards and an executive command center for four primary user personas (`researcher`, `startup_founder`, `innovation_manager`, and `administrator`), presenting operational KPIs, an integrated activity feed, and administrative governance telemetry.

# Official Requirements
- Researcher Dashboard: Funding recommendations, research trends, publication analytics, patent insights, innovation score.
- Startup Dashboard: Funding opportunities, technology opportunities, patent intelligence, commercialization insights.
- Innovation Manager Dashboard: Portfolio analytics, innovation pipeline tracking, technology trend monitoring.
- Admin Dashboard: User management, platform analytics, pipeline monitoring, system reports.

# Mentor Requirements
- Dynamic UI adapting metrics automatically based on authenticated user's role.
- Real-time multi-source activity feed.
- Grant application deadline tracking (highlighting deadlines within 30 days).
- Comprehensive administrator governance and security audit logging.

# Current Implementation
- `CommandCenterService` provides role-tailored KPI summaries and aggregates a chronological multi-source activity feed with 30-day deadline countdowns.
- `AdminService` provides platform-wide telemetry, harvester pipeline status toggles, user management (role updates, activation/deactivation), and security audit trails.

# Frontend
- Route: `/dashboard` in `frontend/src/app/(dashboard)/dashboard/page.tsx` (Command Center overview, KPI cards, activity feed, upcoming deadlines).
- Route: `/admin` in `frontend/src/app/(dashboard)/admin/page.tsx` (Administrator governance, harvester telemetry, user role table, audit logs).

# Backend
- Routers: `backend/app/api/v1/endpoints/command_center.py` and `admin.py`
- Services: `backend/app/services/command_center_service.py` and `admin_service.py`
- Schemas: `backend/app/schemas/command_center.py` and `admin.py`

# Database
- Queries across `users`, `profiles`, `publications`, `patents`, and `funding_opportunities`.

# APIs
- `GET /api/v1/command-center/overview`
- `GET /api/v1/command-center/activity-feed`
- `GET /api/v1/admin/system/overview`
- `GET /api/v1/admin/telemetry/pipelines`
- `GET /api/v1/admin/users` & `GET /api/v1/admin/users/{id}`
- `PUT /api/v1/admin/users/{id}/role` & `PUT /api/v1/admin/users/{id}/status`
- `GET /api/v1/admin/audit-logs`

# AI/ML
- None (Visualization and aggregation domain).

# External Data Sources
- Ingested platform database records.

# Integration With Other Modules
- Aggregates outputs from Modules 1, 2, 3, 4, 5, 6, 7, and 8 into unified views.
- Controls system administration for Module 12.

# Testing
- `backend/tests/test_command_center.py` (6 passing tests).
- `backend/tests/test_admin.py` (8 passing tests).
- `frontend/src/lib/command_center.test.ts` (3 passing tests).
- `frontend/src/lib/admin.test.ts` (3 passing tests).

# Known Issues
- None; both dashboards are fully operational and verified by automated tests.

# Missing Requirements
- Drag-and-drop widget layout customization.

# Next Steps
- Add user-configurable dashboard widget preferences.

# Evidence / File Paths
- [command_center.py](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/api/v1/endpoints/command_center.py)
- [admin.py](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/api/v1/endpoints/admin.py)
- [command_center_service.py](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/services/command_center_service.py)
- [admin_service.py](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/services/admin_service.py)
- [dashboard/page.tsx](file:///d:/Infosys%207.0/Intelligent-Research1/frontend/src/app/(dashboard)/dashboard/page.tsx)
- [admin/page.tsx](file:///d:/Infosys%207.0/Intelligent-Research1/frontend/src/app/(dashboard)/admin/page.tsx)
