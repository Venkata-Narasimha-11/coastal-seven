"""Security utilities for file uploads and path operations.

Provides filename sanitization, directory traversal prevention,
and magic-number signature verification for MIME sniffing defense.
"""

import os
import re
import uuid
from pathlib import Path
from typing import Optional

# Known image magic bytes signatures
IMAGE_SIGNATURES = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"GIF87a": "image/gif",
    b"GIF89a": "image/gif",
}


def sanitize_filename(original_name: str, prefix_uuid: bool = True) -> str:
    """Sanitize an untrusted user-supplied filename.

    - Removes path components (directory traversal defense).
    - Replaces whitespace and non-alphanumeric characters.
    - Optionally prepends a UUID4 hex prefix to ensure uniqueness and prevent collisions.
    """
    basename = os.path.basename(original_name).strip()
    # Separate stem and extension
    path_obj = Path(basename)
    ext = path_obj.suffix.lower()
    raw_stem = path_obj.stem

    # Clean characters in stem: keep alphanumeric, dashes, and underscores
    clean_stem = re.sub(r"[^a-zA-Z0-9_\-]", "_", raw_stem)
    if not clean_stem:
        clean_stem = "upload"

    # Truncate clean_stem if overly long
    clean_stem = clean_stem[:64]

    if prefix_uuid:
        unique_prefix = uuid.uuid4().hex[:12]
        return f"{unique_prefix}_{clean_stem}{ext}"
    return f"{clean_stem}{ext}"


def detect_mime_from_magic_bytes(header: bytes) -> Optional[str]:
    """Inspect the first bytes of a file to verify true MIME type from file signatures.

    Defends against malicious files disguised with valid extensions.
    """
    if len(header) < 12:
        return None

    # Check direct prefix signatures (JPEG, PNG, GIF)
    for signature, mime in IMAGE_SIGNATURES.items():
        if header.startswith(signature):
            return mime

    # Check WebP signature: bytes 0-3 == 'RIFF' and bytes 8-11 == 'WEBP'
    if header.startswith(b"RIFF") and header[8:12] == b"WEBP":
        return "image/webp"

    return None


def is_safe_path(base_directory: Path, target_path: Path) -> bool:
    """Validate that target_path resolves strictly inside base_directory.

    Prevents directory traversal (e.g., ../../../etc/passwd).
    """
    try:
        resolved_base = base_directory.resolve()
        resolved_target = target_path.resolve()
        return (
            resolved_base == resolved_target or resolved_base in resolved_target.parents
        )
    except Exception:
        return False
