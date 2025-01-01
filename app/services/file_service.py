import logging
from typing import Dict, Optional, Any, BinaryIO
import google.generativeai as genai
from PIL import Image
import numpy as np
import easyocr
from app.core.config import settings
from app.services.cache_service import cache_service
from app.services.content_service import content_service
import io
import os



logger = logging.getLogger(__name__)

class FileService:
    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.reader = easyocr.Reader(['en'])
        self.cache = cache_service
        logger.info("FileService initialized")

    def _process_image(self, file: BinaryIO) -> str:
        """Extract text from image using EasyOCR."""
        try:
            logger.info("Starting OCR process")
            
            # Ensure we're at the start of the file
            file.seek(0)
            
            # Read image data
            image_data = file.read()
            
            try:
                # Create BytesIO object and write image data
                image_io = io.BytesIO(image_data)
                image_io.seek(0)  # Reset position to start
                
                # Open with PIL
                image = Image.open(image_io)
                
                # Convert to RGB if necessary
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Convert to numpy array for EasyOCR
                image_np = np.array(image)
                
                # Perform OCR
                results = self.reader.readtext(image_np)
                
                # Extract text from results
                text = ' '.join([result[1] for result in results])
                
                if not text.strip():
                    logger.warning("No text extracted from image")
                    return "No text could be extracted from the image."
                
                logger.info(f"Successfully extracted text from image: {text[:100]}...")
                return text
                
            except Exception as img_error:
                logger.error(f"Error processing image data: {str(img_error)}")
                raise ValueError(f"Failed to process image data: {str(img_error)}")
                
        except Exception as e:
            error_msg = f"Failed to process image: {str(e)}"
            logger.error(f"Error in OCR process: {str(e)}")
            raise ValueError(error_msg)

    def _process_text_file(self, file: BinaryIO) -> str:
        """Extract text from text-based files."""
        try:
            logger.info("Reading text file content")
            # Ensure we're at the start of the file
            file.seek(0)
            content = file.read().decode('utf-8')
            
            if not content.strip():
                error_msg = "The file is empty"
                logger.warning(error_msg)
                raise ValueError(error_msg)
            
            logger.info(f"Successfully read text file: {content[:100]}...")
            return content

        except UnicodeDecodeError as e:
            error_msg = "File encoding not supported. Please ensure the file is in UTF-8 format."
            logger.error(f"Unicode decode error: {str(e)}")
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Failed to read text file: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def _generate_ai_response(self, content: str, model_name: Optional[str] = None) -> str:
        """Generate AI response for the file content."""
        try:
            logger.info("Generating AI response for content")
            
            prompt = f"""
            Analyze the following content and provide a detailed response:
            {content}
            
            Please include:
            1. A summary of the main points
            2. Key insights or observations
            3. Any relevant recommendations
            """
            
            model_name = model_name or settings.DEFAULT_MODEL
            if model_name not in settings.AVAILABLE_MODELS:
                model_name = settings.DEFAULT_MODEL

            # Configure model
            model = genai.GenerativeModel(
                model_name=model_name,
            )
            
            response = model.generate_content(prompt)
            
            if not response.text:
                error_msg = "AI model returned empty response"
                logger.warning(error_msg)
                raise ValueError(error_msg)
            
            logger.info(f"Successfully generated AI response: {response.text[:100]}...")
            return response.text

        except Exception as e:
            error_msg = f"Failed to generate AI response: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    async def process_file(self, file: BinaryIO, filename: str, user_id: str, model_name: Optional[str] = None) -> Dict[str, Any]:
        """Process file based on its type."""
        try:
            file_ext = os.path.splitext(filename)[1].lower()
            logger.info(f"Processing file: {filename} with extension: {file_ext}")

            # Read file content based on type
            if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.webp']:
                logger.info("Processing image file")
                content = self._process_image(file)
            elif file_ext in ['.txt', '.doc', '.docx', '.pdf']:
                logger.info("Processing text file")
                content = self._process_text_file(file)
            else:
                error_msg = f"Unsupported file type: {file_ext}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            if not content or not content.strip():
                error_msg = "No content could be extracted from the file"
                logger.error(error_msg)
                raise ValueError(error_msg)

            logger.info("Generating AI response")
            response = self._generate_ai_response(content, model_name)

            # Save to database
            await content_service.save_content(
                user_id=user_id,
                content_type="FILE",
                title=filename,
                content=response,
                filename=filename,
                metadata={
                    "original_content": content,
                    "file_type": file_ext,
                    "model": model_name
                }
            )

            return {
                "content": content,
                "model": model_name,
                "text": response
            }

        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            raise ValueError(str(e))

file_service = FileService()