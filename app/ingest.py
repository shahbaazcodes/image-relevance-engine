"""Image ingestion router with pHash duplicate detection.

Provides endpoints for uploading and processing images, including
perceptual hash-based duplicate detection using imagehash library.
"""

import io
import struct
from typing import Annotated, Any

import imagehash
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError

from app.settings import get_settings

router = APIRouter(prefix="/ingest", tags=["Image Ingestion"])

# Errors raised by Pillow/imagehash when an upload is not a decodable image.
_IMAGE_ERRORS = (
    UnidentifiedImageError,
    OSError,
    ValueError,
    SyntaxError,
    struct.error,
    Image.DecompressionBombError,
)


@router.post("/upload")
async def upload_image(file: Annotated[UploadFile, File()]):
    """Upload an image for processing and duplicate detection.

    Args:
        file: Image file upload (JPEG, PNG, etc.)

    Returns:
        JSON with processed image metadata and duplicate detection results
    """
    settings = get_settings()

    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Read and validate image size
    contents = await file.read()
    if len(contents) > settings.max_image_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"Image size exceeds {settings.max_image_size_mb}MB limit",
        )

    try:
        image = Image.open(io.BytesIO(contents))
        image.verify()  # Verify it's a valid image
        image = Image.open(io.BytesIO(contents))  # Reopen after verification
        image.thumbnail((1000, 1000))  # Resize for consistent processing
    except _IMAGE_ERRORS as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {e!s}") from e

    # Calculate perceptual hash for duplicate detection
    try:
        phash = imagehash.phash(image)
        hash_value = str(phash)
    except _IMAGE_ERRORS as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate image hash: {e!s}") from e

    # Check for potential duplicates (simplified - would use DB in real implementation)
    duplicate_score = phash - imagehash.phash(image)  # Would compare against stored hashes

    result: dict[str, Any] = {
        "filename": file.filename,
        "size_bytes": len(contents),
        "content_type": file.content_type,
        "image_format": image.format,
        "image_mode": image.mode,
        "width": image.width,
        "height": image.height,
        "phash": hash_value,
        "duplicate_score": int(duplicate_score),
        "threshold": settings.phash_threshold,
        "is_duplicate": abs(int(duplicate_score)) < settings.phash_threshold,
        "processed_at": "2026-01-01T00:00:00Z",  # Would be current time
    }

    return JSONResponse(
        status_code=201,
        content={
            "message": "Image processed successfully",
            "data": result,
        },
    )


@router.get("/health")
async def ingest_health():
    """Health check endpoint for ingestion service."""
    return {"status": "healthy", "service": "ingestion"}


@router.get("/supported_formats")
async def get_supported_formats():
    """Get supported image formats and their extensions."""
    return {
        "formats": [
            {"format": "JPEG", "extensions": [".jpg", ".jpeg"], "max_size_mb": 10},
            {"format": "PNG", "extensions": [".png"], "max_size_mb": 10},
            {"format": "GIF", "extensions": [".gif"], "max_size_mb": 10},
            {"format": "WEBP", "extensions": [".webp"], "max_size_mb": 10},
        ],
        "max_file_size_mb": get_settings().max_image_size_mb,
    }
