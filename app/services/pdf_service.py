import json
import logging
import os
from datetime import datetime
from fpdf import FPDF
import google.generativeai as genai
from typing import Dict, Any

logger = logging.getLogger(__name__)

class UTF8PDF(FPDF):
    def __init__(self):
        super().__init__()
        # Use Arial which has better Unicode support
        self.add_font('Arial Unicode MS', '', 'arial.ttf', uni=True)
        self.add_font('Arial Unicode MS', 'B', 'arialbd.ttf', uni=True)

class PDFService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash-latest")
        self.storage_dir = "storage/pdfs"
        os.makedirs(self.storage_dir, exist_ok=True)
        logger.info("PDF Service initialized successfully")

    def generate_story_content(self, prompt: str) -> Dict[str, Any]:
        """Generate story content using the AI model."""
        try:
            logger.info(f"Generating story content for prompt: {prompt}")
            
            # Create a structured prompt for the AI
            structured_prompt = f"""
            Create a children's story based on this prompt: {prompt}
            Format the response as a JSON object with the following structure:
            {{
                "title": "Story Title",
                "pages": [
                    {{
                        "text": "Page text content",
                        "image_prompt": "Description for generating an illustration"
                    }}
                ]
            }}
            The story should be 5 pages long.
            """

            # Get response from AI model
            response = self.model.generate_content(structured_prompt)
            
            # Extract the text content
            response_text = response.text
            
            # Find the JSON part of the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON object found in response")
                
            json_str = response_text[start_idx:end_idx]
            
            # Parse the JSON
            try:
                story_data = json.loads(json_str)
                logger.info("Successfully generated and parsed story content")
                return story_data
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {str(e)}\nText being parsed: {json_str}")
                raise ValueError(f"Invalid JSON format: {str(e)}")

        except Exception as e:
            logger.error(f"Failed to generate story content: {str(e)}")
            raise ValueError(f"Failed to generate story content: {str(e)}")

    def create_pdf(self, story_data: Dict[str, Any]) -> str:
        """Create a PDF file from the story data."""
        try:
            title = story_data.get('title', 'Untitled Story')
            pages = story_data.get('pages', [])
            
            # Create PDF with Unicode support
            pdf = FPDF()
            pdf.add_page()
            
            # Set font for title (using standard Arial for better compatibility)
            pdf.set_font("Arial", "B", 24)
            # Encode text to handle Unicode
            title_encoded = title.encode('latin-1', 'replace').decode('latin-1')
            pdf.cell(0, 20, title_encoded, ln=True, align='C')
            
            # Add story pages
            pdf.set_font("Arial", "", 12)
            for page in pages:
                pdf.add_page()
                text = page.get('text', '')
                # Encode text to handle Unicode
                text_encoded = text.encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 10, text_encoded)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_title = ''.join(c for c in title if c.isalnum() or c in (' ', '_'))
            filename = f"story_{safe_title.replace(' ', '_')}_{timestamp}.pdf"
            filepath = os.path.join(self.storage_dir, filename)
            
            # Save PDF
            pdf.output(filepath)
            logger.info(f"PDF created successfully: {filepath}")
            
            return {
                "file_id": filename,
                "title": title,
                "download_url": f"/pdf/download/{filename}"
            }

        except Exception as e:
            logger.error(f"Failed to create PDF: {str(e)}")
            raise ValueError(f"Failed to create PDF: {str(e)}")

    def generate_story_pdf(self, prompt: str) -> Dict[str, Any]:
        """Generate a story and create a PDF."""
        try:
            logger.info("Starting story PDF generation process")
            story_data = self.generate_story_content(prompt)
            pdf_info = self.create_pdf(story_data)
            return {
                "success": True,
                "message": "PDF generated successfully",
                "data": pdf_info
            }
        except Exception as e:
            logger.error(f"Failed to generate story PDF: {str(e)}")
            raise ValueError(f"Failed to generate story PDF: {str(e)}")

    def get_pdf_path(self, file_id: str) -> str:
        """Get the full path of a PDF file."""
        filepath = os.path.join(self.storage_dir, file_id)
        if not os.path.exists(filepath):
            raise ValueError("PDF file not found")
        return filepath 