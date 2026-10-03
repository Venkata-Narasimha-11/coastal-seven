import pytest


@pytest.mark.asyncio
async def test_cache_aside_flow_and_hit(client):
    # First Request -> Cache Miss
    res1 = await client.get("/api/v1/cache/products/101")
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["cache_hit"] is False
    assert data1["data"]["id"] == 101
    assert "Simulated Database" in data1["source"]

    # Second Request -> Cache Hit
    res2 = await client.get("/api/v1/cache/products/101")
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["cache_hit"] is True
    assert data2["source"] == "Redis Cache"
    assert data2["data"]["name"] == data1["data"]["name"]


@pytest.mark.asyncio
async def test_cache_invalidation_on_update(client):
    # Ensure cached
    await client.get("/api/v1/cache/products/102")
    cached_check = await client.get("/api/v1/cache/products/102")
    assert cached_check.json()["cache_hit"] is True

    # Mutate product -> invalidates cache
    update_res = await client.put(
        "/api/v1/cache/products/102",
        json={"price": 549.99}
    )
    assert update_res.status_code == 200
    assert update_res.json()["cache_invalidated"] is True

    # Next fetch must be a Cache Miss loading fresh mutated price
    fresh_res = await client.get("/api/v1/cache/products/102")
    assert fresh_res.status_code == 200
    fresh_data = fresh_res.json()
    assert fresh_data["cache_hit"] is False
    assert fresh_data["data"]["price"] == 549.99


@pytest.mark.asyncio
async def test_cache_invalidation_on_delete(client):
    # Ensure cached
    await client.get("/api/v1/cache/products/103")
    
    # Delete product
    del_res = await client.delete("/api/v1/cache/products/103")
    assert del_res.status_code == 200
    assert del_res.json()["cache_invalidated"] is True

    # Next fetch returns 404
    missing_res = await client.get("/api/v1/cache/products/103")
    assert missing_res.status_code == 404


@pytest.mark.asyncio
async def test_cache_purge_all(client):
    await client.get("/api/v1/cache/products/101")
    purge_res = await client.post("/api/v1/cache/purge-all")
    assert purge_res.status_code == 200
    assert purge_res.json()["keys_cleared"] >= 1
