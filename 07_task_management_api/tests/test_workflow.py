"""Unit and integration tests for Task Status Workflow and State Machine enforcement."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_valid_workflow_progression(
    client: AsyncClient,
    auth_tokens,
    seed_project_and_tasks,
):
    """Test standard progression: TODO -> IN_PROGRESS -> REVIEW -> COMPLETED."""
    task_id = seed_project_and_tasks["tasks"][0].id  # Task starts in TODO

    # 1. TODO -> IN_PROGRESS
    r1 = await client.patch(
        f"/api/v1/tasks/{task_id}/status",
        json={"status": "in_progress", "notes": "Starting work"},
        headers=auth_tokens["developer"],
    )
    assert r1.status_code == 200
    assert r1.json()["status"] == "in_progress"

    # 2. IN_PROGRESS -> REVIEW
    r2 = await client.patch(
        f"/api/v1/tasks/{task_id}/status",
        json={"status": "review", "notes": "PR submitted"},
        headers=auth_tokens["developer"],
    )
    assert r2.status_code == 200
    assert r2.json()["status"] == "review"

    # 3. REVIEW -> COMPLETED by Manager
    r3 = await client.patch(
        f"/api/v1/tasks/{task_id}/status",
        json={"status": "completed", "notes": "Approved and merged"},
        headers=auth_tokens["manager"],
    )
    assert r3.status_code == 200
    assert r3.json()["status"] == "completed"


@pytest.mark.asyncio
async def test_invalid_skip_transition_rejected(
    client: AsyncClient,
    auth_tokens,
    seed_project_and_tasks,
):
    """Test that skipping workflow steps (TODO directly to COMPLETED) fails with 400."""
    task_id = seed_project_and_tasks["tasks"][0].id  # Status is TODO

    response = await client.patch(
        f"/api/v1/tasks/{task_id}/status",
        json={"status": "completed", "notes": "Skipping directly to completed"},
        headers=auth_tokens["manager"],
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "INVALID_STATUS_TRANSITION"
    assert "Cannot transition task from 'todo' to 'completed'" in data["error"]["message"]


@pytest.mark.asyncio
async def test_non_manager_cannot_reopen_completed_task(
    client: AsyncClient,
    auth_tokens,
    seed_project_and_tasks,
):
    """Test that regular developer cannot reopen completed task."""
    completed_task_id = seed_project_and_tasks["tasks"][3].id  # Status is COMPLETED

    response = await client.patch(
        f"/api/v1/tasks/{completed_task_id}/status",
        json={"status": "in_progress", "notes": "Attempting reopen"},
        headers=auth_tokens["developer"],
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "PERMISSION_DENIED"


@pytest.mark.asyncio
async def test_manager_can_reopen_completed_task(
    client: AsyncClient,
    auth_tokens,
    seed_project_and_tasks,
):
    """Test that Project Manager can reopen completed task."""
    completed_task_id = seed_project_and_tasks["tasks"][3].id  # Status is COMPLETED

    response = await client.patch(
        f"/api/v1/tasks/{completed_task_id}/status",
        json={"status": "in_progress", "notes": "Reopened by manager for adjustments"},
        headers=auth_tokens["manager"],
    )
    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


@pytest.mark.asyncio
async def test_audit_history_trail(
    client: AsyncClient,
    auth_tokens,
    seed_project_and_tasks,
):
    """Test that task transitions write audit entries retrievable via /history."""
    task_id = seed_project_and_tasks["tasks"][0].id

    # Make two transitions
    await client.patch(
        f"/api/v1/tasks/{task_id}/status",
        json={"status": "in_progress", "notes": "Transition 1"},
        headers=auth_tokens["developer"],
    )
    await client.patch(
        f"/api/v1/tasks/{task_id}/status",
        json={"status": "review", "notes": "Transition 2"},
        headers=auth_tokens["developer"],
    )

    history_res = await client.get(
        f"/api/v1/tasks/{task_id}/history",
        headers=auth_tokens["manager"],
    )
    assert history_res.status_code == 200
    logs = history_res.json()
    assert len(logs) >= 2
    # Verify newest first
    assert logs[0]["new_status"] == "review"
    assert logs[0]["old_status"] == "in_progress"


@pytest.mark.asyncio
async def test_task_assignment_endpoint(
    client: AsyncClient,
    auth_tokens,
    seed_project_and_tasks,
    seed_users,
):
    """Test task assignment endpoint with audit entry."""
    task_id = seed_project_and_tasks["tasks"][0].id
    new_dev_id = seed_users["developer2"].id

    assign_res = await client.patch(
        f"/api/v1/tasks/{task_id}/assign",
        json={"assignee_id": new_dev_id, "notes": "Reassigned to secondary developer"},
        headers=auth_tokens["manager"],
    )
    assert assign_res.status_code == 200
    assert assign_res.json()["assignee"]["id"] == new_dev_id
