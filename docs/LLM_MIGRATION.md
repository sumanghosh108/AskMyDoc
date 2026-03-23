# LLM Migration: Local Models to Groq API

## Overview

This document describes the migration from locally downloaded ML models to the Groq LLM API (`GROQ_API_KEY`) for all inference tasks. The goal is to eliminate heavy local model dependencies (PyTorch, sentence-transformers) and consolidate all ML inference through the Groq cloud API where possible.

---

## What Changed

### 1. Reranker: CrossEncoder (Local) -> Groq LLM (API)

**Before:**
- Used `cross-encoder/ms-marco-MiniLM-L-6-v2` (~88 MB local model)
- Required `sentence-transformers` + PyTorch (~2 GB+ installed)
- Loaded into local memory for inference

**After:**
- Uses Groq LLM API (`llama-3.3-70b-versatile`) for relevance scoring
- Sends query + document passages to the LLM in a single prompt
- Returns JSON array of relevance scores (0-10 scale)
- Falls back to original document order on parse failure

**File changed:** `src/retrieval/reranker.py`

**How it works:**
1. All candidate documents are formatted with indices and sent to the Groq LLM
2. The LLM scores each passage for relevance to the query (0-10 scale)
3. Documents are sorted by score and the top-k are returned
4. Metadata is enriched with `reranker_score` and `reranker_rank`

---

### 2. Embeddings: HuggingFace/sentence-transformers (Local) -> ChromaDB Default (Built-in)

**Before:**
- Used `langchain-huggingface` with `HuggingFaceEmbeddings`
- Required `sentence-transformers` + PyTorch
- Model: `all-MiniLM-L6-v2` loaded via sentence-transformers

**After:**
- Uses ChromaDB's built-in default embedding function
- Same `all-MiniLM-L6-v2` model, but via `onnxruntime` (much lighter)
- No PyTorch dependency required
- ChromaDB handles embedding automatically during ingestion and query

**Files changed:**
- `src/indexing/ingest.py` - Removed `HuggingFaceEmbeddings`, uses ChromaDB default
- `vectorstore/chroma_client.py` - Replaced `SentenceTransformer` with `chromadb.utils.embedding_functions.DefaultEmbeddingFunction()`

---

### 3. Configuration Changes

**`src/core/config.py`:**
- Removed `RERANKER_MODEL` config variable
- Updated comments to reflect Groq-based reranking and ChromaDB default embeddings

**`.env` and `.env.example`:**
- Removed `RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2`
- Updated section header from "Embedding & Reranker Models (Local)" to "Embedding Model (ChromaDB built-in default)"
- Added comment: "Reranking now uses Groq LLM (no local model needed)"

**`render.yaml`:**
- Removed `RERANKER_MODEL` environment variable from Render deployment config

---

### 4. Dependency Changes

**`requirements.txt`:**
- Removed `sentence-transformers>=3.0.0`
- Removed `langchain-huggingface>=0.1.0`
- Updated comments to reflect Groq-based reranking

**`vectorstore/setup.py`:**
- Removed `sentence-transformers>=3.0.0` from install_requires

**Impact:**
- Eliminates ~2 GB+ of PyTorch/sentence-transformers dependencies
- Faster `pip install` and Docker builds
- Smaller container images

---

### 5. Dockerfile Changes

**Before:**
```dockerfile
# Pre-download ML models during build so startup is fast (no network delay)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')" && \
    python -c "from sentence_transformers import CrossEncoder; CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')"
```

**After:**
```dockerfile
# No local ML models to pre-download — embeddings use ChromaDB's built-in
# default (onnxruntime), and reranking uses Groq LLM API
```

---

## Removed Local Models

The following locally cached models are no longer needed and can be safely deleted from `~/.cache/huggingface/hub/`:

| Model | Size | Previously Used For |
|-------|------|-------------------|
| `sentence-transformers/all-MiniLM-L6-v2` | ~88 MB | Embeddings (now via ChromaDB/onnxruntime) |
| `cross-encoder/ms-marco-MiniLM-L-6-v2` | ~88 MB | Reranking (now via Groq LLM API) |
| `BAAI/bge-small-en-v1.5` | ~129 MB | Unused |
| `Qwen/Qwen2.5-0.5B-Instruct` | ~954 MB | Unused |
| `facebook/wav2vec2-base-960h` | ~360 MB | Unused |
| `facebook/wav2vec2-large-960h-lv60-self` | ~1.2 GB | Unused |
| `Salesforce/blip-image-captioning-base` | ~1.9 GB | Unused |

**Total reclaimable space: ~4.6 GB**

To clean up:
```bash
# Remove all cached HuggingFace models
rm -rf ~/.cache/huggingface/hub/
```

---

## Architecture After Migration

```
User Query
    |
    v
[Query Rewriting] -----> Groq LLM API (llama-3.3-70b-versatile)
    |
    v
[Hybrid Retrieval]
    |-- BM25 Keyword Search (local, no model needed)
    |-- Vector Search (ChromaDB built-in embedding via onnxruntime)
    |
    v
[Reranking] -----------> Groq LLM API (llama-3.3-70b-versatile)
    |
    v
[Answer Generation] ---> Groq LLM API (llama-3.3-70b-versatile)
    |
    v
Response + Citations
```

**All LLM inference now flows through `GROQ_API_KEY`:**
- Answer generation (was already Groq)
- Query rewriting (was already Groq)
- Multi-hop reasoning (was already Groq)
- Reranking (NEW - migrated from local CrossEncoder)

**Embeddings use ChromaDB's built-in default:**
- Same `all-MiniLM-L6-v2` model
- Runs via `onnxruntime` instead of PyTorch
- Much lighter dependency footprint

---

## Migration Notes

### Re-ingestion Required
After this migration, existing ChromaDB data should continue to work since the same embedding model (`all-MiniLM-L6-v2`) is used. However, if you encounter any embedding dimension mismatches, clear and re-ingest:

```bash
# Clear existing ChromaDB data
rm -rf chroma_db/

# Re-ingest documents
python main.py ingest <your-source>
```

### API Rate Limits
Since reranking now uses the Groq API, be aware of rate limits:
- Groq free tier: 30 requests/minute, 14,400 requests/day
- Each reranking call = 1 API request
- Plan accordingly for high-traffic deployments

### Fallback Behavior
If the Groq API is unavailable or returns unparseable results during reranking, the system falls back to the original document order (no reranking applied). This ensures the system degrades gracefully.

---

## Files Modified Summary

| File | Change |
|------|--------|
| `src/retrieval/reranker.py` | Replaced CrossEncoder with Groq LLM-based reranking |
| `src/indexing/ingest.py` | Removed HuggingFaceEmbeddings, uses ChromaDB default |
| `src/core/config.py` | Removed RERANKER_MODEL, updated comments |
| `vectorstore/chroma_client.py` | Replaced SentenceTransformer with ChromaDB default embedding |
| `vectorstore/setup.py` | Removed sentence-transformers dependency |
| `requirements.txt` | Removed sentence-transformers, langchain-huggingface |
| `.env` | Removed RERANKER_MODEL |
| `.env.example` | Removed RERANKER_MODEL |
| `render.yaml` | Removed RERANKER_MODEL env var |
| `Dockerfile` | Removed local model pre-download step |
| `docs/LLM_MIGRATION.md` | This documentation |
