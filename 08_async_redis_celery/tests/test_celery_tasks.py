import pytest


@pytest.mark.asyncio
async def test_dispatch_pdf_report_task(client):
    response = await client.post(
        "/api/v1/tasks/celery/report",
        json={"report_name": "Test_Report_Q1", "total_records": 50}
    )
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "QUEUED"
    assert "task_id" in data

    # Query status
    task_id = data["task_id"]
    status_res = await client.get(f"/api/v1/tasks/celery/{task_id}/status")
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert status_data["task_id"] == task_id
    assert status_data["ready"] is True
    assert status_data["state"] == "SUCCESS"
    assert status_data["result"]["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_dispatch_email_retry_task(client):
    response = await client.post(
        "/api/v1/tasks/celery/email-with-retry",
        json={"recipient": "dev@test.org", "subject": "Unit Test Email", "simulate_failure": False}
    )
    assert response.status_code == 202
    data = response.json()
    assert "task_id" in data
    assert data["retry_policy"]["max_retries"] == 3


@pytest.mark.asyncio
async def test_revoke_task(client):
    response = await client.post("/api/v1/tasks/celery/dummy-task-id-123/revoke")
    assert response.status_code == 200
    assert response.json()["action"] == "REVOKED"
