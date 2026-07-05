from pydantic import BaseModel
from typing import List, Optional


class DocumentUploadResponse(BaseModel):
    message: str
    document_id: str
    chunks_inserted: int


class QueryRequest(BaseModel):
    query: str
    limit: int = 5


class SourceNode(BaseModel):
    text: str
    score: float
    metadata: dict


class QueryResponse(BaseModel):
    query: str
    results: List[SourceNode]
