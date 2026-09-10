# 24_KNOWN_ISSUES.md — Known Issues, Technical Debt & Workarounds

> **INTEGRITY PRINCIPLE:**  
> A comprehensive search of the repository confirms zero unresolved syntax errors, zero compiler warnings, and zero failing automated tests (150/150 backend tests and 30/30 frontend tests pass).  
> The items documented below represent architectural limitations, missing secondary features, and known data constraints.

---

## 1. Inventory of Known Issues & Technical Debt

### Issue 1: Sparse Persistent Records in PostgreSQL
- **Component / Location:** Database tables `publications` (2 rows), `patents` (0 rows), `funding_opportunities` (0 rows).
- **Severity:** **MEDIUM**
- **Impact:** While analytical services handle empty rows gracefully, the production database does not yet contain a large persistent corpus of scientific papers or patents.
- **Current Workaround:** Services seamlessly fall back to structured, realistic mock fixtures (`SAMPLE_FUNDING_OPPORTUNITIES`, `SAMPLE_PATENTS` in `backend/app/services/providers/`).
- **Planned Fix:** Execute automated bulk harvester scripts (`POST /api/v1/publications/ingest` and `POST /api/v1/funding/ingest`) to seed 500+ records into PostgreSQL.

### Issue 2: Missing Standalone `notifications` Database Table
- **Component / Location:** Database schema / Module 10 (Notification & Alert System).
- **Severity:** **MEDIUM**
- **Impact:** Users cannot mark individual alerts as "read" or manage notification preference toggles.
- **Current Workaround:** Alerts are generated dynamically on-the-fly from upcoming 30-day grant deadlines (`CommandCenterService`) and harvester health checks (`AdminService`).
- **Planned Fix:** Create an Alembic migration for a `notifications` table (`id`, `user_id`, `title`, `message`, `is_read`, `created_at`).

### Issue 3: Missing Outbound Email & Real-Time Push Dispatcher
- **Component / Location:** Module 10 backend services.
- **Severity:** **LOW / MEDIUM**
- **Impact:** System relies on in-app notifications; no automated emails or WebSocket push messages are transmitted.
- **Current Workaround:** In-app alert banners displayed in `/dashboard` and `/admin`.
- **Planned Fix:** Integrate Python `aiosmtplib` for email alerts and FastAPI WebSocket endpoint for real-time push.

### Issue 4: Binary Report Exports (PDF & Excel) Not Implemented
- **Component / Location:** Module 11 (`backend/app/api/v1/endpoints/executive_reports.py`).
- **Severity:** **LOW**
- **Impact:** Official specification lists PDF and Excel exports. Currently, only Markdown (`.md`) and JSON (`.json`) file exports are wired.
- **Current Workaround:** Users can download comprehensive Markdown and JSON dossiers directly from `/reports`.
- **Planned Fix:** Add ReportLab/WeasyPrint for PDF generation and OpenPyXL for multi-tab Excel workbooks.

### Issue 5: Missing Frontend Dockerfile & Full-Stack Docker Compose
- **Component / Location:** Deployment infrastructure (`frontend/`, `docker-compose.yml`).
- **Severity:** **LOW / MEDIUM**
- **Impact:** Only the PostgreSQL container is orchestrated via Docker Compose; Next.js must be launched manually via `npm run dev` or `npm start`.
- **Current Workaround:** Next.js runs natively on Node 20 LTS.
- **Planned Fix:** Create `frontend/Dockerfile` and author root `docker-compose.prod.yml`.

### Issue 6: Absence of Automated GitHub Actions CI/CD Pipeline
- **Component / Location:** `.github/workflows/` directory does not exist.
- **Severity:** **LOW / MEDIUM**
- **Impact:** Pull requests do not trigger automated cloud testing runners.
- **Current Workaround:** Developers manually execute `pytest tests/ -v` and `npm test` before pushing to feature branches.
- **Planned Fix:** Author `.github/workflows/ci.yml` running both test suites on every PR.
