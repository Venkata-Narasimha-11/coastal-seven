"""File upload management and persistence service.

Handles validation, streaming chunk persistence, SHA-256 integrity,
magic-byte verification, and file lifecycle management.
"""

import hashlib
from pathlib import Path
from typing import Dict, List, Tuple

from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import (
    FileNotFoundAppError,
    FileTooLargeError,
    FileValidationError,
)
from app.core.security import (
    detect_mime_from_magic_bytes,
    is_safe_path,
    sanitize_filename,
)
from app.schemas.file import (
    FileDeleteResponse,
    FileUploadResponse,
    ImageVariant,
    StoredFileInfo,
)
from app.services.image_service import image_service


def format_size(size_bytes: int) -> str:
    """Format bytes into human-readable string (KB, MB, GB)."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}" if unit != "B" else f"{size_bytes} {unit}"
        size_bytes = int(size_bytes / 1024.0)
    return f"{size_bytes:.1f} TB"


class FileService:
    """Service managing uploaded file operations and integrity."""

    CHUNK_SIZE = 64 * 1024  # 64 KB read buffer

    def __init__(self) -> None:
        settings.ensure_directories()

    def _validate_headers(
        self, raw_name: str, extension: str, header_mime: str
    ) -> None:
        """Validate filename extension and declared content-type."""
        if extension not in settings.ALLOWED_EXTENSIONS:
            raise FileValidationError(
                message=f"Unsupported file extension '{extension}'. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}",
                details={"filename": raw_name, "extension": extension},
            )

        if header_mime not in settings.ALLOWED_IMAGE_TYPES:
            raise FileValidationError(
                message=f"Content-Type '{header_mime}' is not permitted.",
                details={"allowed": settings.ALLOWED_IMAGE_TYPES},
            )

    async def _stream_to_disk(
        self, upload_file: UploadFile, destination_path: Path
    ) -> Tuple[int, str]:
        """Stream chunks from upload file to disk while enforcing limits and magic bytes."""
        hasher = hashlib.sha256()
        total_bytes = 0
        first_chunk = True

        try:
            with open(destination_path, "wb") as buffer:
                while True:
                    chunk = await upload_file.read(self.CHUNK_SIZE)
                    if not chunk:
                        break

                    total_bytes += len(chunk)
                    if total_bytes > settings.max_upload_size_bytes:
                        buffer.close()
                        if destination_path.exists():
                            destination_path.unlink()
                        raise FileTooLargeError(
                            message=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB} MB.",
                            details={"max_bytes": settings.max_upload_size_bytes},
                        )

                    if first_chunk:
                        first_chunk = False
                        detected_mime = detect_mime_from_magic_bytes(chunk)
                        if (
                            detected_mime
                            and detected_mime not in settings.ALLOWED_IMAGE_TYPES
                        ):
                            buffer.close()
                            if destination_path.exists():
                                destination_path.unlink()
                            raise FileValidationError(
                                message=f"File content magic bytes detected as '{detected_mime}', which is not allowed.",
                                details={"detected_mime": detected_mime},
                            )

                    hasher.update(chunk)
                    buffer.write(chunk)
        finally:
            await upload_file.close()

        if total_bytes == 0:
            if destination_path.exists():
                destination_path.unlink()
            raise FileValidationError(message="Uploaded file is empty (0 bytes).")

        return total_bytes, hasher.hexdigest()

    def _generate_image_variants(
        self, destination_path: Path, sanitized_name: str, total_bytes: int
    ) -> Dict[str, ImageVariant]:
        """Generate thumbnail and medium image variants."""
        with open(destination_path, "rb") as f:
            img_bytes = f.read()
        fmt, size, _ = image_service.verify_image(img_bytes)

        variants: Dict[str, ImageVariant] = {
            "original": ImageVariant(
                variant_type="original",
                url=f"/static/uploads/originals/{sanitized_name}",
                width=size[0],
                height=size[1],
                file_size_bytes=total_bytes,
                format=fmt,
            )
        }

        generated = image_service.generate_variants(
            original_path=destination_path,
            base_filename=sanitized_name,
        )
        for var_key, var_val in generated.items():
            variants[var_key] = ImageVariant(
                variant_type=var_key,
                url=str(var_val["url"]),
                width=int(var_val["width"]),  # type: ignore
                height=int(var_val["height"]),  # type: ignore
                file_size_bytes=int(var_val["file_size_bytes"]),  # type: ignore
                format=str(var_val["format"]),
            )
        return variants

    async def save_upload_file(
        self,
        upload_file: UploadFile,
        generate_image_variants: bool = True,
    ) -> FileUploadResponse:
        """Validate, stream-save, hash, and optionally generate image thumbnails."""
        raw_name = upload_file.filename or "upload.bin"
        extension = Path(raw_name).suffix.lower()
        header_mime = upload_file.content_type or "application/octet-stream"

        self._validate_headers(raw_name, extension, header_mime)

        sanitized_name = sanitize_filename(raw_name, prefix_uuid=True)
        destination_path = settings.originals_dir / sanitized_name

        total_bytes, checksum = await self._stream_to_disk(
            upload_file, destination_path
        )

        variants_dict: Dict[str, ImageVariant] = {}
        if generate_image_variants and extension in settings.ALLOWED_EXTENSIONS:
            variants_dict = self._generate_image_variants(
                destination_path, sanitized_name, total_bytes
            )

        return FileUploadResponse(
            success=True,
            filename=sanitized_name,
            original_name=raw_name,
            content_type=header_mime,
            file_size_bytes=total_bytes,
            file_size_human=format_size(total_bytes),
            url=f"/static/uploads/originals/{sanitized_name}",
            variants=variants_dict,
            checksum_sha256=checksum,
        )

    def list_stored_files(self) -> List[StoredFileInfo]:
        """List all stored original files and their thumbnails."""
        files: List[StoredFileInfo] = []
        if not settings.originals_dir.exists():
            return files

        for file_path in sorted(
            settings.originals_dir.iterdir(),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        ):
            if file_path.is_file():
                stat = file_path.stat()
                stem = file_path.stem
                thumb_candidates = list(settings.thumbnails_dir.glob(f"{stem}_thumb.*"))
                thumb_url = (
                    f"/static/uploads/thumbnails/{thumb_candidates[0].name}"
                    if thumb_candidates
                    else None
                )
                ext = file_path.suffix.lower()
                mime = (
                    "image/jpeg"
                    if ext in [".jpg", ".jpeg"]
                    else f"image/{ext.replace('.', '')}"
                )

                files.append(
                    StoredFileInfo(
                        filename=file_path.name,
                        size_bytes=stat.st_size,
                        size_human=format_size(stat.st_size),
                        content_type=mime,
                        url=f"/static/uploads/originals/{file_path.name}",
                        thumbnail_url=thumb_url,
                        created_at=str(stat.st_ctime),
                    )
                )
        return files

    def get_file_path(self, filename: str) -> Path:
        """Safely retrieve original file path, checking traversal security."""
        target = settings.originals_dir / filename
        if not is_safe_path(settings.originals_dir, target) or not target.exists():
            raise FileNotFoundAppError(
                message=f"File '{filename}' does not exist on server.",
                details={"filename": filename},
            )
        return target

    def delete_file(self, filename: str) -> FileDeleteResponse:
        """Delete an uploaded file and all its associated variants."""
        target = self.get_file_path(filename)
        deleted: List[str] = []

        if target.exists():
            target.unlink()
            deleted.append(filename)

        stem = Path(filename).stem
        for variant_file in settings.thumbnails_dir.glob(f"{stem}_*"):
            if variant_file.is_file():
                variant_file.unlink()
                deleted.append(variant_file.name)

        return FileDeleteResponse(
            success=True,
            filename=filename,
            deleted_variants=deleted,
            message=f"File {filename} and {len(deleted) - 1} generated variants deleted.",
        )


file_service = FileService()
