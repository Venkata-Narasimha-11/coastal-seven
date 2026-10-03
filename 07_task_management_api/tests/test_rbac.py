"""Unit and integration tests for Role-Based Access Control (RBAC)."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_admin_has_unrestricted_access(
    client: AsyncClient,
    auth_tokens,
    seed_project_and_tasks,
):
    """Test that Admin can delete any task regardless of ownership."""
    task_id = seed_project_and_tasks["tasks"][0].id
    response = await client.delete(f"/api/v1/tasks/{task_id}", headers=auth_tokens["admin"])
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_viewer_is_strictly_read_only(
    client: AsyncClient,
    auth_tokens,
    seed_project_and_tasks,
):
    """Test that Viewer is rejected on all write and transition operations."""
    task_id = seed_project_and_tasks["tasks"][0].id
    project_id = seed_project_and_tasks["project"].id

    # 1. Attempt task creation
    r_create = await client.post(
        "/api/v1/tasks/",
        json={"title": "Viewer Task", "project_id": project_id},
        headers=auth_tokens["viewer"],
    )
    assert r_create.status_code == 403

    # 2. Attempt status update
    r_status = await client.patch(
        f"/api/v1/tasks/{task_id}/status",
        json={"status": "in_progress"},
        headers=auth_tokens["viewer"],
    )
    assert r_status.status_code == 403

    # 3. Attempt task deletion
    r_delete = await client.delete(
        f"/api/v1/tasks/{task_id}",
        headers=auth_tokens["viewer"],
    )
    assert r_delete.status_code == 403


@pytest.mark.asyncio
async def test_developer_cannot_reassign_arbitrary_tasks(
    client: AsyncClient,
    auth_tokens,
    seed_project_and_tasks,
    seed_users,
):
    """Test that developers cannot reassign tasks (requires manager/owner/admin)."""
    task_id = seed_project_and_tasks["tasks"][0].id
    new_user_id = seed_users["developer2"].id

    response = await client.patch(
        f"/api/v1/tasks/{task_id}/assign",
        json={"assignee_id": new_user_id},
        headers=auth_tokens["developer"],
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "PERMISSION_DENIED"


@pytest.mark.asyncio
async def test_developer_can_update_own_assigned_task(
    client: AsyncClient,
    auth_tokens,
    seed_project_and_tasks,
):
    """Test that developer can update status for a task assigned to them."""
    task_id = seed_project_and_tasks["tasks"][0].id  # Assigned to developer_user
    response = await client.patch(
        f"/api/v1/tasks/{task_id}/status",
        json={"status": "in_progress"},
        headers=auth_tokens["developer"],
    )
    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"
