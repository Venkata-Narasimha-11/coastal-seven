"""Pydantic schemas for file uploads, image processing, and media management."""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ImageVariant(BaseModel):
    """Details for a specific processed image variant (thumbnail, medium, etc.)."""

    variant_type: str = Field(
        ..., description="Variant type: original, thumbnail, medium"
    )
    url: str = Field(..., description="Relative or absolute URL path to access variant")
    width: int = Field(..., description="Width in pixels")
    height: int = Field(..., description="Height in pixels")
    file_size_bytes: int = Field(..., description="File size in bytes")
    format: str = Field(..., description="Image format (WEBP, JPEG, PNG)")


class FileUploadResponse(BaseModel):
    """Schema returned upon successful file upload and processing."""

    success: bool = True
    filename: str = Field(..., description="Sanitized unique filename on disk")
    original_name: str = Field(..., description="Original client-provided filename")
    content_type: str = Field(..., description="MIME content type")
    file_size_bytes: int = Field(..., description="Total size in bytes")
    file_size_human: str = Field(
        ..., description="Human-readable size format (e.g., 2.4 MB)"
    )
    url: str = Field(..., description="Direct URL to access the uploaded file")
    variants: Dict[str, ImageVariant] = Field(
        default_factory=dict,
        description="Resized variants generated for images",
    )
    uploaded_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z",
        description="Timestamp of upload",
    )
    checksum_sha256: str = Field(
        ..., description="SHA-256 hash for integrity verification"
    )


class BatchUploadResponse(BaseModel):
    """Schema for multiple concurrent file uploads."""

    uploaded_count: int
    failed_count: int
    results: List[FileUploadResponse]
    errors: List[Dict[str, str]]


class StoredFileInfo(BaseModel):
    """Metadata schema for an already stored file."""

    filename: str
    original_name: Optional[str] = None
    size_bytes: int
    size_human: str
    content_type: str
    url: str
    thumbnail_url: Optional[str] = None
    created_at: str


class FileDeleteResponse(BaseModel):
    """Schema for file deletion response."""

    success: bool
    filename: str
    deleted_variants: List[str]
    message: str
