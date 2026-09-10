# 28_DEVELOPMENT_RULES.md — Permanent Engineering Commandments

To preserve project integrity, maintain architectural consistency, and prevent regressions across developer handovers, all contributors and coding agents must strictly adhere to these 15 permanent project rules:

---

### Rule 1: Inspect Before Modifying
Never alter a file, rewrite an endpoint, or edit a schema without first inspecting the existing implementation, imports, and active callers across both backend and frontend.

### Rule 2: Preserve Working Functionality
Working modules (Modules 1 through 9, and 11) represent verified baselines. New features must extend existing architecture rather than replacing or refactoring stable code.

### Rule 3: No Direct Main Branch Changes
The `main` branch is protected. All modifications must occur on dedicated feature branches (e.g., `feature/aditya-ai-ml`) and merge exclusively via reviewed pull requests.

### Rule 4: Use Isolated Feature Branches
Create focused, descriptively named branches for discrete work packages (e.g., `feature/notifications-engine`, `feature/docker-prod`).

### Rule 5: Test After Every Change
Before staging a commit, execute both test suites:
- Backend: `pytest backend/tests/ -v` (Must maintain 150/150 passing).
- Frontend: `npm test` in `frontend/` (Must maintain 30/30 passing).
- Build verification: `npx next build` in `frontend/` (Must compile 18 routes cleanly).

### Rule 6: Do Not Fabricate External API Data
Do not simulate external data sources with ad-hoc random generation. Harvesters must either query legitimate external endpoints (OpenAlex, Crossref, Semantic Scholar, Grants.gov, NSF) or use standardized, structured fixtures located in `backend/app/services/providers/`.

### Rule 7: Clearly Label Mock Data
Whenever mock fallbacks or development fixtures are utilized, explicitly tag the records with `source="mock"` and document their use clearly in code comments and API responses.

### Rule 8: Distinguish AI from Deterministic Logic
Do not label SQL window functions, statistical CAGR formulas, or NASA TRL rule heuristics as "Deep Learning" or "Artificial Intelligence." Maintain complete transparency regarding algorithmic realities.

### Rule 9: Avoid Unnecessary Dependencies
Do not install heavy libraries (e.g., PyTorch, TensorFlow, LangChain, Elasticsearch) unless a verified feature genuinely requires them and lighter alternatives are insufficient.

### Rule 10: Maintain API Compatibility
Never alter existing REST endpoint URLs, HTTP methods, or required request parameters without maintaining backwards compatibility for the Next.js frontend client.

### Rule 11: Maintain Database Migration Integrity
Never modify existing applied Alembic migration files (`backend/alembic/versions/`). All schema modifications must be introduced through new versioned revisions (`alembic revision --autogenerate`).

### Rule 12: Never Expose Secrets
Never hardcode passwords, JWT secrets, private keys, or API tokens into source code, documentation, or Git history. Always use `.env` loaders and sanitized placeholders.

### Rule 13: Keep Frontend & Backend Contracts Synchronized
Whenever a Pydantic schema in `backend/app/schemas/` is updated, immediately update the corresponding TypeScript interface in `frontend/src/lib/` to prevent runtime serialization mismatches.

### Rule 14: Document Major Architectural Decisions
Record significant design choices, database schema additions, or external provider adoptions in `PROJECT_CONTEXT/29_DECISIONS_LOG.md`.

### Rule 15: Never Rebuild the Project Unnecessarily
Do not discard existing project foundations to "start over." The platform is cumulative; build iteratively on top of verified working checkpoints.
