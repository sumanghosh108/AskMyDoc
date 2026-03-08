# Quick Start: ChromaDB Vector Store

Get started with the new ChromaDB vector store and file upload functionality in 5 minutes.

## Prerequisites

```bash
# Install dependencies (if not already installed)
pip install chromadb sentence-transformers
```

## 1. Test the Vector Store

Run the test suite to verify everything works:

```bash
python test_vectorstore.py
```

**Expected output:**
```
============================================================
ChromaDB Vector Store Test Suite
============================================================

Testing ChromaDB Client
============================================================
✓ ChromaDB client initialized
  Persist directory: vector_db
  Collection: rag_documents
  Embedding model: sentence-transformers/all-MiniLM-L6-v2

✓ Collection stats:
  Document count: 0
  Has documents: False

✓ Adding sample documents...
  Added 5 documents

✓ Querying the database...
  Query: 'What is deep learning?'
  Results found: 3
  ...

✓ All tests completed successfully!
```

## 2. Start the Backend Server

```bash
# Make sure you're in the project root
python main.py serve
```

The server will start at `http://localhost:8000`

## 3. Test File Upload via API

### Using curl:

```bash
# Upload a PDF file
curl -X POST "http://localhost:8000/api/v1/ingest/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_document.pdf"

# Upload a Markdown file
curl -X POST "http://localhost:8000/api/v1/ingest/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_document.md"

# Upload a Text file
curl -X POST "http://localhost:8000/api/v1/ingest/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_document.txt"
```

### Expected Response:

```json
{
  "status": "success",
  "chunks_ingested": 42,
  "sources": ["your_document.pdf"]
}
```

## 4. Test via Frontend

### Start the Frontend:

```bash
cd frontend
npm run dev
```

The frontend will start at `http://localhost:5173`

### Upload a File:

1. Navigate to `http://localhost:5173/upload`
2. Drag and drop a file or click to select
3. Watch the upload progress
4. See success notification when complete

### Query the System:

1. Navigate to `http://localhost:5173/`
2. Enter a question related to your uploaded documents
3. Click "Submit Query"
4. View the answer with source citations

## 5. Verify Storage

Check that files are being stored:

```bash
# List the vector database directory
ls -la vector_db/

# Expected output:
# vector_db/
# ├── chroma.sqlite3
# └── collections/
#     └── <uuid>/
```

## 6. Query via API

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the main topic of the document?",
    "top_k": 5,
    "use_hybrid": true,
    "use_reranker": true
  }'
```

## Common Issues

### Issue: PyTorch DLL Error

**Solution:**
```bash
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Issue: Backend Not Reachable

**Check:**
1. Backend is running: `python main.py serve`
2. Port 8000 is not blocked
3. Check backend logs for errors

### Issue: File Upload Fails

**Check:**
1. File type is supported (PDF, MD, TXT)
2. File size is under 10 MB
3. Backend has write permissions for `vector_db/`

### Issue: No Results from Query

**Check:**
1. Documents are uploaded successfully
2. Check `vector_db/` directory exists
3. Run test suite to verify vector store works

## Configuration

Edit `src/core/config.py` to customize:

```python
# Vector Database
CHROMA_PERSIST_DIR = "vector_db"  # Change storage location
CHROMA_COLLECTION_NAME = "rag_documents"  # Change collection name

# Embedding Model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Change model

# Chunking
CHUNK_SIZE = 500  # Adjust chunk size
CHUNK_OVERLAP = 50  # Adjust overlap
```

## Next Steps

1. **Upload Documents**: Upload your own documents via the frontend
2. **Test Queries**: Ask questions about your documents
3. **Monitor Performance**: Check logs and metrics
4. **Customize**: Adjust configuration for your use case

## API Endpoints

### Upload File
- **Endpoint**: `POST /api/v1/ingest/upload`
- **Content-Type**: `multipart/form-data`
- **Body**: `file` (File)
- **Response**: `{ status, chunks_ingested, sources }`

### Query
- **Endpoint**: `POST /api/v1/query`
- **Content-Type**: `application/json`
- **Body**: `{ question, top_k, use_hybrid, use_reranker }`
- **Response**: `{ answer, sources, context_chunks }`

### Health Check
- **Endpoint**: `GET /health`
- **Response**: `{ status, service, database, ... }`

### Metrics
- **Endpoint**: `GET /api/v1/metrics`
- **Response**: `{ totalQueries, avgLatencyMs, ... }`

## Support

For issues or questions:
1. Check `VECTORSTORE_IMPLEMENTATION.md` for detailed documentation
2. Check `src/vectorstore/README.md` for API reference
3. Run `python test_vectorstore.py` to verify setup
4. Check backend logs in `logs/` directory

## Success Checklist

- ✅ Test suite passes
- ✅ Backend starts without errors
- ✅ Frontend connects to backend
- ✅ File upload works
- ✅ Query returns results
- ✅ `vector_db/` directory created
- ✅ Documents persist after restart

You're all set! 🎉
