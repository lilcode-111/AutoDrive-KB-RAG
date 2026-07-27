from fastapi import FastAPI
from app.routers import health,documents,retrieval,rag

app = FastAPI(
    title="AutoDrive-KB-RAG API",
    description=(
        "FastAPI service for document upload, parsing, chunking, "
        "embedding retrieval, grounded prompt construction, "
        "and RAG answer generation."
    ),
    version = "0.1.0"
)

app.include_router(health.router)
app.include_router(documents.router)
app.include_router(retrieval.router)
app.include_router(rag.router)

@app.get("/")
def root():
    return {
        "project":"AutoDrive-KB-RAG",
        "message":"Welcome to the AutoDrive-KB-RAG FastAPI service",
        "docs":"/docs",
        "health":"/health"
    }
