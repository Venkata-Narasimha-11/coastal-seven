"""Unit and integration tests for Task Filtering, Search, Sorting, and Pagination."""

from datetime import datetime, timedelta, timezone
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_filter_by_status(
    client: AsyncClient,
    auth_tokens,
    seed_project_and_tasks,
):
    """Test filtering tasks by status."""
    response = await client.get("/api/v1/tasks/?status=in_progress", headers=auth_tokens["manager"])
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["status"] == "in_progress"


@pytest.mark.asyncio
async def test_filter_by_priority(
    client: AsyncClient,
    auth_tokens,
    seed_project_and_tasks,
):
    """Test filtering tasks by priority."""
    response = await client.get("/api/v1/tasks/?priority=urgent", headers=auth_tokens["manager"])
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["priority"] == "urgent"


@pytest.mark.asyncio
async def test_filter_by_assignee(
    client: AsyncClient,
    auth_tokens,
    seed_project_and_tasks,
    seed_users,
):
    """Test filtering tasks by assignee ID."""
    dev_id = seed_users["developer"].id
    response = await client.get(f"/api/v1/tasks/?assignee_id={dev_id}", headers=auth_tokens["manager"])
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 4


@pytest.mark.asyncio
async def test_filter_by_search_keyword(
    client: AsyncClient,
    auth_tokens,
    seed_project_and_tasks,
):
    """Test full-text search across task title and description."""
    response = await client.get("/api/v1/tasks/?search=Swagger", headers=auth_tokens["manager"])
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert "Swagger" in data["items"][0]["title"]


@pytest.mark.asyncio
async def test_filter_by_due_date_range(
    client: AsyncClient,
    auth_tokens,
    seed_project_and_tasks,
):
    """Test filtering tasks by due date before a threshold."""
    threshold = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    response = await client.get(
        "/api/v1/tasks/",
        params={"due_date_before": threshold},
        headers=auth_tokens["manager"],
    )
    assert response.status_code == 200
    data = response.json()
    # CI/CD (2 days) and Swagger (-1 day) are <= 3 days
    assert data["total"] >= 2


@pytest.mark.asyncio
async def test_pagination_envelope_structure(
    client: AsyncClient,
    auth_tokens,
    seed_project_and_tasks,
):
    """Test pagination envelope metadata: page, limit, total, total_pages, has_next, has_prev."""
    response = await client.get("/api/v1/tasks/?page=1&limit=2", headers=auth_tokens["manager"])
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["limit"] == 2
    assert data["total"] == 4
    assert data["total_pages"] == 2
    assert data["has_next"] is True
    assert data["has_prev"] is False
    assert len(data["items"]) == 2
