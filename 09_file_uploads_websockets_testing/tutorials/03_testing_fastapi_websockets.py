"""Tutorial 3: Testing FastAPI Applications & WebSockets with Pytest.

Topics covered:
1. Pytest Architecture: Fixtures, Scopes, and Test Isolation.
2. HTTP Multipart Testing: Sending synthetic files to endpoints using TestClient.
3. WebSocket Testing: Using TestClient.websocket_connect() for full-duplex assertion.
4. Async Testing: pytest-asyncio integration for coroutine endpoints.
5. Code Coverage: Measuring branch and line execution with pytest-cov.
"""

import io
import json
import sys
from pathlib import Path

from PIL import Image
from starlette.testclient import TestClient

if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure module importability
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app


def create_in_memory_image(width: int = 200, height: int = 150) -> bytes:
    """Generate in-memory valid JPEG image bytes for fixture testing."""
    img = Image.new("RGB", (width, height), color=(56, 189, 248))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def demo_testing_file_uploads() -> None:
    print("=" * 70)
    print("1. DEMONSTRATING FASTAPI FILE UPLOAD TESTING WITH TESTCLIENT")
    print("=" * 70)

    client = TestClient(app)

    # 1. Create synthetic image bytes
    raw_img = create_in_memory_image(400, 300)
    file_payload = {"file": ("sample_test_photo.jpg", raw_img, "image/jpeg")}

    # 2. Perform POST upload request
    response = client.post("/api/v1/uploads", files=file_payload)
    print(f"[*] POST /api/v1/uploads -> Status: {response.status_code}")
    assert response.status_code == 201

    data = response.json()
    print(f"    - Upload Success: {data['success']}")
    print(f"    - Saved Filename: {data['filename']}")
    print(f"    - Original Name:  {data['original_name']}")
    print(f"    - SHA-256 Hash:   {data['checksum_sha256'][:16]}...")
    print(f"    - Variants:       {list(data['variants'].keys())}")
    assert "thumbnail" in data["variants"]
    assert "medium" in data["variants"]


def demo_testing_websockets() -> None:
    print("\n" + "=" * 70)
    print("2. DEMONSTRATING WEBSOCKET TESTING WITH TESTCLIENT")
    print("=" * 70)

    client = TestClient(app)

    # Test bidirectional WebSocket exchange
    with client.websocket_connect("/ws/test_client_42") as ws:
        # 1. Receive welcome notification
        welcome_raw = ws.receive_text()
        welcome = json.loads(welcome_raw)
        print(
            f"[*] Received Initial Message: event='{welcome['event']}' from='{welcome['sender_id']}'"
        )
        assert welcome["event"] == "notification"

        # 2. Send ping action and assert pong
        print("[*] Sending 'ping' command via WebSocket...")
        ws.send_text(json.dumps({"action": "ping"}))

        reply_raw = ws.receive_text()
        reply = json.loads(reply_raw)
        print(
            f"[*] Server Response: event='{reply['event']}' reply='{reply['data'].get('reply')}'"
        )
        assert reply["event"] == "heartbeat"
        assert reply["data"]["reply"] == "pong"


def demo_testing_final_integration() -> None:
    print("\n" + "=" * 70)
    print("3. TESTING FINAL INTEGRATION (UPLOAD + WEBSOCKET BROADCAST)")
    print("=" * 70)

    client = TestClient(app)

    with client.websocket_connect("/ws/listener_99") as ws:
        # Drain initial welcome message
        _ = ws.receive_text()

        # Perform file upload triggering WebSocket broadcast
        raw_img = create_in_memory_image(500, 500)
        file_payload = {"file": ("broadcast_trigger.jpg", raw_img, "image/jpeg")}
        res = client.post(
            "/api/v1/integrated/upload-notify",
            files=file_payload,
            data={"uploader_name": "IntegrationTester"},
        )
        assert res.status_code == 201

        # The connected WebSocket listener should have received the notification!
        event_raw = ws.receive_text()
        event = json.loads(event_raw)
        print(f"[*] Connected WebSocket Client received real-time push notification:")
        print(f"    - Event:       {event['event']}")
        print(f"    - File Name:   {event['data']['original_name']}")
        print(f"    - Uploader:    {event['data']['uploader']}")
        print(f"    - Proc Time:   {event['data']['processing_time_ms']} ms")
        assert event["event"] == "file_uploaded"
        assert event["data"]["original_name"] == "broadcast_trigger.jpg"


if __name__ == "__main__":
    demo_testing_file_uploads()
    demo_testing_websockets()
    demo_testing_final_integration()
    print("\n" + "=" * 70)
    print("[OK] Tutorial 3 Complete: FastAPI & WebSocket Testing Patterns Mastered!")
    print("=" * 70)
