# 26_NEXT_STEPS.md — Recommended Development Roadmap

> **ENGINEERING CONTINUITY PRINCIPLE:**  
> **DO NOT RESTART THE PROJECT.**  
> Start directly from the verified baseline: Milestones 1, 2, and 3 are 100% complete and tested. Milestone 4 is ~85% complete.  
> Follow this sequenced plan to complete the remaining requirements and achieve production readiness.

---

## 1. Top 5 Immediate Implementation Steps

### Step 1: Complete Module 10 (Notification & Alert System)
- **Objective:** Bridge the final functional gap in Module 10 by introducing persistent alert tracking.
- **Actions:**
  1. Author a new SQLAlchemy model `backend/app/models/notification.py` defining `id`, `user_id`, `category` (grant_deadline, paper_published, patent_alert), `title`, `message`, `is_read`, `created_at`.
  2. Generate and apply Alembic migration:
     ```bash
     alembic revision --autogenerate -m "add_notifications_table"
     alembic upgrade head
     ```
  3. Create REST endpoints in `backend/app/api/v1/endpoints/notifications.py`:
     - `GET /api/v1/notifications`: List unread notifications for the active user.
     - `PUT /api/v1/notifications/{id}/read`: Mark notification as read.
     - `PUT /api/v1/notifications/read-all`: Mark all as read.
  4. Connect an in-app notification bell icon in the Next.js header (`frontend/src/components/layout/Navbar.tsx`).

### Step 2: Configure GitHub Actions CI/CD Pipeline (Module 12)
- **Objective:** Automatically validate all commits and pull requests in cloud CI.
- **Actions:**
  1. Create directory `.github/workflows/`.
  2. Author `.github/workflows/ci.yml` running:
     - Python 3.10 setup, `pip install -r backend/requirements.txt`, and `pytest backend/tests/ -v`.
     - Node.js 20 setup, `npm install`, and `npm test` in `frontend/`.
     - Static compilation check: `npx next build` in `frontend/`.

### Step 3: Author Full-Stack Production Containerization (Module 12)
- **Objective:** Provide a turnkey, single-command deployment for evaluators.
- **Actions:**
  1. Author `frontend/Dockerfile` using multi-stage `node:20-alpine` with Next.js standalone output.
  2. Create root `docker-compose.prod.yml` orchestrating:
     - `postgres` (PostgreSQL 16)
     - `backend` (FastAPI with 4 Uvicorn workers)
     - `frontend` (Next.js production container)
     - `nginx` (Reverse proxy on port 80 routing `/api/` to backend and other routes to frontend).

### Step 4: Batch Seed Database with Scientific Papers & Grants
- **Objective:** Transition the platform from fallback fixtures to a dense, persistent database corpus.
- **Actions:**
  1. Write a standalone utility script `backend/scripts/seed_database.py`.
  2. Utilize `OpenAlexProvider` and `SemanticScholarProvider` to ingest 100+ papers across Quantum Computing, Biotechnology, and Clean Energy into PostgreSQL.
  3. Utilize `GrantsGovProvider` and `NSFFundingProvider` to ingest 50+ active funding opportunities.

### Step 5: Implement Binary Report Exports (Module 11)
- **Objective:** Deliver the PDF and Excel file export formats specified in official requirements.
- **Actions:**
  1. Add `reportlab` and `openpyxl` to `backend/requirements.txt`.
  2. Implement binary streaming endpoints in `backend/app/api/v1/endpoints/executive_reports.py`:
     - `GET /api/v1/reports/export/pdf`
     - `GET /api/v1/reports/export/excel`
  3. Add corresponding download buttons to `/reports` in the Next.js UI.
