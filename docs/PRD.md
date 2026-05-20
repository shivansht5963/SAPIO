# Product Requirements Document (PRD)

## 1. Product Vision & Overview
The Field Force Management System is a role-based, modular platform designed to manage and track the operations of a distributed field team. The system enables managers to assign and monitor tasks, while field agents can seamlessly track and update their visits. A core focus of the platform is strict role-based access control (RBAC), module-level permissions, and scoped data visibility to ensure users only see and interact with data relevant to their role and geographical scope. 

## 2. Target Audience & User Roles
The system targets various stakeholders in a field operations environment. The primary roles and their corresponding scopes are:

*   **Admin**: System-wide access. Can manage all users, roles, teams, modules, and view all data across the platform.
*   **Regional Manager**: Scoped to a specific Region/Zone. Can manage tasks, field agents, and view reports/logs only for their designated region.
*   **Team Lead**: Scoped to a specific Team. Can monitor, assign, and manage tasks specifically for their team members.
*   **Field Agent**: Scoped to Self. Can only view and update tasks and visits assigned directly to them.
*   **Auditor**: Global or Scoped view (depending on assignment) but with Read-Only permissions. Can view reports and activity logs for auditing purposes, without the ability to modify data.

## 3. Core Features

### 3.1 Authentication and Role-Based Access Control
*   **Login**: Secure login system (JWT suggested) to authenticate users.
*   **RBAC & Permissions**: Granular access control based on Roles (Admin, Manager, Agent, etc.) and Module Access (Tasks, Visits, Logs).

### 3.2 Task Management
*   **Creation & Assignment**: Managers and Team Leads can create tasks and assign them to specific Field Agents within their scope.
*   **Status Tracking**: Tasks have a defined lifecycle (e.g., Pending, In Progress, Completed, Cancelled).
*   **Visibility**: Task listing is dynamically filtered based on the user's role and scope (e.g., Agents only see their tasks; Leads see their team's tasks).

### 3.3 Visit Tracking
*   **Visit Lifecycle**: Field Agents can start a visit, log activities, add visit notes, update the visit outcome, and mark the visit as completed.
*   **Note Logging**: Crucial for field data collection, allowing agents to capture qualitative data from their visits.

### 3.4 Scope-Based Visibility
*   **Data Partitioning**: All data queries must evaluate the user's Team, Region, or Zone to prevent unauthorized data access. Action permissions (Create, Update, Delete) are strictly enforced at the API level.

### 3.5 Activity Logging
*   **Audit Trail**: The system automatically logs key events such as:
    *   Task creation and assignment
    *   Status changes (Tasks and Visits)
    *   Visit started and completed events

### 3.6 Mock AI Integration
*   **Feature**: When a Field Agent submits visit notes, the system triggers a mocked AI service.
*   **Behavior**: The service generates automated outputs such as a succinct "visit summary", a "follow-up recommendation", or assigns a "risk/priority flag".
*   **Storage & Display**: Both the original raw notes and the structured AI output are persisted in the database and surfaced on the UI (e.g., Task Detail page).

## 4. User Stories

### Field Agent
*   *As a Field Agent, I want to view a list of tasks assigned to me for the day so that I know where to go.*
*   *As a Field Agent, I want to mark a visit as started and completed, and add my notes, so that my progress is recorded.*
*   *As a Field Agent, I want to see AI-generated summaries and follow-up recommendations based on my notes to help me plan my next steps.*

### Team Lead / Regional Manager
*   *As a Team Lead, I want to create tasks and assign them to members of my team.*
*   *As a Regional Manager, I want to see a dashboard showing the status of all tasks within my region.*
*   *As a Manager, I want to view activity logs to ensure field agents are following proper visit protocols.*

### Admin / Auditor
*   *As an Admin, I want to manage roles, permissions, and regional scopes for all employees.*
*   *As an Auditor, I want read-only access to all activity logs and visit outcomes across the system to verify compliance.*

## 5. UI/UX Expectations
*   **Login Page**: Simple, secure entry point.
*   **Dashboard**: High-level metrics and relevant summaries (scoped by role).
*   **Task List Page**: Paginated or filtered list of tasks.
*   **Task Detail Page**: Comprehensive view of task info, associated visit, raw notes, and the Mock AI Summary section.
*   **Role-Aware Sidebar/Navigation**: Navigation items dynamically render based on the user's permitted modules.
