"""Unit tests for Pillow image processing and thumbnail generation."""

from pathlib import Path

import pytest
from PIL import Image

from app.core.config import settings
from app.core.exceptions import FileValidationError
from app.services.image_service import ImageService, image_service


def test_verify_valid_jpeg(sample_jpeg_bytes: bytes) -> None:
    """Test image verification successfully parses format, dimensions, and mode."""
    fmt, size, mode = image_service.verify_image(sample_jpeg_bytes)
    assert fmt == "JPEG"
    assert size == (400, 300)
    assert mode == "RGB"


def test_verify_valid_png(sample_png_bytes: bytes) -> None:
    """Test PNG verification parses dimensions and RGBA mode."""
    fmt, size, mode = image_service.verify_image(sample_png_bytes)
    assert fmt == "PNG"
    assert size == (250, 250)
    assert mode == "RGBA"


def test_verify_corrupt_image_raises_validation_error(corrupt_bytes: bytes) -> None:
    """Test corrupted bytes raise FileValidationError."""
    with pytest.raises(FileValidationError) as exc_info:
        image_service.verify_image(corrupt_bytes)
    assert "cannot be decoded" in str(exc_info.value.message)


def test_resize_landscape_preserves_aspect_ratio() -> None:
    """Test aspect-ratio preservation when width > height."""
    img = Image.new("RGB", (1000, 500))  # 2:1 aspect ratio
    resized = ImageService.resize_preserving_aspect_ratio(
        img, max_width=200, max_height=200
    )

    assert resized.width == 200
    assert resized.height == 100
    assert resized.width / resized.height == pytest.approx(2.0, rel=1e-2)


def test_resize_portrait_preserves_aspect_ratio() -> None:
    """Test aspect-ratio preservation when height > width."""
    img = Image.new("RGB", (600, 1200))  # 1:2 aspect ratio
    resized = ImageService.resize_preserving_aspect_ratio(
        img, max_width=300, max_height=300
    )

    assert resized.height == 300
    assert resized.width == 150
    assert resized.height / resized.width == pytest.approx(2.0, rel=1e-2)


def test_resize_does_not_upscale_small_images() -> None:
    """Test images smaller than max constraints are preserved without upscaling."""
    img = Image.new("RGB", (80, 60))
    resized = ImageService.resize_preserving_aspect_ratio(
        img, max_width=200, max_height=200
    )

    assert resized.size == (80, 60)


def test_generate_variants_creates_files_on_disk(tmp_path: Path) -> None:
    """Test generate_variants produces valid thumbnail and medium images on disk."""
    # Create original test image on disk
    orig_path = tmp_path / "original_test.png"
    img = Image.new("RGBA", (1200, 800), color=(100, 150, 200, 255))
    img.save(orig_path, format="PNG")

    variants = image_service.generate_variants(
        original_path=orig_path,
        base_filename="original_test.png",
        output_format="WEBP",
    )

    assert "medium" in variants
    assert "thumbnail" in variants

    # Check medium variant
    med = variants["medium"]
    assert Path(str(med["path"])).exists()
    assert int(med["width"]) <= settings.MEDIUM_MAX_WIDTH  # type: ignore
    assert int(med["height"]) <= settings.MEDIUM_MAX_HEIGHT  # type: ignore

    # Check thumbnail variant
    thumb = variants["thumbnail"]
    assert Path(str(thumb["path"])).exists()
    assert int(thumb["width"]) <= settings.THUMBNAIL_MAX_WIDTH  # type: ignore
    assert int(thumb["height"]) <= settings.THUMBNAIL_MAX_HEIGHT  # type: ignore


def test_strip_exif_and_normalize() -> None:
    """Test EXIF normalization creates a clean Image instance."""
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    clean = ImageService.strip_exif_and_normalize(img)

    assert clean.size == (100, 100)
    assert clean.mode == "RGB"
