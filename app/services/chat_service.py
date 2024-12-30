import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
from typing import Optional, Dict, Any
import io
import tempfile
import os
import subprocess
import shutil

class ChatService:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-flash-latest")
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        
    async def process_text_input(self, text: str) -> Dict[str, Any]:
        """Process text input and return AI response"""
        try:
            response = self.model.generate_content(text)
            return {
                "success": True,
                "response": response.text,
                "type": "text"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "text"
            }

    async def process_voice_input(self, audio_file: io.BytesIO) -> Dict[str, Any]:
        """Convert voice to text and process with AI"""
        try:
            # Save temporary WebM file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_webm:
                temp_webm.write(audio_file.read())
                webm_path = temp_webm.name

            # Convert WebM to WAV using ffmpeg
            wav_path = webm_path.replace(".webm", ".wav")
            try:
                # Check if ffmpeg is available
                if not shutil.which("ffmpeg"):
                    raise Exception("FFmpeg is not installed. Please install FFmpeg to process audio.")
                
                subprocess.run([
                    'ffmpeg', '-i', webm_path,
                    '-acodec', 'pcm_s16le',
                    '-ar', '16000',
                    '-ac', '1',
                    '-y', wav_path
                ], check=True, capture_output=True)

                # Convert speech to text
                with sr.AudioFile(wav_path) as source:
                    audio_data = self.recognizer.record(source)
                    text = self.recognizer.recognize_google(audio_data)

                # Process text with AI
                response = await self.process_text_input(text)
                
                return {
                    "success": True,
                    "text_input": text,
                    "response": response["response"],
                    "type": "voice"
                }
            finally:
                # Clean up temporary files
                try:
                    os.unlink(webm_path)
                    os.unlink(wav_path)
                except:
                    pass

        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to convert audio: {e.stderr.decode()}",
                "type": "voice"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "voice"
            }

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