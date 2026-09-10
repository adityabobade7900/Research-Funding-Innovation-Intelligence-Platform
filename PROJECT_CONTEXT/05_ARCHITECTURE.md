# 05_ARCHITECTURE.md — System Architecture & Data Flow

## 1. High-Level Architecture Diagram

The **Research Funding & Innovation Intelligence Platform** follows a decoupled, asynchronous, service-oriented architecture:

```mermaid
flowchart TD
    subgraph Client Layer ["Client / Presentation Layer (Browser)"]
        User["User (Researcher / Founder / Manager / Admin)"]
        NextJS["Next.js 14 App Router (React 18 + TypeScript + Tailwind CSS)\nPort 3000"]
    end

    subgraph API Gateway ["API & Security Layer"]
        FastAPI["FastAPI ASGI Server (Python 3.10 + Uvicorn)\nPort 8000"]
        CORS["CORS Middleware"]
        AuthMiddleware["JWT Bearer Authentication & RBAC Guard\n(deps.get_current_user / require_roles)"]
    end

    subgraph Service Layer ["Business Logic & Intelligence Services"]
        AuthServ["Auth & Token Service"]
        ProfileServ["Profile Service"]
        ResearchServ["Research Trend Service"]
        FundingServ["Funding Service & Eligibility Matcher"]
        PatentServ["Patent Landscape Service"]
        TechServ["Technology Intelligence Service"]
        ScoreServ["Innovation Scoring Engine (5 Pillars)"]
        TRLServ["TRL 1-9 Rule Engine"]
        CommServ["Commercialization Service"]
        ReportServ["Executive Report Synthesis"]
        AdminServ["Admin & Telemetry Service"]
    end

    subgraph Data Ingestion Layer ["Harvesters & External Providers"]
        ProviderDispatcher["ResearchProviderService & FundingIngestService"]
        OpenAlex["OpenAlex API"]
        Crossref["Crossref API"]
        SemanticScholar["Semantic Scholar API"]
        GrantsGov["Grants.gov API"]
        NSF["NSF Awards API"]
        MockFallback["Offline Mock Data Fallbacks"]
    end

    subgraph Persistence Layer ["Database & Storage"]
        SQLA["SQLAlchemy 2.0 Async ORM (asyncpg)"]
        Alembic["Alembic Database Migrations (Head: 244ef6c34a82)"]
        Postgres[("PostgreSQL 16 Database\nresearch_intel_db (Port 5432)")]
        SQLiteMem[("SQLite in-memory\n(Automated Pytest Suite)")]
    end

    User --> NextJS
    NextJS -- "REST Requests (Axios / Fetch) with Bearer Token" --> FastAPI
    FastAPI --> CORS --> AuthMiddleware
    AuthMiddleware --> ServiceLayer
    ServiceLayer --> SQLA
    SQLA --> Postgres
    ProviderDispatcher --> OpenAlex
    ProviderDispatcher --> Crossref
    ProviderDispatcher --> SemanticScholar
    ProviderDispatcher --> GrantsGov
    ProviderDispatcher --> NSF
    ProviderDispatcher --> MockFallback
    ProviderDispatcher --> SQLA
```

---

## 2. Request Lifecycle

1. **Client Dispatch:**  
   The user interacts with the Next.js frontend (running on `http://localhost:3000`). Axios or standard `fetch` transmits an HTTP request with an `Authorization: Bearer <jwt_access_token>` header to the backend API (`http://localhost:8000/api/v1/...`).
2. **CORS & Middleware:**  
   FastAPI verifies the request origin against `settings.CORS_ORIGINS`.
3. **Authentication & RBAC Inspection (`app/core/deps.py`):**  
   - `oauth2_scheme` extracts the bearer token.
   - `decode_token()` cryptographically validates signature and expiration against `settings.JWT_SECRET` (`HS256`).
   - The user ID is fetched from PostgreSQL. If deactivated or invalid, an `AuthenticationFailedException` (HTTP 401) is returned.
   - Role dependencies (`require_roles([UserRole.ADMINISTRATOR, ...])`) verify authorization. Unauthorized access yields `PermissionDeniedException` (HTTP 403).
4. **Router Execution (`app/api/v1/endpoints/`):**  
   The endpoint function parses query parameters and validates request bodies against strict Pydantic v2 schemas.
5. **Business Logic Execution (`app/services/`):**  
   The endpoint delegates to asynchronous service classes (`ResearchTrendService`, `FundingService`, `InnovationScoringService`, etc.).
6. **Persistence Access (`app/core/database.py`):**  
   Services execute queries via `AsyncSessionLocal` using SQLAlchemy 2.0 async select/join expressions.
7. **Response Serialization:**  
   Database ORM objects are transformed into Pydantic response models and returned as JSON (or file streams for Markdown export).

---

## 3. Authentication & Session Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as Client (Next.js)
    participant API as FastAPI Auth Endpoint
    participant DB as PostgreSQL (users, refresh_tokens)

    User->>API: POST /api/v1/auth/login {email, password}
    API->>DB: SELECT * FROM users WHERE email = ?
    DB-->>API: User record (hashed_password, role, is_active)
    API->>API: verify_password(plain, hash) via bcrypt
    API->>API: create_access_token(user_id, role) (expires in 60m)
    API->>API: generate_refresh_token_string() (48 random bytes)
    API->>DB: INSERT INTO refresh_tokens (token_hash, expires_at)
    API-->>User: HTTP 200 {access_token, refresh_token, token_type: "bearer"}

    Note over User,API: Subsequent Authenticated Requests
    User->>API: GET /api/v1/profile/me (Header: Bearer access_token)
    API->>API: decode_token(access_token) -> user_id, role
    API->>DB: Fetch user & profile data
    API-->>User: HTTP 200 {profile data}

    Note over User,API: Token Rotation Flow (When Access Token Expires)
    User->>API: POST /api/v1/auth/refresh {refresh_token}
    API->>DB: Lookup refresh_tokens by SHA-256(refresh_token)
    API->>DB: Mark old token as revoked (token rotation)
    API->>API: Generate new access_token & new refresh_token
    API->>DB: Insert new refresh_token
    API-->>User: HTTP 200 {new access_token, new refresh_token}
```

---

## 4. Intelligence & Scoring Engine Flow (Module 7)

```mermaid
flowchart TD
    Trigger["Client requests Innovation Score\nGET /api/v1/innovation-scoring/score?domain=Quantum+Technologies"]
    
    subgraph Evidence Aggregation ["Multi-Signal Evidence Aggregation"]
        P1["Query Publication Metrics\n(Velocity, YoY growth, citation medians)"]
        P2["Query Patent Metrics\n(Filing velocity, assignee HHI, citations)"]
        P3["Execute TRL Heuristic Engine\n(NASA/DoD Standard TRL 1-9)"]
        P4["Calculate Market Potential\n(Domain breadth, CAGR, commercial activity)"]
        P5["Query Funding Relevance\n(Active grant pool, agency competitiveness)"]
    end

    subgraph Mathematical Fusion ["Mathematical Formula Engine"]
        W1["Novelty Pillar = min(100, (vol*0.35 + growth*0.35 + cit*0.30))"]
        W2["Patent Pillar = min(100, (vol*0.40 + vel*0.30 + cit*0.20 + hhi*0.10))"]
        W3["Maturity Pillar = (TRL / 9.0) * 100"]
        W4["Market Pillar = min(100, (cagr*0.50 + breadth*0.50))"]
        W5["Funding Pillar = min(100, (grants*0.50 + amount_log*0.50))"]
        Formula["Formula:\nScore = (0.30 * Novelty) + (0.20 * Patent) + (0.15 * TRL) + (0.20 * Market) + (0.15 * Funding)"]
    end

    Response["Return InnovationScoreResponse JSON\n(Composite Score, 5 Pillar Breakdowns, Confidence Score, Key Drivers)"]

    Trigger --> P1 & P2 & P3 & P4 & P5
    P1 --> W1
    P2 --> W2
    P3 --> W3
    P4 --> W4
    P5 --> W5
    W1 & W2 & W3 & W4 & W5 --> Formula
    Formula --> Response
```

---

## 5. External Harvester Flow & Error Handling

To ensure continuous operation without external dependencies:
1. **Timeout & Retries:** Every provider request uses a strict timeout (`settings.PROVIDER_TIMEOUT_SECONDS = 8.0s`) and up to 2 retries.
2. **Graceful Fallbacks:** If an external API is offline, rate-limited, or unconfigured, the provider catches the exception and returns curated fallback datasets without failing the client request.
3. **Data Normalization:** All providers normalize incoming external payloads into canonical Pydantic dataclasses (`NormalizedPublication`, `NormalizedFundingOpportunity`, `NormalizedPatent`).
4. **Deduplication:** DOIs, patent numbers, and grant opportunity IDs are checked against PostgreSQL before creating new records.

---

## 6. Integration Boundaries & File Organization

- **Frontend Application (`frontend/`):** Completely decoupled from backend internals. Interacts strictly via REST JSON over HTTP.
- **Backend Application (`backend/`):** Pure Python async application structured around Clean Architecture layers:
  - `app/api/v1/endpoints/`: Routing and HTTP transport.
  - `app/schemas/`: Data contracts and Pydantic validation.
  - `app/services/`: Reusable business logic.
  - `app/models/`: SQLAlchemy ORM entity definitions.
  - `app/core/`: Configuration, database engines, security, and dependencies.
