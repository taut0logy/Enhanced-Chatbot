# AI-Powered Enhanced Chatbot Platform

An advanced chatbot platform that extends beyond traditional text-based interactions, featuring voice commands, image processing, and PDF generation capabilities.

## Features

- Text and Voice-based Chat Interface
- File Upload Support (Images & Text)
- OCR for Image Text Extraction
- Kids' Storybook Generation
- PDF Generation and Management
- Voice-to-Text and Text-to-Speech
- Google Gemini AI Integration
- PDF Sharing Platform

## Tech Stack

- Backend: FastAPI (Python)
- Frontend: React
- Database: SQLite
- AI: Google Gemini API
- Storage: Local File System
- OCR: EasyOCR
- PDF Generation: FPDF

## Setup Instructions

1. Clone the repository
2. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:

   ```bash
   cp .env.example .env
   # Add your Google Gemini API key to .env
   ```

4. Run the backend:

   ```bash
   uvicorn app.main:app --reload
   ```

5. Install frontend dependencies:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Project Structure

```text
├── app/
│   ├── main.py
│   ├── api/
│   ├── core/
│   ├── models/
│   └── services/
├── frontend/
│   ├── src/
│   └── public/
├── requirements.txt
└── README.md
```
