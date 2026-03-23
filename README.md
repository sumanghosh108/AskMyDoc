# AskMyDoc - Production RAG System

A production-grade Retrieval-Augmented Generation (RAG) system that lets you upload documents (PDF, Markdown, TXT) and ask natural-language questions answered directly from your content. Built with a React frontend, FastAPI backend, ChromaDB vector store, Supabase (PostgreSQL) logging, and **Groq LLM API** for all inference.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [CLI Commands](#cli-commands)
  - [REST API](#rest-api)
- [Project Structure](#project-structure)
- [RAG Pipeline](#rag-pipeline)
- [Advanced Features](#advanced-features)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- A free [Groq API key](https://console.groq.com)
- A [Supabase](https://supabase.com) project (for query/error logging)

### 1. Clone & set up the backend

```bash
git clone <repo-url> && cd AskMyDoc
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
```

### 3. Start the backend

```bash
python main.py serve
# API available at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

### 4. Start the frontend

```bash
cd frontend
npm install
npm run dev
# UI available at http://localhost:3000
```

### 5. Ingest documents and start asking questions

```bash
# Ingest a directory of documents
python main.py ingest --source ./sample_docs/

# Or ask via CLI
python main.py query "What is machine learning?"
```

---

## Features

### Frontend (http://localhost:3000)
- **Query Interface** -- Ask questions and get AI-generated answers with source citations
- **Document Upload** -- Drag-and-drop PDF, Markdown, or plain text files
- **Metrics Dashboard** -- Monitor system performance, cache stats, and vector store size
- **Responsive Design** -- Works on desktop and mobile

### Backend (http://localhost:8000)
- **RESTful API** -- FastAPI with automatic OpenAPI documentation
- **Hybrid Retrieval** -- BM25 keyword search + vector similarity search merged via Reciprocal Rank Fusion
- **LLM Reranking** -- Groq-powered relevance scoring replaces local cross-encoder models
- **Query Rewriting** -- LLM-powered query expansion for better recall
- **Multi-Hop Reasoning** -- Iterative retrieval for complex, multi-step questions
- **Caching** -- Optional Redis layer for response caching
- **Observability** -- Structured logging, latency tracking, and pipeline metrics
- **Database Logging** -- Query history and error tracking via Supabase (PostgreSQL)

---

## Architecture

```
Browser (localhost:3000)
    |
    v
Frontend (React + Vite + TailwindCSS)
    | HTTP API
    v
Backend (FastAPI, Python 3.12)
    |
    |---> Groq LLM API  (llama-3.3-70b-versatile)
    |       - Answer generation
    |       - Re-ranking
    |       - Query rewriting
    |       - Multi-hop reasoning
    |
    |---> ChromaDB  (Vector Store)
    |       - Document storage & embedding
    |       - Similarity search
    |       - Built-in embedding (all-MiniLM-L6-v2 via onnxruntime)
    |
    |---> Supabase / PostgreSQL  (Logging)
    |       - Query history
    |       - Error tracking
    |
    |---> Redis  (Optional Cache)
            - Response caching (TTL-based)
```

All LLM inference flows through a single API key (`GROQ_API_KEY`). No local GPU, PyTorch, or heavy ML frameworks required.

---

## Tech Stack

### Backend
| Component | Technology |
|-----------|------------|
| Framework | FastAPI + Uvicorn |
| LLM | Groq API (llama-3.3-70b-versatile) |
| Embeddings | ChromaDB built-in default (all-MiniLM-L6-v2 via onnxruntime) |
| Vector Store | ChromaDB (persistent, on-disk) |
| Orchestration | LangChain 0.3+ |
| Database | Supabase (PostgreSQL) |
| Caching | Redis (optional) |
| Logging | structlog (structured JSON logs) |

### Frontend
| Component | Technology |
|-----------|------------|
| Framework | React 19 + TypeScript |
| Build Tool | Vite 8 |
| Styling | TailwindCSS 4 |
| State | Zustand |
| HTTP Client | Axios |

---

## Installation

### Backend dependencies

```bash
pip install -r requirements.txt
```

Key packages:
- `langchain`, `langchain-groq`, `langchain-chroma` -- RAG orchestration
- `chromadb` -- Vector storage with built-in embeddings
- `fastapi`, `uvicorn` -- API server
- `rank-bm25` -- BM25 keyword retrieval
- `supabase` -- Database logging
- `redis` -- Optional response caching

No `sentence-transformers` or `PyTorch` required. Embeddings run via ChromaDB's lightweight onnxruntime backend.

### Frontend dependencies

```bash
cd frontend && npm install
```

---

## Configuration

All configuration is managed via environment variables. Copy `.env.example` to `.env` and fill in your credentials.

### Required Variables

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Your Groq API key (free tier available) |
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_MODEL` | `llama-3.3-70b-versatile` | Groq model for generation and reranking |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | ChromaDB embedding model |
| `CHUNK_SIZE` | `600` | Tokens per document chunk |
| `CHUNK_OVERLAP` | `100` | Overlap between chunks |
| `TOP_K` | `5` | Final documents returned after reranking |
| `TOP_K_INITIAL` | `20` | Documents retrieved before reranking |
| `MAX_CONTEXT_TOKENS` | `4000` | Maximum context window for generation |
| `CHROMA_PERSIST_DIR` | `chroma_db` | ChromaDB storage directory |
| `CHROMA_COLLECTION_NAME` | `ask_my_doc` | ChromaDB collection name |
| `CACHE_ENABLED` | `false` | Enable Redis response caching |
| `REDIS_HOST` | `localhost` | Redis host |
| `REDIS_PORT` | `6379` | Redis port |
| `REDIS_TTL` | `3600` | Cache TTL in seconds |
| `QUERY_REWRITING_ENABLED` | `false` | Enable LLM query rewriting |
| `MULTI_HOP_ENABLED` | `false` | Enable multi-hop retrieval |
| `MAX_HOPS` | `3` | Maximum retrieval hops |
| `PROMPT_VERSION` | `v1` | Prompt template version |

---

## Usage

### CLI Commands

```bash
# Start the API server
python main.py serve
python main.py serve --port 9000 --no-reload

# Ingest documents
python main.py ingest --source ./sample_docs/
python main.py ingest --source document.pdf
python main.py ingest --source https://example.com/page
python main.py ingest --source ./docs/ --chunk-size 800 --chunk-overlap 150

# Query your documents
python main.py query "What is machine learning?"
python main.py query "Explain the architecture" --top-k 10
python main.py query "Complex question" --multi-hop --query-rewriting
python main.py query "Question" --json --verbose

# Check vector store status
python main.py status

# Cache management
python main.py cache stats
python main.py cache clear

# Run evaluation
python main.py eval
python main.py eval --ragas --dataset eval/golden_dataset.json
```

### REST API

Once the server is running (`python main.py serve`), interactive docs are at **http://localhost:8000/docs**.

#### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check with database status |
| `POST` | `/api/v1/ingest` | Ingest documents from paths/URLs |
| `POST` | `/api/v1/ingest/upload` | Upload and ingest a file (max 10 MB) |
| `POST` | `/api/v1/query` | Query the RAG system |
| `GET` | `/api/v1/metrics` | Pipeline performance metrics |
| `GET` | `/api/v1/cache/stats` | Cache statistics |
| `POST` | `/api/v1/cache/clear` | Clear all cached data |

#### Example: Query

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is retrieval-augmented generation?",
    "top_k": 5,
    "use_hybrid": true,
    "use_reranker": true
  }'
```

#### Example: Ingest

```bash
curl -X POST http://localhost:8000/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{"sources": ["./sample_docs/"]}'
```

#### Example: Upload file

```bash
curl -X POST http://localhost:8000/api/v1/ingest/upload \
  -F "file=@document.pdf"
```

---

## Project Structure

```
AskMyDoc/
├── main.py                        # CLI entry point (ingest, query, serve, eval)
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Production container
├── render.yaml                    # Render deployment blueprint
├── .env                           # Environment variables (not committed)
├── .env.example                   # Environment template
│
├── src/                           # Backend source code
│   ├── api/
│   │   ├── router.py              # FastAPI app, endpoints, middleware
│   │   └── schemas.py             # Pydantic request/response models
│   ├── core/
│   │   └── config.py              # Centralized configuration loader
│   ├── indexing/
│   │   └── ingest.py              # Document loading, chunking, embedding, storage
│   ├── retrieval/
│   │   ├── base.py                # Vector similarity search
│   │   ├── hybrid.py              # BM25 + Vector hybrid retrieval (RRF)
│   │   └── reranker.py            # Groq LLM-based re-ranking
│   ├── generation/
│   │   ├── generator.py           # Basic LLM answer generation
│   │   └── enhanced_generator.py  # Full pipeline with all features
│   ├── context/
│   │   └── builder.py             # Context deduplication and token management
│   ├── query_rewriter/
│   │   └── rewrite_engine.py      # LLM-powered query expansion
│   ├── multi_hop/
│   │   └── reasoning_controller.py # Multi-hop iterative retrieval
│   ├── caching/
│   │   └── redis_cache.py         # Redis response caching
│   ├── observability/
│   │   └── latency_tracker.py     # Component timing and metrics
│   └── utils/
│       ├── logger.py              # Structured logging setup
│       ├── text_splitter.py       # Lightweight text chunking
│       └── exceptions/            # Custom exception hierarchy
│
├── frontend/                      # React application
│   ├── src/
│   │   ├── components/            # UI components
│   │   ├── pages/                 # Page views (Query, Upload, Metrics)
│   │   ├── services/              # API client
│   │   ├── stores/                # Zustand state management
│   │   └── types/                 # TypeScript type definitions
│   └── package.json
│
├── config/
│   └── prompts_v1.yaml            # Versioned RAG prompt templates
│
├── database/                      # Supabase integration
│   ├── db_initializer.py          # Database setup and verification
│   ├── query_logger.py            # Query history logging
│   └── error_logger.py            # Error tracking
│
├── vectorstore/                   # ChromaDB client package
│   ├── chroma_client.py           # Direct ChromaDB client with default embeddings
│   └── setup.py                   # Package setup
│
├── eval/                          # Evaluation pipeline
│   ├── evaluate.py                # Custom evaluation
│   ├── ragas_evaluate.py          # RAGAS framework evaluation
│   └── golden_dataset.json        # Ground-truth test data
│
├── chroma_db/                     # Persistent vector database (auto-created)
├── logs/                          # Application logs
├── sample_docs/                   # Sample documents for testing
│
└── docs/
    └── LLM_MIGRATION.md           # Migration guide: local models to Groq API
```

---

## RAG Pipeline

The full query pipeline processes a user question through these stages:

```
1. QUERY REWRITING  (optional, Groq LLM)
   Input query -> 3 alternative phrasings + acronym expansion

2. HYBRID RETRIEVAL
   BM25 keyword search ──┐
                          ├── Reciprocal Rank Fusion -> top-20 candidates
   Vector similarity ─────┘
   (ChromaDB built-in embedding: all-MiniLM-L6-v2)

3. RERANKING  (Groq LLM)
   20 candidates -> LLM scores relevance 0-10 -> top-5 selected

4. CONTEXT BUILDING
   Deduplicate -> enforce token limit (4000) -> order by relevance

5. MULTI-HOP REASONING  (optional, Groq LLM)
   If context is insufficient -> generate follow-up query -> repeat retrieval

6. ANSWER GENERATION  (Groq LLM)
   System prompt + context + question -> cited answer
```

### Document Ingestion Pipeline

```
Source (PDF/MD/TXT/URL)
    -> Load documents
    -> Chunk (600 tokens, 100 overlap)
    -> Embed (ChromaDB default, automatic)
    -> Store in ChromaDB (persistent on disk)
```

---

## Advanced Features

### Hybrid Retrieval
Combines BM25 keyword search with vector semantic search using Reciprocal Rank Fusion (RRF). Enabled by default. Disable with `--no-hybrid` flag.

### LLM Reranking
After retrieval, the Groq LLM scores each document passage for relevance (0-10 scale). Documents are re-sorted by score before context building. Falls back gracefully to original order if the API is unavailable.

### Query Rewriting
Generates 3 alternative query phrasings using the LLM to improve retrieval recall. Includes spelling normalization and acronym expansion. Enable with `QUERY_REWRITING_ENABLED=true` or `--query-rewriting` flag.

### Multi-Hop Reasoning
For complex questions requiring information from multiple documents, the system iteratively retrieves and reasons until it has enough context (up to 3 hops). Enable with `MULTI_HOP_ENABLED=true` or `--multi-hop` flag.

### Response Caching
Optional Redis-based caching with configurable TTL. Reduces latency and API costs for repeated queries. Enable with `CACHE_ENABLED=true`.

### Observability
- Structured JSON logging via `structlog`
- Per-component latency tracking (retrieval, reranking, generation)
- Pipeline metrics endpoint (`/api/v1/metrics`)
- Query/error logging to Supabase

---

## Deployment

### Docker

```bash
docker build -t askmydoc .
docker run -p 8000:8000 --env-file .env askmydoc
```

The Docker image is lightweight -- no PyTorch or local ML model downloads required. Embeddings use ChromaDB's built-in onnxruntime backend, and all LLM inference goes through the Groq API.

### Render

The project includes a `render.yaml` blueprint for one-click deployment on [Render](https://render.com):

1. Connect your GitHub repo to Render
2. Set environment variables (`GROQ_API_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`) in the Render dashboard
3. Deploy -- Render auto-detects the blueprint

Render provisions a 1 GB persistent disk at `/data` for ChromaDB storage.

### Frontend (Vercel)

The React frontend can be deployed to Vercel:

1. Connect the `frontend/` directory to a Vercel project
2. Set `VITE_API_URL` to your deployed backend URL
3. Deploy

---

## Troubleshooting

### Backend won't start?
- Ensure `GROQ_API_KEY` is set in `.env`
- Ensure `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are set
- Run `pip install -r requirements.txt` to install all dependencies

### No results from queries?
- Ingest documents first: `python main.py ingest --source ./sample_docs/`
- Check vector store: `python main.py status`
- Ensure ChromaDB directory exists and has data

### Reranking errors?
- Check Groq API rate limits (free tier: 30 req/min)
- The system falls back to original document order on failure
- Check logs in `logs/` for detailed error information

### Embedding dimension mismatch after migration?
If upgrading from the previous sentence-transformers setup:
```bash
rm -rf chroma_db/
python main.py ingest --source ./sample_docs/
```

### Clean up old cached models
After migrating to this branch, you can reclaim ~4.6 GB of disk space:
```bash
rm -rf ~/.cache/huggingface/hub/
```

---

## License

MIT License
