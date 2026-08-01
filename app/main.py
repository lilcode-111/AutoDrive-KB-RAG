from fastapi import FastAPI
from app.routers import health,documents,retrieval,rag

OPENAPI_TAGS = [
    {
        "name": "health",
        "description": (
            "Service health checks and project metadata."
        ),
    },
    {
        "name": "documents",
        "description": (
            "Upload, parse, and chunk supported knowledge-base "
            "documents."
        ),
    },
    {
        "name": "retrieval",
        "description": (
            "Index document chunks and perform semantic vector "
            "retrieval."
        ),
    },
    {
        "name": "rag",
        "description": (
            "Generate grounded answers from retrieved knowledge-base "
            "content."
        ),
    },
]

app = FastAPI(
    title="AutoDrive-KB-RAG API",
    description=(
        "FastAPI service for document upload, parsing, chunking, "
        "embedding retrieval, grounded prompt construction, "
        "and RAG answer generation."
    ),
    version = "0.1.0",
    openapi_tags=OPENAPI_TAGS,
)

app.include_router(health.router)
app.include_router(documents.router)
app.include_router(retrieval.router)
app.include_router(rag.router)

@app.get("/")
def root():
    return {
        "project":"AutoDrive-KB-RAG",
        "message":(
            "Welcome to the AutoDrive-KB-RAG FastAPI service"
        ),
        "docs":"/docs",
        "health":"/health"
    }
