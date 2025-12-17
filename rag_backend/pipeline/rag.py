"""
RAG pipeline for the Physical AI & Humanoid Robotics RAG system.
Handles the complete retrieval-augmented generation workflow.
"""
from typing import List, Dict, Any, Optional
from ..db.qdrant_client import retrieve_similar_chunks, store_chunk, batch_store_chunks
from ..pipeline.embed import embed_text, embed_texts
from ..pipeline.document_parser import parse_document
import logging


class RAGPipeline:
    """
    Complete RAG pipeline that handles document ingestion, retrieval, and generation preparation
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def ingest_document(self, file_path: str, doc_path: str) -> bool:
        """
        Ingest a document by parsing it, creating embeddings, and storing in vector database

        Args:
            file_path: Local path to the document file
            doc_path: Document path identifier for retrieval filtering

        Returns:
            Boolean indicating success of ingestion
        """
        try:
            # Parse the document into chunks
            self.logger.info(f"Parsing document: {file_path}")
            document_chunks = parse_document(file_path)

            if not document_chunks:
                self.logger.warning(f"No content found in document: {file_path}")
                return False

            self.logger.info(f"Parsed {len(document_chunks)} chunks from document: {file_path}")

            # Create embeddings for all chunks
            self.logger.info("Creating embeddings for document chunks...")
            contents = [chunk['content'] for chunk in document_chunks]
            embeddings = await embed_texts(contents)

            # Add embeddings to chunks and store in Qdrant
            chunks_to_store = []
            for i, chunk in enumerate(document_chunks):
                chunk_with_embedding = {
                    **chunk,
                    'embedding': embeddings[i]
                }
                chunks_to_store.append(chunk_with_embedding)

            self.logger.info("Storing document chunks in vector database...")
            chunk_ids = await batch_store_chunks(chunks_to_store)

            self.logger.info(f"Successfully stored {len(chunk_ids)} chunks in vector database")
            return True

        except Exception as e:
            self.logger.error(f"Error ingesting document {file_path}: {str(e)}")
            return False

    async def retrieve_context(self, query: str, doc_path_filter: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context for a query using vector search

        Args:
            query: User query to find relevant context for
            doc_path_filter: Optional filter to limit search to specific document
            limit: Maximum number of chunks to retrieve

        Returns:
            List of relevant document chunks with similarity scores
        """
        try:
            # Create embedding for the query
            self.logger.info(f"Creating embedding for query: {query[:50]}...")
            query_embedding = await embed_text(query)

            # Retrieve similar chunks from vector database
            self.logger.info(f"Retrieving similar chunks (limit: {limit})")
            similar_chunks = await retrieve_similar_chunks(
                query_embedding=query_embedding,
                doc_path_filter=doc_path_filter,
                limit=limit
            )

            self.logger.info(f"Retrieved {len(similar_chunks)} relevant chunks")
            return similar_chunks

        except Exception as e:
            self.logger.error(f"Error retrieving context for query '{query[:50]}...': {str(e)}")
            return []

    async def process_query(self, query: str, doc_path_filter: Optional[str] = None, limit: int = 5) -> Dict[str, Any]:
        """
        Complete RAG process: retrieve context and prepare for generation

        Args:
            query: User query
            doc_path_filter: Optional filter to limit search to specific document
            limit: Maximum number of chunks to retrieve

        Returns:
            Dictionary with query, retrieved context, and metadata
        """
        try:
            # Retrieve relevant context
            context_chunks = await self.retrieve_context(query, doc_path_filter, limit)

            # Combine context content
            context_content = []
            sources = []

            for chunk in context_chunks:
                context_content.append(chunk['content'])
                sources.append({
                    'doc_path': chunk['doc_path'],
                    'heading': chunk['heading'],
                    'section': chunk['section'],
                    'similarity_score': chunk['similarity_score']
                })

            # Prepare response
            result = {
                'query': query,
                'context': context_content,
                'sources': sources,
                'context_chunks': context_chunks,
                'retrieval_count': len(context_chunks)
            }

            self.logger.info(f"RAG process completed for query: {query[:50]}...")
            return result

        except Exception as e:
            self.logger.error(f"Error processing query '{query[:50]}...': {str(e)}")

            # Return a structured response even if there was an error
            return {
                'query': query,
                'context': [],
                'sources': [],
                'context_chunks': [],
                'retrieval_count': 0,
                'error': str(e)
            }

    async def batch_ingest_documents(self, file_paths: List[str], doc_paths: List[str]) -> Dict[str, bool]:
        """
        Ingest multiple documents in batch

        Args:
            file_paths: List of local paths to document files
            doc_paths: List of document path identifiers for retrieval filtering

        Returns:
            Dictionary mapping file paths to ingestion success status
        """
        if len(file_paths) != len(doc_paths):
            raise ValueError("file_paths and doc_paths must have the same length")

        results = {}
        for file_path, doc_path in zip(file_paths, doc_paths):
            try:
                success = await self.ingest_document(file_path, doc_path)
                results[file_path] = success
                self.logger.info(f"Document ingestion {'succeeded' if success else 'failed'}: {file_path}")
            except Exception as e:
                self.logger.error(f"Error ingesting document {file_path}: {str(e)}")
                results[file_path] = False

        return results

    async def delete_document(self, doc_path: str) -> bool:
        """
        Delete all chunks associated with a specific document path

        Args:
            doc_path: Document path identifier

        Returns:
            Boolean indicating success of deletion
        """
        try:
            from ..db.qdrant_client import delete_chunks_by_path
            success = await delete_chunks_by_path(doc_path)
            if success:
                self.logger.info(f"Successfully deleted document chunks for: {doc_path}")
            else:
                self.logger.warning(f"No chunks found to delete for document: {doc_path}")
            return success
        except Exception as e:
            self.logger.error(f"Error deleting document {doc_path}: {str(e)}")
            return False


# Global instance
rag_pipeline = RAGPipeline()


async def ingest_document(file_path: str, doc_path: str) -> bool:
    """
    Convenience function to ingest a document
    """
    return await rag_pipeline.ingest_document(file_path, doc_path)


async def retrieve_context(query: str, doc_path_filter: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Convenience function to retrieve context for a query
    """
    return await rag_pipeline.retrieve_context(query, doc_path_filter, limit)


async def process_query(query: str, doc_path_filter: Optional[str] = None, limit: int = 5) -> Dict[str, Any]:
    """
    Convenience function to process a complete RAG query
    """
    return await rag_pipeline.process_query(query, doc_path_filter, limit)


async def batch_ingest_documents(file_paths: List[str], doc_paths: List[str]) -> Dict[str, bool]:
    """
    Convenience function to batch ingest documents
    """
    return await rag_pipeline.batch_ingest_documents(file_paths, doc_paths)


async def delete_document(doc_path: str) -> bool:
    """
    Convenience function to delete a document
    """
    return await rag_pipeline.delete_document(doc_path)