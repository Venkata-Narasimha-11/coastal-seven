from typing import List, Optional, Dict
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.ai_service import AIService
from app.services.rag_service import RAGService

from app.utils.ai_rate_limit import ai_rate_limiter

router = APIRouter(prefix="/chat", tags=["AI Assistant & RAG"])

class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message text")

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="Customer shopping query")
    history: Optional[List[ChatMessage]] = Field(default=[], description="Previous conversation context")

@router.post("/stream", dependencies=[Depends(ai_rate_limiter)])
def stream_ai_chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Day 20 Streaming AI Chat Endpoint:
    Streams real-time Server-Sent Events (SSE) grounded by ChromaDB RAG catalog retrieval.
    Includes fallback provider strategy across Groq, Gemini, and intelligent local assistant.
    """
    history_dicts = [{"role": m.role, "content": m.content} for m in (request.history or [])]
    return StreamingResponse(
        AIService.stream_chat(query=request.message, history=history_dicts, db=db),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

@router.post("/reindex")
def reindex_catalog_vector_store(db: Session = Depends(get_db)):
    """
    Syncs the ChromaDB vector database with all active products in PostgreSQL.
    """
    count = RAGService.index_all_products(db)
    return {
        "status": "success",
        "message": f"Successfully re-indexed {count} products into ChromaDB vector database.",
        "indexed_count": count
    }
