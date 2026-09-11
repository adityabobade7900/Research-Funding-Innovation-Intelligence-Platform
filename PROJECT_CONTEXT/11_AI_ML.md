# 11_AI_ML.md — AI & Machine Learning Reality Audit

> [!IMPORTANT]
> **CRITICAL REALITY PRINCIPLE:**  
> We do NOT label deterministic mathematical equations or SQL aggregate heuristics as "Artificial Intelligence" or "Deep Learning."  
> This file provides an objective audit of what is currently executing in code versus what was listed in academic project specifications.

---

## 1. Classification Categories Defined

1. **REAL AI / ML:** Models employing trained neural networks, matrix factorizations, or statistical machine learning (e.g., PyTorch, Scikit-learn random forests, BERT/transformer embeddings, FAISS vector indexing).
2. **STATISTICAL ANALYSIS:** Mathematical algorithms calculating moving averages, compound annual growth rates (CAGR), market concentration indexes (HHI), or percentile distributions.
3. **RULE-BASED LOGIC / HEURISTICS:** Deterministic conditional trees, NASA TRL 1–9 state transitions, and keyword set-intersection matching.
4. **MOCK AI / FALLBACK:** Pre-generated fixtures or simulated model responses used for offline testing.
5. **PLANNED AI:** Features specified in PDF documentation or mentor discussions that have not yet been coded.

---

## 2. Feature-by-Feature AI/ML Reality Audit

| Feature | Input | Processing / Algorithm | Output | File Location | Reality Classification | Real AI or Deterministic? |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **Innovation Scoring Engine** | Publication volume, patent count, TRL level, market CAGR, funding count | Exact 5-pillar weighted formula: $0.30 \times N + 0.20 \times P + 0.15 \times T + 0.20 \times M + 0.15 \times F$ | Composite score (0–100) + pillar breakdowns | `backend/app/services/innovation_scoring_service.py` | **RULE-BASED LOGIC** | **Deterministic Math** (No ML model) |
| **TRL Estimation Engine** | Publications, citations, patents, grant funding presence | Rule-based decision ladder mapping artifact signals to NASA/DoD TRL 1–9 definitions | Estimated TRL integer (1–9) + milestone explanation | `backend/app/services/trl_service.py` | **RULE-BASED LOGIC** | **Deterministic Heuristics** (No ML model) |
| **Research Trend Hotspots** | Publication dates, domain tags, citation counts | Composite formula combining publication volume (40%), YoY growth (35%), and average citations (25%) | Hotspot score (0–100) & classification | `backend/app/services/research_trend_service.py` | **STATISTICAL ANALYSIS** | **Deterministic Math** (SQL window functions) |
| **Emerging Topic Detection** | Keyword timestamps, frequency over time | Acceleration velocity: comparison of recent 2-year frequency vs historical baseline | Velocity percentage & momentum status | `backend/app/services/research_trend_service.py` | **STATISTICAL ANALYSIS** | **Deterministic Math** (Frequency velocity) |
| **Technology Whitespace Discovery** | IPC patent classifications, technology domains, research activity | Density mapping: domains with high publication volume but zero or minimal patent filings | Whitespace candidate list with gap scores | `backend/app/services/technology_intelligence_service.py` | **STATISTICAL ANALYSIS** | **Deterministic Math** (Matrix density subtraction) |
| **Patent Competitor Index** | Patent counts, filing dates, forward citations, domain breadth | Composite Competitive Index: Volume (40%), Velocity (30%), Citations (20%), Breadth (10%) | Index score (0–100) + assignee classification | `backend/app/services/patent_landscape_service.py` | **STATISTICAL ANALYSIS** | **Deterministic Math** (Weighted index) |
| **Patent Assignee Concentration** | Assignee patent shares per domain | Herfindahl-Hirschman Index: $HHI = \sum (s_i)^2$ across all assignees in a domain | HHI score (0–10,000) & market category | `backend/app/services/patent_landscape_service.py` | **STATISTICAL ANALYSIS** | **Deterministic Math** (Standard HHI formula) |
| **Funding Eligibility Matcher** | User profile institution, country, grant eligibility summary | Keyword set-intersection and string matching against eligibility keywords | Boolean eligibility status + match percentage | `backend/app/services/eligibility_matcher.py` | **RULE-BASED LOGIC** | **Deterministic Logic** (Token intersection) |
| **Funding Recommendations** | User research domains, keywords, opportunity text | Token overlap and domain affinity scoring normalized to 0–100% | Ranked grant recommendations list | `backend/app/services/funding_recommendation_service.py` | **RULE-BASED LOGIC** | **Deterministic Logic** (Keyword scoring) |
| **Commercialization Pathway** | IP defensibility, market demand, regulatory feasibility, team | Multi-criteria scoring mapping scores to Licensing vs Spinout vs Joint Development | Recommended pathway & roadmap | `backend/app/services/commercialization_service.py` | **RULE-BASED LOGIC** | **Deterministic Logic** (Threshold triggers) |
| **Vector Similarity / Embeddings** | Paper titles, abstracts, grant descriptions | Sentence-Transformers (`all-MiniLM-L6-v2`) or PyTorch dense vectors | 384-dimensional vector embeddings | *Not installed in `requirements.txt`* | **PLANNED AI** | **Planned / Not Yet Implemented** |
| **Patent Claim K-Means Clustering** | Patent claim text | Unsupervised ML clustering (e.g. Scikit-learn K-Means / DBSCAN) | Visual cluster centroids | *Not installed in `requirements.txt`* | **PLANNED AI** | **Planned / Not Yet Implemented** |
| **LLM Paper Summarization** | Full scientific paper text | Large Language Model (OpenAI GPT-4, Claude, or local Ollama) | Structured summary (problem, methods, gaps) | *Not installed in `requirements.txt`* | **PLANNED AI** | **Planned / Not Yet Implemented** |

---

## 3. Installed Dependencies Reality Check

Inspecting `backend/requirements.txt`:
```
fastapi==0.111.0
uvicorn[standard]==0.30.1
pydantic==2.7.4
pydantic-settings==2.3.4
sqlalchemy==2.0.31
asyncpg==0.29.0
alembic==1.13.2
aiosqlite==0.20.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
bcrypt==4.0.1
python-multipart==0.0.9
pytest==8.2.2
pytest-asyncio==0.23.7
httpx==0.27.0
```

Notice that **none** of the following libraries are installed in the backend virtual environment:
- `torch` / `tensorflow`
- `sentence-transformers`
- `faiss-cpu` / `faiss-gpu`
- `scikit-learn` / `xgboost`
- `langchain` / `openai`

---

## 4. Planned Engineering Roadmap for Real AI/ML

If future development intends to replace the current deterministic statistical baseline with real ML:
1. **Step 1: Install sentence-transformers & pgvector:**  
   Add `pgvector` extension to PostgreSQL 16 and install `sentence-transformers` to generate 384-dim embeddings for publications and grants.
2. **Step 2: Vector Search Matcher:**  
   Replace `EligibilityMatcher` keyword intersection with cosine distance `<->` in pgvector.
3. **Step 3: Unsupervised Patent Clustering:**  
   Add Scikit-learn to cluster patent abstracts using TF-IDF + K-Means or HDBSCAN.
4. **Step 4: LLM Synthesis Pipeline:**  
   Add LangChain or direct OpenAI/Ollama client to synthesize paper limitations and future research directions from abstracts.
