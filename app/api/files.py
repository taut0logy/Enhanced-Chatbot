import os
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from ..services.file_service import FileService
from ..services.chat_service import chat_service

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/files", tags=["files"])

# Initialize file service with API key from environment
file_service = FileService(os.getenv("GOOGLE_API_KEY"))

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process a file (image or text)"""
    try:
        logger.info(f"Received file upload request: {file.filename}")
        
        # Process the file
        result = file_service.process_file(file.file, file.filename)
        logger.info("File processed successfully")
        
        # Process with chat service if needed
        if result["success"] and result.get("content"):
            ai_response = await chat_service.process_text_input(result["content"])
            result["ai_response"] = ai_response
        
        return result
        
    except ValueError as e:
        logger.error(f"File processing error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in file upload: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing the file"
        )

@router.post("/process-image")
async def process_image(image: UploadFile = File(...)):
    """Process an image file specifically"""
    try:
        logger.info(f"Received image processing request: {image.filename}")
        
        # Validate file type
        if not image.content_type.startswith('image/'):
            logger.error(f"Invalid file type: {image.content_type}")
            raise HTTPException(
                status_code=400,
                detail="File must be an image (JPEG, PNG, or BMP)"
            )
        
        # Validate file size (5MB limit for images)
        if await image.read(5 * 1024 * 1024 + 1):
            logger.error("Image size exceeds limit")
            raise HTTPException(
                status_code=400,
                detail="Image size exceeds the 5MB limit"
            )
        await image.seek(0)
        
        # Process the image
        result = file_service.process_file(image.file, image.filename)
        logger.info("Image processed successfully")
        return result
        
    except ValueError as e:
        logger.error(f"Image processing error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in image processing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing the image"
        ) 