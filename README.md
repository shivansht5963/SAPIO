# FFMS — Field Force Management System

An AI-powered backend for managing field operations, built with Django REST Framework. Features role-based access control (RBAC), real-time visit tracking, and AI-generated risk assessments from field agent notes.

## Links

| | URL |
|--|-----|
| Backend (Live) | [https://sapio.onrender.com](https://sapio.onrender.com) |
| API Docs | [https://sapio.onrender.com/api/docs/](https://sapio.onrender.com/api/docs/) |
| Frontend (Live) | [https://sapio-frontend.vercel.app](https://sapio-frontend.vercel.app) |
| Backend Repo | [github.com/shivansht5963/SAPIO](https://github.com/shivansht5963/SAPIO) |
| Frontend Repo | [github.com/shivansht5963/SAPIO_frontend](https://github.com/shivansht5963/SAPIO_frontend) |

## Tech Stack

- **Backend:** Python 3.12, Django 5.0, Django REST Framework
- **Auth:** JWT (SimpleJWT) — 2h access / 1d refresh tokens
- **Database:** SQLite (dev) 
- **AI Service:** Gemini API for visit note analysis
- **Frontend:** React + Vite (separate repo)
- **Deployment:** Render (backend), Vercel (frontend)

## Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/shivansht5963/SAPIO.git
cd SAPIO

# 2. Create & activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. Seed default roles, teams, regions & demo users
python manage.py seed_data

# 6. Start the server
python manage.py runserver
```

The server starts at `http://127.0.0.1:8000/`

- **Home page:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **API Docs:** [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- **Admin panel:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

### Demo Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin_user` | `admin123` |
| Team Lead | `tl_alpha` | `pass123` |
| Field Agent | `agent_ravi` | `pass123` |
| Auditor | `auditor_meera` | `pass123` |

## Project Structure

```
FFMS/
├── FFMS/                  # Django project settings & root URL config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── accounts/              # User management & authentication
│   ├── models.py          # Role, Region, Team, EmployeeProfile, ModuleAccess
│   ├── views.py           # Login, /me, user list endpoints
│   ├── permissions.py     # RBAC permission classes
│   ├── mixins.py          # ScopeFilterMixin for auto-scoping querysets
│   └── utils.py           # ModulePermission helper
│
├── tasks/                 # Task CRUD & assignment
│   ├── models.py          # Task model (status, priority, scope fields)
│   ├── views.py           # TaskViewSet with assign action
│   └── serializers.py     # List, Detail, Create, Assign serializers
│
├── visits/                # Field visit lifecycle
│   ├── models.py          # Visit model with AI fields
│   ├── views.py           # Start & complete actions (AI on complete)
│   └── serializers.py     # Start, Complete, List, Detail serializers
│
├── activity_logs/         # Audit trail (read-only)
│   ├── models.py          # ActivityLog model
│   └── views.py           # Filterable, role-scoped log viewer
│
├── reports/               # Analytics & dashboard
│   └── views.py           # Pending tasks, completion time, distribution, dashboard
│
├── services/              # Shared services
│   ├── ai_service.py      # Gemini AI integration
│   └── activity_logger.py # Utility to create activity logs
│
├── templates/             # HTML pages served by Django
│   ├── home.html          # Landing page with links to docs & frontend
│   └── api_docs.html      # Interactive Swagger-style API documentation
│
├── docs/                  # Project documentation
├── manage.py
├── requirements.txt
└── build.sh               # Render deploy script
```

## API Overview

Base URL: `https://sapio.onrender.com/api`

| Group | Endpoints | Description |
|-------|-----------|-------------|
| **Auth** | `POST /auth/login/`, `POST /auth/refresh/`, `GET /auth/me/` | JWT login, token refresh, profile fetch |
| **Users** | `GET /users/` | Scoped user listing with role filter |
| **Tasks** | `GET/POST /tasks/`, `GET/PUT/PATCH/DELETE /tasks/{id}/`, `PATCH /tasks/{id}/assign/` | Full CRUD + assignment with scope validation |
| **Visits** | `GET /visits/`, `GET /visits/{id}/`, `POST /visits/start/`, `POST /visits/{id}/complete/` | Visit lifecycle with AI-powered completion |
| **Logs** | `GET /logs/`, `GET /logs/{id}/` | Filterable audit trail (read-only) |
| **Reports** | `GET /reports/pending-tasks/`, `GET /reports/task-distribution/`, `GET /reports/recent-visits/`, `GET /reports/completion-time/`, `GET /reports/dashboard/` | Analytics & dashboard |

For full request/response schemas, visit the [API Documentation](https://sapio.onrender.com/api/docs/).

## Role-Based Access Control

| Role | Tasks | Visits | Logs | Reports |
|------|-------|--------|------|---------|
| **Admin** | Full CRUD | Read all | Read all | Read all |
| **Auditor** | Read (all) | Read (all) | Read (all) | Read (all) |
| **Regional Manager** | Create, Read, Update (own region) | Read (own region) | Read (own region) | Read (own region) |
| **Team Lead** | Create, Read, Update (own team) | Read (own team) | Read (own team) | Read (own team) |
| **Field Agent** | Read (own tasks) | Start & Complete (own) | No access | Read (self-scoped) |

## License

MIT License — see [LICENSE](LICENSE) for details.
