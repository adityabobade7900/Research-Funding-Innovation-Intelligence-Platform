# 01_PROJECT_OVERVIEW.md — Project Overview & Reality Assessment

## 1. Project Objective & Vision

The **Research Funding & Innovation Intelligence Platform** is an enterprise intelligence system built to connect academic research, patent landscapes, government/private funding solicitations, and technology commercialization pathways into a unified analytical ecosystem.

Scientific breakthroughs frequently languish in academic literature without commercial translation, while startups and innovation managers struggle to identify non-dilutive grant funding, competitive intellectual property barriers, or emerging technology whitespace. This platform automates the ingestion, synthesis, evaluation, and strategic recommendation workflows across these four traditionally fragmented domains.

---

## 2. Target User Personas & Value Proposition

| User Role | Target Audience | Primary Platform Value | Core Views & Tools |
| :--- | :--- | :--- | :--- |
| **Researcher** | University professors, PhD candidates, lab directors, research scientists | Discover grants matched to publications/keywords, track domain citation hotspots, monitor patenting activity around research topics | `/profile`, `/publications`, `/funding`, `/research-intelligence`, `/dashboard` |
| **Startup Founder** | Deep tech entrepreneurs, university spinout founders, incubators | Identify non-dilutive federal grants, assess competitive IP landscapes, evaluate Technology Readiness Level (TRL) and commercialization feasibility | `/funding`, `/patents`, `/scoring`, `/commercialization`, `/dashboard` |
| **Innovation Manager** | Corporate R&D directors, Tech Transfer Offices (TTO), innovation hubs | Monitor organizational IP concentration (HHI), identify unpatented technology whitespace, benchmark innovation scores across portfolios | `/technology-intelligence`, `/scoring`, `/commercialization`, `/reports`, `/dashboard` |
| **Administrator** | System operations, compliance officers, platform managers | Oversee system health, pipeline telemetry, user roles, security audits, and data provider connector status | `/admin`, `/admin/audit-logs`, `/command-center` |

---

## 3. Complete End-to-End Workflow

The platform operates across an interconnected, data-driven intelligence pipeline:

```
[ Researcher Profile Creation ]
            │
            ▼ (Extract Domains & Keywords)
[ Multi-Provider Ingestion Engine ] ──► (OpenAlex, Crossref, Semantic Scholar, Grants.gov, NSF, Patents)
            │
            ▼ (Data Normalization & Deduplication)
[ PostgreSQL Relational Persistence ] ──► (Publications, Patents, Grants, Profile Associations)
            │
            ├──────────────────────┬──────────────────────┬──────────────────────┐
            ▼                      ▼                      ▼                      ▼
  [ Research Trends ]    [ Patent Landscape ]    [ Tech Intelligence ]   [ Funding Discovery ]
   • Temporal Velocity    • Assignee HHI          • Density Mapping       • Keyword Matcher
   • CAGR Hotspots        • IPC Distribution      • Whitespace Gaps       • Eligibility Check
   • Citation Medians     • Competitor Index      • Maturity Index        • Deadline Alerts
            │                      │                      │                      │
            └──────────────────────┴──────────────────────┴──────────────────────┘
                                           │
                                           ▼
                       [ 5-Pillar Innovation Scoring Engine ]
                        • 30% Research Novelty
                        • 20% Patent Strength
                        • 15% Technology Maturity (TRL 1–9)
                        • 20% Market Potential
                        • 15% Funding Relevance
                                           │
                                           ▼
                     [ Commercialization Recommendation Engine ]
                        • IP Defensibility & Market Demand
                        • Strategic Pathways: Licensing vs Spinout vs Joint Dev
                                           │
                                           ▼
                     [ Executive Dossier & Report Export ]
                        • Markdown & JSON Strategic Dossier Exports
                        • Command Center Role-Tailored Dashboard
```

---

## 4. Technology Stack: Detected vs. Specified vs. Planned

To maintain complete transparency and prevent false assumptions after a laptop reinstall, this table explicitly separates **what is actually detected in source code** from **what was officially specified in project documentation**:

| Layer / Technology | Status | Detected in Code | Specified in Requirements | Reality / Implementation Details |
| :--- | :---: | :---: | :---: | :--- |
| **Backend Framework** | 🟢 ACTIVE | Python 3.10, FastAPI 0.111.0, Uvicorn | Python, FastAPI | Production-grade async ASGI REST API |
| **Data Validation** | 🟢 ACTIVE | Pydantic v2 (2.7.4), Pydantic-Settings | Pydantic | Strict request/response validation across all endpoints |
| **Database ORM** | 🟢 ACTIVE | SQLAlchemy 2.0.31 (Async Engine) | SQLAlchemy | Full async session handling (`AsyncSessionLocal`) |
| **Relational Database** | 🟢 ACTIVE | PostgreSQL 16 (via Docker container) | PostgreSQL | `research_intel_db` running on port 5432 |
| **Database Migrations** | 🟢 ACTIVE | Alembic 1.13.2 (6 async revisions) | Alembic | Version-controlled relational schema migrations |
| **Test In-Memory DB** | 🟢 ACTIVE | SQLite via `aiosqlite` (0.20.0) | SQLite (Dev/Test) | Used for sub-second, isolated automated testing |
| **Document Database** | 🟡 PLANNED | Configured in `.env.example` (`MONGODB_URL`), inactive | MongoDB (Secondary) | No active Motor/PyMongo drivers in `requirements.txt` |
| **Frontend Framework** | 🟢 ACTIVE | Next.js 14.2.4 (App Router) | React.js, Next.js | Modern React 18, TypeScript, Server & Client Components |
| **UI Styling** | 🟢 ACTIVE | Tailwind CSS 3.4.4, Lucide React icons | Tailwind CSS | Consistent dark glassmorphic theme across 18 routes |
| **Frontend Testing** | 🟢 ACTIVE | Vitest 4.1.11 | Jest / Vitest | 30 tests covering API services and client state |
| **Backend Testing** | 🟢 ACTIVE | Pytest 8.2.2, Pytest-Asyncio, HTTPX | Pytest | 150 automated tests executing in ~41 seconds |
| **Authentication** | 🟢 ACTIVE | PyJWT (`python-jose`), Passlib (bcrypt) | JWT, OAuth2 | JWT access tokens + refresh token rotation + RBAC |
| **AI / NLP Models** | 🟡 SPECIFIED | Deterministic statistics & rule heuristics | Sentence-Transformers, Hugging Face, LangChain, OpenAI | Heavy neural transformers **NOT** installed in backend venv |
| **Machine Learning** | 🟡 SPECIFIED | Mathematical formulas & NASA TRL heuristics | Scikit-learn, XGBoost, TensorFlow, PyTorch | Pure Python `math` & `statistics` used; scikit-learn is not in `requirements.txt` |
| **Vector Search** | 🟡 PLANNED | Keyword overlap & cosine vector heuristics | FAISS, Elasticsearch, Vector DB | FAISS/Elasticsearch not installed; search is SQL-based |
| **Containerization** | 🟡 PARTIAL | `docker-compose.yml` (Postgres), `backend/Dockerfile` | Docker, Docker Compose | Frontend Dockerfile and root full-stack compose pending |
| **CI/CD Pipeline** | 🟡 PLANNED | Local test execution verified | GitHub Actions | `.github/workflows/ci.yml` not yet authored |

---

## 5. Major Verified Integrations

1. **Authentication & Profile Isolation:** Every user owns an isolated `Profile` record linked to 8 child tables (`academic_histories`, `research_histories`, `profile_domains`, `profile_keywords`, `technology_areas`, `profile_publications`, `profile_patents`, `funding_opportunities`).
2. **Multi-Source Data Harvesters:** Modular provider adapters in `backend/app/services/providers/`:
   - `OpenAlexProvider`: Harvests papers via REST API with inverted-index abstract reconstruction.
   - `CrossrefProvider`: Resolves DOIs and biblio metadata.
   - `SemanticScholarProvider`: Graph API integration for citation counts and fields of study.
   - `GrantsGovProvider`: Federal grant opportunity parser.
   - `NSFFundingProvider`: NSF awards search parser.
   - `GooglePatentsProvider`: Canonical patent identifier resolver.
   - `MockProvider`: Comprehensive offline fixtures for deterministic local testing.
3. **Cross-Module Intelligence Synthesis:**
   - Innovation scoring dynamically pulls publication metrics from Module 4, patent metrics from Module 5, technology maturity from Module 6, and funding metrics from Module 3 to generate the specification's 5-pillar score.
   - Executive reports synthesize findings across all modules into downloadable Markdown and JSON intelligence dossiers.
