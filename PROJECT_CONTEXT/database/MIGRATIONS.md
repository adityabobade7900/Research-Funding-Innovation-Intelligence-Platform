# database/MIGRATIONS.md — Alembic Database Migration History

The database schema is managed via Alembic using asynchronous migrations (`alembic/env.py`).  
Current Migration Head: **`244ef6c34a82`** (6 applied revisions).

---

## 1. Migration History Timeline

```
[706d13f3e174] Initial Schema Setup (Users, Refresh Tokens, Basic Profiles)
       │
       ▼
[68afbe48340e] Phase 2A: Normalized Research Domains, Interests, Keywords
       │
       ▼
[53d7c57aa26c] Phase 2B: Scientific Publications & Keywords
       │
       ▼
[626ab1f43993] Phase 2E: Patents & Profile Patent Bookmarks
       │
       ▼
[f8e9f392e6c3] Milestone 2A: Funding Opportunities & Taxonomies
       │
       ▼
[244ef6c34a82] Milestone 1/2 Compliance: User Phone & Profile Designation
```

---

## 2. Granular Revision Inventory

### Revision 1: `706d13f3e174`
- **File:** `2026_08_24_2346-706d13f3e174_initial_schema_setup_with_users_.py`
- **Date:** 2026-08-24 23:46
- **Summary:** Created baseline tables for `users`, `refresh_tokens`, and `profiles`. Established foreign key cascades from users to profiles and refresh tokens.

### Revision 2: `68afbe48340e`
- **File:** `2026_08_25_0033-68afbe48340e_add_phase_2a_normalized_research_.py`
- **Date:** 2026-08-25 00:33
- **Summary:** Added normalized profile taxonomy tables: `research_domains`, `profile_domains`, `research_interests`, `profile_keywords`, `technology_areas`, `academic_histories`, and `research_histories`.

### Revision 3: `53d7c57aa26c`
- **File:** `2026_08_25_0038-53d7c57aa26c_add_phase_2b_publications_and_keywords_.py`
- **Date:** 2026-08-25 00:38
- **Summary:** Created `publications`, `publication_keywords`, and junction table `profile_publications`. Added unique index on `doi` column.

### Revision 4: `626ab1f43993`
- **File:** `2026_08_25_0055-626ab1f43993_add_phase_2e_patents_and_profile_.py`
- **Date:** 2026-08-25 00:55
- **Summary:** Created `patents` and junction table `profile_patents`. Added unique index on `patent_number` column.

### Revision 5: `f8e9f392e6c3`
- **File:** `2026_08_25_0101-f8e9f392e6c3_add_milestone_2a_funding_opportunities_.py`
- **Date:** 2026-08-25 01:01
- **Summary:** Created `funding_opportunities`, `funding_opportunity_domains`, and `funding_keywords`. Added index on `application_deadline`.

### Revision 6: `244ef6c34a82`
- **File:** `2026_08_25_2334-244ef6c34a82_add_user_phone_and_profile_designation_.py`
- **Date:** 2026-08-25 23:34
- **Summary:** Added `phone` column (`VARCHAR(50)`) to `users` table and `designation` column (`VARCHAR(255)`) to `profiles` table to meet mentor profile compliance requirements.

---

## 3. Migration Commands Reference

```powershell
# Check current database revision
alembic current

# Check migration history
alembic history --verbose

# Upgrade to latest revision (head)
alembic upgrade head

# Revert last applied migration (if needed)
alembic downgrade -1

# Generate a new migration revision automatically
alembic revision --autogenerate -m "descriptive_migration_name"
```
