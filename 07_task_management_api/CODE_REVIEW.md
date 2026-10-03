# Peer Code Review: Task Management REST API (Mini-Project 2)

**Review Date:** September 24, 2026  
**Project:** Enterprise Task Management REST API (`07_task_management_api`)  
**Review Focus Areas:** API Design, Authentication & RBAC, Database Modeling & Migrations, Workflow State Machine, Error Handling, and Code Maintainability  
**Verdict:** **APPROVED (Production-Ready)**  

---

## 1. Executive Summary

This peer code review evaluates the architecture, security, database schema, workflow engine, and overall maintainability of the **Task Management REST API** built for Day 7 Mini-Project 2.

The implementation strictly satisfies all core specifications:
- **JWT-Secured Authentication** with password hashing (`bcrypt`), access & refresh tokens, token rotation, and OAuth2 password form support.
- **Role-Based Access Control (RBAC)** across `admin`, `manager`, `developer`, and `viewer` roles.
- **Relational Database Modeling** using modern SQLAlchemy 2.0 `Mapped` columns, proper foreign key cascades (`CASCADE` vs `SET NULL`), performance indexes, and Alembic migrations.
- **Task Workflow State Machine** with strict transition enforcement (`TODO` ➔ `IN_PROGRESS` ➔ `REVIEW` ➔ `COMPLETED`), manager-only reopen protections, and immutable audit logging.
- **Advanced Filtering & Pagination** supporting dynamic status, assignee, priority, and date range filters, full-text search, and standardized pagination envelopes.
- **Standardized Error Handling** with custom domain exceptions and uniform JSON error structures across all HTTP status codes (400, 401, 403, 404, 409, 422, 500).

---

## 2. Architecture & Design Patterns

### Strengths
1. **Layered Clean Architecture**:
   - `core/`: Pure business logic, configuration, security primitives, custom exceptions, and the workflow state machine. Free from HTTP framework dependencies.
   - `models/`: Modern SQLAlchemy 2.0 ORM declarations defining tables, indexes, and relationships.
   - `schemas/`: Pydantic V2 contracts enforcing strict input validation and output serialization.
   - `crud/`: Asynchronous data access repositories encapsulating database queries.
   - `services/`: Domain service layer orchestrating workflows, RBAC checks, and cross-model business rules.
   - `api/v1/`: FastAPI routers exposing endpoints, managing request dependencies, and returning HTTP responses.
2. **Explicit Async Session Lifecycle**:
   - Fast, non-blocking asynchronous database operations via `asyncpg` for PostgreSQL and `aiosqlite` for in-memory testing.
   - Transactions are automatically committed on success and cleanly rolled back on exceptions in the `get_async_db` dependency generator.

---

## 3. Security & RBAC Evaluation

### Strengths
1. **Cryptographic Integrity**:
   - Plaintext passwords are never stored. Passwords are salted and hashed using `passlib` with standard `bcrypt`.
   - JWT tokens are signed using `HS256` with separated access and refresh secret keys (`SECRET_KEY` and `REFRESH_SECRET_KEY`).
   - Token type discrimination: Access tokens explicitly declare `"type": "access"` while refresh tokens declare `"type": "refresh"`, preventing refresh tokens from being misused against protected API endpoints.
2. **Hierarchical RBAC Enforcement**:
   - `admin`: Complete unrestricted access over all projects, tasks, and users.
   - `manager`: Project creation, team member enrollment, project updates, task assignment, and transition reopens.
   - `developer`: Access scoped to enrolled projects; can update status and details of assigned/created tasks; blocked from arbitrary reassignments or project deletions.
   - `viewer`: Strictly read-only access across projects and tasks. Any mutating request is intercepted and rejected with `403 Forbidden`.
3. **Swagger UI Interoperability**:
   - Provided standard OAuth2 password endpoint (`POST /api/v1/auth/token`) alongside the JSON endpoint (`POST /api/v1/auth/login`), enabling native Swagger UI "Authorize" modal login without manual token copying.

---

## 4. Database Modeling & Alembic Migrations

### Schema Design & Foreign Key Strategies
- `users`: Indexed on `username` and `email` for $\mathcal{O}(1)$ lookups during authentication.
- `projects`: `owner_id` references `users.id` with `ON DELETE CASCADE`.
- `project_members`: Composite association entity with a `UniqueConstraint("project_id", "user_id")` preventing duplicate memberships.
- `tasks`:
  - `project_id` references `projects.id` with `ON DELETE CASCADE`: Deleting a project automatically cascades to its tasks.
  - `assignee_id` references `users.id` with `ON DELETE SET NULL`: Deleting a user account retains the task in the project with an unassigned status, preventing orphaned records.
  - `creator_id` references `users.id` with `ON DELETE CASCADE`.
  - Composite indexes on `tasks.status`, `tasks.priority`, `tasks.due_date`, and `tasks.project_id` optimize filtering and sorting performance.
- `task_audit_logs`: Immutable ledger tracking every workflow status transition and reassignment event.

---

## 5. Peer Review Findings & Incorporated Improvements

During the iterative development and verification cycle, five important technical improvements were identified and incorporated into the codebase:

| # | Review Finding | Risk / Impact | Resolution Incorporated | Status |
| :- | :--- | :--- | :--- | :--- |
| **1** | **Alembic Version ID Length** | Alembic's default `alembic_version` table in PostgreSQL defines `version_num VARCHAR(32)`. The initial migration ID `"001_initial_task_management_schema"` was 35 characters, triggering a `StringDataRightTruncationError`. | Shortened the migration revision identifier to `"001_initial_task_mgmt"` (22 characters, safely under the 32-character limit). | **RESOLVED** |
| **2** | **Async Eager-Loading (`MissingGreenlet`)** | When serializing `ProjectDetailResponse` and `ProjectMemberResponse`, accessing unloaded related entities (`owner` or `user`) triggered SQLAlchemy's async `MissingGreenlet` error during Pydantic serialization. | Added explicit `selectinload(Project.owner)` and `selectinload(ProjectMember.user)` across all project and member queries in CRUD and service layers. | **RESOLVED** |
| **3** | **URL Parameter Encoding on Datetime Filters** | Passing ISO 8601 strings containing `+00:00` directly in URL query strings converted `+` to space (` `), failing Pydantic's datetime validator with a `422 Unprocessable Entity`. | Standardized query string encoding using HTTP client `params` dictionaries so `+` is safely URL-encoded as `%2B`. | **RESOLVED** |
| **4** | **Viewer Authorization Order in State Machine** | In `WorkflowEngine.validate_transition`, transition graph validity was initially checked before the user's role. A viewer requesting an invalid transition received a `400 Bad Request` instead of the expected `403 Forbidden`. | Moved the viewer role check to the very top of `validate_transition` so unauthorized actors are always rejected with `403 Forbidden` regardless of the payload. | **RESOLVED** |
| **5** | **Session Isolation in Table Resets** | Nesting an engine table drop/create block inside an active `AsyncSessionLocal` caused connection rollback failures on the dropped database tables. | Refactored the database initialization sequence to drop/create tables on a dedicated engine connection *prior* to opening transactional sessions. | **RESOLVED** |

---

## 6. Verification & Automated Test Results

The test suite (`tests/`) consists of **41 automated test cases** executed via `pytest`:

```text
============================= test session starts =============================
platform win32 -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\venka\Desktop\Narasimha\07_task_management_api
configfile: pytest.ini
collected 41 items

tests/test_auth.py::test_register_user_success PASSED                    [  2%]
tests/test_auth.py::test_register_duplicate_username_fails PASSED        [  4%]
tests/test_auth.py::test_register_duplicate_email_fails PASSED           [  7%]
tests/test_auth.py::test_login_json_success PASSED                       [  9%]
tests/test_auth.py::test_login_invalid_password_fails PASSED             [ 12%]
tests/test_auth.py::test_login_form_oauth2_success PASSED                [ 14%]
tests/test_auth.py::test_refresh_token_rotation PASSED                   [ 17%]
tests/test_auth.py::test_get_current_user_me PASSED                      [ 19%]
tests/test_auth.py::test_unauthenticated_request_rejected PASSED         [ 21%]
tests/test_error_handling.py::test_error_404_standard_response PASSED    [ 24%]
tests/test_error_handling.py::test_error_403_standard_response PASSED    [ 26%]
tests/test_error_handling.py::test_error_409_standard_response PASSED    [ 29%]
tests/test_error_handling.py::test_error_422_standard_response PASSED    [ 31%]
tests/test_filtering_pagination.py::test_filter_by_status PASSED         [ 34%]
tests/test_filtering_pagination.py::test_filter_by_priority PASSED       [ 36%]
tests/test_filtering_pagination.py::test_filter_by_assignee PASSED       [ 39%]
tests/test_filtering_pagination.py::test_filter_by_search_keyword PASSED [ 41%]
tests/test_filtering_pagination.py::test_filter_by_due_date_range PASSED [ 43%]
tests/test_filtering_pagination.py::test_pagination_envelope_structure PASSED [ 46%]
tests/test_projects.py::test_create_project_success PASSED               [ 48%]
tests/test_projects.py::test_viewer_cannot_create_project PASSED         [ 51%]
tests/test_projects.py::test_list_projects_pagination_and_scoping PASSED [ 53%]
tests/test_projects.py::test_get_project_detail_with_task_counts PASSED  [ 56%]
tests/test_projects.py::test_update_project_by_owner PASSED              [ 58%]
tests/test_projects.py::test_add_project_member PASSED                   [ 60%]
tests/test_projects.py::test_delete_project PASSED                       [ 63%]
tests/test_rbac.py::test_admin_has_unrestricted_access PASSED            [ 65%]
tests/test_rbac.py::test_viewer_is_strictly_read_only PASSED             [ 68%]
tests/test_rbac.py::test_developer_cannot_reassign_arbitrary_tasks PASSED [ 70%]
tests/test_rbac.py::test_developer_can_update_own_assigned_task PASSED   [ 73%]
tests/test_tasks.py::test_create_task_success PASSED                     [ 75%]
tests/test_tasks.py::test_get_task_details PASSED                        [ 78%]
tests/test_tasks.py::test_update_task_put PASSED                         [ 80%]
tests/test_tasks.py::test_patch_task PASSED                              [ 82%]
tests/test_tasks.py::test_delete_task PASSED                             [ 85%]
tests/test_workflow.py::test_valid_workflow_progression PASSED           [ 87%]
tests/test_workflow.py::test_invalid_skip_transition_rejected PASSED     [ 90%]
tests/test_workflow.py::test_non_manager_cannot_reopen_completed_task PASSED [ 92%]
tests/test_workflow.py::test_manager_can_reopen_completed_task PASSED    [ 95%]
tests/test_workflow.py::test_audit_history_trail PASSED                  [ 97%]
tests/test_workflow.py::test_task_assignment_endpoint PASSED             [100%]

============================= 41 passed in 56.56s =============================
```

---

## 7. Review Checklist Sign-Off

- [x] **API Design**: RESTful conventions, semantic HTTP methods (GET, POST, PUT, PATCH, DELETE) and status codes (200, 201, 204, 400, 401, 403, 404, 409, 422, 500).
- [x] **Authentication**: JWT token pair issuance, refresh token exchange, secure bcrypt hashing.
- [x] **Authorization**: Granular RBAC (`admin`, `manager`, `developer`, `viewer`) with endpoint dependencies.
- [x] **Database Modeling**: DeclarativeBase, Mapped types, foreign keys, cascades, composite indexes.
- [x] **Migrations**: Clean Alembic migration script executing without warnings.
- [x] **CRUD Operations**: Projects and tasks support full lifecycle create, read, update, delete.
- [x] **Workflow & Audit**: Finite state machine with valid transitions, manager-only reopen restrictions, and audit history.
- [x] **Filtering & Pagination**: Multi-parameter task queries, full-text search, and pagination metadata envelopes.
- [x] **Documentation & Testing**: Interactive Swagger UI docs at `/docs`, Postman Collection v2.1.0 (`postman_collection.json`), and 41 passing automated tests.
- [x] **Error Handling**: Standardized JSON responses for all domain and HTTP errors.
