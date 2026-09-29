"""End-to-End integration tests combining File Uploads, WebSockets, and Static Serving."""

import json

from starlette.testclient import TestClient


def test_integrated_upload_triggers_live_websocket_notification(
    client: TestClient, sample_jpeg_bytes: bytes
) -> None:
    """Validate full flow: upload image -> Pillow processing -> live WebSocket push -> static file serving."""
    # 1. Establish persistent WebSocket connection
    with client.websocket_connect("/ws/realtime_observer") as ws:
        # Drain initial welcome message
        _ = ws.receive_text()

        # 2. Upload image via integrated endpoint
        upload_response = client.post(
            "/api/v1/integrated/upload-notify",
            files={"file": ("breaking_news.jpg", sample_jpeg_bytes, "image/jpeg")},
            data={"uploader_name": "ReporterJane"},
        )
        assert upload_response.status_code == 201
        upload_data = upload_response.json()
        assert upload_data["success"] is True

        # 3. Assert WebSocket client immediately receives real-time broadcast notification
        raw_event = ws.receive_text()
        event = json.loads(raw_event)

        assert event["event"] == "file_uploaded"
        assert event["sender_id"] == "media_pipeline"
        assert event["data"]["original_name"] == "breaking_news.jpg"
        assert event["data"]["uploader"] == "ReporterJane"
        assert "thumbnail_url" in event["data"]
        assert "medium_url" in event["data"]
        assert event["data"]["processing_time_ms"] >= 0

        # 4. Verify Static File Serving: thumbnail & original are accessible via HTTP
        thumb_url = event["data"]["thumbnail_url"]
        thumb_res = client.get(thumb_url)
        assert thumb_res.status_code == 200
        assert len(thumb_res.content) > 0

        orig_url = event["data"]["url"]
        orig_res = client.get(orig_url)
        assert orig_res.status_code == 200
        assert orig_res.content == sample_jpeg_bytes


def test_hub_status_endpoint(client: TestClient, sample_png_bytes: bytes) -> None:
    """Test metrics endpoint reporting storage and connection telemetry."""
    # Upload one file
    client.post(
        "/api/v1/uploads",
        files={"file": ("test_metric.png", sample_png_bytes, "image/png")},
    )

    res = client.get("/api/v1/integrated/hub-status")
    assert res.status_code == 200
    data = res.json()

    assert data["total_files_stored"] >= 1
    assert data["total_disk_bytes"] > 0
    assert "image_presets" in data
    assert "thumbnail" in data["image_presets"]


def test_dashboard_ui_and_health_endpoints(client: TestClient) -> None:
    """Test dashboard HTML serving and health check endpoint."""
    # Health endpoint
    h_res = client.get("/health")
    assert h_res.status_code == 200
    assert h_res.json()["status"] == "healthy"

    # Dashboard root
    ui_res = client.get("/")
    assert ui_res.status_code == 200
    assert "Real-Time Media & Notification Hub" in ui_res.text
    assert "<!DOCTYPE html>" in ui_res.text
