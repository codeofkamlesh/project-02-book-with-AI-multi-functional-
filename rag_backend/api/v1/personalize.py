from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import os
from ...pipeline.rag import RAGPipeline
from ...agents.openai_agent_integration import OpenAIAgent
from ...db.pg_client import get_personalized_content, save_personalized_content, get_user_profile

router = APIRouter()

class PersonalizeRequest(BaseModel):
    doc_path: str
    profile: Optional[Dict[str, Any]] = None
    mode: str = "simpler"  # Options: "simpler", "advanced", "visual", "code-heavy"
    content: Optional[str] = None  # Content can be provided directly or fetched from doc_path

class PersonalizeResponse(BaseModel):
    original_doc_path: str
    mode: str
    personalized_content: str
    timestamp: datetime

@router.post("/personalize/render", response_model=PersonalizeResponse)
async def personalize_content_endpoint(request: PersonalizeRequest):
    """
    Personalize chapter content based on user profile and requested mode
    """
    try:
        # Get user profile if not provided (in a real implementation, this would come from auth)
        user_profile = request.profile
        if not user_profile and request.doc_path:  # If no profile provided, try to get from db
            # Extract user_id from auth context in real implementation
            user_profile = {"software_background": {"level": "intermediate"}, "hardware_background": {"experience": "basic robotics"}}

        # Get original content if not provided
        original_content = request.content
        if not original_content:
            # In a real implementation, this would fetch the content from the document path
            # For now, we'll use a placeholder
            original_content = f"Original content for {request.doc_path}. This would be the actual chapter content from the Docusaurus docs."

        # Check if personalized content is already cached
        user_id = "12345"  # This would come from auth context in real implementation
        cached_content = await get_personalized_content(user_id, request.doc_path, request.mode)

        if cached_content:
            return PersonalizeResponse(
                original_doc_path=request.doc_path,
                mode=request.mode,
                personalized_content=cached_content,
                timestamp=datetime.now()
            )

        # Use the OpenAI agent to personalize the content
        agent = OpenAIAgent()
        personalized_content = await agent.personalize_content(
            original_content,
            user_profile or {"software_background": {"level": "intermediate"}, "hardware_background": {"experience": "basic robotics"}},
            request.mode
        )

        # Cache the personalized content
        await save_personalized_content(user_id, request.doc_path, request.mode, personalized_content)

        return PersonalizeResponse(
            original_doc_path=request.doc_path,
            mode=request.mode,
            personalized_content=personalized_content,
            timestamp=datetime.now()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Personalization failed: {str(e)}")

# Include this router in the main app
# This would be added to main.py: app.include_router(personalize_router, prefix="/api/v1", tags=["personalize"])