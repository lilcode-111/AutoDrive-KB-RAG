from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.routers.retrieval import RetrievedChunk
from app.dependencies import get_rag_service
from src.rag.rag_service import RAGService

router = APIRouter(
    prefix="/api/v1/rag",
    tags=["rag"],
)

class RAGAnswerRequest(BaseModel):
    """
    Request body for the RAG answer endpoint.
    """
    query: str = Field(...,min_length = 1)
    top_k: int = Field(default = 5, gt = 0)

class RAGAnswerResponse(BaseModel):
    """
    Response body returned by the RAG answer endpoint.
    """

    query: str
    answer: str
    answer_status: str
    source_count: int
    sources: List[RetrievedChunk]


@router.post("/answer",response_model=RAGAnswerResponse,)
def answer_question(request:RAGAnswerRequest,rag_service: RAGService = Depends(
        get_rag_service),)->RAGAnswerResponse:
    """
    Retrieve relevant chunks and generate a grounded answer.
    """
    try:
        result = rag_service.answer(query=request.query,top_k=request.top_k,)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code = 400,detail = str(exc)) from exc
    
    return RAGAnswerResponse(**result)
