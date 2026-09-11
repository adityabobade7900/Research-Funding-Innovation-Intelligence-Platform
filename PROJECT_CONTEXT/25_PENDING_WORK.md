# 25_PENDING_WORK.md — Prioritized Development Backlog

> **PRIORITY CLASSIFICATIONS:**  
> • **P0 (Blocking):** Critical for core operations or evaluator demonstrations.  
> • **P1 (Important):** High-value specification requirements completing Milestone 4.  
> • **P2 (Normal):** Platform enhancements, performance tuning, and automated pipelines.  
> • **P3 (Optional / Future):** Advanced research extensions and cloud scale features.

---

## 1. Prioritized Task Backlog

| Priority | Module | Task Name | Reason & Business Value | Dependencies | Files Likely Affected | Status |
| :---: | :---: | :--- | :--- | :--- | :--- | :---: |
| **P1** | **M10** | **Implement Dedicated `Notification` Model & Table** | Complete Module 10 specification by allowing persistent user notifications and read/unread states. | Alembic, PostgreSQL | `app/models/notification.py`, `alembic/versions/`, `app/api/v1/endpoints/notifications.py` | 🟡 Pending |
| **P1** | **M12** | **Create Automated GitHub Actions CI/CD Pipeline** | Automate Pytest (150 tests) and Vitest (30 tests) verification on every pull request. | Git, GitHub | `.github/workflows/ci.yml` | 🟡 Pending |
| **P1** | **M12** | **Author Multi-Stage `frontend/Dockerfile` & Compose** | Containerize the Next.js frontend and provide a single-command `docker compose up` for the entire platform. | Docker, Node 20 | `frontend/Dockerfile`, `docker-compose.prod.yml` | 🟡 Pending |
| **P1** | **M3/4** | **Batch Ingestion of Research Literature & Grants** | Seed PostgreSQL database with 200+ publications and 50+ grants from OpenAlex and Grants.gov. | Harvester services | `backend/scripts/seed_database.py`, `backend/app/services/providers/` | 🟡 Pending |
| **P2** | **M11** | **Binary PDF & Excel Dossier Export** | Implement official specification export formats for executive reports. | Python ReportLab, OpenPyXL | `backend/app/api/v1/endpoints/executive_reports.py`, `backend/requirements.txt` | 🟡 Pending |
| **P2** | **M4** | **Saved Funding Watchlist Junction Table** | Allow users to bookmark grants directly into a personal watchlist (`ProfileFunding`). | PostgreSQL, Auth | `backend/app/models/funding.py`, `backend/app/api/v1/endpoints/funding.py` | 🟡 Pending |
| **P2** | **M10** | **Outbound Email Alert Dispatcher** | Transmit automated email alerts for grants closing within 14 days. | SMTP server, FastAPI background tasks | `backend/app/services/email_service.py`, `backend/app/core/config.py` | 🟡 Pending |
| **P2** | **M6** | **2D Interactive Whitespace Scatter Visualization** | Render interactive visual map of unpatented research whitespace in Next.js. | Recharts / Plotly | `frontend/src/app/(dashboard)/technology-intelligence/page.tsx` | 🟡 Pending |
| **P3** | **M3/4** | **Dense Vector Similarity Search (`pgvector`)** | Upgrade keyword matching to dense 384-dimensional vector embeddings. | PostgreSQL pgvector extension, Sentence-Transformers | `backend/requirements.txt`, `backend/app/services/embedding_service.py` | 🟡 Planned |
| **P3** | **M5** | **Unsupervised Patent Semantic Clustering** | Cluster patent abstracts using Scikit-learn TF-IDF + K-Means or BERTopic. | Scikit-learn | `backend/app/services/patent_landscape_service.py` | 🟡 Planned |
| **P3** | **M12** | **AWS / Azure Cloud Deployment Manifests** | Cloud infrastructure configuration for deploying platform to AWS ECS or Azure Container Apps. | AWS / Azure CLI, Docker | `deploy/aws/`, `deploy/azure/` | 🟡 Planned |
