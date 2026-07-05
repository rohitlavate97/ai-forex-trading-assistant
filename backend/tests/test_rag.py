import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import UploadFile
import io

from src.modules.rag.service import RAGService


@pytest.fixture
def mock_upload_file():
    content = b"This is a test document containing information about Forex trading."
    file = UploadFile(filename="test_doc.txt", file=io.BytesIO(content))
    return file


@pytest.mark.asyncio
@patch("src.modules.rag.service.VectorStoreIndex")
@patch("src.modules.rag.service.SimpleDirectoryReader")
@patch("src.modules.rag.service.QdrantVectorStore")
@patch("src.modules.rag.service.AsyncQdrantClient")
async def test_ingest_document(mock_qdrant_client, mock_qdrant_vs, mock_reader_class, mock_index_class, mock_upload_file):
    # Setup mock reader
    mock_reader_instance = MagicMock()
    
    mock_doc = MagicMock()
    mock_doc.metadata = {}
    mock_reader_instance.load_data.return_value = [mock_doc]
    mock_reader_class.return_value = mock_reader_instance
    
    # Init service
    service = RAGService()
    
    result = await service.ingest_document(mock_upload_file)
    
    assert "Successfully ingested test_doc.txt" in result["message"]
    assert "document_id" in result
    assert result["chunks_inserted"] == 1
    mock_index_class.from_documents.assert_called_once()


@pytest.mark.asyncio
@patch("src.modules.rag.service.VectorStoreIndex")
@patch("src.modules.rag.service.QdrantVectorStore")
@patch("src.modules.rag.service.AsyncQdrantClient")
async def test_query_knowledge_base(mock_qdrant_client, mock_qdrant_vs, mock_index_class):
    # Setup mock retriever
    mock_index_instance = MagicMock()
    mock_retriever = MagicMock()
    
    mock_node = MagicMock()
    mock_node.node.get_content.return_value = "Test content chunk"
    mock_node.score = 0.95
    mock_node.node.metadata = {"filename": "test_doc.txt"}
    
    # aretrieve is an async method on the retriever
    mock_retriever.aretrieve = AsyncMock(return_value=[mock_node])
    mock_index_instance.as_retriever.return_value = mock_retriever
    
    mock_index_class.from_vector_store.return_value = mock_index_instance
    
    # Init service
    service = RAGService()
    
    results = await service.query_knowledge_base("What is Forex?")
    
    assert len(results) == 1
    assert results[0]["text"] == "Test content chunk"
    assert results[0]["score"] == 0.95
    assert results[0]["metadata"]["filename"] == "test_doc.txt"
    mock_retriever.aretrieve.assert_called_once_with("What is Forex?")
