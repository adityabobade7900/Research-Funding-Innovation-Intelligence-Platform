# 17_INNOVATION_SCORING.md — Innovation Scoring & TRL Estimation Engine

> **MODULE NUMBERING CONTEXT:**  
> Consistent across Official Specification and Mentor Communications: **Module 7: Innovation Scoring Engine**.

---

## 1. Official Mathematical Scoring Formula Verification

The official project specification PDF dictates the exact multi-factor weighting formula:

$$\text{Innovation Score} = (0.30 \times \text{Novelty}) + (0.20 \times \text{Patent}) + (0.15 \times \text{Maturity}) + (0.20 \times \text{Market}) + (0.15 \times \text{Funding})$$

> [!IMPORTANT]
> **CODE IMPLEMENTATION VERIFICATION:**  
> In `backend/app/services/innovation_scoring_service.py` (lines 350–365), the scoring engine implements **this mathematically exact formula**:
> ```python
> composite_score = round(
>     (0.30 * novelty_pillar.score) +
>     (0.20 * patent_pillar.score) +
>     (0.15 * maturity_pillar.score) +
>     (0.20 * market_pillar.score) +
>     (0.15 * funding_pillar.score),
>     2
> )
> ```
> Every pillar produces a normalized score between 0.0 and 100.0, yielding a composite Innovation Score between 0.0 and 100.0.

---

## 2. The Five Scoring Pillars Explained

| Pillar | Weight | Underlying Metrics & Formula | Key Driver Signals |
| :--- | :---: | :--- | :--- |
| **1. Research Novelty** | **30%** | Combines publication volume (35%), YoY publication growth rate (35%), and average citation impact (30%). | Scientific velocity, top-tier venue presence, high citation impact. |
| **2. Patent Strength** | **20%** | Combines patent portfolio size (40%), recent 3-year filing velocity (30%), citation impact (20%), and assignee concentration (10%). | Active intellectual property filings, forward citations, freedom-to-operate. |
| **3. Technology Maturity (TRL)** | **15%** | Evaluates Technology Readiness Level (1–9) normalized as $(\text{TRL} / 9.0) \times 100$. | Basic principles observed (TRL 1) to flight/market proven (TRL 9). |
| **4. Market Potential** | **20%** | Combines multi-year technology CAGR (50%) and cross-domain classification breadth (50%). | High commercial growth velocity, diversified multi-industry applications. |
| **5. Funding Relevance** | **15%** | Measures available grant opportunity volume (50%) and aggregate pool capital funding size (50%). | Active government grant solicitations, non-dilutive capital availability. |

---

## 3. NASA / DoD Standard TRL 1–9 Estimation Engine

Implemented in `backend/app/services/trl_service.py`:
- **TRL 1 — Basic Principles Observed:** Pure academic publications with no patents or grant funding.
- **TRL 2 — Technology Concept Formulated:** Emerging keywords and multi-author exploratory papers.
- **TRL 3 — Analytical & Experimental Critical Function:** Publications with high citation velocity and laboratory findings.
- **TRL 4 — Component Validation in Laboratory:** Initial patent filing or provisional IP application lodged.
- **TRL 5 — Component Validation in Relevant Environment:** Granted patent + active federal research grant funding.
- **TRL 6 — System/Subsystem Model in Relevant Environment:** High patent citation count + commercial development grant.
- **TRL 7 — System Prototype Demonstration in Operational Environment:** Multi-domain patent portfolio + commercialization readiness.
- **TRL 8 — Actual System Completed & Qualified:** Broad corporate assignee licensing or active spinout venture.
- **TRL 9 — Actual System Proven in Operational Environment:** Mature patent portfolio with extensive industry citations and revenue.

---

## 4. API Endpoints & Schemas

### Endpoints (`backend/app/api/v1/endpoints/innovation_scoring.py`)
- `GET /api/v1/innovation-scoring/score`: Computes the composite 5-pillar score for a domain or researcher profile.
- `GET /api/v1/innovation-scoring/trl`: Detailed TRL 1–9 estimation with milestone requirements.
- `GET /api/v1/innovation-scoring/evidence`: Granular breakdown of underlying data points and driver explanations.
- `GET /api/v1/innovation-scoring/summary`: Platform-wide benchmark distribution.

### Frontend View (`frontend/src/app/(dashboard)/scoring/page.tsx`)
- Visual components include:
  - Large composite score gauge (0–100) with rating classification (`HIGH_INNOVATION_POTENTIAL`, `MODERATE`, `DEVELOPING`).
  - Radar / spider breakdown chart visualizing all 5 pillars simultaneously.
  - Interactive TRL 1–9 milestone progress bar.
  - Deep-dive evidence accordion with explanation chips.

---

## 5. Algorithmic Reality: Deterministic Math vs. ML

- **Current Implementation:** 🟢 **DETERMINISTIC MATHEMATICAL HEURISTIC**  
  The formula is completely deterministic and reproducible. It does not use stochastic machine learning models or black-box neural networks.
- **Future ML Milestone:** Train an XGBoost or Random Forest regression model on historical Crunchbase / PitchBook startup exits to compare ML predictions against the specification's 5-pillar mathematical score.
