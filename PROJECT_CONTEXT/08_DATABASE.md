# 08_DATABASE.md — Database Architecture & Schema Reference

## 1. Database Architecture & Technology

- **RDBMS Engine:** PostgreSQL 16-alpine (Containerized in Docker as `research_intel_postgres`, port 5432).
- **ORM:** SQLAlchemy 2.0 Async ORM with `asyncpg` driver.
- **Migration Manager:** Alembic (6 applied asynchronous migration versions).
- **Active Connection URL:** `postgresql+asyncpg://postgres:postgres@localhost:5432/research_intel_db`
- **Testing In-Memory DB:** `sqlite+aiosqlite:///:memory:` (used in automated Pytest suite for zero-latency, isolated testing).

---

## 2. Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    users ||--o| profiles : "has one"
    users ||--o{ refresh_tokens : "owns"
    users ||--o{ funding_opportunities : "creates"

    profiles ||--o{ profile_domains : "tags"
    profiles ||--o{ research_interests : "defines"
    profiles ||--o{ profile_keywords : "lists"
    profiles ||--o{ technology_areas : "specializes"
    profiles ||--o{ academic_histories : "holds"
    profiles ||--o{ research_histories : "conducts"
    profiles ||--o{ profile_publications : "bookmarks"
    profiles ||--o{ profile_patents : "bookmarks"

    research_domains ||--o{ profile_domains : "tagged in"
    research_domains ||--o{ funding_opportunity_domains : "categorizes"

    publications ||--o{ profile_publications : "referenced by"
    publications ||--o{ publication_keywords : "has"

    patents ||--o{ profile_patents : "referenced by"

    funding_opportunities ||--o{ funding_opportunity_domains : "associated with"
    funding_opportunities ||--o{ funding_keywords : "tagged with"
```

---

## 3. Detailed Table Schema Inventory

### 1. `users`
- **Purpose:** Core user account authentication, credentials, and RBAC roles.
- **Columns:**
  - `id` (Integer, PK, autoincrement)
  - `email` (String(255), Unique, Indexed, Not Null)
  - `hashed_password` (String(255), Not Null)
  - `full_name` (String(255), Not Null)
  - `phone` (String(50), Nullable)
  - `role` (Enum `UserRole`: `researcher`, `startup_founder`, `innovation_manager`, `administrator`, Default: `researcher`)
  - `is_active` (Boolean, Default: True)
  - `is_superuser` (Boolean, Default: False)
  - `created_at`, `updated_at` (DateTime with timezone)
- **Relationships:** `profile`, `refresh_tokens`, `funding_opportunities`

### 2. `profiles`
- **Purpose:** Extended researcher and institutional profile information.
- **Columns:**
  - `id` (Integer, PK)
  - `user_id` (Integer, FK -> `users.id`, Unique, Not Null)
  - `institution`, `department`, `designation`, `country` (String(255))
  - `bio` (Text)
  - `orcid_id` (String(50))
  - `website` (String(255))
  - `created_at`, `updated_at` (DateTime with timezone)
- **Relationships:** `domains`, `interests`, `keywords`, `technology_areas`, `academic_histories`, `research_histories`, `publications`, `patents`

### 3. `refresh_tokens`
- **Purpose:** Cryptographically secure refresh token rotation and revocation tracking.
- **Columns:**
  - `id` (Integer, PK)
  - `user_id` (Integer, FK -> `users.id`, Not Null)
  - `token_hash` (String(64), SHA-256 hash, Unique, Indexed, Not Null)
  - `issued_at`, `expires_at` (DateTime with timezone, Not Null)
  - `revoked_at` (DateTime with timezone, Nullable)
  - `is_revoked` (Boolean, Default: False)
  - `replaced_by_token_hash` (String(64), Nullable)

### 4. `research_domains`
- **Purpose:** Standardized taxonomy of scientific and innovation disciplines.
- **Columns:**
  - `id` (Integer, PK)
  - `name` (String(150), Unique, Not Null)
  - `description` (Text, Nullable)

### 5. `profile_domains` (Junction Table)
- **Purpose:** Many-to-many association linking profiles to research domains.
- **Columns:**
  - `profile_id` (Integer, FK -> `profiles.id`, PK)
  - `domain_id` (Integer, FK -> `research_domains.id`, PK)

### 6. `research_interests`
- **Purpose:** Granular research topics and priority weights defined by a user.
- **Columns:**
  - `id` (Integer, PK)
  - `profile_id` (Integer, FK -> `profiles.id`, Not Null)
  - `title` (String(255), Not Null)
  - `description` (Text, Nullable)
  - `importance_level` (Integer, Default: 1)

### 7. `profile_keywords`
- **Purpose:** Indexable search keywords associated with a user profile.
- **Columns:**
  - `id` (Integer, PK)
  - `profile_id` (Integer, FK -> `profiles.id`, Not Null)
  - `keyword` (String(100), Not Null)

### 8. `technology_areas`
- **Purpose:** Technical areas of focus for startup founders and innovation managers.
- **Columns:**
  - `id` (Integer, PK)
  - `profile_id` (Integer, FK -> `profiles.id`, Not Null)
  - `name` (String(150), Not Null)
  - `description` (Text, Nullable)

### 9. `academic_histories`
- **Purpose:** Academic education qualifications tracking.
- **Columns:**
  - `id` (Integer, PK)
  - `profile_id` (Integer, FK -> `profiles.id`, Not Null)
  - `degree`, `field_of_study`, `institution` (String(255), Not Null)
  - `start_year`, `end_year` (Integer, Nullable)

### 10. `research_histories`
- **Purpose:** Prior research projects, lab positions, and grant track records.
- **Columns:**
  - `id` (Integer, PK)
  - `profile_id` (Integer, FK -> `profiles.id`, Not Null)
  - `project_title`, `role`, `organization` (String(255), Not Null)
  - `start_date`, `end_date` (Date, Nullable)
  - `description` (Text, Nullable)

### 11. `publications`
- **Purpose:** Scientific research papers, conference proceedings, and literature.
- **Columns:**
  - `id` (Integer, PK)
  - `title` (String(500), Not Null)
  - `authors` (Text, Not Null)
  - `abstract` (Text, Nullable)
  - `publication_date` (Date, Nullable)
  - `venue` (String(255), Nullable)
  - `doi` (String(255), Unique, Indexed, Nullable)
  - `citation_count` (Integer, Default: 0)
  - `primary_domain` (String(150), Nullable)
  - `source` (String(50), e.g., `openalex`, `crossref`, `semanticscholar`, `mock`)
  - `external_id` (String(150), Nullable)
  - `url` (String(500), Nullable)
  - `created_at`, `updated_at` (DateTime with timezone)

### 12. `profile_publications` (Junction Table)
- **Purpose:** Bookmarking and author association between profiles and publications.
- **Columns:**
  - `profile_id` (Integer, FK -> `profiles.id`, PK)
  - `publication_id` (Integer, FK -> `publications.id`, PK)
  - `is_primary_author` (Boolean, Default: False)
  - `created_at` (DateTime with timezone)

### 13. `publication_keywords`
- **Purpose:** Specific keywords and subject tags extracted from publications.
- **Columns:**
  - `id` (Integer, PK)
  - `publication_id` (Integer, FK -> `publications.id`, Not Null)
  - `keyword` (String(100), Not Null)

### 14. `patents`
- **Purpose:** Intellectual property patents and published applications.
- **Columns:**
  - `id` (Integer, PK)
  - `patent_number` (String(100), Unique, Indexed, Not Null)
  - `title` (String(500), Not Null)
  - `abstract` (Text, Nullable)
  - `assignee` (String(255), Nullable)
  - `inventors` (Text, Nullable)
  - `filing_date`, `publication_date` (Date, Nullable)
  - `patent_classification` (String(100), Nullable)
  - `technology_domain` (String(150), Nullable)
  - `citation_count` (Integer, Default: 0)
  - `source` (String(50), e.g., `uspto`, `google_patents`, `mock`)
  - `external_id` (String(150), Nullable)
  - `url` (String(500), Nullable)
  - `created_at`, `updated_at` (DateTime with timezone)

### 15. `profile_patents` (Junction Table)
- **Purpose:** Many-to-many bookmarks connecting user profiles to patents.
- **Columns:**
  - `profile_id` (Integer, FK -> `profiles.id`, PK)
  - `patent_id` (Integer, FK -> `patents.id`, PK)
  - `created_at` (DateTime with timezone)

### 16. `funding_opportunities`
- **Purpose:** Grant solicitations, innovation fund awards, and RFP opportunities.
- **Columns:**
  - `id` (Integer, PK)
  - `title` (String(500), Not Null)
  - `funding_agency` (String(255), Not Null)
  - `funding_program` (String(255), Nullable)
  - `description` (Text, Nullable)
  - `funding_amount` (Numeric(15, 2), Nullable)
  - `currency` (String(10), Default: "USD")
  - `application_deadline` (DateTime with timezone, Nullable)
  - `opportunity_type` (String(100), Nullable)
  - `eligibility_summary` (Text, Nullable)
  - `eligible_institutions` (String(255), Nullable)
  - `geographic_restrictions` (String(255), Nullable)
  - `status` (String(50), Default: "open")
  - `source` (String(50), e.g., `grants_gov`, `nsf`, `mock`)
  - `external_id` (String(150), Nullable)
  - `url` (String(500), Nullable)
  - `created_by_user_id` (Integer, FK -> `users.id`, Nullable)
  - `created_at`, `updated_at` (DateTime with timezone)

### 17. `funding_opportunity_domains` & `funding_keywords`
- **Purpose:** Junction tables indexing funding opportunities by research domain and keyword tags.

---

## 4. Tables Not Yet Implemented

> [!NOTE]
> **NOTIFICATION SYSTEM PERSISTENCE:**  
> The `notifications` table (for Module 10) does **NOT** exist in the current database schema. In-app alerts are currently rendered dynamically from recent activity feeds and upcoming grant deadlines. An Alembic migration for `notifications` is queued as P1 work.
