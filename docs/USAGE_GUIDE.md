# Ask My Doc - Usage Guide

Complete guide for using the production-grade RAG system.

## Table of Contents

1. [Quick Start](#quick-start)
2. [CLI Commands](#cli-commands)
3. [API Usage](#api-usage)
4. [Advanced Features](#advanced-features)
5. [Configuration](#configuration)
6. [Evaluation](#evaluation)
7. [Troubleshooting](#troubleshooting)

## Quick Start

### 1. Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Optional: Start Redis for caching
docker run -d -p 6379:6379 redis:latest
```

### 2. Ingest Documents

```bash
# Ingest a single file
python main.py ingest --source document.pdf

# Ingest a directory
python main.py ingest --source ./docs/

# Ingest from URL
python main.py ingest --source https://example.com/article

# Multiple sources
python main.py ingest --source doc1.pdf doc2.md ./docs/
```

### 3. Query

```bash
# Basic query
python main.py query "What is machine learning?"

# With all features enabled
python main.py query "What is ML?" \
  --query-rewriting \
  --multi-hop \
  --cache \
  --verbose
```

## CLI Commands

### Ingest

Ingest documents into the vector store.

```bash
python main.py ingest --source <path> [options]

Options:
  --source, -s      File path(s), directory, or URL(s) (required)
  --chunk-size      Override default chunk size (default: 600)
  --chunk-overlap   Override default chunk overlap (default: 100)
```

Examples:

```bash
# Custom chunking
python main.py ingest --source docs/ --chunk-size 800 --chunk-overlap 150

# Multiple sources
python main.py ingest -s doc1.pdf -s doc2.md -s https://example.com
```

### Query

Ask questions to the RAG system.

```bash
python main.py query "<question>" [options]

Options:
  --top-k N             Number of chunks to retrieve (default: 5)
  --no-hybrid           Disable hybrid retrieval (vector only)
  --no-reranker         Disable cross-encoder reranking
  --query-rewriting     Enable query rewriting
  --multi-hop           Enable multi-hop retrieval
  --cache               Enable caching
  --verbose, -v         Show detailed metadata
  --json                Output in JSON format
```

Examples:

```bash
# Basic query
python main.py query "What is the main topic?"

# With hybrid retrieval and reranking (default)
python main.py query "Explain transformers"

# With all advanced features
python main.py query "What drugs treat diseases discovered after 2015?" \
  --query-rewriting \
  --multi-hop \
  --cache \
  --verbose

# Vector-only retrieval
python main.py query "What is ML?" --no-hybrid --no-reranker

# JSON output
python main.py query "What is AI?" --json > result.json
```

### Status

Check vector store status.

```bash
python main.py status
```

### Cache

Manage Redis cache.

```bash
# View cache statistics
python main.py cache stats

# Clear all cached data
python main.py cache clear
```

### Eval

Run evaluation pipeline.

```bash
python main.py eval [options]

Options:
  --dataset PATH        Path to golden dataset (default: eval/golden_dataset.json)
  --threshold FLOAT     Quality threshold (default: 0.7)
  --no-hybrid           Disable hybrid retrieval
  --no-reranker         Disable reranker
  --ragas               Use RAGAS evaluation (recommended)
```

Examples:

```bash
# Simple evaluation
python main.py eval

# RAGAS evaluation (recommended)
python main.py eval --ragas

# Custom threshold
python main.py eval --ragas --threshold 0.85

# Custom dataset
python main.py eval --dataset my_dataset.json --ragas
```

### Serve

Start the FastAPI server.

```bash
python main.py serve [options]

Options:
  --host HOST     Host to bind to (default: 0.0.0.0)
  --port PORT     Port to bind to (default: 8000)
```

Example:

```bash
# Start server
python main.py serve

# Custom host/port
python main.py serve --host localhost --port 8080
```

## API Usage

### Start Server

```bash
python main.py serve
```

API documentation available at: http://localhost:8000/docs

### Endpoints

#### POST /api/v1/ingest

Ingest documents.

```bash
curl -X POST "http://localhost:8000/api/v1/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "sources": ["sample_docs/"],
    "chunk_size": 600,
    "chunk_overlap": 100
  }'
```

Response:

```json
{
  "status": "success",
  "chunks_ingested": 42,
  "sources": ["sample_docs/"]
}
```

#### POST /api/v1/query

Query the RAG system.

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is machine learning?",
    "top_k": 5,
    "use_hybrid": true,
    "use_reranker": true
  }'
```

Response:

```json
{
  "answer": "Machine learning is...",
  "sources": [
    {
      "source": "ml_intro.pdf",
      "page": 3,
      "reranker_score": 0.95
    }
  ],
  "context_chunks": 5
}
```

#### GET /health

Health check.

```bash
curl "http://localhost:8000/health"
```

#### GET /api/v1/cache/stats

Get cache statistics.

```bash
curl "http://localhost:8000/api/v1/cache/stats"
```

Response:

```json
{
  "cache_stats": {
    "enabled": true,
    "connected": true,
    "total_rag_keys": 15,
    "hit_rate": 0.67
  }
}
```

#### POST /api/v1/cache/clear

Clear cache.

```bash
curl -X POST "http://localhost:8000/api/v1/cache/clear"
```

#### GET /api/v1/metrics

Get pipeline metrics.

```bash
curl "http://localhost:8000/api/v1/metrics"
```

Response:

```json
{
  "metrics": {
    "total_executions": 100,
    "success_rate": 0.98,
    "latency": {
      "avg_ms": 1250,
      "p50_ms": 1100,
      "p95_ms": 2000,
      "p99_ms": 3500
    }
  }
}
```

## Advanced Features

### Query Rewriting

Improves retrieval by generating alternative query phrasings.

```bash
# CLI
python main.py query "ml memory issues" --query-rewriting

# Python
from src.query_rewriter import QueryRewriter

rewriter = QueryRewriter()
queries = rewriter.rewrite("ml memory issues")
# Returns: ["ml memory issues", "machine learning memory limitations", ...]
```

### Multi-Hop Retrieval

For complex questions requiring multiple reasoning steps.

```bash
# CLI
python main.py query "Which drugs approved in 2022 treat diseases discovered after 2015?" \
  --multi-hop

# Python
from src.multi_hop import MultiHopController

controller = MultiHopController(max_hops=3)
result = controller.execute_multi_hop_retrieval(question, retriever_fn)
```

### Context Building

Optimizes context with deduplication and token limits.

```python
from src.context import ContextBuilder

builder = ContextBuilder(max_tokens=4000)
result = builder.build(documents)

print(f"Tokens used: {result['stats']['tokens_used']}")
print(result['context'])
```

### Caching

Redis-based caching for improved performance.

```bash
# Enable in .env
CACHE_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379

# Use with CLI
python main.py query "What is AI?" --cache

# Check stats
python main.py cache stats

# Clear cache
python main.py cache clear
```

### Latency Tracking

Comprehensive timing across all components.

```python
from src.observability import LatencyTracker

tracker = LatencyTracker()
tracker.start()

with tracker.track("retrieval"):
    # ... retrieval code ...
    pass

tracker.end()
summary = tracker.get_summary()
```

## Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Required
OPENROUTER_API_KEY=your_key

# Models
LLM_MODEL=stepfun/step-3.5-flash
EMBEDDING_MODEL=all-MiniLM-L6-v2
RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2

# Retrieval
TOP_K=5                    # Final number of chunks
TOP_K_INITIAL=20           # Before reranking
CHUNK_SIZE=600
CHUNK_OVERLAP=100

# Advanced Features
CACHE_ENABLED=true
QUERY_REWRITING_ENABLED=true
MULTI_HOP_ENABLED=true
MAX_CONTEXT_TOKENS=4000
MAX_HOPS=3

# Evaluation
EVAL_THRESHOLD=0.7
```

### Prompt Versioning

Edit prompts in `config/prompts_v1.yaml`:

```yaml
version: "1.0"
qa_prompt:
  system: |
    You are a knowledgeable assistant...
  user: |
    Context: {context}
    Question: {question}
```

Change version:

```bash
PROMPT_VERSION=v2
```

## Evaluation

### Golden Dataset Format

`eval/golden_dataset.json`:

```json
{
  "dataset": [
    {
      "id": "q1",
      "question": "What is machine learning?",
      "ground_truth_answer": "Machine learning is...",
      "expected_sources": ["ml_intro.md"],
      "difficulty": "easy"
    }
  ]
}
```

### Simple Evaluation

Uses heuristic metrics (token overlap).

```bash
python main.py eval
```

### RAGAS Evaluation

Uses comprehensive RAGAS metrics (recommended).

```bash
python main.py eval --ragas
```

Metrics:
- **Faithfulness**: Answer grounded in context
- **Answer Relevancy**: Answer relevance to question
- **Context Precision**: Precision of retrieved context
- **Context Recall**: Recall of relevant information

### CI/CD Integration

```yaml
# .github/workflows/quality.yml
- name: Run Evaluation
  run: python main.py eval --ragas --threshold 0.8
```

Exit codes:
- `0`: Passed
- `1`: Failed

## Troubleshooting

### Redis Connection Failed

```
❌ Cache is enabled but not connected to Redis
```

Solution:

```bash
# Start Redis
docker run -d -p 6379:6379 redis:latest

# Or disable caching
CACHE_ENABLED=false
```

### Out of Memory

Solution:

```bash
# Reduce retrieval size
TOP_K=3
TOP_K_INITIAL=10

# Reduce context size
MAX_CONTEXT_TOKENS=2000

# Disable multi-hop
MULTI_HOP_ENABLED=false
```

### Slow Performance

Solutions:

1. Enable caching: `CACHE_ENABLED=true`
2. Reduce `TOP_K` and `TOP_K_INITIAL`
3. Use faster models
4. Disable query rewriting for simple queries

### API Key Errors

```
❌ Configuration error: OPENROUTER_API_KEY is not set
```

Solution:

```bash
# Add to .env
OPENROUTER_API_KEY=your_key_here
```

### Import Errors

```
ModuleNotFoundError: No module named 'redis'
```

Solution:

```bash
pip install -r requirements.txt
```

## Performance Tips

### Optimal Configuration

For best balance of quality and speed:

```bash
TOP_K=5
TOP_K_INITIAL=20
CHUNK_SIZE=600
CHUNK_OVERLAP=100
CACHE_ENABLED=true
QUERY_REWRITING_ENABLED=false  # Enable for complex queries
MULTI_HOP_ENABLED=false        # Enable for multi-step questions
```

### Latency Expectations

- **Cache hit**: 50-100ms
- **Cache miss**: 1-3s
- **With query rewriting**: +200-500ms
- **With multi-hop**: +500-2000ms

### Caching Strategy

1. Enable for production: `CACHE_ENABLED=true`
2. Set appropriate TTL: `REDIS_TTL=3600` (1 hour)
3. Monitor hit rate: `python main.py cache stats`
4. Clear when updating documents: `python main.py cache clear`

## Support

For issues or questions:

1. Check this guide
2. Review logs in `logs/`
3. Check API docs at `/docs`
4. Review code documentation

## Next Steps

1. Ingest your documents
2. Test with sample queries
3. Run evaluation
4. Enable advanced features as needed
5. Deploy API server
6. Monitor metrics and optimize
