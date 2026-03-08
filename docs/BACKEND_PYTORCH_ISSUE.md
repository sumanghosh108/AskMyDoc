# Backend PyTorch Dependency Issue

## Problem

The backend API fails to start due to a PyTorch DLL dependency error:
```
OSError: [WinError 126] The specified module could not be found. 
Error loading "C:\Machine\Lib\site-packages\torch\lib\fbgemm.dll" or one of its dependencies.
```

## Root Cause

The issue stems from the dependency chain:
1. `src/indexing/ingest.py` imports `langchain_community.document_loaders`
2. `langchain_community` imports `transformers`
3. `transformers` imports `torch` (PyTorch)
4. PyTorch's `fbgemm.dll` has missing Windows dependencies

## Impact

- **Frontend:** ✓ Working (http://localhost:3000)
- **ChromaDB:** ✓ Working (direct access via vectorstore package)
- **PostgreSQL:** ✓ Working (direct access via database package)
- **Backend API:** ✗ Not starting (PyTorch DLL issue)
- **File Upload via UI:** ✗ Shows "Network error" (backend not available)

## Solutions

### Option 1: Fix PyTorch Installation (Recommended)

#### A. Reinstall PyTorch with proper dependencies
```bash
# Uninstall current PyTorch
pip uninstall torch torchvision torchaudio

# Install CPU-only version (lighter, no CUDA dependencies)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

#### B. Install Visual C++ Redistributables
PyTorch requires Visual C++ Redistributables:
1. Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Install and restart
3. Try starting backend again

### Option 2: Use ChromaDB Directly (Workaround)

Since ChromaDB works independently, you can upload files directly without the backend:

```python
from vectorstore import get_index_manager
from pathlib import Path

# Initialize manager
manager = get_index_manager()

# Index a file
file_path = "path/to/your/document.txt"
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Add to ChromaDB
chunks_added = manager.add_documents(
    texts=[text],
    metadatas=[{"source": file_path}]
)

print(f"Added {chunks_added} chunks to ChromaDB")

# Search
results = manager.search("your query", n_results=5)
for result in results:
    print(f"Text: {result['text'][:100]}...")
    print(f"Score: {result['relevance_score']:.4f}")
```

### Option 3: Create Lightweight API (Alternative)

Create a minimal FastAPI server without langchain dependencies:

```python
# minimal_api.py
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import shutil

from vectorstore import get_index_manager

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = get_index_manager()

@app.get("/health")
def health():
    return {"status": "ok", "service": "minimal_api"}

@app.post("/api/v1/ingest/upload")
async def upload_file(file: UploadFile = File(...)):
    # Save temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        shutil.copyfileobj(file.file, tmp)
        temp_path = tmp.name
    
    try:
        # Read and index
        with open(temp_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        chunks = manager.add_documents(
            texts=[text],
            metadatas=[{"source": file.filename}]
        )
        
        return {
            "status": "success",
            "chunks_ingested": chunks,
            "sources": [file.filename]
        }
    finally:
        import os
        os.unlink(temp_path)

@app.post("/api/v1/query")
async def query(request: dict):
    question = request.get("question", "")
    top_k = request.get("top_k", 5)
    
    results = manager.search(question, n_results=top_k)
    
    # Format response
    answer = f"Found {len(results)} relevant results:\n\n"
    for i, result in enumerate(results, 1):
        answer += f"{i}. {result['text'][:200]}...\n\n"
    
    sources = [
        {
            "source": r["metadata"].get("source", "unknown"),
            "relevance_score": r["relevance_score"],
            "text": r["text"][:200]
        }
        for r in results
    ]
    
    return {
        "answer": answer,
        "sources": sources,
        "context_chunks": len(results)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Run it:
```bash
python minimal_api.py
```

## Current Workaround

The system is 83% operational without the backend:

1. **ChromaDB** - Fully functional for direct access
2. **PostgreSQL** - Connected and ready
3. **Frontend** - Running at http://localhost:3000
4. **Vector Search** - Working via direct ChromaDB access

You can:
- Use ChromaDB directly via Python scripts
- Query existing data
- View the frontend UI
- Test all components except file upload via UI

## Testing Without Backend

Run the integration test to verify what's working:
```bash
python test_integration.py
```

Expected results:
- ✓ ChromaDB Connection
- ✓ ChromaDB Search
- ✓ PostgreSQL Connection
- ✓ Vector DB Persistence
- ✗ Backend API (expected failure)
- ✓ Frontend

## Next Steps

1. **Try Option 1A** (reinstall PyTorch CPU version) - Most likely to work
2. **If that fails, try Option 1B** (install Visual C++ Redistributables)
3. **If still failing, use Option 2** (direct ChromaDB access) for testing
4. **Or use Option 3** (minimal API) for a lightweight backend

## Additional Resources

- PyTorch Installation Guide: https://pytorch.org/get-started/locally/
- Visual C++ Redistributables: https://aka.ms/vs/17/release/vc_redist.x64.exe
- ChromaDB Documentation: https://docs.trychroma.com/
- FastAPI Documentation: https://fastapi.tiangolo.com/

## System Status

Run this to check current status:
```bash
python test_integration.py
```

Or check manually:
```bash
# Frontend
curl http://localhost:3000

# Backend (will fail until PyTorch is fixed)
curl http://localhost:8000/health

# ChromaDB (via Python)
python -c "from vectorstore import get_chroma_client; print(get_chroma_client().get_collection_stats())"
```
