# api/ENDPOINT_STATUS.md — Exhaustive REST Endpoint Implementation Status

Total Endpoints Documented: **82 Routes** across 14 API Groups.

---

## 1. Status Legend
- 🟢 **LIVE & TESTED:** Endpoint active, backed by unit tests and Next.js UI integration.
- 🟡 **PARTIAL:** Backend route functions, but UI or data persistence is incomplete.
- ⚪ **STUB / STATIC:** Static HTML documentation or diagnostic redirection routes.

---

## 2. Exhaustive Endpoint Status Table

| # | Group | Method | Path | Auth? | Controller File | Test File | Status |
| :---: | :--- | :---: | :--- | :---: | :--- | :--- | :---: |
| 1 | System | `GET` | `/` | No | `app/main.py` | `test_health.py` | 🟢 LIVE |
| 2 | Health | `GET` | `/api/v1/health` | No | `endpoints/health.py` | `test_health.py` | 🟢 LIVE |
| 3 | Auth | `POST` | `/api/v1/auth/register` | No | `endpoints/auth.py` | `test_auth.py`, `test_rbac.py` | 🟢 LIVE |
| 4 | Auth | `POST` | `/api/v1/auth/login` | No | `endpoints/auth.py` | `test_auth.py` | 🟢 LIVE |
| 5 | Auth | `POST` | `/api/v1/auth/login/form` | No | `endpoints/auth.py` | `test_auth.py` | 🟢 LIVE |
| 6 | Auth | `POST` | `/api/v1/auth/refresh` | No | `endpoints/auth.py` | `test_auth.py` | 🟢 LIVE |
| 7 | Auth | `POST` | `/api/v1/auth/logout` | Yes | `endpoints/auth.py` | `test_auth.py` | 🟢 LIVE |
| 8 | Auth | `GET` | `/api/v1/auth/me` | Yes | `endpoints/auth.py` | `test_auth.py` | 🟢 LIVE |
| 9 | Auth | `PUT` | `/api/v1/auth/me` | Yes | `endpoints/auth.py` | `test_auth.py` | 🟢 LIVE |
| 10 | Auth | `GET` | `/api/v1/auth/test/researcher-only` | Yes | `endpoints/auth.py` | `test_rbac.py` | 🟢 LIVE |
| 11 | Auth | `GET` | `/api/v1/auth/test/founder-only` | Yes | `endpoints/auth.py` | `test_rbac.py` | 🟢 LIVE |
| 12 | Auth | `GET` | `/api/v1/auth/test/manager-only` | Yes | `endpoints/auth.py` | `test_rbac.py` | 🟢 LIVE |
| 13 | Auth | `GET` | `/api/v1/auth/test/admin-only` | Yes | `endpoints/auth.py` | `test_rbac.py` | 🟢 LIVE |
| 14 | Profile | `GET` | `/api/v1/profile/domains` | No | `endpoints/profile.py` | `test_profile_extended.py` | 🟢 LIVE |
| 15 | Profile | `GET` | `/api/v1/profile/me` | Yes | `endpoints/profile.py` | `test_profile.py` | 🟢 LIVE |
| 16 | Profile | `PUT` | `/api/v1/profile/me` | Yes | `endpoints/profile.py` | `test_profile.py` | 🟢 LIVE |
| 17 | Profile | `GET` | `/api/v1/profile/{user_id}` | Yes | `endpoints/profile.py` | `test_profile.py` | 🟢 LIVE |
| 18 | Publications | `GET` | `/api/v1/publications` | No | `endpoints/publications.py` | `test_publications.py` | 🟢 LIVE |
| 19 | Publications | `POST` | `/api/v1/publications` | Yes | `endpoints/publications.py` | `test_publications.py` | 🟢 LIVE |
| 20 | Publications | `POST` | `/api/v1/publications/ingest` | Yes | `endpoints/publications.py` | `test_ingest.py`, `test_providers.py` | 🟢 LIVE |
| 21 | Publications | `GET` | `/api/v1/publications/my` | Yes | `endpoints/publications.py` | `test_publications.py` | 🟢 LIVE |
| 22 | Publications | `GET` | `/api/v1/publications/{id}` | No | `endpoints/publications.py` | `test_publications.py` | 🟢 LIVE |
| 23 | Publications | `PUT` | `/api/v1/publications/{id}` | Yes | `endpoints/publications.py` | `test_publications.py` | 🟢 LIVE |
| 24 | Publications | `DELETE`| `/api/v1/publications/{id}` | Yes | `endpoints/publications.py` | `test_publications.py` | 🟢 LIVE |
| 25 | Research Trends | `GET` | `/api/v1/research-intelligence/trends/publications` | No | `endpoints/research_intelligence.py` | `test_research_intelligence.py` | 🟢 LIVE |
| 26 | Research Trends | `GET` | `/api/v1/research-intelligence/trends/domains` | No | `endpoints/research_intelligence.py` | `test_research_intelligence.py` | 🟢 LIVE |
| 27 | Research Trends | `GET` | `/api/v1/research-intelligence/trends/keywords` | No | `endpoints/research_intelligence.py` | `test_research_intelligence.py` | 🟢 LIVE |
| 28 | Research Trends | `GET` | `/api/v1/research-intelligence/trends/citations` | No | `endpoints/research_intelligence.py` | `test_research_intelligence.py` | 🟢 LIVE |
| 29 | Research Trends | `GET` | `/api/v1/research-intelligence/emerging-topics` | No | `endpoints/research_intelligence.py` | `test_research_intelligence.py` | 🟢 LIVE |
| 30 | Research Trends | `GET` | `/api/v1/research-intelligence/hotspots` | No | `endpoints/research_intelligence.py` | `test_research_intelligence.py` | 🟢 LIVE |
| 31 | Funding | `GET` | `/api/v1/funding` | No | `endpoints/funding.py` | `test_funding.py` | 🟢 LIVE |
| 32 | Funding | `POST` | `/api/v1/funding` | Yes | `endpoints/funding.py` | `test_funding.py` | 🟢 LIVE |
| 33 | Funding | `POST` | `/api/v1/funding/ingest` | Yes | `endpoints/funding.py` | `test_funding_ingest.py` | 🟢 LIVE |
| 34 | Funding | `GET` | `/api/v1/funding/recommendations` | Yes | `endpoints/funding.py` | `test_funding_recommendations.py` | 🟢 LIVE |
| 35 | Funding | `GET` | `/api/v1/funding/{id}` | No | `endpoints/funding.py` | `test_funding.py` | 🟢 LIVE |
| 36 | Funding | `PUT` | `/api/v1/funding/{id}` | Yes | `endpoints/funding.py` | `test_funding.py` | 🟢 LIVE |
| 37 | Funding | `DELETE`| `/api/v1/funding/{id}` | Yes | `endpoints/funding.py` | `test_funding.py` | 🟢 LIVE |
| 38 | Funding | `GET` | `/api/v1/funding/{id}/eligibility` | Yes | `endpoints/funding.py` | `test_funding_eligibility.py` | 🟢 LIVE |
| 39 | Patents | `GET` | `/api/v1/patents` | No | `endpoints/patents.py` | `test_patents.py` | 🟢 LIVE |
| 40 | Patents | `POST` | `/api/v1/patents` | Yes | `endpoints/patents.py` | `test_patents.py` | 🟢 LIVE |
| 41 | Patents | `POST` | `/api/v1/patents/ingest` | Yes | `endpoints/patents.py` | `test_patents.py` | 🟢 LIVE |
| 42 | Patents | `GET` | `/api/v1/patents/my` | Yes | `endpoints/patents.py` | `test_patents.py` | 🟢 LIVE |
| 43 | Patents | `GET` | `/api/v1/patents/{id}` | No | `endpoints/patents.py` | `test_patents.py` | 🟢 LIVE |
| 44 | Patents | `PUT` | `/api/v1/patents/{id}` | Yes | `endpoints/patents.py` | `test_patents.py` | 🟢 LIVE |
| 45 | Patents | `DELETE`| `/api/v1/patents/{id}` | Yes | `endpoints/patents.py` | `test_patents.py` | 🟢 LIVE |
| 46 | Patent Intel | `GET` | `/api/v1/patent-intelligence/landscape` | No | `endpoints/patent_intelligence.py` | `test_patent_intelligence.py` | 🟢 LIVE |
| 47 | Patent Intel | `GET` | `/api/v1/patent-intelligence/trends` | No | `endpoints/patent_intelligence.py` | `test_patent_intelligence.py` | 🟢 LIVE |
| 48 | Patent Intel | `GET` | `/api/v1/patent-intelligence/technology-domains`| No | `endpoints/patent_intelligence.py` | `test_patent_intelligence.py` | 🟢 LIVE |
| 49 | Patent Intel | `GET` | `/api/v1/patent-intelligence/assignees` | No | `endpoints/patent_intelligence.py` | `test_patent_intelligence.py` | 🟢 LIVE |
| 50 | Patent Intel | `GET` | `/api/v1/patent-intelligence/jurisdictions` | No | `endpoints/patent_intelligence.py` | `test_patent_intelligence.py` | 🟢 LIVE |
| 51 | Patent Intel | `GET` | `/api/v1/patent-intelligence/status` | No | `endpoints/patent_intelligence.py` | `test_patent_intelligence.py` | 🟢 LIVE |
| 52 | Patent Intel | `GET` | `/api/v1/patent-intelligence/competitive-landscape`| No | `endpoints/patent_intelligence.py` | `test_patent_intelligence.py` | 🟢 LIVE |
| 53 | Technology Intel| `GET` | `/api/v1/technology-intelligence/summary` | No | `endpoints/technology_intelligence.py` | `test_technology_intelligence.py` | 🟢 LIVE |
| 54 | Technology Intel| `GET` | `/api/v1/technology-intelligence/activity`| No | `endpoints/technology_intelligence.py` | `test_technology_intelligence.py` | 🟢 LIVE |
| 55 | Technology Intel| `GET` | `/api/v1/technology-intelligence/growth` | No | `endpoints/technology_intelligence.py` | `test_technology_intelligence.py` | 🟢 LIVE |
| 56 | Technology Intel| `GET` | `/api/v1/technology-intelligence/coverage` | No | `endpoints/technology_intelligence.py` | `test_technology_intelligence.py` | 🟢 LIVE |
| 57 | Technology Intel| `GET` | `/api/v1/technology-intelligence/whitespace`| No | `endpoints/technology_intelligence.py` | `test_technology_intelligence.py` | 🟢 LIVE |
| 58 | Scoring | `GET` | `/api/v1/innovation-scoring/score` | No | `endpoints/innovation_scoring.py` | `test_innovation_scoring.py` | 🟢 LIVE |
| 59 | Scoring | `GET` | `/api/v1/innovation-scoring/trl` | No | `endpoints/innovation_scoring.py` | `test_innovation_scoring.py` | 🟢 LIVE |
| 60 | Scoring | `GET` | `/api/v1/innovation-scoring/evidence` | No | `endpoints/innovation_scoring.py` | `test_innovation_scoring.py` | 🟢 LIVE |
| 61 | Scoring | `GET` | `/api/v1/innovation-scoring/summary` | No | `endpoints/innovation_scoring.py` | `test_innovation_scoring.py` | 🟢 LIVE |
| 62 | Commercial | `GET` | `/api/v1/commercialization/summary` | No | `endpoints/commercialization.py` | `test_commercialization.py` | 🟢 LIVE |
| 63 | Commercial | `GET` | `/api/v1/commercialization/readiness` | No | `endpoints/commercialization.py` | `test_commercialization.py` | 🟢 LIVE |
| 64 | Commercial | `GET` | `/api/v1/commercialization/recommendations`| No | `endpoints/commercialization.py` | `test_commercialization.py` | 🟢 LIVE |
| 65 | Commercial | `GET` | `/api/v1/commercialization/evidence` | No | `endpoints/commercialization.py` | `test_commercialization.py` | 🟢 LIVE |
| 66 | Command Center | `GET` | `/api/v1/command-center/overview` | Yes | `endpoints/command_center.py` | `test_command_center.py` | 🟢 LIVE |
| 67 | Command Center | `GET` | `/api/v1/command-center/activity-feed` | Yes | `endpoints/command_center.py` | `test_command_center.py` | 🟢 LIVE |
| 68 | Reports | `GET` | `/api/v1/reports/summary` | No | `endpoints/executive_reports.py` | `test_executive_reports.py` | 🟢 LIVE |
| 69 | Reports | `GET` | `/api/v1/reports/dossier` | No | `endpoints/executive_reports.py` | `test_executive_reports.py` | 🟢 LIVE |
| 70 | Reports | `GET` | `/api/v1/reports/export/markdown` | No | `endpoints/executive_reports.py` | `test_executive_reports.py` | 🟢 LIVE |
| 71 | Reports | `GET` | `/api/v1/reports/export/json` | No | `endpoints/executive_reports.py` | `test_executive_reports.py` | 🟢 LIVE |
| 72 | Admin | `GET` | `/api/v1/admin/system/overview` | Yes (Admin) | `endpoints/admin.py` | `test_admin.py` | 🟢 LIVE |
| 73 | Admin | `GET` | `/api/v1/admin/telemetry/pipelines` | Yes (Admin) | `endpoints/admin.py` | `test_admin.py` | 🟢 LIVE |
| 74 | Admin | `GET` | `/api/v1/admin/users` | Yes (Admin) | `endpoints/admin.py` | `test_admin.py` | 🟢 LIVE |
| 75 | Admin | `GET` | `/api/v1/admin/users/{id}` | Yes (Admin) | `endpoints/admin.py` | `test_admin.py` | 🟢 LIVE |
| 76 | Admin | `PUT` | `/api/v1/admin/users/{id}/role` | Yes (Admin) | `endpoints/admin.py` | `test_admin.py` | 🟢 LIVE |
| 77 | Admin | `PUT` | `/api/v1/admin/users/{id}/status` | Yes (Admin) | `endpoints/admin.py` | `test_admin.py` | 🟢 LIVE |
| 78 | Admin | `GET` | `/api/v1/admin/audit-logs` | Yes (Admin) | `endpoints/admin.py` | `test_admin.py` | 🟢 LIVE |
| 79 | OpenAPI | `GET` | `/api/v1/openapi.json` | No | FastAPI core | Fastapi | 🟢 LIVE |
| 80 | Docs | `GET` | `/docs` | No | FastAPI Swagger | Fastapi | 🟢 LIVE |
| 81 | Docs Redirect | `GET` | `/docs/oauth2-redirect` | No | FastAPI Swagger | Fastapi | 🟢 LIVE |
| 82 | ReDoc | `GET` | `/redoc` | No | FastAPI ReDoc | Fastapi | 🟢 LIVE |
