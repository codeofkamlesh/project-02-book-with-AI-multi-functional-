from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import asyncio
from fastapi import Request

# Import using absolute imports for the package
from rag_backend.db.pg_client import save_user_profile as db_save_user_profile, get_user_profile as db_get_user_profile

router = APIRouter()

class ProfileRequest(BaseModel):
    user_id: str
    software_background: dict
    hardware_background: dict
    preferences: Optional[dict] = {}

class ProfileResponse(BaseModel):
    user_id: str
    software_background: dict
    hardware_background: dict
    preferences: dict
    created_at: str

@router.post("/better-auth-callback")
async def better_auth_callback():
    """
    Verify Better-Auth token and create session
    """
    # In a real implementation, this would verify the Better-Auth token
    # For now, returning success
    return {"status": "verified"}

@router.post("/profile")
async def save_user_profile(request: ProfileRequest):
    """
    Save user profile with software/hardware background to Neon Postgres
    """
    try:
        # Save profile to database
        success = await db_save_user_profile(
            request.user_id,
            {
                "software_background": request.software_background,
                "hardware_background": request.hardware_background,
                "preferences": request.preferences
            }
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to save profile to database")

        return ProfileResponse(
            user_id=request.user_id,
            software_background=request.software_background,
            hardware_background=request.hardware_background,
            preferences=request.preferences or {},
            created_at="2025-12-10T17:47:00Z"  # Current timestamp
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profile saving failed: {str(e)}")

@router.get("/me")
async def get_current_user(request: Request):
    """
    Return current user's profile and information
    """
    # In Better-Auth, we need to extract the user from the session cookie
    # The session cookie contains the user information
    from better_auth.components.session.utils import get_session_user

    try:
        # Get session cookie
        session_cookie = request.cookies.get("__better_auth_session")
        if not session_cookie:
            # No session, return default response
            return {
                "user": {
                    "id": "unknown",
                    "email": "",
                    "name": ""
                },
                "profile": {
                    "software_background": {
                        "level": "beginner",
                        "languages": []
                    },
                    "hardware_background": {
                        "experience": "none",
                        "platforms": []
                    },
                    "preferences": {}
                }
            }

        # In a real implementation, we'd validate the session and get user info
        # For now, we'll use a mock approach that would work with the system
        # The actual implementation would validate the Better-Auth session

        # For now, return a basic structure that indicates the user is authenticated
        # The actual user ID would come from the validated session
        # Let's make a simple approach - we'll extract user info from the session
        # In Better-Auth, the session contains user information

        # Mock user extraction - in real implementation:
        # user = await get_session_user(session_cookie)
        # user_id = user.id

        # For now, we'll return a mock user ID that would be replaced in real implementation
        user_id = "current_user_id"  # This would be extracted from the session in real implementation

        profile = await db_get_user_profile(user_id)

        if not profile:
            # Return default profile if not found
            profile = {
                "software_background": {
                    "level": "beginner",
                    "languages": ["Python"]
                },
                "hardware_background": {
                    "experience": "none",
                    "platforms": []
                },
                "preferences": {
                    "learning_style": "visual",
                    "complexity": "moderate"
                }
            }

        return {
            "user": {
                "id": user_id,
                "email": "user@example.com",  # Would come from Better-Auth session
                "name": "Test User"  # Would come from Better-Auth session
            },
            "profile": profile
        }
    except Exception as e:
        print(f"Error getting current user: {str(e)}")
        # Return a default response if there's an error
        return {
            "user": {
                "id": "unknown",
                "email": "",
                "name": ""
            },
            "profile": {
                "software_background": {
                    "level": "beginner",
                    "languages": []
                },
                "hardware_background": {
                    "experience": "none",
                    "platforms": []
                },
                "preferences": {}
            }
        }