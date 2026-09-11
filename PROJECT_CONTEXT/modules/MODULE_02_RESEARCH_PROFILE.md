# MODULE_02_RESEARCH_PROFILE.md — Research Profile Management

# Objective
Enable comprehensive researcher identity and academic track-record management, allowing users to define scientific domains, weighted research interests, indexable keywords, technology areas, academic qualifications, research project histories, and bookmarked publications and patents.

# Official Requirements
- Research profile creation
- Research interest management
- Publication management
- Academic profile tracking
- Research history management
- Profile Information: Research Domains, Keywords, Publications, Patents, Technology Areas, Organization Information

# Mentor Requirements
- Enforce complete user isolation (users can only edit their own profile).
- Support standardized scientific domain selection from database taxonomy.
- Add designation field to meet institutional profile standards.
- Restrict phone number updates to valid formats.

# Current Implementation
- Complete extended profile CRUD with 8 distinct facets.
- Standardized taxonomy of 8 research domains loaded into PostgreSQL (`research_domains`).
- Many-to-many junction tables for profile domains (`profile_domains`), publications (`profile_publications`), and patents (`profile_patents`).
- One-to-many child tables for `academic_histories`, `research_histories`, `research_interests`, `profile_keywords`, and `technology_areas`.

# Frontend
- Route: `/profile` in `frontend/src/app/(dashboard)/profile/page.tsx`.
- Multi-tab management interface:
  - Personal Information & Bio
  - Research Domains & Taxonomy Badges
  - Research Interests & Priority Sliders
  - Search Keywords Tags Input
  - Technology Areas Specializations
  - Academic Qualifications History
  - Research Projects History

# Backend
- Router: `backend/app/api/v1/endpoints/profile.py`
- Service: `backend/app/services/profile_service.py`
- Schemas: `backend/app/schemas/profile.py`

# Database
- Models: `Profile`, `ResearchDomain`, `ResearchInterest`, `ProfileKeyword`, `TechnologyArea`, `AcademicHistory`, `ResearchHistory`.
- Migrations: `68afbe48340e`, `53d7c57aa26c`, `626ab1f43993`, and `244ef6c34a82` (added designation).

# APIs
- `GET /api/v1/profile/domains` (Standardized domain taxonomy list)
- `GET /api/v1/profile/me` (Full current user extended profile)
- `PUT /api/v1/profile/me` (Update extended profile and facets)
- `GET /api/v1/profile/{user_id}` (Public profile retrieval)

# AI/ML
- None (Taxonomy and data storage).

# External Data Sources
- None currently active; ORCID iD field stored as string.

# Integration With Other Modules
- User domains and keywords directly feed Module 4 (`FundingRecommendationService`) to generate personalized grant matches.
- User profile ID feeds Module 7 (`InnovationScoringService`) to personalize novelty and maturity scores.
- Publication and patent bookmarks link directly to Modules 3 and 5.

# Testing
- `backend/tests/test_profile.py` (8 passing tests).
- `backend/tests/test_profile_extended.py` (10 passing tests).
- `frontend/src/lib/user_profile.test.ts` (3 passing tests).

# Known Issues
- ORCID public API synchronization is not automated; users manually type their ORCID identifier string.

# Missing Requirements
- Automatic bibliographic synchronization via live ORCID REST API.

# Next Steps
- Implement background sync worker to fetch works automatically from `https://pub.orcid.org/v3.0/`.

# Evidence / File Paths
- [profile.py](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/api/v1/endpoints/profile.py)
- [profile_service.py](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/services/profile_service.py)
- [profile.py (models)](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/models/profile.py)
- [profile/page.tsx](file:///d:/Infosys%207.0/Intelligent-Research1/frontend/src/app/(dashboard)/profile/page.tsx)
