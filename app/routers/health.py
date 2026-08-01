from fastapi import APIRouter
from app.config import get_settings
from app.schemas import (
    HealthResponse,
    ReadinessResponse,
    ProjectInfoResponse,
    HealthDependencies,
    RetrievalHealth,
)
from app.dependencies import (get_retrieval_service, get_llm_client)

router = APIRouter(tags=["health"])

@router.get(
    "/health",
    response_model=HealthResponse,
)
def health_check() -> HealthResponse:

    settings = get_settings()

    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.version,
    )

@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
)
def readiness_check() -> ReadinessResponse:

    retrieval_service = get_retrieval_service()

    llm_client = get_llm_client()

    return ReadinessResponse(
        status="ready",
        dependencies=HealthDependencies(
            retrieval="ready",
            llm=type(llm_client).__name__,
        ),
        retrieval=RetrievalHealth(
            indexed_chunks=retrieval_service.count(),
        ),
    )

@router.get("/api/v1/info",response_model=ProjectInfoResponse)
def project_info()->ProjectInfoResponse:
    return ProjectInfoResponse(
        project = "AutoDrive-KB-RAG",
        description="A RAG knowledge base project for autonomous driving evaluation documents.",
        current_stage="Production-oriented RAG service with Docker deployment",
        completed_modules=[
            "Document chunking",
            "Semantic retrieval",
            "Prompt construction",
            "RAG answer pipeline",
            "Embedding cache",
            "Logging system",
            "Docker deployment",
        ],
        next_modules= [
            "Markdown/TXT parser enhancement",
            "JSON evaluation result parser",
            "PDF parser",
            "Persistent vector database",
            "RAG evaluation pipeline",
        ]
    )