# Milestone 11: RAG Knowledge Base

**Status**: Completed
**Tag**: `v0.11-rag-knowledge-base`

## Objective
Establish a vector search pipeline to allow the ingestion of custom trading strategies, central bank reports, and macroeconomic documents, making them queryable for future agent orchestration.

## Implementation Details
1. **Dependencies**: 
    - Migrated to `llama-index-core>=0.14.0` native Pydantic V2 to resolve architecture constraints in Python 3.14.
    - Added `llama-index-embeddings-openai`, `llama-index-vector-stores-qdrant`, and `qdrant-client`.
2. **Qdrant Vector DB**:
    - Connected to the local Docker Compose Qdrant container running on port `6333`.
3. **Ingestion & Retrieval Pipeline (`RAGService`)**:
    - Created `backend/src/modules/rag/service.py` to handle chunking, temporary file persistence during upload, metadata attachment, and `QdrantVectorStore` sync.
    - Set up a query mechanism using LlamaIndex's high-level `VectorStoreIndex.as_retriever`.
4. **API Routing**:
    - Built `POST /api/v1/rag/upload` and `POST /api/v1/rag/query` with full Pydantic schemas.
5. **Testing**:
    - Designed tests using `unittest.mock.patch` to heavily mock `LlamaIndex`'s `VectorStoreIndex`, `SimpleDirectoryReader`, and `QdrantVectorStore`, ensuring that the API layers logic is tested without hitting the real embedding endpoints or database.
6. **Documentation**:
    - Authored `docs/rag_knowledge_base_guide.md` specifying upload requirements, embedding configurations, and architecture flow.

## Deliverables
- Knowledge Base module spanning Service, Router, and Schemas.
- File upload and semantic search integration with Qdrant.
- Tested endpoints isolating the vector database and LLM calls.
- Documentation and Milestone records.
