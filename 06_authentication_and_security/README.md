# 🔐 Day 6: Authentication & Security

Welcome to **Day 6** of the Python Backend & API Engineering Curriculum. This module implements a production-grade, hardened authentication and authorization architecture connecting **FastAPI**, **passlib + bcrypt**, **python-jose JWT**, **OAuth2 with Password Bearer flow**, **Role-Based Access Control (RBAC)**, **CORS Middleware**, and **Pydantic Settings**.

---

## 📋 Curriculum Learning Matrix & Implementation Overview

| Topic | Learning & Implementation Details | Expected Outcome |
| :--- | :--- | :--- |
| **Password Security** | Configured `passlib.context.CryptContext` with the `bcrypt` hashing scheme (work factor 12). Implemented `get_password_hash()` and `verify_password()`. Automatic per-password random salting. | Store passwords securely with salted bcrypt hashes without exposing plain-text credentials in database or API responses. |
| **JWT Authentication** | Implemented cryptographic JWT signing using `python-jose` with `HS256`. Generated short-lived access tokens (30 mins) and long-lived refresh tokens (7 days) with strict type claim isolation (`"type": "access"` vs `"type": "refresh"`). | Enable secure, stateless token-based authentication and session renewal. |
| **OAuth2 Flow** | Configured `OAuth2PasswordBearer` pointing to the login token URL. Implemented dual authentication flow supporting standard `application/x-www-form-urlencoded` credentials (for Swagger UI Authorize modal) and `application/json` payloads. | Standard OAuth2 password authentication flow fully compliant with OpenAPI specifications. |
| **Authentication Endpoints** | Built complete `/register`, `/login`, `/me`, and `/refresh` endpoints under `/api/v1/auth`. Handled duplicate conflicts, password complexity validation, and token rotation. | Provide complete user authentication, session initiation, profile extraction, and token rotation management. |
| **User Authentication Dependency** | Created FastAPI dependency `get_current_user` using `Depends(oauth2_scheme)`. Decoded and verified token signature, extracted user identity (`sub`), and resolved live database entity with active status validation. | Protect API endpoints and reliably identify the current user across request lifecycles. |
| **Role-Based Access Control (RBAC)** | Implemented `UserRole` enum (`admin`, `user`), database model column `role`, and dependency factory `require_roles(*allowed_roles)` and `get_current_admin_user`. Enforced HTTP 403 Forbidden on unauthorized roles. | Ensure users can access only authorized operations and prevent privilege escalation. |
| **CORS Configuration** | Configured FastAPI `CORSMiddleware` with configurable allowed origins (`BACKEND_CORS_ORIGINS`), allowed HTTP methods (`*`), headers (`*`), credentials support, and preflight max-age caching (600s). | Enable secure cross-origin communication between frontend single-page applications and backend APIs. |
| **Environment Configuration** | Structured centralized application configuration with `pydantic-settings` `BaseSettings` reading from `.env` and `.env.example`. Managed secret keys, algorithm, token expiry durations, and database credentials. | Manage sensitive secrets and application configuration safely outside the codebase. |
| **Practice – Secure Product API** | Applied authentication and authorization across the Product catalog API: unauthenticated users cannot read/write (401), standard users can only view products, and **only administrators can create (`POST`), edit (`PUT`/`PATCH`), or delete (`DELETE`) products** (403 for non-admins). | Complete secure catalog API with JWT authentication, role-based authorization, and protected routes. |

---

## 🏛️ Project Architecture & Directory Layout

```
06_authentication_and_security/
│
├── .env                              # PostgreSQL connection, JWT secret keys, and CORS origins
├── .env.example                      # Configuration template
├── alembic.ini                       # Alembic migration configuration
├── pytest.ini                        # Pytest configuration with async loop scope
├── requirements.txt                  # Python dependencies
├── run.py                            # Application entrypoint launcher (uvicorn)
├── README.md                         # Detailed documentation and architectural guide
│
├── alembic/                          # Alembic database migrations
│   ├── env.py                        # Async runner loading SQLAlchemy 2.0 Base.metadata
│   └── script.py.mako                # Revision migration template
│
├── app/
│   ├── main.py                       # FastAPI application factory, lifespan, CORS, and router registration
│   ├── core/
│   │   ├── config.py                 # Pydantic Settings V2 configuration (secrets, expiry, CORS)
│   │   ├── exceptions.py             # Custom domain exceptions (Auth, PermissionDenied, Not Found)
│   │   └── security.py               # passlib bcrypt hashing + python-jose JWT access & refresh tokens
│   ├── db/
│   │   ├── base.py                   # SQLAlchemy 2.0 DeclarativeBase & TimestampMixin
│   │   └── session.py                # AsyncEngine, AsyncSessionLocal, and get_async_db dependency
│   ├── models/
│   │   ├── user.py                   # SQLAlchemy 2.0 User model (role, is_superuser, hashed_password)
│   │   └── product.py                # SQLAlchemy 2.0 Product model (price, stock_quantity, owner)
│   ├── schemas/
│   │   ├── auth.py                   # Token, RefreshTokenRequest, LoginRequest, UserRegister schemas
│   │   ├── common.py                 # PaginatedResponse[T], MessageResponse, HealthCheckResponse
│   │   ├── user.py                   # Pydantic V2 User schemas (UserCreate, UserUpdate, UserResponse)
│   │   └── product.py                # Pydantic V2 Product schemas (ProductCreate, ProductUpdate, etc.)
│   ├── crud/
│   │   ├── base.py                   # Generic CRUDBase[Model, Create, Update] repository
│   │   ├── crud_user.py              # User CRUD (authenticate, create_with_hash, role support)
│   │   └── crud_product.py           # Product CRUD (multi-attribute search and owner linkage)
│   └── api/
│       ├── deps.py                   # Dependencies: get_current_user, require_roles, SessionDep
│       └── v1/
│           ├── router.py             # APIRouter mounting Auth, Users, and Products
│           └── endpoints/
│               ├── auth.py           # /register, /login, /me, /refresh endpoints
│               ├── users.py          # User management endpoints protected by RBAC
│               └── products.py       # Product catalog endpoints protected by Admin RBAC
│
├── scripts/
│   ├── seed_data.py                  # Database seeder creating Admin, Standard user, and sample products
│   └── run_demo.py                   # End-to-end automated live demonstration runner
│
└── tests/
    ├── conftest.py                   # Async client and isolated database fixtures
    ├── test_password_security.py     # Passlib + bcrypt hashing, salting, and validation (7 tests)
    ├── test_jwt_tokens.py            # Python-jose access/refresh encoding, claims, type checks (6 tests)
    ├── test_oauth2_flow.py           # OAuth2 password form authentication & WWW-Authenticate headers (3 tests)
    ├── test_auth_endpoints.py        # /register, /login, /me, /refresh integration tests (9 tests)
    ├── test_rbac_and_roles.py        # Role permission enforcement & privilege escalation checks (5 tests)
    ├── test_cors_middleware.py       # Cross-Origin headers & preflight validation (2 tests)
    ├── test_secure_product_api.py    # Product API protection & Admin-only write enforcement (6 tests)
    └── test_user_management.py       # User CRUD under RBAC (3 tests)
```

---

## 🔑 Key Architectural Details

### 1. Password Security (`passlib` + `bcrypt`)
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### 2. JWT Authentication & Token Rotation (`python-jose`)
Two distinct tokens are generated upon authentication:
- **Access Token**: Short validity (30 minutes), carries `"type": "access"` and `roles`, signed with `SECRET_KEY`.
- **Refresh Token**: Long validity (7 days), carries `"type": "refresh"`, signed with `REFRESH_SECRET_KEY`.
- **Type Isolation**: If an access token is presented to `/refresh`, it is rejected. If a refresh token is presented to `/products`, it is rejected.

### 3. Role-Based Access Control (RBAC) Dependency
```python
def require_roles(*allowed_roles: str):
    async def role_checker(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        user_role = current_user.role.lower() if current_user.role else "user"
        if user_role not in allowed_roles and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Requires role: {', '.join(allowed_roles)}.",
            )
        return current_user
    return role_checker

CurrentAdminUserDep = Annotated[User, Depends(require_roles("admin"))]
```

### 4. Practice: Secured Product API Permissions

| Endpoint | HTTP Method | Permitted Roles | Non-Permitted Response |
| :--- | :--- | :--- | :--- |
| `/api/v1/products` | `GET` | Authenticated (`user`, `admin`) | `401 Unauthorized` |
| `/api/v1/products/{id}` | `GET` | Authenticated (`user`, `admin`) | `401 Unauthorized` |
| `/api/v1/products` | `POST` | **Admin only** (`admin`) | `403 Forbidden` (`user`) / `401` |
| `/api/v1/products/{id}` | `PUT` | **Admin only** (`admin`) | `403 Forbidden` (`user`) / `401` |
| `/api/v1/products/{id}` | `PATCH` | **Admin only** (`admin`) | `403 Forbidden` (`user`) / `401` |
| `/api/v1/products/{id}` | `DELETE` | **Admin only** (`admin`) | `403 Forbidden` (`user`) / `401` |

---

## 🚀 How to Run the Application & Tests

### 1. Database Seeding
Populate the database with pre-configured Admin (`admin@techstore.io` / `AdminPass123!`), Standard User (`customer@techstore.io` / `UserPass123!`), and catalog items:
```powershell
python 06_authentication_and_security/scripts/seed_data.py
```

### 2. Run the End-to-End Live Demonstration Script
Executes all 9 learning topics sequentially against the ASGI app:
```powershell
python 06_authentication_and_security/scripts/run_demo.py
```

### 3. Run the Automated Test Suite (41 Tests)
Run the entire automated test suite:
```powershell
cd 06_authentication_and_security
python -m pytest tests -v
```

### 4. Launch the FastAPI Application
Launch Uvicorn server:
```powershell
cd 06_authentication_and_security
python run.py
```
- Interactive Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Interactive ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📡 API Authentication Flow (cURL Examples)

### Step 1: Register New User
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice_admin",
    "email": "alice@store.com",
    "password": "SecurePassword123!",
    "confirm_password": "SecurePassword123!",
    "full_name": "Alice Administrator",
    "role": "admin"
  }'
```

### Step 2: Log In & Obtain JWT Access and Refresh Tokens
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@store.com",
    "password": "SecurePassword123!"
  }'
```
Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Step 3: Access Protected Profile (`/auth/me`)
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/auth/me" \
  -H "Authorization: Bearer <access_token>"
```

### Step 4: Refresh Access Token (`/auth/refresh`)
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<refresh_token>"
  }'
```

### Step 5: Admin Creates Product (`POST /products`)
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/products" \
  -H "Authorization: Bearer <admin_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Ergonomic Mechanical Keyboard",
    "sku": "KB-ERG99",
    "price": 149.99,
    "category": "Peripherals"
  }'
```
*(Standard user with role `user` attempting this request will receive `403 Forbidden`)*.
