# 📋 Field Force Management System — Master Project Details

> **Assignment**: Full Stack Developer Interview Assignment  
> **Preferred Stack**: Django · React · PostgreSQL  
> **Completion Target**: 3 Days  
> **Last Updated**: May 2026

---

## Table of Contents
1. [Project Vision & Overview](#1-project-vision--overview)
2. [Target Audience & User Roles](#2-target-audience--user-roles)
3. [Core Features (PRD)](#3-core-features-prd)
4. [User Stories](#4-user-stories)
5. [Technology Stack & Architecture (SRS)](#5-technology-stack--architecture-srs)
6. [Database Schema & Entities](#6-database-schema--entities)
7. [API Specifications](#7-api-specifications)
8. [Mock AI Service](#8-mock-ai-service)
9. [SQL Reporting Use Cases](#9-sql-reporting-use-cases)
10. [UI/UX Expectations](#10-uiux-expectations)
11. [Final Outcomes & Deliverables](#11-final-outcomes--deliverables)
12. [Project Constraints & Assumptions](#12-project-constraints--assumptions)

---

## 1. Project Vision & Overview

The **Field Force Management System (FFMS)** is a role-based, modular web platform designed to manage and track the operations of a distributed field team. The system enables managers to assign and monitor tasks, while field agents seamlessly track and update their on-site visits.

Key pillars:
- **Strict Role-Based Access Control (RBAC)** — every action is gated by role and permission.
- **Scope-Based Data Visibility** — users only see data pertaining to their team, region, or themselves.
- **Mock AI Integration** — an isolated AI-like service generates visit summaries and recommendations from field notes.
- **Complete Audit Trail** — every significant action is logged for compliance and review.

---

## 2. Target Audience & User Roles

| Role | Scope | Can Create/Edit | Can View |
|---|---|---|---|
| **Admin** | System-wide | Users, Roles, Teams, Tasks, Visits | Everything |
| **Regional Manager** | Own Region/Zone | Tasks, Assignments in their region | Regional tasks, agents, reports, logs |
| **Team Lead** | Own Team | Tasks, Assignments for team members | Team tasks, team visits, team logs |
| **Field Agent** | Self only | Own visit notes & status updates | Own assigned tasks and visits |
| **Auditor** | Global (Read-Only) | Nothing | All logs, reports, and visit outcomes |

---

## 3. Core Features (PRD)

### 3.1 Authentication & Role-Based Access Control
- JWT-based stateless authentication.
- Role and Module permission checks on every protected API endpoint.
- Login returns JWT token along with user's Role, Scope, and permitted modules.

### 3.2 Task Management
- **Create Task**: Available to Admin, Regional Manager, Team Lead (within scope).
- **Assign Task**: Assign to a Field Agent within the creator's scope.
- **Update Task Status**: Lifecycle — `Pending → Assigned → In Progress → Completed / Cancelled`.
- **List Tasks**: Filtered by role and scope automatically by the backend.

### 3.3 Visit Tracking
- **Start Visit**: Agent creates a visit record linked to a task with a `start_time`.
- **Complete Visit**: Agent submits notes and marks the visit complete; triggers AI processing.
- **Visit Outcome**: Status updated, `end_time` recorded, AI outputs stored alongside raw notes.

### 3.4 Scope-Based Visibility
- All DB queries inject a scope filter based on the JWT user's profile.
- API-level enforcement: unauthorized access returns `403 Forbidden`.

### 3.5 Activity Logging
Auto-generated logs for:
- Task created, assigned, status changed
- Visit started, visit completed
- Any permission violation attempts

### 3.6 Mock AI Integration
- Triggered automatically when visit notes are submitted on completion.
- Generates: **Visit Summary**, **Follow-Up Recommendation**, **Risk Flag** (Low / Medium / High).
- Placed behind a clean service abstraction (`MockAIService`) swappable for a real LLM provider.
- Both raw notes and AI output are stored in the `Visit` table.

---

## 4. User Stories

### Field Agent
- *As a Field Agent, I want to view my assigned tasks for the day.*
- *As a Field Agent, I want to start and complete a visit and log my notes.*
- *As a Field Agent, I want to see the AI-generated summary and follow-up for my submitted notes.*

### Team Lead
- *As a Team Lead, I want to create tasks and assign them to agents on my team.*
- *As a Team Lead, I want a dashboard view showing my team's task completion rates.*
- *As a Team Lead, I want to see activity logs for my team members.*

### Regional Manager
- *As a Regional Manager, I want to see all tasks across my region with filtering.*
- *As a Regional Manager, I want a report showing agents' average completion time.*

### Admin
- *As an Admin, I want to manage all users, roles, teams, and regions.*
- *As an Admin, I want full visibility into all logs and reports.*

### Auditor
- *As an Auditor, I want read-only access to all activity logs and visit outcomes.*

---

## 5. Technology Stack & Architecture (SRS)

### 5.1 Technology Stack

| Layer | Technology |
|---|---|
| Backend | Django + Django REST Framework (DRF) |
| Frontend | React (Vite or CRA) + Axios |
| Database | PostgreSQL (preferred) or MySQL |
| Auth | JWT (`djangorestframework-simplejwt`) |
| AI Service | Mocked Python module (`services/ai_service.py`) |

### 5.2 System Architecture

```
┌──────────────────────┐         ┌──────────────────────────────────────┐
│   React Frontend     │ ──API── │         Django Backend               │
│  (Role-aware SPA)    │         │  ┌────────────┐  ┌────────────────┐  │
└──────────────────────┘         │  │ Auth/JWT   │  │ Scope Filter   │  │
                                 │  └────────────┘  └────────────────┘  │
                                 │  ┌──────────────────────────────────┐ │
                                 │  │ Business Logic (Tasks, Visits)   │ │
                                 │  └──────────────────────────────────┘ │
                                 │  ┌───────────────┐                    │
                                 │  │ MockAIService │                    │
                                 │  └───────────────┘                    │
                                 └──────────────────────────────────────┘
                                              │
                                 ┌────────────────────┐
                                 │   PostgreSQL DB    │
                                 └────────────────────┘
```

---

## 6. Database Schema & Entities

### `users` / `auth_user`
| Field | Type | Notes |
|---|---|---|
| id | PK | Auto |
| username | VARCHAR | Unique |
| email | VARCHAR | Unique |
| password | HASH | bcrypt |
| is_active | BOOL | |

### `roles`
| Field | Type | Notes |
|---|---|---|
| id | PK | |
| name | VARCHAR | Admin, Regional Manager, Team Lead, Field Agent, Auditor |

### `module_access` (Permissions)
| Field | Type | Notes |
|---|---|---|
| id | PK | |
| role | FK → roles | |
| module_name | VARCHAR | tasks, visits, logs, reports |
| can_create | BOOL | |
| can_read | BOOL | |
| can_update | BOOL | |
| can_delete | BOOL | |

### `regions`
| Field | Type | Notes |
|---|---|---|
| id | PK | |
| name | VARCHAR | e.g., North, South |

### `teams`
| Field | Type | Notes |
|---|---|---|
| id | PK | |
| name | VARCHAR | |
| region | FK → regions | |

### `employee_profiles`
| Field | Type | Notes |
|---|---|---|
| id | PK | |
| user | OneToOne → auth_user | |
| role | FK → roles | |
| team | FK → teams (nullable) | |
| region | FK → regions (nullable) | |

### `tasks`
| Field | Type | Notes |
|---|---|---|
| id | PK | |
| title | VARCHAR | |
| description | TEXT | |
| created_by | FK → employee_profiles | |
| assigned_to | FK → employee_profiles | |
| status | ENUM | Pending, Assigned, In Progress, Completed, Cancelled |
| due_date | DATE | |
| team_scope | FK → teams (nullable) | |
| region_scope | FK → regions (nullable) | |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

### `visits`
| Field | Type | Notes |
|---|---|---|
| id | PK | |
| task | FK → tasks | |
| started_by | FK → employee_profiles | |
| status | ENUM | Started, Completed |
| start_time | TIMESTAMP | |
| end_time | TIMESTAMP (nullable) | |
| visit_notes | TEXT (nullable) | Raw notes from agent |
| ai_summary | TEXT (nullable) | Generated by MockAIService |
| ai_recommendation | TEXT (nullable) | Generated by MockAIService |
| ai_risk_flag | VARCHAR | Low / Medium / High |

### `activity_logs`
| Field | Type | Notes |
|---|---|---|
| id | PK | |
| user | FK → auth_user | |
| action | VARCHAR | created, assigned, started, completed, status_changed |
| entity_type | VARCHAR | Task, Visit |
| entity_id | INT | |
| description | TEXT | Human-readable log message |
| timestamp | TIMESTAMP | Auto-set |

---

## 7. API Specifications

### Authentication
| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/api/auth/login/` | Public | Get JWT tokens |
| POST | `/api/auth/refresh/` | Public | Refresh access token |

### Tasks
| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/api/tasks/` | All roles | List tasks (scoped) |
| POST | `/api/tasks/` | Admin, Manager, Lead | Create a task |
| GET | `/api/tasks/{id}/` | All roles (scoped) | Task detail |
| PATCH | `/api/tasks/{id}/` | Admin, Manager, Lead | Update task details |
| PATCH | `/api/tasks/{id}/assign/` | Admin, Manager, Lead | Assign to agent |

### Visits
| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/api/visits/{task_id}/start/` | Field Agent | Start a visit |
| POST | `/api/visits/{visit_id}/complete/` | Field Agent | Complete + submit notes → triggers AI |
| GET | `/api/visits/{visit_id}/` | Manager, Lead, Agent (scoped) | View visit details + AI output |

### Reports & Logs
| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/api/reports/dashboard/` | All (scoped) | Aggregated summary stats |
| GET | `/api/reports/pending-tasks/` | Manager, Admin | Pending tasks grouped by team/region |
| GET | `/api/reports/completion-time/` | Manager, Admin, Auditor | Avg completion time per agent |
| GET | `/api/logs/` | Admin, Auditor | Paginated activity logs |

---

## 8. Mock AI Service

The AI service is decoupled behind a service class. **No real LLM or paid API is used.**

```python
# backend/services/ai_service.py

class MockAIService:
    """
    Mocked AI integration for visit note analysis.
    Can be replaced with a real OpenAI/Anthropic call without
    changing the interface.
    """

    @staticmethod
    def generate_insights(notes: str) -> dict:
        notes_lower = notes.lower()
        word_count = len(notes.split())

        # Deterministic summary
        summary = (
            f"Agent reported: '{notes[:80]}...'"
            if len(notes) > 80
            else f"Agent reported: '{notes}'"
        )

        # Risk flag logic
        high_risk_keywords = ["angry", "cancel", "refused", "complaint", "issue", "problem"]
        medium_risk_keywords = ["delay", "reschedule", "unavailable", "busy"]

        if any(kw in notes_lower for kw in high_risk_keywords):
            risk_flag = "High"
            recommendation = "Immediate escalation required. Notify Team Lead within 24 hours."
        elif any(kw in notes_lower for kw in medium_risk_keywords):
            risk_flag = "Medium"
            recommendation = "Schedule a follow-up visit within 3 business days."
        else:
            risk_flag = "Low"
            recommendation = "No immediate action needed. Standard 7-day follow-up recommended."

        return {
            "summary": summary,
            "recommendation": recommendation,
            "risk_flag": risk_flag,
            "note_length": word_count,
        }
```

---

## 9. SQL Reporting Use Cases

### Query 1: Pending Tasks by Region / Team
```sql
SELECT
    r.name AS region,
    t.name AS team,
    COUNT(tk.id) AS pending_tasks
FROM tasks tk
JOIN teams t ON tk.team_scope_id = t.id
JOIN regions r ON t.region_id = r.id
WHERE tk.status NOT IN ('Completed', 'Cancelled')
GROUP BY r.name, t.name
ORDER BY pending_tasks DESC;
```

### Query 2: Average Visit Completion Time per Field Agent
```sql
SELECT
    u.username AS agent,
    ROUND(AVG(EXTRACT(EPOCH FROM (v.end_time - v.start_time)) / 60), 2) AS avg_duration_minutes
FROM visits v
JOIN tasks tk ON v.task_id = tk.id
JOIN employee_profiles ep ON tk.assigned_to_id = ep.id
JOIN auth_user u ON ep.user_id = u.id
WHERE v.status = 'Completed'
GROUP BY u.username
ORDER BY avg_duration_minutes;
```

### Query 3: Visits Completed in the Last 7 Days
```sql
SELECT
    DATE(v.end_time) AS visit_date,
    COUNT(v.id) AS visits_completed
FROM visits v
WHERE v.status = 'Completed'
  AND v.end_time >= NOW() - INTERVAL '7 days'
GROUP BY DATE(v.end_time)
ORDER BY visit_date DESC;
```

### Query 4: Task Status Distribution by Manager / Region
```sql
SELECT
    r.name AS region,
    tk.status,
    COUNT(tk.id) AS task_count
FROM tasks tk
JOIN regions r ON tk.region_scope_id = r.id
GROUP BY r.name, tk.status
ORDER BY r.name, tk.status;
```

---

## 10. UI/UX Expectations

| Page | Description |
|---|---|
| **Login Page** | JWT login form with error handling |
| **Dashboard** | Scoped stats: pending tasks, completed visits, risk flags |
| **Task List** | Filterable/paginated table; role-aware create button |
| **Task Detail** | Full task info, linked visit status, visit notes, AI summary panel |
| **Visit Update Form** | Agent: start visit, add notes, complete visit |
| **Logs/Reports** | Paginated activity log; report tables for Admin/Auditor |
| **Sidebar/Nav** | Dynamically renders links based on user's permitted modules |

---

## 11. Final Outcomes & Deliverables

This section defines the **expected final state** of the project upon submission.

### ✅ Backend (Django)
- [ ] Django project with modular apps: `auth_app`, `tasks`, `visits`, `reports`, `activity_logs`
- [ ] Custom User model with `EmployeeProfile` (role + scope)
- [ ] RBAC middleware / permission classes enforcing scope on every endpoint
- [ ] Full task CRUD APIs with scope-based filtering
- [ ] Visit lifecycle APIs (start, complete) with AI trigger on completion
- [ ] `MockAIService` behind a clean interface in `services/ai_service.py`
- [ ] `ActivityLog` auto-created via Django signals or service layer
- [ ] JWT authentication using `djangorestframework-simplejwt`
- [ ] Database migrations for all models
- [ ] Django Admin panel with all models registered
- [ ] Seed data / management command for sample users, roles, and tasks

### ✅ Frontend (React)
- [ ] Role-aware login page with JWT token storage
- [ ] Protected route system based on user role
- [ ] Dynamic sidebar navigation (links based on permitted modules)
- [ ] Dashboard page with aggregated stats (scoped by role)
- [ ] Task list page with filters (status, team, region)
- [ ] Task detail page with visit info and **Mock AI Summary panel**
- [ ] Visit update form (start visit, submit notes, complete visit)
- [ ] Activity logs / reports page (Admin and Auditor views)

### ✅ Reporting / SQL
- [ ] Pending tasks by region/team
- [ ] Average completion time per field agent
- [ ] Visits completed in the last 7 days
- [ ] Task status distribution by region

### ✅ Documentation
- [ ] `README.md` with setup, migration, and run instructions
- [ ] Sample credentials for each role (Admin, Manager, Lead, Agent, Auditor)
- [ ] `docs/PRD.md` — Product Requirements Document
- [ ] `docs/SRS.md` — Software Requirements Specification
- [ ] `docs/PROJECT_DETAILS.md` — This master file

### ✅ Code Quality (Good-to-Have)
- [ ] Pagination and filtering on list endpoints
- [ ] Basic unit tests for permission classes
- [ ] Search capability on task list

---

## 12. Project Constraints & Assumptions

| Constraint | Detail |
|---|---|
| **AI Requirement** | Must be a **mocked module only**. No paid APIs or real LLMs. Must be behind a swappable service abstraction. |
| **Deployment** | Running locally is sufficient. AWS / cloud deployment is NOT required. |
| **UI Polish** | Not the priority. Functional correctness, backend quality, and clarity matter most. |
| **Deadline** | 3 days from assignment date. Late submissions not accepted. |
| **Scope of Test Data** | Seed data / sample credentials must be provided for evaluators to test all roles. |
| **Auth** | JWT is strongly recommended; session auth is acceptable but JWT is preferred. |
