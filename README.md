# Python Intensive Learning Plan: September 18, 2026

Welcome! Below is the roadmap and file index prepared for today's learning sessions.

---

## 📅 Schedule Overview

| Session | Topic | Key Coverage | Learning Outcome |
| :--- | :--- | :--- | :--- |
| **1st Half** *(Before Lunch)* | **Control Flow & Functions** | `if/elif/else`, `for/while` loops, `break/continue/pass`, `range()`, list comprehensions, `*args`, `**kwargs`, multiple returns, lambdas, LEGB scope rule | Confidently write structured logic and modular, reusable functions. |
| **2nd Half** *(Post Lunch)* | **Data Structures + File Handling** | Lists, Tuples, Sets, Dictionaries, JSON & CSV I/O, `try/except` handling, Capstone: Contact Book with JSON persistence | Master Python's 4 core data structures, handle file I/O safely, and build persistent applications. |
| **Day 4** | **SQL & Git Foundations + Mini-Project 1: CLI Task Manager** | Relational Model, PostgreSQL via `psycopg2`, JOINs, GROUP BY/HAVING, aggregate functions, keys & indexes, OOP `Task` & `TaskManager`, GitHub Flow branching, structured JSON export, logging & `unittest` suite | Production-grade CLI Task Manager with persistent database backend and peer-review ready architecture. |
| **Day 5** | **FastAPI Setup, Pydantic V2 & SQLAlchemy 2.0** | Asynchronous FastAPI architecture, Pydantic V2 `@field_validator`/`@model_validator`, modern SQLAlchemy 2.0 `DeclarativeBase` & `Mapped`, 1:N / N:1 relationships & cascades, Alembic migrations, full User/Product CRUD, and 31 automated `pytest` tests | Production-grade async REST API with live PostgreSQL persistence, OpenAPI/Swagger docs, and complete test suite. |
| **Day 6** | **Authentication & Security** | Secure password hashing (`passlib` + `bcrypt`), JWT access & refresh tokens (`python-jose`), OAuth2PasswordBearer flow, `/register`, `/login`, `/me`, `/refresh` endpoints, `Depends(get_current_user)`, Role-Based Access Control (`admin` vs `user`), FastAPI `CORSMiddleware`, `pydantic-settings` `.env` management, and Practice: Secured Product API with 41 automated `pytest` tests | Production-grade secure FastAPI service with JWT tokens, token refresh, and RBAC-protected Product API. |

---

## 📂 Workspace Structure & Code Files

### 1️⃣ First Half: Control Flow & Functions
Located in: [`01_control_flow_and_functions/`](file:///c:/Users/venka/Desktop/Narasimha/01_control_flow_and_functions)

- [`notes_and_examples.py`](file:///c:/Users/venka/Desktop/Narasimha/01_control_flow_and_functions/notes_and_examples.py)
  - Interactive walkthrough covering condition branches, loop control, list comprehensions, `*args` / `**kwargs`, lambdas, and LEGB scope.
- [`fizzbuzz.py`](file:///c:/Users/venka/Desktop/Narasimha/01_control_flow_and_functions/fizzbuzz.py)
  - Classic modulus and conditional branching problem (multiples of 3, 5, and both).
- [`prime_checker.py`](file:///c:/Users/venka/Desktop/Narasimha/01_control_flow_and_functions/prime_checker.py)
  - Prime detection optimized to $\mathcal{O}(\sqrt{n})$ plus list comprehension range generation.
- [`temp_converter.py`](file:///c:/Users/venka/Desktop/Narasimha/01_control_flow_and_functions/temp_converter.py)
  - Conversions between Celsius, Fahrenheit, and Kelvin with input validation.

### 2️⃣ Second Half: Data Structures & File Handling
Located in: [`02_data_structures_and_file_handling/`](file:///c:/Users/venka/Desktop/Narasimha/02_data_structures_and_file_handling)

- [`data_structures_examples.py`](file:///c:/Users/venka/Desktop/Narasimha/02_data_structures_and_file_handling/data_structures_examples.py)
  - Lists (CRUD, slicing, `sort()`, `reverse()`), Tuples (immutability, unpacking), Sets (union, intersection, difference), Dictionaries (`.get()`, `.items()`, comprehensions), and nested objects.
- [`file_handling_examples.py`](file:///c:/Users/venka/Desktop/Narasimha/02_data_structures_and_file_handling/file_handling_examples.py)
  - Structured file storage with `json` (`dump`/`load`), `csv` (`DictReader`/`DictWriter`), and safe execution with `try/except/else/finally`.
- [`contact_book.py`](file:///c:/Users/venka/Desktop/Narasimha/02_data_structures_and_file_handling/contact_book.py)
  - **Capstone Project**: Full CRUD CLI contact book with automatic JSON persistence and error handling.

### 3️⃣ Day 4: SQL & Git Foundations + CLI Task Manager
Located in: [`04_sql_and_git_task_manager/`](file:///c:/Users/venka/Desktop/Narasimha/04_sql_and_git_task_manager)

- **Database Layer**: [`database/schema.sql`](file:///c:/Users/venka/Desktop/Narasimha/04_sql_and_git_task_manager/database/schema.sql), [`database/queries.sql`](file:///c:/Users/venka/Desktop/Narasimha/04_sql_and_git_task_manager/database/queries.sql), [`database/connection.py`](file:///c:/Users/venka/Desktop/Narasimha/04_sql_and_git_task_manager/database/connection.py), [`database/seed.py`](file:///c:/Users/venka/Desktop/Narasimha/04_sql_and_git_task_manager/database/seed.py).
- **OOP Domain Models**: [`models/task.py`](file:///c:/Users/venka/Desktop/Narasimha/04_sql_and_git_task_manager/models/task.py), [`models/category.py`](file:///c:/Users/venka/Desktop/Narasimha/04_sql_and_git_task_manager/models/category.py), [`models/exceptions.py`](file:///c:/Users/venka/Desktop/Narasimha/04_sql_and_git_task_manager/models/exceptions.py).
- **Service Layer**: [`managers/task_manager.py`](file:///c:/Users/venka/Desktop/Narasimha/04_sql_and_git_task_manager/managers/task_manager.py) (CRUD, JOINs, GROUP BY & HAVING analytics).
- **CLI Interface**: [`cli.py`](file:///c:/Users/venka/Desktop/Narasimha/04_sql_and_git_task_manager/cli.py) & [`main.py`](file:///c:/Users/venka/Desktop/Narasimha/04_sql_and_git_task_manager/main.py).
- **Utilities**: [`utils/exporter.py`](file:///c:/Users/venka/Desktop/Narasimha/04_sql_and_git_task_manager/utils/exporter.py) (JSON export) & [`utils/logger.py`](file:///c:/Users/venka/Desktop/Narasimha/04_sql_and_git_task_manager/utils/logger.py) (Rotating log).
- **Automated Tests**: [`tests/test_models.py`](file:///c:/Users/venka/Desktop/Narasimha/04_sql_and_git_task_manager/tests/test_models.py), [`tests/test_manager.py`](file:///c:/Users/venka/Desktop/Narasimha/04_sql_and_git_task_manager/tests/test_manager.py), [`tests/test_queries_and_joins.py`](file:///c:/Users/venka/Desktop/Narasimha/04_sql_and_git_task_manager/tests/test_queries_and_joins.py).

### 4️⃣ Day 5: FastAPI, Pydantic V2 & SQLAlchemy 2.0
Located in: [`05_fastapi_pydantic_sqlalchemy/`](file:///c:/Users/venka/Desktop/Narasimha/05_fastapi_pydantic_sqlalchemy)

- **FastAPI Core & App**: [`app/main.py`](file:///c:/Users/venka/Desktop/Narasimha/05_fastapi_pydantic_sqlalchemy/app/main.py), [`app/core/config.py`](file:///c:/Users/venka/Desktop/Narasimha/05_fastapi_pydantic_sqlalchemy/app/core/config.py), [`app/core/security.py`](file:///c:/Users/venka/Desktop/Narasimha/05_fastapi_pydantic_sqlalchemy/app/core/security.py).
- **Modern SQLAlchemy 2.0 Layer**: [`app/db/base.py`](file:///c:/Users/venka/Desktop/Narasimha/05_fastapi_pydantic_sqlalchemy/app/db/base.py), [`app/db/session.py`](file:///c:/Users/venka/Desktop/Narasimha/05_fastapi_pydantic_sqlalchemy/app/db/session.py), [`app/models/user.py`](file:///c:/Users/venka/Desktop/Narasimha/05_fastapi_pydantic_sqlalchemy/app/models/user.py), [`app/models/product.py`](file:///c:/Users/venka/Desktop/Narasimha/05_fastapi_pydantic_sqlalchemy/app/models/product.py).
- **Pydantic V2 Validation Schemas**: [`app/schemas/user.py`](file:///c:/Users/venka/Desktop/Narasimha/05_fastapi_pydantic_sqlalchemy/app/schemas/user.py), [`app/schemas/product.py`](file:///c:/Users/venka/Desktop/Narasimha/05_fastapi_pydantic_sqlalchemy/app/schemas/product.py), [`app/schemas/common.py`](file:///c:/Users/venka/Desktop/Narasimha/05_fastapi_pydantic_sqlalchemy/app/schemas/common.py).
- **Async CRUD Repositories**: [`app/crud/base.py`](file:///c:/Users/venka/Desktop/Narasimha/05_fastapi_pydantic_sqlalchemy/app/crud/base.py), [`app/crud/crud_user.py`](file:///c:/Users/venka/Desktop/Narasimha/05_fastapi_pydantic_sqlalchemy/app/crud/crud_user.py), [`app/crud/crud_product.py`](file:///c:/Users/venka/Desktop/Narasimha/05_fastapi_pydantic_sqlalchemy/app/crud/crud_product.py).
- **REST Endpoints**: [`app/api/v1/endpoints/users.py`](file:///c:/Users/venka/Desktop/Narasimha/05_fastapi_pydantic_sqlalchemy/app/api/v1/endpoints/users.py), [`app/api/v1/endpoints/products.py`](file:///c:/Users/venka/Desktop/Narasimha/05_fastapi_pydantic_sqlalchemy/app/api/v1/endpoints/products.py).
- **Alembic Migrations**: [`alembic.ini`](file:///c:/Users/venka/Desktop/Narasimha/05_fastapi_pydantic_sqlalchemy/alembic.ini), [`alembic/env.py`](file:///c:/Users/venka/Desktop/Narasimha/05_fastapi_pydantic_sqlalchemy/alembic/env.py), [`alembic/versions/001_initial_users_and_products.py`](file:///c:/Users/venka/Desktop/Narasimha/05_fastapi_pydantic_sqlalchemy/alembic/versions/001_initial_users_and_products.py).
- **Testing & Demos**: [`scripts/seed_data.py`](file:///c:/Users/venka/Desktop/Narasimha/05_fastapi_pydantic_sqlalchemy/scripts/seed_data.py), [`scripts/run_demo.py`](file:///c:/Users/venka/Desktop/Narasimha/05_fastapi_pydantic_sqlalchemy/scripts/run_demo.py), [`tests/`](file:///c:/Users/venka/Desktop/Narasimha/05_fastapi_pydantic_sqlalchemy/tests).

### 5️⃣ Day 6: Authentication & Security
Located in: [`06_authentication_and_security/`](file:///c:/Users/venka/Desktop/Narasimha/06_authentication_and_security)

- **Security & JWT Core**: [`app/core/security.py`](file:///c:/Users/venka/Desktop/Narasimha/06_authentication_and_security/app/core/security.py) (`passlib` + `bcrypt` hashing, `python-jose` access & refresh tokens, token type separation), [`app/core/config.py`](file:///c:/Users/venka/Desktop/Narasimha/06_authentication_and_security/app/core/config.py) (`pydantic-settings` BaseSettings, `.env` file management, CORS origins).
- **Domain Models & RBAC**: [`app/models/user.py`](file:///c:/Users/venka/Desktop/Narasimha/06_authentication_and_security/app/models/user.py) (`UserRole` enum: `admin` vs `user`, `is_admin` property), [`app/models/product.py`](file:///c:/Users/venka/Desktop/Narasimha/06_authentication_and_security/app/models/product.py).
- **Authentication Schemas**: [`app/schemas/auth.py`](file:///c:/Users/venka/Desktop/Narasimha/06_authentication_and_security/app/schemas/auth.py) (`Token`, `RefreshTokenRequest`, `LoginRequest`, `UserRegister`), [`app/schemas/user.py`](file:///c:/Users/venka/Desktop/Narasimha/06_authentication_and_security/app/schemas/user.py), [`app/schemas/product.py`](file:///c:/Users/venka/Desktop/Narasimha/06_authentication_and_security/app/schemas/product.py).
- **Dependencies & RBAC Enforcers**: [`app/api/deps.py`](file:///c:/Users/venka/Desktop/Narasimha/06_authentication_and_security/app/api/deps.py) (`oauth2_scheme`, `get_current_user`, `require_roles`, `CurrentAdminUserDep`).
- **REST Endpoints**:
  - [`app/api/v1/endpoints/auth.py`](file:///c:/Users/venka/Desktop/Narasimha/06_authentication_and_security/app/api/v1/endpoints/auth.py): `/register`, `/login`, `/me`, `/refresh`, and OAuth2 standard `/token`.
  - [`app/api/v1/endpoints/users.py`](file:///c:/Users/venka/Desktop/Narasimha/06_authentication_and_security/app/api/v1/endpoints/users.py): User CRUD protected by RBAC.
  - [`app/api/v1/endpoints/products.py`](file:///c:/Users/venka/Desktop/Narasimha/06_authentication_and_security/app/api/v1/endpoints/products.py): **Practice Secured Product API** (Admin-only create, edit, delete; customer browsing).
- **CORS Middleware**: [`app/main.py`](file:///c:/Users/venka/Desktop/Narasimha/06_authentication_and_security/app/main.py) (`CORSMiddleware` with allowed origins, methods, headers, credentials).
- **Testing & Demos**: [`scripts/seed_data.py`](file:///c:/Users/venka/Desktop/Narasimha/06_authentication_and_security/scripts/seed_data.py), [`scripts/run_demo.py`](file:///c:/Users/venka/Desktop/Narasimha/06_authentication_and_security/scripts/run_demo.py), [`tests/`](file:///c:/Users/venka/Desktop/Narasimha/06_authentication_and_security/tests) (**41 automated `pytest` tests passing 100%**).

---

## 🚀 How to Run the Programs

```powershell
# Run Part 1 Examples & Practice Programs
python 01_control_flow_and_functions/notes_and_examples.py
python 01_control_flow_and_functions/fizzbuzz.py
python 01_control_flow_and_functions/prime_checker.py
python 01_control_flow_and_functions/temp_converter.py

# Run Part 2 Examples & Contact Book
python 02_data_structures_and_file_handling/data_structures_examples.py
python 02_data_structures_and_file_handling/file_handling_examples.py
python 02_data_structures_and_file_handling/contact_book.py

# Run Day 4 CLI Task Manager
python 04_sql_and_git_task_manager/main.py
# Or run with CLI flags
python 04_sql_and_git_task_manager/main.py --list
python 04_sql_and_git_task_manager/main.py --analytics
python 04_sql_and_git_task_manager/main.py --export

# Run Day 4 Automated Test Suite (25 Tests)
python -m unittest discover -s 04_sql_and_git_task_manager/tests -p "test_*.py" -v

# Run Day 5 Alembic Migrations & Seeder
cd 05_fastapi_pydantic_sqlalchemy
python -m alembic upgrade head
python scripts/seed_data.py

# Run Day 5 Live End-to-End Demo Script
python scripts/run_demo.py

# Run Day 5 Complete Automated Test Suite (31 Tests)
python -m pytest tests -v

# Launch Day 5 FastAPI Server (Swagger docs at http://127.0.0.1:8000/docs)
python run.py

# ==============================================================================
# Run Day 6: Authentication & Security
# ==============================================================================
cd ../06_authentication_and_security

# Seed Day 6 database with Admin, Standard User, and catalog items
python scripts/seed_data.py

# Run Day 6 Live End-to-End Demo Script (all 9 learning topics validated live)
python scripts/run_demo.py

# Run Day 6 Complete Automated Test Suite (41 Tests)
python -m pytest tests -v

# Launch Day 6 FastAPI Server (Swagger docs at http://127.0.0.1:8000/docs)
python run.py
```
