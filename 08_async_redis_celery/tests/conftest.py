import pytest
import pytest_asyncio
import fakeredis.aioredis
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.redis_client import get_redis
from app.celery_app import celery_app


@pytest.fixture(autouse=True)
def configure_celery_eager():
    """Ensure Celery executes tasks synchronously in-process with memory broker/backend during tests."""
    orig_broker = celery_app.conf.broker_url
    orig_backend = celery_app.conf.result_backend
    orig_eager = celery_app.conf.task_always_eager
    orig_store = getattr(celery_app.conf, "task_store_eager_result", False)

    celery_app.conf.broker_url = "memory://"
    celery_app.conf.result_backend = "cache+memory://"
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
    celery_app.conf.task_store_eager_result = True
    yield
    celery_app.conf.broker_url = orig_broker
    celery_app.conf.result_backend = orig_backend
    celery_app.conf.task_always_eager = orig_eager
    celery_app.conf.task_store_eager_result = orig_store




@pytest_asyncio.fixture
async def fake_redis():
    """Provides an isolated in-memory FakeRedis instance for tests."""
    client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield client
    await client.flushall()
    if hasattr(client, "aclose"):
        await client.aclose()
    else:
        await client.close()



@pytest_asyncio.fixture
async def client(fake_redis):
    """Provides test AsyncClient with overridden Redis dependency."""
    app.dependency_overrides[get_redis] = lambda: fake_redis
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
