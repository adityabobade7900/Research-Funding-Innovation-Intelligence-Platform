# 15_PATENT_INTELLIGENCE.md — Patent Landscape & Competitive Intelligence

> **MODULE NUMBERING CONTEXT:**  
> Consistent across both Official Specification and Mentor Communications: **Module 5: Patent Landscape Analysis Module**.

---

## 1. Five Core Capabilities Breakdown

### 1. Patent Search & Portfolio Management
- **Requirement:** Comprehensive search and retrieval across patent titles, abstracts, assignees, classifications (IPC), and technology domains.
- **Current Implementation:** Endpoints support full-text search, domain filtering, and pagination.
- **Database Model:** `patents` table in `backend/app/models/patent.py`.
- **Backend API:** `GET /api/v1/patents`, `GET /api/v1/patents/{id}`, `POST /api/v1/patents`, `PUT /api/v1/patents/{id}`.
- **Frontend View:** `/patents` (Portfolio tab with edit/delete modal).
- **Status:** 🟢 **IMPLEMENTED**

### 2. Patent Clustering
- **Requirement:** Unsupervised grouping of patent documents into thematic clusters.
- **Current Implementation Reality:**  
  > [!WARNING]
  > **NO MACHINE LEARNING CLUSTERING ACTIVE:**  
  > Current clustering is **rule-based aggregation** using International Patent Classification (IPC) codes (e.g., `G06N`, `A61K`, `H01M`) and assigned `technology_domain` values.  
  > K-Means, HDBSCAN, or transformer embedding clustering are **NOT** currently implemented in code.
- **Backend API:** `GET /api/v1/patent-intelligence/technology-domains`.
- **Status:** 🟡 **PARTIALLY IMPLEMENTED (RULE-BASED)**

### 3. Patent Trend Analysis
- **Requirement:** Measure filing velocity over time, active jurisdiction distributions, and legal status.
- **Current Implementation:** `PatentLandscapeService.get_patent_trends()` calculates annual filing volume, active percentage, and Year-over-Year growth curves.
- **Jurisdictions Analyzed:** USPTO (US), European Patent Office (EP), WIPO/PCT (WO), China (CN), Japan (JP), Germany (DE), India (IN).
- **Backend API:** `GET /api/v1/patent-intelligence/trends`, `GET /api/v1/patent-intelligence/jurisdictions`, `GET /api/v1/patent-intelligence/status`.
- **Frontend View:** `/patents` (Landscape tab with trend line charts and jurisdiction breakdowns).
- **Status:** 🟢 **IMPLEMENTED**

### 4. Competitor Patent Analysis
- **Requirement:** Analyze competitive market concentration, applicant filing rates, and identify dominant versus emerging market players.
- **Current Implementation:**
  - **Herfindahl-Hirschman Index (HHI):** Computes market concentration across assignee portfolios:
    $$HHI = \sum_{i=1}^{n} (s_i)^2$$
    where $s_i$ is the percentage market share of assignee $i$.
  - **Composite Competitive Index:** Multi-factor index (0–100) combining:
    - Volume Score (40%): Size of assignee patent portfolio.
    - Velocity Score (30%): Percentage of patents filed within the last 3 years.
    - Citation Score (20%): Average forward citations per patent.
    - Domain Breadth Score (10%): Number of distinct technology domains covered.
  - **Applicant Classifications:** Assignees are categorized into:
    - `DOMINANT_PORTFOLIO` (Large established incumbent)
    - `HIGH_VELOCITY` (Rapidly filing challenger)
    - `NICHE_SPECIALIST` (Focused, high-impact player)
    - `EMERGING_APPLICANT` (Early-stage entrant)
- **Backend API:** `GET /api/v1/patent-intelligence/assignees`, `GET /api/v1/patent-intelligence/competitive-landscape`.
- **Status:** 🟢 **IMPLEMENTED**

### 5. Innovation Mapping
- **Requirement:** Map patent clusters to scientific research domains and commercial technology readiness.
- **Current Implementation:** Cross-references `Patent.technology_domain` with `research_domains` and passes patent volume/velocity metrics directly into Module 7 (`InnovationScoringService`) and Module 6 (`TechnologyIntelligenceService`).
- **Status:** 🟢 **IMPLEMENTED**

---

## 2. Database Schema for Patents

Defined in `backend/app/models/patent.py`:
- `id` (Integer, Primary Key)
- `patent_number` (String(100), Unique, Indexed, e.g., `US11234567B2`)
- `title` (String(500), Not Null)
- `abstract` (Text, Nullable)
- `assignee` (String(255), Organization / University / Corporate applicant)
- `inventors` (Text, Comma-separated inventor names)
- `filing_date`, `publication_date` (Date)
- `patent_classification` (String(100), e.g., `G06N10/00`, `A61K31/7105`)
- `technology_domain` (String(150), e.g., `Quantum Technologies`, `Biotechnology`)
- `citation_count` (Integer, Default: 0)
- `source` (String(50), e.g., `uspto`, `google_patents`, `mock`)
- `external_id` (String(150), External database reference)
- `url` (String(500), Link to Google Patents / official registry)

> [!NOTE]
> **DATABASE POPULATION STATUS:**  
> The PostgreSQL database currently has **0 persistent patent rows**.  
> The services fall back to `SAMPLE_PATENTS` in `backend/app/services/providers/patent_providers.py` (Quantum processor, mRNA nanoparticle, and solid-state battery patents) or accept live creation via `POST /api/v1/patents/ingest`.

---

## 3. Missing Requirements & Future Enhancements

1. **Unsupervised Machine Learning Clustering:**  
   Implement Scikit-learn TF-IDF + K-Means or BERTopic on patent abstracts to discover organic semantic patent clusters.
2. **USPTO Bulk Harvest Script:**  
   Write a batch harvester to pull 500+ recent patents across emerging technology areas.
3. **Patent Claim Dependency Visualizer:**  
   Build an interactive tree diagram mapping independent claims to dependent claims.
