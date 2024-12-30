from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import StreamingResponse
from typing import Optional
from pydantic import BaseModel
import io
from ..services.chat_service import chat_service

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatMessage(BaseModel):
    message: str

@router.post("/text")
async def chat_text(message: ChatMessage):
    """
    Process text input and return AI response
    """
    response = await chat_service.process_text_input(message.message)
    if not response["success"]:
        raise HTTPException(status_code=500, detail=response["error"])
    return response

@router.post("/voice")
async def chat_voice(audio: UploadFile = File(...)):
    """
    Process voice input and return AI response
    """
    try:
        # Read the audio file into memory
        audio_bytes = io.BytesIO(await audio.read())
        
        # Process the audio
        response = await chat_service.process_voice_input(audio_bytes)
        
        if not response["success"]:
            raise HTTPException(status_code=500, detail=response["error"])
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/text-to-speech")
async def text_to_speech(text: str):
    """
    Convert text to speech
    """
    try:
        audio_data = await chat_service.text_to_speech(text)
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/mp3",
            headers={"Content-Disposition": "attachment; filename=response.mp3"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 