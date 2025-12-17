from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ...agents.openai_agent_integration import OpenAIAgent
from ...db.pg_client import get_translation, save_translation

router = APIRouter()

class TranslateRequest(BaseModel):
    text: str
    targetLang: str = "ur"  # Default to Urdu, following the command specification

class TranslateResponse(BaseModel):
    translatedText: str  # Following the command specification

@router.post("/translate", response_model=TranslateResponse)
async def translate_endpoint(request: TranslateRequest):
    """
    Translate English text to target language (currently supports Urdu only)
    Following the command specification: accepts { text: string, targetLang: "ur" } and returns { translatedText: string }
    """
    try:
        # For now, we'll use a simple hash of the text as a document identifier for caching
        import hashlib
        doc_path = hashlib.md5(request.text.encode()).hexdigest()

        # Check if translation is already cached
        try:
            cached_translation = await get_translation(doc_path, request.targetLang)

            if cached_translation:
                translated_text = cached_translation
            else:
                # Use the OpenAI agent to translate the content
                agent = OpenAIAgent()
                translated_text = await agent.translate_to_urdu(request.text)

                # Cache the translation (only if database is available)
                try:
                    await save_translation(doc_path, request.targetLang, translated_text)
                except Exception as cache_error:
                    # If caching fails, still return the translation
                    print(f"Warning: Could not cache translation: {str(cache_error)}")

        except Exception as db_error:
            # If database operations fail, still attempt translation
            print(f"Database error (proceeding with translation): {str(db_error)}")
            agent = OpenAIAgent()
            translated_text = await agent.translate_to_urdu(request.text)

        return TranslateResponse(
            translatedText=translated_text
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

# Backward compatibility endpoint for Urdu translation
@router.post("/translate/urdu", response_model=TranslateResponse)
async def translate_to_urdu_endpoint(request: TranslateRequest):
    """
    Translate English text to Urdu (backward compatibility)
    """
    # Override target language to Urdu for this endpoint
    request.targetLang = "ur"
    return await translate_endpoint(request)