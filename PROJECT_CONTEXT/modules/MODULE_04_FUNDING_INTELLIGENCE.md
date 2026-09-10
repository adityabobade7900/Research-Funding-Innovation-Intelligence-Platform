# MODULE_04_FUNDING_INTELLIGENCE.md — Funding Intelligence & Opportunity Analysis

> **NUMBERING CLARIFICATION:**  
> • Designated as **Module 4** in Mentor Communications.  
> • Designated as **Module 3** in the Official Specification PDF.

# Objective
Automate grant and funding opportunity discovery, external solicitation harvesting (Grants.gov, NSF), rule-based eligibility evaluation, personalized grant recommendation ranking, and upcoming deadline tracking.

# Official Requirements (Module 3 in PDF)
- Funding opportunity collection
- Funding recommendation engine
- Eligibility matching
- Grant search
- Funding alerts
- Funding Sources: Government Grants, Research Councils, Innovation Funds, Startup Accelerators

# Mentor Requirements (Module 4 in Mentor Specs)
- Funding Intelligence Dashboard with funding pool metrics and agency breakdown.
- Funding search and details view with application deadline countdown.
- Personalized funding recommendations based on user research profile.
- Eligibility analysis evaluating institution and geographic constraints.
- Deadline tracking and saved funding watchlist.
- Multi-source ingestion support (Grants.gov, NSF, mock fallbacks).

# Current Implementation
- Full funding opportunity search catalog with agency, status, and domain filtering.
- Recommendation algorithm (`FundingRecommendationService`) calculating match scores (0–100%) against user profile domains and keywords.
- Eligibility engine (`EligibilityMatcher`) checking institutional type and country restrictions.
- In-app 30-day deadline alerts rendered on `/dashboard`.
- Multi-provider adapter in `backend/app/services/providers/funding_providers.py` (Grants.gov, NSF, Mock).

# Frontend
- Route: `/funding` in `frontend/src/app/(dashboard)/funding/page.tsx` (Opportunities catalog, Recommended tab, Eligibility modal, Ingestion modal).

# Backend
- Router: `backend/app/api/v1/endpoints/funding.py`
- Services: `backend/app/services/funding_service.py`, `funding_recommendation_service.py`, `eligibility_matcher.py`, `funding_ingest_service.py`
- Providers: `backend/app/services/providers/funding_providers.py`

# Database
- Models: `FundingOpportunity`, `FundingKeyword`, and `funding_opportunity_domains`.
- Persistent Reality: Currently **0 persistent rows** in PostgreSQL. Fallback fixtures (`SAMPLE_FUNDING_OPPORTUNITIES`) power development and testing seamlessly.
- Migration: `f8e9f392e6c3`.

# APIs
- `GET /api/v1/funding` & `POST /api/v1/funding`
- `POST /api/v1/funding/ingest` (Triggers Grants.gov/NSF/Mock harvest)
- `GET /api/v1/funding/recommendations` (Personalized grant matches)
- `GET /api/v1/funding/{id}` (Grant details)
- `GET /api/v1/funding/{id}/eligibility` (Eligibility check)
- `PUT /api/v1/funding/{id}` & `DELETE /api/v1/funding/{id}`

# AI/ML
- **Current Reality:** Rule-based keyword overlap and token intersection heuristics.
- **Not Real AI:** Dense vector embedding similarity is **PLANNED**, not currently executing.

# External Data Sources
- Grants.gov API / public search
- NSF Awards Search REST API
- Built-in offline mock grant fixtures

# Integration With Other Modules
- User profile (Module 2) provides domains and keywords for recommendation matching.
- Active grant pool metrics feed Module 7 (`InnovationScoringService`, 15% weight).
- Commercialization grants feed Module 8 (SBIR/STTR spinout pathways).

# Testing
- `backend/tests/test_funding.py` (10 passing tests).
- `backend/tests/test_funding_recommendations.py` (8 passing tests).
- `backend/tests/test_funding_eligibility.py` (8 passing tests).
- `backend/tests/test_funding_ingest.py` (6 passing tests).
- `backend/tests/test_funding_providers.py` (6 passing tests).
- `frontend/src/lib/funding.test.ts` (3 passing tests).

# Known Issues
- Database currently contains 0 persistent grant rows (handled via mock fixtures).
- Saved funding watchlist table (`ProfileFunding`) is not yet created in PostgreSQL.

# Missing Requirements
- Junction table and API endpoint for users to bookmark grants into a personal watchlist.
- Live periodic cron harvester polling Grants.gov weekly.

# Next Steps
- Implement `POST /api/v1/funding/{id}/save` watchlist endpoint.
- Seed PostgreSQL database with 50+ real federal grants via `POST /api/v1/funding/ingest`.

# Evidence / File Paths
- [funding.py](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/api/v1/endpoints/funding.py)
- [funding_service.py](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/services/funding_service.py)
- [funding_recommendation_service.py](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/services/funding_recommendation_service.py)
- [eligibility_matcher.py](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/services/eligibility_matcher.py)
- [funding/page.tsx](file:///d:/Infosys%207.0/Intelligent-Research1/frontend/src/app/(dashboard)/funding/page.tsx)
