from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from rag_backend.api.v1.translate import router as translate_router

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Physical AI & Humanoid Robotics Translation API",
    description="Minimal API for Urdu translation service",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Translation API is running"}

@app.get("/api/v1/status")
def health_check():
    return {"status": "healthy", "service": "translation-api"}

# Include only the translation API routes
app.include_router(translate_router, prefix="/api/v1", tags=["translate"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))