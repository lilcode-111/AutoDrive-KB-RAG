# Week10 Day7 - Docker Deployment and Production Readiness

## 1. Overview

Day7 focuses on containerizing the AutoDrive-KB-RAG FastAPI service and improving deployment readiness.

The main objectives:

- Dockerize FastAPI application
- Introduce Docker Compose deployment
- Add health and readiness checks
- Improve environment-based configuration
- Deploy local embedding model inside Docker

---

# 2. Docker Deployment

## 2.1 Docker Image

The project is packaged as a Docker image.

Build:

```bash
docker compose build
```

Run:

```bash
docker compose up
```

The FastAPI service is exposed through:

```
http://localhost:8000
```

---

# 3. Docker Compose

Docker Compose manages the application lifecycle.

Current service:

```
autodrive-kb-rag-service
```

Port mapping:

```
8000:8000
```

Environment configuration:

```
.env
```

The service can be started and stopped through:

```bash
docker compose up
```

and

```bash
docker compose down
```

---

# 4. Environment Configuration

The application uses environment variables for runtime configuration.

Main configurable components:

- LLM provider
- Embedding model
- Embedding batch size
- Retrieval parameters
- Logging level


Example:

```env
LLM_PROVIDER=fake

EMBEDDING_MODEL=/app/models/paraphrase-multilingual-MiniLM-L12-v2

EMBEDDING_BATCH_SIZE=32

EMBEDDING_NORMALIZE=true
```

---

# 5. Local Embedding Model Deployment

## 5.1 Problem

Initially, the container attempted to download the SentenceTransformer model from HuggingFace during runtime.

This caused deployment issues:

- Docker container does not share host cache
- External model download depends on network availability
- Runtime startup becomes unstable


## 5.2 Solution

The embedding model was exported from the local HuggingFace cache and packaged separately.

Model directory:

```
models/
└── paraphrase-multilingual-MiniLM-L12-v2
```


The container loads the model from:

```
/app/models/paraphrase-multilingual-MiniLM-L12-v2
```


Benefits:

- No runtime model download
- Stable container startup
- Reproducible deployment environment

---

# 6. Health Check API

## 6.1 Liveness Check

Endpoint:

```
GET /health
```


Purpose:

Verify that the FastAPI service is running.


Example response:

```json
{
    "status": "ok",
    "service": "AutoDrive-KB-RAG",
    "version": "0.1.0"
}
```

---

# 7. Readiness Check

Endpoint:

```
GET /health/ready
```


Purpose:

Verify that required RAG components are available.


Example response:

```json
{
    "status": "ready",
    "dependencies": {
        "retrieval": "ready",
        "llm": "FakeLLMClient"
    },
    "retrieval": {
        "indexed_chunks": 0
    }
}
```


The readiness check validates:

- Retrieval service initialization
- Embedding model availability
- LLM client availability

---

# 8. Engineering Issues Solved

During Day7 deployment, several practical engineering issues were resolved.

## 8.1 Docker Environment Isolation

Docker containers have independent environments.

Host machine:

```
~/.cache/huggingface
```

is not automatically available inside containers.


## 8.2 Docker Image Rebuild

Source changes require rebuilding the image:

```bash
docker compose build
```


## 8.3 Runtime Model Dependency

Downloading models during container startup introduces external dependency.

The final solution packages the embedding model locally.

---

# 9. Day7 Completion Status

Completed:

- FastAPI Docker deployment
- Docker Compose workflow
- Environment configuration
- Local embedding model deployment
- Health endpoint
- Readiness endpoint


The AutoDrive-KB-RAG project now has a production-oriented RAG service foundation.

Next stage:

- Document ingestion pipeline
- PDF/TXT/Markdown parser
- Chunk processing API
- Vector database integration