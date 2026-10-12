import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

# Inject Windows system certificates to prevent SSL verify failures on Windows
try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

import chromadb
from chromadb.utils import embedding_functions
from sqlalchemy.orm import Session, joinedload

from app.config import BASE_DIR, settings
from app.models.product import Product

logger = logging.getLogger(__name__)

class RAGService:
    """
    Day 20 RAG Pipeline Service:
    Manages vector embeddings, ChromaDB indexing, and context retrieval
    grounded in the e-commerce product catalog.
    """
    _client = None
    _collection = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            persist_dir = BASE_DIR / settings.CHROMA_PERSIST_DIR
            persist_dir.mkdir(parents=True, exist_ok=True)
            try:
                cls._client = chromadb.PersistentClient(path=str(persist_dir))
                logger.info(f"Initialized ChromaDB PersistentClient at {persist_dir}")
            except Exception as e:
                logger.warning(f"Failed to initialize PersistentClient ({e}), falling back to EphemeralClient")
                cls._client = chromadb.EphemeralClient()
        return cls._client

    @classmethod
    def get_collection(cls):
        if cls._collection is None:
            client = cls.get_client()
            # Default embedding function uses lightweight ONNX/MiniLM
            try:
                emb_fn = embedding_functions.DefaultEmbeddingFunction()
                cls._collection = client.get_or_create_collection(
                    name="products_catalog",
                    embedding_function=emb_fn,
                    metadata={"hnsw:space": "cosine"}
                )
            except Exception as e:
                logger.error(f"Error creating ChromaDB collection with default embedding function: {e}")
                cls._collection = client.get_or_create_collection(
                    name="products_catalog",
                    metadata={"hnsw:space": "cosine"}
                )
        return cls._collection

    @classmethod
    def index_all_products(cls, db: Session) -> int:
        """
        Indexes all active products from PostgreSQL into ChromaDB.
        Uses product title, category, description, and price to create rich chunks.
        """
        collection = cls.get_collection()
        products = (
            db.query(Product)
            .options(joinedload(Product.category))
            .filter(Product.is_active == True)
            .all()
        )

        if not products:
            logger.warning("No active products found in database to index into ChromaDB.")
            return 0

        documents = []
        metadatas = []
        ids = []

        for p in products:
            cat_name = p.category.name if p.category else "General"
            doc_text = (
                f"Product: {p.name}\n"
                f"Category: {cat_name}\n"
                f"Price: INR {float(p.price):,.2f}\n"
                f"Stock: {p.stock} units available\n"
                f"Description: {p.description or 'No description available.'}"
            )
            documents.append(doc_text)
            ids.append(f"prod_{p.id}")
            metadatas.append({
                "product_id": int(p.id),
                "name": str(p.name),
                "category": str(cat_name),
                "price": float(p.price),
                "stock": int(p.stock),
                "image_url": str(p.image_url or ""),
                "slug": str(p.slug or ""),
            })

        # Upsert in batch to ChromaDB
        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

        indexed_count = len(documents)
        logger.info(f"Successfully indexed {indexed_count} products into ChromaDB 'products_catalog'.")
        return indexed_count

    @classmethod
    def retrieve_relevant_context(cls, query: str, n_results: int = 4, db: Optional[Session] = None) -> Dict[str, Any]:
        """
        Searches ChromaDB for relevant products matching the query.
        Returns formatted context string for LLM and structured citations list.
        """
        collection = cls.get_collection()
        total_count = collection.count()

        # Auto-index if ChromaDB is empty and DB session is available
        if total_count == 0 and db is not None:
            logger.info("ChromaDB is empty. Auto-indexing products from database...")
            cls.index_all_products(db)
            total_count = collection.count()

        if total_count == 0:
            return {
                "context_text": "No products currently available in the catalog.",
                "sources": []
            }

        # Query vector database
        query_n = min(n_results, total_count)
        results = collection.query(
            query_texts=[query],
            n_results=query_n
        )

        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0] if "distances" in results and results["distances"] else [0.0] * len(docs)

        formatted_context_parts = []
        sources = []

        for idx, (doc, meta, dist) in enumerate(zip(docs, metas, distances), 1):
            formatted_context_parts.append(
                f"[{idx}] {doc}"
            )
            sources.append({
                "id": meta.get("product_id"),
                "name": meta.get("name"),
                "category": meta.get("category"),
                "price": meta.get("price"),
                "stock": meta.get("stock"),
                "image_url": meta.get("image_url"),
                "slug": meta.get("slug"),
                "relevance_score": round(1.0 - float(dist), 3) if dist is not None else 1.0
            })

        context_text = "\n\n".join(formatted_context_parts)
        return {
            "context_text": context_text,
            "sources": sources
        }
