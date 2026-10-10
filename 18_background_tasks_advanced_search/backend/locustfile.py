"""Locust load testing benchmark for Day 19 performance and rate limit evaluation."""

import random
from locust import HttpUser, between, task


class ECommerceCustomerUser(HttpUser):
    """Simulates realistic customer browsing and shopping behavior."""

    # Simulated think time between user actions: 1 to 3 seconds
    wait_time = between(1, 3)

    @task(6)
    def browse_products(self):
        """Browse catalog with pagination and sorting (weight: 6)."""
        page = random.randint(1, 3)
        sort_by = random.choice(["newest", "price_asc", "price_desc", "name_asc"])
        with self.client.get(
            f"/api/v1/products?page={page}&size=10&sort_by={sort_by}",
            headers={"Accept-Encoding": "gzip"},
            name="/api/v1/products [Catalog List]",
            catch_response=True,
        ) as response:
            if response.status_code in (200, 429):
                # 200 = Success, 429 = Valid SlowAPI rate limiting protection
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")

    @task(3)
    def search_products(self):
        """Search products using full-text and fuzzy search (weight: 3)."""
        queries = ["headphone", "phone", "electronics", "wireless", "test"]
        term = random.choice(queries)
        with self.client.get(
            f"/api/v1/products?search={term}",
            headers={"Accept-Encoding": "gzip"},
            name="/api/v1/products?search=[Search]",
            catch_response=True,
        ) as response:
            if response.status_code in (200, 429):
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")

    @task(2)
    def check_health(self):
        """Quick healthcheck ping (weight: 2)."""
        self.client.get("/health", name="/health [Health Check]")

    @task(1)
    def attempt_login(self):
        """Simulate user login attempt (weight: 1)."""
        payload = {
            "username": "customer1",
            "password": "SecretPassword123!",
        }
        with self.client.post(
            "/api/v1/auth/login",
            json=payload,
            catch_response=True,
            name="/api/v1/auth/login [Auth]",
        ) as response:
            if response.status_code in (200, 429):
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")
