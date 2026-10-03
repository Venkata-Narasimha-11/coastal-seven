import pytest
import time


@pytest.mark.asyncio
async def test_async_concepts_endpoint(client):
    response = await client.get("/api/v1/async/concepts")
    assert response.status_code == 200
    data = response.json()
    assert "event_loop" in data
    assert "async_def_vs_def" in data
    assert "concurrency_primitive" in data


@pytest.mark.asyncio
async def test_sequential_vs_concurrent_gather(client):
    # Concurrent call
    t_start = time.perf_counter()
    conc_res = await client.get("/api/v1/async/concurrent?city=Paris&currency=USD&stock=MSFT")
    conc_time = time.perf_counter() - t_start

    assert conc_res.status_code == 200
    data = conc_res.json()
    assert data["mode"] == "concurrent (asyncio.gather)"
    assert "results" in data
    assert data["results"]["weather"]["city"] == "Paris"
    assert data["results"]["currency"]["base"] == "USD"
    assert data["results"]["stock"]["symbol"] == "MSFT"


@pytest.mark.asyncio
async def test_gather_error_handling(client):
    response = await client.get("/api/v1/async/gather-error-handling?simulate_error=true")
    assert response.status_code == 200
    data = response.json()
    assert data["strategy"] == "asyncio.gather(..., return_exceptions=True)"
    results = data["results"]
    assert len(results) == 3
    # Check that error was captured without blowing up the request
    assert results[0]["status"] == "OK"
    assert results[1]["status"] == "ERROR"
    assert results[2]["status"] == "OK"
