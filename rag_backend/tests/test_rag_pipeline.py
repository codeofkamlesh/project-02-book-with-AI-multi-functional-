"""
Tests for the RAG pipeline functionality in the Physical AI & Humanoid Robotics system.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from pipeline.rag import RAGPipeline
from pipeline.embed import Embedder
from pipeline.retriever import Retriever
from agents.openai_agent_integration import OpenAIAgent


@pytest.fixture
def mock_embedder():
    """Mock embedder for testing"""
    embedder = AsyncMock(spec=Embedder)
    embedder.embed_single_text.return_value = [0.1, 0.2, 0.3] * 512  # 1536-dim vector
    embedder.embed_texts.return_value = [[0.1, 0.2, 0.3] * 512]
    return embedder


@pytest.fixture
def mock_retriever():
    """Mock retriever for testing"""
    retriever = AsyncMock(spec=Retriever)
    retriever.retrieve_documents.return_value = [
        {
            "id": "test_chunk_1",
            "score": 0.9,
            "payload": {"title": "Test Doc", "path": "/docs/test.md", "source_text": "This is a test document"},
            "source_text": "This is a test document",
            "title": "Test Doc",
            "path": "/docs/test.md",
            "module": "test",
            "is_code_block": False
        }
    ]
    return retriever


@pytest.fixture
def mock_agent():
    """Mock OpenAI agent for testing"""
    agent = AsyncMock(spec=OpenAIAgent)
    agent.generate_rag_response.return_value = "This is a test response based on the context."
    return agent


@pytest.fixture
def rag_pipeline(mock_embedder, mock_retriever, mock_agent):
    """Create a RAG pipeline with mocked dependencies"""
    pipeline = RAGPipeline()
    pipeline.embedder = mock_embedder
    pipeline.retriever = mock_retriever
    pipeline.agent = mock_agent
    return pipeline


@pytest.mark.asyncio
async def test_rag_pipeline_process_query(rag_pipeline, mock_embedder, mock_retriever, mock_agent):
    """Test the complete RAG pipeline process_query method"""
    query = "What is ROS2?"
    user_profile = {
        "software_background": {"level": "beginner"},
        "hardware_background": {"experience": "none"}
    }

    result = await rag_pipeline.process_query(query, user_profile)

    # Assertions
    assert "answer" in result
    assert "sources" in result
    assert "query" in result
    assert result["query"] == query
    assert len(result["sources"]) > 0

    # Verify that the correct methods were called
    mock_embedder.embed_single_text.assert_called_once_with(query)
    mock_retriever.retrieve_documents.assert_called_once()
    mock_agent.generate_rag_response.assert_called_once()


@pytest.mark.asyncio
async def test_rag_pipeline_process_query_with_highlight(rag_pipeline, mock_embedder, mock_retriever, mock_agent):
    """Test the RAG pipeline with highlight text functionality"""
    query = "Explain the concept"
    highlight_text = "This specific text was highlighted by the user"

    # Mock the search_by_text_content method
    mock_retriever.search_by_text_content = AsyncMock(return_value=[
        {
            "id": "highlight_chunk_1",
            "score": 0.95,
            "payload": {"title": "Highlighted Doc", "path": "/docs/highlight.md", "source_text": highlight_text},
            "source_text": highlight_text,
            "title": "Highlighted Doc",
            "path": "/docs/highlight.md",
            "module": "test",
            "is_code_block": False
        }
    ])

    result = await rag_pipeline.process_query(query, highlight_text=highlight_text)

    # Assertions
    assert "answer" in result
    assert "sources" in result
    assert result["query"] == query

    # Verify that search_by_text_content was called instead of retrieve_documents
    mock_retriever.search_by_text_content.assert_called_once_with(highlight_text, top_k=6)


@pytest.mark.asyncio
async def test_rag_pipeline_ingest_document(rag_pipeline, mock_embedder, mock_retriever):
    """Test the RAG pipeline ingest_document method"""
    path = "/docs/test.md"
    content = "This is test content for ingestion."
    title = "Test Document"

    # Mock chunker
    with patch('pipeline.rag.DocumentChunker') as mock_chunker_class:
        mock_chunker_instance = MagicMock()
        mock_chunker_instance.chunk_document.return_value = [
            {
                "chunk_id": "test_chunk_1",
                "doc_id": "test_doc_1",
                "title": title,
                "path": path,
                "source_text": content,
                "is_code_block": False,
                "char_count": len(content),
                "token_estimate": len(content.split())
            }
        ]
        mock_chunker_class.return_value = mock_chunker_instance

        result = await rag_pipeline.ingest_document(path, content, title)

        # Assertions
        assert result["status"] == "success"
        assert result["doc_path"] == path
        assert result["chunks_created"] == 1

        # Verify methods were called
        mock_chunker_instance.chunk_document.assert_called_once_with(content, path, title)
        mock_embedder.embed_texts.assert_called_once()
        mock_retriever.upsert_chunks.assert_called_once()


def test_rag_pipeline_initialization():
    """Test RAG pipeline initialization"""
    pipeline = RAGPipeline()

    # Check that components are initialized
    assert hasattr(pipeline, 'embedder')
    assert hasattr(pipeline, 'retriever')
    assert hasattr(pipeline, 'agent')


if __name__ == "__main__":
    pytest.main([__file__])