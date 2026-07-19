from typing import Any,Dict,List
from fastapi import APIRouter,File,UploadFile
from pydantic import BaseModel,Field

from src.chunking.simple_chunker import chunk_parsed_document
from src.parsing.document_parser import parse_document_by_type
from src.retrieval.retrieval_service import RetrievalService

router = APIRouter(
    prefix="/api/v1/retrieval",
    tags=["retrieval"]
)

# Global in-memory retrieval service.
# The model is loaded once when this module is imported.
retrieval_service = RetrievalService()

class RetrievalIndexResponse(BaseModel):
    filename: str
    file_type: str
    status: str
    text_length: int
    chunk_count: int
    indexed_chunk_count: int
    total_indexed_chunk_count: int
    embedding_dimension: int|None
    metadata: Dict[str,Any] = Field(default_factory=dict)

class RetrievalSearchRequest(BaseModel):
    query: str
    top_k: int = 5

class RetrievedChunk(BaseModel):
    rank: int
    score: float
    chunk_id: str
    source: str
    doc_type: str
    text: str
    text_length: int| None = None
    metadata: Dict[str,Any] = Field(default_factory=dict)

class RetrievalSearchResponse(BaseModel):
    query: str
    top_k: int
    result_count: int
    results: List[RetrievedChunk]

def normalize_chunk(chunk: Dict[str,Any]) -> Dict[str,Any]:
    """
    Normalize chunk dictionary for retrieval API.

    This keeps Day5 compatible with slightly different chunk formats
    from Week9/Week10.
    """
    normalized = dict(chunk)

    if "text_length" not in normalized:
        normalized["text_length"] = len(str(normalized.get("text","")))

    if "metadata" not in normalized or normalized["metadata"] is None:
        normalized["metadata"] = {}
    
    return normalized

@router.post("/index-document", response_model=RetrievalIndexResponse)
async def index_document(file:UploadFile = File(...))->RetrievalIndexResponse:
    """
    Upload a document, parse it, chunk it, embed chunks, and add them into the
    in-memory vector index.
    """
    filename = file.filename or "upload_file"
    content = await file.read()
    
    parse_result = parse_document_by_type(
        filename= filename,
        content = content,
    )

    chunks = chunk_parsed_document(
        text=parse_result["text"],
        filename=parse_result["filename"],
        file_type=parse_result["file_type"],
        base_metadata=parse_result.get("metadata", {}),
    )

    normalized_chunks = [normalize_chunk(chunk) for chunk in chunks]
    index_result = retrieval_service.index_chunks(normalized_chunks)

    return RetrievalIndexResponse(
        filename=parse_result["filename"],
        file_type=parse_result["file_type"],
        status=parse_result["status"],
        text_length=parse_result["text_length"],
        chunk_count=len(normalized_chunks),
        indexed_chunk_count=index_result["indexed_chunk_count"],
        total_indexed_chunk_count=index_result["total_indexed_chunk_count"],
        embedding_dimension=index_result["embedding_dimension"],
        metadata=parse_result.get("metadata", {}),
    )

@router.post("/search",response_model=RetrievalSearchResponse)
def search(request:RetrievalSearchRequest)->RetrievalSearchResponse:
    """
    Search indexed chunks by semantic similarity.
    """
    search_result = retrieval_service.search(
        query = request.query,
        top_k = request.top_k,
    )
    
    return RetrievalSearchResponse(
        query = search_result["query"],
        top_k = search_result["top_k"],
        result_count = search_result["result_count"],
        results = search_result["results"]
    )

@router.post("/clear")
def clear_index()->Dict[str,Any]:
    """
    Clear the in-memory retrieval index.
    Useful during local testing.
    """
    retrieval_service.clear()
    return {
       "status": "success",
       "message": "Retrieval index cleared",
       "total_indexed_chunk_count": retrieval_service.count() 
    }


@router.get("/status")
def retrieval_status()->Dict[str,Any]:
    """
    Return current retrieval index status.
    """
    return {
        "status": "ok",
        "module": "retrieval",
        "total_indexed_chunk_count": retrieval_service.count()
    }


