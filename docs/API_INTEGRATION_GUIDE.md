# API Integration Guide

> **Base URL:** `https://sapio.onrender.com/api`  
> **Auth:** JWT Bearer Token — `Authorization: Bearer <access_token>`  
> **Content-Type:** `application/json`  
> **Pagination:** All list endpoints return 10 items per page. Use `?page=N` for pagination. Response shape: `{ count, next, previous, results }`.  
> **Render Note:** Free tier cold-starts in ~30s after inactivity. Handle with a loading state.

---

## Auth Flow

1. **Login** → `POST /auth/login/` with `{ username, password }` (no auth needed)  
   Returns `access` token (2h TTL), `refresh` token (24h TTL), plus `user`, `profile`, and `permissions` objects.  
   Store the tokens. Store `profile.role.name` for role-based UI decisions. Store `permissions[]` for module-level checks.

2. **Token Refresh** → `POST /auth/refresh/` with `{ refresh }` (no auth needed)  
   Returns a new `access` token. Call this when any request gets a `401`.

3. **Rehydrate on Reload** → `GET /auth/me/` (auth required)  
   Returns `user`, `profile`, `permissions` — same shape as login minus tokens. Call on app init if a stored token exists.

4. **Logout** → Clear stored tokens and redirect to login. No server-side endpoint needed.

---

## Permission Model

Every user has a **role** and a set of **module permissions** (returned at login).

**Roles & Scoping** — The backend auto-filters all list data based on role:

| Role | Sees |
|------|------|
| Admin | Everything |
| Regional Manager | Only their region's data |
| Team Lead | Only their team's data |
| Field Agent | Only tasks assigned to them |
| Auditor | Everything (read-only) |

**Module Permissions** — Each entry in the `permissions[]` array has:

```
{ module_name, can_create, can_read, can_update, can_delete }
```

Modules: `tasks`, `visits`, `logs`, `reports`, `users`. Use these booleans to show/hide UI elements (create buttons, edit forms, sidebar links, etc).

---

## Endpoints

### Tasks — `/tasks/`

| Action | Method & URL | Permission | Body |
|--------|-------------|------------|------|
| List | `GET /tasks/` | tasks.read | — |
| Detail | `GET /tasks/{id}/` | tasks.read | — |
| Create | `POST /tasks/` | tasks.create | `{ title, description, priority, due_date, assigned_to? }` |
| Update | `PATCH /tasks/{id}/` | tasks.update | Any subset of fields |
| Assign | `PATCH /tasks/{id}/assign/` | tasks.update | `{ assigned_to: <EmployeeProfile ID> }` |
| Delete | `DELETE /tasks/{id}/` | tasks.delete | — |

- `assigned_to` is an **EmployeeProfile ID** (not User ID). The backend auto-sets `team_scope` and `region_scope` from the assigned agent's profile.
- **Status values:** `pending`, `assigned`, `in_progress`, `completed`, `cancelled`
- **Priority values:** `low`, `medium`, `high`

---

### Visits — `/visits/`

| Action | Method & URL | Permission | Body |
|--------|-------------|------------|------|
| List | `GET /visits/` | visits.read | — |
| Detail | `GET /visits/{id}/` | visits.read | — |
| Start | `POST /visits/start/` | visits.create | `{ task_id }` |
| Complete | `POST /visits/{id}/complete/` | visits.update | `{ visit_notes }` |

- **Start** validates: task is assigned to you, task is not completed/cancelled, no active visit exists for the task.
- **Complete** triggers the Mock AI — response includes `ai_summary`, `ai_recommendation`, and `ai_risk_flag` (`low` / `medium` / `high`). Display these prominently in the Task Detail / Visit Detail page.

---

### Activity Logs — `/logs/`

| Action | Method & URL | Permission |
|--------|-------------|------------|
| List | `GET /logs/` | logs.read |
| Detail | `GET /logs/{id}/` | logs.read |

- **Not accessible to Field Agents.**
- **Filters:** `?action=completed`, `?entity_type=visit`, `?user__id=5` — combinable.
- Logs are auto-created by the backend. No write endpoints.

---

### Reports — `/reports/`

| Endpoint | Returns |
|----------|---------|
| `GET /reports/dashboard/` | Task counts by status + visit counts + high-risk count + last 5 activity logs |
| `GET /reports/pending-tasks/` | Pending tasks grouped by region & team |
| `GET /reports/task-distribution/` | Task status counts grouped by region |
| `GET /reports/recent-visits/` | Completed visits per day (last 7 days) |
| `GET /reports/completion-time/` | Average visit duration per agent (minutes) |

All require `reports.read`. All auto-scoped by role.

---

## Error Handling

| Status | Meaning | Suggested UX |
|--------|---------|-------------|
| `400` | Validation error — `detail` or field-level errors in body | Show inline form errors |
| `401` | Token expired or missing | Auto-refresh token; if refresh fails → force logout |
| `403` | Role lacks permission for this action | Show "Access Denied" |
| `404` | Resource not found or outside user's scope | Show 404 or redirect to list |

---

## Test Credentials

| Username | Password | Role | Scope |
|----------|----------|------|-------|
| `admin_user` | `admin123` | Admin | Global |
| `rm_north` | `pass123` | Regional Manager | North Region |
| `rm_south` | `pass123` | Regional Manager | South Region |
| `tl_alpha` | `pass123` | Team Lead | Team Alpha / North |
| `agent_ravi` | `pass123` | Field Agent | Team Alpha / North |
| `agent_priya` | `pass123` | Field Agent | Team Gamma / South |
| `auditor_meera` | `pass123` | Auditor | Global (read-only) |
