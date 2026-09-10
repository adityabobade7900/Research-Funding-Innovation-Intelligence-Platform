# 29_DECISIONS_LOG.md — Architectural Decision Records (ADRs)

---

### ADR 001: Web Framework Selection (FastAPI & Next.js 14)
- **Date:** 2026-08-24
- **Decision:** Standardize on **Python FastAPI** for the backend API and **Next.js 14 (App Router)** with React 18 & TypeScript for the frontend.
- **Reason:** FastAPI provides native Python async performance, automatic OpenAPI documentation, and native Pydantic v2 data validation. Next.js 14 provides static rendering, typed route structures, and modern React 18 server/client separation.
- **Alternatives Considered:** Django REST Framework (heavier, slower for micro-APIs), Express.js (non-Python, incompatible with Python ML ecosystem), Vite React SPA (lacked server-side rendering and built-in routing).
- **Current Status:** 🟢 **Active & Implemented**

---

### ADR 002: Primary Relational Database (PostgreSQL 16 & SQLAlchemy 2.0 Async)
- **Date:** 2026-08-24
- **Decision:** Use **PostgreSQL 16** via Docker container with SQLAlchemy 2.0 async engine (`asyncpg`) and Alembic migrations.
- **Reason:** Relational integrity is mandatory for multi-tenant user profile isolation, foreign keys across publications, patents, and grants, and ACID audit tracking.
- **Alternatives Considered:** MySQL (less robust JSON handling), MongoDB as primary (insufficient relational integrity for RBAC and relational taxonomy).
- **Current Status:** 🟢 **Active & Implemented** (Head migration: `244ef6c34a82`)

---

### ADR 003: Stateless JWT with Server-Side Refresh Token Rotation
- **Date:** 2026-08-24
- **Decision:** Implement stateless short-lived JWT access tokens (60 min) combined with high-entropy cryptographic refresh tokens stored as SHA-256 hashes in PostgreSQL.
- **Reason:** Balances stateless scalability for API endpoints with the ability to instantly revoke compromised sessions or log out users. Token rotation prevents replay attacks.
- **Alternatives Considered:** Pure stateful session cookies (poor API portability), pure long-lived JWTs (cannot be revoked if compromised).
- **Current Status:** 🟢 **Active & Implemented**

---

### ADR 004: In-Memory SQLite for Automated Test Suites
- **Date:** 2026-08-25
- **Decision:** Use `sqlite+aiosqlite:///:memory:` for backend Pytest suites while running PostgreSQL for runtime development.
- **Reason:** In-memory SQLite enables executing all 150 unit and integration tests in ~41 seconds without external database dependencies or test database pollution.
- **Alternatives Considered:** Mocking all database queries (brittle, misses SQL query errors), dedicated test PostgreSQL container (slower teardown/setup cycles).
- **Current Status:** 🟢 **Active & Implemented**

---

### ADR 005: Deterministic Statistical Algorithms as Baseline Intelligence
- **Date:** 2026-08-25
- **Decision:** Implement the Innovation Scoring formula, Technology Whitespace detection, and Patent Landscape concentration (HHI) using pure Python `math`, `statistics`, and SQL aggregations rather than heavy neural networks.
- **Reason:** Guarantees 100% test reproducibility, eliminates gigabyte-sized PyTorch/CUDA dependencies, meets exact project formula requirements, and runs with sub-50ms API latency.
- **Alternatives Considered:** Immediate deployment of large LLMs / PyTorch transformers (high memory footprint, nondeterministic outputs, slows local development).
- **Current Status:** 🟢 **Active & Implemented** (Vector ML deferred to Phase 3)

---

### ADR 006: Modular Harvester Provider Architecture with Offline Fallbacks
- **Date:** 2026-08-25
- **Decision:** Implement modular abstract base classes (`BaseResearchProvider`, `BaseFundingProvider`) with concrete adapters (OpenAlex, Crossref, Semantic Scholar, Grants.gov, NSF) and built-in offline mock fixtures.
- **Reason:** Prevents platform crashes when external APIs experience downtime, rate limiting, or network unavailability. Guarantees 100% unit test reliability.
- **Alternatives Considered:** Direct ad-hoc HTTP calls inside route controllers (violates separation of concerns, impossible to test offline).
- **Current Status:** 🟢 **Active & Implemented**

---

### ADR 007: Strict Administrator Registration Lockdown
- **Date:** 2026-08-26
- **Decision:** Restrict public registration to `researcher`, `startup_founder`, and `innovation_manager`. Forbid `administrator` registration at both API and UI layers, and introduce a dedicated server-side CLI provisioning script (`backend/scripts/create_admin.py`).
- **Reason:** Eliminates privilege escalation vulnerability where public visitors could register with root administrator privileges.
- **Alternatives Considered:** Simple invitation codes (complex to manage), single hardcoded default admin in migrations (insecure).
- **Current Status:** 🟢 **Active & Implemented**
