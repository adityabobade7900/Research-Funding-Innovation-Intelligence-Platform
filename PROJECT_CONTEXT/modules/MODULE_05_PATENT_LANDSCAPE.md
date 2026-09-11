# MODULE_05_PATENT_LANDSCAPE.md — Patent Landscape Analysis

# Objective
Provide intellectual property portfolio tracking, patent classification distribution, filing velocity curves, assignee market concentration (Herfindahl-Hirschman Index), and competitive landscape benchmarking.

# Official Requirements
- Patent search
- Patent clustering
- Patent trend analysis
- Competitor patent analysis
- Innovation mapping
- Patent Information: Title, Assignee, Filing Date, Classification, Technology Domain, Citation Count

# Mentor Requirements
- Measure assignee concentration using the Herfindahl-Hirschman Index (HHI).
- Compute a Composite Competitive Index weighting volume, velocity, citations, and domain breadth.
- Support modal editing and bookmarking of patents.
- Map patent activity directly into technology whitespace (Module 6) and innovation scoring (Module 7).

# Current Implementation
- Full patent CRUD catalog with classification and domain filters.
- Interactive patent editing modal on `/patents`.
- `PatentLandscapeService` computes:
  - Total patents, assignees, domains, and citation averages.
  - Annual filing velocity and growth curves.
  - Multi-jurisdiction breakdown (USPTO, EPO, WIPO, CNIPA, IPO).
  - Assignee concentration via HHI ($HHI = \sum (s_i)^2$).
  - Composite Competitive Index classifying assignees into `DOMINANT_PORTFOLIO`, `HIGH_VELOCITY`, `NICHE_SPECIALIST`, `EMERGING_APPLICANT`.

# Frontend
- Route: `/patents` in `frontend/src/app/(dashboard)/patents/page.tsx` (Dual-tab interface: Portfolio management and Landscape analytics with charts).

# Backend
- Routers: `backend/app/api/v1/endpoints/patents.py` and `patent_intelligence.py`
- Service: `backend/app/services/patent_landscape_service.py`
- Providers: `backend/app/services/providers/patent_providers.py` (Google Patents URL resolver and mock fixtures)

# Database
- Models: `Patent` and junction `profile_patents`.
- Persistent Reality: Currently **0 persistent rows** in PostgreSQL; development runs smoothly via `SAMPLE_PATENTS` fixtures.
- Migration: `626ab1f43993`.

# APIs
- `GET /api/v1/patents` & `POST /api/v1/patents`
- `GET /api/v1/patents/{id}` & `PUT /api/v1/patents/{id}`
- `GET /api/v1/patent-intelligence/landscape`
- `GET /api/v1/patent-intelligence/trends`
- `GET /api/v1/patent-intelligence/technology-domains`
- `GET /api/v1/patent-intelligence/assignees`
- `GET /api/v1/patent-intelligence/jurisdictions`
- `GET /api/v1/patent-intelligence/status`
- `GET /api/v1/patent-intelligence/competitive-landscape`

# AI/ML
- **Current Reality:** Deterministic statistical formulas (HHI, Composite Index, IPC aggregations).
- **Not Real AI:** Unsupervised machine learning clustering (K-Means/BERTopic) is **PLANNED**, not currently executing.

# External Data Sources
- Google Patents canonical URL generator
- Curated offline mock patent fixtures (Quantum, mRNA, Solid-state batteries)

# Integration With Other Modules
- Feeds patent volume, velocity, and citation strength into Module 7 (`InnovationScoringService`, 20% weight).
- Supplies patent density signals to Module 6 (`TechnologyIntelligenceService`) for whitespace discovery.
- Supplies IP defensibility metrics to Module 8 (`CommercializationService`).

# Testing
- `backend/tests/test_patents.py` (8 passing tests).
- `backend/tests/test_patent_intelligence.py` (8 passing tests).
- `frontend/src/lib/patent_intelligence.test.ts` (3 passing tests).

# Known Issues
- Database currently contains 0 persistent patent records.
- Clustering relies on IPC class grouping rather than semantic abstract clustering.

# Missing Requirements
- Unsupervised vector clustering of patent claims.
- Bulk USPTO data harvester.

# Next Steps
- Implement batch ingestion script to pull live USPTO/Google patent data.
- Add Scikit-learn K-Means clustering on patent abstracts.

# Evidence / File Paths
- [patents.py](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/api/v1/endpoints/patents.py)
- [patent_intelligence.py](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/api/v1/endpoints/patent_intelligence.py)
- [patent_landscape_service.py](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/services/patent_landscape_service.py)
- [patent_providers.py](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/services/providers/patent_providers.py)
- [patents/page.tsx](file:///d:/Infosys%207.0/Intelligent-Research1/frontend/src/app/(dashboard)/patents/page.tsx)
