# 00_READ_FIRST.md — Project Continuity Master Guide

> **CRITICAL WARNING FOR DEVELOPER / AGENT / USER:**  
> **DO NOT START FROM SCRATCH.**  
> **DO NOT REWRITE EXISTING FUNCTIONALITY.**  
> **DO NOT REBUILD MODULES 1 THROUGH 9 OR 11.**  
> **DO NOT MODIFY APPLICATION CODE WITHOUT INSPECTING EXISTING SOURCE FILES FIRST.**  
> The repository already contains a functioning, production-tested platform with 150 backend tests passing, 30 frontend tests passing, 18 compiled Next.js routes, and an active PostgreSQL 16 database.

---

## 1. Project Identification

- **Project Name:** Research Funding & Innovation Intelligence Platform
- **Official GitHub Repository:** [https://github.com/adityabobade7900/Research-Funding-Innovation-Intelligence-Platform](https://github.com/adityabobade7900/Research-Funding-Innovation-Intelligence-Platform)
- **Secondary / Origin Git Remote:** `https://github.com/springboardmentor3214x/Intelligent-Research1.git`
- **Active Feature Branch:** `feature/aditya-ai-ml` (synced with `personal/main`)
- **Primary Purpose:** An enterprise-grade AI-powered intelligence platform bridging academic scientific research, intellectual property (patent landscape), grant funding opportunities, and commercial market viability for Researchers, Startup Founders, Innovation Managers, and Administrators.

---

## 2. Current Overall Status

As of this checkpoint:
- **Total Modules:** 12 Official Modules (10 Fully Implemented, 2 Partially Implemented, 0 Not Started).
- **Total Milestones:** 4 Official Milestones (3 Fully Completed: Milestones 1, 2, 3; Milestone 4 is ~85% complete).
- **Backend Quality:** 150 / 150 unit & integration tests passing (`pytest tests/ -v`).
- **Frontend Quality:** 30 / 30 tests passing (`vitest run`).
- **Build Quality:** Next.js 14.2 App Router builds 18 production routes cleanly with 0 TypeScript/ESLint errors.
- **Active Persistence:** Docker PostgreSQL 16 container (`research_intel_postgres`) running on port 5432, managed by SQLAlchemy 2.0 async ORM and 6 Alembic migrations.

---

## 3. Current Active Development Focus

The current project position is **Milestone 4 (Weeks 7 & 8)**:
1. **Module 10 (Notification & Alert System):** Currently at 40% completion. In-app alerts exist on `/dashboard` and `/admin`, but the standalone `notifications` database table, notification preference center, and outbound email dispatcher remain pending.
2. **Module 12 (Final Integration, Testing & Deployment):** Currently at 70% completion. Test suites pass 100%, but an automated `.github/workflows/ci.yml` pipeline and production multi-stage Docker deployment with Nginx need to be added.
3. **Module 3 / 4 Ingestion Pipeline:** While provider adapters (OpenAlex, Crossref, Semantic Scholar, Grants.gov, NSF) and mock fallbacks exist, live production data harvesting scripts need ongoing execution.

---

## 4. Where to Start After Reinstalling Your Laptop

Follow this exact document sequence to resume development without losing context:

1. **First Read:** This file (`00_READ_FIRST.md`) to understand the constraints.
2. **Setup Instructions:** Open [27_RESUME_AFTER_REINSTALL.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/27_RESUME_AFTER_REINSTALL.md) for the step-by-step checklist on setting up Python, Node.js, Docker, and PostgreSQL on a fresh Windows machine.
3. **Environment Variables:** Review [22_ENVIRONMENT_SETUP.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/22_ENVIRONMENT_SETUP.md) to populate your `.env` file safely without committing secrets.
4. **Current State & Checkpoint:** Read [checkpoints/CURRENT_STATE.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/checkpoints/CURRENT_STATE.md) and [checkpoints/RESUME_CHECKLIST.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/checkpoints/RESUME_CHECKLIST.md).
5. **Next Work to Do:** Check [26_NEXT_STEPS.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/26_NEXT_STEPS.md) and [25_PENDING_WORK.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/25_PENDING_WORK.md).

---

## 5. Critical Warnings & Architectural Realities

> [!CAUTION]
> **DO NOT MERGE THE TWO MODULE NUMBERING SYSTEMS SILENTLY:**  
> The **Official Project Specification PDF** numbers modules 1 through 12, where:  
> • Module 3 = Funding Opportunity Discovery  
> • Module 4 = Research Trend Intelligence  
> • Module 5 = Patent Landscape Analysis  
>  
> The **Mentor Communications** refer to:  
> • Module 3 = Research Intelligence and Research Paper Analysis  
> • Module 4 = Funding Intelligence and Funding Opportunity Analysis  
> • Module 5 = Patent Landscape Analysis  
>  
> Read [02_OFFICIAL_REQUIREMENTS.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/02_OFFICIAL_REQUIREMENTS.md) and [03_MENTOR_REQUIREMENTS.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/03_MENTOR_REQUIREMENTS.md) for full details.

> [!IMPORTANT]
> **AI/ML IMPLEMENTATION REALITY:**  
> The current platform implements **deterministic mathematical models, statistical algorithms (HHI concentration, CAGR, moving averages), and rule-based heuristics (NASA TRL 1–9, keyword matching)**.  
> Heavy ML libraries like PyTorch, Sentence-Transformers, and FAISS are **NOT** currently in `backend/requirements.txt`. Do not claim neural embeddings or vector search are active until they are implemented. See [11_AI_ML.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/11_AI_ML.md).

> [!WARNING]
> **DATABASE POPULATION REALITY:**  
> The PostgreSQL database currently contains:  
> • 9 Users & 9 Profiles  
> • 8 Research Domains  
> • 2 Publications  
> • 0 Patents  
> • 0 Funding Opportunities  
> Analytical dashboards function using statistical SQL queries combined with rich mock provider fallbacks when live records are sparse. See [13_RESEARCH_INTELLIGENCE.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/13_RESEARCH_INTELLIGENCE.md).

---

## 6. Directory Map of PROJECT_CONTEXT

| File / Folder | Focus Area |
| :--- | :--- |
| [01_PROJECT_OVERVIEW.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/01_PROJECT_OVERVIEW.md) | Business problem, core workflows, tech stack detected vs planned |
| [02_OFFICIAL_REQUIREMENTS.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/02_OFFICIAL_REQUIREMENTS.md) | 12 modules, 4 milestones, exact evaluation rubric from PDF |
| [03_MENTOR_REQUIREMENTS.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/03_MENTOR_REQUIREMENTS.md) | Mentor module definitions, numbering reconciliation, expectations |
| [04_MODULE_STATUS.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/04_MODULE_STATUS.md) | Granular feature status table with file evidence |
| [05_ARCHITECTURE.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/05_ARCHITECTURE.md) | Full system architecture, request lifecycle, data flow diagrams |
| [06_FRONTEND.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/06_FRONTEND.md) | Next.js 14 App Router, routes inventory, component architecture |
| [07_BACKEND.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/07_BACKEND.md) | FastAPI, routers, schemas, services component map |
| [08_DATABASE.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/08_DATABASE.md) | Database models, schemas, ER diagram, Alembic migrations |
| [09_API_REFERENCE.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/09_API_REFERENCE.md) | 82 REST endpoints mapped by method, auth, parameters, status |
| [10_AUTH_RBAC.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/10_AUTH_RBAC.md) | JWT auth, refresh token rotation, 4 roles, admin security |
| [11_AI_ML.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/11_AI_ML.md) | Real AI vs deterministic math audit, TRL rules, scoring formula |
| [12_EXTERNAL_DATA_SOURCES.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/12_EXTERNAL_DATA_SOURCES.md) | OpenAlex, Crossref, Semantic Scholar, Grants.gov, NSF, Patents |
| [13_RESEARCH_INTELLIGENCE.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/13_RESEARCH_INTELLIGENCE.md) | Research trends, publication analytics, citation metrics |
| [14_FUNDING_INTELLIGENCE.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/14_FUNDING_INTELLIGENCE.md) | Grant discovery, eligibility matching, recommendation engine |
| [15_PATENT_INTELLIGENCE.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/15_PATENT_INTELLIGENCE.md) | Patent landscape, assignee concentration (HHI), competitor index |
| [16_TECHNOLOGY_INTELLIGENCE.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/16_TECHNOLOGY_INTELLIGENCE.md) | Whitespace discovery, technology maturity, CAGR trajectories |
| [17_INNOVATION_SCORING.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/17_INNOVATION_SCORING.md) | 5-pillar mathematical scoring engine, TRL 1–9 rule heuristic |
| [18_COMMERCIALIZATION.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/18_COMMERCIALIZATION.md) | 4 readiness dimensions, commercial pathway classification |
| [19_DASHBOARD_NOTIFICATIONS_REPORTS.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/19_DASHBOARD_NOTIFICATIONS_REPORTS.md) | Command center, admin telemetry, executive dossiers, exports |
| [20_TESTING.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/20_TESTING.md) | 150 pytest tests, 30 vitest tests, build checks, commands |
| [21_DOCKER_DEPLOYMENT.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/21_DOCKER_DEPLOYMENT.md) | Docker Compose PostgreSQL setup, backend Dockerfile, staging |
| [22_ENVIRONMENT_SETUP.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/22_ENVIRONMENT_SETUP.md) | Fresh machine setup, dependency installation, .env templates |
| [23_GIT_WORKFLOW.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/23_GIT_WORKFLOW.md) | Git branches, remotes, commit standards, pull request policies |
| [24_KNOWN_ISSUES.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/24_KNOWN_ISSUES.md) | Identified bugs, limitations, technical debt, and workarounds |
| [25_PENDING_WORK.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/25_PENDING_WORK.md) | Prioritized backlog (P0 to P3) for finishing Milestone 4 |
| [26_NEXT_STEPS.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/26_NEXT_STEPS.md) | Step-by-step engineering roadmap continuing from current state |
| [27_RESUME_AFTER_REINSTALL.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/27_RESUME_AFTER_REINSTALL.md) | Step-by-step fresh installation & continuity walkthrough |
| [28_DEVELOPMENT_RULES.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/28_DEVELOPMENT_RULES.md) | Permanent development commandments and quality rules |
| [29_DECISIONS_LOG.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/29_DECISIONS_LOG.md) | Chronological architecture decision records (ADRs) |
| [30_CHANGELOG.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/30_CHANGELOG.md) | Verified historical changelog of implemented milestones |
| `api/` | In-depth REST contracts and route status inventory |
| `database/` | Model definitions, entity relationships, migration history |
| `modules/` | 12 dedicated deep-dive files for each platform module |
| `checkpoints/` | Verified operational state and quick resume checklist |

---

LAST DOCUMENTATION UPDATE:  
2026-09-11 03:40 IST

DOCUMENTATION GENERATED BY:  
Antigravity (Google DeepMind Advanced Agentic Coding Assistant)
