"""Integrated endpoints demonstrating File Uploads + Image Processing + WebSockets."""

import time
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from app.api.deps import get_connection_manager, get_file_service
from app.core.config import settings
from app.schemas.file import FileUploadResponse
from app.schemas.websocket import WebSocketEventType, WebSocketMessage
from app.services.file_service import FileService, format_size
from app.services.websocket_manager import ConnectionManager

router = APIRouter(prefix="/integrated", tags=["Final Integration"])
SERVER_START_TIME = time.time()


@router.post(
    "/upload-notify",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload image, process thumbnail/medium variants, and broadcast live WebSocket notification",
)
async def upload_and_notify(
    file: UploadFile = File(..., description="Image to upload and process"),
    uploader_name: Optional[str] = Form(default="Anonymous User"),
    file_service: FileService = Depends(get_file_service),
    ws_manager: ConnectionManager = Depends(get_connection_manager),
) -> FileUploadResponse:
    """Uploads file, validates formats, generates Pillow thumbnails, and broadcasts live WebSocket event."""
    start_time = time.perf_counter()

    # 1. Save and process image variants
    upload_result = await file_service.save_upload_file(
        file, generate_image_variants=True
    )
    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

    # 2. Extract variant information for the live notification
    thumb_url = (
        upload_result.variants["thumbnail"].url
        if "thumbnail" in upload_result.variants
        else upload_result.url
    )
    medium_url = (
        upload_result.variants["medium"].url
        if "medium" in upload_result.variants
        else upload_result.url
    )

    # 3. Broadcast real-time WebSocket event to all connected clients
    notification_event = WebSocketMessage(
        event=WebSocketEventType.FILE_UPLOADED,
        sender_id="media_pipeline",
        channel="uploads",
        data={
            "filename": upload_result.filename,
            "original_name": upload_result.original_name,
            "content_type": upload_result.content_type,
            "file_size_human": upload_result.file_size_human,
            "file_size_bytes": upload_result.file_size_bytes,
            "checksum_sha256": upload_result.checksum_sha256,
            "url": upload_result.url,
            "thumbnail_url": thumb_url,
            "medium_url": medium_url,
            "uploader": uploader_name,
            "processing_time_ms": duration_ms,
            "message": f"New image '{upload_result.original_name}' uploaded and processed!",
        },
    )

    # Broadcast to uploads channel and general broadcast channel
    await ws_manager.broadcast_to_channel("uploads", notification_event)
    await ws_manager.broadcast(notification_event)

    return upload_result


@router.get(
    "/hub-status",
    summary="Get integrated hub metrics, storage stats, and WebSocket status",
)
def get_hub_status(
    file_service: FileService = Depends(get_file_service),
    ws_manager: ConnectionManager = Depends(get_connection_manager),
) -> Dict[str, Any]:
    """Provide real-time telemetry of stored files, storage disk usage, and active WebSockets."""
    stored_files = file_service.list_stored_files()
    total_bytes = sum(f.size_bytes for f in stored_files)
    uptime_seconds = int(time.time() - SERVER_START_TIME)

    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "uptime_seconds": uptime_seconds,
        "active_websocket_connections": ws_manager.connection_count,
        "total_files_stored": len(stored_files),
        "total_disk_usage": format_size(total_bytes),
        "total_disk_bytes": total_bytes,
        "image_presets": {
            "thumbnail": f"{settings.THUMBNAIL_MAX_WIDTH}x{settings.THUMBNAIL_MAX_HEIGHT}",
            "medium": f"{settings.MEDIUM_MAX_WIDTH}x{settings.MEDIUM_MAX_HEIGHT}",
            "default_output_format": settings.DEFAULT_OUTPUT_FORMAT,
            "quality": settings.IMAGE_QUALITY,
        },
    }
