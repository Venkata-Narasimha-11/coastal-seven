"""Enterprise AI Features Router (Day 21).

Exposes production-ready AI endpoints:
- POST /api/v1/ai/generate-description  (AI-Powered Product Descriptions)
- GET  /api/v1/ai/semantic-search        (Embedding-Based Semantic Search)
- POST /api/v1/ai/moderate               (AI Content Moderation)
- POST /api/v1/ai/agent                  (AI Autonomous Agent & Tool Calling)
- GET  /api/v1/ai/cache-metrics          (Redis AI Response Caching Analytics)
- POST /api/v1/ai/clear-cache            (Admin Cache Invalidation)

Protected by Per-User / Per-IP Rate Limiting, Redis Caching, and Fallback Degradation.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.ai_agent_service import AIAgentService
from app.services.ai_cache_service import AICacheService
from app.services.ai_description_service import AIDescriptionService
from app.services.ai_moderation_service import AIModerationService
from app.services.semantic_search_service import SemanticSearchService
from app.utils.ai_rate_limit import ai_rate_limiter

router = APIRouter(prefix="/ai", tags=["AI Focus Features (Day 21)"])


# -------------------------------------------------------------
# Pydantic Schemas
# -------------------------------------------------------------
class GenerateDescriptionRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=200, description="Product Name")
    category: Optional[str] = Field(default="General", description="Product Category")
    features: Optional[List[str]] = Field(default=[], description="Bullet points / key specifications")
    price: Optional[float] = Field(default=None, ge=0, description="Product price in INR")
    tone: Optional[str] = Field(
        default="engaging",
        description="Description tone: 'engaging', 'professional', 'technical', 'concise', or 'luxury'"
    )
    target_audience: Optional[str] = Field(default=None, description="Intended customer segment")


class ModerationRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000, description="User-generated text to moderate")
    content_type: Optional[str] = Field(
        default="review",
        description="Type of content: 'review', 'comment', 'query', or 'product'"
    )


class AgentQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="User question or command for the agent")


# -------------------------------------------------------------
# Endpoints
# -------------------------------------------------------------
@router.post(
    "/generate-description",
    summary="Generate AI Product Description",
    dependencies=[Depends(ai_rate_limiter)]
)
def generate_product_description(
    payload: GenerateDescriptionRequest,
    response: Response,
):
    """Integrates LLMs to generate clear, engaging, and context-aware product descriptions automatically.

    Backed by 24-hour Redis response caching and 3-tier fallback degradation.
    """
    result = AIDescriptionService.generate_description(
        name=payload.name,
        category=payload.category or "General",
        features=payload.features or [],
        price=payload.price,
        tone=payload.tone or "engaging",
        target_audience=payload.target_audience,
    )
    response.headers["X-AI-Cache"] = "HIT" if result.get("cached") else "MISS"
    response.headers["X-AI-Provider"] = str(result.get("provider"))
    return result


@router.get(
    "/semantic-search",
    summary="Embedding-Based Semantic Product Search",
    dependencies=[Depends(ai_rate_limiter)]
)
def semantic_product_search(
    response: Response,
    q: str = Query(..., min_length=1, max_length=500, description="Semantic search query (e.g., 'noise-free headphones for study')"),
    category: Optional[str] = Query(None, description="Filter by category name"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    limit: int = Query(10, ge=1, le=50, description="Max products to return"),
    db: Session = Depends(get_db),
):
    """Implements embedding-based vector search in ChromaDB to retrieve products based on user intent and semantic similarity.

    Includes automatic SQL keyword fallback and Redis caching.
    """
    result = SemanticSearchService.search(
        query=q,
        db=db,
        category=category,
        min_price=min_price,
        max_price=max_price,
        limit=limit,
    )
    response.headers["X-AI-Cache"] = "HIT" if result.get("cached") else "MISS"
    response.headers["X-AI-Provider"] = str(result.get("provider"))
    return result


@router.post(
    "/moderate",
    summary="AI Content Moderation Check",
    dependencies=[Depends(ai_rate_limiter)]
)
def moderate_user_content(
    payload: ModerationRequest,
    response: Response,
):
    """Integrates content moderation checks to identify inappropriate, abusive, or unsafe user-generated content.

    Flags profanity, toxicity, contact info, and spam with confidence scores and censored text.
    """
    result = AIModerationService.moderate_content(
        content=payload.content,
        content_type=payload.content_type or "review",
    )
    response.headers["X-AI-Cache"] = "HIT" if result.get("cached") else "MISS"
    response.headers["X-AI-Safety"] = "SAFE" if result.get("is_safe") else "FLAGGED"
    return result


@router.post(
    "/agent",
    summary="AI Agent with Autonomous Tool Calling",
    dependencies=[Depends(ai_rate_limiter)]
)
def invoke_ai_agent(
    payload: AgentQueryRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    """Autonomous AI Shopping Agent executing tool calls against the application:

    - check_product_stock
    - lookup_product_price
    - apply_coupon_calculator
    - check_order_status
    - search_catalog
    """
    result = AIAgentService.run_agent(query=payload.query, db=db)
    response.headers["X-AI-Cache"] = "HIT" if result.get("cached") else "MISS"
    response.headers["X-AI-Tools-Executed"] = str(result.get("tools_count", 0))
    return result


@router.get("/cache-metrics", summary="Get Redis AI Cache Analytics")
def get_ai_cache_analytics():
    """Returns analytics for Redis AI caching: hits, misses, hit ratio, and latency saved."""
    return {
        "status": "success",
        "metrics": AICacheService.get_metrics(),
    }


@router.post("/clear-cache", summary="Invalidate AI Response Cache")
def clear_ai_response_cache():
    """Clears all cached AI responses in Redis."""
    count = AICacheService.clear_all_ai_caches()
    return {
        "status": "success",
        "message": f"Successfully flushed {count} AI response cache entries from Redis.",
        "cleared_count": count,
    }
