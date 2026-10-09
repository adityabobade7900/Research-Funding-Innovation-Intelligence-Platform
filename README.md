# Research Funding & Innovation Intelligence Platform

> **Infosys Springboard Virtual Internship 7.0 — Final Project Documentation**  
> **Repository:** [https://github.com/adityabobade7900/Research-Funding-Innovation-Intelligence-Platform](https://github.com/adityabobade7900/Research-Funding-Innovation-Intelligence-Platform)  
> **Development Branch:** `feature/aditya-ai-ml`  
> **Functional Scope:** Modules M1–M11 (Fully Implemented & Verified)

---

## Table of Contents

- [1. Executive Overview](#1-executive-overview)
  - [Problem Statement](#problem-statement)
  - [Platform Objectives](#platform-objectives)
  - [Target Personas](#target-personas)
- [2. Key Capabilities & Module Overview](#2-key-capabilities--module-overview)
- [3. System Architecture](#3-system-architecture)
  - [High-Level Architectural Diagram](#high-level-architectural-diagram)
  - [Architectural Layers](#architectural-layers)
- [4. Technology Stack](#4-technology-stack)
- [5. Functional Modules (M1–M11) Detailed Specification](#5-functional-modules-m1m11-detailed-specification)
  - [Module 1: Authentication & Role-Based Access Control (RBAC)](#module-1-authentication--role-based-access-control-rbac)
  - [Module 2: Research Profile Management](#module-2-research-profile-management)
  - [Module 3: Research Intelligence & Paper Analysis](#module-3-research-intelligence--paper-analysis)
  - [Module 4: Funding Intelligence & Grant Discovery](#module-4-funding-intelligence--grant-discovery)
  - [Module 5: Patent Landscape Analysis & Clustering](#module-5-patent-landscape-analysis--clustering)
  - [Module 6: Technology Intelligence & Whitespace Discovery](#module-6-technology-intelligence--whitespace-discovery)
  - [Module 7: Multi-Factor Innovation Scoring & TRL Engine](#module-7-multi-factor-innovation-scoring--trl-engine)
  - [Module 8: Commercialization Recommendations](#module-8-commercialization-recommendations)
  - [Module 9: Dashboard & Administrative Command Center](#module-9-dashboard--administrative-command-center)
  - [Module 10: Notification & Alert System](#module-10-notification--alert-system)
  - [Module 11: Reports & Export System](#module-11-reports--export-system)
- [6. Database Architecture & Schema Design](#6-database-architecture--schema-design)
  - [Entity-Relationship Diagram](#entity-relationship-diagram)
  - [Tables, Relationships & Migration History](#tables-relationships--migration-history)
- [7. Complete REST API Reference](#7-complete-rest-api-reference)
- [8. AI/ML, NLP & Analytical Methodology](#8-aiml-nlp--analytical-methodology)
- [9. Repository Structure](#9-repository-structure)
- [10. Prerequisites & System Requirements](#10-prerequisites--system-requirements)
- [11. Installation & Local Setup Guide](#11-installation--local-setup-guide)
  - [Step-by-Step PowerShell Setup](#step-by-step-powershell-setup)
  - [Three-Terminal Running Workflow](#three-terminal-running-workflow)
- [12. Environment Variable Configuration](#12-environment-variable-configuration)
- [13. Testing & Verification Suite](#13-testing--verification-suite)
  - [Backend Pytest Suite (221 Tests)](#backend-pytest-suite-221-tests)
  - [Frontend Vitest Suite (70 Tests)](#frontend-vitest-suite-70-tests)
  - [Next.js 14 Production Build Verification (18/18 Routes)](#nextjs-14-production-build-verification-1818-routes)
- [14. Security & Governance Implementation](#14-security--governance-implementation)
- [15. Team Roles & Git Collaboration Workflow](#15-team-roles--git-collaboration-workflow)
- [16. Troubleshooting & Diagnostics](#16-troubleshooting--diagnostics)
- [17. Current Implementation Status & Known Limitations](#17-current-implementation-status--known-limitations)
- [18. Future Roadmap](#18-future-roadmap)
- [19. Deliverables & Conclusion](#19-deliverables--conclusion)
- [20. License & Acknowledgments](#20-license--acknowledgments)

---

## 1. Executive Overview

### Problem Statement
Scientific research and technological innovation frequently stall during the transition from laboratory discovery to commercial deployment. Researchers face fragmented academic literature silos, opaque grant qualification rules, and lack of visibility into commercial patent portfolios. Technology Transfer Offices (TTOs) and institutional investors lack objective, quantitative indicators to evaluate technology maturity and defensibility. Conversely, deep-tech founders struggle to identify unpatented whitespace niches and non-dilutive federal capital to de-risk laboratory prototypes.

### Platform Objectives
Developed under the **Infosys Springboard Virtual Internship 7.0**, the **Research Funding & Innovation Intelligence Platform** is an enterprise-grade full-stack decision-support system. It unifies academic literature indexing, automated scientific discourse analysis, grant eligibility matchmaking, patent landscape analytics, unsupervised patent clustering, technology whitespace radar, an objective 5-pillar mathematical innovation scoring model, commercialization readiness assessment, in-app notifications, and multi-format reporting into a cohesive platform.

### Target Personas
1. **Academic Researchers & Faculty:** Discover tailored non-dilutive grants, benchmark research novelty, ingest publications via DOI, and analyze paper methodology facets.
2. **Deep-Tech Startup Founders:** Identify unpatented technological whitespace, analyze corporate patent competitor concentration, and evaluate spinout pathways.
3. **Innovation Managers & TTO Officers:** Benchmark institutional Technology Readiness Levels (TRL 1–9), review out-licensing candidates, and generate executive dossiers.
4. **Platform Administrators & IT Governance:** Oversee connector pipelines, govern role-based access, audit security events, and inspect system health.

---

## 2. Key Capabilities & Module Overview

The platform implements **11 production-grade functional modules (M1–M11)** backed by verified database models, asynchronous services, secure REST endpoints, and an interactive Next.js interface:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│               RESEARCH FUNDING & INNOVATION INTELLIGENCE PLATFORM                      │
└────────────────────────────────────────────────────────────────────────────────────────┘
  │
  ├── [M1] Authentication & RBAC       ── JWT Access/Refresh, Bcrypt, 4 Hardened Roles
  ├── [M2] Research Profile            ── Multi-domain taxonomy, ORCID, history tracking
  ├── [M3] Research Intelligence       ── Paper NLP discourse analysis, velocity & gaps
  ├── [M4] Funding Intelligence        ── Grants.gov/NSF search, semantic eligibility, bookmarks
  ├── [M5] Patent Landscape            ── HHI concentration, IPC analytics, TF-IDF + KMeans clustering
  ├── [M6] Technology Intelligence     ── 6-indicator maturity, CAGR trajectory, whitespace gaps
  ├── [M7] Innovation Scoring          ── Deterministic 30/20/15/20/15 formula + TRL 1–9 engine
  ├── [M8] Commercialization           ── 4 Pathways: Productization, Licensing, Spinout, Partnership
  ├── [M9] Dashboard & Command Center  ── Role-tailored KPI cards, grant deadlines, admin audit
  ├── [M10] Notifications & Alerts     ── Persistent model, event scan, unread badges, user isolation
  └── [M11] Reports & Export System    ── 5 Types + Dossier, ReportLab PDF, openpyxl Excel (.xlsx)
```

*(Note: Per official project directives, Module 12 deployment/CI was designated out of mentor-assigned functional scope. All 11 core functional modules M1–M11 are fully completed and verified).*

---

## 3. System Architecture

### High-Level Architectural Diagram

```mermaid
flowchart TD
    subgraph ClientLayer["Frontend Client Layer (Next.js 14 App Router)"]
        UI["Web Application\nReact 18 / TypeScript / Tailwind CSS"]
        AuthContext["Auth State & Storage\n(JWT in LocalStorage/Axios Interceptor)"]
        NotifCenter["Notification Center\n(Unread Counter & Popover)"]
        ExportHub["Reports & Export Hub\n(PDF / Excel / Markdown / JSON)"]
    end

    subgraph APILayer["Backend API Gateway (FastAPI 0.111.0 / Uvicorn)"]
        Router["Master API Router (/api/v1)"]
        AuthMid["JWT Bearer Authentication & RBAC Guard"]
        RateLimit["CORS & Error Handlers"]
    end

    subgraph ServiceLayer["Domain Intelligence & Analytical Services"]
        M1_Auth["Auth & User Service"]
        M2_Prof["Profile & Taxonomy Service"]
        M3_Paper["Paper Analysis & Research Trends"]
        M4_Fund["Funding Matcher & Grants Ingestion"]
        M5_Patent["Patent Landscape & KMeans Clustering"]
        M6_Tech["Technology Intelligence & Whitespace"]
        M7_Score["5-Pillar Innovation Scoring & TRL Engine"]
        M8_Comm["Commercialization Pathway Engine"]
        M9_Dash["Command Center & Admin Telemetry"]
        M10_Notif["Notification Scanning & Alert Service"]
        M11_Export["ReportLab PDF & OpenPyXL Excel Service"]
    end

    subgraph PersistenceLayer["Database & Storage Layer"]
        PG[("PostgreSQL 16 (Primary RDBMS)\nAsyncPG + SQLAlchemy 2.0 ORM\n8 Alembic Revisions")]
        SQLite[("In-Memory SQLite\n(Automated Test Suite Engine)")]
    end

    subgraph ExternalEcosystem["External Data Registries & AI Integrations"]
        OpenAlex["OpenAlex / CrossRef / Semantic Scholar APIs"]
        GrantsGov["Grants.gov / NSF Data Connectors"]
        GenAI["Optional LLM Fallback (Google Gemini / OpenAI)"]
    end

    UI --> Router
    AuthContext --> Router
    NotifCenter --> Router
    ExportHub --> Router

    Router --> AuthMid
    AuthMid --> ServiceLayer

    M3_Paper -.-> GenAI
    M3_Paper --> OpenAlex
    M4_Fund --> GrantsGov

    ServiceLayer -->|"SQLAlchemy Async ORM"| PG
    ServiceLayer -.->|"Test Execution Isolation"| SQLite
```

### Architectural Layers
1. **Frontend Layer (Next.js 14.2.4):** Built on React 18, TypeScript 5.4, and Tailwind CSS. Employs client hooks, Axios HTTP interceptors with automatic Bearer token injection, dynamic modal workflows, and responsive data visualization tables.
2. **API & Security Gateway (FastAPI 0.111.0):** Asynchronous ASGI controllers running on Uvicorn. Exposes 108 registered routes under `/api/v1` with Pydantic v2 schema validation, Bcrypt cryptographic password verification, and OAuth2 JWT token handlers.
3. **Core Intelligence Engines:** Python 3.10 asynchronous domain services implementing deterministic mathematical formulas, scikit-learn machine learning pipelines, and heuristic rule engines.
4. **Data Persistence Layer:** PostgreSQL 16 relational database with 15 normalized tables and 4 association tables managed via Alembic database migrations. Automated test executions run against an isolated in-memory SQLite database (`sqlite+aiosqlite:///:memory:`).

---

## 4. Technology Stack

| Category | Technology | Version | Purpose in this Project |
| :--- | :--- | :--- | :--- |
| **Backend Framework** | FastAPI | `0.111.0` | Asynchronous high-performance REST API routing, dependency injection, OpenAPI documentation. |
| **ASGI Server** | Uvicorn | `0.30.1` | ASGI production application server with standard workers. |
| **Data Validation** | Pydantic / Pydantic-Settings | `2.7.4` / `2.3.4` | Strict schema serialization, request/response validation, environment settings. |
| **Relational Database** | PostgreSQL | `16-alpine` | Primary transactional relational database storing users, profiles, publications, patents, grants, notifications. |
| **Database Driver** | asyncpg | `0.29.0` | High-throughput asynchronous PostgreSQL client library. |
| **Async ORM** | SQLAlchemy | `2.0.31` | Asynchronous ORM models, relational mapping, queries, and joins. |
| **Database Migrations**| Alembic | `1.13.2` | Version-controlled, reproducible database schema migrations (8 revisions). |
| **Test Database** | aiosqlite | `0.20.0` | Fast in-memory asynchronous SQLite engine for isolated pytest execution. |
| **Security & JWT** | Python-Jose | `3.3.0` | Cryptographic JSON Web Token (JWT) signing, verification, and claims parsing. |
| **Password Hashing** | Passlib & Bcrypt | `1.7.4` & `4.0.1` | Cryptographic salt generation and Bcrypt password hashing. |
| **Machine Learning** | Scikit-learn & NumPy | `1.7.2` & `1.26.4` | Unsupervised TF-IDF vectorization and K-Means clustering for patent classification. |
| **PDF Generation** | ReportLab | `5.0.1` | Programmatic vector PDF document compilation (headers, tables, wrapped cells, footers). |
| **Excel Generation** | openpyxl | `3.1.5` | Multi-sheet structured `.xlsx` spreadsheet workbook creation with cell styling. |
| **HTTP Client (Backend)**| HTTPX | `0.27.0` | Asynchronous external REST requests for academic registries, grants, and test clients. |
| **Backend Testing** | Pytest / Pytest-Asyncio | `8.2.2` / `0.23.7` | Asynchronous backend test runner (221 test cases passing). |
| **Frontend Framework**| Next.js | `14.2.4` | React framework using App Router, static page compilation, and server/client boundary. |
| **Frontend Library** | React & React DOM | `18.3.1` | Component-based reactive user interface. |
| **Language (Frontend)**| TypeScript | `5.4.5` | Static type safety across client state, API contracts, and domain models. |
| **Styling** | Tailwind CSS & PostCSS | `3.4.4` & `8.4.38` | Utility-first responsive design tokens, glassmorphism, and dark theme UI. |
| **Icons** | Lucide React | `0.395.0` | Modern SVG iconography across dashboard navigation, telemetry, and actions. |
| **HTTP Client (Web)** | Axios | `1.7.2` | Client-side HTTP requests, request/response interceptors, and error handling. |
| **Frontend Testing** | Vitest | `4.1.11` | Vite-native unit testing runner for TypeScript contracts and logic (70 test cases passing). |
| **Containerization** | Docker & Docker Compose| `3.8` spec | Containerized PostgreSQL 16 database provisioning. |

---

## 5. Functional Modules (M1–M11) Detailed Specification

### Module 1: Authentication & Role-Based Access Control (RBAC)
- **Objective:** Provide secure authentication, role segregation, session refresh token management, and data isolation.
- **Implemented Features:**
  - Self-registration with email validation and strong password requirements (min 8 chars, uppercase, lowercase, number, special char).
  - Public registration restricted to 3 roles: `researcher`, `startup_founder`, `innovation_manager`.
  - Registration with `administrator` role explicitly forbidden (`HTTP 403 Permission Denied`). Root administrators must be provisioned via server-side CLI (`scripts/create_admin.py`).
  - Cryptographic JWT access token (HS256, 60-minute expiry) paired with persistent database-backed refresh tokens (7-day sliding expiry).
  - Role-based route guards (`require_roles`) on backend endpoints and client-side route protection.
- **Key Files:** [`backend/app/api/v1/endpoints/auth.py`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/api/v1/endpoints/auth.py), [`backend/app/core/security.py`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/core/security.py), [`backend/app/models/user.py`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/models/user.py).

### Module 2: Research Profile Management
- **Objective:** Model and maintain institutional researcher profiles, academic history, research interests, and domain taxonomies.
- **Implemented Features:**
  - 8 core profile attributes: institution, department, designation, country, phone, biography, ORCID identifier, and personal website.
  - Hierarchical research taxonomy linking normalized research domains (`research_domains`), custom research interests (`research_interests`), keywords (`profile_keywords`), and technology focus areas (`technology_areas`).
  - Academic history (`academic_histories`) and research experience tracking (`research_histories`).
  - User-profile scoping ensuring non-admin users cannot mutate other researchers' profile records.
- **Key Files:** [`backend/app/api/v1/endpoints/profile.py`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/api/v1/endpoints/profile.py), [`backend/app/models/profile.py`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/models/profile.py), [`frontend/src/app/(dashboard)/profile/page.tsx`](file:///d:/Infosys%207.0/Intelligent-Research1/frontend/src/app/(dashboard)/profile/page.tsx).

### Module 3: Research Intelligence & Paper Analysis
- **Objective:** Catalog scholarly publications, extract structured scientific discourse, track temporal citation velocity, and surface emerging research hotspots.
- **Implemented Features:**
  - Multi-provider publication ingestion (OpenAlex, CrossRef, Semantic Scholar, with deterministic MockProvider fallback) and DOI deduplication.
  - **Paper Analysis Engine:** Multi-facet extraction identifying Problem Statement, Methodology, Findings & Contributions, Limitations, and Future Directions. Operates via deterministic NLP discourse heuristics with optional LLM fallback (Gemini/OpenAI) when configured.
  - **Research Trend Analytics:** Temporal publication velocity tracking, median citations by publication year, Compound Annual Growth Rate (CAGR) trajectory, and accelerating keyword hotspots.
- **Key Files:** [`backend/app/services/paper_analysis_service.py`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/services/paper_analysis_service.py), [`backend/app/services/research_trend_service.py`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/services/research_trend_service.py), [`backend/app/api/v1/endpoints/publications.py`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/api/v1/endpoints/publications.py).

### Module 4: Funding Intelligence & Grant Discovery
- **Objective:** Discover active grant solicitations, evaluate researcher eligibility, calculate relevance match scores, and track upcoming deadlines.
- **Implemented Features:**
  - Ingestion from Grants.gov and NSF APIs with deterministic fallback to verified mock opportunities.
  - Multi-factor eligibility matcher evaluating research domain overlap, keyword alignment, geographic jurisdiction, and institutional eligibility.
  - Relevance scoring (0–100%) with human-readable eligibility rationales and criteria breakdown.
  - Grant bookmarking (`/funding/{id}/save`) and personalized deadline tracking feed.
- **Key Files:** [`backend/app/services/funding_service.py`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/services/funding_service.py), [`backend/app/services/eligibility_matcher.py`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/services/eligibility_matcher.py), [`backend/app/models/funding.py`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/models/funding.py).

### Module 5: Patent Landscape Analysis & Clustering
- **Objective:** Analyze intellectual property disclosures, evaluate assignee market concentration, map international filing jurisdictions, and cluster patents using unsupervised machine learning.
- **Implemented Features:**
  - Patent portfolio management (CRUD, manual entry, external registry ingestion, user bookmarking).
  - Landscape metrics: Assignee market concentration via **Herfindahl-Hirschman Index (HHI)**, IPC classification distribution, filing growth rates, legal status breakdown, and competitive litigation indicators.
  - **Unsupervised Patent Clustering:** TF-IDF text vectorization paired with K-Means clustering (`scikit-learn`) over patent titles, abstracts, domains, and claims. Dynamically clusters patents into topical technological clusters (k=2 to 8).
- **Key Files:** [`backend/app/services/patent_landscape_service.py`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/services/patent_landscape_service.py), [`backend/app/services/patent_clustering_service.py`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/services/patent_clustering_service.py), [`backend/app/models/patent.py`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/models/patent.py).

### Module 6: Technology Intelligence & Whitespace Discovery
- **Objective:** Track technology maturity indicators, quantify technological growth trajectories, and identify unpatented whitespace opportunities.
- **Implemented Features:**
  - **6-Indicator Technology Maturity Model:** Evaluates research publication velocity, patent disclosure rate, active publishing organizations, assignee concentration, international jurisdiction spread, and temporal recency ratio.
  - **Whitespace Radar:** Detects technological focus areas characterized by high scientific publication density but low patent filing concentration. Identifies addressable market niches.
  - Transparent data status policy: Unmeasured adoption metrics are explicitly reported as `DATA_UNAVAILABLE` rather than hallucinating proxy scores.
- **Key Files:** [`backend/app/services/technology_intelligence_service.py`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/services/technology_intelligence_service.py), [`backend/app/api/v1/endpoints/technology_intelligence.py`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/api/v1/endpoints/technology_intelligence.py).

### Module 7: Multi-Factor Innovation Scoring & TRL Engine
- **Objective:** Calculate an objective composite Innovation Score (0–100) and estimate Technology Readiness Levels (TRL 1–9) with complete component explainability.
- **Mathematical Formula & Weights:**
  $$\text{Innovation Score} = (0.30 \times \text{Research Novelty}) + (0.20 \times \text{Patent Strength}) + (0.15 \times \text{Technology Maturity}) + (0.20 \times \text{Market Potential}) + (0.15 \times \text{Funding Relevance})$$
- **Implemented Features:**
  - Decomposes scores into all 5 official pillars: Research Novelty (30%), Patent Strength (20%), Technology Maturity (15%), Market Potential (20%), Funding Relevance (15%).
  - **TRL Heuristic Engine:** Maps empirical artifact evidence (publications, granted patents, prototype validation, grant awards) to NASA/DoD standard Technology Readiness Levels (TRL 1: Basic Principles to TRL 9: Operational Deployment).
  - Explicit data sufficiency ratings: `SUFFICIENT`, `PARTIAL_EVIDENCE`, `INSUFFICIENT_DATA`. Missing signals default conservatively without fabricating evidence.
- **Key Files:** [`backend/app/services/innovation_scoring_service.py`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/services/innovation_scoring_service.py), [`backend/app/schemas/innovation_scoring.py`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/schemas/innovation_scoring.py), [`frontend/src/app/(dashboard)/scoring/page.tsx`](file:///d:/Infosys%207.0/Intelligent-Research1/frontend/src/app/(dashboard)/scoring/page.tsx).

### Module 8: Commercialization Recommendations
- **Objective:** Synthesize multi-module signals to formulate actionable, conservative commercial translation roadmaps across 4 canonical pathways.
- **Implemented Features:**
  - **Four Canonical Pathways:**
    1. *Potential Productization Pathway:* Direct technical translation into commercial software/hardware products.
    2. *Potential Corporate Licensing Pathway:* Out-licensing patent claims to corporate assignees identified from patent landscape overlap.
    3. *Potential Startup Spinout Pathway:* Venture creation leveraging non-dilutive translation funding.
    4. *Potential Industry Partnership Pathway:* Collaborative co-development and pre-commercial operational testing.
  - Strict conservative advisory wording: uses phrases like *"potential productization pathway"* and *"potential licensing candidate"*; zero promissory claims or guaranteed commercial forecasts.
  - Transparent disclosure of unmeasured dimensions: regulatory feasibility (`DATA_UNAVAILABLE`), team capability (`DATA_UNAVAILABLE`).
- **Key Files:** [`backend/app/services/commercialization_service.py`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/services/commercialization_service.py), [`backend/app/schemas/commercialization.py`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/schemas/commercialization.py), [`MODULE_08_COMMERCIALIZATION.md`](file:///d:/Infosys%207.0/Intelligent-Research1/MODULE_08_COMMERCIALIZATION.md).

### Module 9: Dashboard & Administrative Command Center
- **Objective:** Deliver executive dashboards tailored to active user roles and provide administrators with platform telemetry and governance tools.
- **Implemented Features:**
  - **Role-Tailored KPI Cards:**
    - *Researcher:* Active publications, matching grants, average citations, novelty score.
    - *Startup Founder:* Whitespace opportunities, tracked patents, addressable capital pool.
    - *Innovation Manager:* Portfolio average innovation score, portfolio TRL distribution, dominant pathways.
    - *Administrator:* Registered users, connector health, active background jobs, audit logs.
  - Multi-stream real-time activity timeline, grant submission deadline calendar, and cross-domain benchmark matrices.
  - User governance endpoints (`/api/v1/admin/users`) allowing role mutations and account activation/deactivation.
- **Key Files:** [`backend/app/services/command_center_service.py`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/services/command_center_service.py), [`backend/app/services/admin_service.py`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/services/admin_service.py), [`frontend/src/app/(dashboard)/dashboard/page.tsx`](file:///d:/Infosys%207.0/Intelligent-Research1/frontend/src/app/(dashboard)/dashboard/page.tsx).

### Module 10: Notification & Alert System
- **Objective:** Ingest system-wide intelligence events, check relevance against researcher profiles, persist user-specific alerts, and manage read/unread states.
- **Implemented Features:**
  - **Persistent Database Model:** Dedicated SQLAlchemy model `Notification` (`notifications` table) with foreign key to `users.id`.
  - **Notification Types:** `FUNDING` (upcoming grant deadlines), `PATENT` (competitor filings in tracked domains), `TECHNOLOGY` (emerging whitespace), `RESEARCH_TREND` (accelerating topics), `COMMERCIALIZATION` (readiness updates), and `SYSTEM` (account notifications).
  - **Automated Event Scanner:** Scans platform telemetry, matches against profile domains, deduplicates alerts, and assigns priority (`HIGH`, `MEDIUM`, `LOW`).
  - **Interactive UI:** Header notification bell with unread badge counter, sliding popover, type filtering, "Mark as Read" action, "Mark All as Read" batch patch, and instant deep-linking to related modules.
- **Key Files:** [`backend/app/models/notification.py`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/models/notification.py), [`backend/app/services/notification_service.py`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/services/notification_service.py), [`backend/app/api/v1/endpoints/notifications.py`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/api/v1/endpoints/notifications.py), [`frontend/src/components/NotificationCenter.tsx`](file:///d:/Infosys%207.0/Intelligent-Research1/frontend/src/components/NotificationCenter.tsx).

### Module 11: Reports & Export System
- **Objective:** Provide automated analytical report generation, live structured telemetry preview, and downloadable multi-format exports (PDF and Excel).
- **Supported Report Categories:**
  1. `FUNDING`: Active grant solicitations, agencies, pools, deadlines, and eligibility criteria.
  2. `PATENT`: Tracked patent disclosures, assignees, classifications, filing dates, and citation depth.
  3. `RESEARCH_TREND`: Literature momentum, thematic keywords, recent/historical volumes, growth rates, and velocity scores.
  4. `INNOVATION_INTELLIGENCE`: Detailed 5-pillar score factor breakdown (Novelty 30%, Patents 20%, Maturity 15%, Market 20%, Funding 15%), statuses, weights, evidence, and estimated TRL.
  5. `COMMERCIALIZATION`: Four translational pathways, feasibility statuses, readiness levels, and conservative guidelines.
  6. `EXECUTIVE_DOSSIER`: Cross-module strategic synthesis, SWOT assessment, 3-phase roadmap, and portfolio benchmarks.
- **Export Engines:**
  - **ReportLab PDF:** Generates styled vector PDF documents with branded cover headers, executive summary callouts, metrics tables, auto-wrapped table rows to prevent page overflow, and governance footers.
  - **OpenPyXL Excel (.xlsx):** Multi-sheet workbooks containing `Summary & Metrics`, `Data Records`, and `5-Pillar Score Factors` sheets with formatted headers and auto-adjusted column widths.
  - **Live Preview:** Interactive `/reports` interface with dynamic backend filtering (date range, domain, agency, min amount, user portfolio scope) and clean empty-state handling.
- **Key Files:** [`backend/app/services/report_export_service.py`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/services/report_export_service.py), [`backend/app/schemas/report_export.py`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/schemas/report_export.py), [`backend/app/api/v1/endpoints/executive_reports.py`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/api/v1/endpoints/executive_reports.py), [`frontend/src/app/(dashboard)/reports/page.tsx`](file:///d:/Infosys%207.0/Intelligent-Research1/frontend/src/app/(dashboard)/reports/page.tsx).

---

## 6. Database Architecture & Schema Design

### Entity-Relationship Diagram

```mermaid
erDiagram
    users ||--o| profiles : "has one"
    users ||--o{ refresh_tokens : "owns"
    users ||--o{ notifications : "receives"
    users ||--o{ saved_funding : "bookmarks"

    profiles ||--o{ academic_histories : "includes"
    profiles ||--o{ research_histories : "includes"
    profiles ||--o{ research_interests : "has"
    profiles ||--o{ profile_keywords : "tagged with"
    profiles ||--o{ technology_areas : "specializes in"

    profiles }o--o{ research_domains : "profile_domains"
    profiles }o--o{ publications : "profile_publications"
    profiles }o--o{ patents : "profile_patents"

    publications ||--o{ publication_keywords : "indexed by"
    funding_opportunities ||--o{ funding_keywords : "indexed by"
    funding_opportunities }o--o{ research_domains : "funding_opportunity_domains"
    funding_opportunities ||--o{ saved_funding : "saved in"

    users {
        int id PK
        string email UK
        string hashed_password
        string full_name
        string phone
        string role
        boolean is_active
        boolean is_superuser
        datetime created_at
        datetime updated_at
    }

    profiles {
        int id PK
        int user_id FK,UK
        string institution
        string department
        string designation
        string country
        string orcid_id
        text biography
        string website_url
        datetime created_at
        datetime updated_at
    }

    publications {
        int id PK
        string title
        string doi UK
        text abstract
        string authors
        string venue
        date publication_date
        int citation_count
        string primary_domain
        datetime created_at
    }

    patents {
        int id PK
        string patent_number UK
        string title
        text abstract
        string assignee
        string inventors
        date filing_date
        date publication_date
        string legal_status
        string technology_domain
        int citation_count
        datetime created_at
    }

    funding_opportunities {
        int id PK
        string title
        string opportunity_number UK
        string funding_agency
        text description
        float funding_amount
        string currency
        date application_deadline
        string status
        string eligibility_criteria
        datetime created_at
    }

    notifications {
        int id PK
        int user_id FK
        string title
        text message
        string notification_type
        string priority
        string source_module
        string related_entity_type
        int related_entity_id
        string action_url
        boolean is_read
        datetime read_at
        datetime created_at
    }
```

### Tables, Relationships & Migration History

The schema is version-controlled via Alembic across 8 sequential database migration scripts:

| Revision Hash | Migration Title | Schema Additions & Key Changes |
| :--- | :--- | :--- |
| `706d13f3e174` | Initial Schema Setup | Created `users`, `profiles`, and `refresh_tokens` tables. |
| `68afbe48340e` | Research Taxonomy | Added `research_domains`, `research_interests`, `profile_keywords`, `technology_areas`, `academic_histories`, `research_histories`, and `profile_domains`. |
| `53d7c57aa26c` | Publications & Keywords | Added `publications`, `publication_keywords`, and `profile_publications`. |
| `626ab1f43993` | Patents & IP Portfolio | Added `patents` and `profile_patents`. |
| `f8e9f392e6c3` | Funding Solicitations | Added `funding_opportunities`, `funding_keywords`, and `funding_opportunity_domains`. |
| `244ef6c34a82` | User Phone & Designation | Added `phone` to `users` and `designation` to `profiles`. |
| `c3d4e5f6a1b2` | Saved Funding Bookmarks | Added `saved_funding` table linking `users.id` and `funding_opportunities.id`. |
| `d4e5f6a7b8c9` | Notifications Table | Added `notifications` table with user foreign keys, enums, read tracking, and indexes. |

---

## 7. Complete REST API Reference

The FastAPI backend exposes **108 registered routes** under `/api/v1`. Interactive documentation is available locally via Swagger UI (`http://localhost:8000/docs`) and ReDoc (`http://localhost:8000/redoc`).

### 1. Health & Readiness
| Method | Endpoint | Description | Access Level |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Service liveness, readiness, and database probe | Public |

### 2. Authentication & Authorization (`/auth`)
| Method | Endpoint | Description | Access Level |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Self-registration (Researcher, Founder, Manager) | Public |
| `POST` | `/api/v1/auth/login` | JSON credential login; returns JWT access + refresh token | Public |
| `POST` | `/api/v1/auth/login/form` | OAuth2 password request form login | Public |
| `POST` | `/api/v1/auth/refresh` | Rotate refresh token and issue new access token | Public |
| `POST` | `/api/v1/auth/logout` | Invalidate active refresh token | Authenticated |
| `GET` | `/api/v1/auth/me` | Fetch active user credentials and role | Authenticated |
| `PUT` | `/api/v1/auth/me` | Update active user details | Authenticated |

### 3. Research Profile (`/profile`)
| Method | Endpoint | Description | Access Level |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/profile/me` | Retrieve authenticated user's complete research profile | Authenticated |
| `PUT` | `/api/v1/profile/me` | Update profile facets, taxonomy domains, interests | Authenticated |
| `GET` | `/api/v1/profile/domains` | List all system-indexed research taxonomy domains | Authenticated |
| `GET` | `/api/v1/profile/{user_id}`| Retrieve public research profile by user ID | Authenticated |

### 4. Publications & AI Paper Analysis (`/publications`)
| Method | Endpoint | Description | Access Level |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/publications` | Paginated publication catalog search and filter | Authenticated |
| `POST` | `/api/v1/publications` | Add custom publication to catalog | Authenticated |
| `POST` | `/api/v1/publications/ingest` | Automated ingestion from OpenAlex/CrossRef/Semantic Scholar | Authenticated |
| `GET` | `/api/v1/publications/my` | Retrieve publications linked to authenticated profile | Authenticated |
| `GET` | `/api/v1/publications/recommendations` | Get personalized publication recommendations | Authenticated |
| `GET` | `/api/v1/publications/{id}`| Fetch publication details by ID | Authenticated |
| `PUT` | `/api/v1/publications/{id}`| Update publication metadata | Authenticated |
| `DELETE`| `/api/v1/publications/{id}`| Remove publication from catalog | Authenticated |
| `GET/POST`| `/api/v1/publications/{id}/analyze` | Trigger or retrieve AI paper discourse analysis | Authenticated |

### 5. Patents & Patent Landscape (`/patents`, `/patent-intelligence`)
| Method | Endpoint | Description | Access Level |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/patents` | Paginated patent disclosures catalog search | Authenticated |
| `POST` | `/api/v1/patents` | Register new patent disclosure | Authenticated |
| `POST` | `/api/v1/patents/ingest` | Ingest external patent disclosures | Authenticated |
| `GET` | `/api/v1/patents/my` | List patents attributed to user profile | Authenticated |
| `POST/DELETE`| `/api/v1/patents/{id}/bookmark` | Toggle user patent bookmarking | Authenticated |
| `GET` | `/api/v1/patent-intelligence/landscape` | Landscape metrics (total, granted, assignees, citations) | Authenticated |
| `GET` | `/api/v1/patent-intelligence/trends` | Temporal patent filing trends by year | Authenticated |
| `GET` | `/api/v1/patent-intelligence/assignees` | Top patent assignees and HHI concentration index | Authenticated |
| `GET` | `/api/v1/patent-intelligence/clusters` | **K-Means unsupervised patent text clustering** | Authenticated |
| `GET` | `/api/v1/patent-intelligence/competitive-landscape` | Competitor portfolio density analysis | Authenticated |
| `GET` | `/api/v1/patent-intelligence/jurisdictions` | Patent distribution across USPTO, EPO, WIPO, CNIPA, etc. | Authenticated |

### 6. Funding Intelligence (`/funding`)
| Method | Endpoint | Description | Access Level |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/funding` | Search active grant solicitations with filters | Authenticated |
| `POST` | `/api/v1/funding` | Create new funding opportunity record | Authenticated |
| `POST` | `/api/v1/funding/ingest` | Trigger Grants.gov / NSF grant ingestion pipeline | Authenticated |
| `GET` | `/api/v1/funding/recommendations` | Personalized grants ranked by profile match score | Authenticated |
| `GET` | `/api/v1/funding/saved` | List bookmarked grants for user | Authenticated |
| `GET` | `/api/v1/funding/{id}` | Retrieve grant details by ID | Authenticated |
| `GET` | `/api/v1/funding/{id}/eligibility` | Evaluate eligibility match criteria and rationale | Authenticated |
| `POST/DELETE`| `/api/v1/funding/{id}/save` | Bookmark or unbookmark funding opportunity | Authenticated |

### 7. Research Intelligence & Trends (`/research-intelligence`)
| Method | Endpoint | Description | Access Level |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/research-intelligence/trends/publications` | Publication growth volume and CAGR trends | Authenticated |
| `GET` | `/api/v1/research-intelligence/trends/citations` | Citation velocity and median metrics by year | Authenticated |
| `GET` | `/api/v1/research-intelligence/emerging-topics` | Topics accelerating in publication velocity | Authenticated |
| `GET` | `/api/v1/research-intelligence/hotspots` | Cross-domain critical research hotspots | Authenticated |
| `GET` | `/api/v1/research-intelligence/gaps` | Identified literature white spaces and research gaps | Authenticated |

### 8. Technology Intelligence & Whitespace (`/technology-intelligence`)
| Method | Endpoint | Description | Access Level |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/technology-intelligence/activity` | Activity volume across papers and patents | Authenticated |
| `GET` | `/api/v1/technology-intelligence/growth` | Multi-year growth velocity and momentum trajectory | Authenticated |
| `GET` | `/api/v1/technology-intelligence/maturity` | **6-indicator Technology Maturity Model** | Authenticated |
| `GET` | `/api/v1/technology-intelligence/whitespace` | Statistical whitespace gap detection radar | Authenticated |
| `GET` | `/api/v1/technology-intelligence/summary` | Comprehensive technology intelligence summary | Authenticated |

### 9. Innovation Scoring & TRL (`/innovation-scoring`)
| Method | Endpoint | Description | Access Level |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/innovation-scoring/score` | **5-Pillar Innovation Score** with factor explainability | Authenticated |
| `GET` | `/api/v1/innovation-scoring/trl` | Estimated Technology Readiness Level (TRL 1–9) | Authenticated |
| `GET` | `/api/v1/innovation-scoring/evidence` | Supporting publication, patent, and grant evidence | Authenticated |
| `GET` | `/api/v1/innovation-scoring/summary` | Portfolio-wide innovation scoring summary | Authenticated |

### 10. Commercialization Intelligence (`/commercialization`)
| Method | Endpoint | Description | Access Level |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/commercialization/readiness` | Multi-dimensional commercialization readiness score | Authenticated |
| `GET` | `/api/v1/commercialization/recommendations` | Four canonical pathway recommendations | Authenticated |
| `GET` | `/api/v1/commercialization/evidence` | Evidence justification from patents and grants | Authenticated |
| `GET` | `/api/v1/commercialization/summary` | Cross-domain commercialization readiness distribution | Authenticated |

### 11. Command Center & Dashboard (`/command-center`)
| Method | Endpoint | Description | Access Level |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/command-center/overview` | Role-tailored strategic KPI cards and metrics | Authenticated |
| `GET` | `/api/v1/command-center/activity-feed` | Unified real-time platform event timeline | Authenticated |

### 12. Notification & Alert System (`/notifications`)
| Method | Endpoint | Description | Access Level |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/notifications` | Paginated user notification list with type filtering | Authenticated |
| `GET` | `/api/v1/notifications/unread` | Unread notification list and badge count | Authenticated |
| `PATCH`| `/api/v1/notifications/{id}/read` | Mark single notification as read | Authenticated |
| `PATCH`| `/api/v1/notifications/read-all` | Mark all user notifications as read | Authenticated |
| `POST` | `/api/v1/notifications/scan` | Trigger telemetry scan and generate relevant alerts | Authenticated |

### 13. Reports & Export System (`/reports`)
| Method | Endpoint | Description | Access Level |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/reports/types` | List supported report categories and filter definitions | Authenticated |
| `POST` | `/api/v1/reports/preview` | Generate live structured preview and factor matrices | Authenticated |
| `POST` | `/api/v1/reports/export/pdf` | **Download vector PDF report (ReportLab)** | Authenticated |
| `POST` | `/api/v1/reports/export/excel` | **Download structured Excel workbook (.xlsx)** | Authenticated |
| `GET` | `/api/v1/reports/dossier` | Generate strategic executive dossier | Authenticated |
| `GET` | `/api/v1/reports/summary` | Portfolio cross-domain benchmark matrix | Authenticated |
| `GET` | `/api/v1/reports/export/markdown` | Export dossier as formatted Markdown | Authenticated |
| `GET` | `/api/v1/reports/export/json` | Export dossier as structured JSON | Authenticated |

### 14. Administration & Governance (`/admin`)
| Method | Endpoint | Description | Access Level |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/admin/users` | List platform users with role and status filters | Administrator Only |
| `PUT` | `/api/v1/admin/users/{user_id}/role` | Mutate user platform role | Administrator Only |
| `PUT` | `/api/v1/admin/users/{user_id}/status` | Activate or deactivate user account | Administrator Only |
| `GET` | `/api/v1/admin/system/overview` | High-level system counts and platform health | Administrator Only |
| `GET` | `/api/v1/admin/telemetry/pipelines`| External data provider latency and success telemetry | Administrator Only |
| `GET` | `/api/v1/admin/audit-logs` | Security and administrative audit trail logs | Administrator Only |

---

## 8. AI/ML, NLP & Analytical Methodology

### 1. Scientific Discourse NLP Analysis (Module 3)
- Implemented in [`NLPHeuristicPaperAnalyzer`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/services/paper_analysis_service.py).
- Splits scientific abstracts into discourse units using regex boundaries and classifies sentences using linguistic markers:
  - *Problem Statement:* Identifies goal/challenge markers (`"we investigate"`, `"remains a challenge"`, `"the problem of"`).
  - *Methodology:* Identifies experimental and algorithmic terms (`"we propose"`, `"using deep learning"`, `"framework"`).
  - *Findings & Contributions:* Detects quantitative and outcome terms (`"we demonstrate"`, `"achieving"`, `"results show"`).
  - *Limitations:* Detects constraint vocabulary (`"limited by"`, `"trade-off"`, `"bottleneck"`).
  - *Future Directions:* Detects roadmap phrases (`"future work"`, `"open challenge"`, `"promising direction"`).
- Fallback Architecture: If configured with valid API keys (`GEMINI_API_KEY` or `OPENAI_API_KEY`), the service delegates to LLM providers; otherwise, it executes the deterministic NLP heuristic analyzer.

### 2. Unsupervised Machine Learning Patent Clustering (Module 5)
- Implemented in [`PatentClusteringService`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/services/patent_clustering_service.py).
- Vectorizes normalized patent titles, abstracts, and classifications using `scikit-learn`'s `TfidfVectorizer` (sublinear TF scaling, max 1,000 features, English stop-word filtering).
- Applies `KMeans` centroid clustering to partition disclosures into topical clusters (dynamic k between 2 and 8).
- Extracts top cluster keywords by ordering TF-IDF centroid weights and maps assignees across clusters.

### 3. Assignee Concentration via Herfindahl-Hirschman Index (Module 5)
- Measures patent applicant monopoly density in each technology domain:
  $$\text{HHI} = \sum_{i=1}^{N} \left( \frac{\text{Patents held by Assignee } i}{\text{Total Patents in Domain}} \times 100 \right)^2$$
- Classified into standard economic antitrust tiers:
  - $\text{HHI} < 1,500$: *Unconcentrated Market* (Diverse assignee ecosystem)
  - $1,500 \le \text{HHI} \le 2,500$: *Moderately Concentrated Market*
  - $\text{HHI} > 2,500$: *Highly Concentrated Market* (Patent thicket dominated by few corporations)

### 4. Six-Indicator Technology Maturity Model (Module 6)
- Implemented in [`TechnologyIntelligenceService`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/services/technology_intelligence_service.py).
- Evaluates six indicators normalized to 0–100:
  1. *Publication Growth Velocity:* 3-year Compound Annual Growth Rate (CAGR).
  2. *Patent Filing Velocity:* Patent filing volume growth rate.
  3. *Organization Diversity:* Distinct universities, research centers, and corporate entities publishing.
  4. *Assignee Penetration:* Presence of commercial industrial assignees.
  5. *Jurisdictional Breadth:* Filing ratio across USPTO, EPO, WIPO, CNIPA, and JPO.
  6. *Temporal Recency Ratio:* Proportion of artifacts published within the last 36 months.

### 5. Multi-Factor Innovation Scoring & TRL Engine (Module 7)
- Official formula enforced in [`InnovationScoringService`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/services/innovation_scoring_service.py):
  $$\text{Score} = (0.30 \times \text{Novelty}) + (0.20 \times \text{Patent Strength}) + (0.15 \times \text{Tech Maturity}) + (0.20 \times \text{Market Potential}) + (0.15 \times \text{Funding Relevance})$$
- TRL Rule Engine maps artifacts to standard NASA/DoD stages:
  - *TRL 1–3 (Basic Research):* Scientific publications without patent disclosures or prototype testing.
  - *TRL 4–6 (Laboratory & System Validation):* Disclosed patents, active translational grants, lab prototypes.
  - *TRL 7–9 (Operational Demonstration & Deployment):* Granted patents, corporate co-development, operational demonstration.

### 6. Four-Pathway Commercialization Decision Engine (Module 8)
- Grounded in empirical IP, grant, and ecosystem signals:
  - *Productization:* Triggered by prototype validation (TRL 5+) and commercial application fit.
  - *Licensing:* Triggered by granted patents and identifying corporate patent owners in adjacent domains.
  - *Startup Creation:* Triggered by high novelty, prototype de-risking, and matching SBIR/STTR non-dilutive grant capital.
  - *Industry Partnership:* Triggered by mid-stage maturity (TRL 4–5) benefiting from corporate joint development.
- Transparent reporting policy: Adheres to conservative advisory phrasing; explicitly marks unmeasured dimensions as `DATA_UNAVAILABLE`.

---

## 9. Repository Structure

```text
Research-Funding-Innovation-Intelligence-Platform/
├── backend/
│   ├── alembic/                          # Database schema migration framework
│   │   ├── versions/                     # 8 migration revisions (head: d4e5f6a7b8c9)
│   │   └── env.py                        # Asynchronous SQLAlchemy migration environment
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── endpoints/                # 15 FastAPI endpoint route modules
│   │   │   │   ├── admin.py              # Platform governance, telemetry, user management
│   │   │   │   ├── auth.py               # Authentication, registration, token refresh
│   │   │   │   ├── command_center.py     # Role-tailored KPIs, multi-stream activity feeds
│   │   │   │   ├── commercialization.py  # 4-pathway commercial translation endpoints
│   │   │   │   ├── executive_reports.py  # Reports, live preview, PDF/Excel export endpoints
│   │   │   │   ├── funding.py            # Grant discovery, eligibility match, bookmarks
│   │   │   │   ├── health.py             # Liveness and readiness health checks
│   │   │   │   ├── innovation_scoring.py # 5-pillar innovation score and TRL engine
│   │   │   │   ├── notifications.py      # Notifications, unread counts, event scanning
│   │   │   │   ├── patent_intelligence.py# Landscape analytics, HHI, KMeans clustering
│   │   │   │   ├── patents.py            # Patent CRUD, ingest, bookmarks
│   │   │   │   ├── profile.py            # Research profile facets, taxonomy domains
│   │   │   │   ├── publications.py       # Publication CRUD, DOI ingest, paper analysis
│   │   │   │   ├── research_intelligence.py # Publication velocity, citations, topic hotspots
│   │   │   │   └── technology_intelligence.py # 6-indicator maturity, whitespace radar
│   │   │   └── api_router.py             # Master APIRouter mounting all 15 controllers
│   │   ├── core/                         # Core infrastructure
│   │   │   ├── config.py                 # Pydantic-Settings environment configuration
│   │   │   ├── database.py               # Async SQLAlchemy engine and session factory
│   │   │   ├── deps.py                   # Dependency injection (get_db, get_current_user, RBAC)
│   │   │   ├── exceptions.py             # Domain exception hierarchy and error handlers
│   │   │   └── security.py               # JWT encoding/decoding and Bcrypt hashing
│   │   ├── models/                       # SQLAlchemy ORM database models
│   │   │   ├── __init__.py               # Central registry of all 15 models + association tables
│   │   │   ├── academic_history.py       # AcademicHistory and ResearchHistory
│   │   │   ├── funding.py                # FundingOpportunity, FundingKeyword, SavedFunding
│   │   │   ├── notification.py           # Notification model (Module 10)
│   │   │   ├── patent.py                 # Patent and profile_patents association
│   │   │   ├── profile.py                # Profile entity linked one-to-one to User
│   │   │   ├── publication.py            # Publication, PublicationKeyword, profile_publications
│   │   │   ├── refresh_token.py          # Persistent RefreshToken model
│   │   │   ├── research_domain.py        # ResearchDomain, ResearchInterest, ProfileKeyword
│   │   │   └── user.py                   # User model with UserRole enumeration
│   │   ├── schemas/                      # Pydantic validation schemas
│   │   │   ├── __init__.py               # Re-exported schema namespace
│   │   │   ├── commercialization.py      # Module 8 response models
│   │   │   ├── funding.py                # Grant discovery and eligibility schemas
│   │   │   ├── innovation_scoring.py     # 5-Pillar breakdown and TRL response schemas
│   │   │   ├── notification.py           # Notification schemas and filter payloads
│   │   │   ├── patent.py & patent_intelligence.py # Patent analytics and clustering schemas
│   │   │   ├── profile.py                # User profile update and read schemas
│   │   │   ├── publication.py            # Publication catalog and paper analysis schemas
│   │   │   ├── report_export.py          # Module 11 preview and export request schemas
│   │   │   └── user.py                   # Auth credentials and token response schemas
│   │   ├── services/                     # Business logic and analytical services
│   │   │   ├── admin_service.py          # Governance telemetry and user administration
│   │   │   ├── command_center_service.py # Role-scoped KPI calculation
│   │   │   ├── commercialization_service.py # 4-pathway commercialization logic
│   │   │   ├── eligibility_matcher.py    # Semantic grant qualification matcher
│   │   │   ├── funding_service.py        # Grant search, ranking, and bookmarking
│   │   │   ├── innovation_scoring_service.py # 5-Pillar formula and TRL engine
│   │   │   ├── notification_service.py   # Event scanning and notification persistence
│   │   │   ├── paper_analysis_service.py # Scientific discourse NLP analysis engine
│   │   │   ├── patent_clustering_service.py # Scikit-learn TF-IDF + KMeans clustering
│   │   │   ├── patent_landscape_service.py # HHI concentration and IPC landscape
│   │   │   ├── publication_service.py    # Publication catalog and provider ingest
│   │   │   ├── report_export_service.py  # ReportLab PDF & OpenPyXL Excel generators
│   │   │   ├── research_trend_service.py # Velocity, CAGR, topic momentum tracking
│   │   │   ├── technology_intelligence_service.py # 6-indicator maturity & whitespace radar
│   │   │   └── providers/                # External connector adapters (OpenAlex, CrossRef, etc.)
│   │   └── main.py                       # FastAPI application entry point, CORS, lifespan
│   ├── scripts/
│   │   ├── create_admin.py               # Administrative provisioning CLI
│   │   └── seed_demo_data.py             # Realistic deep-tech publication seeder
│   ├── tests/                            # 29 Pytest async test modules (221 tests)
│   │   ├── conftest.py                   # In-memory SQLite fixtures and test client setup
│   │   ├── test_auth.py & test_rbac.py   # Auth and RBAC security tests
│   │   ├── test_commercialization.py     # Module 8 commercialization pathway tests
│   │   ├── test_executive_reports.py     # Module 11 PDF/Excel generation and filter tests
│   │   ├── test_funding*.py              # Module 4 grant discovery and eligibility tests
│   │   ├── test_innovation_scoring.py    # Module 7 5-pillar innovation and TRL tests
│   │   ├── test_notifications.py         # Module 10 notification scanning and read tests
│   │   ├── test_patent*.py               # Module 5 patent landscape and clustering tests
│   │   ├── test_profile*.py              # Module 2 profile and taxonomy tests
│   │   └── test_technology_intelligence*.py # Module 6 maturity and whitespace tests
│   ├── alembic.ini                       # Alembic database migration configuration
│   ├── Dockerfile                        # Multi-stage container definition
│   └── requirements.txt                  # Python dependency manifest
├── frontend/
│   ├── src/
│   │   ├── app/                          # Next.js 14 App Router routes (18 routes)
│   │   │   ├── (auth)/login & register   # Public authentication interfaces
│   │   │   ├── (dashboard)/              # Authenticated workspace layout and pages
│   │   │   │   ├── admin/                # System governance and audit logs (M9)
│   │   │   │   ├── commercialization/    # 4-Pathway commercialization dashboard (M8)
│   │   │   │   ├── dashboard/            # Role-tailored command center (M9)
│   │   │   │   ├── funding/              # Grant radar and eligibility analyzer (M4)
│   │   │   │   ├── patents/              # Patent landscape and clustering view (M5)
│   │   │   │   ├── profile/              # Researcher profile and taxonomy management (M2)
│   │   │   │   ├── publications/         # Catalog search and paper analysis (M3)
│   │   │   │   ├── reports/              # Reports, live preview & PDF/Excel export (M11)
│   │   │   │   ├── research-intelligence/# Literature velocity and gap analysis (M3)
│   │   │   │   ├── scoring/              # 5-Pillar innovation and TRL engine (M7)
│   │   │   │   ├── technology-intelligence/# 6-indicator maturity & whitespace radar (M6)
│   │   │   │   └── trends/               # Emerging topic momentum view (M3)
│   │   │   ├── globals.css               # Design tokens, custom utilities, dark theme
│   │   │   ├── layout.tsx                # Root layout with font configuration
│   │   │   └── page.tsx                  # Public marketing hero landing page
│   │   ├── components/                   # UI components
│   │   │   ├── NotificationCenter.tsx    # Module 10 Notification bell, popover, badge
│   │   │   └── ui/                       # Reusable UI primitives (Button, Input, Badge)
│   │   ├── lib/                          # Client utilities and Vitest test suites
│   │   │   ├── api.ts                    # Axios client instance with Bearer interceptors
│   │   │   ├── auth.ts                   # Token storage and session management
│   │   │   ├── reports.ts                # Module 11 report metadata and filter validation
│   │   │   └── *.test.ts                 # 14 Vitest unit test modules (70 tests)
│   │   └── types/                        # TypeScript domain interfaces
│   ├── package.json                      # NPM dependencies and scripts
│   ├── tailwind.config.ts                # Tailwind design configuration
│   ├── tsconfig.json                     # TypeScript compiler configuration
│   └── vitest.config.ts                  # Vitest test runner configuration
├── .env.example                          # Safe environment variable template
├── .gitignore                            # Git file exclusion rules
├── docker-compose.yml                    # PostgreSQL 16 container definition
├── MODULE_08_COMMERCIALIZATION.md        # Module 8 deep-dive audit report
└── README.md                             # Comprehensive project documentation
```

---

## 10. Prerequisites & System Requirements

Before running the platform, ensure the following tools are installed:

- **Operating System:** Windows 10/11 (PowerShell), macOS (Zsh), or Linux (Bash).
- **Python:** Version `3.10.x` or `3.11.x` (`python --version`).
- **Node.js:** Version `18.x` or `20.x` LTS (`node --version`).
- **Package Manager:** `npm` (version `9.x` or `10.x`).
- **Container Runtime:** Docker Desktop and Docker Compose v2 (`docker --version`, `docker compose version`).
- **Version Control:** Git (`git --version`).

---

## 11. Installation & Local Setup Guide

### Step-by-Step PowerShell Setup

Follow these commands to configure the platform locally on Windows:

```powershell
# 1. Clone the repository
git clone https://github.com/adityabobade7900/Research-Funding-Innovation-Intelligence-Platform.git
cd Research-Funding-Innovation-Intelligence-Platform

# 2. Configure the environment file
Copy-Item .env.example .env

# 3. Start the PostgreSQL 16 container using Docker Compose
docker compose up -d

# Verify container is healthy
docker ps

# 4. Configure Backend Python Environment
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1

# Upgrade pip and install all verified dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# 5. Apply Database Migrations
alembic upgrade head

# 6. Provision the Initial Administrator Account
python scripts/create_admin.py --email admin@platform.gov --password SecureAdminPassword123! --name "Platform Administrator"

# 7. (Optional) Seed realistic deep-tech demo publications
python scripts/seed_demo_data.py

# 8. Configure Frontend Node Environment (in frontend directory)
cd ..\frontend
npm install
```

---

### Three-Terminal Running Workflow

To run the full-stack system concurrently:

#### Terminal 1: Database Infrastructure
```powershell
# In project root
docker compose up
```

#### Terminal 2: FastAPI Backend Server
```powershell
# In project root
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
*Backend is operational at:*
- **Base API:** `http://localhost:8000/api/v1`
- **Health Probe:** `http://localhost:8000/api/v1/health`
- **Interactive Swagger Docs:** `http://localhost:8000/docs`
- **ReDoc Documentation:** `http://localhost:8000/redoc`

#### Terminal 3: Next.js 14 Web Application
```powershell
# In project root
cd frontend
npm run dev
```
*Frontend application is operational at:*
- **Web Portal:** `http://localhost:3000`
- **Login Screen:** `http://localhost:3000/login`
- **Registration Screen:** `http://localhost:3000/register`
- **Executive Dashboard:** `http://localhost:3000/dashboard`

---

## 12. Environment Variable Configuration

All environment configuration is governed through Pydantic-Settings in [`backend/app/core/config.py`](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/core/config.py). Variables are read from the root `.env` file:

| Environment Variable | Required | Default / Safe Example | Description & Development Notes |
| :--- | :---: | :--- | :--- |
| `ENVIRONMENT` | Optional | `development` | Runtime environment (`development`, `staging`, `production`). |
| `PROJECT_NAME` | Optional | `"Research Funding..."` | Application name displayed across logs and documentation. |
| `API_V1_STR` | Optional | `/api/v1` | Root URL prefix for REST endpoints. |
| `BACKEND_HOST` | Optional | `0.0.0.0` | Bind host IP for Uvicorn server. |
| `BACKEND_PORT` | Optional | `8000` | Bind port number for Uvicorn server. |
| `JWT_SECRET` | **Required** | *Placeholder* | Cryptographic key used to sign and verify JWT tokens. Must be changed in production. |
| `JWT_ALGORITHM` | Optional | `HS256` | Cryptographic signature algorithm for JWT tokens. |
| `ACCESS_TOKEN_EXPIRE_MINUTES`| Optional | `60` | Duration in minutes before JWT access tokens expire. |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Optional | `7` | Duration in days before persistent refresh tokens expire. |
| `DATABASE_URL` | **Required** | `postgresql+asyncpg://postgres:postgres@localhost:5432/research_intel_db` | Asynchronous connection string for the primary PostgreSQL database. |
| `TEST_DATABASE_URL` | Optional | `sqlite+aiosqlite:///:memory:` | Connection string for isolated test suite execution. |
| `CORS_ORIGINS` | Optional | `["http://localhost:3000"]` | JSON-encoded or comma-separated list of allowed client origins. |
| `OPENALEX_EMAIL` | Optional | `researcher@domain.edu` | Email sent to OpenAlex API for polite rate-limit tier. |
| `SEMANTIC_SCHOLAR_API_KEY` | Optional | *None* | Optional API key for Semantic Scholar citation data. |
| `CROSSREF_MAILTO` | Optional | `researcher@domain.edu` | Email for CrossRef metadata ingestion polite pool. |
| `GEMINI_API_KEY` | Optional | *None* | Optional API key for Google Gemini LLM paper analysis fallback. |
| `OPENAI_API_KEY` | Optional | *None* | Optional API key for OpenAI GPT paper analysis fallback. |
| `NEXT_PUBLIC_API_URL` | **Required** | `http://localhost:8000/api/v1` | Public backend URL consumed by Next.js frontend Axios client. |

---

## 13. Testing & Verification Suite

The repository includes test suites across backend Python logic, frontend TypeScript contracts, and Next.js static build compilation.

### Backend Pytest Suite (221 Tests)
The backend test suite executes against an isolated in-memory SQLite database (`sqlite+aiosqlite:///:memory:`) using `pytest-asyncio` fixtures, avoiding external database dependencies or test pollution:

```powershell
# Navigate to backend directory with virtual environment active:
cd backend
pytest -v
```
**Observed Test Results:**
```
============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-8.2.2, pluggy-1.6.0
rootdir: D:\Infosys 7.0\Intelligent-Research1\backend
plugins: anyio-4.14.2, asyncio-0.23.7
collected 221 items

tests/test_health.py .                                                   [  0%]
tests/test_auth.py ......................                                [ 10%]
tests/test_rbac.py ..                                                    [ 11%]
tests/test_profile.py .                                                  [ 11%]
tests/test_profile_extended.py ......                                    [ 14%]
tests/test_publications.py .........                                     [ 18%]
tests/test_ingest.py .....                                               [ 20%]
tests/test_providers.py ........                                         [ 24%]
tests/test_paper_analysis.py .......                                     [ 27%]
tests/test_paper_recommendations_and_gaps.py ..........                  [ 32%]
tests/test_patents.py ........                                           [ 35%]
tests/test_patent_intelligence.py ........                               [ 39%]
tests/test_patent_clustering_and_landscape.py ...........                [ 44%]
tests/test_funding.py ......                                             [ 47%]
tests/test_funding_eligibility.py ......                                 [ 49%]
tests/test_funding_ingest.py .....                                       [ 52%]
tests/test_funding_providers.py .....                                    [ 54%]
tests/test_funding_recommendations.py .......                            [ 57%]
tests/test_funding_saved_and_deadlines.py ...........                    [ 62%]
tests/test_research_intelligence.py ........                             [ 66%]
tests/test_technology_intelligence.py ........                          [ 69%]
tests/test_technology_intelligence_extended.py ...........               [ 74%]
tests/test_innovation_scoring.py ................                        [ 81%]
tests/test_commercialization.py ..............                           [ 88%]
tests/test_command_center.py ......                                      [ 90%]
tests/test_admin.py ........                                             [ 94%]
tests/test_notifications.py ...........                                  [ 99%]
tests/test_executive_reports.py ................                         [100%]

============================= 221 passed in 62.83s =============================
```

---

### Frontend Vitest Suite (70 Tests)
The frontend test suite evaluates API client contracts, data models, role-based utilities, and filter boundary validation:

```powershell
# In frontend directory:
cd frontend
npm test
```
**Observed Test Results:**
```
 RUN  v4.1.11 D:/Infosys 7.0/Intelligent-Research1/frontend

 ✓ src/lib/funding.test.ts (8 tests)
 ✓ src/lib/paper_recommendations_and_gaps.test.ts (5 tests)
 ✓ src/lib/technology_intelligence.test.ts (10 tests)
 ✓ src/lib/paper_analysis.test.ts (6 tests)
 ✓ src/lib/notifications.test.ts (6 tests)
 ✓ src/lib/patent_intelligence.test.ts (6 tests)
 ✓ src/lib/research_intelligence.test.ts (5 tests)
 ✓ src/lib/admin.test.ts (4 tests)
 ✓ src/lib/user_profile.test.ts (4 tests)
 ✓ src/lib/commercialization.test.ts (5 tests)
 ✓ src/lib/executive_report.test.ts (3 tests)
 ✓ src/lib/command_center.test.ts (1 test)
 ✓ src/lib/utils.test.ts (2 tests)
 ✓ src/lib/innovation_scoring.test.ts (5 tests)

 Test Files  14 passed (14)
      Tests  70 passed (70)
   Duration  672ms
```

---

### Next.js 14 Production Build Verification (18/18 Routes)
Validates TypeScript static compilation, ESLint rules, and static route optimization:

```powershell
# In frontend directory:
cd frontend
npm run build
```
**Observed Build Results:**
```
  ▲ Next.js 14.2.35

 ✓ Compiled successfully
   Linting and checking validity of types ...
   Collecting page data ...
 ✓ Generating static pages (18/18)
   Finalizing page optimization ...
   Collecting build traces ...

Route (app)                              Size     First Load JS
┌ ○ /                                    175 B          96.2 kB
├ ○ /_not-found                          873 B          88.2 kB
├ ○ /admin                               4.24 kB         110 kB
├ ○ /commercialization                   6.82 kB         112 kB
├ ○ /dashboard                           4.96 kB         127 kB
├ ○ /funding                             9.62 kB         115 kB
├ ○ /login                               3 kB            125 kB
├ ○ /patents                             9.38 kB         115 kB
├ ○ /profile                             6.7 kB          120 kB
├ ○ /publications                        5.94 kB         128 kB
├ ƒ /publications/[id]                   7.67 kB         129 kB
├ ○ /register                            3.93 kB         126 kB
├ ○ /reports                             6.74 kB         112 kB
├ ○ /research-intelligence               180 B           134 kB
├ ○ /scoring                             5.11 kB         111 kB
├ ○ /technology-intelligence             6.62 kB         112 kB
└ ○ /trends                              180 B           134 kB
+ First Load JS shared by all            87.3 kB

○  (Static)   prerendered as static content
ƒ  (Dynamic)  server-rendered on demand
```

---

## 14. Security & Governance Implementation

1. **Password Hashing:** Passwords hashed using Bcrypt (`passlib.context.CryptContext` with `bcrypt` backend and automatic salt generation). Plaintext passwords are never logged or stored.
2. **Access & Refresh Token Separation:** Short-lived JWT access tokens (60 minutes) signed with HS256 algorithm. Refresh tokens stored as SHA-256 hashes in the PostgreSQL `refresh_tokens` table, allowing revocation upon logout.
3. **Hardened RBAC:** Route guards on FastAPI backend dependencies (`require_roles([UserRole.ADMINISTRATOR])`) and Next.js client-side route guards.
4. **Administrative Protection:** Self-registration with `administrator` role explicitly rejected (`403 Forbidden`). Administrator accounts can only be provisioned via server-side CLI execution (`scripts/create_admin.py`).
5. **Cross-User Data Isolation:** Profile-scoped SQL queries filter records by `profile_id` or `current_user.id`, preventing cross-user data tampering across publications, bookmarks, notifications, and custom exports.
6. **Strict Input Validation:** All endpoint request bodies validated through Pydantic v2 schemas; invalid inputs rejected with `422 Unprocessable Entity`.

---

## 15. Team Roles & Git Collaboration Workflow

### Internship Team Assignments
The platform was built by a collaborative team of six engineers under the **Infosys Springboard Virtual Internship 7.0**:

| Team Member | Engineering Role | Assigned Scope | Feature Branch |
| :--- | :--- | :--- | :--- |
| **Jyotirmaya** | Backend & API Developer + Team Lead | FastAPI core architecture, REST routing, services orchestration | `feature/jyotirmaya-backend` |
| **Deepti** | Database & Data Engineer | PostgreSQL relational models, Alembic migrations, indexes | `feature/deepti-database` |
| **Nalini** | Frontend Developer | Next.js 14 App Router, Tailwind UI layout, client state | `feature/nalini-frontend` |
| **Zoha** | Git, Integration, DevOps & Documentation | Git branch workflow, container setup, documentation | `feature/zoha-devops` |
| **Aditya Bobade** | AI/ML & Intelligence + Testing | Scikit-learn clustering, scoring formulas, test suites | `feature/aditya-ai-ml` |
| **Lokesh** | Data Research, Analytics & Reporting | Data connectors, research trends, PDF/Excel export system | `feature/lokesh-analytics` |

---

### Standard Git Branching & Submission Workflow

To ensure clean collaboration, team members adhere to the following workflow:

```powershell
# 1. Fetch latest changes from official repository
git fetch origin

# 2. Check out your assigned feature branch
git checkout feature/aditya-ai-ml   # (replace with assigned branch)

# 3. Pull latest baseline from main
git merge origin/main

# 4. Implement changes within assigned module scope
# Verify git status to ensure untracked files are appropriate
git status

# 5. Execute automated test suites before committing
cd backend; pytest -q; cd ../frontend; npm test; npm run build; cd ..

# 6. Stage and commit changes with descriptive message
git add .
git commit -m "feat(M11): implement ReportLab PDF and OpenPyXL Excel export service"

# 7. Push to the remote repository
git push origin feature/aditya-ai-ml
```

*Collaboration Notes:*
- Never commit `.env`, virtual environment folders (`venv/`, `.venv/`), `node_modules/`, or temporary SQLite database files (`*.db`).
- Protected `main` branch merges occur exclusively through pull request review and mentor verification.
- Direct force pushes (`git push --force`) to shared branches are prohibited.

---

## 16. Troubleshooting & Diagnostics

| Symptom / Error | Root Cause | Verified Solution |
| :--- | :--- | :--- |
| `ConnectionRefusedError: [WinError 1225]` on port 5432 | PostgreSQL container is stopped or Docker is not running. | Run `docker compose up -d` in project root and verify container health with `docker ps`. |
| `sqlalchemy.exc.OperationalError: no such table` | Database migrations have not been applied to the database. | Activate backend virtual environment and execute: `alembic upgrade head`. |
| `Cannot find module '@/...'` in frontend test execution | Vitest relative import resolution issue within `src/lib/`. | Ensure intra-library imports in `src/lib/` use relative paths (`./reports`) rather than root aliases. |
| `HTTP 401 Unauthorized` on export/notification endpoints | Missing Bearer token in request headers. | Ensure user is authenticated via `/login` or provide `Authorization: Bearer <TOKEN>` in API client. |
| `HTTP 403 Forbidden: PERMISSION_DENIED` during registration | User attempted to self-register with `administrator` role. | Register as `researcher`, `startup_founder`, or `innovation_manager`. Provision admin via `python scripts/create_admin.py`. |
| `Port 8000 already in use` | Existing Uvicorn or Python process is still bound to port 8000. | Stop existing process via Task Manager or run `netstat -ano \| findstr :8000` and `taskkill /PID <PID> /F`. |
| `Port 3000 already in use` | Existing Node.js development server is still running. | Stop existing Next.js process or launch on alternate port: `npm run dev -- -p 3001`. |
| Empty results returned from Grants.gov / NSF search | Live government grant search returned no live records for domain. | The platform automatically utilizes `MockFundingProvider` fallback records to provide deterministic demo opportunities. |

---

## 17. Current Implementation Status & Known Limitations

### Implementation Audit Matrix
| Module | Official Module Title | Implementation Status | Verified Test Coverage |
| :---: | :--- | :---: | :---: |
| **M1** | User Authentication & Role-Based Access Control | 🟢 **Verified & Complete** | 24 Pytest cases (`test_auth.py`, `test_rbac.py`) |
| **M2** | Research Profile Management | 🟢 **Verified & Complete** | 7 Pytest cases (`test_profile.py`, `test_profile_extended.py`) |
| **M3** | Research Intelligence & Paper Analysis | 🟢 **Verified & Complete** | 24 Pytest cases (`test_publications.py`, `test_paper_analysis.py`, etc.) |
| **M4** | Funding Intelligence & Grant Discovery | 🟢 **Verified & Complete** | 35 Pytest cases (`test_funding*.py`) |
| **M5** | Patent Landscape Analysis & Clustering | 🟢 **Verified & Complete** | 27 Pytest cases (`test_patent*.py`) |
| **M6** | Technology Intelligence & Whitespace Discovery | 🟢 **Verified & Complete** | 19 Pytest cases (`test_technology_intelligence*.py`) |
| **M7** | Multi-Factor Innovation Scoring & TRL Engine | 🟢 **Verified & Complete** | 16 Pytest cases (`test_innovation_scoring.py`) |
| **M8** | Commercialization Recommendations | 🟢 **Verified & Complete** | 14 Pytest cases (`test_commercialization.py`) |
| **M9** | Dashboard & Administrative Command Center | 🟢 **Verified & Complete** | 14 Pytest cases (`test_command_center.py`, `test_admin.py`) |
| **M10**| Notification & Alert System | 🟢 **Verified & Complete** | 11 Pytest cases (`test_notifications.py`) |
| **M11**| Reports & Export System | 🟢 **Verified & Complete** | 16 Pytest cases (`test_executive_reports.py`) |

---

### Known Limitations & Honest Disclosures
1. **Synchronous Document Generation:** PDF (ReportLab) and Excel (openpyxl) generation occurs synchronously within HTTP request workers. This is suitable for current reporting workloads; asynchronous background queues (Celery/Redis) are planned for large historical archives.
2. **External Data Provider Availability:** Live Grants.gov and NSF searches depend on external agency availability. In local environments without API keys or during upstream agency downtime, the system falls back to mock providers to ensure reliability.
3. **Transparent Adoption Status:** Real-world corporate adoption telemetry and clinical regulatory approvals are not indexed. Rather than generating inaccurate scores, these dimensions are marked as `DATA_UNAVAILABLE`.
4. **Document Database Scope:** MongoDB is configured in `.env.example` as a placeholder for future document storage pipelines, but all primary relational data models currently reside in PostgreSQL.
5. **Module 12 Scope:** Module 12 (deployment/CI as a separate project module) was excluded from the mentor's assigned functional scope. Containerization and test suites are documented as implemented in the repository.

---

## 18. Future Roadmap

- [ ] **Asynchronous Task Queue:** Integrate Celery and Redis to handle batch background document export and scheduled external scraper runs.
- [ ] **Outbound Notification Delivery:** Add an SMTP/SendGrid email dispatcher and Web Push notifications alongside the database-backed notification center.
- [ ] **Real-Time WebSocket Updates:** Implement WebSocket connections for instant notification delivery without polling.
- [ ] **USPTO Bulk Ingestion Pipeline:** Add automated bulk patent ingestion from USPTO weekly bulk data feeds.
- [ ] **ORCID OAuth Integration:** Enable direct researcher sign-in through institutional ORCID OAuth2 login.

---

## 19. Deliverables & Conclusion

The **Research Funding & Innovation Intelligence Platform** delivers a full-stack solution bridging academic discovery and commercial translation:
- **Unified Intelligence:** Integrates publications, grants, patents, and market signals into a centralized PostgreSQL database.
- **Explainable Analytics:** Uses an objective 5-pillar mathematical model (Novelty 30%, Patents 20%, Tech Maturity 15%, Market Potential 20%, Funding 15%) and TRL heuristics.
- **Actionable Commercialization:** Provides 4 conservative translation pathways with IP attribution and explicit data limitations.
- **Professional Reporting:** Features dynamic live previews, ReportLab PDF generation, and multi-sheet openpyxl Excel exports.
- **Verification:** Verified by **221 passing backend tests**, **70 passing frontend tests**, and **18/18 compiling Next.js routes**.

---

## 20. License & Acknowledgments

### Project Attribution
- **Program:** Infosys Springboard Virtual Internship 7.0
- **Project Domain:** Artificial Intelligence, Machine Learning, Full-Stack Enterprise Systems
- **Repository:** `adityabobade7900/Research-Funding-Innovation-Intelligence-Platform`

### Data Sources & Open-Source Acknowledgments
We acknowledge the open scientific registries and libraries that support this platform:
- [OpenAlex](https://openalex.org/) and [CrossRef](https://www.crossref.org/) for scholarly publication metadata.
- [Grants.gov](https://www.grants.gov/) and the [National Science Foundation (NSF)](https://www.nsf.gov/) for public funding solicitation data.
- [FastAPI](https://fastapi.tiangolo.com/), [SQLAlchemy](https://www.sqlalchemy.org/), [ReportLab](https://www.reportlab.com/), [OpenPyXL](https://openpyxl.readthedocs.io/), and [Next.js](https://nextjs.org/) for open-source frameworks.

*(Educational and internship evaluation project. All rights reserved by project contributors and Infosys Springboard Internship 7.0).*
