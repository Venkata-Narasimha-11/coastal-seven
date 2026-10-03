import pytest


@pytest.mark.asyncio
async def test_integrated_dashboard_flow(client):
    # Call 1: Cache Miss -> invokes concurrent gather, sets cache, triggers bg tasks
    res1 = await client.get("/api/v1/integrated/dashboard/user_99")
    assert res1.status_code == 200
    d1 = res1.json()
    assert d1["status"] == "SUCCESS"
    
    perf1 = d1["performance_and_architecture"]
    assert perf1["cache"]["hit"] is False
    assert "rate_limiting" in perf1
    assert "celery_distributed_task" in perf1["background_processing"]
    
    data1 = d1["data"]
    assert data1["profile"]["user_id"] == "user_99"
    assert "weather" in data1["widgets"]
    assert "currency_market" in data1["widgets"]
    assert "portfolio" in data1["widgets"]

    # Call 2: Cache Hit -> returns instant response from Redis
    res2 = await client.get("/api/v1/integrated/dashboard/user_99")
    assert res2.status_code == 200
    d2 = res2.json()
    perf2 = d2["performance_and_architecture"]
    assert perf2["cache"]["hit"] is True

    # Call Refresh: Invalidate Cache
    ref_res = await client.post("/api/v1/integrated/dashboard/user_99/refresh")
    assert ref_res.status_code == 200
    assert ref_res.json()["invalidated"] is True

    # Call 3: Fresh Cache Miss after invalidation
    res3 = await client.get("/api/v1/integrated/dashboard/user_99")
    assert res3.status_code == 200
    assert res3.json()["performance_and_architecture"]["cache"]["hit"] is False
