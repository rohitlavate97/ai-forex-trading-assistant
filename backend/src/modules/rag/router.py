from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from typing import Any

from src.modules.auth.dependencies import get_current_user
from src.modules.rag.schemas import DocumentUploadResponse, QueryRequest, QueryResponse
from src.modules.rag.service import RAGService

router = APIRouter(prefix="/rag", tags=["RAG Knowledge Base"])


def get_rag_service() -> RAGService:
    return RAGService()


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: Any = Depends(get_current_user),
    service: RAGService = Depends(get_rag_service)
):
    """
    Upload a document (PDF, TXT, etc.) to the RAG Knowledge Base.
    The document is chunked, embedded, and stored in the vector database.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing")
        
    try:
        result = await service.ingest_document(file)
        return DocumentUploadResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=QueryResponse)
async def query_knowledge_base(
    request: QueryRequest,
    current_user: Any = Depends(get_current_user),
    service: RAGService = Depends(get_rag_service)
):
    """
    Search the vector database for chunks relevant to the query.
    Returns the top matching text segments and metadata.
    """
    try:
        results = await service.query_knowledge_base(request.query, request.limit)
        return QueryResponse(
            query=request.query,
            results=results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
