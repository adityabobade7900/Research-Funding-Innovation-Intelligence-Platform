# MODULE_01_AUTH.md — User Authentication & Role-Based Access Control

# Objective
Provide a secure, stateless, and audited authentication and role-based access control (RBAC) foundation across the platform, establishing four distinct user personas (`researcher`, `startup_founder`, `innovation_manager`, and `administrator`) with strict user profile isolation and privilege escalation protection.

# Official Requirements
- User registration and login
- JWT authentication
- OAuth2 login
- Role-based access control
- User profile management
- Supported roles: Researcher, Startup Founder, Innovation Manager, Administrator

# Mentor Requirements
- Enforce strict public registration boundaries: public visitors can select only Researcher, Startup Founder, or Innovation Manager.
- Prohibit Administrator registration via public UI or API.
- Provide a secure server-side administrative CLI provisioning tool.
- Restrict phone number format and support token rotation and revocation.

# Current Implementation
- Complete stateless JWT access tokens (60-minute expiry) signed via `HS256`.
- High-entropy cryptographic refresh tokens (48 bytes) stored as SHA-256 hashes in PostgreSQL.
- Complete refresh token rotation on `/api/v1/auth/refresh` and revocation on logout.
- Bcrypt password hashing (12 rounds).
- Granular dependency injection guard `require_roles([UserRole.ADMINISTRATOR, ...])`.

# Frontend
- Route: `/login` in `frontend/src/app/(auth)/login/page.tsx` (Supports JSON credentials and OAuth2 form submission).
- Route: `/register` in `frontend/src/app/(auth)/register/page.tsx` (Wide responsive desktop grid, administrator role hidden).
- Token Management: `frontend/src/lib/auth.ts` and Axios interceptor in `frontend/src/lib/api.ts`.

# Backend
- Router: `backend/app/api/v1/endpoints/auth.py`
- Security Engine: `backend/app/core/security.py`
- Dependencies & Guards: `backend/app/core/deps.py`
- Admin CLI Provisioner: `backend/scripts/create_admin.py`

# Database
- Tables: `users` (id, email, hashed_password, full_name, phone, role, is_active, is_superuser), `refresh_tokens`.
- Migrations: `706d13f3e174` and `244ef6c34a82` (added phone column).

# APIs
- `POST /api/v1/auth/register` (HTTP 201)
- `POST /api/v1/auth/login` (HTTP 200)
- `POST /api/v1/auth/login/form` (HTTP 200)
- `POST /api/v1/auth/refresh` (HTTP 200)
- `POST /api/v1/auth/logout` (HTTP 200)
- `GET /api/v1/auth/me` & `PUT /api/v1/auth/me`
- `GET /api/v1/auth/test/*-only` (RBAC test endpoints)

# AI/ML
- None (Security and identity domain).

# External Data Sources
- None.

# Integration With Other Modules
- Injects `current_user` into every protected module endpoint.
- Isolates researcher profiles in Module 2 by linking `profiles.user_id == current_user.id`.
- Controls administrative governance access in Module 9 and Module 12.

# Testing
- `backend/tests/test_auth.py` (22 passing unit tests).
- `backend/tests/test_rbac.py` (2 passing RBAC authorization tests).

# Known Issues
- Third-party social OAuth buttons (Google/GitHub) are currently UI placeholders and not connected to live OAuth identity providers.

# Missing Requirements
- Live third-party OAuth2 social identity integration.

# Next Steps
- Implement Google/GitHub OAuth2 authentication if explicitly requested by project evaluators.

# Evidence / File Paths
- [auth.py](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/api/v1/endpoints/auth.py)
- [security.py](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/core/security.py)
- [deps.py](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/core/deps.py)
- [create_admin.py](file:///d:/Infosys%207.0/Intelligent-Research1/backend/scripts/create_admin.py)
- [login/page.tsx](file:///d:/Infosys%207.0/Intelligent-Research1/frontend/src/app/(auth)/login/page.tsx)
- [register/page.tsx](file:///d:/Infosys%207.0/Intelligent-Research1/frontend/src/app/(auth)/register/page.tsx)
