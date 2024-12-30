import os
import logging
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from ..services.pdf_service import PDFService

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/pdf", tags=["pdf"])

# Initialize PDF service with API key from environment
pdf_service = PDFService(os.getenv("GOOGLE_API_KEY"))

class StoryPrompt(BaseModel):
    prompt: str

@router.post("/generate-story")
async def generate_story(prompt: StoryPrompt):
    """Generate a story PDF from a prompt."""
    try:
        logger.info(f"Received story generation request with prompt: {prompt.prompt}")
        result = pdf_service.generate_story_pdf(prompt.prompt)
        return result
    except ValueError as e:
        logger.error(f"Failed to generate story PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in generate_story: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.get("/download/{file_id}")
async def download_pdf(file_id: str):
    """Download a generated PDF file."""
    try:
        file_path = pdf_service.get_pdf_path(file_id)
        return FileResponse(
            file_path,
            media_type="application/pdf",
            filename=file_id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error downloading PDF: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to download PDF") 