# 27_RESUME_AFTER_REINSTALL.md — Post-Reinstallation Continuity Checklist

> **PURPOSE:**  
> This file is your exact, practical walkthrough when sitting in front of a fresh Windows installation.  
> Follow these phases in sequential order to restore the platform to 100% operational readiness in less than 20 minutes.

---

## 1. Step-by-Step Restoration Checklist

### PHASE 1 — Install Git
Open PowerShell as Administrator:
```powershell
winget install --id Git.Git -e --source winget
```
*Close and reopen PowerShell to refresh PATH, then verify:*
```powershell
git --version
```

---

### PHASE 2 — Clone Repository
```powershell
cd D:\
git clone https://github.com/adityabobade7900/Research-Funding-Innovation-Intelligence-Platform.git Intelligent-Research1
cd Intelligent-Research1
```

---

### PHASE 3 — Open Repository in IDE
Launch your development environment:
```powershell
code .
```
*(or open inside Antigravity IDE).*

---

### PHASE 4 — Read Master Documentation
Open and review:
`PROJECT_CONTEXT/00_READ_FIRST.md`

---

### PHASE 5 — Install Python 3.10
> [!IMPORTANT]
> Install **Python 3.10**. Do not use Python 3.14 as default for ML/FastAPI venvs.
```powershell
winget install --id Python.Python.3.10 -e --source winget
```
*Verify installation:*
```powershell
py -3.10 --version
```

---

### PHASE 6 — Create Python Virtual Environment
```powershell
cd D:\Intelligent-Research1\backend
py -3.10 -m venv venv
```

---

### PHASE 7 — Install Backend Dependencies
```powershell
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

### PHASE 8 — Install Node.js 20 LTS
```powershell
winget install --id OpenJS.NodeJS.LTS -e --source winget
```
*Verify installation:*
```powershell
node -v
npm -v
```

---

### PHASE 9 — Install Frontend Dependencies
```powershell
cd D:\Intelligent-Research1\frontend
npm install
```

---

### PHASE 10 — Configure Environment File (`.env`)
Return to project root and copy `.env.example`:
```powershell
cd D:\Intelligent-Research1
Copy-Item .env.example .env
```
Generate a fresh JWT secret using Python:
```powershell
py -3.10 -c "import secrets; print(secrets.token_urlsafe(32))"
```
Edit `.env` and set:
```ini
JWT_SECRET=<paste_your_generated_secret_here>
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/research_intel_db
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

### PHASE 11 — Start PostgreSQL Database Container
Install Docker Desktop if not present:
```powershell
winget install --id Docker.DockerDesktop -e --source winget
```
Launch Docker Desktop, then run:
```powershell
cd D:\Intelligent-Research1
docker compose up -d
docker ps
```
*(Verify container `research_intel_postgres` is running).*

---

### PHASE 12 — Run Database Migrations & Provision Admin
```powershell
cd D:\Intelligent-Research1\backend
.\venv\Scripts\Activate.ps1

# Run all 6 Alembic migrations up to head
alembic upgrade head

# Provision the local administrator account
python scripts/create_admin.py --email admin@platform.gov --password "Admin@2026Test!" --name "Platform Administrator"
```

---

### PHASE 13 — Start FastAPI Backend Server
In Terminal 1:
```powershell
cd D:\Intelligent-Research1\backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
*Check API health at:* `http://localhost:8000/api/v1/health`  
*Swagger Docs available at:* `http://localhost:8000/docs`

---

### PHASE 14 — Start Next.js Frontend
In Terminal 2:
```powershell
cd D:\Intelligent-Research1\frontend
npm run dev
```
*Open application at:* `http://localhost:3000`

---

### PHASE 15 — Run Automated Tests
In Terminal 3:
```powershell
# Run backend tests (150 tests)
cd D:\Intelligent-Research1\backend
.\venv\Scripts\pytest.exe tests/ -v

# Run frontend tests (30 tests)
cd D:\Intelligent-Research1\frontend
npm test
```
*(Ensure all 150 backend tests and 30 frontend tests pass).*

---

### PHASE 16 — Verify Login
1. Open browser to `http://localhost:3000/login`.
2. Enter credentials:
   - **Email:** `admin@platform.gov`
   - **Password:** `Admin@2026Test!`
3. Verify successful redirection to `/dashboard`.

---

### PHASE 17 — Verify Existing Modules
Click through each navigation item to verify functionality:
- `/dashboard`: Command Center overview & activity feed.
- `/profile`: Research profile facets and domains.
- `/publications`: Publication search catalog.
- `/funding`: Grants list, recommendations, eligibility check.
- `/patents`: Patent landscape and competitor index.
- `/research-intelligence`: Trend velocity and hotspots.
- `/technology-intelligence`: Whitespace discovery.
- `/scoring`: 5-pillar score and NASA TRL 1–9.
- `/commercialization`: Readiness scores and strategic pathways.
- `/reports`: Executive dossier generator and Markdown export.
- `/admin`: System telemetry and user management.

---

### PHASE 18 — Continue Development
Review [26_NEXT_STEPS.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/26_NEXT_STEPS.md) to begin work on Step 1 (Notification model and table).

---

## 2. "DO NOT DO THIS" — Protection Rules

- ❌ **DO NOT DELETE EXISTING DATABASE MODELS:** The models in `backend/app/models/` are linked to 6 applied Alembic migrations.
- ❌ **DO NOT REBUILD FROM SCRATCH:** The platform is ~93% complete with 180 passing tests.
- ❌ **DO NOT OVERWRITE WORKING MODULES:** Modules 1 through 9 and 11 are verified working.
- ❌ **DO NOT WORK DIRECTLY ON `main`:** Keep all work on `feature/aditya-ai-ml` or a new feature branch.
- ❌ **DO NOT COMMIT SECRETS OR `.env`:** Keep tokens sanitized.
- ❌ **DO NOT INVENT APIS:** Always check [09_API_REFERENCE.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/09_API_REFERENCE.md) before writing frontend hooks.
- ❌ **DO NOT CLAIM RAW PYTHON MATH IS "DEEP LEARNING":** Preserve the objective AI/ML audit in [11_AI_ML.md](file:///d:/Infosys%207.0/Intelligent-Research1/PROJECT_CONTEXT/11_AI_ML.md).
