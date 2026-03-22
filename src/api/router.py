import time
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI, Request, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
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

        # Initialize Supabase database connection
        from database.db_initializer import initialize_database
        try:
            db_result = initialize_database()

            if db_result['success']:
                log.info(
                    "Supabase database verified",
                    tables_found=len(db_result.get('verification', {}).get('tables', [])),
                    missing_tables=db_result.get('verification', {}).get('missing_tables', []),
                )
            else:
                log.warning(
                    "Supabase verification failed, continuing without database logging",
                    error=db_result.get('error', 'Unknown error')
                )
        except Exception as db_error:
            log.warning(
                "Database initialization failed, continuing without logging",
                error=str(db_error)
            )

        # Pre-connect to ChromaDB so it's ready
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

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows Vercel frontend + localhost dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next: Callable):
    """Structured logging middleware to trace API request times."""
    # Skip logging for health checks to reduce log noise
    if request.url.path == "/health":
        return await call_next(request)

    start_time = time.time()

    # Generate request trace
    logger = log.bind(
        path=request.url.path,
        method=request.method,
        client=request.client.host if request.client else "unknown"
    )

    logger.info("Request started")

    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(
            "Request completed",
            status_code=response.status_code,
            latency_seconds=round(process_time, 4)
        )
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            "Request failed",
            error=str(e),
            latency_seconds=round(process_time, 4)
        )
        raise


@app.get("/health", tags=["System"])
async def health_check(request: Request):
    """Health check endpoint with Supabase database status."""
    from database.db_initializer import verify_database_setup

    health_status = {
        "status": "ok",
        "service": "ask_my_doc_api",
        "version": "2.0.0",
        "database": "unknown"
    }

    try:
        db_verification = verify_database_setup(silent=True)
        if db_verification.get("status") == "healthy":
            health_status["database"] = "healthy"
            health_status["database_provider"] = "supabase"
            health_status["database_tables"] = len(db_verification.get("tables", []))
        elif db_verification.get("status") == "partial":
            health_status["database"] = "partial"
            health_status["database_provider"] = "supabase"
            health_status["missing_tables"] = db_verification.get("missing_tables", [])
        else:
            health_status["database"] = "unhealthy"
            health_status["database_error"] = db_verification.get("error")
    except Exception as e:
        health_status["database"] = "error"
        health_status["database_error"] = str(e)

    return health_status


@app.post("/api/v1/ingest", response_model=IngestResponse, tags=["RAG Pipeline"])
async def ingest_documents_endpoint(request: IngestRequest):
    """Ingest documents into the vector store from file paths or URLs."""
    from src.indexing.ingest import ingest_documents

    start_time = time.time()
    total_chunks = 0

    for source in request.sources:
        try:
            count = ingest_documents(
                source,
                chunk_size=request.chunk_size,
                chunk_overlap=request.chunk_overlap,
            )
            total_chunks += count
        except Exception as e:
            logger = get_logger(__name__)
            logger.error("API ingestion failed for source", source=source, error=str(e))

            # Log error to database
            try:
                from database.error_logger import get_error_logger
                error_logger = get_error_logger()
                error_logger.log_exception(
                    exception=e,
                    pipeline_stage="ingestion",
                    query_text=f"Ingest: {source}",
                    severity="ERROR"
                )
            except Exception as log_error:
                logger.error("Error logging failed", error=str(log_error))

            return JSONResponse(
                status_code=500,
                content={"detail": f"Failed to ingest '{source}': {str(e)}"}
            )

    # Log successful ingestion
    try:
        from database.query_logger import get_query_logger
        query_logger = get_query_logger()
        latency = (time.time() - start_time) * 1000
        query_logger.log_query(
            query_text=f"Ingestion: {', '.join(request.sources)}",
            total_latency=latency,
            retrieved_chunks=total_chunks
        )
    except Exception as e:
        logger = get_logger(__name__)
        logger.error("Ingestion logging failed", error=str(e))

    return IngestResponse(
        status="success",
        chunks_ingested=total_chunks,
        sources=request.sources
    )


@app.post("/api/v1/ingest/upload", response_model=IngestResponse, tags=["RAG Pipeline"])
async def upload_and_ingest_file(file: UploadFile = File(...)):
    """
    Upload a file and ingest it into the vector store.

    Supports: PDF, Markdown (.md), and Text (.txt) files.
    Maximum file size: 10 MB
    """
    import tempfile
    import shutil
    import os
    from pathlib import Path
    from src.indexing.ingest import ingest_documents

    logger = get_logger(__name__)
    start_time = time.time()

    # Validate file type
    allowed_extensions = {".pdf", ".md", ".markdown", ".txt"}
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in allowed_extensions:
        return JSONResponse(
            status_code=400,
            content={"detail": f"Unsupported file type: {file_ext}. Allowed: {', '.join(allowed_extensions)}"}
        )

    # Validate file size (10 MB limit)
    max_size = 10 * 1024 * 1024  # 10 MB in bytes
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning

    if file_size > max_size:
        return JSONResponse(
            status_code=413,
            content={"detail": f"File too large: {file_size / 1024 / 1024:.2f} MB. Maximum: 10 MB"}
        )

    # Create temporary file
    temp_file = None
    try:
        # Create temp file with same extension
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_file = tmp.name

        logger.info(
            "File uploaded to temp location",
            filename=file.filename,
            size_mb=file_size / 1024 / 1024,
            temp_path=temp_file
        )

        # Ingest the file
        try:
            count = ingest_documents(temp_file)

            logger.info(
                "File ingested successfully",
                filename=file.filename,
                chunks=count
            )

            # Log successful ingestion to database
            try:
                from database.query_logger import get_query_logger
                query_logger = get_query_logger()
                latency = (time.time() - start_time) * 1000
                query_logger.log_query(
                    query_text=f"Upload: {file.filename}",
                    total_latency=latency,
                    retrieved_chunks=count
                )
            except Exception as log_error:
                logger.error("Ingestion logging failed", error=str(log_error))

            return IngestResponse(
                status="success",
                chunks_ingested=count,
                sources=[file.filename]
            )

        except Exception as e:
            # Extract original error if this is a wrapped exception
            error_details = {"error": str(e)}
            if hasattr(e, 'original_error') and e.original_error:
                error_details["original_error"] = str(e.original_error)
                error_details["original_error_type"] = type(e.original_error).__name__
            if hasattr(e, 'details'):
                error_details["details"] = e.details

            logger.error("File ingestion failed", filename=file.filename, **error_details)

            # Log error to database
            try:
                from database.error_logger import get_error_logger
                error_logger = get_error_logger()
                error_logger.log_exception(
                    exception=e,
                    pipeline_stage="file_upload_ingestion",
                    query_text=f"Upload: {file.filename}",
                    severity="ERROR"
                )
            except Exception as log_error:
                logger.error("Error logging failed", error=str(log_error))

            return JSONResponse(
                status_code=500,
                content={"detail": f"Failed to ingest file: {str(e)}"}
            )

    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
                logger.info("Temporary file cleaned up", temp_path=temp_file)
            except Exception as e:
                logger.error("Failed to clean up temp file", temp_path=temp_file, error=str(e))


@app.post("/api/v1/query", response_model=QueryResponse, tags=["RAG Pipeline"])
async def query_endpoint(request: QueryRequest):
    """Query the RAG system and generate an answer with all production features."""
    from src.generation.enhanced_generator import generate_answer_enhanced

    try:
        result = generate_answer_enhanced(
            request.question,
            top_k=request.top_k,
            use_hybrid=request.use_hybrid,
            use_reranker=request.use_reranker,
        )

        return QueryResponse(
            answer=result["answer"],
            sources=[SourceMeta(**s) for s in result["sources"]],
            context_chunks=len(result.get("sources", []))
        )
    except Exception as e:
        logger = get_logger(__name__)
        logger.error("API query failed", query=request.question, error=str(e))

        # Log error to database
        try:
            from database.error_logger import get_error_logger
            error_logger = get_error_logger()
            error_logger.log_exception(
                exception=e,
                pipeline_stage="api_endpoint",
                query_text=request.question,
                severity="ERROR",
                http_status_code=500
            )
        except Exception as log_error:
            logger.error("Error logging failed", error=str(log_error))

        return JSONResponse(
            status_code=500,
            content={"detail": f"Query generation failed: {str(e)}"}
        )


@app.get("/api/v1/cache/stats", tags=["System"])
async def cache_stats():
    """Get cache statistics."""
    from src.caching import get_cache

    cache = get_cache()
    stats = cache.get_stats()

    return {"cache_stats": stats}


@app.post("/api/v1/cache/clear", tags=["System"])
async def clear_cache():
    """Clear all cached data."""
    from src.caching import get_cache

    cache = get_cache()
    success = cache.clear_all()

    if success:
        return {"status": "success", "message": "Cache cleared"}
    else:
        return JSONResponse(
            status_code=500,
            content={"detail": "Failed to clear cache"}
        )


@app.get("/api/v1/metrics", tags=["System"])
async def pipeline_metrics():
    """Get pipeline performance metrics."""
    from src.observability import get_metrics
    from src.caching import get_cache
    from src.indexing.ingest import get_vector_store

    # Get pipeline metrics
    metrics = get_metrics()
    stats = metrics.get_stats()

    # Get cache stats
    cache_hit_rate = 0.0
    cache_stats_data = None
    try:
        cache = get_cache()
        cache_stats = cache.get_stats()
        if cache_stats and 'hit_rate' in cache_stats:
            cache_hit_rate = cache_stats['hit_rate']
            cache_stats_data = {
                "enabled": cache_stats.get('enabled', False),
                "connected": cache_stats.get('connected', False),
                "totalRagKeys": cache_stats.get('total_rag_keys', 0),
                "keyspaceHits": cache_stats.get('keyspace_hits', 0),
                "keyspaceMisses": cache_stats.get('keyspace_misses', 0),
                "hitRate": cache_hit_rate
            }
    except Exception as e:
        log.warning("Failed to get cache stats", error=str(e))

    # Get vector store document count
    vector_store_docs = 0
    try:
        vector_store = get_vector_store()
        collection = vector_store._collection
        vector_store_docs = collection.count()
    except Exception as e:
        log.warning("Failed to get vector store count", error=str(e))

    # Transform to frontend format
    if "error" in stats:
        # No executions yet
        response = {
            "totalQueries": 0,
            "avgLatencyMs": 0,
            "cacheHitRate": cache_hit_rate,
            "vectorStoreDocs": vector_store_docs
        }
    else:
        response = {
            "totalQueries": stats.get("total_executions", 0),
            "avgLatencyMs": stats.get("latency", {}).get("avg_ms", 0),
            "cacheHitRate": cache_hit_rate,
            "vectorStoreDocs": vector_store_docs
        }

    if cache_stats_data:
        response["cacheStats"] = cache_stats_data

    return response
