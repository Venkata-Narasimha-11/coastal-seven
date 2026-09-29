"""Image processing service using Pillow.

Provides image verification, aspect-ratio preserving resizing,
thumbnail generation, EXIF metadata stripping, and format optimization.
"""

import io
from pathlib import Path
from typing import Dict, Optional, Tuple

from PIL import Image, ImageOps

from app.core.config import settings
from app.core.exceptions import FileValidationError


class ImageService:
    """Handles image validation, transforms, thumbnails, and conversions."""

    @staticmethod
    def verify_image(image_bytes: bytes) -> Tuple[str, Tuple[int, int], str]:
        """Validate raw image bytes using Pillow.

        Returns tuple of (format, (width, height), mode).
        Raises FileValidationError if image is corrupt or unreadable.
        """
        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                img.verify()
            # Image.open again because verify() leaves file in unusable state
            with Image.open(io.BytesIO(image_bytes)) as img:
                return (img.format or "UNKNOWN", img.size, img.mode)
        except Exception as exc:
            raise FileValidationError(
                message="File payload cannot be decoded as a valid image.",
                details={"pillow_error": str(exc)},
            )

    @staticmethod
    def strip_exif_and_normalize(image: Image.Image) -> Image.Image:
        """Strip EXIF metadata for user privacy and auto-orient based on EXIF orientation."""
        try:
            # Auto-orient if image has orientation tags
            image = ImageOps.exif_transpose(image)
        except Exception:
            pass

        # Create clean copy without EXIF tags
        clean_img = Image.new(image.mode, image.size)
        clean_img.paste(image)
        return clean_img

    @staticmethod
    def resize_preserving_aspect_ratio(
        image: Image.Image, max_width: int, max_height: int
    ) -> Image.Image:
        """Resize image down preserving aspect ratio using high-quality LANCZOS filter.

        Never upscales images smaller than target boundaries.
        """
        orig_width, orig_height = image.size
        if orig_width <= max_width and orig_height <= max_height:
            return image.copy()

        # Calculate target bounding box maintaining aspect ratio
        ratio = min(max_width / orig_width, max_height / orig_height)
        new_width = max(1, int(orig_width * ratio))
        new_height = max(1, int(orig_height * ratio))

        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    @classmethod
    def generate_variants(
        cls,
        original_path: Path,
        base_filename: str,
        output_format: Optional[str] = None,
    ) -> Dict[str, Dict[str, object]]:
        """Generate thumbnail and medium-size variants from original image on disk.

        Saves variants into settings.thumbnails_dir.
        """
        fmt = (output_format or settings.DEFAULT_OUTPUT_FORMAT).upper()
        stem = Path(base_filename).stem
        ext = f".{fmt.lower()}"

        results: Dict[str, Dict[str, object]] = {}

        try:
            with Image.open(original_path) as raw_img:
                clean_img = cls.strip_exif_and_normalize(raw_img)

                # Prepare image mode for formats like JPEG (which doesn't support RGBA)
                if fmt in ["JPEG", "JPG"] and clean_img.mode in ("RGBA", "P"):
                    clean_img = clean_img.convert("RGB")

                # 1. Medium Variant
                medium_img = cls.resize_preserving_aspect_ratio(
                    clean_img,
                    settings.MEDIUM_MAX_WIDTH,
                    settings.MEDIUM_MAX_HEIGHT,
                )
                medium_filename = f"{stem}_medium{ext}"
                medium_path = settings.thumbnails_dir / medium_filename
                medium_img.save(
                    medium_path,
                    format=fmt,
                    quality=settings.IMAGE_QUALITY,
                    optimize=True,
                )
                results["medium"] = {
                    "filename": medium_filename,
                    "path": str(medium_path),
                    "url": f"/static/uploads/thumbnails/{medium_filename}",
                    "width": medium_img.width,
                    "height": medium_img.height,
                    "file_size_bytes": medium_path.stat().st_size,
                    "format": fmt,
                }

                # 2. Thumbnail Variant
                thumb_img = cls.resize_preserving_aspect_ratio(
                    clean_img,
                    settings.THUMBNAIL_MAX_WIDTH,
                    settings.THUMBNAIL_MAX_HEIGHT,
                )
                thumb_filename = f"{stem}_thumb{ext}"
                thumb_path = settings.thumbnails_dir / thumb_filename
                thumb_img.save(
                    thumb_path,
                    format=fmt,
                    quality=settings.IMAGE_QUALITY,
                    optimize=True,
                )
                results["thumbnail"] = {
                    "filename": thumb_filename,
                    "path": str(thumb_path),
                    "url": f"/static/uploads/thumbnails/{thumb_filename}",
                    "width": thumb_img.width,
                    "height": thumb_img.height,
                    "file_size_bytes": thumb_path.stat().st_size,
                    "format": fmt,
                }

        except Exception as exc:
            raise FileValidationError(
                message=f"Failed to process image variants: {str(exc)}",
                details={"file": str(original_path)},
            )

        return results


image_service = ImageService()
