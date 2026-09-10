# checkpoints/LAST_WORKING_STATE.md — Last Verified Working State

---

## 1. Verified Baseline Functionality

The following platform features are verified to work end-to-end between the FastAPI backend and Next.js frontend:

1. **Authentication & RBAC:**
   - Public registration strictly allows `researcher`, `startup_founder`, and `innovation_manager`.
   - Administrator self-registration is blocked with HTTP 403.
   - Admin accounts provisioned via `backend/scripts/create_admin.py`.
   - Login generates signed JWT access token and cryptographic refresh token.
   - Refresh token rotation verifies and revokes old tokens.
   - Protected routes enforce role claims via `require_roles`.

2. **Research Profile Management:**
   - Full 8-facet extended profile CRUD (`domains`, `interests`, `keywords`, `technology_areas`, `academic_history`, `research_history`, `publications`, `patents`).
   - Profile isolation ensures users only modify their own profile records.

3. **Research Trends & Intelligence:**
   - Publication search catalog with multi-provider ingest (OpenAlex, Crossref, Semantic Scholar).
   - YoY publication velocity calculations and domain growth trajectories.
   - Citation statistics (averages, medians, top-cited papers).
   - Emerging topic acceleration rankings.
   - Composite research hotspot scoring.

4. **Funding Intelligence:**
   - Grant search catalog with agency, status, and domain filtering.
   - Personalized recommendation ranking based on researcher profile match.
   - Rule-based eligibility checking against institutional and geographic constraints.
   - 30-day grant deadline alerts on Command Center.

5. **Patent Landscape Analysis:**
   - Patent catalog with IPC classification and domain filtering.
   - Interactive modal for patent editing and registration.
   - Herfindahl-Hirschman Index (HHI) measuring assignee market concentration.
   - Composite Competitive Index classifying assignees into dominant versus emerging players.
   - Global jurisdiction distribution analysis (USPTO, EPO, WIPO, CNIPA, IPO).

6. **Technology Intelligence & Whitespace:**
   - Technology sector CAGR velocity rankings.
   - IPC classification coverage density mapping.
   - Statistical whitespace detection identifying under-patented research domains.

7. **Innovation Scoring & TRL Engine:**
   - Exact 5-pillar mathematical formula: Novelty (30%), Patent (20%), Maturity (15%), Market (20%), Funding (15%).
   - NASA/DoD standard TRL 1–9 rule-based state estimation.
   - Granular evidence dossier explaining each pillar score.

8. **Commercialization Recommendations:**
   - Evaluation of 4 commercial readiness dimensions (IP, Market, Regulatory, Team).
   - Strategic pathway classification (`LICENSING`, `SPINOUT_VENTURE`, `JOINT_DEVELOPMENT`).
   - Phased execution roadmaps.

9. **Dashboards & Executive Reports:**
   - Unified Command Center with role-specific KPIs and multi-source activity feed.
   - Admin governance dashboard with pipeline telemetry, audit logs, and user management.
   - Executive dossier synthesis with direct Markdown (`.md`) and JSON (`.json`) streaming downloads.

---

## 2. Test Verification Log

- **Pytest:** `150 passed in 41.2s`
- **Vitest:** `30 passed in 1.18s`
- **Next.js Build:** `18/18 static pages generated in 28.4s`
- **Docker Postgres:** Healthy on port 5432
