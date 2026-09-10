# 22_ENVIRONMENT_SETUP.md — Fresh Workstation Setup & Environment Reference

> [!CAUTION]
> **ZERO SECRET EXPOSURE POLICY:**  
> NEVER store production secrets, private keys, database passwords, or third-party API tokens in version control or documentation.  
> All environment values shown below use secure sanitized placeholders.

---

## 1. System Requirements & Assumptions

- **Host OS:** Windows 10/11 64-bit (PowerShell 5.1+ or PowerShell 7+), Linux (Ubuntu 22.04+), or macOS (Sonoma+).
- **Python Version:** **Python 3.10.x** (Mandatory: Python 3.14 breaks specific C-extension wheels; install Python 3.10 from `python.org` or Winget).
- **Node.js Version:** **Node.js 20.x LTS** (includes `npm` 10.x).
- **Git:** Git 2.40+ configured with your GitHub credentials.
- **Docker:** Docker Desktop with WSL2 backend (or Docker Engine on Linux).

---

## 2. Complete Fresh Installation Walkthrough

### Step 1: Install Core Runtimes (Windows PowerShell as Admin)
```powershell
# Install Git
winget install --id Git.Git -e --source winget

# Install Python 3.10
winget install --id Python.Python.3.10 -e --source winget

# Install Node.js 20 LTS
winget install --id OpenJS.NodeJS.LTS -e --source winget

# Install Docker Desktop
winget install --id Docker.DockerDesktop -e --source winget
```

### Step 2: Clone the Repository
```powershell
cd D:\
git clone https://github.com/adityabobade7900/Research-Funding-Innovation-Intelligence-Platform.git Intelligent-Research1
cd Intelligent-Research1
```

### Step 3: Initialize Environment Variables
Copy `.env.example` to `.env` in the repository root:
```powershell
Copy-Item .env.example .env
```

Review `.env` and configure your local settings:
```ini
# ==============================================================================
# Research Funding & Innovation Intelligence Platform - Local Dev Config
# ==============================================================================

ENVIRONMENT=development
PROJECT_NAME="Research Funding & Innovation Intelligence Platform"
API_V1_STR="/api/v1"

# Backend Server
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Security / JWT Configuration
# Generate your own secret via: python -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SECRET=<generate_a_random_32_byte_secret_string>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Primary Database (PostgreSQL 16)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/research_intel_db

# Async Test Database (In-Memory SQLite)
TEST_DATABASE_URL=sqlite+aiosqlite:///:memory:

# Optional External API Keys (Leave blank to use mock fallbacks)
OPENALEX_EMAIL=<your_email_for_polite_pool>
SEMANTIC_SCHOLAR_API_KEY=<your_optional_s2_api_key>
CROSSREF_MAILTO=<your_email_for_crossref>

# Frontend Next.js Public Variable
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### Step 4: Launch PostgreSQL Database Container
```powershell
docker compose up -d
# Verify container is healthy
docker ps --filter "name=research_intel_postgres"
```

### Step 5: Setup Python Backend Virtual Environment
```powershell
cd backend

# Create virtual environment targeting Python 3.10 explicitly
py -3.10 -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 6: Apply Database Migrations & Seed Admin
```powershell
# Run all 6 Alembic migrations up to head (244ef6c34a82)
alembic upgrade head

# Provision the local administrator account
python scripts/create_admin.py --email admin@platform.gov --password "Admin@2026Test!" --name "Platform Administrator"
```

### Step 7: Setup Next.js Frontend
```powershell
cd ..\frontend
npm install
```

---

## 3. Daily Development Startup Commands

Open three terminal tabs:

**Terminal 1 — Database:**
```powershell
cd Intelligent-Research1
docker compose up -d
```

**Terminal 2 — FastAPI Backend:**
```powershell
cd Intelligent-Research1\backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
*Swagger documentation available at: `http://localhost:8000/docs`*

**Terminal 3 — Next.js Frontend:**
```powershell
cd Intelligent-Research1\frontend
npm run dev
```
*Frontend application available at: `http://localhost:3000`*

---

## 4. Quality Verification Commands

```powershell
# Run backend tests (150 tests)
cd Intelligent-Research1\backend
.\venv\Scripts\pytest.exe tests/ -v

# Run frontend tests (30 tests)
cd ..\frontend
npm test

# Verify production build compiles
npx next build
```
