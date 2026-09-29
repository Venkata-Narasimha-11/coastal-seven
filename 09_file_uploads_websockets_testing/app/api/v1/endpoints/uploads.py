"""File upload, retrieval, and management API endpoints."""

from typing import List

from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import FileResponse

from app.api.deps import get_file_service
from app.schemas.file import (
    BatchUploadResponse,
    FileDeleteResponse,
    FileUploadResponse,
    StoredFileInfo,
)
from app.services.file_service import FileService

router = APIRouter(prefix="/uploads", tags=["File Uploads"])


@router.post(
    "",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and process a single media file",
)
async def upload_single_file(
    file: UploadFile = File(
        ..., description="Image file to upload (JPEG, PNG, WebP, GIF)"
    ),
    service: FileService = Depends(get_file_service),
) -> FileUploadResponse:
    """Upload a single image file, validate magic bytes and size, and generate thumbnails."""
    return await service.save_upload_file(file, generate_image_variants=True)


@router.post(
    "/batch",
    response_model=BatchUploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload multiple files in batch",
)
async def upload_multiple_files(
    files: List[UploadFile] = File(..., description="Multiple image files to upload"),
    service: FileService = Depends(get_file_service),
) -> BatchUploadResponse:
    """Upload multiple files in batch, isolating individual upload failures."""
    success_results: List[FileUploadResponse] = []
    failure_errors: List[dict] = []

    for upload_file in files:
        raw_name = upload_file.filename or "unknown"
        try:
            result = await service.save_upload_file(
                upload_file, generate_image_variants=True
            )
            success_results.append(result)
        except Exception as exc:
            failure_errors.append({"filename": raw_name, "error": str(exc)})

    return BatchUploadResponse(
        uploaded_count=len(success_results),
        failed_count=len(failure_errors),
        results=success_results,
        errors=failure_errors,
    )


@router.get(
    "",
    response_model=List[StoredFileInfo],
    summary="List all uploaded media files",
)
def list_uploaded_files(
    service: FileService = Depends(get_file_service),
) -> List[StoredFileInfo]:
    """Retrieve metadata and thumbnail URLs for all stored media files."""
    return service.list_stored_files()


@router.get(
    "/{filename}",
    summary="Download or stream an original stored file",
)
def download_file(
    filename: str,
    service: FileService = Depends(get_file_service),
) -> FileResponse:
    """Download an uploaded file by its sanitized server filename."""
    file_path = service.get_file_path(filename)
    return FileResponse(path=file_path, filename=filename)


@router.delete(
    "/{filename}",
    response_model=FileDeleteResponse,
    summary="Delete an uploaded file and all its variants",
)
def delete_file(
    filename: str,
    service: FileService = Depends(get_file_service),
) -> FileDeleteResponse:
    """Delete an uploaded original file and all associated generated variants."""
    return service.delete_file(filename)
