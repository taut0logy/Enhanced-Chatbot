import logging
import os
from typing import Dict, Any, BinaryIO
import easyocr
from PIL import Image
import google.generativeai as genai
import io
import numpy as np

# Configure logging
logger = logging.getLogger(__name__)

class FileService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash-latest")
        # Initialize EasyOCR reader for English
        self.reader = easyocr.Reader(['en'])
        logger.info("File Service initialized successfully")

    def process_file(self, file: BinaryIO, filename: str) -> Dict[str, Any]:
        """Process uploaded file and generate AI response."""
        try:
            logger.info(f"Processing file: {filename}")
            
            # Get file extension
            file_ext = os.path.splitext(filename)[1].lower()
            logger.info(f"File extension: {file_ext}")

            # Read file content based on type
            if file_ext in ['.jpg', '.jpeg', '.png', '.bmp']:
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
            response = self._generate_ai_response(content)

            return {
                "success": True,
                "content": content,
                "ai_response": response
            }

        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            raise ValueError(str(e))

    def _process_image(self, file: BinaryIO) -> str:
        """Extract text from image using EasyOCR."""
        try:
            logger.info("Starting OCR process")
            
            # Read image data
            image_data = file.read()
            
            # Convert to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
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

        except Exception as e:
            error_msg = f"Failed to process image: {str(e)}"
            logger.error(f"Error in OCR process: {str(e)}")
            raise ValueError(error_msg)

    def _process_text_file(self, file: BinaryIO) -> str:
        """Extract text from text-based files."""
        try:
            logger.info("Reading text file content")
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

    def _generate_ai_response(self, content: str) -> Dict[str, Any]:
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
            
            response = self.model.generate_content(prompt)
            
            if not response.text:
                error_msg = "AI model returned empty response"
                logger.warning(error_msg)
                raise ValueError(error_msg)
            
            logger.info(f"Successfully generated AI response: {response.text[:100]}...")
            return {
                "success": True,
                "response": response.text
            }

        except Exception as e:
            error_msg = f"Failed to generate AI response: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg) 