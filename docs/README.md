# Production-Grade RAG System

A complete, production-ready Retrieval Augmented Generation (RAG) system with advanced features for accurate, scalable question answering over document collections.

## Features

### Phase 1: Core RAG Pipeline ✅
- **Document Ingestion**: PDF, Markdown, and web page support
- **Intelligent Chunking**: 500-800 token chunks with 100 token overlap
- **Vector Storage**: ChromaDB with metadata preservation
- **Semantic Retrieval**: Vector similarity search
- **Answer Generation**: LLM-powered answers with source citations

### Phase 2: Production Quality Retrieval ✅
- **Hybrid Retrieval**: BM25 keyword + vector semantic search with Reciprocal Rank Fusion (RRF)
- **Cross-Encoder Reranking**: Sentence-transformers for improved relevance
- **Prompt Versioning**: YAML-based configuration for easy prompt management

### Phase 3: Advanced Features ✅
- **Query Rewriting**: Spelling normalization, acronym expansion, query expansion
- **Multi-Hop Retrieval**: Iterative context gathering for complex questions
- **Context Builder**: Deduplication, relevance ordering, token limit enforcement
- **Redis Caching**: Retrieval and response caching for reduced latency
- **RAGAS Evaluation**: Comprehensive metrics (faithfulness, relevancy, precision, recall)
- **Observability**: Detailed latency tracking across all components
- **FastAPI Server**: Production-ready REST API

## Architecture

```
User Query
     │
Query Rewriting (optional)
     │
Hybrid Retrieval Layer
 ┌───────────────┬───────────────┐
 │               │               │
Vector Search   BM25 Search   Metadata Filters
 │               │               │
 └───────Merge & Deduplicate────┘
            │
Cross Encoder Re-Ranker
            │
Multi-Hop Retrieval Controller (optional)
            │
Context Builder
 ├─ Deduplication
 ├─ Relevance Ordering
 └─ Token Limit Enforcement
            │
LLM Generation
            │
Citation Generator
            │
Response Cache
            │
Final Answer
```

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd rag-system

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Required Environment Variables

```bash
# API Keys
OPENROUTER_API_KEY=your_openrouter_key
GOOGLE_API_KEY=your_google_key  # Optional

# Models
LLM_MODEL=stepfun/step-3.5-flash
EMBEDDING_MODEL=all-MiniLM-L6-v2
RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2

# Retrieval
TOP_K=5
TOP_K_INITIAL=20
CHUNK_SIZE=600
CHUNK_OVERLAP=100

# Caching (optional)
CACHE_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_TTL=3600

# Advanced Features (optional)
QUERY_REWRITING_ENABLED=true
MULTI_HOP_ENABLED=true
MAX_CONTEXT_TOKENS=4000
MAX_HOPS=3

# Evaluation
EVAL_THRESHOLD=0.7
```

## Quick Start

### 1. Ingest Documents

```python
from src.indexing.ingest import ingest_documents

# Ingest a single file
ingest_documents("path/to/document.pdf")

# Ingest a directory
ingest_documents("path/to/documents/")

# Ingest from URL
ingest_documents("https://example.com/article")
```

### 2. Query the System

```python
from src.generation.enhanced_generator import generate_answer_enhanced

result = generate_answer_enhanced(
    question="What is the main topic of the documents?",
    use_hybrid=True,
    use_reranker=True,
    use_query_rewriting=True,
    use_multi_hop=True,
    use_cache=True
)

print(result["answer"])
print(result["sources"])
```

### 3. Start the API Server

```bash
# Start the FastAPI server
uvicorn src.api.router:app --reload --port 8000

# API will be available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### 4. Use the API

```bash
# Ingest documents
curl -X POST "http://localhost:8000/api/v1/ingest" \
  -H "Content-Type: application/json" \
  -d '{"sources": ["sample_docs/"]}'

# Query
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is machine learning?",
    "use_hybrid": true,
    "use_reranker": true
  }'

# Get cache stats
curl "http://localhost:8000/api/v1/cache/stats"

# Get metrics
curl "http://localhost:8000/api/v1/metrics"

# Clear cache
curl -X POST "http://localhost:8000/api/v1/cache/clear"
```

## Evaluation

### Simple Evaluation (Heuristic-based)

```bash
python eval/evaluate.py
python eval/evaluate.py --threshold 0.8
python eval/evaluate.py --no-hybrid --no-reranker
```

### RAGAS Evaluation (Recommended)

```bash
python eval/ragas_evaluate.py
python eval/ragas_evaluate.py --threshold 0.8
```

RAGAS metrics:
- **Faithfulness**: How grounded the answer is in the retrieved context
- **Answer Relevancy**: How relevant the answer is to the question
- **Context Precision**: Precision of retrieved context
- **Context Recall**: Recall of relevant information

## Project Structure

```
rag_system/
├── src/
│   ├── api/                    # FastAPI server
│   │   ├── router.py          # API endpoints
│   │   └── schemas.py         # Request/response models
│   ├── indexing/              # Document ingestion
│   │   └── ingest.py          # Loaders, chunking, embedding
│   ├── retrieval/             # Retrieval modules
│   │   ├── base.py            # Vector retrieval
│   │   ├── hybrid.py          # BM25 + Vector with RRF
│   │   └── reranker.py        # Cross-encoder reranking
│   ├── query_rewriter/        # Query rewriting
│   │   └── rewrite_engine.py # Query expansion and normalization
│   ├── multi_hop/             # Multi-hop retrieval
│   │   └── reasoning_controller.py
│   ├── context/               # Context building
│   │   └── builder.py         # Deduplication, token limits
│   ├── generation/            # Answer generation
│   │   ├── generator.py       # Basic generator
│   │   └── enhanced_generator.py  # Full-featured generator
│   ├── caching/               # Redis caching
│   │   └── redis_cache.py     # Cache implementation
│   ├── observability/         # Monitoring
│   │   └── latency_tracker.py # Latency tracking
│   ├── core/                  # Configuration
│   │   └── config.py          # Environment config
│   └── utils/                 # Utilities
│       └── logger.py          # Structured logging
├── eval/                      # Evaluation
│   ├── evaluate.py            # Simple evaluation
│   ├── ragas_evaluate.py      # RAGAS evaluation
│   └── golden_dataset.json    # Test dataset
├── config/                    # Configuration files
│   └── prompts_v1.yaml        # Versioned prompts
├── sample_docs/               # Sample documents
├── requirements.txt           # Dependencies
├── main.py                    # CLI entry point
└── README.md                  # This file
```

## Advanced Usage

### Query Rewriting

```python
from src.query_rewriter import QueryRewriter

rewriter = QueryRewriter()
queries = rewriter.rewrite("ml memory issues")
# Returns: [
#   "ml memory issues",
#   "machine learning memory limitations",
#   "memory complexity in ML models",
#   "ML memory optimization techniques"
# ]
```

### Multi-Hop Retrieval

```python
from src.multi_hop import MultiHopController

controller = MultiHopController(max_hops=3)

# Automatically detects if multi-hop is needed
result = controller.execute_multi_hop_retrieval(
    question="Which drugs approved in 2022 treat diseases discovered after 2015?",
    retriever_fn=my_retriever_function
)

print(f"Used {result['hop_count']} hops")
print(f"Retrieved {len(result['documents'])} documents")
```

### Context Building

```python
from src.context import ContextBuilder

builder = ContextBuilder(max_tokens=4000)

result = builder.build(documents)

print(f"Original: {result['stats']['original_count']} docs")
print(f"Final: {result['stats']['final_count']} docs")
print(f"Tokens: {result['stats']['tokens_used']}")
print(result['context'])
```

### Caching

```python
from src.caching import get_cache

cache = get_cache(enabled=True)

# Cache is automatically used by enhanced_generator
# Manual cache operations:
cache.clear_all()
stats = cache.get_stats()
print(f"Hit rate: {stats['hit_rate']:.2%}")
```

### Latency Tracking

```python
from src.observability import LatencyTracker

tracker = LatencyTracker()
tracker.start()

with tracker.track("retrieval", method="hybrid"):
    # ... retrieval code ...
    pass

with tracker.track("generation"):
    # ... generation code ...
    pass

tracker.end()
summary = tracker.get_summary()
print(f"Total time: {summary['total_time_ms']}ms")
```

## Performance Optimization

### Caching Strategy

1. **Retrieval Cache**: Caches query → documents mapping
2. **Response Cache**: Caches query + context → answer mapping
3. **TTL**: Default 1 hour (configurable)

Expected improvements:
- Cache hit: ~50-100ms response time
- Cache miss: ~1-3s response time

### Token Optimization

The context builder automatically:
- Removes duplicate chunks
- Orders by relevance score
- Enforces token limits (default 4000)
- Truncates intelligently when needed

### Retrieval Optimization

- **Hybrid retrieval**: Combines keyword and semantic search
- **RRF fusion**: Merges results effectively
- **Reranking**: Cross-encoder for final relevance scoring
- **Top-K tuning**: Retrieve 20, rerank to 5

## Monitoring and Observability

### Structured Logging

All components use structured logging with `structlog`:

```json
{
  "event": "retrieval completed",
  "component": "hybrid_retriever",
  "duration_ms": 145.23,
  "bm25_candidates": 20,
  "vector_candidates": 20,
  "merged_results": 15
}
```

### Metrics Endpoint

```bash
curl http://localhost:8000/api/v1/metrics
```

Returns:
- Total executions
- Success rate
- Latency percentiles (p50, p95, p99)
- Component-level timing

### Latency Breakdown

Track time spent in each component:
- Query rewriting: ~200-500ms
- Retrieval: ~100-300ms
- Reranking: ~50-150ms
- Multi-hop: ~500-2000ms (if used)
- Context building: ~10-50ms
- LLM generation: ~800-2000ms

## Testing

```bash
# Run evaluation
python eval/evaluate.py

# Run RAGAS evaluation
python eval/ragas_evaluate.py

# Test API
pytest tests/  # (if tests are added)
```

## CI/CD Integration

The evaluation pipeline can be integrated into CI/CD:

```yaml
# .github/workflows/quality-check.yml
- name: Run RAG Evaluation
  run: |
    python eval/ragas_evaluate.py --threshold 0.8
```

Exit codes:
- `0`: All checks passed
- `1`: Quality below threshold

## Troubleshooting

### Redis Connection Issues

If Redis is not available, caching will be automatically disabled:

```
WARNING: Redis not installed. Caching will be disabled.
```

Install Redis:
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Or use Docker
docker run -d -p 6379:6379 redis:latest
```

### Memory Issues

If you encounter memory issues with large document collections:

1. Reduce `TOP_K_INITIAL` (default 20)
2. Reduce `MAX_CONTEXT_TOKENS` (default 4000)
3. Disable multi-hop retrieval
4. Use smaller embedding models

### Slow Performance

1. Enable caching: `CACHE_ENABLED=true`
2. Reduce `TOP_K` and `TOP_K_INITIAL`
3. Disable query rewriting for simple queries
4. Use faster LLM models

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure evaluation passes
5. Submit a pull request

## License

[Your License Here]

## Acknowledgments

- LangChain for RAG framework
- ChromaDB for vector storage
- RAGAS for evaluation metrics
- Sentence-Transformers for embeddings and reranking
