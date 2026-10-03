"""Pytest configuration and async test fixtures for Day 7."""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import AsyncGenerator
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.deps import get_async_db
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.core.workflow import TaskPriority, TaskStatus
from app.db.base import Base
from app.main import app
from app.models.project import Project, ProjectMember, ProjectMemberRole, ProjectStatus
from app.models.task import Task
from app.models.user import User, UserRole

# Use SQLite in-memory for isolated, fast, clean tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_async_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    future=True,
)

TestingSessionLocal = async_sessionmaker(
    bind=test_async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create session-scoped event loop."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def prepare_database():
    """Setup clean tables before each test and teardown after."""
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency override injecting test SQLite session."""
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


app.dependency_overrides[get_async_db] = override_get_async_db


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session fixture for test data setup."""
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client fixture communicating with FastAPI application."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest.fixture
async def seed_users(db_session: AsyncSession):
    """Seed test users across all roles."""
    users = {
        "admin": User(
            username="admin_user",
            email="admin@test.io",
            hashed_password=get_password_hash("Password123!"),
            full_name="Admin User",
            role=UserRole.ADMIN,
            is_active=True,
        ),
        "manager": User(
            username="manager_user",
            email="manager@test.io",
            hashed_password=get_password_hash("Password123!"),
            full_name="Manager User",
            role=UserRole.MANAGER,
            is_active=True,
        ),
        "developer": User(
            username="developer_user",
            email="developer@test.io",
            hashed_password=get_password_hash("Password123!"),
            full_name="Developer User",
            role=UserRole.DEVELOPER,
            is_active=True,
        ),
        "developer2": User(
            username="developer2_user",
            email="developer2@test.io",
            hashed_password=get_password_hash("Password123!"),
            full_name="Developer Two",
            role=UserRole.DEVELOPER,
            is_active=True,
        ),
        "viewer": User(
            username="viewer_user",
            email="viewer@test.io",
            hashed_password=get_password_hash("Password123!"),
            full_name="Viewer User",
            role=UserRole.VIEWER,
            is_active=True,
        ),
    }
    for u in users.values():
        db_session.add(u)
    await db_session.commit()
    for u in users.values():
        await db_session.refresh(u)
    return users


@pytest.fixture
def auth_tokens(seed_users):
    """Generate authorization headers for seeded users."""
    headers = {}
    for role_name, user in seed_users.items():
        token = create_access_token(subject=user.username, role=user.role.value)
        headers[role_name] = {"Authorization": f"Bearer {token}"}
    return headers


@pytest.fixture
async def seed_project_and_tasks(db_session: AsyncSession, seed_users):
    """Create a project and multiple tasks with varying priorities and statuses."""
    now = datetime.now(timezone.utc)
    project = Project(
        name="Test Core Project",
        description="Core project for automated test suite",
        status=ProjectStatus.ACTIVE,
        owner_id=seed_users["manager"].id,
    )
    db_session.add(project)
    await db_session.flush()

    # Add developer as contributor member
    member = ProjectMember(
        project_id=project.id,
        user_id=seed_users["developer"].id,
        role=ProjectMemberRole.CONTRIBUTOR,
    )
    db_session.add(member)

    tasks = [
        Task(
            title="Setup CI/CD Pipeline",
            description="GitHub actions deployment workflow",
            status=TaskStatus.TODO,
            priority=TaskPriority.HIGH,
            due_date=now + timedelta(days=2),
            project_id=project.id,
            assignee_id=seed_users["developer"].id,
            creator_id=seed_users["manager"].id,
        ),
        Task(
            title="Implement User Auth Flow",
            description="JWT token validation logic",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.URGENT,
            due_date=now + timedelta(days=4),
            project_id=project.id,
            assignee_id=seed_users["developer"].id,
            creator_id=seed_users["manager"].id,
        ),
        Task(
            title="Database Schema Migration",
            description="Write Alembic migration scripts",
            status=TaskStatus.REVIEW,
            priority=TaskPriority.MEDIUM,
            due_date=now + timedelta(days=7),
            project_id=project.id,
            assignee_id=seed_users["developer"].id,
            creator_id=seed_users["manager"].id,
        ),
        Task(
            title="Write OpenAPI Swagger Docs",
            description="Document all endpoints and responses",
            status=TaskStatus.COMPLETED,
            priority=TaskPriority.LOW,
            due_date=now - timedelta(days=1),
            project_id=project.id,
            assignee_id=seed_users["developer"].id,
            creator_id=seed_users["manager"].id,
        ),
    ]
    for t in tasks:
        db_session.add(t)
    await db_session.commit()
    await db_session.refresh(project)
    for t in tasks:
        await db_session.refresh(t)

    return {"project": project, "tasks": tasks}
