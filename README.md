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
| **Day 7** | **Mini-Project 2: Enterprise Task Management REST API** | JWT Authentication & OAuth2 Bearer, RBAC (`admin`, `manager`, `developer`, `viewer`), Project & Task CRUD, Status Workflow State Machine, Filtering & Pagination, Alembic Migrations, Swagger Docs, Postman Collection, and 41 automated `pytest` tests | Production-grade Task Management REST API with full lifecycle workflow enforcement and peer review sign-off. |
| **Day 8** | **Async Programming, Redis Caching & Celery Background Tasks** | Event loop internals, coroutines, `async def` vs `def`, `asyncio.gather()`, Redis Cache-Aside pattern, TTL, cache invalidation, Redis Sorted Set sliding-window rate limiting, Celery workers (Windows solo pool), Celery Beat periodic crons, retries with exponential backoff & jitter, Flower monitoring, FastAPI `BackgroundTasks` vs Celery comparison, and unified high-performance integrated dashboard with 16 automated tests | Production-grade high-concurrency API service with live Redis caching, algorithmic rate limiting, and distributed Celery background processing. |
| **Day 9** | **File Uploads, WebSockets, Testing & Code Quality** | `UploadFile`, streaming chunks, magic-byte inspection, Pillow aspect-ratio resizing, multi-resolution thumbnails (150x150, 600x600 WebP), static file serving, full-duplex WebSockets, `ConnectionManager` (personal, channels, broadcast, heartbeat), 38 automated `pytest` tests reaching 92%+ coverage, and Black, isort, Flake8, mypy code quality pipeline | Production-grade real-time media hub with instant WebSocket push notifications, responsive web dashboard, and CI/CD-ready lint-clean codebase with >92% test coverage. |
| **Day 10** | **Mini-Project 3: Production E-Commerce Backend Hub** | Complete authentication (JWT + RBAC), product catalog CRUD & Pillow image/thumbnail uploads, Redis shopping cart, transactional order checkout with atomic stock availability validation, Celery background confirmation email tasks, full-duplex WebSocket order tracking, Redis Cache-Aside product caching, and 48 automated tests | Production-grade e-commerce backend with Redis cart, stock validation, background email, real-time updates, and caching working end-to-end. |
| **Day 11** | **React Fundamentals, Hooks & Router Integration** | Components, JSX, props, composition slots, conditional & list rendering, `useState`, `useEffect` with cleanup, `useRef` DOM access & render counters, controlled inputs, SyntheticEvents, React Router v6 nested routes & `<Outlet />`, `useParams`, `useNavigate`, Axios service layer, request/response interceptors with silent 401 token refresh queues, `<ProtectedRoute />` with RBAC, and full FastAPI integration with 16 automated backend tests and 12-step demo verification | Production-grade multi-page React application with client-side routing, interactive fundamentals lab, and JWT-authenticated calls into the FastAPI backend. |
| **Day 12** | **Tailwind CSS, Shadcn/ui, Forms & Validation** | Utility-first styling, responsive breakpoints, persistent dark mode strategy, Shadcn/ui suite (`Button`, `Dialog`, `Table`, `Toast`, `DropdownMenu`, `Tabs`), `react-hook-form` state handling, `Zod` validation schemas with password refinements, dynamic form fields (`useFieldArray`), multi-step form workflows (Checkout & Product wizards), `react-dropzone` drag & drop image uploads with live preview, and WCAG A11y accessibility standards | Production-grade responsive UI with accessible client-validated forms, interactive Day 12 mastery lab, and seamless integration with FastAPI backend. |
| **Day 13** | **E-Commerce Frontend Architecture: Part 1** | Modular folder architecture, component composition, Axios HTTP service layer, reactive interceptors, JWT persistence, protected routes, and interactive Day 13 mastery lab | Production-grade fullstack storefront with real-time interceptor inspector and seamless FastAPI backend integration. |
| **Day 14** | **State Management, React Query & Performance Patterns** | Zustand global auth & cart stores, TanStack Query v5 caching, optimistic UI updates with snapshot rollback, infinite scrolling, React performance optimizations (`useMemo`, `useCallback`, `React.memo`), code splitting, and Lighthouse 90+ dashboard | High-performance storefront with 0ms optimistic UI updates, infinite product catalog, and interactive state benchmark lab. |
| **Day 15** | **TypeScript for React & Component Testing** | Strict TypeScript interfaces, generics (`ApiResponse<T>`, `<GenericList<T>>`), polymorphic components (`Button as="button" \| "a"`), typed FastAPI schema mirrors, Vitest & React Testing Library (41 passing tests), MSW v2 API mocking, Playwright E2E browser automation (9 passing journeys), and automated GitHub Actions CI pipeline | Enterprise-grade type-safe React storefront backed by 41 automated component tests, MSW mock isolation, Playwright E2E testing, and CI verification. |
| **Day 16** | **E-Commerce Frontend (Part 2)** | Global Zustand shopping cart store, React Hook Form + Zod checkout validation, TanStack React Query data layer & mutations, Order History & shipment tracking, Admin Dashboard with product CRUD & order status management, Dark/Light mode theme toggle, expanded automated test suite (63 passing tests), and end-to-end FastAPI integration | Complete, polished React e-commerce frontend with cart, checkout, order history, and admin dashboard fully connected end-to-end to FastAPI. |
| **Day 17** | **Full-Stack Integration & Real-Time Features** | FastAPI + React integration, WebSockets real-time order tracking (`/ws/orders/{id}`), live notifications panel, exponential backoff reconnection, and full-duplex Admin ↔ Customer Live Support Chat | Production-grade real-time storefront with zero-refresh live order status updates and interactive customer service. |
| **Day 18** | **Background Tasks & Advanced Search** | Celery + Redis distributed workers (Windows solo pool), ReportLab automated PDF invoices, bulk CSV product import, PostgreSQL full-text search (`tsvector`), and Trigram fuzzy search (`pg_trgm` `word_similarity > 0.28`) | High-scale catalog with typo-tolerant product search, background worker queue, and PDF receipt downloads. |
| **Day 19** | **API Security & Performance Optimization** | SlowAPI rate limiting (Login 5/min, CSV 3/min), OWASP safe client IP resolution, FastAPI GZip response compression, React code-splitting (`React.lazy`), image lazy loading, Lighthouse 94+ Mobile score, and 50-user Locust load testing | Hardened enterprise security with sub-35ms latency under 50 concurrent users and 41 passing pytest tests. |
| **Day 20** | **AI Focus: RAG Pipeline & Streaming AI Chat** | Free LLM providers (Groq LLaMA-3.3, Google Gemini), ChromaDB vector store with ONNX/MiniLM embeddings, RAG catalog retrieval, 3-tier fallback provider strategy, Server-Sent Events (SSE) token streaming, and interactive product source citations with 1-click cart addition | Enterprise-grade intelligent streaming AI Shopping Assistant grounded in store inventory with 45 passing automated tests. |
| **Day 21** | **AI Focus: Semantic Search, Redis Caching, Moderation & AI Agents** | AI-powered product descriptions, embedding-based semantic/vector search, AI content moderation, Redis AI response caching (SHA-256 keys), per-user rate limiting (tiered quotas), AI testing & mocking, multi-provider fallbacks, and autonomous AI agents with tool calling | Production-ready fullstack AI platform with 21 backend tests (100% passing) and 68 frontend Vitest tests (100% passing). |


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

### 6️⃣ Day 7: Mini-Project 2: Enterprise Task Management REST API
Located in: [`07_task_management_api/`](file:///c:/Users/venka/Desktop/Narasimha/07_task_management_api)

- **FastAPI Core & Security**: [`app/main.py`](file:///c:/Users/venka/Desktop/Narasimha/07_task_management_api/app/main.py), [`app/core/config.py`](file:///c:/Users/venka/Desktop/Narasimha/07_task_management_api/app/core/config.py), [`app/core/security.py`](file:///c:/Users/venka/Desktop/Narasimha/07_task_management_api/app/core/security.py), [`app/core/exceptions.py`](file:///c:/Users/venka/Desktop/Narasimha/07_task_management_api/app/core/exceptions.py).
- **Task Workflow State Machine**: [`app/core/workflow.py`](file:///c:/Users/venka/Desktop/Narasimha/07_task_management_api/app/core/workflow.py) (`TODO` ➔ `IN_PROGRESS` ➔ `REVIEW` ➔ `COMPLETED`, manager-only reopen protections).
- **Modern SQLAlchemy 2.0 Layer**: [`app/models/user.py`](file:///c:/Users/venka/Desktop/Narasimha/07_task_management_api/app/models/user.py), [`app/models/project.py`](file:///c:/Users/venka/Desktop/Narasimha/07_task_management_api/app/models/project.py), [`app/models/task.py`](file:///c:/Users/venka/Desktop/Narasimha/07_task_management_api/app/models/task.py), [`app/models/audit_log.py`](file:///c:/Users/venka/Desktop/Narasimha/07_task_management_api/app/models/audit_log.py).
- **Pydantic V2 Schemas**: [`app/schemas/`](file:///c:/Users/venka/Desktop/Narasimha/07_task_management_api/app/schemas) (`auth.py`, `user.py`, `project.py`, `task.py`, `audit_log.py`, `common.py`).
- **Async CRUD & Services**: [`app/crud/`](file:///c:/Users/venka/Desktop/Narasimha/07_task_management_api/app/crud), [`app/services/`](file:///c:/Users/venka/Desktop/Narasimha/07_task_management_api/app/services).
- **REST Endpoints & RBAC**: [`app/api/deps.py`](file:///c:/Users/venka/Desktop/Narasimha/07_task_management_api/app/api/deps.py), [`app/api/v1/endpoints/`](file:///c:/Users/venka/Desktop/Narasimha/07_task_management_api/app/api/v1/endpoints).
- **Alembic Migrations**: [`alembic/versions/001_initial_task_mgmt.py`](file:///c:/Users/venka/Desktop/Narasimha/07_task_management_api/alembic/versions/001_initial_task_mgmt.py).
- **Testing, Demos & Docs**: [`scripts/seed_data.py`](file:///c:/Users/venka/Desktop/Narasimha/07_task_management_api/scripts/seed_data.py), [`scripts/run_demo.py`](file:///c:/Users/venka/Desktop/Narasimha/07_task_management_api/scripts/run_demo.py), [`tests/`](file:///c:/Users/venka/Desktop/Narasimha/07_task_management_api/tests) (**41 automated `pytest` tests passing 100%**), [`postman_collection.json`](file:///c:/Users/venka/Desktop/Narasimha/07_task_management_api/postman_collection.json), [`CODE_REVIEW.md`](file:///c:/Users/venka/Desktop/Narasimha/07_task_management_api/CODE_REVIEW.md).

### 7️⃣ Day 8: Async Programming, Redis Caching & Celery Hub
Located in: [`08_async_redis_celery/`](file:///c:/Users/venka/Desktop/Narasimha/08_async_redis_celery)

- **Interactive Standalone Tutorials**:
  - [`tutorials/01_async_deep_dive.py`](file:///c:/Users/venka/Desktop/Narasimha/08_async_redis_celery/tutorials/01_async_deep_dive.py): Event loop internals, `async def` vs `def`, and `asyncio.gather()` live speedup benchmark.
  - [`tutorials/02_redis_caching_patterns.py`](file:///c:/Users/venka/Desktop/Narasimha/08_async_redis_celery/tutorials/02_redis_caching_patterns.py): Cache-Aside workflow, TTL automatic expiration, cache purge on mutation, and Redis ZSET sliding-window algorithm.
  - [`tutorials/03_celery_architecture.py`](file:///c:/Users/venka/Desktop/Narasimha/08_async_redis_celery/tutorials/03_celery_architecture.py): Celery topology (Producer -> Broker -> Worker -> Backend), lifecycle states, backoff retries with jitter, and Flower.
  - [`tutorials/04_bg_tasks_vs_celery.py`](file:///c:/Users/venka/Desktop/Narasimha/08_async_redis_celery/tutorials/04_bg_tasks_vs_celery.py): In-process vs out-of-process deep dive, crash scenarios, and decision framework.
- **FastAPI Core & Endpoints**:
  - [`app/main.py`](file:///c:/Users/venka/Desktop/Narasimha/08_async_redis_celery/app/main.py): FastAPI app with async lifespan management and CORS middleware.
  - [`app/core/redis_client.py`](file:///c:/Users/venka/Desktop/Narasimha/08_async_redis_celery/app/core/redis_client.py): Async Redis connection pool with automatic fallback to FakeRedis.
  - [`app/services/cache_service.py`](file:///c:/Users/venka/Desktop/Narasimha/08_async_redis_celery/app/services/cache_service.py): Cache-Aside service & `@cached` decorator.
  - [`app/services/rate_limiter.py`](file:///c:/Users/venka/Desktop/Narasimha/08_async_redis_celery/app/services/rate_limiter.py): Redis Sorted Set (ZSET) Sliding-Window Rate Limiter.
  - [`app/celery_app.py`](file:///c:/Users/venka/Desktop/Narasimha/08_async_redis_celery/app/celery_app.py): Celery application configuration & Beat schedule.
  - [`app/tasks/celery_tasks.py`](file:///c:/Users/venka/Desktop/Narasimha/08_async_redis_celery/app/tasks/celery_tasks.py): Heavy PDF batch job, auto-retry email task, periodic tasks.
  - [`app/tasks/fastapi_bg.py`](file:///c:/Users/venka/Desktop/Narasimha/08_async_redis_celery/app/tasks/fastapi_bg.py): In-process audit logging via FastAPI BackgroundTasks.
  - [`app/api/v1/endpoints/integrated.py`](file:///c:/Users/venka/Desktop/Narasimha/08_async_redis_celery/app/api/v1/endpoints/integrated.py): Unified final integration dashboard endpoint.
- **Runners, Demos & Tests**:
  - [`scripts/run_demo.py`](file:///c:/Users/venka/Desktop/Narasimha/08_async_redis_celery/scripts/run_demo.py): End-to-end automated live demonstration validating all topics.
  - [`tests/`](file:///c:/Users/venka/Desktop/Narasimha/08_async_redis_celery/tests): **16 automated pytest tests passing 100%**.
  - [`run.py`](file:///c:/Users/venka/Desktop/Narasimha/08_async_redis_celery/run.py), [`celery_worker.py`](file:///c:/Users/venka/Desktop/Narasimha/08_async_redis_celery/celery_worker.py), [`celery_beat.py`](file:///c:/Users/venka/Desktop/Narasimha/08_async_redis_celery/celery_beat.py).

### 8️⃣ Day 9: File Uploads, WebSockets, Testing & Code Quality
Located in: [`09_file_uploads_websockets_testing/`](file:///c:/Users/venka/Desktop/Narasimha/09_file_uploads_websockets_testing)

- **Interactive Standalone Tutorials**:
  - [`tutorials/01_file_upload_and_pillow.py`](file:///c:/Users/venka/Desktop/Narasimha/09_file_uploads_websockets_testing/tutorials/01_file_upload_and_pillow.py): `UploadFile`, chunk streaming, magic bytes inspection, Pillow aspect ratio resizing, EXIF privacy stripping.
  - [`tutorials/02_websocket_connection_manager.py`](file:///c:/Users/venka/Desktop/Narasimha/09_file_uploads_websockets_testing/tutorials/02_websocket_connection_manager.py): WebSocket protocol RFC 6455, `ConnectionManager` pattern, direct messaging, channels, broadcasting, disconnect cleanup.
  - [`tutorials/03_testing_fastapi_websockets.py`](file:///c:/Users/venka/Desktop/Narasimha/09_file_uploads_websockets_testing/tutorials/03_testing_fastapi_websockets.py): Testing with Pytest, `TestClient.websocket_connect()`, in-memory mock file fixtures, coverage calculation.
  - [`tutorials/04_code_quality_pipeline.py`](file:///c:/Users/venka/Desktop/Narasimha/09_file_uploads_websockets_testing/tutorials/04_code_quality_pipeline.py): The 5 Pillars of Python Code Quality: Black, isort, Flake8, mypy, and pre-commit hooks.
- **FastAPI Core & Endpoints**:
  - [`app/main.py`](file:///c:/Users/venka/Desktop/Narasimha/09_file_uploads_websockets_testing/app/main.py): FastAPI app with static file mounts, exception handlers, Web UI dashboard route.
  - [`app/core/config.py`](file:///c:/Users/venka/Desktop/Narasimha/09_file_uploads_websockets_testing/app/core/config.py): Pydantic Settings, storage paths, file limits, image presets.
  - [`app/core/security.py`](file:///c:/Users/venka/Desktop/Narasimha/09_file_uploads_websockets_testing/app/core/security.py): Filename sanitization, path traversal prevention, magic-byte MIME signature verification.
  - [`app/core/exceptions.py`](file:///c:/Users/venka/Desktop/Narasimha/09_file_uploads_websockets_testing/app/core/exceptions.py): Custom application exceptions and unified JSON handlers.
  - [`app/services/file_service.py`](file:///c:/Users/venka/Desktop/Narasimha/09_file_uploads_websockets_testing/app/services/file_service.py): Streaming upload persistence, SHA-256 integrity, file listing, deletion.
  - [`app/services/image_service.py`](file:///c:/Users/venka/Desktop/Narasimha/09_file_uploads_websockets_testing/app/services/image_service.py): Pillow image verification, aspect-ratio preserved resizing (LANCZOS), multi-resolution variants (thumbnail & medium WebP), EXIF stripping.
  - [`app/services/websocket_manager.py`](file:///c:/Users/venka/Desktop/Narasimha/09_file_uploads_websockets_testing/app/services/websocket_manager.py): Multi-client connection tracking, channel/room subscriptions, personal direct messaging, broadcast hub.
  - [`app/api/v1/endpoints/uploads.py`](file:///c:/Users/venka/Desktop/Narasimha/09_file_uploads_websockets_testing/app/api/v1/endpoints/uploads.py): Single & batch file upload endpoints, file listing, download, delete.
  - [`app/api/v1/endpoints/websockets.py`](file:///c:/Users/venka/Desktop/Narasimha/09_file_uploads_websockets_testing/app/api/v1/endpoints/websockets.py): Real-time bi-directional WebSocket endpoint `/ws/{client_id}`, channel endpoint, HTTP-to-WebSocket broadcast bridge.
  - [`app/api/v1/endpoints/integrated.py`](file:///c:/Users/venka/Desktop/Narasimha/09_file_uploads_websockets_testing/app/api/v1/endpoints/integrated.py): Unified endpoint combining file upload + Pillow processing + instant real-time WebSocket push broadcast.
- **Frontend Web Dashboard**:
  - [`app/static/index.html`](file:///c:/Users/venka/Desktop/Narasimha/09_file_uploads_websockets_testing/app/static/index.html), [`app/static/styles.css`](file:///c:/Users/venka/Desktop/Narasimha/09_file_uploads_websockets_testing/app/static/styles.css), [`app/static/app.js`](file:///c:/Users/venka/Desktop/Narasimha/09_file_uploads_websockets_testing/app/static/app.js): Modern interactive dashboard with drag-and-drop uploads, live WebSocket event cards, ping tool, and gallery.
- **Code Quality, Testing & Demos**:
  - [`pyproject.toml`](file:///c:/Users/venka/Desktop/Narasimha/09_file_uploads_websockets_testing/pyproject.toml), [`.flake8`](file:///c:/Users/venka/Desktop/Narasimha/09_file_uploads_websockets_testing/.flake8), [`.pre-commit-config.yaml`](file:///c:/Users/venka/Desktop/Narasimha/09_file_uploads_websockets_testing/.pre-commit-config.yaml).
  - [`scripts/run_demo.py`](file:///c:/Users/venka/Desktop/Narasimha/09_file_uploads_websockets_testing/scripts/run_demo.py): End-to-end automated live demonstration validating all 5 learning topics.
  - [`tests/`](file:///c:/Users/venka/Desktop/Narasimha/09_file_uploads_websockets_testing/tests): **38 automated pytest tests passing 100% with 92.31% code coverage**.
  - [`run.py`](file:///c:/Users/venka/Desktop/Narasimha/09_file_uploads_websockets_testing/run.py): FastAPI application launcher.

### 9️⃣ Day 10: Mini-Project 3: Production E-Commerce Backend Hub
Located in: [`10_ecommerce_mini_project/`](file:///c:/Users/venka/Desktop/Narasimha/10_ecommerce_mini_project)

- **FastAPI Core & Real-Time Engine**:
  - [`app/main.py`](file:///c:/Users/venka/Desktop/Narasimha/10_ecommerce_mini_project/app/main.py): FastAPI application with async lifespan, database table creation, and static mounts.
  - [`app/core/config.py`](file:///c:/Users/venka/Desktop/Narasimha/10_ecommerce_mini_project/app/core/config.py): Pydantic Settings V2 for PostgreSQL, Redis, Celery, JWT auth, and image limits.
  - [`app/core/security.py`](file:///c:/Users/venka/Desktop/Narasimha/10_ecommerce_mini_project/app/core/security.py): Password hashing via bcrypt, JWT access & refresh token encoding/decoding.
  - [`app/core/redis_client.py`](file:///c:/Users/venka/Desktop/Narasimha/10_ecommerce_mini_project/app/core/redis_client.py): Async Redis connection pool with automatic FakeRedis fallback.
  - [`app/core/websocket_manager.py`](file:///c:/Users/venka/Desktop/Narasimha/10_ecommerce_mini_project/app/core/websocket_manager.py): Full-duplex WebSocket ConnectionManager with channel subscriptions.
  - [`app/celery_app.py`](file:///c:/Users/venka/Desktop/Narasimha/10_ecommerce_mini_project/app/celery_app.py): Distributed Celery task app with Windows solo pool and eager fallback.
- **Relational Domain Models & Schemas**:
  - [`app/models/user.py`](file:///c:/Users/venka/Desktop/Narasimha/10_ecommerce_mini_project/app/models/user.py): User entity with `UserRole` (`admin`, `customer`).
  - [`app/models/product.py`](file:///c:/Users/venka/Desktop/Narasimha/10_ecommerce_mini_project/app/models/product.py): Product model with inventory stock, price, category, and image URLs.
  - [`app/models/order.py`](file:///c:/Users/venka/Desktop/Narasimha/10_ecommerce_mini_project/app/models/order.py): Order & OrderItem models with `OrderStatus` state machine.
  - [`app/schemas/`](file:///c:/Users/venka/Desktop/Narasimha/10_ecommerce_mini_project/app/schemas): Pydantic validation schemas (`auth.py`, `user.py`, `product.py`, `cart.py`, `order.py`).
- **Service Layer & Background Tasks**:
  - [`app/services/cache_service.py`](file:///c:/Users/venka/Desktop/Narasimha/10_ecommerce_mini_project/app/services/cache_service.py): Cache-Aside logic & pattern-based listing invalidation.
  - [`app/services/cart_service.py`](file:///c:/Users/venka/Desktop/Narasimha/10_ecommerce_mini_project/app/services/cart_service.py): Redis Hash shopping cart (`cart:{user_id}`) with live database stock verification.
  - [`app/services/order_service.py`](file:///c:/Users/venka/Desktop/Narasimha/10_ecommerce_mini_project/app/services/order_service.py): Atomic checkout transaction, strict stock validation, inventory decrements, and cancellation stock refunds.
  - [`app/services/image_service.py`](file:///c:/Users/venka/Desktop/Narasimha/10_ecommerce_mini_project/app/services/image_service.py): Magic bytes inspection and Pillow LANCZOS aspect-ratio thumbnail generator.
  - [`app/tasks/order_tasks.py`](file:///c:/Users/venka/Desktop/Narasimha/10_ecommerce_mini_project/app/tasks/order_tasks.py): Celery asynchronous confirmation and status update email tasks.
- **REST Endpoints & WebSockets**:
  - [`app/api/v1/endpoints/auth.py`](file:///c:/Users/venka/Desktop/Narasimha/10_ecommerce_mini_project/app/api/v1/endpoints/auth.py): Register, login, token refresh, `/me` profile.
  - [`app/api/v1/endpoints/products.py`](file:///c:/Users/venka/Desktop/Narasimha/10_ecommerce_mini_project/app/api/v1/endpoints/products.py): Cached listing with `X-Cache` header, detail, Admin CRUD, image uploads.
  - [`app/api/v1/endpoints/cart.py`](file:///c:/Users/venka/Desktop/Narasimha/10_ecommerce_mini_project/app/api/v1/endpoints/cart.py): Redis cart get, add, update quantity, remove item, clear cart.
  - [`app/api/v1/endpoints/orders.py`](file:///c:/Users/venka/Desktop/Narasimha/10_ecommerce_mini_project/app/api/v1/endpoints/orders.py): Checkout, list orders, detail, status update, order cancellation.
  - [`app/api/v1/endpoints/websockets.py`](file:///c:/Users/venka/Desktop/Narasimha/10_ecommerce_mini_project/app/api/v1/endpoints/websockets.py): Full-duplex WebSocket stream `/ws/orders` and `/ws/broadcast` HTTP bridge.
  - [`app/api/v1/endpoints/tasks.py`](file:///c:/Users/venka/Desktop/Narasimha/10_ecommerce_mini_project/app/api/v1/endpoints/tasks.py): Celery task inspection endpoint.
- **Frontend Web Dashboard**:
  - [`app/static/index.html`](file:///c:/Users/venka/Desktop/Narasimha/10_ecommerce_mini_project/app/static/index.html), [`app/static/css/styles.css`](file:///c:/Users/venka/Desktop/Narasimha/10_ecommerce_mini_project/app/static/css/styles.css), [`app/static/js/app.js`](file:///c:/Users/venka/Desktop/Narasimha/10_ecommerce_mini_project/app/static/js/app.js): Modern interactive dashboard with live catalog, Redis cart drawer, real-time WebSocket order tracking ticker, and Celery outbox log.
- **Documentation, Testing & Tooling**:
  - [`postman_collection.json`](file:///c:/Users/venka/Desktop/Narasimha/10_ecommerce_mini_project/postman_collection.json): Production Postman collection v2.1 with 20 pre-configured requests.
  - [`scripts/seed_data.py`](file:///c:/Users/venka/Desktop/Narasimha/10_ecommerce_mini_project/scripts/seed_data.py): Sample database seeder with categories, products, and Pillow thumbnails.
  - [`scripts/demo_flow.py`](file:///c:/Users/venka/Desktop/Narasimha/10_ecommerce_mini_project/scripts/demo_flow.py): End-to-end automated command-line walkthrough script.
  - [`tests/`](file:///c:/Users/venka/Desktop/Narasimha/10_ecommerce_mini_project/tests): **48 automated pytest tests passing 100%**.
  - [`run.py`](file:///c:/Users/venka/Desktop/Narasimha/10_ecommerce_mini_project/run.py), [`celery_worker.py`](file:///c:/Users/venka/Desktop/Narasimha/10_ecommerce_mini_project/celery_worker.py).

### 🔟 Day 11: React Fundamentals, Hooks & Router Integration
Located in: [`11_react_fundamentals_hooks_router/`](file:///c:/Users/venka/Desktop/Narasimha/11_react_fundamentals_hooks_router)

- **FastAPI Core & JWT Backend**:
  - [`backend/app/main.py`](file:///c:/Users/venka/Desktop/Narasimha/11_react_fundamentals_hooks_router/backend/app/main.py): FastAPI application with async lifespan schema creation and CORS middleware.
  - [`backend/app/core/config.py`](file:///c:/Users/venka/Desktop/Narasimha/11_react_fundamentals_hooks_router/backend/app/core/config.py): Pydantic Settings, JWT secret keys, and CORS origins.
  - [`backend/app/core/database.py`](file:///c:/Users/venka/Desktop/Narasimha/11_react_fundamentals_hooks_router/backend/app/core/database.py): Async SQLAlchemy 2.0 engine and session factory (`sqlite+aiosqlite`).
  - [`backend/app/core/security.py`](file:///c:/Users/venka/Desktop/Narasimha/11_react_fundamentals_hooks_router/backend/app/core/security.py): Passlib bcrypt password hashing, JWT access & refresh token encoders.
  - [`backend/app/api/deps.py`](file:///c:/Users/venka/Desktop/Narasimha/11_react_fundamentals_hooks_router/backend/app/api/deps.py): OAuth2 password bearer flow, `get_current_user`, and role enforcement.
  - [`backend/app/api/v1/endpoints/auth.py`](file:///c:/Users/venka/Desktop/Narasimha/11_react_fundamentals_hooks_router/backend/app/api/v1/endpoints/auth.py): `/login`, `/register`, `/me`, and `/refresh` token rotation.
  - [`backend/app/api/v1/endpoints/items.py`](file:///c:/Users/venka/Desktop/Narasimha/11_react_fundamentals_hooks_router/backend/app/api/v1/endpoints/items.py): Item CRUD, category filtering, search, and pagination.
  - [`backend/app/api/v1/endpoints/analytics.py`](file:///c:/Users/venka/Desktop/Narasimha/11_react_fundamentals_hooks_router/backend/app/api/v1/endpoints/analytics.py): Dashboard analytics telemetry and distribution aggregations.
- **Modern React 18 & Vite Frontend**:
  - [`frontend/src/main.jsx`](file:///c:/Users/venka/Desktop/Narasimha/11_react_fundamentals_hooks_router/frontend/src/main.jsx): React DOM application entrypoint.
  - [`frontend/src/App.jsx`](file:///c:/Users/venka/Desktop/Narasimha/11_react_fundamentals_hooks_router/frontend/src/App.jsx): React Router v6 nested route tree, `AuthProvider`, route guards.
  - [`frontend/src/context/AuthContext.jsx`](file:///c:/Users/venka/Desktop/Narasimha/11_react_fundamentals_hooks_router/frontend/src/context/AuthContext.jsx): Global auth state, session persistence, automatic expiration listener.
  - [`frontend/src/services/api.js`](file:///c:/Users/venka/Desktop/Narasimha/11_react_fundamentals_hooks_router/frontend/src/services/api.js): Centralized Axios client, Bearer request interceptor, 401 refresh token queue and replay.
  - [`frontend/src/services/authService.js`](file:///c:/Users/venka/Desktop/Narasimha/11_react_fundamentals_hooks_router/frontend/src/services/authService.js), [`frontend/src/services/itemService.js`](file:///c:/Users/venka/Desktop/Narasimha/11_react_fundamentals_hooks_router/frontend/src/services/itemService.js): Domain service layers.
  - [`frontend/src/hooks/`](file:///c:/Users/venka/Desktop/Narasimha/11_react_fundamentals_hooks_router/frontend/src/hooks): Custom hooks (`useAuth.js`, `useDebounce.js`, `useAsync.js`).
  - [`frontend/src/components/common/`](file:///c:/Users/venka/Desktop/Narasimha/11_react_fundamentals_hooks_router/frontend/src/components/common): Reusable UI components (`Button`, `Input`, `Card`, `Badge`, `Alert`, `Modal`, `Spinner`, `Navbar`, `Sidebar`).
  - [`frontend/src/components/items/`](file:///c:/Users/venka/Desktop/Narasimha/11_react_fundamentals_hooks_router/frontend/src/components/items): Task management UI (`ItemCard`, `ItemForm`, `ItemList`).
  - [`frontend/src/components/routing/`](file:///c:/Users/venka/Desktop/Narasimha/11_react_fundamentals_hooks_router/frontend/src/components/routing): Route guards (`AppLayout`, `ProtectedRoute`, `PublicOnlyRoute`).
  - [`frontend/src/pages/`](file:///c:/Users/venka/Desktop/Narasimha/11_react_fundamentals_hooks_router/frontend/src/pages): Application views (`HomePage`, `FundamentalsPage`, `LoginPage`, `RegisterPage`, `DashboardPage`, `ItemsPage`, `ItemDetailPage`, `ProfilePage`, `AdminPage`, `NotFoundPage`).
- **Testing, Seeding & Demos**:
  - [`scripts/run_demo.py`](file:///c:/Users/venka/Desktop/Narasimha/11_react_fundamentals_hooks_router/scripts/run_demo.py): Automated 12-step end-to-end verification script.
  - [`backend/seed_data.py`](file:///c:/Users/venka/Desktop/Narasimha/11_react_fundamentals_hooks_router/backend/seed_data.py): Sample database seeder for admin & demo users and items.
  - [`backend/tests/`](file:///c:/Users/venka/Desktop/Narasimha/11_react_fundamentals_hooks_router/backend/tests): **16 automated pytest tests passing 100%**.
  - [`README.md`](file:///c:/Users/venka/Desktop/Narasimha/11_react_fundamentals_hooks_router/README.md): Comprehensive Day 11 architectural guide.

### 1️⃣1️⃣ Day 12: Tailwind CSS, Shadcn/ui, Forms & Validation Fullstack Hub
Located in: [`ecommerce-frontend/`](file:///c:/Users/venka/Desktop/Narasimha/ecommerce-frontend) (connected to [`ecommerce-backend/`](file:///c:/Users/venka/Desktop/Narasimha/ecommerce-backend))

- **Design System & Theme Engine**:
  - [`ecommerce-frontend/tailwind.config.js`](file:///c:/Users/venka/Desktop/Narasimha/ecommerce-frontend/tailwind.config.js): Tailwind CSS tokens, container queries, HSL design tokens, animation keyframes, and `class` strategy dark mode.
  - [`ecommerce-frontend/src/index.css`](file:///c:/Users/venka/Desktop/Narasimha/ecommerce-frontend/src/index.css): `@tailwind base; components; utilities;` with light `:root` and `.dark` palettes.
  - [`ecommerce-frontend/src/context/ThemeContext.jsx`](file:///c:/Users/venka/Desktop/Narasimha/ecommerce-frontend/src/context/ThemeContext.jsx): Persistent Light/Dark/System theme context.
  - [`ecommerce-frontend/src/lib/utils.js`](file:///c:/Users/venka/Desktop/Narasimha/ecommerce-frontend/src/lib/utils.js): Canonical `cn()` utility (`clsx` + `tailwind-merge`).
- **Shadcn/ui Accessible Component Suite**:
  - [`src/components/ui/button.jsx`](file:///c:/Users/venka/Desktop/Narasimha/ecommerce-frontend/src/components/ui/button.jsx): Button with 7 CVA variants, 4 sizes, and integrated loading spinner.
  - [`src/components/ui/dialog.jsx`](file:///c:/Users/venka/Desktop/Narasimha/ecommerce-frontend/src/components/ui/dialog.jsx): Accessible Radix modal dialog with focus trapping and Escape handling.
  - [`src/components/ui/table.jsx`](file:///c:/Users/venka/Desktop/Narasimha/ecommerce-frontend/src/components/ui/table.jsx): Data Table (Header, Body, Footer, Head, Row, Cell, Caption).
  - [`src/components/ui/dropdown-menu.jsx`](file:///c:/Users/venka/Desktop/Narasimha/ecommerce-frontend/src/components/ui/dropdown-menu.jsx): Radix DropdownMenu with sub-items, separators, and shortcuts.
  - [`src/components/ui/sonner.jsx`](file:///c:/Users/venka/Desktop/Narasimha/ecommerce-frontend/src/components/ui/sonner.jsx): Sonner toast integration for success, error, warning, info, and actions.
  - [`src/components/ui/tabs.jsx`](file:///c:/Users/venka/Desktop/Narasimha/ecommerce-frontend/src/components/ui/tabs.jsx): Tabbed panels used in Admin and Showcase Lab.
  - [`src/components/ui/input.jsx`](file:///c:/Users/venka/Desktop/Narasimha/ecommerce-frontend/src/components/ui/input.jsx), [`src/components/ui/label.jsx`](file:///c:/Users/venka/Desktop/Narasimha/ecommerce-frontend/src/components/ui/label.jsx), [`src/components/ui/card.jsx`](file:///c:/Users/venka/Desktop/Narasimha/ecommerce-frontend/src/components/ui/card.jsx), [`src/components/ui/badge.jsx`](file:///c:/Users/venka/Desktop/Narasimha/ecommerce-frontend/src/components/ui/badge.jsx), [`src/components/ui/textarea.jsx`](file:///c:/Users/venka/Desktop/Narasimha/ecommerce-frontend/src/components/ui/textarea.jsx).
- **React Forms, Zod Validation & Form Accessibility (A11y)**:
  - [`src/components/ui/form.jsx`](file:///c:/Users/venka/Desktop/Narasimha/ecommerce-frontend/src/components/ui/form.jsx): Form primitives with automatic `aria-invalid`, `aria-describedby`, accessible `<label htmlFor>`, and `role="alert"`.
  - [`src/schemas/authSchemas.js`](file:///c:/Users/venka/Desktop/Narasimha/ecommerce-frontend/src/schemas/authSchemas.js): Zod schemas for login & registration with password match refinement.
  - [`src/schemas/productSchemas.js`](file:///c:/Users/venka/Desktop/Narasimha/ecommerce-frontend/src/schemas/productSchemas.js): Zod product schemas with numeric type coercion and dynamic specification array.
  - [`src/schemas/checkoutSchemas.js`](file:///c:/Users/venka/Desktop/Narasimha/ecommerce-frontend/src/schemas/checkoutSchemas.js): Step-by-step schemas with conditional superRefine validation.
- **Dynamic Forms & Multi-Step Workflows**:
  - [`src/pages/CheckoutPage.jsx`](file:///c:/Users/venka/Desktop/Narasimha/ecommerce-frontend/src/pages/CheckoutPage.jsx): 4-step multi-step checkout workflow with persistent state across steps.
  - [`src/pages/AdminPage.jsx`](file:///c:/Users/venka/Desktop/Narasimha/ecommerce-frontend/src/pages/AdminPage.jsx): 4-step Product Creation Wizard with dynamic attributes via `useFieldArray`.
- **Drag & Drop File Uploads & Live Previews**:
  - [`src/components/ui/image-dropzone.jsx`](file:///c:/Users/venka/Desktop/Narasimha/ecommerce-frontend/src/components/ui/image-dropzone.jsx): `react-dropzone` drag-and-drop zone with instant Object URL preview, size limit check, and direct upload into Day 10 FastAPI Pillow service.
- **Day 12 Interactive Mastery Lab**:
  - [`src/pages/Day12LabPage.jsx`](file:///c:/Users/venka/Desktop/Narasimha/ecommerce-frontend/src/pages/Day12LabPage.jsx): Dedicated interactive testing ground with 6 testbeds (Shadcn Suite, Zod Validation Playground, Dynamic useFieldArray Builder, Multi-Step Wizard, Dropzone Sandbox, and A11y & Dark Mode Inspector).

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

# ==============================================================================
# Run Day 7: Mini-Project 2: Enterprise Task Management REST API
# ==============================================================================
cd ../07_task_management_api

# Run Day 7 Alembic Migrations & Seeder
python -m alembic upgrade head
python scripts/seed_data.py

# Run Day 7 Live End-to-End Demo Script (all 9 learning topics validated live)
python scripts/run_demo.py

# Run Day 7 Complete Automated Test Suite (41 Tests)
python -m pytest tests -v

# Launch Day 7 FastAPI Server (Swagger docs at http://127.0.0.1:8000/docs)
python run.py

# ==============================================================================
# Run Day 8: Async Programming, Redis Caching & Celery Hub
# ==============================================================================
cd ../08_async_redis_celery

# 1. Run Interactive Tutorials
python tutorials/01_async_deep_dive.py
python tutorials/02_redis_caching_patterns.py
python tutorials/03_celery_architecture.py
python tutorials/04_bg_tasks_vs_celery.py

# 2. Run Day 8 Live End-to-End Demo Script (all 6 topics validated live)
python scripts/run_demo.py

# 3. Run Day 8 Complete Automated Test Suite (16 Tests)
python -m pytest tests -v

# 4. Launch Day 8 FastAPI Server (Swagger docs at http://127.0.0.1:8000/docs)
python run.py

# ==============================================================================
# Run Day 9: File Uploads, WebSockets, Testing & Code Quality
# ==============================================================================
cd ../09_file_uploads_websockets_testing

# 1. Run Interactive Tutorials
python tutorials/01_file_upload_and_pillow.py
python tutorials/02_websocket_connection_manager.py
python tutorials/03_testing_fastapi_websockets.py
python tutorials/04_code_quality_pipeline.py

# 2. Run Day 9 Live End-to-End Demo Script (all 5 topics validated live)
python scripts/run_demo.py

# 3. Run Day 9 Complete Automated Test Suite (38 Tests, 92%+ coverage)
python -m pytest tests --cov=app --cov-report=term-missing

# 4. Run Code Quality Checks (Black, isort, Flake8, mypy)
python -m black --check .
python -m isort --check-only .
python -m flake8 .
python -m mypy app

# 5. Launch Day 9 FastAPI Server (Web Dashboard at http://127.0.0.1:8000/)
python run.py

# ==============================================================================
# Run Day 10: Mini-Project 3: Production E-Commerce Backend Hub
# ==============================================================================
cd ../10_ecommerce_mini_project

# 1. Seed Database & Sample Catalog with Pillow Thumbnails
python scripts/seed_data.py

# 2. Run Day 10 Live End-to-End Demo Script (all topics validated live)
python scripts/demo_flow.py

# 3. Run Day 10 Complete Automated Test Suite (48 Tests passing 100%)
python -m pytest tests -v

# 4. Optional: Run Celery Distributed Worker (Solo Pool for Windows)
python celery_worker.py

# 5. Launch Day 10 FastAPI Server (Interactive Storefront at http://127.0.0.1:8000/)
python run.py

# ==============================================================================
# Run Day 11: React Fundamentals, Hooks & Router SPA (Connected to Day 10 Backend)
# ==============================================================================
# Option A: Run Fullstack with Day 10 E-Commerce Backend (Port 8000)
# Terminal 1: Launch Day 10 E-Commerce Backend Hub
cd ../10_ecommerce_mini_project
python run.py

# Terminal 2: Launch Day 11 React 18 & Vite Frontend SPA (Port 5173)
cd ../11_react_fundamentals_hooks_router/frontend
$env:PATH = "C:\Program Files\nodejs;$env:PATH"
npm.cmd run dev
# Open Storefront in browser at http://localhost:5173/ (Catalog, Redis Cart, Orders & WebSockets)

# Option B: Run Standalone Day 11 Backend & Automated Verification
cd ../11_react_fundamentals_hooks_router
python backend/seed_data.py
python scripts/run_demo.py
$env:PYTHONPATH = "backend"
python -m pytest backend/tests -v

# ==============================================================================
# Run Day 12: Tailwind CSS, Shadcn/ui, Forms & Validation Fullstack Hub
# ==============================================================================
# Terminal 1: Launch FastAPI Backend Hub (Port 8000)
cd ../ecommerce-backend
python scripts/seed_data.py
python run.py

# Terminal 2: Launch Vite Storefront & Day 12 Lab (Port 5173)
cd ../ecommerce-frontend
npm.cmd run dev
# Open in browser:
# - Storefront: http://localhost:5173/
# - Day 12 Interactive Mastery Lab: http://localhost:5173/day12-lab
# - Multi-Step Checkout: http://localhost:5173/checkout
# - Admin Control Hub: http://localhost:5173/admin
# - Interactive API Docs: http://127.0.0.1:8000/docs

# ==============================================================================
# Run Day 15: TypeScript for React & Component Testing Fullstack Hub
# ==============================================================================
# Terminal 1: Launch Frontend & Interactive Testing Lab (Port 5173)
cd ../15_typescript_react_component_testing/frontend
npm run dev

# Run Automated Test Suite (41 Vitest Tests + 9 Playwright E2E Tests):
npm run typecheck       # Strict TypeScript verification
npm run test:run        # Run 41 Vitest component & store tests
npm run test:coverage   # V8 test coverage breakdown
npm run test:e2e        # Run 9 Playwright browser user journeys
npm run test:ci         # Run complete CI pipeline locally

# ==============================================================================
# Run Day 16: E-Commerce Frontend (Part 2) (Continuous in Day 15 Hub)
# ==============================================================================
# Terminal 1: Launch Backend (Port 8000)
cd ../15_typescript_react_component_testing/backend
python run.py

# Terminal 2: Launch Frontend Storefront & Admin Hub (Port 5173)
cd ../15_typescript_react_component_testing/frontend
npm run dev

# Run Day 16 Expanded Test Suite (63 automated Vitest tests passing 100%):
npm run test:run

# ==============================================================================
# Run Day 20: AI Focus — RAG Pipeline & Streaming AI Chat
# ==============================================================================
# Terminal 1: Launch FastAPI Backend Hub (Port 8000)
cd ../20_ai_focus/backend
.\.venv\Scripts\uvicorn.exe app.main:app --reload --port 8000

# Terminal 2: Launch Vite Storefront (Port 5173)
cd ../20_ai_focus/frontend
npm run dev

# Run Automated Test Suite:
cd ../20_ai_focus/backend
.\.venv\Scripts\pytest.exe tests/test_day20_ai_rag.py -v

# ==============================================================================
# Run Day 21: AI Focus — Semantic Search, Redis Caching, Moderation & Agents
# ==============================================================================
# Terminal 1: Launch FastAPI Backend Hub (Port 8000)
cd ../21_ai_focus/backend
.\.venv\Scripts\uvicorn.exe app.main:app --reload --port 8000

# Terminal 2: Launch React 18 & Vite Frontend (Port 5173)
cd ../21_ai_focus/frontend
npm run dev

# Run Day 21 Complete Automated Backend Test Suite (21 Tests passing 100%):
cd ../21_ai_focus/backend
.\.venv\Scripts\pytest.exe tests/test_day20_ai_rag.py tests/test_day21_ai_focus.py -v

# Run Day 21 Complete Automated Frontend Test Suite (68 Tests passing 100%):
cd ../21_ai_focus/frontend
npm run typecheck
npm run test:run
```



