# checkpoints/RESUME_CHECKLIST.md — Rapid Continuity Checklist

Use this quick checklist immediately after cloning the repository on your freshly formatted machine:

- [ ] **Clone Repository:**
  ```powershell
  git clone https://github.com/adityabobade7900/Research-Funding-Innovation-Intelligence-Platform.git Intelligent-Research1
  cd Intelligent-Research1
  ```
- [ ] **Read Master Guide:** Read `PROJECT_CONTEXT/00_READ_FIRST.md`.
- [ ] **Environment Setup:** Follow detailed instructions in `PROJECT_CONTEXT/27_RESUME_AFTER_REINSTALL.md`.
- [ ] **Configure Environment File:**
  ```powershell
  Copy-Item .env.example .env
  ```
- [ ] **Start PostgreSQL Container:**
  ```powershell
  docker compose up -d
  ```
- [ ] **Setup Python 3.10 Backend:**
  ```powershell
  cd backend
  py -3.10 -m venv venv
  .\venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  ```
- [ ] **Run Database Migrations:**
  ```powershell
  alembic upgrade head
  ```
- [ ] **Provision Administrator Account:**
  ```powershell
  python scripts/create_admin.py --email admin@platform.gov --password "Admin@2026Test!" --name "Platform Administrator"
  ```
- [ ] **Setup Next.js Frontend:**
  ```powershell
  cd ..\frontend
  npm install
  ```
- [ ] **Run Test Suites:**
  ```powershell
  # Backend
  cd ..\backend
  .\venv\Scripts\pytest.exe tests/ -v
  # Frontend
  cd ..\frontend
  npm test
  ```
- [ ] **Start Application Servers:**
  - Terminal 1 (Backend): `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
  - Terminal 2 (Frontend): `npm run dev` (Port 3000)
- [ ] **Verify Login & Modules:** Login at `http://localhost:3000/login` with `admin@platform.gov` / `Admin@2026Test!`.
- [ ] **Resume Engineering:** Follow priorities in `PROJECT_CONTEXT/26_NEXT_STEPS.md`.
