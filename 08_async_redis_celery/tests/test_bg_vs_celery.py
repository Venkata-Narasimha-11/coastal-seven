import pytest


@pytest.mark.asyncio
async def test_fastapi_background_tasks_execution(client):
    response = await client.post(
        "/api/v1/tasks/comparison/fastapi-bg",
        json={"action": "USER_SIGNUP", "resource_id": "USR-401"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ACCEPTED_IN_PROCESS"
    assert "FastAPI BackgroundTasks" in data["technology"]

    # Verify log entry in in-process buffer
    logs_res = await client.get("/api/v1/tasks/comparison/fastapi-bg/logs")
    assert logs_res.status_code == 200
    logs_data = logs_res.json()
    assert logs_data["total_in_process_logs"] >= 1
    latest = logs_data["recent_entries"][-1]
    assert latest["action"] == "USER_SIGNUP"
    assert latest["resource"] == "USR-401"


@pytest.mark.asyncio
async def test_celery_comparison_task(client):
    response = await client.post(
        "/api/v1/tasks/comparison/celery",
        json={"action": "PROCESS_BATCH", "resource_id": "BATCH-11"}
    )
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "QUEUED_OUT_OF_PROCESS"
    assert "Celery" in data["technology"]
    assert "task_id" in data


@pytest.mark.asyncio
async def test_comparison_matrix_endpoint(client):
    response = await client.get("/api/v1/tasks/comparison/matrix")
    assert response.status_code == 200
    data = response.json()
    assert "comparison_table" in data
    assert "decision_rule" in data
    assert len(data["comparison_table"]) >= 6
