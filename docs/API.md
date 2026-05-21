# FFMS API Documentation

> **Field Force Management System (FFMS)** — Backend REST API  
> Base URL: `http://127.0.0.1:8000/api`  
> Authentication: JWT Bearer Token (obtain via `/api/auth/login/`)  
> Content-Type: `application/json`

---

## Table of Contents

1. [Auth](#1-auth)
2. [Tasks](#2-tasks)
3. [Visits](#3-visits)
4. [Activity Logs](#4-activity-logs)
5. [Reports & Dashboard](#5-reports--dashboard)

---

## Role-Based Access Summary

| Role | Tasks | Visits | Logs | Reports | Notes |
|---|---|---|---|---|---|
| `admin` | CRUD | CRUD | CRUD | Read | Full access |
| `regional_manager` | CRU | CRU | Read | Read | Scoped to their region |
| `team_lead` | CRU | CRU | Read | Read | Scoped to their team |
| `field_agent` | Read | CRU | — | Read (dashboard only) | Scoped to tasks assigned to them |
| `auditor` | Read | Read | Read | Read | Global read-only access |

> All list endpoints automatically scope results based on the authenticated user's role.

---

## 1. Auth

### POST /api/auth/login/
Obtain a JWT access + refresh token pair.

**Auth required:** No

**Request Body:**
```json
{
  "username": "tl_alpha",
  "password": "pass123"
}
```

**Response `200 OK`:**
```json
{
  "access": "<jwt_access_token>",
  "refresh": "<jwt_refresh_token>",
  "user": {
    "id": 4,
    "username": "tl_alpha",
    "role": "team_lead",
    "team": "Team Alpha",
    "region": "North Region"
  }
}
```

**Errors:**
| Status | Reason |
|---|---|
| `400` | Missing username or password |
| `401` | Invalid credentials |

---

### POST /api/auth/refresh/
Obtain a new access token using a refresh token.

**Auth required:** No

**Request Body:**
```json
{
  "refresh": "<jwt_refresh_token>"
}
```

**Response `200 OK`:**
```json
{
  "access": "<new_jwt_access_token>"
}
```

---

### GET /api/auth/me/
Get the profile of the currently authenticated user.

**Auth required:** Yes (any role)

**Response `200 OK`:**
```json
{
  "id": 4,
  "username": "tl_alpha",
  "email": "tl.alpha@ffms.com",
  "first_name": "Tl",
  "role": "team_lead",
  "team": "Team Alpha",
  "region": "North Region",
  "employee_id": "EMP-004",
  "phone": "9000000004"
}
```

---

## 2. Tasks

### GET /api/tasks/
List all tasks. Results are automatically scoped by the user's role.

**Auth required:** Yes — `tasks.read`

**Query Params:** None (scoping is automatic)

**Response `200 OK`:**
```json
[
  {
    "id": 1,
    "title": "Site inspection at Warehouse A",
    "status": "assigned",
    "priority": "high",
    "due_date": "2026-05-23",
    "assigned_to": {
      "id": 1,
      "employee_id": "EMP-005",
      "username": "agent_ravi"
    },
    "team_scope": "Team Alpha",
    "region_scope": "North Region"
  }
]
```

---

### POST /api/tasks/
Create a new task.

**Auth required:** Yes — `tasks.create` (admin, regional_manager, team_lead)

**Request Body:**
```json
{
  "title": "New Site Visit",
  "description": "Inspect the new site for compliance.",
  "priority": "high",
  "due_date": "2026-06-01",
  "assigned_to": 5
}
```
> `assigned_to` is an `EmployeeProfile` ID. `team_scope` and `region_scope` are automatically set from the assigned agent's profile.

**Response `201 Created`:**
```json
{
  "id": 11,
  "title": "New Site Visit",
  "status": "pending",
  "priority": "high",
  "due_date": "2026-06-01",
  "assigned_to": {...},
  "team_scope": "Team Alpha",
  "region_scope": "North Region",
  "created_at": "2026-05-21T...",
  "updated_at": "2026-05-21T..."
}
```

**Errors:**
| Status | Reason |
|---|---|
| `400` | Missing required fields (`title`, `description`, `due_date`) |
| `403` | Role does not have `tasks.create` permission |

---

### GET /api/tasks/{id}/
Get full detail of a single task.

**Auth required:** Yes — `tasks.read`

**Response `200 OK`:** Full task object including `visit_count`, `created_by`.

---

### PATCH /api/tasks/{id}/
Partially update a task (e.g. change status or priority).

**Auth required:** Yes — `tasks.update`

**Request Body (any subset):**
```json
{
  "status": "completed",
  "priority": "low"
}
```

---

### DELETE /api/tasks/{id}/
Delete a task.

**Auth required:** Yes — `tasks.delete` (admin only)

---

### PATCH /api/tasks/{id}/assign/
Assign or reassign a task to a different field agent.

**Auth required:** Yes — `tasks.update`

**Request Body:**
```json
{
  "assigned_to": 6
}
```

> Automatically updates `team_scope` and `region_scope` to match the new agent's profile.

**Response `200 OK`:** Full task detail object.

---

## 3. Visits

### GET /api/visits/
List all visits. Scoped by the user's role (via the related task's team/region).

**Auth required:** Yes — `visits.read`

**Response `200 OK`:**
```json
[
  {
    "id": 1,
    "task": { "id": 3, "title": "Equipment delivery verification", "status": "completed" },
    "started_by": { "id": 1, "username": "agent_ravi", "employee_id": "EMP-005" },
    "status": "completed",
    "start_time": "2026-05-20T15:00:00Z",
    "end_time": "2026-05-20T17:00:00Z",
    "ai_risk_flag": "low"
  }
]
```

---

### POST /api/visits/start/
Start a new visit for a task assigned to the current user.

**Auth required:** Yes — `visits.create` (field_agent)

**Request Body:**
```json
{
  "task_id": 1
}
```

**Validations:**
- Task must be assigned to the requesting user
- Task must not be `completed` or `cancelled`
- No active (`started`) visit can already exist for the task

**Response `201 Created`:** Full visit detail object.

**Errors:**
| Status | Reason |
|---|---|
| `400` | Task not assigned to you, task already completed, or active visit exists |
| `403` | Role does not have `visits.create` permission |

---

### POST /api/visits/{id}/complete/
Complete an ongoing visit and trigger Mock AI analysis on the notes.

**Auth required:** Yes — `visits.update`

**Request Body:**
```json
{
  "visit_notes": "Customer was cooperative. All documentation signed."
}
```

**Response `200 OK`:**
```json
{
  "id": 1,
  "status": "completed",
  "visit_notes": "Customer was cooperative...",
  "ai_risk_flag": "low",
  "ai_summary": "The visit was routine with no significant issues reported.",
  "ai_recommendation": "No immediate action needed. Standard 7-day follow-up recommended.",
  "end_time": "2026-05-21T08:30:00Z"
}
```

**AI Risk Flag Logic (Mock):**
| Keywords in Notes | Risk Flag |
|---|---|
| `angry`, `escalate`, `urgent`, `refused`, `injury` | `high` |
| `delayed`, `issue`, `problem`, `pending`, `reschedule` | `medium` |
| Anything else | `low` |

---

### GET /api/visits/{id}/
Get full detail of a single visit including AI outputs.

**Auth required:** Yes — `visits.read`

---

## 4. Activity Logs

### GET /api/logs/
List all activity logs. Scoped by the user's role.

**Auth required:** Yes — `logs.read` (admin, auditor, regional_manager, team_lead)

> ⚠️ Field agents cannot access logs.

**Query Params:**

| Param | Type | Example |
|---|---|---|
| `action` | string | `?action=completed` |
| `entity_type` | string | `?entity_type=visit` |
| `user__id` | integer | `?user__id=5` |

**Response `200 OK`:**
```json
[
  {
    "id": 12,
    "user_profile": {
      "id": 1,
      "employee_id": "EMP-005",
      "username": "agent_ravi",
      "first_name": "Agent",
      "role_name": "field_agent"
    },
    "action": "completed",
    "entity_type": "visit",
    "entity_id": 3,
    "description": "Visit completed for task 3.",
    "timestamp": "2026-05-21T08:30:00Z"
  }
]
```

**Actions logged automatically:**

| Trigger | `action` | `entity_type` |
|---|---|---|
| Task created | `created` | `task` |
| Task assigned | `assigned` | `task` |
| Task status changed | `status_changed` | `task` |
| Visit started | `started` | `visit` |
| Visit completed | `completed` | `visit` |

---

### GET /api/logs/{id}/
Get a single activity log entry.

**Auth required:** Yes — `logs.read`

---

## 5. Reports & Dashboard

> All report endpoints respect the same role-based scoping as Tasks/Visits.  
> Admin and Auditor see global data. Manager sees region. Lead sees team. Agent sees self.

### GET /api/reports/pending-tasks/
Pending tasks grouped by region and team.

**Auth required:** Yes — `reports.read`

**Response `200 OK`:**
```json
[
  { "region_name": "North Region", "team_name": "Team Alpha", "pending_count": 3 },
  { "region_name": "South Region", "team_name": "Team Gamma", "pending_count": 1 }
]
```

---

### GET /api/reports/task-distribution/
Task status counts grouped by region.

**Auth required:** Yes — `reports.read`

**Response `200 OK`:**
```json
[
  { "region_name": "North Region", "task_status": "completed", "count": 5 },
  { "region_name": "North Region", "task_status": "pending", "count": 3 },
  { "region_name": "South Region", "task_status": "in_progress", "count": 2 }
]
```

---

### GET /api/reports/recent-visits/
Visits completed in the last 7 days, broken down by day.

**Auth required:** Yes — `reports.read`

**Response `200 OK`:**
```json
[
  { "date": "2026-05-19", "completed_count": 2 },
  { "date": "2026-05-20", "completed_count": 5 },
  { "date": "2026-05-21", "completed_count": 1 }
]
```

---

### GET /api/reports/completion-time/
Average visit completion time per agent (in minutes).

**Auth required:** Yes — `reports.read`

**Response `200 OK`:**
```json
[
  {
    "agent_username": "agent_priya",
    "agent_employee_id": "EMP-006",
    "visit_count": 3,
    "avg_completion_minutes": 142.5
  },
  {
    "agent_username": "agent_ravi",
    "agent_employee_id": "EMP-005",
    "visit_count": 4,
    "avg_completion_minutes": 98.2
  }
]
```

---

### GET /api/reports/dashboard/
Comprehensive summary dashboard. Scoped to the requesting user's role.

**Auth required:** Yes — `reports.read`

**Response `200 OK`:**
```json
{
  "tasks": {
    "total": 22,
    "by_status": {
      "pending": 9,
      "in_progress": 5,
      "completed": 6,
      "assigned": 2,
      "cancelled": 0
    }
  },
  "visits": {
    "total": 12,
    "completed": 8,
    "started": 4,
    "high_risk": 3
  },
  "recent_activity": [
    {
      "id": 18,
      "user_profile": { "username": "agent_ravi", ... },
      "action": "completed",
      "entity_type": "visit",
      "entity_id": 12,
      "description": "Visit completed for task 22.",
      "timestamp": "2026-05-21T..."
    }
  ]
}
```

---

## Common HTTP Status Codes

| Code | Meaning |
|---|---|
| `200` | Success |
| `201` | Created |
| `400` | Bad Request — validation error |
| `401` | Unauthorized — missing or invalid token |
| `403` | Forbidden — insufficient role permissions |
| `404` | Not Found |
| `500` | Server Error |

---

## Sample Credentials (Dev/Seed Data)

| Username | Password | Role |
|---|---|---|
| `admin_user` | `admin123` | Admin |
| `rm_north` | `pass123` | Regional Manager (North) |
| `rm_south` | `pass123` | Regional Manager (South) |
| `tl_alpha` | `pass123` | Team Lead (Team Alpha) |
| `agent_ravi` | `pass123` | Field Agent (Team Alpha) |
| `agent_priya` | `pass123` | Field Agent (Team Gamma) |
| `auditor_meera` | `pass123` | Auditor |
