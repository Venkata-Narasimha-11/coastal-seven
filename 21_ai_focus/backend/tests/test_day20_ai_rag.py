import json
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.rag_service import RAGService
from app.services.ai_service import AIService

def test_rag_service_indexing_and_retrieval(client, db):
    """Verify that products from database are indexed into ChromaDB and retrieved via similarity."""
    count = RAGService.index_all_products(db)
    assert count >= 0

    # Query ChromaDB collection
    res = RAGService.retrieve_relevant_context("wireless headphones", n_results=3, db=db)
    assert "context_text" in res
    assert "sources" in res
    assert isinstance(res["sources"], list)
    if res["sources"]:
        assert "name" in res["sources"][0]
        assert "price" in res["sources"][0]
        assert "category" in res["sources"][0]

def test_ai_service_prompt_engineering():
    """Verify that system prompt enforces catalog context and proper structure."""
    context = "[1] Product: Sony WH-1000XM5\nPrice: ₹29,990"
    messages = AIService.build_prompt("recommend headphones", context=context)

    assert len(messages) >= 2
    assert messages[0]["role"] == "system"
    assert "CATALOG CONTEXT" in messages[0]["content"]
    assert "Sony WH-1000XM5" in messages[0]["content"]
    assert messages[-1]["role"] == "user"
    assert messages[-1]["content"] == "recommend headphones"

def test_ai_chat_reindex_endpoint(client):
    """Test POST /api/v1/chat/reindex."""
    response = client.post("/api/v1/chat/reindex")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "indexed_count" in data

def test_ai_chat_stream_endpoint(client):
    """Test POST /api/v1/chat/stream Server-Sent Events (SSE) streaming."""
    payload = {
        "message": "Which wireless headphones do you have under 30000?",
        "history": []
    }
    response = client.post("/api/v1/chat/stream", json=payload)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]

    # Read SSE stream lines
    lines = response.text.strip().split("\n")
    events = [line for line in lines if line.startswith("data: ")]
    assert len(events) >= 2

    # Verify first event contains sources citation payload
    first_data = json.loads(events[0].replace("data: ", ""))
    assert first_data["type"] == "sources"
    assert "sources" in first_data

    # Verify last event is done signal with provider info
    last_data = json.loads(events[-1].replace("data: ", ""))
    assert last_data["type"] == "done"
    assert "provider" in last_data
