"""Unit and integration tests for Task CRUD operations."""

from datetime import datetime, timedelta, timezone
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_task_success(
    client: AsyncClient,
    auth_tokens,
    seed_project_and_tasks,
    seed_users,
):
    """Test task creation with initial status and audit trail."""
    project_id = seed_project_and_tasks["project"].id
    dev_id = seed_users["developer"].id
    payload = {
        "title": "Build Docker Multi-Stage Image",
        "description": "Optimize Dockerfile size with slim debian base",
        "project_id": project_id,
        "priority": "high",
        "due_date": (datetime.now(timezone.utc) + timedelta(days=3)).isoformat(),
        "assignee_id": dev_id,
    }
    response = await client.post("/api/v1/tasks/", json=payload, headers=auth_tokens["manager"])
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["status"] == "todo"
    assert data["priority"] == "high"
    assert data["assignee"]["id"] == dev_id


@pytest.mark.asyncio
async def test_get_task_details(
    client: AsyncClient,
    auth_tokens,
    seed_project_and_tasks,
):
    """Test fetching task details with allowed transitions."""
    task_id = seed_project_and_tasks["tasks"][0].id
    response = await client.get(f"/api/v1/tasks/{task_id}", headers=auth_tokens["manager"])
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert "allowed_transitions" in data
    assert "in_progress" in data["allowed_transitions"]


@pytest.mark.asyncio
async def test_update_task_put(
    client: AsyncClient,
    auth_tokens,
    seed_project_and_tasks,
):
    """Test full update of task attributes via PUT."""
    task_id = seed_project_and_tasks["tasks"][0].id
    payload = {
        "title": "Completely Overhauled Task Title",
        "description": "Updated description",
        "priority": "urgent",
        "due_date": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
    }
    response = await client.put(f"/api/v1/tasks/{task_id}", json=payload, headers=auth_tokens["manager"])
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["priority"] == "urgent"


@pytest.mark.asyncio
async def test_patch_task(
    client: AsyncClient,
    auth_tokens,
    seed_project_and_tasks,
):
    """Test partial update of task attributes via PATCH."""
    task_id = seed_project_and_tasks["tasks"][0].id
    response = await client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"priority": "low"},
        headers=auth_tokens["manager"],
    )
    assert response.status_code == 200
    assert response.json()["priority"] == "low"


@pytest.mark.asyncio
async def test_delete_task(
    client: AsyncClient,
    auth_tokens,
    seed_project_and_tasks,
):
    """Test task deletion."""
    task_id = seed_project_and_tasks["tasks"][0].id
    del_res = await client.delete(f"/api/v1/tasks/{task_id}", headers=auth_tokens["manager"])
    assert del_res.status_code == 204

    get_res = await client.get(f"/api/v1/tasks/{task_id}", headers=auth_tokens["manager"])
    assert get_res.status_code == 404
