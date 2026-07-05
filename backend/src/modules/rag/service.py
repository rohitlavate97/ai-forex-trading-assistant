import os
from typing import List, Any
import uuid
import tempfile
from fastapi import UploadFile

from qdrant_client import AsyncQdrantClient
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings

from src.core.config import settings

# Configure global settings for llama-index
if settings.OPENAI_API_KEY:
    Settings.embed_model = OpenAIEmbedding(api_key=settings.OPENAI_API_KEY)
else:
    # Use a dummy embedding model for tests if no API key is provided
    from llama_index.core.embeddings import MockEmbedding
    Settings.embed_model = MockEmbedding(embed_dim=1536)


class RAGService:
    """Service layer for RAG operations (Document Ingestion and Retrieval)."""

    def __init__(self, collection_name: str = "forex_knowledge_base"):
        self.collection_name = collection_name
        self.client = AsyncQdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT
        )
        self.vector_store = QdrantVectorStore(
            collection_name=self.collection_name, 
            aclient=self.client, 
            prefer_grpc=False
        )

    async def ingest_document(self, file: UploadFile) -> dict:
        """
        Saves the uploaded file to a temporary directory, parses it into nodes/chunks,
        generates embeddings, and stores them in Qdrant.
        """
        doc_id = str(uuid.uuid4())
        
        # Save file to temporary storage to use SimpleDirectoryReader
        suffix = os.path.splitext(file.filename)[1] if file.filename else ".txt"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name

        try:
            # Read document
            reader = SimpleDirectoryReader(input_files=[temp_path])
            documents = reader.load_data()
            
            # Attach custom metadata
            for doc in documents:
                doc.metadata["document_id"] = doc_id
                doc.metadata["filename"] = file.filename

            # Create index (this embeds and inserts into Qdrant)
            storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
            index = VectorStoreIndex.from_documents(
                documents, 
                storage_context=storage_context,
                show_progress=False
            )
            
            # LlamaIndex abstracts the exact chunk count, but we can return the doc count
            return {
                "message": f"Successfully ingested {file.filename}",
                "document_id": doc_id,
                "chunks_inserted": len(documents) # Note: actual chunk count might be higher due to splitting
            }
            
        finally:
            # Cleanup temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    async def query_knowledge_base(self, query: str, limit: int = 5) -> List[dict]:
        """
        Embeds the query and searches Qdrant for the top k most similar chunks.
        """
        # Create an index from the existing vector store
        index = VectorStoreIndex.from_vector_store(vector_store=self.vector_store)
        
        # Use as retriever
        retriever = index.as_retriever(similarity_top_k=limit)
        
        # Execute query
        nodes = await retriever.aretrieve(query)
        
        results = []
        for node_with_score in nodes:
            results.append({
                "text": node_with_score.node.get_content(),
                "score": float(node_with_score.score) if node_with_score.score else 0.0,
                "metadata": node_with_score.node.metadata
            })
            
        return results
