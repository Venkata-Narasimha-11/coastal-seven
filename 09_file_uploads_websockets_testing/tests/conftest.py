"""Pytest fixtures and configuration for testing file uploads and WebSockets."""

import io
from pathlib import Path
from typing import Generator

import pytest
from PIL import Image
from starlette.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.services.websocket_manager import manager


@pytest.fixture(autouse=True)
def isolate_upload_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Generator[Path, None, None]:
    """Isolate uploads directory to a temporary path for each test."""
    temp_upload = tmp_path / "test_uploads"
    temp_upload.mkdir(parents=True, exist_ok=True)
    (temp_upload / "originals").mkdir(exist_ok=True)
    (temp_upload / "thumbnails").mkdir(exist_ok=True)

    monkeypatch.setattr(settings, "UPLOAD_DIR", temp_upload)
    monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE_MB", 2)  # 2 MB for tests

    orig_dirs = []
    for route in app.routes:
        if getattr(route, "name", None) == "uploads" and hasattr(route, "app"):
            orig_dirs.append(
                (
                    route.app,
                    getattr(route.app, "directory", None),
                    getattr(route.app, "all_directories", None),
                )
            )
            route.app.directory = str(temp_upload)
            route.app.all_directories = [str(temp_upload)]

    yield temp_upload

    for app_obj, orig_dir, orig_all in orig_dirs:
        app_obj.directory = orig_dir
        app_obj.all_directories = orig_all


@pytest.fixture(autouse=True)
def reset_websocket_manager() -> Generator[None, None, None]:
    """Ensure clean WebSocket manager state between tests."""
    manager.active_connections.clear()
    manager.channels.clear()
    manager.client_subscriptions.clear()
    yield
    manager.active_connections.clear()
    manager.channels.clear()
    manager.client_subscriptions.clear()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """TestClient fixture with Lifespan support."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_jpeg_bytes() -> bytes:
    """Generate in-memory valid JPEG bytes."""
    img = Image.new("RGB", (400, 300), color=(56, 189, 248))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture
def sample_png_bytes() -> bytes:
    """Generate in-memory valid PNG bytes with transparency."""
    img = Image.new("RGBA", (250, 250), color=(245, 158, 11, 200))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def sample_webp_bytes() -> bytes:
    """Generate in-memory valid WebP bytes."""
    img = Image.new("RGB", (150, 150), color=(16, 185, 129))
    buf = io.BytesIO()
    img.save(buf, format="WEBP")
    return buf.getvalue()


@pytest.fixture
def corrupt_bytes() -> bytes:
    """Corrupt image payload (PNG header followed by garbage)."""
    return b"\x89PNG\r\n\x1a\nCorruptRandomDataThatCannotBeDecodedByPillow"


@pytest.fixture
def fake_script_bytes() -> bytes:
    """Executable text disguised with binary extension."""
    return b"#!/bin/bash\necho 'hello world'\n"
