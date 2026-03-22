"""
Simplified API module (legacy).
The main API is in src/api/router.py
"""

import time
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.utils.logger import get_logger
from src.api.schemas import IngestRequest, IngestResponse, QueryRequest, QueryResponse, SourceMeta
from src.core.config import validate_config

log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup, clean up on shutdown."""
    log.info("Setting up Ask My Doc API...")
    try:
        validate_config()
        from src.indexing.ingest import get_vector_store
        get_vector_store()
        log.info("Vector store initialized")
        yield
    except Exception as e:
        log.error("Failed to initialize API", error=str(e))
        raise e
    finally:
        log.info("Shutting down Ask My Doc API...")


app = FastAPI(
    title="Ask My Doc",
    description="Production Retrieval-Augmented Generation API",
    version="2.0.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def log_requests(request: Request, call_next: Callable):
    """Structured logging middleware to trace API request times."""
    start_time = time.time()
    logger = log.bind(
        path=request.url.path,
        method=request.method,
        client=request.client.host if request.client else "unknown"
    )
    logger.info("Request started")
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info("Request completed", status_code=response.status_code, latency_seconds=round(process_time, 4))
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error("Request failed", error=str(e), latency_seconds=round(process_time, 4))
        raise


@app.get("/health", tags=["System"])
async def health_check():
    """Simple ping endpoint to verify the server is running."""
    return {"status": "ok", "service": "ask_my_doc_api"}


@app.post("/api/v1/ingest", response_model=IngestResponse, tags=["RAG Pipeline"])
async def ingest_documents_endpoint(request: IngestRequest):
    """Ingest documents into the vector store."""
    from src.indexing.ingest import ingest_documents

    total_chunks = 0
    for source in request.sources:
        try:
            count = ingest_documents(source, chunk_size=request.chunk_size, chunk_overlap=request.chunk_overlap)
            total_chunks += count
        except Exception as e:
            return JSONResponse(status_code=500, content={"detail": f"Failed to ingest '{source}': {str(e)}"})

    return IngestResponse(status="success", chunks_ingested=total_chunks, sources=request.sources)


@app.post("/api/v1/query", response_model=QueryResponse, tags=["RAG Pipeline"])
async def query_endpoint(request: QueryRequest):
    """Query the RAG system and generate an answer."""
    from src.generation.generator import generate_answer

    try:
        result = generate_answer(request.question, top_k=request.top_k, use_hybrid=request.use_hybrid, use_reranker=request.use_reranker)
        return QueryResponse(
            answer=result["answer"],
            sources=[SourceMeta(**s) for s in result["sources"]],
            context_chunks=len(result.get("sources", []))
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Query generation failed: {str(e)}"})
