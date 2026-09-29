"""Unit and integration tests for FastAPI file upload functionality."""

from pathlib import Path

from starlette.testclient import TestClient

from app.core.config import settings
from app.core.security import is_safe_path, sanitize_filename


def test_upload_single_jpeg_success(
    client: TestClient, sample_jpeg_bytes: bytes
) -> None:
    """Test successful single JPEG image upload and thumbnail generation."""
    response = client.post(
        "/api/v1/uploads",
        files={"file": ("beach_vacation.jpg", sample_jpeg_bytes, "image/jpeg")},
    )
    assert response.status_code == 201
    data = response.json()

    assert data["success"] is True
    assert data["original_name"] == "beach_vacation.jpg"
    assert data["content_type"] == "image/jpeg"
    assert data["file_size_bytes"] == len(sample_jpeg_bytes)
    assert len(data["checksum_sha256"]) == 64
    assert "original" in data["variants"]
    assert "thumbnail" in data["variants"]
    assert "medium" in data["variants"]

    # Verify original file exists in storage
    saved_path = settings.originals_dir / data["filename"]
    assert saved_path.exists()


def test_upload_single_png_success(client: TestClient, sample_png_bytes: bytes) -> None:
    """Test successful PNG upload with transparency."""
    response = client.post(
        "/api/v1/uploads",
        files={"file": ("transparent_logo.png", sample_png_bytes, "image/png")},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["content_type"] == "image/png"
    assert "thumbnail" in data["variants"]


def test_upload_single_webp_success(
    client: TestClient, sample_webp_bytes: bytes
) -> None:
    """Test successful WebP upload."""
    response = client.post(
        "/api/v1/uploads",
        files={"file": ("modern_banner.webp", sample_webp_bytes, "image/webp")},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["content_type"] == "image/webp"


def test_upload_invalid_extension(client: TestClient) -> None:
    """Test rejection of disallowed file extensions (e.g., .exe, .sh)."""
    response = client.post(
        "/api/v1/uploads",
        files={"file": ("danger.exe", b"binary content", "image/jpeg")},
    )
    assert response.status_code == 415
    assert "Unsupported file extension" in response.json()["message"]


def test_upload_disallowed_mime_type(
    client: TestClient, sample_jpeg_bytes: bytes
) -> None:
    """Test rejection when Content-Type header is not an allowed image MIME."""
    response = client.post(
        "/api/v1/uploads",
        files={"file": ("document.jpg", sample_jpeg_bytes, "application/pdf")},
    )
    assert response.status_code == 415
    assert (
        "Content-Type 'application/pdf' is not permitted" in response.json()["message"]
    )


def test_upload_empty_file(client: TestClient) -> None:
    """Test upload rejection on empty 0-byte file."""
    response = client.post(
        "/api/v1/uploads",
        files={"file": ("empty.jpg", b"", "image/jpeg")},
    )
    assert response.status_code == 415
    assert "empty" in response.json()["message"].lower()


def test_upload_corrupt_image(client: TestClient, corrupt_bytes: bytes) -> None:
    """Test upload rejection when file payload is corrupt."""
    response = client.post(
        "/api/v1/uploads",
        files={"file": ("broken.png", corrupt_bytes, "image/png")},
    )
    assert response.status_code == 415
    assert "cannot be decoded" in response.json()["message"].lower()


def test_upload_spoofed_magic_bytes(
    client: TestClient, fake_script_bytes: bytes
) -> None:
    """Test that text files masquerading as images fail magic-byte validation."""
    response = client.post(
        "/api/v1/uploads",
        files={"file": ("trojan.jpg", fake_script_bytes, "image/jpeg")},
    )
    assert response.status_code == 415


def test_upload_oversized_file(client: TestClient) -> None:
    """Test upload rejection when exceeding MAX_UPLOAD_SIZE_MB (set to 2MB in fixture)."""
    huge_payload = b"X" * (3 * 1024 * 1024)  # 3 MB
    response = client.post(
        "/api/v1/uploads",
        files={"file": ("huge.jpg", huge_payload, "image/jpeg")},
    )
    assert response.status_code == 413
    assert "exceeds maximum allowed size" in response.json()["message"].lower()


def test_batch_upload_files(
    client: TestClient, sample_jpeg_bytes: bytes, sample_png_bytes: bytes
) -> None:
    """Test batch file upload with multiple attachments."""
    files = [
        ("files", ("image1.jpg", sample_jpeg_bytes, "image/jpeg")),
        ("files", ("image2.png", sample_png_bytes, "image/png")),
        ("files", ("invalid.pdf", b"pdf data", "application/pdf")),
    ]
    response = client.post("/api/v1/uploads/batch", files=files)
    assert response.status_code == 200
    data = response.json()

    assert data["uploaded_count"] == 2
    assert data["failed_count"] == 1
    assert len(data["results"]) == 2
    assert len(data["errors"]) == 1
    assert data["errors"][0]["filename"] == "invalid.pdf"


def test_list_and_download_stored_files(
    client: TestClient, sample_jpeg_bytes: bytes
) -> None:
    """Test file listing and subsequent download."""
    upload_res = client.post(
        "/api/v1/uploads",
        files={"file": ("gallery_item.jpg", sample_jpeg_bytes, "image/jpeg")},
    )
    filename = upload_res.json()["filename"]

    # List files
    list_res = client.get("/api/v1/uploads")
    assert list_res.status_code == 200
    files = list_res.json()
    assert any(f["filename"] == filename for f in files)

    # Download original file
    dl_res = client.get(f"/api/v1/uploads/{filename}")
    assert dl_res.status_code == 200
    assert dl_res.content == sample_jpeg_bytes


def test_download_nonexistent_file(client: TestClient) -> None:
    """Test 404 error when downloading unknown file."""
    res = client.get("/api/v1/uploads/nonexistent_file_99.jpg")
    assert res.status_code == 404


def test_delete_uploaded_file(client: TestClient, sample_jpeg_bytes: bytes) -> None:
    """Test deleting uploaded file and verifying variant cleanup."""
    upload_res = client.post(
        "/api/v1/uploads",
        files={"file": ("to_delete.jpg", sample_jpeg_bytes, "image/jpeg")},
    )
    filename = upload_res.json()["filename"]

    # Delete
    del_res = client.delete(f"/api/v1/uploads/{filename}")
    assert del_res.status_code == 200
    del_data = del_res.json()
    assert del_data["success"] is True
    assert filename in del_data["deleted_variants"]

    # Verify no longer on disk
    assert not (settings.originals_dir / filename).exists()

    # Second delete returns 404
    del_again = client.delete(f"/api/v1/uploads/{filename}")
    assert del_again.status_code == 404


def test_security_path_traversal_detection() -> None:
    """Test is_safe_path prevents traversal outside root directory."""
    base = Path("/var/app/uploads")
    safe_child = Path("/var/app/uploads/originals/image.jpg")
    malicious = Path("/var/app/uploads/../../etc/passwd")

    assert is_safe_path(base, safe_child) is True
    assert is_safe_path(base, malicious) is False


def test_security_filename_sanitization() -> None:
    """Test filename sanitization strips dots, slashes, and spaces."""
    dirty = "....//....//hello world $#@!.png"
    clean = sanitize_filename(dirty, prefix_uuid=False)
    assert "/" not in clean
    assert "\\" not in clean
    assert " " not in clean
    assert clean.endswith(".png")
