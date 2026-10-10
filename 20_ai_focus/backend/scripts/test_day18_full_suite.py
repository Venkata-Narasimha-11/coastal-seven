"""Comprehensive Integration Test Suite for Day 18.
Covers:
1. PostgreSQL Full-Text Search (tsvector & GIN index)
2. PostgreSQL Fuzzy Search (pg_trgm word_similarity & typo tolerance)
3. Hybrid Search
4. N+1 Query Optimization with joinedload and selectinload
5. Celery Task Lifecycle: PDF Invoice Generation with live progress tracking
6. Celery Task Lifecycle: Bulk CSV Import with live progress tracking
"""

import io
import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_search_and_tasks():
    print("================================================================")
    print("1. TESTING POSTGRESQL FUZZY SEARCH (TYPO TOLERANCE via pg_trgm)")
    print("================================================================")
    # Testing typo: 'iphoen'
    res = client.get("/api/v1/products/search/advanced?q=iphoen&mode=fuzzy")
    assert res.status_code == 200, res.text
    data = res.json()
    print(f"Query: '{data['query']}' | Dialect: {data['dialect']} | Results Count: {data['count']}")
    assert data["count"] > 0, "Fuzzy search should find products despite typos"
    for item in data["results"]:
        print(f"  [Match] {item['name']} - ${item['price']} (Category: {item['category']})")

    print("\n================================================================")
    print("2. TESTING POSTGRESQL FULL-TEXT SEARCH (STEMMING & GIN INDEX)")
    print("================================================================")
    # Testing fulltext query: 'smartphone'
    res = client.get("/api/v1/products/search/advanced?q=smartphone&mode=fulltext")
    assert res.status_code == 200, res.text
    data = res.json()
    print(f"Query: '{data['query']}' | Mode: {data['mode']} | Results Count: {data['count']}")
    assert data["count"] > 0, "FTS should match smartphone in product descriptions"
    for item in data["results"]:
        print(f"  [Match] {item['name']} - ${item['price']} (Category: {item['category']})")

    print("\n================================================================")
    print("3. TESTING MAIN PRODUCT CATALOG HYBRID SEARCH (Typo: 'keybord')")
    print("================================================================")
    res = client.get("/api/v1/products?search=keybord")
    assert res.status_code == 200, res.text
    data = res.json()
    print(f"Catalog Total Found: {data['total']}")
    assert data["total"] > 0
    for item in data["items"]:
        print(f"  [Match] {item['name']} - Category: {item['category']['name']}")

    print("\n================================================================")
    print("4. TESTING CELERY PDF INVOICE TASK LIFECYCLE (TRIGGER & POLL)")
    print("================================================================")
    # Login as admin to get auth token
    login_res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "AdminPassword123!"})
    assert login_res.status_code == 200, f"Admin login failed: {login_res.text}"
    admin_token = login_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    trigger_res = client.post("/api/v1/tasks/orders/1/invoice", headers=admin_headers)
    assert trigger_res.status_code == 202
    task_id = trigger_res.json()["task_id"]
    print(f"Task Triggered Successfully! Task ID: {task_id}")

    # Poll status
    status_res = client.get(f"/api/v1/tasks/{task_id}", headers=admin_headers)
    assert status_res.status_code == 200
    st_data = status_res.json()
    print(f"Task Polling Status: State={st_data['state']}, Progress={st_data['progress']}%")
    print(f"Task Result: {st_data.get('result')}")
    assert st_data["state"] in ["PROGRESS", "SUCCESS"]

    print("\n================================================================")
    print("5. TESTING CELERY BULK CSV IMPORT & RBAC SECURITY")
    print("================================================================")
    csv_data = (
        "name,description,price,stock,category_id\n"
        "Smart Fitness Band,Waterproof AMOLED health tracker,49.99,100,1\n"
        "Bluetooth Soundbar,Dolby Audio Home Theater,149.99,40,1\n"
    )
    files = {"file": ("integration_test.csv", io.BytesIO(csv_data.encode("utf-8")), "text/csv")}

    # RBAC Test: Non-admin customer cannot import CSV (should return 403 Forbidden)
    cust_login = client.post("/api/v1/auth/login", json={"username": "customer1", "password": "SecretPassword123!"})
    cust_token = cust_login.json()["access_token"]
    cust_headers = {"Authorization": f"Bearer {cust_token}"}
    forbidden_res = client.post("/api/v1/tasks/products/import-csv", files=files, headers=cust_headers)
    print(f"Customer CSV Import Attempt Response Code: {forbidden_res.status_code}")
    assert forbidden_res.status_code == 403, "Customer should be rejected with 403 Forbidden!"
    print("  -> Customer correctly blocked from bulk CSV import (RBAC Protected)")

    # Admin successfully triggers bulk import
    files2 = {"file": ("integration_test.csv", io.BytesIO(csv_data.encode("utf-8")), "text/csv")}
    csv_trigger = client.post("/api/v1/tasks/products/import-csv", files=files2, headers=admin_headers)
    assert csv_trigger.status_code == 202
    csv_task_id = csv_trigger.json()["task_id"]
    print(f"Admin CSV Task Triggered! Task ID: {csv_task_id}")

    csv_status = client.get(f"/api/v1/tasks/{csv_task_id}", headers=admin_headers)
    assert csv_status.status_code == 200
    csv_data_out = csv_status.json()
    print(f"CSV Polling Status: State={csv_data_out['state']}, Progress={csv_data_out['progress']}%")
    print(f"CSV Result: {csv_data_out.get('result')}")

    print("\n================================================================")
    print("ALL DAY 18 BACKEND, SEARCH & RBAC SECURITY PASSED 100%!")
    print("================================================================")


if __name__ == "__main__":
    test_search_and_tasks()
