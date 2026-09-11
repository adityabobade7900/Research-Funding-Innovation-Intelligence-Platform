# database/TABLES.md — Relational Table Definitions & DDL Reference

---

## 1. Table Inventory Overview

| Table Name | Primary Key | Foreign Keys | Row Count in DB | Primary Purpose |
| :--- | :---: | :--- | :---: | :--- |
| `users` | `id` | None | 9 | User authentication credentials and system roles |
| `profiles` | `id` | `user_id -> users.id` | 9 | Extended biographical and institutional profile data |
| `refresh_tokens` | `id` | `user_id -> users.id` | 34 | Cryptographic refresh token rotation and revocation |
| `research_domains` | `id` | None | 8 | Standard taxonomy of scientific disciplines |
| `profile_domains` | `(profile_id, domain_id)` | FKs to `profiles` & `research_domains` | Junction | Junction mapping users to scientific domains |
| `research_interests` | `id` | `profile_id -> profiles.id` | 0 | Weighted research topics declared by user |
| `profile_keywords` | `id` | `profile_id -> profiles.id` | 0 | Search keywords associated with user profile |
| `technology_areas` | `id` | `profile_id -> profiles.id` | 0 | Technology domain specializations for founders/managers |
| `academic_histories` | `id` | `profile_id -> profiles.id` | 0 | Academic degrees and university qualifications |
| `research_histories` | `id` | `profile_id -> profiles.id` | 0 | Research projects, grants, and laboratory track record |
| `publications` | `id` | None | 2 | Indexed scientific papers, conference proceedings |
| `profile_publications` | `(profile_id, publication_id)`| FKs to `profiles` & `publications` | Junction | Junction linking users to authored/saved papers |
| `publication_keywords` | `id` | `publication_id -> publications.id` | 0 | Keyword tags indexed per publication |
| `patents` | `id` | None | 0 | Intellectual property patents and published applications |
| `profile_patents` | `(profile_id, patent_id)` | FKs to `profiles` & `patents` | Junction | Junction linking users to bookmarked patents |
| `funding_opportunities`| `id` | `created_by_user_id -> users.id` | 0 | Grant solicitations, RFPs, and innovation funds |
| `funding_opportunity_domains` | `(funding_opportunity_id, domain_id)` | FKs to `funding_opportunities` & `research_domains` | Junction | Taxonomy tags for funding opportunities |
| `funding_keywords` | `id` | `funding_opportunity_id -> funding_opportunities.id` | Junction | Search keywords attached to funding opportunities |

---

## 2. Granular Table DDL & Column Specs

### 2.1. `users`
- `id`: `INTEGER`, PRIMARY KEY, autoincrement.
- `email`: `VARCHAR(255)`, NOT NULL, UNIQUE, INDEXED.
- `hashed_password`: `VARCHAR(255)`, NOT NULL.
- `full_name`: `VARCHAR(255)`, NOT NULL.
- `phone`: `VARCHAR(50)`, NULLABLE. Added in migration `244ef6c34a82`.
- `role`: `VARCHAR(50)`, ENUM (`researcher`, `startup_founder`, `innovation_manager`, `administrator`), NOT NULL.
- `is_active`: `BOOLEAN`, DEFAULT `TRUE`.
- `is_superuser`: `BOOLEAN`, DEFAULT `FALSE`.
- `created_at`: `TIMESTAMP WITH TIME ZONE`, DEFAULT `now()`.
- `updated_at`: `TIMESTAMP WITH TIME ZONE`, DEFAULT `now()`.

### 2.2. `profiles`
- `id`: `INTEGER`, PRIMARY KEY, autoincrement.
- `user_id`: `INTEGER`, UNIQUE, NOT NULL, FK `users.id` ON DELETE CASCADE.
- `institution`: `VARCHAR(255)`, NULLABLE.
- `department`: `VARCHAR(255)`, NULLABLE.
- `designation`: `VARCHAR(255)`, NULLABLE. Added in migration `244ef6c34a82`.
- `country`: `VARCHAR(255)`, NULLABLE.
- `bio`: `TEXT`, NULLABLE.
- `orcid_id`: `VARCHAR(50)`, NULLABLE.
- `website`: `VARCHAR(255)`, NULLABLE.
- `created_at`, `updated_at`: `TIMESTAMP WITH TIME ZONE`.

### 2.3. `refresh_tokens`
- `id`: `INTEGER`, PRIMARY KEY, autoincrement.
- `user_id`: `INTEGER`, NOT NULL, FK `users.id` ON DELETE CASCADE.
- `token_hash`: `VARCHAR(64)`, NOT NULL, UNIQUE, INDEXED (SHA-256 hash).
- `issued_at`: `TIMESTAMP WITH TIME ZONE`, NOT NULL.
- `expires_at`: `TIMESTAMP WITH TIME ZONE`, NOT NULL.
- `revoked_at`: `TIMESTAMP WITH TIME ZONE`, NULLABLE.
- `is_revoked`: `BOOLEAN`, DEFAULT `FALSE`.
- `replaced_by_token_hash`: `VARCHAR(64)`, NULLABLE.

### 2.4. `publications`
- `id`: `INTEGER`, PRIMARY KEY, autoincrement.
- `title`: `VARCHAR(500)`, NOT NULL.
- `authors`: `TEXT`, NOT NULL.
- `abstract`: `TEXT`, NULLABLE.
- `publication_date`: `DATE`, NULLABLE.
- `venue`: `VARCHAR(255)`, NULLABLE.
- `doi`: `VARCHAR(255)`, NULLABLE, UNIQUE, INDEXED.
- `citation_count`: `INTEGER`, DEFAULT 0.
- `primary_domain`: `VARCHAR(150)`, NULLABLE.
- `source`: `VARCHAR(50)`, DEFAULT "manual".
- `external_id`: `VARCHAR(150)`, NULLABLE.
- `url`: `VARCHAR(500)`, NULLABLE.
- `created_at`, `updated_at`: `TIMESTAMP WITH TIME ZONE`.

### 2.5. `patents`
- `id`: `INTEGER`, PRIMARY KEY, autoincrement.
- `patent_number`: `VARCHAR(100)`, NOT NULL, UNIQUE, INDEXED.
- `title`: `VARCHAR(500)`, NOT NULL.
- `abstract`: `TEXT`, NULLABLE.
- `assignee`: `VARCHAR(255)`, NULLABLE.
- `inventors`: `TEXT`, NULLABLE.
- `filing_date`: `DATE`, NULLABLE.
- `publication_date`: `DATE`, NULLABLE.
- `patent_classification`: `VARCHAR(100)`, NULLABLE (IPC/CPC).
- `technology_domain`: `VARCHAR(150)`, NULLABLE.
- `citation_count`: `INTEGER`, DEFAULT 0.
- `source`: `VARCHAR(50)`, DEFAULT "manual".
- `external_id`: `VARCHAR(150)`, NULLABLE.
- `url`: `VARCHAR(500)`, NULLABLE.
- `created_at`, `updated_at`: `TIMESTAMP WITH TIME ZONE`.

### 2.6. `funding_opportunities`
- `id`: `INTEGER`, PRIMARY KEY, autoincrement.
- `title`: `VARCHAR(500)`, NOT NULL.
- `funding_agency`: `VARCHAR(255)`, NOT NULL.
- `funding_program`: `VARCHAR(255)`, NULLABLE.
- `description`: `TEXT`, NULLABLE.
- `funding_amount`: `NUMERIC(15, 2)`, NULLABLE.
- `currency`: `VARCHAR(10)`, DEFAULT "USD".
- `application_deadline`: `TIMESTAMP WITH TIME ZONE`, NULLABLE.
- `opportunity_type`: `VARCHAR(100)`, DEFAULT "Grant".
- `eligibility_summary`: `TEXT`, NULLABLE.
- `eligible_institutions`: `VARCHAR(255)`, NULLABLE.
- `geographic_restrictions`: `VARCHAR(255)`, NULLABLE.
- `status`: `VARCHAR(50)`, DEFAULT "open".
- `source`: `VARCHAR(50)`, DEFAULT "manual".
- `external_id`: `VARCHAR(150)`, NULLABLE.
- `url`: `VARCHAR(500)`, NULLABLE.
- `created_by_user_id`: `INTEGER`, FK `users.id`, NULLABLE.
- `created_at`, `updated_at`: `TIMESTAMP WITH TIME ZONE`.
