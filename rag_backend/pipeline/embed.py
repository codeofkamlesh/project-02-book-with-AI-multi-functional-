"""
Embedding service for the RAG Chatbot system.
Handles text embedding generation using OpenAI's text-embedding-3-small model.
"""
import os
from typing import List, Optional
import openai
from openai import AsyncOpenAI


class EmbeddingService:
    """
    Service for generating text embeddings using OpenAI's text-embedding-3-small model
    """

    def __init__(self):
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "text-embedding-3-small"

    async def embed_text(self, text: str, dimensions: Optional[int] = 1536) -> List[float]:
        """
        Generate embedding for a single text

        Args:
            text: Input text to embed
            dimensions: Desired embedding dimensions (default 1536 for text-embedding-3-small)

        Returns:
            List of floats representing the embedding vector
        """
        try:
            response = await self.client.embeddings.create(
                input=text,
                model=self.model,
                dimensions=dimensions
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {str(e)}")
            # Return a zero vector of specified dimensions as fallback
            return [0.0] * (dimensions or 1536)

    async def embed_texts(self, texts: List[str], dimensions: Optional[int] = 1536) -> List[List[float]]:
        """
        Generate embeddings for multiple texts

        Args:
            texts: List of input texts to embed
            dimensions: Desired embedding dimensions (default 1536 for text-embedding-3-small)

        Returns:
            List of embedding vectors (each vector is a list of floats)
        """
        if not texts:
            return []

        try:
            # OpenAI API has a limit on the number of texts per request
            # For safety, we'll process in batches of 100
            batch_size = 100
            all_embeddings = []

            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                response = await self.client.embeddings.create(
                    input=batch,
                    model=self.model,
                    dimensions=dimensions
                )

                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)

            return all_embeddings
        except Exception as e:
            print(f"Error generating embeddings: {str(e)}")
            # Return zero vectors as fallback
            return [[0.0] * (dimensions or 1536) for _ in texts]

    async def embed_document_chunks(self, chunks: List[dict]) -> List[dict]:
        """
        Embed a list of document chunks, adding the embedding to each chunk

        Args:
            chunks: List of document chunks with content field

        Returns:
            List of document chunks with embedding added
        """
        if not chunks:
            return []

        # Extract content from chunks
        texts = [chunk.get("content", "") for chunk in chunks]
        embeddings = await self.embed_texts(texts)

        # Add embeddings back to chunks
        updated_chunks = []
        for i, chunk in enumerate(chunks):
            updated_chunk = chunk.copy()
            updated_chunk["embedding"] = embeddings[i]
            updated_chunks.append(updated_chunk)

        return updated_chunks


# Global instance
embedding_service = EmbeddingService()


async def embed_text(text: str, dimensions: Optional[int] = 1536) -> List[float]:
    """
    Convenience function to embed a single text
    """
    return await embedding_service.embed_text(text, dimensions)


async def embed_texts(texts: List[str], dimensions: Optional[int] = 1536) -> List[List[float]]:
    """
    Convenience function to embed multiple texts
    """
    return await embedding_service.embed_texts(texts, dimensions)


async def embed_document_chunks(chunks: List[dict]) -> List[dict]:
    """
    Convenience function to embed document chunks
    """
    return await embedding_service.embed_document_chunks(chunks)