# 02_OFFICIAL_REQUIREMENTS.md — Official Project Specification

> **AUTHORITATIVE SOURCE:**  
> Extracted verbatim from the official internship project document:  
> `AI_Research Funding & Innovation Intelligence Platform.pdf` (Infosys Springboard Internship 7.0).

---

## 1. Official Project Title & Objective

- **Title:** Research Funding & Innovation Intelligence Platform
- **Objective:**  
  "Build an AI-powered Research Funding & Innovation Intelligence Platform that helps researchers, startups, universities, innovation centers, and enterprises identify relevant funding opportunities, analyze research trends, evaluate patent landscapes, discover emerging technologies, and generate commercialization recommendations.  
  The platform combines research intelligence, funding opportunity discovery, patent analytics, technology trend analysis, and innovation strategy recommendations through a centralized innovation intelligence dashboard."

### Official Expected Outcomes
1. Developed and deployed an AI-powered innovation intelligence platform.
2. Implemented secure authentication and role-based access control.
3. Built funding opportunity discovery and recommendation workflows.
4. Developed research trend analysis and technology intelligence modules.
5. Implemented patent landscape analysis and intellectual property analytics.
6. Built innovation scoring and commercialization recommendation systems.
7. Developed dashboards for funding, research, patent, and innovation insights.
8. Deployed the platform using Docker and cloud deployment platforms such as AWS or Azure.

---

## 2. The 12 Official Specification Modules

| Module # | Official Module Name | Sub-Features Specified in Official PDF |
| :---: | :--- | :--- |
| **1** | **User Authentication & Role-Based Access** | • User registration and login<br>• JWT authentication<br>• OAuth2 login<br>• Role-based access control<br>• User profile management<br>• **Roles:** Researcher, Startup Founder, Innovation Manager, Administrator |
| **2** | **Research Profile Management** | • Research profile creation<br>• Research interest management<br>• Publication management<br>• Academic profile tracking<br>• Research history management<br>• **Profile Information:** Research Domains, Keywords, Publications, Patents, Technology Areas, Organization Information |
| **3** | **Funding Opportunity Discovery Module** | • Funding opportunity collection<br>• Funding recommendation engine<br>• Eligibility matching<br>• Grant search<br>• Funding alerts<br>• **Funding Sources:** Government Grants, Research Councils, Innovation Funds, Startup Accelerators, Venture Programs, International Funding Agencies |
| **4** | **Research Trend Intelligence Module** | • Publication trend analysis<br>• Emerging topic detection<br>• Research hotspot identification<br>• Domain trend monitoring<br>• Citation analytics<br>• **Data Sources:** Research Papers, Publications, Conference Proceedings, Open Research Repositories |
| **5** | **Patent Landscape Analysis Module** | • Patent search<br>• Patent clustering<br>• Patent trend analysis<br>• Competitor patent analysis<br>• Innovation mapping<br>• **Patent Information:** Patent Title, Assignee, Filing Date, Patent Classification, Technology Domain, Citation Count |
| **6** | **Technology Intelligence Module** | • Emerging technology identification<br>• Technology maturity analysis<br>• Technology adoption tracking<br>• Innovation opportunity discovery<br>• Competitive technology monitoring |
| **7** | **Innovation Scoring Engine** | • Innovation potential scoring<br>• Research impact scoring<br>• Technology readiness scoring<br>• Commercial viability scoring<br>• Funding attractiveness scoring<br>• **Official Weighted Scoring Formula:**<br>  $$\text{Innovation Score} = (0.30 \times \text{Novelty}) + (0.20 \times \text{Patent}) + (0.15 \times \text{Maturity}) + (0.20 \times \text{Market}) + (0.15 \times \text{Funding})$$ |
| **8** | **Commercialization Recommendation Module** | • Research commercialization analysis<br>• Productization recommendations<br>• Licensing opportunities<br>• Startup creation recommendations<br>• Industry partnership suggestions |
| **9** | **Dashboard & Analytics** | • **Researcher Dashboard:** Funding recommendations, research trends, publication analytics, patent insights, innovation score<br>• **Startup Dashboard:** Funding opportunities, technology opportunities, patent intelligence, commercialization insights<br>• **Innovation Manager Dashboard:** Portfolio analytics, innovation pipeline tracking, technology trend monitoring, funding analytics<br>• **Admin Dashboard:** User management, platform analytics, recommendation monitoring, system reports |
| **10** | **Notification & Alert System** | • New funding alerts<br>• Patent monitoring alerts<br>• Emerging technology alerts<br>• Research trend updates<br>• Commercialization opportunities<br>• Platform notifications |
| **11** | **Reports & Export System** | • Funding reports<br>• Patent reports<br>• Research trend reports<br>• Innovation intelligence reports<br>• Commercialization reports<br>• PDF export<br>• Excel export |
| **12** | **Final Integration, Testing & Deployment** | • Frontend and backend integration<br>• API validation and testing<br>• End-to-end workflow testing<br>• Security testing<br>• Performance optimization<br>• Docker containerization<br>• Production deployment<br>• Monitoring and logging setup<br>• Documentation and user guides |

---

## 3. Official 4-Milestone Schedule & Evaluation Criteria

### Milestone 1: Week 1 & 2 — Project Initialization, Design Process & Core Setup
- **Tasks:** Define objectives and workflows; design architecture and DB schema; setup frontend and backend; implement authentication & RBAC; build research profile workflows; integrate publication and patent datasets.
- **Evaluation Criteria:** Project initialization completed; authentication implemented; research profile management functional; publication and patent datasets integrated.

### Milestone 2: Week 3 & 4 — Funding Discovery & Research Intelligence
- **Tasks:** Implement funding recommendation engine; build grant matching workflows; develop publication trend analysis; create research intelligence dashboards; generate funding opportunity recommendations.
- **Evaluation Criteria:** Funding recommendation system operational; research intelligence dashboards functional; trend analysis workflows implemented.

### Milestone 3: Week 5 & 6 — Patent Analytics & Innovation Intelligence
- **Tasks:** Implement patent landscape analysis; build technology intelligence engine; develop innovation scoring workflows; generate commercialization recommendations; create innovation analytics dashboards.
- **Evaluation Criteria:** Patent intelligence operational; innovation scoring functional; commercialization recommendation workflows completed.

### Milestone 4: Week 7 & 8 — Analytics, Testing & Deployment
- **Tasks:** Build executive dashboards; add reports and visualization modules; implement testing and validations; deploy platform using Docker and cloud services; prepare final documentation and presentation.
- **Evaluation Criteria:** Fully deployed frontend and backend; dashboards and reporting systems operational; end-to-end innovation intelligence workflow demonstrated.

---

## 4. Official Tools & Tech Stack (From PDF Page 11–13)

- **Backend:** Python, FastAPI
- **Frontend:** JavaScript, React.js, Next.js, Tailwind CSS
- **Database:** PostgreSQL (Primary), MongoDB (Secondary)
- **AI & Machine Learning:** Scikit-learn, XGBoost, TensorFlow, PyTorch, Pandas, NumPy
- **NLP & Research Intelligence:** Sentence Transformers, Hugging Face Transformers, LangChain, OpenAI APIs
- **Search & Analytics:** Elasticsearch, FAISS, Vector Database
- **Data Sources:** OpenAlex, CrossRef, Semantic Scholar, Google Patents, The Lens, USPTO Public Data
- **DevOps:** Docker, Docker Compose, GitHub Actions, AWS / Azure

---

## 5. Official Requirements vs. Actual Implementation Delta

| Area | Official Requirement | Actual Implementation in Repository | Status / Delta Note |
| :--- | :--- | :--- | :--- |
| **Module 1 (Auth)** | OAuth2 login (Google/GitHub) | OAuth2 Password Bearer form implemented; third-party OAuth social login pending | Partially Implemented |
| **Module 7 (Scoring)** | Exact 5-pillar formula | Exact 5-pillar mathematical formula implemented: Novelty 30%, Patent 20%, TRL 15%, Market 20%, Funding 15% in `InnovationScoringService` | 🟢 Verified & Implemented |
| **Module 10 (Alerts)** | Outbound alerts (Email/Push) | In-app alerts on Command Center & Admin; standalone `Notification` DB table & SMTP pending | Partially Implemented (40%) |
| **Module 11 (Reports)** | PDF and Excel export | Markdown (`.md`) and JSON (`.json`) dossier export fully implemented; PDF/Excel binary rendering planned | Partially Implemented |
| **Secondary Database** | MongoDB document store | Connection string configured in `.env.example`, but no MongoDB driver active in `backend/requirements.txt` | Planned for raw payload caching |
| **AI/ML Layer** | PyTorch, Sentence-Transformers, FAISS | Pure Python statistical analysis, moving averages, CAGR, and rule-based heuristics | Functional without heavy ML overhead |
| **Deployment** | AWS / Azure deployment, CI/CD | Local Docker Compose (PostgreSQL) and `backend/Dockerfile`; cloud manifests and GitHub Actions pending | Milestone 4 pending work |
