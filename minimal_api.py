"""
Minimal FastAPI Server - No PyTorch Dependencies
Provides basic upload and query functionality using ChromaDB directly.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tempfile
import shutil
import os
from typing import List, Optional

from vectorstore import get_index_manager

app = FastAPI(
    title="Minimal RAG API",
    description="Lightweight API without PyTorch dependencies",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize index manager
manager = get_index_manager()


class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 5
    use_hybrid: Optional[bool] = False
    use_reranker: Optional[bool] = False


class SourceMeta(BaseModel):
    source: str
    relevance_score: float
    text: str


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceMeta]
    context_chunks: int


@app.get("/health")
def health():
    """Health check endpoint."""
    try:
        stats = manager.chroma_client.get_collection_stats()
        return {
            "status": "ok",
            "service": "minimal_rag_api",
            "database": "healthy",
            "vector_store_docs": stats["document_count"]
        }
    except Exception as e:
        return {
            "status": "ok",
            "service": "minimal_rag_api",
            "database": "error",
            "error": str(e)
        }


@app.post("/api/v1/ingest/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and ingest a file into ChromaDB.
    Supports: PDF, Markdown (.md), and Text (.txt) files.
    """
    # Validate file type
    allowed_extensions = {".pdf", ".md", ".markdown", ".txt"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Validate file size (10 MB limit)
    max_size = 10 * 1024 * 1024
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large: {file_size / 1024 / 1024:.2f} MB. Maximum: 10 MB"
        )
    
    # Save to temp file
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_path = tmp.name
        
        # Read file content
        with open(temp_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="File is empty or unreadable")
        
        # Index in ChromaDB
        chunks = manager.add_documents(
            texts=[text],
            metadatas=[{"source": file.filename}]
        )
        
        return {
            "status": "success",
            "chunks_ingested": chunks,
            "sources": [file.filename]
        }
        
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Unable to read file. Please ensure it's a text-based file."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest file: {str(e)}")
    finally:
        # Cleanup temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass


@app.post("/api/v1/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Query the RAG system and generate an answer."""
    try:
        # Search ChromaDB
        results = manager.search(request.question, n_results=request.top_k)
        
        if not results:
            return QueryResponse(
                answer="No relevant information found in the knowledge base.",
                sources=[],
                context_chunks=0
            )
        
        # Generate answer from results
        answer = f"Based on the knowledge base, here are the most relevant findings:\n\n"
        
        for i, result in enumerate(results, 1):
            text = result['text']
            # Truncate long texts
            if len(text) > 300:
                text = text[:300] + "..."
            answer += f"{i}. {text}\n\n"
        
        # Format sources
        sources = [
            SourceMeta(
                source=r["metadata"].get("source", "unknown"),
                relevance_score=r["relevance_score"],
                text=r["text"][:200] + "..." if len(r["text"]) > 200 else r["text"]
            )
            for r in results
        ]
        
        return QueryResponse(
            answer=answer.strip(),
            sources=sources,
            context_chunks=len(results)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.get("/api/v1/metrics")
async def metrics():
    """Get system metrics."""
    try:
        stats = manager.chroma_client.get_collection_stats()
        
        return {
            "metrics": {
                "totalQueries": 0,  # Not tracked in minimal version
                "avgLatencyMs": 0,
                "cacheHitRate": 0,
                "vectorStoreDocs": stats["document_count"],
                "cacheStats": {
                    "enabled": False,
                    "connected": False
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("  Minimal RAG API Server")
    print("  No PyTorch dependencies - ChromaDB only")
    print("="*60)
    print("\n  Starting server at http://localhost:8000")
    print("  Frontend should be at http://localhost:3000")
    print("\n  Endpoints:")
    print("    GET  /health")
    print("    POST /api/v1/ingest/upload")
    print("    POST /api/v1/query")
    print("    GET  /api/v1/metrics")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
