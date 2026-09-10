# 10_AUTH_RBAC.md — Authentication & Role-Based Access Control (RBAC)

## 1. Authentication Architecture Overview

The platform implements a secure, stateless JWT authentication architecture with server-side refresh token rotation and revocation tracking in PostgreSQL:

- **Password Hashing:** Passlib with `bcrypt` (12 rounds) in `backend/app/core/security.py`.
- **JWT Signing:** Signed using `HS256` with `settings.JWT_SECRET` in `backend/app/core/security.py`.
- **Access Tokens:** Short-lived (60 minutes), containing `sub` (user ID), `role`, `iat`, and `exp`.
- **Refresh Tokens:** High-entropy cryptographic strings (48 bytes via `secrets.token_urlsafe(48)`). Stored as SHA-256 hashes in the `refresh_tokens` table.
- **Refresh Token Rotation:** Every refresh invalidates the old token and issues a new pair, preventing replay attacks.
- **Revocation / Logout:** Revocation sets `is_revoked = True` and records `revoked_at` timestamp.

---

## 2. Four Platform Roles & Permissions Matrix

| Permission / Capability | Researcher | Startup Founder | Innovation Manager | Administrator |
| :--- | :---: | :---: | :---: | :---: |
| **Manage Personal Profile & Facets** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Bookmark Publications & Patents** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Access Research Intelligence & Trends** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **View Funding & Match Recommendations** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **View Patent Landscape & Competitors** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **View Technology Whitespace** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Calculate Innovation Scores & TRL** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **View Commercialization Pathways** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Export Executive Dossiers (MD/JSON)** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Access Command Center Overview** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Access Admin Governance (`/admin`)** | ❌ Forbidden | ❌ Forbidden | ❌ Forbidden | ✅ Authorized |
| **Modify User Roles & Account Status** | ❌ Forbidden | ❌ Forbidden | ❌ Forbidden | ✅ Authorized |
| **View System Audit Logs & Telemetry** | ❌ Forbidden | ❌ Forbidden | ❌ Forbidden | ✅ Authorized |
| **Superuser Privileges (`is_superuser`)** | ❌ No | ❌ No | ❌ No | ✅ Supported |

---

## 3. Strict Administrator Registration Security

> [!IMPORTANT]
> **PREVENTION OF PRIVILEGE ESCALATION:**  
> In initial development, public registration allowed users to select the `Administrator` role. This vulnerability was fixed and strictly verified across both backend and frontend:
> 1. **Backend Enforcement (`app/api/v1/endpoints/auth.py` L49–54):**  
>    The `POST /api/v1/auth/register` endpoint explicitly rejects any registration request with `role == UserRole.ADMINISTRATOR`, returning HTTP 403 Forbidden (`Registration with Administrator role is forbidden`).
> 2. **Frontend UI Enforcement (`src/app/(auth)/register/page.tsx`):**  
>    The public registration card renders only 3 selectable roles: `Researcher`, `Startup Founder`, and `Innovation Manager`.
> 3. **Administrator Provisioning CLI (`backend/scripts/create_admin.py`):**  
>    Administrators must be provisioned directly via server-side database access using:
>    ```bash
>    python scripts/create_admin.py --email admin@platform.gov --password "Admin@2026Test!" --name "Platform Administrator"
>    ```

---

## 4. Key Security Source Files

| Feature | Implementation File Path | Key Functions / Classes |
| :--- | :--- | :--- |
| **Password Hashing** | [security.py](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/core/security.py#L13-L20) | `verify_password`, `get_password_hash` |
| **JWT Generation & Verification** | [security.py](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/core/security.py#L33-L57) | `create_access_token`, `decode_token` |
| **Token Hashing & Rotation** | [security.py](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/core/security.py#L23-L30) | `hash_token`, `generate_refresh_token_string` |
| **Database Session Dependency** | [deps.py](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/core/deps.py#L19-L30) | `get_db` (async generator with rollback) |
| **Current User Extraction** | [deps.py](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/core/deps.py#L32-L71) | `get_current_user`, `get_current_active_user` |
| **RBAC Role Guard Dependency** | [deps.py](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/core/deps.py#L97-L108) | `require_roles(allowed_roles)` |
| **Auth Endpoints Controller** | [auth.py](file:///d:/Infosys%207.0/Intelligent-Research1/backend/app/api/v1/endpoints/auth.py) | `register`, `login_json`, `refresh_token`, `logout` |
| **Admin Provisioning Script** | [create_admin.py](file:///d:/Infosys%207.0/Intelligent-Research1/backend/scripts/create_admin.py) | `provision_admin(email, password, name)` |

---

## 5. Automated Tests for Auth & RBAC

- `backend/tests/test_auth.py` (22 tests): Verifies registration, login validation, token issuance, token expiration handling, refresh token rotation, and invalid credential rejections.
- `backend/tests/test_rbac.py` (2 tests): Verifies role enforcement on `/auth/test/*-only` endpoints and confirms that non-administrators receive HTTP 403 when requesting administrative resources.
