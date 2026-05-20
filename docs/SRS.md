# Software Requirements Specification (SRS)

## 1. Technology Stack
*   **Backend Framework**: Django (Python) - Recommended for rapid development and built-in ORM/Admin features.
*   **Frontend Framework**: React (JavaScript/TypeScript) - Ideal for building dynamic, role-aware interfaces.
*   **Database**: PostgreSQL or MySQL (Relational DB preferred for rigid schemas and reporting queries).
*   **Authentication**: JSON Web Tokens (JWT) for stateless REST API authentication.

## 2. System Architecture
The application will follow a standard Client-Server architecture:
1.  **React Frontend (SPA)**: Communicates with the backend via RESTful APIs. It maintains local state for the logged-in user's role and conditionally renders UI components.
2.  **Django Backend (API Server)**: Exposes endpoints, handles authentication, enforces business logic, applies scope-based visibility filters on DB queries, and interacts with the AI Service.
3.  **Database Layer**: Stores all relational data.
4.  **Mock AI Service**: A decoupled Python module/service abstracting the AI behavior. It receives input text, processes it through deterministic rules (mocking LLM behavior), and returns structured JSON.

## 3. Database Model & Entities

### 3.1 Core Entities
*   **User**: Standard auth user (username, email, password, is_active).
*   **Role**: Defines the job function (name: Admin, Regional Manager, Team Lead, Field Agent, Auditor).
*   **Permission / ModuleAccess**: Granular permissions (e.g., `can_create_task`, `can_view_logs`). Mapped to Roles.
*   **Team / Region / Zone**: Hierarchical organizational structures to define data boundaries.
*   **EmployeeProfile**: Extends the User model. Contains foreign keys to Role, and optionally Team or Region, defining their exact scope.
*   **Task**: 
    *   Fields: title, description, assigned_to (FK to EmployeeProfile), created_by (FK to EmployeeProfile), status (Pending, Assigned, Completed), due_date, team_scope, region_scope.
*   **Visit**: 
    *   Fields: task (FK to Task), status (Started, Completed), start_time, end_time, visit_notes (TextField), ai_summary (JSONField/TextField), ai_recommendation (TextField), ai_risk_flag (CharField).
*   **ActivityLog**:
    *   Fields: user (FK to User), action (Create, Update, Delete, Start, Complete), entity_type (Task, Visit), entity_id, timestamp, description.

## 4. API Specifications (RESTful)

### 4.1 Authentication
*   `POST /api/auth/login/`: Accepts credentials, returns JWT tokens and User Role/Scope details.

### 4.2 Tasks
*   `GET /api/tasks/`: Lists tasks. **Logic**: Backend reads the JWT, identifies the user's role and scope, and filters the DB query (e.g., `Tasks.objects.filter(assigned_to=user)` for Agents, or `Tasks.objects.filter(team=user.team)` for Leads).
*   `POST /api/tasks/`: Create a new task. Validates if the user has `can_create_task` permission.
*   `GET /api/tasks/{id}/`: Fetch full details of a specific task.
*   `PATCH /api/tasks/{id}/assign/`: Update the `assigned_to` field.

### 4.3 Visits
*   `POST /api/visits/{task_id}/start/`: Creates a Visit record with `start_time` and status 'Started'.
*   `POST /api/visits/{visit_id}/complete/`: 
    *   **Payload**: `{"notes": "Customer was interested but budget is low..."}`
    *   **Logic**: 
        1. Updates Visit status, `end_time`, and saves raw notes.
        2. Triggers `MockAIService.generate_insights(notes)`.
        3. Saves AI outputs (`ai_summary`, `ai_recommendation`) to the Visit record.
        4. Logs the activity.

### 4.4 Reporting & Logs (Auditor/Manager Access)
*   `GET /api/reports/dashboard/`: Returns aggregated data based on user scope.
*   `GET /api/logs/`: Returns paginated ActivityLogs filtered by scope.

## 5. Mock AI Service Contract
To evaluate abstraction, the AI logic must be isolated:

```python
class MockAIService:
    @staticmethod
    def generate_insights(notes: str) -> dict:
        """
        Mock implementation of AI processing.
        In reality, this would call OpenAI/Anthropic APIs.
        """
        summary = f"Summary of notes: {notes[:50]}..."
        recommendation = "Schedule a follow-up meeting in 7 days."
        risk_flag = "Low"
        
        if "angry" in notes.lower() or "cancel" in notes.lower():
            risk_flag = "High"
            recommendation = "Immediate escalation to Team Lead."
            
        return {
            "summary": summary,
            "recommendation": recommendation,
            "risk_flag": risk_flag
        }
```

## 6. SQL & Reporting Use Cases
The system must support the following reporting queries (implemented either via ORM or raw SQL for performance):

1.  **Pending Tasks by Region/Team**: 
    *   `SELECT team_id, COUNT(*) FROM tasks WHERE status != 'Completed' GROUP BY team_id;`
2.  **Average Completion Time per Field Agent**: 
    *   Join Tasks and Visits to calculate `AVG(visit.end_time - visit.start_time)` grouped by `tasks.assigned_to`.
3.  **Visits Completed in the Last 7 Days**: 
    *   `SELECT COUNT(*) FROM visits WHERE status = 'Completed' AND end_time >= NOW() - INTERVAL '7 days';`
4.  **Task Status Distribution**: 
    *   `SELECT status, COUNT(*) FROM tasks WHERE region_id = X GROUP BY status;`
