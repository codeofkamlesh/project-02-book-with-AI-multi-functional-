"""
Retriever module for the Physical AI & Humanoid Robotics RAG system.
Handles document retrieval from Qdrant vector database with re-ranking and provenance tracking.
"""
import asyncio
import os
from typing import List, Dict, Any, Optional
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams
import numpy as np

class Retriever:
    """
    Handles document retrieval from Qdrant vector database
    """

    def __init__(self, collection_name: str = "book_chunks"):
        self.collection_name = collection_name
        self.client = AsyncQdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
            prefer_grpc=True
        )

    async def initialize_collection(self):
        """
        Initialize the Qdrant collection if it doesn't exist
        """
        try:
            # Check if collection exists
            collections = await self.client.get_collections()
            collection_names = [coll.name for coll in collections.collections]

            if self.collection_name not in collection_names:
                # Create collection with appropriate vector size
                # Using 1536 dimensions for OpenAI text-embedding-3-small
                await self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
                )

                print(f"Created Qdrant collection: {self.collection_name}")
            else:
                print(f"Qdrant collection {self.collection_name} already exists")

        except Exception as e:
            print(f"Error initializing collection: {str(e)}")
            raise

    async def upsert_chunks(self, chunks: List[Dict[str, Any]]):
        """
        Upsert document chunks to Qdrant collection
        """
        try:
            points = []
            for chunk in chunks:
                # Generate embedding for the source text
                # NOTE: In a real implementation, we'd embed the text first
                # For now, we'll create placeholder embeddings (in practice, these would come from the embedder)
                embedding = [0.0] * 1536  # Placeholder - would be real embedding in practice

                point = models.PointStruct(
                    id=chunk["chunk_id"],
                    vector=embedding,
                    payload={
                        "doc_id": chunk["doc_id"],
                        "title": chunk["title"],
                        "path": chunk["path"],
                        "source_text": chunk["source_text"][:500],  # Truncate for storage efficiency
                        "is_code_block": chunk["is_code_block"],
                        "char_count": chunk["char_count"],
                        "token_estimate": chunk["token_estimate"],
                        "module": self._extract_module_from_path(chunk["path"]),
                        "created_at": int(chunk.get("created_at", 0))
                    }
                )
                points.append(point)

            # Upsert points to collection
            await self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

            print(f"Upserted {len(points)} chunks to collection {self.collection_name}")

        except Exception as e:
            print(f"Error upserting chunks: {str(e)}")
            raise

    async def retrieve_documents(
        self,
        query_embedding: List[float],
        top_k: int = 6,
        filters: Optional[Dict[str, Any]] = None,
        user_profile: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents from Qdrant based on query embedding
        """
        try:
            # Build filters if provided
            qdrant_filters = None
            if filters:
                filter_conditions = []
                for key, value in filters.items():
                    if isinstance(value, str):
                        filter_conditions.append(
                            models.FieldCondition(
                                key=key,
                                match=models.MatchText(text=value)
                            )
                        )
                    elif isinstance(value, list):
                        filter_conditions.append(
                            models.FieldCondition(
                                key=key,
                                match=models.MatchAny(any=value)
                            )
                        )

                if filter_conditions:
                    qdrant_filters = models.Filter(must=filter_conditions)

            # Search in Qdrant
            search_results = await self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                query_filter=qdrant_filters,
                with_payload=True,
                with_vectors=False
            )

            # Convert results to our format
            retrieved_docs = []
            for result in search_results:
                doc = {
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload,
                    "source_text": result.payload.get("source_text", ""),
                    "title": result.payload.get("title", ""),
                    "path": result.payload.get("path", ""),
                    "module": result.payload.get("module", ""),
                    "is_code_block": result.payload.get("is_code_block", False)
                }
                retrieved_docs.append(doc)

            # Re-rank based on user profile and context if available
            if user_profile:
                retrieved_docs = self._rerank_by_profile(retrieved_docs, user_profile)

            return retrieved_docs

        except Exception as e:
            print(f"Error retrieving documents: {str(e)}")
            raise

    def _rerank_by_profile(self, docs: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Re-rank documents based on user profile preferences
        """
        # Define weights for different factors
        profile_match_weight = 0.3
        module_relevance_weight = 0.2
        recency_weight = 0.1
        similarity_weight = 0.4  # Original similarity score

        # Calculate adjusted scores
        for doc in docs:
            score_adjustment = 0.0

            # Check if document module matches user's background
            doc_module = doc.get("module", "").lower()
            user_software_level = user_profile.get("software_background", {}).get("level", "")
            user_hardware_experience = user_profile.get("hardware_background", {}).get("experience", "")

            # Adjust score based on module relevance to user's background
            if user_software_level in ["beginner", "intermediate"] and "ros" in doc_module:
                score_adjustment += profile_match_weight * 0.5  # ROS content for beginners/intermediate
            elif user_hardware_experience == "basic robotics" and "simulation" in doc_module:
                score_adjustment += profile_match_weight * 0.3  # Simulation content for basic robotics users

            # Apply adjustment to score
            doc["adjusted_score"] = doc["score"] * (1 + score_adjustment)

        # Sort by adjusted score
        docs.sort(key=lambda x: x["adjusted_score"], reverse=True)

        return docs

    def _extract_module_from_path(self, path: str) -> str:
        """
        Extract module name from document path
        """
        # Example: /docs/ros2-foundations/index.md -> ros2-foundations
        parts = path.split('/')
        for part in parts:
            if 'module' in part or 'foundations' in part or 'simulation' in part or 'isaac' in part or 'vla' in part:
                return part
        return 'general'

    async def search_by_text_content(self, text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search for chunks that contain specific text content (for highlight-to-ask functionality)
        """
        try:
            # This would use Qdrant's full-text search capability or filter-based search
            # For now, we'll use keyword matching in the payload
            search_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="source_text",
                        match=models.MatchText(text=text[:100])  # Use first 100 chars for search
                    )
                ]
            )

            search_results = await self.client.search(
                collection_name=self.collection_name,
                query_vector=[0.0] * 1536,  # Placeholder - in practice would use dense retrieval
                limit=top_k,
                query_filter=search_filter,
                with_payload=True,
                with_vectors=False,
                score_threshold=0.0  # Don't filter by score when doing content-based search
            )

            # Convert results to our format
            retrieved_docs = []
            for result in search_results:
                doc = {
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload,
                    "source_text": result.payload.get("source_text", ""),
                    "title": result.payload.get("title", ""),
                    "path": result.payload.get("path", ""),
                    "module": result.payload.get("module", ""),
                    "is_code_block": result.payload.get("is_code_block", False)
                }
                retrieved_docs.append(doc)

            return retrieved_docs

        except Exception as e:
            print(f"Error searching by text content: {str(e)}")
            raise

    async def upsert_chunks(self, chunks: List[Dict[str, Any]]):
        """
        Upsert document chunks to Qdrant collection with actual embeddings
        """
        try:
            points = []
            for chunk in chunks:
                # Use the embedding from the chunk (assumes it was already computed)
                embedding = chunk.get("embedding", [0.0] * 1536)  # Default to zero vector if not provided

                point = models.PointStruct(
                    id=chunk["chunk_id"],
                    vector=embedding,
                    payload={
                        "doc_id": chunk["doc_id"],
                        "title": chunk["title"],
                        "path": chunk["path"],
                        "source_text": chunk["source_text"][:500],  # Truncate for storage efficiency
                        "is_code_block": chunk["is_code_block"],
                        "char_count": chunk["char_count"],
                        "token_estimate": chunk["token_estimate"],
                        "module": self._extract_module_from_path(chunk["path"]),
                        "created_at": int(chunk.get("created_at", 0))
                    }
                )
                points.append(point)

            # Upsert points to collection
            await self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

            print(f"Upserted {len(points)} chunks to collection {self.collection_name}")

        except Exception as e:
            print(f"Error upserting chunks: {str(e)}")
            raise


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test_retriever():
        retriever = Retriever()

        # Initialize collection
        await retriever.initialize_collection()

        # Sample chunks to upsert (would come from chunker)
        sample_chunks = [
            {
                "chunk_id": "chunk_001",
                "doc_id": "doc_001",
                "title": "Introduction to ROS2",
                "path": "/docs/ros2-foundations/index.md",
                "source_text": "Robot Operating System 2 (ROS 2) is a flexible framework for writing robot software. It is a collection of tools, libraries, and conventions that aim to simplify the task of creating complex and robust robot behavior across a wide variety of robot platforms.",
                "is_code_block": False,
                "char_count": 250,
                "token_estimate": 50
            }
        ]

        print("Upserting sample chunks...")
        # Note: We'd need real embeddings to actually upsert, so skipping this in the example
        # await retriever.upsert_chunks(sample_chunks)

        print("Sample retriever functionality demonstrated")

    # Run the test
    asyncio.run(test_retriever())