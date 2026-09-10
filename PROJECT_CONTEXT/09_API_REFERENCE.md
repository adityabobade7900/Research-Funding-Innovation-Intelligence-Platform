# 09_API_REFERENCE.md — Complete REST API Reference (82 Routes)

> **BASE URL:** `http://localhost:8000/api/v1`  
> **AUTHENTICATION:** Bearer token (`Authorization: Bearer <access_token>`)

---

## 1. Authentication & Security APIs (`/api/v1/auth`)

| Method | Path | Auth Req? | Role Req? | Parameters / Body | Response Model | Purpose | Status |
| :---: | :--- | :---: | :---: | :--- | :--- | :--- | :---: |
| `POST` | `/auth/register` | No | None | Body: `UserRegister` (email, password, full_name, role, phone) | `UserRead` (HTTP 201) | Registers a new user (Admin role forbidden) | 🟢 Implemented |
| `POST` | `/auth/login` | No | None | Body: `UserLogin` (email, password) | `TokenResponse` (access & refresh tokens) | Standard JSON login | 🟢 Implemented |
| `POST` | `/auth/login/form` | No | None | Form: `username`, `password` | `TokenResponse` | OAuth2 password bearer form login | 🟢 Implemented |
| `POST` | `/auth/refresh` | No | None | Body: `TokenRefreshRequest` (refresh_token) | `TokenResponse` | Rotates refresh token & issues new access token | 🟢 Implemented |
| `POST` | `/auth/logout` | Yes | Active User | Body: `TokenRefreshRequest` (refresh_token) | `{message: "Successfully logged out"}` | Revokes refresh token in database | 🟢 Implemented |
| `GET` | `/auth/me` | Yes | Active User | None | `UserRead` | Retrieves current authenticated user profile | 🟢 Implemented |
| `PUT` | `/auth/me` | Yes | Active User | Body: `UserUpdate` (full_name, phone) | `UserRead` | Updates authenticated user's account details | 🟢 Implemented |
| `GET` | `/auth/test/researcher-only` | Yes | `researcher` | None | `{status: "ok"}` | Validates RBAC researcher guard | 🟢 Implemented |
| `GET` | `/auth/test/founder-only` | Yes | `startup_founder` | None | `{status: "ok"}` | Validates RBAC founder guard | 🟢 Implemented |
| `GET` | `/auth/test/manager-only` | Yes | `innovation_manager` | None | `{status: "ok"}` | Validates RBAC manager guard | 🟢 Implemented |
| `GET` | `/auth/test/admin-only` | Yes | `administrator` | None | `{status: "ok"}` | Validates RBAC admin guard | 🟢 Implemented |

---

## 2. Profile Management APIs (`/api/v1/profile`)

| Method | Path | Auth Req? | Role Req? | Parameters / Body | Response Model | Purpose | Status |
| :---: | :--- | :---: | :---: | :--- | :--- | :--- | :---: |
| `GET` | `/profile/domains` | No | None | Query: `limit`, `offset` | `List[ResearchDomainRead]` | Returns standardized research taxonomy domains | 🟢 Implemented |
| `GET` | `/profile/me` | Yes | Active User | None | `ExtendedProfileRead` | Gets current user's full profile & 8 facets | 🟢 Implemented |
| `PUT` | `/profile/me` | Yes | Active User | Body: `ExtendedProfileUpdate` | `ExtendedProfileRead` | Updates user's bio, interests, domains, history | 🟢 Implemented |
| `GET` | `/profile/{user_id}` | Yes | Active User | Path: `user_id` | `ExtendedProfileRead` | Fetches public profile of another researcher | 🟢 Implemented |

---

## 3. Publication & Literature APIs (`/api/v1/publications`)

| Method | Path | Auth Req? | Role Req? | Parameters / Body | Response Model | Purpose | Status |
| :---: | :--- | :---: | :---: | :--- | :--- | :--- | :---: |
| `GET` | `/publications` | No | None | Query: `search`, `domain`, `year`, `limit`, `offset` | `PublicationListResponse` | Searches and filters indexed publications | 🟢 Implemented |
| `POST` | `/publications` | Yes | Active User | Body: `PublicationCreate` | `PublicationRead` (HTTP 201) | Manually creates a new publication | 🟢 Implemented |
| `POST` | `/publications/ingest` | Yes | Active User | Body: `PublicationIngestRequest` (doi, provider) | `PublicationRead` | Ingests publication via OpenAlex/Crossref | 🟢 Implemented |
| `GET` | `/publications/my` | Yes | Active User | Query: `limit`, `offset` | `PublicationListResponse` | Retrieves publications bookmarked by current user | 🟢 Implemented |
| `GET` | `/publications/{id}` | No | None | Path: `id` | `PublicationRead` | Gets deep-dive paper metadata and abstract | 🟢 Implemented |
| `PUT` | `/publications/{id}` | Yes | Active User | Path: `id`, Body: `PublicationUpdate` | `PublicationRead` | Updates publication metadata | 🟢 Implemented |
| `DELETE`| `/publications/{id}` | Yes | Active User / Admin | Path: `id` | `{message: "Publication deleted"}` | Deletes publication record | 🟢 Implemented |

---

## 4. Research Intelligence & Trends APIs (`/api/v1/research-intelligence`)

| Method | Path | Auth Req? | Role Req? | Parameters / Body | Response Model | Purpose | Status |
| :---: | :--- | :---: | :---: | :--- | :--- | :--- | :---: |
| `GET` | `/research-intelligence/trends/publications` | No | None | Query: `start_year`, `end_year`, `domain`, `keyword` | `PublicationTrendsResponse` | Temporal publication volume & YoY growth | 🟢 Implemented |
| `GET` | `/research-intelligence/trends/domains` | No | None | Query: `start_year`, `end_year`, `limit` | `DomainTrendsResponse` | Domain growth curves over time | 🟢 Implemented |
| `GET` | `/research-intelligence/trends/keywords` | No | None | Query: `start_year`, `end_year`, `domain`, `limit` | `KeywordTrendsResponse` | Keyword co-occurrence & velocity trends | 🟢 Implemented |
| `GET` | `/research-intelligence/trends/citations` | No | None | Query: `domain`, `year` | `CitationStatisticsResponse` | Citation averages, medians, and top cited works | 🟢 Implemented |
| `GET` | `/research-intelligence/emerging-topics` | No | None | Query: `time_window`, `limit` | `EmergingTopicsResponse` | Detects emerging terms by acceleration velocity | 🟢 Implemented |
| `GET` | `/research-intelligence/hotspots` | No | None | Query: `domain`, `limit` | `ResearchHotspotsResponse` | Multi-signal composite research hotspot scoring | 🟢 Implemented |

---

## 5. Funding Intelligence APIs (`/api/v1/funding`)

| Method | Path | Auth Req? | Role Req? | Parameters / Body | Response Model | Purpose | Status |
| :---: | :--- | :---: | :---: | :--- | :--- | :--- | :---: |
| `GET` | `/funding` | No | None | Query: `search`, `agency`, `status`, `domain`, `limit` | `FundingOpportunityListResponse` | Searches and filters grant opportunities | 🟢 Implemented |
| `POST` | `/funding` | Yes | Active User | Body: `FundingOpportunityCreate` | `FundingOpportunityRead` (HTTP 201)| Manually creates a funding opportunity | 🟢 Implemented |
| `POST` | `/funding/ingest` | Yes | Active User | Body: `FundingIngestRequest` (agency, provider) | `FundingIngestResponse` | Ingests grants from Grants.gov / NSF | 🟢 Implemented |
| `GET` | `/funding/recommendations` | Yes | Active User | Query: `limit`, `min_score` | `FundingRecommendationsResponse` | Personalized grant matching based on user profile | 🟢 Implemented |
| `GET` | `/funding/{id}` | No | None | Path: `id` | `FundingOpportunityRead` | Retrieves grant details and deadline information | 🟢 Implemented |
| `PUT` | `/funding/{id}` | Yes | Active User | Path: `id`, Body: `FundingOpportunityUpdate` | `FundingOpportunityRead` | Updates funding opportunity | 🟢 Implemented |
| `DELETE`| `/funding/{id}` | Yes | Active User / Admin | Path: `id` | `{message: "Opportunity deleted"}` | Deletes funding opportunity | 🟢 Implemented |
| `GET` | `/funding/{id}/eligibility` | Yes | Active User | Path: `id` | `EligibilityResponse` | Checks user eligibility for a specific grant | 🟢 Implemented |

---

## 6. Patent Portfolio & Landscape APIs (`/api/v1/patents` & `/api/v1/patent-intelligence`)

| Method | Path | Auth Req? | Role Req? | Parameters / Body | Response Model | Purpose | Status |
| :---: | :--- | :---: | :---: | :--- | :--- | :--- | :---: |
| `GET` | `/patents` | No | None | Query: `search`, `classification`, `domain`, `assignee` | `PatentListResponse` | Searches and filters patent portfolio | 🟢 Implemented |
| `POST` | `/patents` | Yes | Active User | Body: `PatentCreate` | `PatentRead` (HTTP 201) | Registers a new patent in system | 🟢 Implemented |
| `POST` | `/patents/ingest` | Yes | Active User | Body: `PatentIngestRequest` (patent_number) | `PatentRead` | Ingests patent via Google Patents / USPTO | 🟢 Implemented |
| `GET` | `/patents/my` | Yes | Active User | Query: `limit`, `offset` | `PatentListResponse` | Lists patents bookmarked by current user | 🟢 Implemented |
| `GET` | `/patents/{id}` | No | None | Path: `id` | `PatentRead` | Gets individual patent details | 🟢 Implemented |
| `PUT` | `/patents/{id}` | Yes | Active User | Path: `id`, Body: `PatentUpdate` | `PatentRead` | Updates patent record | 🟢 Implemented |
| `DELETE`| `/patents/{id}` | Yes | Active User / Admin | Path: `id` | `{message: "Patent deleted"}` | Deletes patent record | 🟢 Implemented |
| `GET` | `/patent-intelligence/landscape` | No | None | Query: `domain`, `assignee`, `jurisdiction`, `start_year` | `PatentLandscapeSummary` | High-level patent landscape summary & counts | 🟢 Implemented |
| `GET` | `/patent-intelligence/trends` | No | None | Query: `domain`, `start_year`, `end_year` | `PatentTrendsResponse` | Patent filing volume and growth over time | 🟢 Implemented |
| `GET` | `/patent-intelligence/technology-domains`| No | None | Query: `limit`, `start_year` | `TechnologyDomainsResponse` | Technology domain distribution across patents | 🟢 Implemented |
| `GET` | `/patent-intelligence/assignees` | No | None | Query: `domain`, `limit` | `AssigneesResponse` | Assignee rankings & Herfindahl-Hirschman Index | 🟢 Implemented |
| `GET` | `/patent-intelligence/jurisdictions` | No | None | Query: `domain`, `assignee` | `JurisdictionsResponse` | Patent jurisdiction distribution (US, EP, CN, WO) | 🟢 Implemented |
| `GET` | `/patent-intelligence/status` | No | None | Query: `domain` | `PatentStatusResponse` | Active vs pending vs expired patent status | 🟢 Implemented |
| `GET` | `/patent-intelligence/competitive-landscape`| No | None | Query: `domain`, `limit` | `CompetitiveLandscapeResponse` | Composite Competitive Index & competitor classes | 🟢 Implemented |

---

## 7. Technology Intelligence & Whitespace APIs (`/api/v1/technology-intelligence`)

| Method | Path | Auth Req? | Role Req? | Parameters / Body | Response Model | Purpose | Status |
| :---: | :--- | :---: | :---: | :--- | :--- | :--- | :---: |
| `GET` | `/technology-intelligence/summary` | No | None | Query: `domain` | `TechnologyIntelligenceSummary` | Summary metrics of patenting activity & whitespace | 🟢 Implemented |
| `GET` | `/technology-intelligence/activity` | No | None | Query: `domain`, `start_year` | `TechnologyActivityResponse` | Annual patent volume across technology sectors | 🟢 Implemented |
| `GET` | `/technology-intelligence/growth` | No | None | Query: `limit` | `TechnologyGrowthResponse` | Multi-year CAGR and technology velocity ranking | 🟢 Implemented |
| `GET` | `/technology-intelligence/coverage` | No | None | Query: `domain` | `TechnologyCoverageResponse` | IPC classification coverage density | 🟢 Implemented |
| `GET` | `/technology-intelligence/whitespace` | No | None | Query: `threshold`, `limit` | `WhitespaceDiscoveryResponse` | Discovers unpatented whitespace innovation niches | 🟢 Implemented |

---

## 8. Innovation Scoring & TRL Engine APIs (`/api/v1/innovation-scoring`)

| Method | Path | Auth Req? | Role Req? | Parameters / Body | Response Model | Purpose | Status |
| :---: | :--- | :---: | :---: | :--- | :--- | :--- | :---: |
| `GET` | `/innovation-scoring/score` | No | None | Query: `domain`, `profile_id` | `InnovationScoreResponse` | Exact 5-pillar mathematical innovation score | 🟢 Implemented |
| `GET` | `/innovation-scoring/trl` | No | None | Query: `domain`, `profile_id` | `TRLEstimationItem` | NASA/DoD standard TRL 1–9 estimation | 🟢 Implemented |
| `GET` | `/innovation-scoring/evidence` | No | None | Query: `domain`, `profile_id` | `List[PillarScoreItem]` | Evidence dossier explaining each pillar score | 🟢 Implemented |
| `GET` | `/innovation-scoring/summary` | No | None | None | `InnovationScoringSummary` | Platform-wide benchmark distribution | 🟢 Implemented |

---

## 9. Commercialization Recommendation APIs (`/api/v1/commercialization`)

| Method | Path | Auth Req? | Role Req? | Parameters / Body | Response Model | Purpose | Status |
| :---: | :--- | :---: | :---: | :--- | :--- | :--- | :---: |
| `GET` | `/commercialization/summary` | No | None | Query: `domain` | `CommercializationSummary` | Overview of readiness and commercial pathways | 🟢 Implemented |
| `GET` | `/commercialization/readiness` | No | None | Query: `domain`, `profile_id` | `CommercialReadinessResponse` | Evaluates 4 dimensions (IP, Market, Reg, Team) | 🟢 Implemented |
| `GET` | `/commercialization/recommendations`| No | None | Query: `domain`, `profile_id` | `List[StrategicPathwayItem]` | Strategic pathway: Licensing, Spinout, Joint Dev | 🟢 Implemented |
| `GET` | `/commercialization/evidence` | No | None | Query: `domain` | `CommercialEvidenceResponse` | Supporting metrics and actionable roadmap steps | 🟢 Implemented |

---

## 10. Dashboard, Reports & Admin Governance APIs

| Method | Path | Auth Req? | Role Req? | Parameters / Body | Response Model | Purpose | Status |
| :---: | :--- | :---: | :---: | :--- | :--- | :--- | :---: |
| `GET` | `/command-center/overview` | Yes | Active User | None | `CommandCenterOverview` | Role-tailored operational KPIs and summaries | 🟢 Implemented |
| `GET` | `/command-center/activity-feed` | Yes | Active User | Query: `limit` | `ActivityFeedResponse` | Multi-source event stream & 30-day grant alerts | 🟢 Implemented |
| `GET` | `/reports/summary` | No | None | Query: `domain` | `ExecutiveReportSummary` | High-level summary of report metrics | 🟢 Implemented |
| `GET` | `/reports/dossier` | No | None | Query: `domain` | `ExecutiveDossierResponse` | Comprehensive strategic intelligence dossier | 🟢 Implemented |
| `GET` | `/reports/export/markdown` | No | None | Query: `domain` | Streaming File (`.md`) | Direct file download of formatted Markdown report | 🟢 Implemented |
| `GET` | `/reports/export/json` | No | None | Query: `domain` | Streaming File (`.json`)| Direct file download of raw JSON intelligence | 🟢 Implemented |
| `GET` | `/admin/system/overview` | Yes | `administrator` | None | `SystemOverviewResponse` | Platform health, DB connection, entity counts | 🟢 Implemented |
| `GET` | `/admin/telemetry/pipelines` | Yes | `administrator` | None | `PipelineTelemetryResponse` | Status of OpenAlex, Grants.gov, USPTO harvesters | 🟢 Implemented |
| `GET` | `/admin/users` | Yes | `administrator` | Query: `limit`, `offset` | `UserListResponse` | Lists all platform users with role and status | 🟢 Implemented |
| `GET` | `/admin/users/{id}` | Yes | `administrator` | Path: `id` | `UserDetailResponse` | Inspects full user record and activity | 🟢 Implemented |
| `PUT` | `/admin/users/{id}/role` | Yes | `administrator` | Path: `id`, Body: `RoleUpdate` | `UserRead` | Changes user role (`researcher`, `founder`, etc.) | 🟢 Implemented |
| `PUT` | `/admin/users/{id}/status` | Yes | `administrator` | Path: `id`, Body: `StatusUpdate` | `UserRead` | Activates or deactivates user account | 🟢 Implemented |
| `GET` | `/admin/audit-logs` | Yes | `administrator` | Query: `limit` | `AuditLogResponse` | Security audit trail of sensitive operations | 🟢 Implemented |
| `GET` | `/health` | No | None | None | `{status: "healthy", database: "connected"}` | Basic health and database ping check | 🟢 Implemented |
