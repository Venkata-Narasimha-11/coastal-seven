"""Pytest fixtures for database, test client, isolated Redis mock, and authentication headers."""

import fakeredis
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app
from app.models.order import Order, OrderItem
from app.models.product import Category, Product
from app.models.user import User, UserRole
from app.services import redis_service
from app.services.celery_app import celery_app
from app.utils.auth import create_access_token, get_password_hash

# Ensure Celery runs tasks eagerly during tests
celery_app.conf.update(task_always_eager=True, task_eager_propagates=True)

# In-memory SQLite engine for fast, isolated test execution
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Ensure database engine is initialized."""
    yield
    test_engine.dispose()


@pytest.fixture
def db():
    """Yield a fresh isolated database session per test."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(autouse=True)
def mock_redis():
    """Provide an isolated, fresh in-memory FakeRedis instance per test."""
    fake = fakeredis.FakeRedis(decode_responses=True)
    orig_client = redis_service.redis_client
    redis_service.redis_client = fake
    yield fake
    fake.flushall()
    redis_service.redis_client = orig_client


@pytest.fixture
def client(db):
    """FastAPI TestClient with overridden get_db dependency."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def customer_user(db) -> User:
    """Create a standard customer user."""
    user = User(
        email="customer@example.com",
        username="customer1",
        full_name="John Customer",
        hashed_password=get_password_hash("SecretPassword123!"),
        role=UserRole.CUSTOMER,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_user(db) -> User:
    """Create an administrator user."""
    admin = User(
        email="admin@example.com",
        username="admin1",
        full_name="Alice Admin",
        hashed_password=get_password_hash("AdminPassword123!"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture
def customer_token_headers(customer_user: User) -> dict:
    """Authorization headers for the standard customer."""
    token = create_access_token(data={"sub": customer_user.username, "role": customer_user.role.value})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_token_headers(admin_user: User) -> dict:
    """Authorization headers for the administrator."""
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role.value})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_category(db) -> Category:
    """Create a sample product category."""
    category = Category(
        name="Electronics",
        slug="electronics",
        description="Gadgets, laptops, and smart devices",
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@pytest.fixture
def sample_product(db, sample_category: Category) -> Product:
    """Create a sample product with 10 units in stock."""
    product = Product(
        name="Wireless Noise-Cancelling Headphones",
        slug="wireless-noise-cancelling-headphones-001",
        description="Premium over-ear headphones with 30-hour battery life",
        price=199.99,
        stock=10,
        category_id=sample_category.id,
        is_active=True,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
