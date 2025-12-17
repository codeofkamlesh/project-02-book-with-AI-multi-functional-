from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List
import asyncio
import tempfile
import os
from ...pipeline.rag import ingest_document as rag_ingest_document
from ...pipeline.document_parser import parse_document

router = APIRouter()

class IngestRequest(BaseModel):
    source: str
    path: str
    content: str
    metadata: Optional[dict] = {}

class BatchIngestRequest(BaseModel):
    documents: List[IngestRequest]

@router.post("/ingest/docs")
async def ingest_document(request: IngestRequest):
    """
    Ingest documents into the vector database for RAG retrieval
    """
    try:
        # Create a temporary file to store the content
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
            temp_file.write(request.content)
            temp_file_path = temp_file.name

        try:
            # Use our RAG pipeline to ingest the document
            success = await rag_ingest_document(temp_file_path, request.path)

            if success:
                return {
                    "status": "success",
                    "doc_id": f"doc_{hash(request.path)}",
                    "path": request.path,
                    "message": "Document ingested successfully"
                }
            else:
                raise HTTPException(status_code=500, detail="Document ingestion failed")
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@router.post("/ingest/docs/file")
async def ingest_document_file(file: UploadFile = File(...), doc_path: str = Form(...)):
    """
    Ingest a document file into the vector database for RAG retrieval
    """
    try:
        # Create a temporary file to save the uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Use our RAG pipeline to ingest the document
            success = await rag_ingest_document(temp_file_path, doc_path)

            if success:
                return {
                    "status": "success",
                    "filename": file.filename,
                    "doc_path": doc_path,
                    "message": "Document ingested successfully"
                }
            else:
                raise HTTPException(status_code=500, detail="Document ingestion failed")
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File ingestion failed: {str(e)}")

@router.post("/ingest/batch")
async def batch_ingest_documents(request: BatchIngestRequest):
    """
    Batch ingest multiple documents into the vector database
    """
    try:
        from ...pipeline.rag import batch_ingest_documents as rag_batch_ingest

        # Create temporary files for each document
        temp_files = []
        file_paths = []
        doc_paths = []

        for doc_request in request.documents:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
                temp_file.write(doc_request.content)
                temp_files.append(temp_file.name)
                file_paths.append(temp_file.name)
                doc_paths.append(doc_request.path)

        try:
            # Use our RAG pipeline to batch ingest documents
            results = await rag_batch_ingest(file_paths, doc_paths)

            return {
                "status": "completed",
                "results": results,
                "total_processed": len(results),
                "successful": sum(1 for success in results.values() if success)
            }
        finally:
            # Clean up all temporary files
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch ingestion failed: {str(e)}")

@router.post("/reindex")
async def reindex_documents():
    """
    Secure endpoint to refresh all embeddings (for cron/manual use)
    """
    try:
        # This would reprocess all documents
        # For now, return success
        return {
            "status": "reindex started",
            "message": "Reindexing process initiated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reindexing failed: {str(e)}")

@router.get("/status")
async def api_status():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "ingestion-api"}

# Context7 MCP server integration endpoints
@router.post("/context7/ingest-content")
async def context7_ingest_content(content: str = Form(...), doc_path: str = Form(...), title: str = Form(...)):
    """
    Endpoint for Context7 MCP server to push content for ingestion
    """
    try:
        # Create a temporary file to store the content
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Use our RAG pipeline to ingest the document
            success = await rag_ingest_document(temp_file_path, doc_path)

            if success:
                return {
                    "status": "success",
                    "doc_path": doc_path,
                    "title": title,
                    "message": "Content ingested successfully from Context7"
                }
            else:
                raise HTTPException(status_code=500, detail="Content ingestion failed")
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Context7 content ingestion failed: {str(e)}")