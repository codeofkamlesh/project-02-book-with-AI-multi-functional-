"""
API endpoints for the RAG Chatbot system.
Handles query processing, document ingestion, and chat session management.
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging
from ...agents.rag_agent import query_with_rag
from ...pipeline.rag import ingest_document, batch_ingest_documents, delete_document
from ...db.pg_client import get_user_profile, create_session, get_session, update_session, save_message, get_session_messages
from ...db.models.chat_session import ChatSession
from ...db.models.message import Message
import uuid
from datetime import datetime


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/v1", tags=["query"])


# Request/Response models
class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    doc_path_filter: Optional[str] = None
    selected_text: Optional[str] = None
    limit: int = 5


class QueryResponse(BaseModel):
    session_id: str
    response: str
    sources: List[Dict[str, Any]]
    query: str
    context_used: str


class IngestDocumentRequest(BaseModel):
    file_path: str
    doc_path: str


class IngestDocumentResponse(BaseModel):
    success: bool
    message: str


class ChatSessionRequest(BaseModel):
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}


class ChatSessionResponse(BaseModel):
    session_id: str
    created_at: datetime


# API endpoints
@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a user query using the RAG system
    """
    try:
        # Create or validate session
        session_id = request.session_id or str(uuid.uuid4())

        # If it's a new session, create it in the database
        if not request.session_id:
            session_data = {
                "session_id": session_id,
                "user_id": request.user_id or "anonymous",
                "created_at": datetime.now(),
                "last_active": datetime.now(),
                "metadata": request.doc_path_filter or {}
            }
            await create_session(session_data)
        else:
            # Update last active time for existing session
            await update_session(session_id, {
                "last_active": datetime.now(),
                "metadata": {"last_query_time": datetime.now().isoformat()}
            })

        # Get user profile if user_id is provided
        user_profile = None
        if request.user_id:
            user_profile = await get_user_profile(request.user_id)

        # Process query through RAG system
        result = await query_with_rag(
            query=request.query,
            doc_path_filter=request.doc_path_filter,
            user_profile=user_profile,
            selected_text=request.selected_text,
            limit=request.limit
        )

        if result.get('error'):
            raise HTTPException(status_code=500, detail=result['error'])

        # Save the query and response as messages
        query_message = {
            "message_id": str(uuid.uuid4()),
            "session_id": session_id,
            "role": "user",
            "content": request.query,
            "timestamp": datetime.now(),
            "context": {
                "selected_text": request.selected_text,
                "doc_path_filter": request.doc_path_filter
            },
            "sources": []
        }

        response_message = {
            "message_id": str(uuid.uuid4()),
            "session_id": session_id,
            "role": "assistant",
            "content": result['response'],
            "timestamp": datetime.now(),
            "context": {
                "sources": result.get('sources', []),
                "model_used": result.get('model_used', 'gpt-4o-mini')
            },
            "sources": result.get('sources', [])
        }

        # Save both messages to the database
        await save_message(query_message)
        await save_message(response_message)

        # Prepare response
        response = QueryResponse(
            session_id=session_id,
            response=result['response'],
            sources=result.get('sources', []),
            query=request.query,
            context_used=result.get('context_used', '')
        )

        logger.info(f"Query processed successfully for session {session_id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.post("/ingest", response_model=IngestDocumentResponse)
async def ingest_document_endpoint(request: IngestDocumentRequest):
    """
    Ingest a document into the RAG system
    """
    try:
        success = await ingest_document(request.file_path, request.doc_path)

        if success:
            logger.info(f"Document {request.file_path} ingested successfully")
            return IngestDocumentResponse(
                success=True,
                message=f"Document {request.file_path} ingested successfully"
            )
        else:
            logger.warning(f"Failed to ingest document {request.file_path}")
            return IngestDocumentResponse(
                success=False,
                message=f"Failed to ingest document {request.file_path}"
            )

    except Exception as e:
        logger.error(f"Error ingesting document {request.file_path}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error ingesting document: {str(e)}")


@router.post("/batch-ingest", response_model=Dict[str, bool])
async def batch_ingest_documents_endpoint(file_paths: List[str], doc_paths: List[str]):
    """
    Ingest multiple documents into the RAG system
    """
    try:
        results = await batch_ingest_documents(file_paths, doc_paths)
        logger.info(f"Batch ingestion completed for {len(results)} documents")
        return results
    except Exception as e:
        logger.error(f"Error in batch ingestion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in batch ingestion: {str(e)}")


@router.delete("/documents/{doc_path}")
async def delete_document_endpoint(doc_path: str):
    """
    Delete a document from the RAG system
    """
    try:
        success = await delete_document(doc_path)

        if success:
            logger.info(f"Document {doc_path} deleted successfully")
            return {"success": True, "message": f"Document {doc_path} deleted successfully"}
        else:
            logger.warning(f"Document {doc_path} not found or could not be deleted")
            return {"success": False, "message": f"Document {doc_path} not found or could not be deleted"}

    except Exception as e:
        logger.error(f"Error deleting document {doc_path}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(request: ChatSessionRequest):
    """
    Create a new chat session
    """
    try:
        session_id = str(uuid.uuid4())
        session_data = {
            "session_id": session_id,
            "user_id": request.user_id or "anonymous",
            "created_at": datetime.now(),
            "last_active": datetime.now(),
            "metadata": request.metadata
        }

        created_session_id = await create_session(session_data)

        response = ChatSessionResponse(
            session_id=created_session_id,
            created_at=datetime.now()
        )

        logger.info(f"Chat session {session_id} created successfully")
        return response

    except Exception as e:
        logger.error(f"Error creating chat session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating chat session: {str(e)}")


@router.get("/sessions/{session_id}", response_model=ChatSession)
async def get_chat_session(session_id: str):
    """
    Get a specific chat session
    """
    try:
        session = await get_session(session_id)

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Convert to ChatSession model (assuming it matches the structure)
        return ChatSession(
            id=session["session_id"],
            user_id=session["user_id"],
            created_at=session["created_at"],
            last_active=session["last_active"],
            metadata=session["metadata"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting chat session: {str(e)}")


@router.get("/sessions/{session_id}/messages", response_model=List[Message])
async def get_session_messages(session_id: str):
    """
    Get all messages for a specific session
    """
    try:
        messages = await get_session_messages(session_id)

        # Convert to Message models
        message_models = []
        for msg in messages:
            message_models.append(Message(
                session_id=msg["session_id"],
                role=msg["role"],
                content=msg["content"],
                timestamp=msg["timestamp"],
                context=msg["context"],
                sources=msg["sources"]
            ))

        logger.info(f"Retrieved {len(message_models)} messages for session {session_id}")
        return message_models

    except Exception as e:
        logger.error(f"Error getting messages for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting session messages: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "RAG Chatbot API"}


# Example usage and testing endpoints
@router.get("/debug/test-query")
async def test_query():
    """
    Test endpoint for debugging query functionality
    """
    try:
        # This is just for testing - in a real implementation, you'd want to be more careful
        result = await query_with_rag("What is Physical AI?", limit=3)
        return {
            "query": "What is Physical AI?",
            "response": result.get('response', 'No response generated'),
            "sources_count": len(result.get('sources', [])),
            "model_used": result.get('model_used', 'unknown')
        }
    except Exception as e:
        return {"error": str(e)}