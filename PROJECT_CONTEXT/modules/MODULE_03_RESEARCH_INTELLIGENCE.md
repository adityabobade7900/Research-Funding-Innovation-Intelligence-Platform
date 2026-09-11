# MODULE_03_RESEARCH_INTELLIGENCE.md — Research Intelligence & Paper Analysis

> **NUMBERING CLARIFICATION:**  
> • Designated as **Module 3** in Mentor Communications.  
> • Designated as **Module 4** in the Official Specification PDF.

# Objective
Provide scientific literature discovery, external bibliographic ingestion, temporal publication trend tracking, citation analytics, emerging scientific topic detection, and composite research hotspot discovery.

# Official Requirements (Module 4 in PDF)
- Publication trend analysis
- Emerging topic detection
- Research hotspot identification
- Domain trend monitoring
- Citation analytics
- Data Sources: Research Papers, Publications, Conference Proceedings, Open Repositories

# Mentor Requirements (Module 3 in Mentor Specs)
- Research Intelligence Dashboard with publication velocity and domain distribution.
- Research paper search and detailed metadata page (`/publications/[id]`).
- AI Paper Analysis framework (Problem, Methodology, Findings, Limitations, Future Directions).
- Research recommendations based on user research profile.
- Multi-provider ingestion support (Semantic Scholar, OpenAlex, Crossref).

# Current Implementation
- Full scientific literature CRUD and search catalog.
- Multi-provider adapter layer in `backend/app/services/providers/` (OpenAlex, Crossref, Semantic Scholar, Mock).
- DOI-based single paper ingestion (`POST /api/v1/publications/ingest`).
- Inverted-index abstract reconstruction for OpenAlex works.
- SQL-level aggregation engine (`ResearchTrendService`) calculating YoY publication growth, domain growth curves, citation medians/averages, and composite hotspot scores.

# Frontend
- Route: `/publications` in `frontend/src/app/(dashboard)/publications/page.tsx` (Search, domain filters, year filters, ingest modal).
- Route: `/publications/[id]` in `frontend/src/app/(dashboard)/publications/[id]/page.tsx` (Paper details, abstract, DOI link, citations).
- Route: `/research-intelligence` in `frontend/src/app/(dashboard)/research-intelligence/page.tsx` (Publication trends, domain shares, citation statistics).
- Route: `/trends` in `frontend/src/app/(dashboard)/trends/page.tsx` (Emerging topic acceleration rankings).

# Backend
- Routers: `backend/app/api/v1/endpoints/publications.py` and `research_intelligence.py`
- Services: `backend/app/services/publication_service.py` and `research_trend_service.py`
- Providers: `backend/app/services/providers/openalex.py`, `crossref.py`, `semantic_scholar.py`

# Database
- Models: `Publication`, `PublicationKeyword`, and junction `profile_publications`.
- Persistent Reality: Only **2 persistent rows** currently exist in PostgreSQL; test suites and dashboards utilize mock provider fixtures for full test reliability.
- Migration: `53d7c57aa26c`.

# APIs
- `GET /api/v1/publications` & `POST /api/v1/publications`
- `POST /api/v1/publications/ingest` (Passes DOI to harvester)
- `GET /api/v1/publications/{id}`
- `GET /api/v1/research-intelligence/trends/publications`
- `GET /api/v1/research-intelligence/trends/domains`
- `GET /api/v1/research-intelligence/trends/citations`
- `GET /api/v1/research-intelligence/emerging-topics`
- `GET /api/v1/research-intelligence/hotspots`

# AI/ML
- **Current Reality:** Deterministic statistical analysis (YoY growth rates, citation averages, moving velocity).
- **Not Real AI:** Neural embeddings and LLM paper summarization are **PLANNED**, not currently executing.

# External Data Sources
- OpenAlex API (works endpoint)
- Crossref REST API (works DOI endpoint)
- Semantic Scholar Graph API
- Built-in offline mock provider

# Integration With Other Modules
- Feeds publication novelty metrics into Module 7 (`InnovationScoringService`, 30% weight).
- Links academic publications to patent prior art in Module 5.
- Provides scientific baseline for Module 6 (Whitespace discovery).

# Testing
- `backend/tests/test_publications.py` (10 passing tests).
- `backend/tests/test_research_intelligence.py` (8 passing tests).
- `backend/tests/test_providers.py` (8 passing tests).
- `frontend/src/lib/research_intelligence.test.ts` (3 passing tests).

# Known Issues
- Sparse persistent data in PostgreSQL (only 2 records).
- Deep learning semantic paper search not yet installed.

# Missing Requirements
- Batch automated ingestion script to seed 100+ papers.
- LLM summarizer generating explicit Problem / Limitation / Future Gap sections.

# Next Steps
- Execute bulk ingestion from OpenAlex into PostgreSQL.
- Add `sentence-transformers` for dense semantic vector search.

# Evidence / File Paths
- [publications.py](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/api/v1/endpoints/publications.py)
- [research_intelligence.py](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/api/v1/endpoints/research_intelligence.py)
- [research_trend_service.py](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/services/research_trend_service.py)
- [openalex.py](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/services/providers/openalex.py)
- [publications/page.tsx](file:///d:/Infosys%207.0/Intelligent-Research1/frontend/src/app/(dashboard)/publications/page.tsx)
