# 06_FRONTEND.md — Frontend Architecture & Route Inventory

## 1. Frontend Technology Stack & Versioning

- **Framework:** Next.js 14.2.4 (React 18.3.1) utilizing the App Router pattern (`src/app/`).
- **Language:** TypeScript 5.4.5 with strict type checking enabled.
- **Styling & Design System:** Tailwind CSS 3.4.4, `clsx`, and `tailwind-merge` for responsive, glassmorphic dark theme.
- **Iconography:** Lucide React 0.395.0.
- **HTTP Client:** Axios 1.7.2 with automated bearer token interception.
- **Testing Engine:** Vitest 4.1.11 with 30 unit tests across 10 test suites.
- **Build Status:** 18 / 18 routes statically generated with 0 errors via `npm run build`.

---

## 2. Directory Structure

```
frontend/
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── postcss.config.js
├── next.config.mjs
├── vitest.config.ts
└── src/
    ├── app/
    │   ├── layout.tsx                     # Global HTML/Body root layout
    │   ├── page.tsx                       # Landing / Marketing homepage
    │   ├── globals.css                    # Tailwind directives and theme variables
    │   ├── (auth)/
    │   │   ├── login/page.tsx             # User Login page
    │   │   └── register/page.tsx          # User Registration page (desktop-wide responsive layout)
    │   └── (dashboard)/
    │       ├── layout.tsx                 # Dashboard navigation layout (Sidebar, Header, Profile badge)
    │       ├── dashboard/page.tsx         # Unified Command Center & Analytics Overview
    │       ├── profile/page.tsx           # Extended Profile & Research Taxonomy editor
    │       ├── publications/
    │       │   ├── page.tsx               # Publications list, filtering & ingest trigger
    │       │   └── [id]/page.tsx          # Deep-dive scientific paper metadata & analysis
    │       ├── funding/page.tsx           # Grant discovery, eligibility checker & recommendations
    │       ├── patents/page.tsx           # Patent portfolio & competitive landscape analytics
    │       ├── research-intelligence/page.tsx # Publication trends, CAGR hotspots, citation charts
    │       ├── trends/page.tsx            # Topic acceleration & keyword trend explorer
    │       ├── technology-intelligence/page.tsx # Technology density & whitespace discovery
    │       ├── scoring/page.tsx           # 5-Pillar Innovation Scoring & TRL 1-9 evaluation
    │       ├── commercialization/page.tsx # Readiness dimension scoring & strategic pathways
    │       ├── reports/page.tsx           # Executive dossier generator & Markdown/JSON export
    │       └── admin/page.tsx             # System telemetry, pipeline status & user RBAC management
    ├── components/
    │   ├── layout/                        # Sidebar, Navbar, Breadcrumbs, UserDropdown
    │   ├── ui/                            # Buttons, Cards, Modals, Badges, Tabs, FormInputs
    │   ├── dashboard/                     # KPI summary cards, Activity Feed, Deadline Countdown
    │   ├── charts/                        # Bar, Line, Radar, and Progress visual components
    │   └── common/                        # ErrorBoundaries, LoadingSpinners, ToastAlerts
    └── lib/
        ├── api.ts                         # Axios base instance, interceptors, error formatting
        ├── auth.ts                        # Auth state management, token storage, logout handlers
        ├── admin.ts                       # Admin API client functions
        ├── command_center.ts              # Command center API client functions
        ├── commercialization.ts           # Commercialization API client functions
        ├── executive_report.ts            # Executive report API client functions
        ├── funding.ts                     # Funding API client functions
        ├── innovation_scoring.ts          # Scoring API client functions
        ├── patent_intelligence.ts         # Patent intelligence API client functions
        ├── research_intelligence.ts       # Research intelligence API client functions
        ├── technology_intelligence.ts     # Technology intelligence API client functions
        └── user_profile.ts                # Profile API client functions
```

---

## 3. Complete Route Inventory (18 Routes)

| Route Path | Type | Purpose & Description | Backend API Endpoints Consumed | Status |
| :--- | :---: | :--- | :--- | :---: |
| `/` | Static | Platform landing page with feature overview and role navigation | None (Static) | 🟢 Working |
| `/_not-found` | Static | Global 404 error page | None (Static) | 🟢 Working |
| `/login` | Static | User authentication form with OAuth2 / JSON login | `POST /api/v1/auth/login` | 🟢 Working |
| `/register` | Static | Desktop-wide multi-column account creation form (Admin role hidden) | `POST /api/v1/auth/register` | 🟢 Working |
| `/dashboard` | Static | Unified Command Center dashboard with role-specific KPIs | `GET /api/v1/command-center/overview`, `activity-feed` | 🟢 Working |
| `/profile` | Static | Profile editor for bio, domains, keywords, and academic history | `GET /api/v1/profile/me`, `PUT /api/v1/profile/me` | 🟢 Working |
| `/publications` | Static | Search, filter, and ingest scientific literature | `GET /api/v1/publications`, `POST /api/v1/publications/ingest` | 🟢 Working |
| `/publications/[id]` | Dynamic | Paper details view with citation count, DOI, and abstract | `GET /api/v1/publications/{id}` | 🟢 Working |
| `/funding` | Static | Grant search, eligibility checks, and personalized recommendations | `GET /api/v1/funding`, `/recommendations`, `/{id}/eligibility` | 🟢 Working |
| `/patents` | Static | Patent landscape, assignee concentration, and portfolio editor | `GET /api/v1/patents`, `GET /api/v1/patent-intelligence/*` | 🟢 Working |
| `/research-intelligence` | Static | Publication velocity, CAGR trends, domain hotspots, citation medians | `GET /api/v1/research-intelligence/*` | 🟢 Working |
| `/trends` | Static | Topic acceleration, keyword trends, and emerging research topics | `GET /api/v1/research-intelligence/emerging-topics` | 🟢 Working |
| `/technology-intelligence`| Static | Technology density coverage, maturity index, whitespace detection | `GET /api/v1/technology-intelligence/*` | 🟢 Working |
| `/scoring` | Static | 5-pillar mathematical innovation scoring and NASA TRL 1–9 engine | `GET /api/v1/innovation-scoring/*` | 🟢 Working |
| `/commercialization` | Static | 4 readiness dimensions and strategic pathways (Licensing, Spinout) | `GET /api/v1/commercialization/*` | 🟢 Working |
| `/reports` | Static | Executive intelligence dossier generator with Markdown/JSON export | `GET /api/v1/reports/dossier`, `export/markdown`, `export/json` | 🟢 Working |
| `/admin` | Static | User role management, pipeline health telemetry, system audit logs | `GET /api/v1/admin/*`, `PUT /api/v1/admin/users/{id}/*` | 🟢 Working |

---

## 4. State Management & API Communication

- **Token Storage:** Access and refresh tokens are managed in `localStorage` through `src/lib/auth.ts`.
- **Axios Interceptor (`src/lib/api.ts`):**  
  Every outgoing request automatically injects `Authorization: Bearer <access_token>`. When an HTTP 401 error is encountered, the interceptor attempts a transparent call to `POST /api/v1/auth/refresh`. If successful, the original request is retried with the new token; otherwise, the user is safely redirected to `/login`.
- **Form Handling:** Reactive React state handles forms with inline validation (e.g., regex phone format, password strength indicators, and alphabet-only name constraints).
- **Loading & Error States:** All asynchronous dashboard widgets implement skeleton loaders and localized error banners to prevent layout flashing.

---

## 5. Frontend Commands

```bash
# Install frontend dependencies
cd frontend
npm install

# Start local Next.js development server on port 3000
npm run dev

# Run automated Vitest test suite (30 tests)
npm test

# Create optimized production build
npm run build

# Start production server
npm start
```
