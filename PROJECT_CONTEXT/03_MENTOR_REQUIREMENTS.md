# 03_MENTOR_REQUIREMENTS.md — Mentor Requirements & Numbering Reconciliation

## 1. OFFICIAL MODULE NUMBERING VS MENTOR MODULE NUMBERING

> [!CAUTION]
> **CRITICAL ARCHITECTURAL CONFLICT & NUMBERING DISCREPANCY:**  
> A known numbering discrepancy exists between the initial **Official Internship Specification PDF** and subsequent **Mentor Communications**.  
>  
> • In the **Official Document**, Funding is Module 3 and Research Trends is Module 4.  
> • In **Mentor Communications**, Research Intelligence & Paper Analysis is designated as **Module 3**, while Funding Intelligence is designated as **Module 4**.  
>  
> **DO NOT SILENTLY OVERWRITE OR MERGE EITHER CONVENTION.** This documentation preserves both mappings clearly so that any team member, evaluator, or mentor can navigate the codebase seamlessly.

### Module Cross-Reference Matrix

| Topic / Domain Area | Official Specification Number | Mentor Communication Number | Codebase Endpoints | Frontend Routes |
| :--- | :---: | :---: | :--- | :--- |
| **Authentication & RBAC** | Module 1 | Module 1 | `/api/v1/auth/*` | `/login`, `/register`, `/admin` |
| **Research Profile Management** | Module 2 | Module 2 | `/api/v1/profile/*` | `/profile`, `/publications`, `/patents` |
| **Research Intelligence & Paper Analysis** | **Module 4** | **Module 3** | `/api/v1/research-intelligence/*`, `/api/v1/publications/*` | `/research-intelligence`, `/trends`, `/publications` |
| **Funding Intelligence & Opportunity Analysis** | **Module 3** | **Module 4** | `/api/v1/funding/*` | `/funding` |
| **Patent Landscape Analysis** | Module 5 | Module 5 | `/api/v1/patent-intelligence/*`, `/api/v1/patents/*` | `/patents` |
| **Technology Intelligence & Whitespace** | Module 6 | Module 6 | `/api/v1/technology-intelligence/*` | `/technology-intelligence` |
| **Innovation Scoring Engine** | Module 7 | Module 7 | `/api/v1/innovation-scoring/*` | `/scoring` |
| **Commercialization Recommendations** | Module 8 | Module 8 | `/api/v1/commercialization/*` | `/commercialization` |
| **Dashboard & Analytics** | Module 9 | Module 9 | `/api/v1/command-center/*`, `/api/v1/admin/*` | `/dashboard`, `/admin` |
| **Notification & Alert System** | Module 10 | Module 10 | `/api/v1/command-center/activity-feed` | Integrated in `/dashboard` & `/admin` |
| **Reports & Export System** | Module 11 | Module 11 | `/api/v1/reports/*` | `/reports` |
| **Testing, Integration & Deployment** | Module 12 | Module 12 | Tests & Docker configs | N/A |

---

## 2. Mentor Requirements: Module 3 (Research Intelligence & Paper Analysis)

The mentor specified a comprehensive scientific research analysis workflow centered around academic publications:

### Core Requirements
1. **Research Intelligence Dashboard:** High-level metrics showing publication velocity, emerging topic acceleration, citation impact, and domain distribution.
2. **Research Paper Search:** Multi-faceted filtering by title, abstract, author, publication year, domain, DOI, and venue.
3. **Research Paper Details:** Deep-dive view (`/publications/[id]`) displaying full metadata, author affiliations, abstract, citation count, open access status, and external links.
4. **AI Paper Analysis (Planned / Heuristic):** Structured breakdown separating source data from analytical insights:
   - Problem statement
   - Proposed methodology
   - Key findings & contributions
   - Known limitations
   - Future research directions
5. **Research Trends & Hotspots:** Identification of trending scientific domains using YoY growth rates, citation medians, and keyword co-occurrence.
6. **Research Insights & Gaps:** Pinpointing unaddressed research questions and scientific gaps.
7. **Recommendations:** Personalized paper recommendations matched to the user's research profile domains and keywords.
8. **Data Sources:** Real, legally compliant bibliographic sources:
   - Primary Candidate: **Semantic Scholar Graph API**
   - Secondary Candidate: **OpenAlex API**
   - Verification Status: Adapters exist in `backend/app/services/providers/`; offline mock fallbacks guarantee 100% test reliability.
9. **Inter-Module Connections:**
   - Feeds publication novelty metrics into Module 7 (Innovation Scoring).
   - Links literature citations to Module 5 (Patent prior art).
   - Informs Module 4 (Funding grant alignment).

---

## 3. Mentor Requirements: Module 4 (Funding Intelligence & Opportunity Analysis)

The mentor specified an end-to-end grant discovery and tracking engine:

### Core Requirements
1. **Funding Intelligence Dashboard:** Total grant pool valuation, upcoming deadlines, funding by agency, and opportunity type breakdown.
2. **Funding Search & Filtering:** Granular search by grant title, funding agency, opportunity type (Grant, Contract, Fellowship), status (open/upcoming), and funding amount range.
3. **Funding Details:** Detailed grant page with eligibility criteria, application guidelines, deadline countdown, and direct agency solicitation URL.
4. **Personalized Funding Recommendations:** Matching algorithm calculating relevancy scores (0–100%) against user profile domains, keywords, and academic history.
5. **Eligibility Analysis:** Rule-based matching checking institutional type (e.g., higher ed, small business, non-profit) and geographic constraints.
6. **Deadline Tracking & Saved Funding:** Bookmarking opportunities and alerting users to critical application cutoffs.
7. **Funding Comparison:** Multi-grant side-by-side comparative analysis of award amounts, duration, and competitiveness.
8. **Data Sources:** Federal and global funding registries:
   - **Grants.gov** (US Federal opportunities)
   - **National Science Foundation (NSF)** awards/programs
   - Verified mock fallbacks in `backend/app/services/providers/funding_providers.py`.
9. **Inter-Module Connections:**
   - Feeds funding relevance into Module 7 (Innovation Scoring 15% weight).
   - Connects commercialization grants to Module 8 (SBIR/STTR spinout pathways).

---

## 4. Mentor Requirements: Module 5 (Patent Landscape Analysis)

The mentor specified deep intellectual property analysis:

### Core Requirements
1. **Patent Search:** Full-text and metadata search by patent number, title, assignee, inventor, IPC classification, and technology domain.
2. **Mandatory Patent Metadata Fields:**
   - Patent Title
   - Assignee (Corporate or Academic Applicant)
   - Filing Date & Publication Date
   - Patent Classification (IPC / CPC, e.g., `G06N10/00`, `A61K31/7105`)
   - Technology Domain
   - Citation Count (Forward/Backward citations)
3. **Patent Clustering:** Grouping patents by shared classification and technical domain.
   - *Current Implementation Reality:* Rule-based SQL categorization and IPC grouping. Embedding-based k-means / DBSCAN clustering is planned for future enhancement.
4. **Patent Trend Analysis:** Filing velocity over time, active jurisdiction distribution (USPTO, EPO, WIPO, CNIPA, IPO), and status breakdown (granted, pending, expired).
5. **Competitor Patent Analysis:**
   - Assignee portfolio concentration using the **Herfindahl-Hirschman Index (HHI)**.
   - **Composite Competitive Index:** Multi-factor formula weighting Volume (40%), Filing Velocity (30%), Citation Impact (20%), and Domain Breadth (10%).
   - Assignee classifications: `DOMINANT_PORTFOLIO`, `HIGH_VELOCITY`, `NICHE_SPECIALIST`, `EMERGING_APPLICANT`.
6. **Innovation Mapping:** Mapping patents to commercial technology areas and research publication foundations.
7. **Branch & Collaboration Rules:**
   - All patent analysis features developed on dedicated feature branches (`feature/aditya-ai-ml`).
   - No direct commits to `main`.
