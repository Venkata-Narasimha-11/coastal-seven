"""Semantic Product Search Service.

Performs vector embedding-based similarity search using ChromaDB and cosine distance,
supporting price/category filtering, SQL fallback for resilience, and Redis query caching.
"""

import logging
import time
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.models.product import Product
from app.services.ai_cache_service import AICacheService
from app.services.rag_service import RAGService

logger = logging.getLogger("semantic_search_service")


class SemanticSearchService:
    """Enterprise Semantic Search Service."""

    @classmethod
    def _sql_keyword_fallback(
        cls,
        db: Session,
        query: str,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Graceful SQL fallback when vector search is unavailable."""
        q = db.query(Product).filter(Product.is_active == True)
        search_term = f"%{query.strip()}%"
        q = q.filter(Product.name.ilike(search_term) | Product.description.ilike(search_term))

        if min_price is not None:
            q = q.filter(Product.price >= min_price)
        if max_price is not None:
            q = q.filter(Product.price <= max_price)

        products = q.limit(limit).all()
        results = []
        for p in products:
            cat_name = p.category.name if p.category else "General"
            if category and category.lower() not in cat_name.lower():
                continue
            results.append({
                "id": p.id,
                "name": p.name,
                "category": cat_name,
                "price": float(p.price),
                "stock": p.stock,
                "similarity_score": 0.75,
                "image_url": p.image_url or "",
                "description": p.description or "",
            })
        return results

    @classmethod
    def search(
        cls,
        query: str,
        db: Session,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        limit: int = 10,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Performs semantic vector search with Redis caching and graceful fallback."""
        start_time = time.time()
        clean_query = query.strip()

        # 1. Check Redis Cache
        cache_payload = {
            "query": clean_query.lower(),
            "category": category,
            "min_price": min_price,
            "max_price": max_price,
            "limit": limit,
        }
        cache_key = AICacheService.generate_key(AICacheService.PREFIX_SEMANTIC, cache_payload)

        if use_cache:
            cached_data, is_hit = AICacheService.get(cache_key)
            if is_hit and cached_data:
                cached_data["cached"] = True
                cached_data["latency_ms"] = round((time.time() - start_time) * 1000, 2)
                return cached_data

        # 2. ChromaDB Vector Similarity Search
        results = []
        provider_used = "chromadb-vector"

        try:
            collection = RAGService.get_collection()
            total_docs = collection.count()

            # Auto-index if vector collection is currently unpopulated
            if total_docs == 0:
                logger.info("ChromaDB unpopulated during semantic search. Indexing products now...")
                RAGService.index_all_products(db)
                total_docs = collection.count()

            if total_docs > 0:
                n_fetch = min(limit * 3, total_docs)  # Fetch candidate pool for post-filtering
                query_res = collection.query(query_texts=[clean_query], n_results=n_fetch)

                metadatas = query_res.get("metadatas", [[]])[0]
                distances = query_res.get("distances", [[]])[0] if "distances" in query_res else [0.0] * len(metadatas)
                documents = query_res.get("documents", [[]])[0]

                for meta, dist, doc in zip(metadatas, distances, documents):
                    prod_price = float(meta.get("price", 0.0))
                    prod_cat = str(meta.get("category", "General"))

                    # Apply filters
                    if category and category.lower() not in prod_cat.lower():
                        continue
                    if min_price is not None and prod_price < min_price:
                        continue
                    if max_price is not None and prod_price > max_price:
                        continue

                    similarity = round(max(0.0, 1.0 - float(dist)), 3) if dist is not None else 0.85
                    results.append({
                        "id": meta.get("product_id"),
                        "name": meta.get("name"),
                        "category": prod_cat,
                        "price": prod_price,
                        "stock": meta.get("stock", 0),
                        "similarity_score": similarity,
                        "image_url": meta.get("image_url", ""),
                        "description": doc,
                    })

                    if len(results) >= limit:
                        break
            else:
                results = cls._sql_keyword_fallback(db, clean_query, category, min_price, max_price, limit)
                provider_used = "sql-keyword-fallback"

        except Exception as exc:
            logger.warning("ChromaDB vector search failed (%s). Degrading to SQL search...", exc)
            results = cls._sql_keyword_fallback(db, clean_query, category, min_price, max_price, limit)
            provider_used = "sql-keyword-fallback"

        latency_ms = round((time.time() - start_time) * 1000, 2)
        response_payload = {
            "query": clean_query,
            "total_results": len(results),
            "results": results,
            "provider": provider_used,
            "cached": False,
            "latency_ms": latency_ms,
        }

        # 3. Store in Redis Cache (15-minute TTL)
        if use_cache:
            AICacheService.set(cache_key, response_payload, ttl_seconds=900)

        return response_payload
