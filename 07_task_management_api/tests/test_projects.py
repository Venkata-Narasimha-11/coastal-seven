"""Unit and integration tests for Project CRUD and membership endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_project_success(client: AsyncClient, auth_tokens):
    """Test project creation by manager."""
    payload = {
        "name": "E-Commerce Microservices",
        "description": "Decomposing monolith into distributed microservices",
        "status": "active",
    }
    response = await client.post("/api/v1/projects/", json=payload, headers=auth_tokens["manager"])
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["status"] == "active"
    assert data["owner"]["username"] == "manager_user"


@pytest.mark.asyncio
async def test_viewer_cannot_create_project(client: AsyncClient, auth_tokens):
    """Test that viewers receive 403 when attempting project creation."""
    payload = {"name": "Unauthorized Project"}
    response = await client.post("/api/v1/projects/", json=payload, headers=auth_tokens["viewer"])
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "PERMISSION_DENIED"


@pytest.mark.asyncio
async def test_list_projects_pagination_and_scoping(
    client: AsyncClient,
    auth_tokens,
    seed_project_and_tasks,
):
    """Test project listing with pagination envelope."""
    response = await client.get("/api/v1/projects/?page=1&limit=5", headers=auth_tokens["manager"])
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["page"] == 1
    assert data["limit"] == 5
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_get_project_detail_with_task_counts(
    client: AsyncClient,
    auth_tokens,
    seed_project_and_tasks,
):
    """Test project detail retrieval including task status counts and members."""
    project_id = seed_project_and_tasks["project"].id
    response = await client.get(f"/api/v1/projects/{project_id}", headers=auth_tokens["manager"])
    assert response.status_code == 200
    data = response.json()
    assert "task_counts" in data
    counts = data["task_counts"]
    assert counts["total"] == 4
    assert counts["todo"] == 1
    assert counts["in_progress"] == 1
    assert counts["review"] == 1
    assert counts["completed"] == 1
    assert len(data["members"]) >= 1


@pytest.mark.asyncio
async def test_update_project_by_owner(
    client: AsyncClient,
    auth_tokens,
    seed_project_and_tasks,
):
    """Test project updates permitted to project owner."""
    project_id = seed_project_and_tasks["project"].id
    payload = {"name": "Updated Core Project Name", "status": "completed"}
    response = await client.put(
        f"/api/v1/projects/{project_id}",
        json=payload,
        headers=auth_tokens["manager"],
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Core Project Name"
    assert response.json()["status"] == "completed"


@pytest.mark.asyncio
async def test_add_project_member(
    client: AsyncClient,
    auth_tokens,
    seed_project_and_tasks,
    seed_users,
):
    """Test adding new member to project."""
    project_id = seed_project_and_tasks["project"].id
    new_user_id = seed_users["developer2"].id
    payload = {"user_id": new_user_id, "role": "contributor"}
    response = await client.post(
        f"/api/v1/projects/{project_id}/members",
        json=payload,
        headers=auth_tokens["manager"],
    )
    assert response.status_code == 201
    assert response.json()["user_id"] == new_user_id
    assert response.json()["role"] == "contributor"


@pytest.mark.asyncio
async def test_delete_project(
    client: AsyncClient,
    auth_tokens,
    seed_project_and_tasks,
):
    """Test project deletion (204 No Content) and subsequent 404."""
    project_id = seed_project_and_tasks["project"].id
    del_res = await client.delete(
        f"/api/v1/projects/{project_id}",
        headers=auth_tokens["manager"],
    )
    assert del_res.status_code == 204

    # Verify not found
    get_res = await client.get(
        f"/api/v1/projects/{project_id}",
        headers=auth_tokens["manager"],
    )
    assert get_res.status_code == 404
