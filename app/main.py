from fastapi import FastAPI
from app.routers import health,documents,retrieval

app = FastAPI(
    title="AutoDrive-KB-RAG API",
    description=(
        "FastAPI service for the AutoDrive-KB-RAG project. "
        "This service will support document upload, parsing, cleaning, chunking, "
        "retrieval, and RAG prompt construction."
    ),
    version = "0.1.0"
)

app.include_router(health.router)
app.include_router(documents.router)
app.include_router(retrieval.router)

@app.get("/")
def root():
    return {
        "project":"AutoDrive-KB-RAG",
        "message":"Welcome to the AutoDrive-KB-RAG FastAPI service",
        "docs":"/docs",
        "health":"/health"
    }
