# 30_CHANGELOG.md — Historical Project Changelog

This changelog records all verified milestone deliveries and major architectural modifications derived from commit history and codebase checkpoints.

---

### [2026-08-28] — Test Orchestration & Provider Hardening
- **Module:** Module 3 (Research Intelligence) & Module 4 (Funding Intelligence)
- **Change:** Added comprehensive unit test coverage for external harvester provider normalization, error handling (timeouts, rate limits, 404s), and service cascade logic.
- **Commit:** `fec6f56` — *test: add unit tests for research provider normalization, error handling, and service orchestration*
- **Status:** 🟢 **Verified & Tested**

---

### [2026-08-27] — Project Documentation & Overview Update
- **Module:** Cross-Platform Documentation
- **Change:** Expanded root `README.md` to detail end-to-end user roles, 12-module mapping, architecture diagrams, and testing metrics.
- **Commit:** `83672c0` — *Revise README.md to enhance project overview, expand table of contents, and detail key features and user roles*
- **Status:** 🟢 **Verified & Tested**

---

### [2026-08-26] — Registration UI Redesign & Grid Layout
- **Module:** Module 1 (User Authentication & RBAC)
- **Change:** Redesigned the Create Account / Registration page into a desktop-wide responsive grid layout, preserving color theme and form validation.
- **Commit:** `f531897` — *Enhance registration form layout and styling for improved user experience*
- **Status:** 🟢 **Verified & Tested**

---

### [2026-08-26] — Administrator Registration Security & CLI Provisioner
- **Module:** Module 1 (User Authentication & RBAC)
- **Change:** Prohibited public self-registration with `role=administrator` in both FastAPI backend and Next.js frontend. Added `backend/scripts/create_admin.py` CLI provisioning utility.
- **Commit:** `8e65194` — *Implement role-based restrictions for user registration and add admin provisioning script*
- **Status:** 🟢 **Verified & Tested**

---

### [2026-08-25] — Patent Management Modal & CRUD
- **Module:** Module 5 (Patent Landscape Analysis)
- **Change:** Added interactive patent editing modal with full form validation, assignee tracking, and classification inputs in `/patents`.
- **Commit:** `2969294` — *Add edit patent functionality with modal and form handling*
- **Status:** 🟢 **Verified & Tested**

---

### [2026-08-25] — Milestone 3: Patent, Whitespace & Innovation Scoring Delivery
- **Module:** Modules 5, 6, 7, 8
- **Change:** Delivered Patent Landscape Service (HHI index), Technology Intelligence Service (whitespace detection), Innovation Scoring Engine (exact 5-pillar formula), NASA TRL 1–9 engine, and Commercialization Recommendation pathways.
- **Commit:** `9d86c3e` — *Complete Module 1 and 2 compliance fixes and Milestone 3 analytics*
- **Status:** 🟢 **Verified & Tested**

---

### [2026-08-24] — Milestone 1 & 2: Core Foundation, Auth & Profile
- **Module:** Modules 1, 2, 3, 4
- **Change:** Initialized FastAPI backend, Next.js 14 frontend, PostgreSQL 16 database container, JWT authentication, refresh token rotation, 4 user roles, research profile management, and multi-provider harvesters.
- **Status:** 🟢 **Verified & Tested**
