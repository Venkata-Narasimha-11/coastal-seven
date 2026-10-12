"""Comprehensive Automated Test Suite for Day 21 – AI FOCUS.

Tests all 8 core syllabus requirements:
1. AI-Powered Product Descriptions (tones, structuring, SEO tags)
2. Semantic / Intent-Based Search (ChromaDB vector retrieval, score, price/category filters)
3. AI Content Moderation (profanity, toxicity, spam/links, asterisks censoring)
4. Redis AI Response Caching (deterministic keys, cache hit/miss, latency reduction)
5. Per-User & Per-IP Rate Limiting (tiered limits, HTTP 429, Retry-After header)
6. AI Testing & Mocking (external LLM isolation, deterministic offline verification)
7. Fallbacks & Graceful Degradation (vector fallback to SQL, LLM fallback to heuristic engine)
8. AI Agents & Tool Calling (stock lookup, price check, coupon calculator, order status)
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.models.product import Category, Product
from app.models.order import Order
from app.services.ai_cache_service import AICacheService
from app.services.ai_description_service import AIDescriptionService
from app.services.ai_moderation_service import AIModerationService
from app.services.ai_agent_service import AIAgentService
from app.services.semantic_search_service import SemanticSearchService
from app.utils.ai_rate_limit import AIRateLimiter


@pytest.fixture
def sample_catalog(db):
    """Seeds test database with sample products for AI testing."""
    cat_elec = Category(name="Electronics", slug="electronics")
    cat_foot = Category(name="Footwear", slug="footwear")
    db.add_all([cat_elec, cat_foot])
    db.commit()

    prod1 = Product(
        name="Sony WH-1000XM5 Wireless Headphones",
        slug="sony-wh-1000xm5",
        description="Industry leading noise canceling headphones with 30-hour battery life and crystal clear calling.",
        price=29990.0,
        stock=15,
        category_id=cat_elec.id,
        is_active=True,
    )
    prod2 = Product(
        name="Apple AirPods Pro 2nd Gen",
        slug="apple-airpods-pro-2",
        description="Active noise cancellation, transparency mode, and spatial audio with MagSafe USB-C case.",
        price=24900.0,
        stock=8,
        category_id=cat_elec.id,
        is_active=True,
    )
    prod3 = Product(
        name="Nike Air Zoom Pegasus 40",
        slug="nike-air-zoom-pegasus-40",
        description="Lightweight breathable responsive road running shoes with dual Zoom Air units.",
        price=11895.0,
        stock=20,
        category_id=cat_foot.id,
        is_active=True,
    )
    db.add_all([prod1, prod2, prod3])
    db.commit()
    db.refresh(prod1)
    db.refresh(prod2)
    db.refresh(prod3)
    return [prod1, prod2, prod3]


# ==============================================================================
# 1. AI-POWERED PRODUCT DESCRIPTIONS
# ==============================================================================
def test_ai_product_description_generation_tones():
    """Verify description generation across different tones and formatting."""
    # Engaging tone
    res_engaging = AIDescriptionService.generate_description(
        name="Sony WH-1000XM5",
        category="Electronics",
        features=["Industry-leading ANC", "30hr battery", "Multipoint bluetooth"],
        price=29990.0,
        tone="engaging",
        use_cache=False,
    )
    assert res_engaging["product_name"] == "Sony WH-1000XM5"
    assert "Key Features" in res_engaging["description"]
    assert "Sony WH-1000XM5" in res_engaging["description"]
    assert "₹29,990.00" in res_engaging["description"]
    assert "electronics" in res_engaging["suggested_tags"]

    # Technical tone
    res_tech = AIDescriptionService.generate_description(
        name="Precision Multimeter",
        category="Tools",
        features=["True RMS", "6000 counts"],
        price=4500.0,
        tone="technical",
        use_cache=False,
    )
    assert "Engineered Precision" in res_tech["description"]
    assert "True RMS" in res_tech["description"]


def test_ai_description_api_endpoint(client):
    """Test POST /api/v1/ai/generate-description API endpoint."""
    payload = {
        "name": "Bose QuietComfort 45",
        "category": "Audio",
        "features": ["World-class noise cancellation", "Lightweight comfort", "24-hr battery"],
        "price": 28900.0,
        "tone": "luxury",
        "target_audience": "Frequent flyers and audiophiles"
    }
    response = client.post("/api/v1/ai/generate-description", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["product_name"] == "Bose QuietComfort 45"
    assert "Elegance Redefined" in data["description"]
    assert response.headers["X-AI-Cache"] in ["MISS", "HIT"]
    assert "X-AI-Provider" in response.headers


# ==============================================================================
# 2. REDIS AI RESPONSE CACHING
# ==============================================================================
def test_redis_ai_response_caching(client):
    """Verify that repeated AI queries are served instantly from Redis cache."""
    AICacheService.clear_all_ai_caches()

    payload = {
        "name": "Garmin Fenix 7 Pro Solar",
        "category": "Wearables",
        "features": ["Solar charging", "Heart rate sensor", "Topo maps"],
        "price": 82000.0,
        "tone": "engaging",
    }

    # Call 1: Expect Cache Miss
    resp1 = client.post("/api/v1/ai/generate-description", json=payload)
    assert resp1.status_code == 200
    assert resp1.headers["X-AI-Cache"] == "MISS"
    data1 = resp1.json()
    assert data1["cached"] is False

    # Call 2: Expect Cache Hit with identical response
    resp2 = client.post("/api/v1/ai/generate-description", json=payload)
    assert resp2.status_code == 200
    assert resp2.headers["X-AI-Cache"] == "HIT"
    data2 = resp2.json()
    assert data2["cached"] is True
    assert data2["description"] == data1["description"]

    # Verify metrics endpoint
    metrics_resp = client.get("/api/v1/ai/cache-metrics")
    assert metrics_resp.status_code == 200
    metrics_data = metrics_resp.json()["metrics"]
    assert metrics_data["cache_hits"] >= 1
    assert metrics_data["hit_ratio_percent"] > 0


# ==============================================================================
# 3. AI CONTENT MODERATION
# ==============================================================================
def test_ai_content_moderation_safe_text():
    """Verify approved verdict for clean user reviews."""
    review = "Outstanding product! The sound quality is crisp and comfortable for all-day listening."
    result = AIModerationService.moderate_content(review, use_cache=False)
    assert result["is_safe"] is True
    assert result["status"] == "approved"
    assert len(result["flagged_categories"]) == 0
    assert result["confidence_score"] >= 0.9


def test_ai_content_moderation_profanity_censorship():
    """Verify rejected verdict and asterisks masking for vulgarity."""
    bad_text = "This damn product is a complete fake scam and total shit!"
    result = AIModerationService.moderate_content(bad_text, use_cache=False)
    assert result["is_safe"] is False
    assert result["status"] == "rejected"
    assert "profanity" in result["flagged_categories"]
    assert "***" in result["censored_content"] or "d***" in result["censored_content"]


def test_ai_content_moderation_spam_and_contact_leak():
    """Verify flagged status when unauthorized external URLs or emails are present."""
    spam_text = "Great deal! Contact me at seller@promo.com or visit http://scam-store.com for free money!"
    result = AIModerationService.moderate_content(spam_text, use_cache=False)
    assert result["is_safe"] is False
    assert "spam_or_contact_leak" in result["flagged_categories"]
    assert "[REDACTED LINK/CONTACT]" in result["censored_content"]


def test_ai_moderation_endpoint(client):
    """Test POST /api/v1/ai/moderate endpoint."""
    response = client.post("/api/v1/ai/moderate", json={"content": "Excellent battery life!", "content_type": "review"})
    assert response.status_code == 200
    data = response.json()
    assert data["is_safe"] is True
    assert response.headers["X-AI-Safety"] == "SAFE"


# ==============================================================================
# 4. SEMANTIC / VECTOR SEARCH
# ==============================================================================
def test_semantic_search_with_filters(sample_catalog, db):
    """Verify semantic intent matching with category and price limits."""
    # Search for running footwear
    search_res = SemanticSearchService.search(
        query="running shoe for outdoor morning marathon",
        db=db,
        category="Footwear",
        max_price=15000.0,
        limit=5,
        use_cache=False,
    )
    assert search_res["total_results"] >= 1
    top_result = search_res["results"][0]
    assert "Nike" in top_result["name"] or top_result["category"] == "Footwear"
    assert top_result["price"] <= 15000.0
    assert "similarity_score" in top_result


def test_semantic_search_sql_graceful_fallback(sample_catalog, db):
    """Verify that search degrades safely to SQL if vector service encounters an issue."""
    with patch("app.services.rag_service.RAGService.get_collection", side_effect=Exception("ChromaDB service down")):
        fallback_res = SemanticSearchService.search(
            query="Sony",
            db=db,
            limit=5,
            use_cache=False
        )
        assert fallback_res["provider"] == "sql-keyword-fallback"
        assert fallback_res["total_results"] >= 1
        assert "Sony" in fallback_res["results"][0]["name"]


def test_semantic_search_api_endpoint(sample_catalog, client):
    """Test GET /api/v1/ai/semantic-search endpoint."""
    response = client.get("/api/v1/ai/semantic-search?q=wireless+headphones&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "total_results" in data
    assert "provider" in data


# ==============================================================================
# 5. PER-USER & PER-IP RATE LIMITING
# ==============================================================================
def test_per_user_rate_limiting_enforcement(client):
    """Verify rate limiter allows requests up to quota and returns 429 when exceeded."""
    limiter = AIRateLimiter(custom_limit=3)

    # Override ai_rate_limiter dependency with custom low limit
    from app.utils.ai_rate_limit import ai_rate_limiter
    app.dependency_overrides[ai_rate_limiter] = limiter

    try:
        # 1st request -> Allowed
        r1 = client.post("/api/v1/ai/moderate", json={"content": "Test check 1"})
        assert r1.status_code == 200
        assert r1.headers["X-RateLimit-Limit"] == "3"

        # 2nd request -> Allowed
        r2 = client.post("/api/v1/ai/moderate", json={"content": "Test check 2"})
        assert r2.status_code == 200

        # 3rd request -> Allowed
        r3 = client.post("/api/v1/ai/moderate", json={"content": "Test check 3"})
        assert r3.status_code == 200

        # 4th request -> Rate Limit Exceeded (HTTP 429)
        r4 = client.post("/api/v1/ai/moderate", json={"content": "Test check 4"})
        assert r4.status_code == 429
        assert "Retry-After" in r4.headers
        data4 = r4.json()
        assert "Rate limit exceeded" in str(data4)

    finally:
        app.dependency_overrides.pop(ai_rate_limiter, None)


# ==============================================================================
# 6. AI AGENTS & TOOL CALLING
# ==============================================================================
def test_agent_tool_check_product_stock(sample_catalog, db):
    """Verify check_product_stock tool returns live inventory."""
    stock_res = AIAgentService.execute_check_product_stock(db, "Sony")
    assert stock_res["found"] is True
    assert stock_res["stock_quantity"] == 15
    assert stock_res["in_stock"] is True
    assert stock_res["status"] == "In Stock"


def test_agent_tool_apply_coupon_calculator():
    """Verify apply_coupon_calculator calculates exact discounts."""
    # Valid SAVE10 coupon
    res_10 = AIAgentService.execute_apply_coupon_calculator("SAVE10", order_amount=10000.0)
    assert res_10["valid"] is True
    assert res_10["discount_amount"] == 1000.0
    assert res_10["final_amount"] == 9000.0

    # Valid WELCOME20 coupon
    res_20 = AIAgentService.execute_apply_coupon_calculator("WELCOME20", order_amount=5000.0)
    assert res_20["valid"] is True
    assert res_20["discount_amount"] == 1000.0
    assert res_20["final_amount"] == 4000.0

    # Invalid coupon
    res_invalid = AIAgentService.execute_apply_coupon_calculator("INVALID99", order_amount=5000.0)
    assert res_invalid["valid"] is False


def test_agent_run_multi_step_reasoning(sample_catalog, db):
    """Verify autonomous agent loop selects tools and synthesizes grounded answer."""
    query = "Is Sony headphones in stock, and how much will it cost with coupon SAVE10?"
    agent_res = AIAgentService.run_agent(query, db=db, use_cache=False)

    assert "response" in agent_res
    assert len(agent_res["tool_calls"]) >= 1
    # Check that stock tool or coupon tool was executed
    tool_names = [t["tool"] for t in agent_res["tool_calls"]]
    assert "check_product_stock" in tool_names or "apply_coupon_calculator" in tool_names
    assert "Sony" in agent_res["response"] or "Stock" in agent_res["response"]


def test_agent_api_endpoint(sample_catalog, client):
    """Test POST /api/v1/ai/agent endpoint."""
    payload = {"query": "Check stock for Nike shoes"}
    response = client.post("/api/v1/ai/agent", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "tool_calls" in data
    assert "X-AI-Tools-Executed" in response.headers


# ==============================================================================
# 7. AI TESTING & MOCKING OF EXTERNAL APIS
# ==============================================================================
def test_mocking_external_llm_calls():
    """Verify external Groq/Gemini calls can be mocked during automated testing."""
    mock_groq_response = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "### Mocked LLM Output\nHigh quality product description generated via mocked API."
    mock_groq_response.choices = [mock_choice]

    with patch("groq.Groq") as mock_groq_class:
        mock_instance = MagicMock()
        mock_instance.chat.completions.create.return_value = mock_groq_response
        mock_groq_class.return_value = mock_instance

        with patch("app.config.settings.GROQ_API_KEY", "mock-groq-key-12345"):
            result = AIDescriptionService.generate_description(
                name="Test Mock Product",
                category="Gadgets",
                use_cache=False
            )
            assert result["provider"] == "groq"
            assert "Mocked LLM Output" in result["description"]


# ==============================================================================
# 8. CACHE CLEAR AND METRICS INTEGRATION
# ==============================================================================
def test_cache_clear_endpoint(client):
    """Test POST /api/v1/ai/clear-cache invalidates Redis AI keys."""
    response = client.post("/api/v1/ai/clear-cache")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "cleared_count" in data
