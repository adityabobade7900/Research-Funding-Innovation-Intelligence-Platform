# 07_BACKEND.md — Backend Architecture & Component Map

## 1. Backend Framework & Core Technologies

- **Runtime:** Python 3.10 (Standardized in `backend/venv/`).
- **Web Framework:** FastAPI 0.111.0 on Uvicorn 0.30.1 ASGI server.
- **ORM & Database Driver:** SQLAlchemy 2.0.31 (Async Engine) with `asyncpg` 0.29.0 for PostgreSQL and `aiosqlite` 0.20.0 for unit testing.
- **Migrations:** Alembic 1.13.2 (6 async migration scripts).
- **Data Validation & Settings:** Pydantic 2.7.4 and `pydantic-settings` 2.3.4.
- **Security & Crypto:** `python-jose` 3.3.0 (JWT HS256), `passlib[bcrypt]` 1.7.4, `hashlib` (SHA-256 token hashing).
- **HTTP Client for Harvesters:** HTTPX 0.27.0 (asynchronous request pooling).
- **Test Framework:** Pytest 8.2.2 with `pytest-asyncio` 0.23.7 (150 tests passing in ~41s).

---

## 2. Application Layout (`backend/`)

```
backend/
├── alembic/
│   ├── env.py                             # Async Alembic runtime configuration
│   ├── script.py.mako                     # Migration template
│   └── versions/                          # 6 schema migration scripts
├── alembic.ini                            # Alembic database configuration
├── requirements.txt                       # Locked production dependencies
├── Dockerfile                             # Multi-stage Python 3.10 container
├── scripts/
│   └── create_admin.py                    # Root administrator provisioning CLI
├── tests/                                 # 22 test suites (150 passing tests)
└── app/
    ├── main.py                            # FastAPI application factory & router registration
    ├── core/
    │   ├── config.py                      # Pydantic BaseSettings (.env loader)
    │   ├── database.py                    # AsyncEngine & AsyncSessionLocal factory
    │   ├── security.py                    # Password hashing, JWT creation & token rotation
    │   ├── deps.py                        # Dependency injection: get_db, get_current_user, require_roles
    │   └── exceptions.py                  # Standardized API exception classes
    ├── models/                            # 9 SQLAlchemy ORM model definitions
    ├── schemas/                           # Pydantic v2 request/response validation contracts
    ├── api/
    │   └── v1/
    │       ├── api.py                     # Master API v1 router aggregator
    │       └── endpoints/                 # 14 specialized REST endpoint controllers
    └── services/                          # 14 business logic and analytics services
        └── providers/                     # Modular external API harvester adapters
```

---

## 3. Backend Component Map

### 3.1. Routers & Endpoints (`app/api/v1/endpoints/`)
1. **`auth.py` (8 routes):** User registration, JSON login, OAuth2 form login, token refresh, logout, `/me` profile retrieval, and role test endpoints.
2. **`profile.py` (4 routes):** Multi-facet researcher profile CRUD, research domain taxonomy, user keywords.
3. **`publications.py` (6 routes):** Publication search, CRUD, user bookmarks, and external ingest triggers.
4. **`patents.py` (6 routes):** Patent search, CRUD, user bookmarks, and external ingest triggers.
5. **`funding.py` (8 routes):** Grant search, CRUD, personalized recommendations, and rule-based eligibility checks.
6. **`research_intelligence.py` (6 routes):** Publication velocity trends, domain trends, keyword trends, citation statistics, emerging topics, and hotspot detection.
7. **`patent_intelligence.py` (7 routes):** Patent landscape summary, assignee concentration (HHI), competitor landscape index, jurisdiction breakdown, and trend curves.
8. **`technology_intelligence.py` (5 routes):** Technology activity, IPC coverage density, CAGR growth, summary KPIs, and whitespace discovery.
9. **`innovation_scoring.py` (4 routes):** 5-pillar composite innovation score, NASA TRL 1–9 estimation, evidence dossier, and summary statistics.
10. **`commercialization.py` (4 routes):** 4 readiness dimensions (IP, Market, Regulatory, Team), strategic pathway recommendations (Licensing, Spinout, Joint Dev), and roadmaps.
11. **`command_center.py` (2 routes):** Role-tailored operational KPIs, multi-source activity feed, and 30-day grant deadline alerts.
12. **`executive_reports.py` (4 routes):** Cross-domain executive dossier synthesis, Markdown export, and structured JSON export.
13. **`admin.py` (7 routes):** System health overview, harvester pipeline telemetry, user listings, role modification, and audit logs.
14. **`health.py` (1 route):** Database ping and liveness probe (`/api/v1/health`).

### 3.2. Service Layer (`app/services/`)
- **`profile_service.py`:** Manages user profile isolation and many-to-many facet bindings.
- **`publication_service.py` & `patent_service.py`:** Handles deduplication and search filtering.
- **`funding_service.py`:** Coordinates opportunity queries and deadline sorting.
- **`funding_recommendation_service.py`:** Matches grant opportunities to researcher keywords and domains.
- **`eligibility_matcher.py`:** Evaluates institutional and geographic constraints against user profile.
- **`research_trend_service.py`:** SQL-level publication velocity, YoY growth rates, and composite hotspot scores.
- **`patent_landscape_service.py`:** HHI concentration index, filing velocity, and Composite Competitive Index.
- **`technology_intelligence_service.py`:** Detects unpatented whitespace domains with active research.
- **`innovation_scoring_service.py`:** Computes the exact 5-pillar weighted score.
- **`trl_service.py`:** Executes NASA/DoD standard rule-based TRL 1–9 estimation.
- **`commercialization_service.py`:** Evaluates commercial readiness and recommends strategic paths.
- **`command_center_service.py`:** Aggregates real-time feeds and deadline counters.
- **`executive_report_service.py`:** Synthesizes strategic intelligence dossiers and formats file exports.
- **`admin_service.py`:** Provides system telemetry and role modification security.

### 3.3. Harvesters & External Providers (`app/services/providers/`)
- **`base.py` & `funding_base.py` & `patent_base.py`:** Abstract base classes and dataclasses.
- **`openalex.py`:** Inverted-index abstract reconstruction and OpenAlex API queries.
- **`crossref.py`:** DOI metadata resolution.
- **`semantic_scholar.py`:** Citation count and field of study extraction.
- **`funding_providers.py`:** Grants.gov and NSF award parsers.
- **`patent_providers.py`:** Google Patents resolver and structured mock patent datasets.
- **`mock_provider.py`:** Comprehensive offline fixtures for deterministic testing.

---

## 4. Error Handling & Security Dependencies

- **Global Error Handlers (`app/main.py`):** Automatically intercept `APIException`, `Pydantic ValidationError`, and general exceptions, returning structured JSON errors:
  ```json
  {
    "detail": "Descriptive error message",
    "status_code": 400,
    "error_code": "RESOURCE_NOT_FOUND"
  }
  ```
- **Security Guard (`app/core/deps.py`):**  
  Every protected endpoint injects `current_user: User = Depends(get_current_user)`.  
  Restricted endpoints inject `require_roles([UserRole.ADMINISTRATOR])`, preventing privilege escalation.
