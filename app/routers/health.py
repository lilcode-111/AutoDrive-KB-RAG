from fastapi import APIRouter
from app.schemas import HealthResponse,ProjectInfoResponse

router = APIRouter(tags=["health"])

@router.get("/health",response_model=HealthResponse)
def health_check()->HealthResponse:
    return HealthResponse(
        status = "ok",
        project = "AutoDrive-KB-RAG",
        week="week10",
        message="FastAPI service is running"
    )

@router.get("/api/v1/info",response_model=ProjectInfoResponse)
def project_info()->ProjectInfoResponse:
    return ProjectInfoResponse(
        project = "AutoDrive-KB-RAG",
        description="A RAG knowledge base project for autonomous driving evaluation documents.",
        current_stage="Week10 Day1 - FastAPI service skeleton",
        completed_modules=[
            "Week9 chunking demo",
            "Toy Retrieval",
            "Prompt build"
        ],
        next_modules= [
            "Markdown/TxT parser",
            "Json evaluation result parser",
            "PDF parser",
            "Upload and chunk API",
            "Embedding and vector search"
        ]
    )