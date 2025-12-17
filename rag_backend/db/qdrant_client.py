"""
Qdrant client for vector database operations in the RAG Chatbot system.
Handles document chunk storage and retrieval for RAG functionality.
"""
import os
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams
import uuid


class QdrantManager:
    """
    Qdrant client for vector operations
    """

    def __init__(self):
        self.client = None
        self.collection_name = "textbook_chunks"

    async def initialize(self):
        """
        Initialize the Qdrant client
        """
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")

        if not qdrant_url:
            raise ValueError("QDRANT_URL environment variable is required")

        # Initialize Qdrant client
        if qdrant_api_key:
            self.client = QdrantClient(
                url=qdrant_url,
                api_key=qdrant_api_key,
                timeout=10
            )
        else:
            self.client = QdrantClient(
                url=qdrant_url,
                timeout=10
            )

        # Create collection if it doesn't exist
        await self._ensure_collection_exists()

    async def _ensure_collection_exists(self):
        """
        Ensure the textbook chunks collection exists
        """
        try:
            # Check if collection exists
            self.client.get_collection(self.collection_name)
        except:
            # Create collection with 1536 dimensions for OpenAI embeddings
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            )

            # Create payload index for faster filtering
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="doc_path",
                field_schema=models.PayloadSchemaType.KEYWORD
            )

    async def store_chunk(self, content: str, doc_path: str, heading: Optional[str] = None,
                         section: Optional[str] = None, metadata: Optional[Dict] = None) -> str:
        """
        Store a document chunk in Qdrant
        """
        if not self.client:
            await self.initialize()

        # Generate a unique ID for the chunk
        chunk_id = str(uuid.uuid4())

        # Create embedding using a placeholder - in real implementation this would call OpenAI
        # For now, we'll just store the content with empty vector (actual embedding happens elsewhere)
        # This is just a structure placeholder

        points = [
            models.PointStruct(
                id=chunk_id,
                vector=[0.0] * 1536,  # Placeholder - actual embedding would be here
                payload={
                    "content": content,
                    "doc_path": doc_path,
                    "heading": heading or "",
                    "section": section or "",
                    "metadata": metadata or {}
                }
            )
        ]

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

        return chunk_id

    async def retrieve_similar_chunks(self, query_embedding: List[float], doc_path_filter: Optional[str] = None,
                                    limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve similar document chunks based on query embedding
        """
        if not self.client:
            await self.initialize()

        # Build filter conditions
        filters = []
        if doc_path_filter:
            filters.append(models.FieldCondition(
                key="doc_path",
                match=models.MatchValue(value=doc_path_filter)
            ))

        # Create filter if any conditions exist
        search_filter = None
        if filters:
            search_filter = models.Filter(
                must=filters
            )

        # Search for similar vectors
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=search_filter,
            limit=limit,
            with_payload=True
        )

        # Format results
        chunks = []
        for result in results:
            chunks.append({
                "id": result.id,
                "content": result.payload["content"],
                "doc_path": result.payload["doc_path"],
                "heading": result.payload["heading"],
                "section": result.payload["section"],
                "metadata": result.payload["metadata"],
                "similarity_score": result.score
            })

        return chunks

    async def batch_store_chunks(self, chunks: List[Dict[str, Any]]) -> List[str]:
        """
        Store multiple document chunks in Qdrant
        """
        if not self.client:
            await self.initialize()

        point_structs = []
        chunk_ids = []

        for chunk_data in chunks:
            chunk_id = str(uuid.uuid4())
            chunk_ids.append(chunk_id)

            point = models.PointStruct(
                id=chunk_id,
                vector=chunk_data.get("embedding", [0.0] * 1536),  # Placeholder
                payload={
                    "content": chunk_data["content"],
                    "doc_path": chunk_data.get("doc_path", ""),
                    "heading": chunk_data.get("heading", ""),
                    "section": chunk_data.get("section", ""),
                    "metadata": chunk_data.get("metadata", {})
                }
            )
            point_structs.append(point)

        self.client.upsert(
            collection_name=self.collection_name,
            points=point_structs
        )

        return chunk_ids

    async def delete_chunks_by_path(self, doc_path: str) -> bool:
        """
        Delete all chunks associated with a specific document path
        """
        if not self.client:
            await self.initialize()

        # Create filter to find points with matching doc_path
        filter_condition = models.Filter(
            must=[
                models.FieldCondition(
                    key="doc_path",
                    match=models.MatchValue(value=doc_path)
                )
            ]
        )

        try:
            # Delete points matching the filter
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=filter_condition
                )
            )
            return True
        except Exception as e:
            print(f"Error deleting chunks for path {doc_path}: {str(e)}")
            return False


# Global instance
qdrant_manager = QdrantManager()


# Convenience functions for use in API endpoints
async def init_qdrant():
    """
    Initialize the Qdrant client
    """
    await qdrant_manager.initialize()


async def store_chunk(content: str, doc_path: str, heading: Optional[str] = None,
                     section: Optional[str] = None, metadata: Optional[Dict] = None) -> str:
    """
    Convenience function to store a document chunk
    """
    return await qdrant_manager.store_chunk(content, doc_path, heading, section, metadata)


async def retrieve_similar_chunks(query_embedding: List[float], doc_path_filter: Optional[str] = None,
                                limit: int = 5) -> List[Dict[str, Any]]:
    """
    Convenience function to retrieve similar document chunks
    """
    return await qdrant_manager.retrieve_similar_chunks(query_embedding, doc_path_filter, limit)


async def batch_store_chunks(chunks: List[Dict[str, Any]]) -> List[str]:
    """
    Convenience function to batch store document chunks
    """
    return await qdrant_manager.batch_store_chunks(chunks)


async def delete_chunks_by_path(doc_path: str) -> bool:
    """
    Convenience function to delete chunks by document path
    """
    return await qdrant_manager.delete_chunks_by_path(doc_path)