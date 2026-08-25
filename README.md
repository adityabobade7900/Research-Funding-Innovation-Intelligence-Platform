# Research Funding & Innovation Intelligence Platform

An enterprise-grade AI-powered intelligence platform connecting academic research, intellectual property (patents), grant funding, and commercial market viability.

## Supported Roles
- **Researcher**: Profile sync, research novelty scoring, and semantic grant matchmaking.
- **Startup Founder**: Deep-tech whitespace discovery, non-dilutive grant radar, and commercial viability evaluation.
- **Innovation Manager**: Institutional portfolio benchmarking, TRL estimation, and commercialization pipelines.
- **Administrator**: User RBAC governance, pipeline telemetry, and audit logs.

## 5-Pillar Innovation Scoring Formula
$$\text{Innovation Score} = (0.30 \times \text{Novelty}) + (0.20 \times \text{Patent}) + (0.15 \times \text{TRL}) + (0.20 \times \text{Market}) + (0.15 \times \text{Funding})$$

---

## Tech Stack (Stage 1 Foundation)
- **Backend**: Python 3.10, FastAPI, Pydantic v2, SQLAlchemy 2.0 (Async), Alembic, Asyncpg, Python-Jose (JWT), Passlib (Bcrypt).
- **Frontend**: Next.js 14+ (App Router), React 18, TypeScript, Tailwind CSS, Lucide React, Axios.
- **Database**: PostgreSQL 16 (via Docker Compose or local instance) + Async SQLite for local testing.
- **Testing**: Pytest, Pytest-asyncio, HTTPX AsyncClient.

---

## Getting Started

### 1. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Activate Python 3.10 virtual environment
.\venv\Scripts\Activate.ps1  # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Run migrations (or start server which initializes tables in dev mode)
alembic upgrade head

# Start FastAPI development server
uvicorn app.main:app --reload --port 8000
```
Interactive API docs available at: `http://localhost:8000/docs`

### 2. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Next.js development server
npm run dev
```
Web application available at: `http://localhost:3000`

### 3. Running Automated Tests
```bash
# In backend directory with active virtual environment:
pytest tests/ -v
```
