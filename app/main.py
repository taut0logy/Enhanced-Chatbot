from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import google.generativeai as genai
import os
from dotenv import load_dotenv

from .api import chat, files, pdf

# Load environment variables
load_dotenv()

# Initialize Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = FastAPI(
    title="Enhanced AI Chatbot",
    description="An AI-powered chatbot with voice, image, and PDF generation capabilities",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(files.router)
app.include_router(pdf.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Enhanced AI Chatbot API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Error handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 