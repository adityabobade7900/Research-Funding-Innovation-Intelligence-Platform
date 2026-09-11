# 19_DASHBOARD_NOTIFICATIONS_REPORTS.md — Dashboards, Notifications & Reports

> **MODULE COVERAGE:**  
> • **Module 9:** Dashboard & Analytics  
> • **Module 10:** Notification & Alert System  
> • **Module 11:** Reports & Export System

---

## 1. Module 9: Dashboard & Analytics

### 1.1. Role-Tailored Operational Dashboards
The platform dynamically adjusts dashboard KPI metrics based on the active user's role (`researcher`, `startup_founder`, `innovation_manager`, `administrator`):

| Persona | Primary Displayed KPIs | Key Interactive Widgets | Backend API |
| :--- | :--- | :--- | :--- |
| **Researcher** | My Publications count, Target Grant Opportunities, Matched Funding Pool, Domain Hotspots | Recent publications list, Top matched grants with deadlines, Hotspot quick links | `GET /api/v1/command-center/overview` |
| **Startup Founder** | Commercial Readiness Index, Estimated TRL, Active Patents in Domain, Non-Dilutive Grant Pool | Commercialization roadmap, TRL progress bar, Competitor patent landscape summary | `GET /api/v1/command-center/overview` |
| **Innovation Manager** | Portfolio Innovation Score, Unpatented Whitespaces, Assignee Concentration (HHI), Grant Pipeline | Domain radar comparison, Whitespace gap alert cards, HHI market status badge | `GET /api/v1/command-center/overview` |
| **Administrator** | Total System Users, Active Harvester Pipelines, Database Health, Security Audit Log Entries | Pipeline telemetry toggles, User role updater modal, System audit log stream | `GET /api/v1/admin/system/overview` |

### 1.2. Command Center & Activity Feed
- Implemented in `backend/app/api/v1/endpoints/command_center.py`.
- **Activity Feed (`/activity-feed`):** Chronological stream combining newly published papers, active patent filings, and upcoming funding application deadlines.
- **Deadline Tracking:** Automatically highlights grants closing within the next 30 days.

---

## 2. Module 10: Notification & Alert System (Reality & Gap Audit)

> [!WARNING]
> **NOTIFICATION SYSTEM REALITY:**  
> Module 10 is currently **PARTIALLY IMPLEMENTED (40%)**.  
> In-app alerts exist visually on `/dashboard` and `/admin`, but the backend architecture for asynchronous notifications is incomplete.

### What is Actually Implemented:
1. **In-App Grant Deadline Alerts:** `CommandCenterService.get_activity_feed()` scans funding opportunities and triggers high-priority warning cards for solicitations closing within 30 days.
2. **Connector Pipeline Failure Alerts:** `AdminService.get_pipeline_telemetry()` surfaces warning alerts if OpenAlex, Grants.gov, or USPTO endpoints encounter network timeouts.

### What is Missing / Not Implemented:
1. **Standalone `Notification` Database Table:** No `notifications` table currently exists in PostgreSQL. Notifications are dynamically calculated on-the-fly from existing entity timestamps.
2. **Notification Preference Center:** No UI or API for users to toggle email vs push alerts.
3. **Outbound SMTP Email Dispatcher:** No email client configured to send automated grant reminders.
4. **Real-Time WebSocket Push:** No WebSocket endpoint; frontend relies on standard HTTP polling.

---

## 3. Module 11: Reports & Export System

### 3.1. Executive Dossier Synthesis
- Implemented in `backend/app/services/executive_report_service.py`.
- Endpoint: `GET /api/v1/reports/dossier`
- **Report Contents:**
  - Executive Summary & Evaluation Metadata
  - Research Velocity & Emerging Topics Breakdown
  - Patent Landscape & Competitor HHI Index
  - Technology Whitespace Opportunities
  - 5-Pillar Innovation Score & TRL Analysis
  - Commercialization Strategy & Recommended Pathways
  - Formal Governance & Legal Disclaimers

### 3.2. Export Formats Reality Check

| Export Format | Implementation Status | Technical Mechanism | Endpoint |
| :---: | :---: | :--- | :--- |
| **Markdown (`.md`)** | 🟢 **IMPLEMENTED** | Server-side template synthesis streaming formatted Markdown file with download headers | `GET /api/v1/reports/export/markdown` |
| **JSON (`.json`)** | 🟢 **IMPLEMENTED** | Complete structured data object exported directly for external data science pipelines | `GET /api/v1/reports/export/json` |
| **PDF (`.pdf`)** | 🟡 **PLANNED** | ReportLab / WeasyPrint binary PDF rendering specified in syllabus; not yet wired to endpoint | Planned for Milestone 4 |
| **Excel (`.xlsx`)** | 🟡 **PLANNED** | OpenPyXL multi-tab spreadsheet generation specified in syllabus; not yet wired to endpoint | Planned for Milestone 4 |
