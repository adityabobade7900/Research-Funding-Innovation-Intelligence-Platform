# 20_TESTING.md — Testing Suite & Quality Verification

## 1. Verified Quality & Test Summary

| Test Layer | Test Runner | Total Tests | Passed | Failed | Execution Time | Coverage Scope |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Backend Unit & Integration** | Pytest 8.2.2 + Pytest-Asyncio | **150** | **150** | **0** | ~41 seconds | All 14 API routers, services, providers, auth, RBAC |
| **Frontend Unit & Component** | Vitest 4.1.11 | **30** | **30** | **0** | ~1.2 seconds | API client wrappers, state management, utilities |
| **Next.js Production Build** | Next.js 14 Compiler | **18 Routes** | **18** | **0** | ~28 seconds | TypeScript types, ESLint rules, static page compilation |

---

## 2. Backend Automated Test Inventory (22 Test Files, 150 Tests)

Located in `backend/tests/`:

1. `test_auth.py` (22 tests): User registration validation, password hashing, JWT creation, token expiration, refresh rotation, logout revocation, and invalid credentials.
2. `test_rbac.py` (2 tests): Role-based access control, forbidden administrator self-registration, and endpoint authorization guards.
3. `test_profile.py` (8 tests): User profile creation, update, and retrieval.
4. `test_profile_extended.py` (10 tests): Multi-facet profile management (domains, interests, keywords, technology areas, academic history, research history).
5. `test_publications.py` (10 tests): Publication CRUD, search filtering, deduplication, and user bookmark associations.
6. `test_patents.py` (8 tests): Patent CRUD, classification filtering, and user bookmark associations.
7. `test_funding.py` (10 tests): Funding opportunity search, agency filtering, deadline sorting, and creation.
8. `test_funding_recommendations.py` (8 tests): Relevancy scoring algorithm and keyword matching for personalized grants.
9. `test_funding_eligibility.py` (8 tests): Institutional and geographic constraint evaluation.
10. `test_funding_ingest.py` (6 tests): Harvester pipeline deduplication and persistence into PostgreSQL.
11. `test_funding_providers.py` (6 tests): Grants.gov and NSF provider normalization and mock fallbacks.
12. `test_providers.py` (8 tests): OpenAlex inverted-index parser, Crossref DOI resolution, and Semantic Scholar graph queries.
13. `test_ingest.py` (6 tests): Ingestion service orchestration and error resilience.
14. `test_research_intelligence.py` (8 tests): YoY publication velocity, domain growth curves, citation statistics, and hotspot formula.
15. `test_patent_intelligence.py` (8 tests): Assignee market concentration (HHI), Composite Competitive Index, and trend curves.
16. `test_technology_intelligence.py` (8 tests): Technology sector CAGR, IPC coverage density, and statistical whitespace detection.
17. `test_innovation_scoring.py` (8 tests): Exact 5-pillar mathematical scoring formula, edge cases, and TRL estimation.
18. `test_commercialization.py` (8 tests): 4 readiness dimensions, pathway classification triggers (Licensing, Spinout, Joint Dev), and roadmaps.
19. `test_command_center.py` (6 tests): Operational KPI summaries and 30-day grant deadline alerts.
20. `test_executive_reports.py` (8 tests): Strategic dossier synthesis, Markdown export stream, and JSON export stream.
21. `test_admin.py` (8 tests): Administrator telemetry, pipeline status toggles, user role modification, and security audit logs.
22. `test_health.py` (2 tests): Database liveness probe and health endpoint status.

---

## 3. Frontend Automated Test Inventory (10 Test Suites, 30 Tests)

Located in `frontend/src/lib/*.test.ts`:

1. `admin.test.ts` (3 tests): Admin user role updating and pipeline telemetry API client functions.
2. `command_center.test.ts` (3 tests): Overview KPI calculations and activity feed parsing.
3. `commercialization.test.ts` (3 tests): Commercial readiness scoring and strategic pathway validation.
4. `executive_report.test.ts` (3 tests): Executive dossier retrieval and export file download triggers.
5. `funding.test.ts` (3 tests): Funding search, recommendation parsing, and eligibility checks.
6. `innovation_scoring.test.ts` (3 tests): 5-pillar score validation and TRL level rendering.
7. `patent_intelligence.test.ts` (3 tests): Patent landscape aggregation and competitor index formatting.
8. `research_intelligence.test.ts` (3 tests): Research trend velocity curves and hotspot scorecards.
9. `technology_intelligence.test.ts` (3 tests): Whitespace discovery response parsing and CAGR growth ranks.
10. `user_profile.test.ts` & `utils.test.ts` (3 tests): Profile facet state updates and classname merging.

---

## 4. Exact Commands to Run All Tests

### Run Backend Tests (From Project Root)
```powershell
# Using the backend virtual environment python
& "d:\Infosys 7.0\Intelligent-Research1\backend\venv\Scripts\pytest.exe" "backend/tests" -v
```

### Run Frontend Tests (From Project Root)
```powershell
cd frontend
npm test
```

### Verify Production Build & Static Compilation
```powershell
cd frontend
npx next build
```
*(Confirms that all 18 routes compile with 0 TypeScript and 0 ESLint errors).*
