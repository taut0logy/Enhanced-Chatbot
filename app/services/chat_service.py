import logging
from typing import Dict, Optional
import google.generativeai as genai
from app.core.config import settings
from app.services.cache_service import cache_service
from app.services.content_service import content_service
import speech_recognition as sr
import io
from pydub import AudioSegment
import os
import tempfile

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.cache = cache_service
        self.recognizer = sr.Recognizer()

    def _get_model_config(self, model_name: str) -> Dict:
        """Get the configuration for the specified model."""
        return settings.MODEL_CONFIGS.get(model_name, settings.MODEL_CONFIGS[settings.DEFAULT_MODEL])

    async def process_text_input(self, text: str, user_id: str, model_name: Optional[str] = None) -> Dict:
        """Process text input using the specified model."""
        try:
            # Use default model if none specified
            model_name = model_name or settings.DEFAULT_MODEL
            if model_name not in settings.AVAILABLE_MODELS:
                model_name = settings.DEFAULT_MODEL

            # Configure model
            model = genai.GenerativeModel(
                model_name=model_name,
            )

            # Generate response
            response = model.generate_content(text)
            
            # Cache the response
            cache_key = f"chat:{user_id}:{text}"
            await self.cache.set(cache_key, response.text)

            # Save to database
            await content_service.save_content(
                user_id=user_id,
                content_type="CHAT",
                title=text[:50] + "...",  # Use first 50 chars of query as title
                content=response.text,
                metadata={
                    "query": text,
                    "model": model_name
                }
            )

            return {
                "text": response.text,
                "model": model_name,
            }

        except Exception as e:
            logger.error(f"Error processing text input: {str(e)}")
            raise

    async def process_voice_input(self, audio_data: bytes, user_id: str, model_name: Optional[str] = None) -> Dict:
        """Process voice input using the specified model."""
        try:
            # Use default model if none specified
            model_name = model_name or settings.VOICE_MODEL
            if model_name not in settings.AVAILABLE_VOICE_MODELS:
                model_name = settings.VOICE_MODEL

            # Convert WebM to WAV
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format="webm")
            wav_io = io.BytesIO()
            audio_segment.export(wav_io, format="wav")
            wav_io.seek(0)
            
            # Create AudioFile from WAV bytes
            with sr.AudioFile(wav_io) as source:
                audio = self.recognizer.record(source)
                
            try:
                # Perform speech recognition
                transcribed_text = self.recognizer.recognize_google(audio)
                logger.info(f"Transcribed text: {transcribed_text}")
                
                # Now process the text with Gemini
                model = genai.GenerativeModel(model_name=model_name)
                gemini_response = model.generate_content(transcribed_text)
                
                # Cache the response
                cache_key = f"voice:{user_id}:{hash(str(audio_data))}"
                await self.cache.set(cache_key, gemini_response.text)

                # Save to database
                await content_service.save_content(
                    user_id=user_id,
                    content_type="VOICE",
                    title=transcribed_text[:50] + "...",  # Use first 50 chars of transcription as title
                    content=gemini_response.text,
                    metadata={
                        "transcription": transcribed_text,
                        "model": model_name
                    }
                )

                return {
                    "text": gemini_response.text,
                    "model": model_name,
                    "transcription": transcribed_text
                }
                
            except sr.UnknownValueError:
                return {
                    "text": "I couldn't understand the audio. Please try speaking more clearly.",
                    "model": model_name,
                    "transcription": None
                }
            except sr.RequestError as e:
                logger.error(f"Speech recognition request error: {str(e)}")
                raise Exception("Speech recognition service is unavailable")

        except Exception as e:
            logger.error(f"Error processing voice input: {str(e)}")
            raise
        
    async def text_to_speech(self, text: str) -> bytes:
        """Convert text response to speech"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                self.engine.save_to_file(text, temp_audio.name)
                self.engine.runAndWait()
                
                with open(temp_audio.name, 'rb') as audio_file:
                    audio_data = audio_file.read()
                os.unlink(temp_audio.name)
                return audio_data
        except Exception as e:
            raise Exception(f"Text-to-speech conversion failed: {str(e)}")

chat_service = ChatService() 