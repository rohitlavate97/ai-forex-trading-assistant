# RAG Knowledge Base Guide

The **RAG (Retrieval-Augmented Generation) Knowledge Base** allows traders to upload custom trading strategies, macro-economic reports, and central bank PDFs. These documents are embedded and stored in Qdrant, a vector database, enabling the AI to answer complex questions grounded in the user's specific uploaded material.

## Architecture

This module utilizes `LlamaIndex` to orchestrate the chunking, embedding, and retrieval pipeline. 

### Ingestion Flow
1. **Upload**: User uploads a file (PDF, TXT) via the `/api/v1/rag/upload` endpoint.
2. **Parsing**: The file is saved to a temporary directory and parsed using `SimpleDirectoryReader`.
3. **Embedding**: `OpenAIEmbedding` converts text chunks into high-dimensional vectors (dim=1536).
4. **Storage**: Vectors and metadata (filename, unique ID) are persisted directly into the **Qdrant** container via gRPC/HTTP. 

### Retrieval Flow
1. **Query**: A user submits a query to `/api/v1/rag/query`.
2. **Search**: The query is embedded, and Qdrant performs a cosine similarity search to find the top matching chunks.
3. **Response**: Raw chunks (nodes) and their similarity scores are returned to the frontend (or an Agent).

## Endpoints

- `POST /api/v1/rag/upload`
  - Accepts `multipart/form-data` with a `file` field.
  - Returns `DocumentUploadResponse` containing the assigned `document_id` and the number of chunks inserted.

- `POST /api/v1/rag/query`
  - Accepts a JSON payload containing the `query` string and a `limit` (default 5).
  - Returns `QueryResponse` containing the top matching `results` with text, score, and metadata.

## Security & Reliability
- **Isolated Storage**: Vector data is stored in a dedicated Qdrant instance separate from relational SQL data.
- **Dependency Abstraction**: In tests, Qdrant and OpenAI are mocked using `unittest.mock.patch` to prevent network calls and API charges.
- **Cleanup**: Temporary files created during the ingestion process are aggressively deleted utilizing a `finally` block to prevent disk exhaustion.
