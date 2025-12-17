from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from rag_backend.db.pg_client import init_db

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Physical AI & Humanoid Robotics RAG API",
    description="API for RAG chatbot, authentication, and personalization services",
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
    return {"message": "Physical AI & Humanoid Robotics RAG API"}

@app.get("/api/v1/status")
def health_check():
    return {"status": "healthy", "service": "rag-backend"}

# Include API routes
from rag_backend.api.v1.query import router as query_router
from rag_backend.api.v1.ingest import router as ingest_router
from rag_backend.api.v1.auth import router as auth_router
from rag_backend.api.v1.personalize import router as personalize_router
from rag_backend.api.v1.translate import router as translate_router
from rag_backend.api.v1.agents import router as agents_router

# Better-Auth integration
try:
    from better_auth import auth
    from better_auth.fastapi import get_better_auth_fastapi_app
    from rag_backend.auth.config import better_auth

    # Create Better-Auth FastAPI app
    better_auth_app = get_better_auth_fastapi_app(better_auth)

    # Mount Better-Auth app under /api/auth
    app.mount("/api/auth", better_auth_app)
except ImportError:
    print("Better-Auth not installed, using mock auth routes")
    # Fallback to existing auth routes
    from api.v1.auth import router as auth_router
    app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
else:
    # Include other API routes
    app.include_router(query_router, prefix="/api/v1", tags=["query"])
    app.include_router(ingest_router, prefix="/api/v1", tags=["ingest"])
    app.include_router(personalize_router, prefix="/api/v1", tags=["personalize"])
    app.include_router(translate_router, prefix="/api/v1", tags=["translate"])
    app.include_router(agents_router, prefix="/api/v1", tags=["agents"])

# Context7 MCP Server Integration
@app.post("/context7/webhook")
async def context7_webhook():
    """
    Webhook endpoint for Context7 MCP server to notify about content updates
    """
    # This endpoint would receive notifications from the Context7 MCP server
    # about new content that needs to be ingested into the RAG system
    return {"status": "received", "message": "Context7 webhook received"}

@app.get("/context7/health")
async def context7_health():
    """
    Health check endpoint for Context7 MCP server integration
    """
    return {"status": "healthy", "service": "context7-integration"}

@app.on_event("startup")
async def startup_event():
    await init_db()
    print("RAG Chatbot API started successfully")
    print("Context7 MCP Server integration ready")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))