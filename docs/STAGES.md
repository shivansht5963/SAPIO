# 🚀 FFMS — Development Stages & Phases

> Execute stage-by-stage. Each stage has multiple phases.  
> Mark phases `[x]` as completed. Verification = curl + JSON format checks.  
> API docs maintained in `docs/API.md` · HTTP tests in `docs/test.http`

---

## Stage 1: Project Scaffolding & Database Models

> **Goal**: Django project skeleton, all apps created, all models defined, migrations run, admin registered.

### Phase 1.1 — Django Project Init
- [ ] Create Django project `ffms` inside the repo root
- [ ] Create Django apps: `accounts`, `tasks`, `visits`, `reports`, `logs`
- [ ] Configure `settings.py`: installed apps, database (SQLite for dev), REST framework, SimpleJWT
- [ ] Install dependencies: `djangorestframework`, `djangorestframework-simplejwt`, `django-cors-headers`
- [ ] Create `requirements.txt`

### Phase 1.2 — Core Models (`accounts`)
- [ ] `Role` model — name (Admin, Regional Manager, Team Lead, Field Agent, Auditor)
- [ ] `Region` model — name
- [ ] `Team` model — name, FK → Region
- [ ] `ModuleAccess` model — FK → Role, module_name, can_create, can_read, can_update, can_delete
- [ ] `EmployeeProfile` model — OneToOne → User, FK → Role, FK → Team (nullable), FK → Region (nullable)

### Phase 1.3 — Domain Models (`tasks`, `visits`, `logs`)
- [ ] `Task` model — title, description, created_by, assigned_to, status (choices), due_date, team_scope, region_scope, timestamps
- [ ] `Visit` model — FK → Task, started_by, status, start_time, end_time, visit_notes, ai_summary, ai_recommendation, ai_risk_flag
- [ ] `ActivityLog` model — FK → User, action, entity_type, entity_id, description, timestamp

### Phase 1.4 — Migrations & Admin
- [ ] Run `makemigrations` and `migrate`
- [ ] Register all models in `admin.py` for each app
- [ ] Create superuser
- [ ] Verify all tables created via Django admin panel

---

## Stage 2: Seed Data & Management Command

> **Goal**: Populate the DB with realistic sample data for all 5 roles so every endpoint can be tested immediately.

### Phase 2.1 — Seed Management Command
- [ ] Create `management/commands/seed_data.py` in `accounts` app
- [ ] Seed 5 Roles: Admin, Regional Manager, Team Lead, Field Agent, Auditor
- [ ] Seed 3 Regions: North, South, West
- [ ] Seed 5 Teams (spread across regions)
- [ ] Seed `ModuleAccess` rows for each Role × Module combo
- [ ] Seed 5+ Users with EmployeeProfiles (one per role minimum)
- [ ] Seed 8-10 Tasks (various statuses, assigned across teams)
- [ ] Seed 4-5 Visits (some started, some completed with notes)
- [ ] Seed 10+ ActivityLog entries
- [ ] Print sample credentials to console on completion

### Phase 2.2 — Verify Seed
- [ ] Run `python manage.py seed_data`
- [ ] Verify via Django admin that all data is present
- [ ] Document sample credentials in this file

**Sample Credentials** (populated after Phase 2.1):

| Username | Password | Role |
|---|---|---|
| `admin` | `admin123` | Admin |
| `rm_north` | `pass123` | Regional Manager |
| `tl_alpha` | `pass123` | Team Lead |
| `agent_ravi` | `pass123` | Field Agent |
| `auditor_priya` | `pass123` | Auditor |

---

## Stage 3: Authentication & RBAC APIs

> **Goal**: JWT login, token refresh, custom permission classes that enforce role + scope on every request.

### Phase 3.1 — JWT Auth Endpoints
- [ ] Configure SimpleJWT in `settings.py` (access token lifetime, refresh lifetime)
- [ ] `POST /api/auth/login/` — returns access + refresh tokens, user role, scope info
- [ ] `POST /api/auth/refresh/` — refresh access token
- [ ] `GET /api/auth/me/` — returns logged-in user profile, role, team, region, permissions
- [ ] Curl verify: login → get token → call `/me/` with Bearer token

### Phase 3.2 — Custom Permission Classes
- [ ] `IsAdmin` — allows only Admin role
- [ ] `IsManagerOrAbove` — Admin + Regional Manager
- [ ] `IsLeadOrAbove` — Admin + Regional Manager + Team Lead
- [ ] `IsFieldAgent` — only Field Agent
- [ ] `IsAuditor` — only Auditor (read-only)
- [ ] `ScopeFilterMixin` — a mixin/utility that filters querysets by the user's team/region automatically

### Phase 3.3 — Module Permission Middleware
- [ ] Utility function `check_module_access(user, module_name, action)` → reads `ModuleAccess` table
- [ ] Apply as a decorator or inline check in views that need module-level gating
- [ ] Curl verify: Agent trying to create a task → 403

**Curl Verification Checklist**:
```
✓ Login as admin       → 200 + tokens
✓ Login wrong password  → 401
✓ /me/ with valid token → 200 + profile
✓ /me/ without token    → 401
✓ Agent create task     → 403
```

---

## Stage 4: Task APIs

> **Goal**: Full task CRUD with scope-based filtering. Only users within scope can see/edit tasks.

### Phase 4.1 — Task Serializers
- [ ] `TaskListSerializer` — lightweight fields for list view
- [ ] `TaskDetailSerializer` — all fields, nested assigned_to and created_by info
- [ ] `TaskCreateSerializer` — validate required fields, auto-set created_by and scope fields
- [ ] `TaskAssignSerializer` — validate assigned_to is within creator's scope

### Phase 4.2 — Task Views & URLs
- [ ] `GET /api/tasks/` — list tasks (scoped by role: Agent sees own, Lead sees team, Manager sees region, Admin sees all)
- [ ] `POST /api/tasks/` — create task (Admin, Manager, Lead only)
- [ ] `GET /api/tasks/{id}/` — task detail (scoped)
- [ ] `PATCH /api/tasks/{id}/` — update task status/details
- [ ] `PATCH /api/tasks/{id}/assign/` — assign to agent (validate scope)
- [ ] Wire up URLs in `tasks/urls.py` → include in project `urls.py`

### Phase 4.3 — Scope Filtering Logic
- [ ] Admin: `Task.objects.all()`
- [ ] Regional Manager: `Task.objects.filter(region_scope=user.profile.region)`
- [ ] Team Lead: `Task.objects.filter(team_scope=user.profile.team)`
- [ ] Field Agent: `Task.objects.filter(assigned_to=user.profile)`
- [ ] Auditor: same as Admin but read-only

### Phase 4.4 — Curl Verify Tasks
- [ ] Create task as Team Lead → 201
- [ ] List tasks as Agent → only sees own assigned tasks
- [ ] List tasks as Admin → sees all
- [ ] Get task detail → 200 (in scope), 403/404 (out of scope)
- [ ] Assign task → 200 (valid agent in scope), 400 (agent not in scope)
- [ ] Update `test.http` with all task endpoints

---

## Stage 5: Visit APIs & Mock AI Integration

> **Goal**: Visit lifecycle (start → complete with notes → AI processing). Mock AI service behind clean abstraction.

### Phase 5.1 — Mock AI Service
- [ ] Create `services/ai_service.py` with `MockAIService` class
- [ ] Method: `generate_insights(notes: str) → dict` with summary, recommendation, risk_flag
- [ ] Keyword-based logic: high-risk words → High flag, medium → Medium, else → Low
- [ ] Keep it stateless and side-effect free (pure function)

### Phase 5.2 — Visit Serializers
- [ ] `VisitStartSerializer` — validate task exists and is assigned to the requesting agent
- [ ] `VisitCompleteSerializer` — requires visit_notes, triggers AI on save
- [ ] `VisitDetailSerializer` — all fields including AI outputs
- [ ] `VisitListSerializer` — lightweight for listing

### Phase 5.3 — Visit Views & URLs
- [ ] `POST /api/visits/{task_id}/start/` — create Visit with status=Started, start_time=now
- [ ] `POST /api/visits/{visit_id}/complete/` — save notes, call `MockAIService`, save AI output, set end_time
- [ ] `GET /api/visits/{visit_id}/` — view visit detail + AI outputs (scoped)
- [ ] `GET /api/visits/` — list visits (scoped by role, similar to tasks)
- [ ] Wire URLs

### Phase 5.4 — Curl Verify Visits
- [ ] Start visit as Agent → 201 + visit record
- [ ] Start visit on someone else's task → 403
- [ ] Complete visit with notes → 200 + AI fields populated
- [ ] Complete visit with "angry customer" note → risk_flag = High
- [ ] View visit detail → see AI summary, recommendation, risk_flag
- [ ] Update `test.http` with all visit endpoints

---

## Stage 6: Activity Logging

> **Goal**: Auto-log important actions. Expose log list endpoint for Admins and Auditors.

### Phase 6.1 — Activity Log Service
- [ ] Create `services/activity_logger.py` with utility function:
  `log_activity(user, action, entity_type, entity_id, description)`
- [ ] Call this from Task views (created, assigned, status_changed)
- [ ] Call this from Visit views (started, completed)

### Phase 6.2 — Log API
- [ ] `GET /api/logs/` — paginated list of ActivityLogs
- [ ] Access: Admin sees all, Manager sees region, Lead sees team, Auditor sees all (read-only)
- [ ] Support query params: `?entity_type=Task`, `?action=created`, `?user_id=X`

### Phase 6.3 — Curl Verify Logs
- [ ] Create a task → check log entry exists
- [ ] Complete a visit → check log entry exists
- [ ] Fetch logs as Auditor → 200 + list
- [ ] Fetch logs as Agent → 403
- [ ] Update `test.http`

---

## Stage 7: Reports & Dashboard APIs

> **Goal**: Backend endpoints for the 4 SQL reporting use cases + dashboard summary.

### Phase 7.1 — Reporting Queries
- [ ] `GET /api/reports/pending-tasks/` — Pending tasks grouped by region + team
- [ ] `GET /api/reports/completion-time/` — Avg visit completion time per agent
- [ ] `GET /api/reports/recent-visits/` — Visits completed in last 7 days (daily breakdown)
- [ ] `GET /api/reports/task-distribution/` — Task status count grouped by region

### Phase 7.2 — Dashboard Endpoint
- [ ] `GET /api/reports/dashboard/` — returns scoped summary:
  - Total tasks (by status counts)
  - Total visits (completed vs pending)
  - High-risk visit count
  - Recent activity (last 5 logs)
- [ ] Scoped: Admin/Auditor = global, Manager = region, Lead = team, Agent = self

### Phase 7.3 — Curl Verify Reports
- [ ] Hit each report endpoint as Admin → valid JSON with grouped data
- [ ] Hit dashboard as Agent → only self-scoped stats
- [ ] Update `test.http`

---

## Stage 8: API Documentation & HTTP Test File

> **Goal**: Comprehensive API doc and a ready-to-use `.http` test file with every endpoint.

### Phase 8.1 — API Documentation
- [ ] Create/update `docs/API.md` with every endpoint:
  - Method, URL, Auth, Request body, Response body, Status codes
- [ ] Group by module: Auth, Tasks, Visits, Logs, Reports

### Phase 8.2 — test.http File
- [ ] Create `docs/test.http` with all endpoints organized by section
- [ ] Include `@baseUrl`, `@token` variables at top
- [ ] Login request that captures token
- [ ] Every endpoint with sample body, headers, and comments
- [ ] Separate sections: Auth, Tasks, Visits, Logs, Reports

---

## Stage 9: Frontend Setup & Auth

> **Goal**: React app scaffolded, login page functional, JWT stored, protected routes in place.

### Phase 9.1 — React Project Init
- [ ] Create React app (Vite) in `frontend/` directory
- [ ] Install dependencies: `axios`, `react-router-dom`
- [ ] Set up project structure: `components/`, `pages/`, `services/`, `context/`
- [ ] Configure Axios instance with base URL + JWT interceptor
- [ ] Set up CORS on Django backend

### Phase 9.2 — Auth Context & Login Page
- [ ] Create `AuthContext` — stores token, user info, role, permissions
- [ ] Login page — form → calls `/api/auth/login/` → stores token in localStorage + context
- [ ] Logout — clears token, redirects to login
- [ ] `ProtectedRoute` component — checks auth, redirects if not logged in

### Phase 9.3 — Role-Aware Layout
- [ ] Sidebar/Navigation component — dynamically shows links based on role:
  - Admin: Dashboard, Tasks, Visits, Logs, Reports, Users
  - Manager: Dashboard, Tasks, Visits, Reports
  - Lead: Dashboard, Tasks, Visits
  - Agent: Dashboard, My Tasks, My Visits
  - Auditor: Dashboard, Logs, Reports
- [ ] Main layout wrapper with sidebar + content area
- [ ] Basic routing for all pages (placeholder components)

---

## Stage 10: Frontend Core Pages

> **Goal**: Dashboard, task list, task detail, visit form — all connected to backend APIs.

### Phase 10.1 — Dashboard Page
- [ ] Fetch `/api/reports/dashboard/` on mount
- [ ] Display stat cards: total tasks, pending, completed, visits today, high-risk flags
- [ ] Scoped automatically by backend

### Phase 10.2 — Task List Page
- [ ] Fetch `/api/tasks/` with pagination
- [ ] Table/list view with columns: title, status, assigned_to, due_date
- [ ] Status filter dropdown
- [ ] "Create Task" button (visible only if role permits)
- [ ] Click row → navigate to task detail

### Phase 10.3 — Task Detail Page
- [ ] Fetch `/api/tasks/{id}/`
- [ ] Display all task fields
- [ ] "Assign" action (if permitted) — dropdown of agents in scope
- [ ] "Start Visit" button (if Agent + task assigned to them + no active visit)
- [ ] Show linked visit if exists (status, times, notes)

### Phase 10.4 — Visit Update Form
- [ ] "Start Visit" → `POST /api/visits/{task_id}/start/`
- [ ] "Complete Visit" form → textarea for notes → `POST /api/visits/{visit_id}/complete/`
- [ ] After completion, display AI summary panel:
  - Summary text
  - Recommendation
  - Risk flag (color-coded badge: green/yellow/red)

---

## Stage 11: Frontend Reports, Logs & Polish

> **Goal**: Reports page, activity logs page, final integration polish.

### Phase 11.1 — Reports Page
- [ ] Pending tasks by region/team — table view
- [ ] Avg completion time per agent — table view
- [ ] Recent visits (7 days) — table or simple list
- [ ] Task distribution — table grouped by region + status

### Phase 11.2 — Activity Logs Page
- [ ] Fetch `/api/logs/` with pagination
- [ ] Table: timestamp, user, action, entity, description
- [ ] Filter by entity_type, action
- [ ] Visible only to Admin + Auditor

### Phase 11.3 — Final Polish
- [ ] Error handling on all API calls (toast/alert on 4xx/5xx)
- [ ] Loading states (spinners/skeletons)
- [ ] Empty states ("No tasks found")
- [ ] Role-based button/action visibility reviewed on every page
- [ ] Cross-check: every backend endpoint is consumed by at least one frontend page

---

## Stage 12: README & Final Documentation

> **Goal**: Submission-ready repository with clear instructions.

### Phase 12.1 — README.md
- [ ] Project overview (1 paragraph)
- [ ] Tech stack summary
- [ ] Setup instructions: clone, install deps, migrate, seed, run backend, run frontend
- [ ] Sample credentials table
- [ ] Architecture overview (brief)
- [ ] Assumptions and tradeoffs

### Phase 12.2 — Final File Audit
- [ ] Verify `docs/PRD.md` is up to date
- [ ] Verify `docs/SRS.md` is up to date
- [ ] Verify `docs/PROJECT_DETAILS.md` is up to date
- [ ] Verify `docs/API.md` is complete with all endpoints
- [ ] Verify `docs/test.http` covers all endpoints
- [ ] Verify seed data works on a fresh DB

---

## Summary: Stage → Deliverable Map

| Stage | Primary Deliverable | Approx Effort |
|---|---|---|
| **1** | Django project + all models + migrations | 2-3 hrs |
| **2** | Seed data command + sample users | 1 hr |
| **3** | JWT auth + RBAC permission classes | 2-3 hrs |
| **4** | Task CRUD APIs (scoped) | 2-3 hrs |
| **5** | Visit APIs + MockAIService | 2-3 hrs |
| **6** | Activity logging service + API | 1-2 hrs |
| **7** | Reports + Dashboard APIs | 2 hrs |
| **8** | API.md + test.http | 1 hr |
| **9** | React setup + Auth + Layout | 2-3 hrs |
| **10** | Frontend core pages (Dashboard, Tasks, Visits) | 3-4 hrs |
| **11** | Frontend Reports, Logs, Polish | 2-3 hrs |
| **12** | README + final docs | 1 hr |
| | **Total Estimated** | **~22-28 hrs** |
