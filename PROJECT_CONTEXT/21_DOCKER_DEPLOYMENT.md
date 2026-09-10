# 21_DOCKER_DEPLOYMENT.md — Containerization & Deployment Status

## 1. Containerization Reality Audit

| Component | Status | Location / Details | Notes |
| :--- | :---: | :--- | :--- |
| **PostgreSQL 16 Service** | 🟢 **IMPLEMENTED** | Root `docker-compose.yml` (`research_intel_postgres`) | Runs on port 5432 with health check and persistent volume `postgres_data`. |
| **Backend Dockerfile** | 🟢 **IMPLEMENTED** | `backend/Dockerfile` | Multi-stage image based on `python:3.10-slim`. Non-root `appuser`. |
| **Frontend Dockerfile** | 🔴 **NOT IMPLEMENTED** | None in `frontend/` | Next.js currently runs natively via `npm run dev` or `next start`. |
| **Full-Stack Compose** | 🟡 **PARTIALLY IMPLEMENTED** | Root `docker-compose.yml` only contains Postgres | Need multi-container compose with backend, frontend, and nginx. |
| **Reverse Proxy (Nginx)** | 🔴 **NOT IMPLEMENTED** | None | Direct client-to-API communication across ports 3000 and 8000. |
| **CI/CD Pipeline** | 🔴 **NOT IMPLEMENTED** | `.github/workflows/` does not exist | Manual test execution currently required before commits. |
| **Cloud Deployment Manifests** | 🟡 **PLANNED** | AWS ECS / Azure Container Apps | Cloud infrastructure templates pending for Milestone 4. |

---

## 2. Active Root `docker-compose.yml`

Located at the repository root:
```yaml
version: "3.8"

services:
  postgres:
    image: postgres:16-alpine
    container_name: research_intel_postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
      POSTGRES_DB: ${POSTGRES_DB:-research_intel_db}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
    driver: local
```

---

## 3. Backend Multi-Stage Dockerfile

Located at `backend/Dockerfile`:
```dockerfile
# Stage 1: Build Dependencies
FROM python:3.10-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Final Minimal Runtime Image
FROM python:3.10-slim AS runner

WORKDIR /app

RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY --from=builder /root/.local /home/appuser/.local
COPY . /app

ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 4. Production Deployment Blueprint (Planned)

To achieve production readiness in Milestone 4, the following files should be created:
1. `frontend/Dockerfile`: Multi-stage Next.js standalone runner (`node:20-alpine`).
2. `docker-compose.prod.yml`: Single-command stack linking:
   - `postgres:16-alpine` (internal network)
   - `backend` (FastAPI, 4 Uvicorn workers)
   - `frontend` (Next.js production build)
   - `nginx:alpine` (reverse proxy on port 80/443 with SSL termination).
3. `.github/workflows/ci.yml`: Automated testing on every pull request.
