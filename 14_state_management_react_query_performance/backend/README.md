# Production-Ready Modular E-Commerce Backend (FastAPI)

An enterprise-grade, modular e-commerce backend built with **FastAPI**, **SQLAlchemy 2.0**, **PostgreSQL** (with **SQLite fallback**), **Redis** (for temporary carts & catalog caching), **Celery** (for asynchronous email notifications), **WebSockets** (for real-time order tracking), and **Pytest** (**34 automated tests**).

---

## 📁 Project Folder Structure

```
ecommerce-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point & lifespan setup
│   ├── config.py            # Pydantic Settings V2 configuration & env vars
│   ├── database.py          # SQLAlchemy 2.0 engine, SessionLocal & get_db dependency
│   ├── models/              # Database ORM Tables
│   │   ├── __init__.py
│   │   ├── user.py          # User entity with UserRole (customer / admin)
│   │   ├── product.py       # Category & Product models with CheckConstraints
│   │   └── order.py         # Order & OrderItem entities with OrderStatus
│   ├── schemas/             # Pydantic V2 Schemas (Request/Response Validation)
│   │   ├── __init__.py
│   │   ├── user.py          # UserCreate, UserLogin, UserResponse, Token
│   │   ├── product.py       # ProductCreate, ProductUpdate, ProductResponse, Category
│   │   ├── cart.py          # AddToCartSchema, UpdateCartItem, CartResponse
│   │   └── order.py         # OrderCreate, OrderStatusUpdate, OrderResponse
│   ├── routers/             # API Endpoints
│   │   ├── __init__.py
│   │   ├── auth.py          # /register, /login, /me, /me (update)
│   │   ├── products.py      # Product CRUD, category CRUD, image upload, caching
│   │   ├── cart.py          # Redis cart operations: view, add, update, remove, clear
│   │   ├── orders.py        # Atomic checkout, stock decrement, order history
│   │   └── websocket.py     # Real-time WebSocket order tracking (/ws/orders/{id})
│   ├── services/            # Redis, Celery & Helper Services
│   │   ├── __init__.py
│   │   ├── redis_service.py # Redis CartService (Hashes) & CacheService (Cache-Aside)
│   │   └── celery_app.py    # Background order confirmation email worker
│   └── utils/
│       ├── __init__.py
│       └── auth.py          # Password hashing (bcrypt), JWT creation & OAuth2 deps
├── tests/                   # Pytest Automated Test Suite (34 Passed Tests)
│   ├── __init__.py
│   ├── conftest.py          # Test fixtures (isolated SQLite DB, FakeRedis, TestClient)
│   ├── test_auth.py         # Registration, duplicate validation, login, profile (10 tests)
│   ├── test_products.py     # Categories, product catalog CRUD, caching (10 tests)
│   ├── test_cart.py         # Redis shopping cart operations & inventory limits (7 tests)
│   └── test_orders.py       # Atomic checkout, stock decrement, WS tracking (7 tests)
├── .env                     # Local environment variables
├── .env.example             # Template environment variables
├── requirements.txt         # Production dependencies
└── README.md                # Project documentation
```

---

## 🚀 Key Architectural Features

1. **JWT Authentication & RBAC**:
   - Secure password hashing using `passlib[bcrypt]`.
   - Signed JSON Web Tokens (HS256) with expiration handling.
   - Role-Based Access Control (`admin` vs `customer`).

2. **Redis Cart System**:
   - Temporary shopping cart stored in Redis Hashes (`cart:{user_id}`).
   - Fast subtotal calculations, dynamic quantity modification, and TTL expiration.

3. **Atomic Stock Decrement & Checkout**:
   - Order checkout executes in a single database transaction.
   - Validates that every line item has sufficient inventory before committing.
   - Decrements stock atomically and rolls back completely on any shortage, preventing overselling.

4. **Redis Product Caching**:
   - Cache-Aside (Lazy Loading) pattern applied to product listing and detail endpoints.
   - Automatic cache invalidation upon product creation, update, deletion, or stock checkout.
   - Transparent in-memory fallback (`FakeRedis`) if Redis is offline locally.

5. **Asynchronous Celery Order Confirmation**:
   - Decoupled worker dispatches customer email receipts without blocking HTTP response latency.
   - Automatic eager fallback when running tests or in lightweight local development.

6. **Real-Time WebSocket Order Tracking**:
   - Full-duplex WebSocket channel at `/ws/orders/{order_id}`.
   - `ConnectionManager` broadcasts live lifecycle transitions (`PENDING` -> `CONFIRMED` -> `SHIPPED` -> `DELIVERED`).

---

## 🛠️ Setup & Running

### 1. Prerequisites & Virtual Environment

```bash
# Clone or navigate to the directory
cd ecommerce-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment (`.env`)

Copy `.env.example` to `.env` or use default local development settings:

```env
PROJECT_NAME="Modular E-Commerce Backend"
ENVIRONMENT="development"
DEBUG=True
API_V1_STR="/api/v1"

# Database Configuration
USE_SQLITE_FALLBACK=True
SQLITE_DB_PATH="ecommerce.db"

# Redis
REDIS_URL="redis://localhost:6379/0"

# Celery
CELERY_BROKER_URL="redis://localhost:6379/1"
CELERY_RESULT_BACKEND="redis://localhost:6379/2"

# Security
SECRET_KEY="ecommerce-secret-key-production-grade-at-least-32-chars-long"
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 3. Start FastAPI Server

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- **Interactive Swagger Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative ReDoc UI**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### 4. Run Celery Worker (Optional for background processing)

```bash
# Windows solo pool:
celery -A app.services.celery_app.celery_app worker --loglevel=info -P solo

# Linux/macOS prefork:
celery -A app.services.celery_app.celery_app worker --loglevel=info
```

---

## 🧪 Automated Testing

Run the comprehensive Pytest suite containing **34 automated tests**:

```bash
python -m pytest -v
```

### Test Suite Summary:
- [`tests/test_auth.py`](tests/test_auth.py): 10 tests (Registration, uniqueness, invalid passwords, login, JWT decode, current user, profile updates).
- [`tests/test_products.py`](tests/test_products.py): 10 tests (Category creation, RBAC protections, product catalog CRUD, image uploads, pagination, and caching).
- [`tests/test_cart.py`](tests/test_cart.py): 7 tests (Adding items, stock limit validation, quantity updates, removal, view cart calculations, clearing cart).
- [`tests/test_orders.py`](tests/test_orders.py): 7 tests (Empty cart protection, atomic stock decrement, overselling rollback, order history, owner access checks, admin status transitions, and WebSocket order tracking).

---

## 📡 API Endpoint Reference

| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Register a new user | Public |
| `POST` | `/api/v1/auth/login` | Authenticate and obtain JWT Bearer token | Public |
| `GET` | `/api/v1/auth/me` | Get profile of logged in user | Authenticated |
| `PUT` | `/api/v1/auth/me` | Update profile information | Authenticated |
| `GET` | `/api/v1/products/categories` | List all product categories (Cached) | Public |
| `POST` | `/api/v1/products/categories` | Create a category | Admin |
| `GET` | `/api/v1/products` | Paginated product listing with search/filter (Cached) | Public |
| `GET` | `/api/v1/products/{id}` | Get product details (Cached) | Public |
| `POST` | `/api/v1/products` | Create a new product | Admin |
| `PUT` | `/api/v1/products/{id}` | Update product & invalidate cache | Admin |
| `DELETE` | `/api/v1/products/{id}` | Delete product & invalidate cache | Admin |
| `POST` | `/api/v1/products/{id}/upload-image` | Upload image & generate thumbnail | Admin |
| `GET` | `/api/v1/cart` | View current shopping cart | Authenticated |
| `POST` | `/api/v1/cart/items` | Add product to cart with inventory check | Authenticated |
| `PUT` | `/api/v1/cart/items/{product_id}` | Update cart quantity | Authenticated |
| `DELETE` | `/api/v1/cart/items/{product_id}` | Remove line item from cart | Authenticated |
| `DELETE` | `/api/v1/cart` | Clear entire shopping cart | Authenticated |
| `POST` | `/api/v1/orders/checkout` | Atomic checkout with stock decrement & Celery email | Authenticated |
| `GET` | `/api/v1/orders` | View user order history | Authenticated |
| `GET` | `/api/v1/orders/{order_id}` | View detailed order information | Owner / Admin |
| `PUT` | `/api/v1/orders/{order_id}/status` | Update status & broadcast via WebSocket | Admin |
| `WS` | `/ws/orders/{order_id}` | Live WebSocket order tracking channel | Public / Client |
