# 🚀 Day 5: FastAPI Setup, Pydantic V2 & SQLAlchemy 2.0

Welcome to **Day 5** of the Python Backend & API Engineering Curriculum. This module implements a production-grade, asynchronous RESTful API architecture connecting **FastAPI**, **Pydantic V2**, **SQLAlchemy 2.0**, **Alembic**, and **PostgreSQL**.

---

## 📋 Curriculum Learning Matrix

| Topic | Learning & Implementation Details | Expected Outcome |
| :--- | :--- | :--- |
| **FastAPI Setup** | Modular project structure (`app/core`, `app/db`, `app/models`, `app/schemas`, `app/crud`, `app/api`), path/query parameters, `response_model`, status codes, OpenAPI/Swagger metadata, and lifespan context. | Master modern FastAPI project structure and high-performance API design. |
| **Pydantic V2** | `Field()` constraints, `@field_validator` with `mode='before'` / `mode='after'`, `@model_validator` cross-field logic, nested models, and strict schema separation (`Base`, `Create`, `Update`, `Response`). | Construct robust, self-documenting data validation and serialization contracts. |
| **SQLAlchemy 2.0** | `DeclarativeBase`, typed `Mapped[T]` and `mapped_column()` descriptors, 1:N relationships (`relationship()`), `cascade="all, delete-orphan"`, async engine (`asyncpg`), and `AsyncSession` dependency injection. | Seamlessly integrate FastAPI with PostgreSQL using modern, type-safe SQLAlchemy 2.0. |
| **Alembic Migrations** | Asynchronous Alembic configuration (`alembic.ini`, `env.py`), revision generation, and automated PostgreSQL schema migration (`upgrade head`). | Professionally manage database schema evolution and migrations. |
| **CRUD Development** | Repository pattern (`CRUDBase`, `CRUDUser`, `CRUDProduct`), multi-attribute filtering (category, price range, search query), pagination, and secure password hashing with `bcrypt`. | Build robust Create, Read, Update, and Delete business services. |
| **Final Integration** | Full stack integration verified by 26 automated unit & integration tests (`pytest`, `httpx`), interactive Swagger UI (`/docs`), and an automated demo runner (`run_demo.py`). | Production-ready, tested service running against live PostgreSQL. |

---

## 🏛️ Project Architecture & Directory Layout

```
05_fastapi_pydantic_sqlalchemy/
│
├── .env                              # PostgreSQL connection and environment variables
├── .env.example                      # Configuration template
├── alembic.ini                       # Alembic migration configuration
├── pytest.ini                        # Pytest configuration with async loop scope
├── requirements.txt                  # Python dependencies
├── run.py                            # Application entrypoint launcher (uvicorn)
│
├── alembic/                          # Alembic database migrations
│   ├── env.py                        # Async runner loading SQLAlchemy 2.0 Base.metadata
│   ├── script.py.mako                # Revision migration template
│   └── versions/
│       └── 001_initial_users_and_products.py  # Initial schema migration
│
├── app/
│   ├── main.py                       # FastAPI application factory, lifespan, CORS, error handling
│   ├── core/
│   │   ├── config.py                 # Pydantic Settings V2 configuration
│   │   ├── exceptions.py             # Custom domain exceptions and HTTP handlers
│   │   └── security.py               # Password hashing & verification via bcrypt
│   ├── db/
│   │   ├── base.py                   # SQLAlchemy 2.0 DeclarativeBase & TimestampMixin
│   │   └── session.py                # AsyncEngine, AsyncSessionLocal, and get_async_db dependency
│   ├── models/
│   │   ├── user.py                   # SQLAlchemy 2.0 User model (Mapped, mapped_column, 1:N)
│   │   └── product.py                # SQLAlchemy 2.0 Product model (Mapped, ForeignKey, N:1)
│   ├── schemas/
│   │   ├── common.py                 # PaginatedResponse[T], MessageResponse, HealthCheckResponse
│   │   ├── user.py                   # Pydantic V2 User schemas (Field, validators, nested)
│   │   └── product.py                # Pydantic V2 Product schemas (discount check, SKU regex)
│   ├── crud/
│   │   ├── base.py                   # Generic CRUDBase[Model, Create, Update] repository
│   │   ├── crud_user.py              # User CRUD (authentication, get_by_email, get_with_products)
│   │   └── crud_product.py           # Product CRUD (multi-filter, full-text search, by owner)
│   └── api/
│       ├── deps.py                   # FastAPI dependencies (SessionDep, Pagination, Filters)
│       └── v1/
│           ├── router.py             # APIRouter mounting Users and Products
│           └── endpoints/
│               ├── users.py          # User CRUD endpoints (POST, GET, PUT, DELETE)
│               └── products.py       # Product CRUD & search endpoints
│
├── scripts/
│   ├── seed_data.py                  # Database seeder populating sample users and products
│   └── run_demo.py                   # End-to-end automated demo script
│
└── tests/
    ├── conftest.py                   # Pytest fixtures with NullPool test isolation
    ├── test_pydantic_validators.py   # Unit tests for Field(), field_validator, model_validator
    ├── test_sqlalchemy_models.py     # Unit tests for DeclarativeBase, relationships, cascades
    ├── test_users_api.py             # Integration tests for User CRUD endpoints
    └── test_products_api.py          # Integration tests for Product catalog endpoints
```

---

## 🔍 Core Topic Deep Dive

### 1. FastAPI Setup & Project Structure
- **Lifespan Context Manager**: Uses `@asynccontextmanager async def lifespan(app: FastAPI)` to check PostgreSQL connectivity on startup and cleanly dispose connection pools on shutdown.
- **Path & Query Parameters**:
  - `Path(..., ge=1, description="...")` validates numerical boundaries on path identifiers.
  - `Query(...)` provides default pagination offsets, search terms, and category filters.
- **Typed Response Models**: Every endpoint explicitly declares `response_model=...` to ensure data contracts are strictly enforced, discarding internal attributes like hashed passwords.
- **Interactive Documentation**: Swagger UI available at `/docs`, ReDoc available at `/redoc`.

### 2. Pydantic V2 Deep Dive
- **`Field()` Validation**:
  - String constraints: `min_length=3`, `max_length=50`, `pattern=r"^[a-zA-Z0-9_]+$"`.
  - Numerical constraints: `gt=0`, `ge=0`.
- **Field Validators (`@field_validator`)**:
  - Normalization before regex parsing using `mode='before'`:
    ```python
    @field_validator("username", mode="before")
    @classmethod
    def normalize_username(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return v
    ```
- **Model Validators (`@model_validator(mode='after')`)**:
  - Multi-field cross-validation logic:
    ```python
    @model_validator(mode="after")
    def verify_password_match(self) -> "UserCreate":
        if self.password != self.confirm_password:
            raise ValueError("Password and confirmation password do not match")
        return self
    ```
  - Product promotional pricing constraint: `discount_price < price`.
- **Schema Separation**:
  - `UserBase` ➔ `UserCreate` (adds `password`, `confirm_password`)
  - `UserUpdate` (all fields optional for PATCH)
  - `UserResponse` (`model_config = ConfigDict(from_attributes=True)`)
  - `UserDetailResponse` (embeds nested `List[ProductSummary]`)

### 3. SQLAlchemy 2.0 (Modern Type-Safe Style)
- **Declarative Base**:
  ```python
  class Base(DeclarativeBase):
      pass
  ```
- **`Mapped[T]` and `mapped_column()` Descriptors**:
  ```python
  id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
  email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
  ```
- **Relationships & Cascading Deletes**:
  - One-to-Many (`User ➔ Product`):
    ```python
    products: Mapped[List["Product"]] = relationship(
        "Product", back_populates="owner", cascade="all, delete-orphan", lazy="selectin"
    )
    ```
  - Many-to-One (`Product ➔ User`):
    ```python
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    owner: Mapped["User"] = relationship("User", back_populates="products", lazy="selectin")
    ```
- **Async Execution**:
  - Asyncpg driver: `postgresql+asyncpg://...`
  - Modern statement syntax: `stmt = select(User).where(...); res = await session.execute(stmt)`

### 4. Alembic Migrations
- Asynchronous Alembic configuration in `alembic/env.py` utilizing `run_sync` over an async engine connection.
- Target metadata bound to `Base.metadata`.
- Initial revision: `alembic/versions/001_initial_users_and_products.py`.

---

## ⚡ API Endpoints Specification

### Users Router (`/api/v1/users`)

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/users` | Register a new user (with password hashing) | `201 Created` |
| `GET` | `/api/v1/users` | List users with pagination (`skip`, `limit`, `is_active`) | `200 OK` |
| `GET` | `/api/v1/users/{user_id}` | Get full user profile including owned products | `200 OK` |
| `PUT` | `/api/v1/users/{user_id}` | Update user information | `200 OK` |
| `DELETE` | `/api/v1/users/{user_id}` | Delete user (cascades to owned products) | `204 No Content` |
| `GET` | `/api/v1/users/{user_id}/products` | List all products owned by user | `200 OK` |

### Products Router (`/api/v1/products`)

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/products` | Create a catalog product linked to an owner | `201 Created` |
| `GET` | `/api/v1/products` | Filter & search products (`search`, `category`, `price`, `owner_id`) | `200 OK` |
| `GET` | `/api/v1/products/{product_id}` | Get product details with owner information | `200 OK` |
| `PUT` | `/api/v1/products/{product_id}` | Update product pricing, inventory, or description | `200 OK` |
| `DELETE` | `/api/v1/products/{product_id}` | Permanently delete product from catalog | `204 No Content` |

### System Router

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Application metadata and documentation links | `200 OK` |
| `GET` | `/health` | Diagnostic probe verifying PostgreSQL connectivity | `200 OK` |

---

## 🛠️ Step-by-Step Execution Guide

### 1. Database Migrations via Alembic
Apply the database migrations to build tables and indexes in PostgreSQL:
```powershell
python -m alembic upgrade head
```

### 2. Seed Initial Sample Data
Populate realistic users and catalog items:
```powershell
python scripts/seed_data.py
```

### 3. Run Automated End-to-End Demo
Execute the full live validation script verifying all components:
```powershell
python scripts/run_demo.py
```

### 4. Run Automated Test Suite (26 Tests)
Run unit and integration tests with pytest:
```powershell
python -m pytest tests -v
```

### 5. Launch the FastAPI Development Server
Start the live Uvicorn server:
```powershell
python run.py
```
Then visit:
- **Interactive Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check Endpoint**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
