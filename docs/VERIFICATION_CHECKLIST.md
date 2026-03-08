# Verification Checklist

Use this checklist to verify that all features are working correctly.

## Prerequisites

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] `.env` file created with `OPENROUTER_API_KEY`
- [ ] (Optional) Redis running for caching tests

## Phase 1: Core RAG Pipeline

### Document Ingestion

- [ ] Ingest sample documents:
  ```bash
  python main.py ingest --source sample_docs/
  ```
- [ ] Verify success message shows chunks ingested
- [ ] Check vector store status:
  ```bash
  python main.py status
  ```

### Basic Query

- [ ] Run a basic query:
  ```bash
  python main.py query "What is machine learning?"
  ```
- [ ] Verify answer is generated
- [ ] Verify sources are listed
- [ ] Check logs in `logs/` directory

## Phase 2: Production Quality Retrieval

### Hybrid Retrieval

- [ ] Query with hybrid retrieval (default):
  ```bash
  python main.py query "What is NLP?" --verbose
  ```
- [ ] Verify metadata shows hybrid retrieval used
- [ ] Check for BM25 and vector scores in logs

### Reranking

- [ ] Query with reranking (default):
  ```bash
  python main.py query "Explain transformers" --verbose
  ```
- [ ] Verify reranker scores in sources
- [ ] Check metadata shows reranking used

### Prompt Versioning

- [ ] Verify prompt config exists:
  ```bash
  ls config/prompts_v1.yaml
  ```
- [ ] Check prompt is loaded in logs

## Phase 3: Advanced Features

### Query Rewriting

- [ ] Test query rewriting:
  ```bash
  python main.py query "ml memory issues" --query-rewriting --verbose
  ```
- [ ] Verify multiple queries generated in metadata
- [ ] Check logs for rewritten queries

### Multi-Hop Retrieval

- [ ] Test multi-hop (if you have complex questions):
  ```bash
  python main.py query "Which drugs approved in 2022 treat diseases discovered after 2015?" --multi-hop --verbose
  ```
- [ ] Verify hop count in metadata
- [ ] Check logs for follow-up queries

### Context Builder

- [ ] Query with verbose output:
  ```bash
  python main.py query "What is AI?" --verbose
  ```
- [ ] Verify context stats in metadata:
  - Original chunk count
  - Final chunk count
  - Tokens used
  - Duplicates removed

### Caching (Requires Redis)

- [ ] Start Redis:
  ```bash
  docker run -d -p 6379:6379 redis:latest
  ```
- [ ] Enable caching in `.env`:
  ```bash
  CACHE_ENABLED=true
  ```
- [ ] First query (cache miss):
  ```bash
  python main.py query "What is machine learning?" --cache --verbose
  ```
- [ ] Note the total time
- [ ] Second query (cache hit):
  ```bash
  python main.py query "What is machine learning?" --cache --verbose
  ```
- [ ] Verify much faster (should show cache_hit: true in metadata)
- [ ] Check cache stats:
  ```bash
  python main.py cache stats
  ```
- [ ] Verify hit rate > 0
- [ ] Clear cache:
  ```bash
  python main.py cache clear
  ```

### Observability

- [ ] Run query with verbose:
  ```bash
  python main.py query "What is AI?" --verbose
  ```
- [ ] Verify timing breakdown in metadata:
  - Total time
  - Component breakdown (retrieval, reranking, generation, etc.)
- [ ] Check structured logs in `logs/`

## Evaluation

### Simple Evaluation

- [ ] Run simple evaluation:
  ```bash
  python main.py eval
  ```
- [ ] Verify evaluation completes
- [ ] Check results in `eval/results/`
- [ ] Verify metrics are calculated

### RAGAS Evaluation

- [ ] Run RAGAS evaluation:
  ```bash
  python main.py eval --ragas
  ```
- [ ] Verify RAGAS metrics:
  - Faithfulness
  - Answer Relevancy
  - Context Precision
  - Context Recall
- [ ] Check results saved to `eval/results/`
- [ ] Verify pass/fail based on threshold

## API Server

### Start Server

- [ ] Start the API server:
  ```bash
  python main.py serve
  ```
- [ ] Verify server starts without errors
- [ ] Access API docs: http://localhost:8000/docs
- [ ] Verify all endpoints are listed

### Test Endpoints

- [ ] Health check:
  ```bash
  curl "http://localhost:8000/health"
  ```

- [ ] Ingest via API:
  ```bash
  curl -X POST "http://localhost:8000/api/v1/ingest" \
    -H "Content-Type: application/json" \
    -d '{"sources": ["sample_docs/"]}'
  ```

- [ ] Query via API:
  ```bash
  curl -X POST "http://localhost:8000/api/v1/query" \
    -H "Content-Type: application/json" \
    -d '{"question": "What is ML?", "use_hybrid": true, "use_reranker": true}'
  ```

- [ ] Cache stats:
  ```bash
  curl "http://localhost:8000/api/v1/cache/stats"
  ```

- [ ] Metrics:
  ```bash
  curl "http://localhost:8000/api/v1/metrics"
  ```

- [ ] Clear cache:
  ```bash
  curl -X POST "http://localhost:8000/api/v1/cache/clear"
  ```

## Python API

### Import Tests

- [ ] Test imports:
  ```python
  from src.query_rewriter import QueryRewriter
  from src.multi_hop import MultiHopController
  from src.context import ContextBuilder
  from src.caching import get_cache
  from src.observability import LatencyTracker
  from src.generation.enhanced_generator import generate_answer_enhanced
  ```

### Query Rewriter

- [ ] Test query rewriter:
  ```python
  from src.query_rewriter import QueryRewriter
  
  rewriter = QueryRewriter()
  queries = rewriter.rewrite("ml memory issues")
  print(queries)
  ```
- [ ] Verify multiple queries returned

### Context Builder

- [ ] Test context builder:
  ```python
  from src.context import ContextBuilder
  from src.retrieval.base import retrieve_chunks
  
  docs = retrieve_chunks("What is AI?", top_k=10)
  builder = ContextBuilder(max_tokens=2000)
  result = builder.build(docs)
  
  print(f"Original: {result['stats']['original_count']}")
  print(f"Final: {result['stats']['final_count']}")
  print(f"Tokens: {result['stats']['tokens_used']}")
  ```

### Latency Tracker

- [ ] Test latency tracker:
  ```python
  from src.observability import LatencyTracker
  import time
  
  tracker = LatencyTracker()
  tracker.start()
  
  with tracker.track("test_component"):
      time.sleep(0.1)
  
  tracker.end()
  summary = tracker.get_summary()
  print(summary)
  ```

## Configuration

### Environment Variables

- [ ] Verify all config variables are recognized:
  ```python
  from src.core.config import (
      CACHE_ENABLED,
      QUERY_REWRITING_ENABLED,
      MULTI_HOP_ENABLED,
      MAX_CONTEXT_TOKENS,
      MAX_HOPS,
      REDIS_HOST,
      REDIS_PORT
  )
  print(f"Cache: {CACHE_ENABLED}")
  print(f"Query Rewriting: {QUERY_REWRITING_ENABLED}")
  print(f"Multi-Hop: {MULTI_HOP_ENABLED}")
  ```

## Documentation

- [ ] README.md exists and is complete
- [ ] USAGE_GUIDE.md exists and is complete
- [ ] IMPLEMENTATION_SUMMARY.md exists
- [ ] QUICK_REFERENCE.md exists
- [ ] This checklist exists

## Final Integration Test

- [ ] Run complete workflow:
  ```bash
  # 1. Ingest
  python main.py ingest --source sample_docs/
  
  # 2. Query with all features
  python main.py query "What is machine learning?" \
    --query-rewriting \
    --multi-hop \
    --cache \
    --verbose
  
  # 3. Check cache
  python main.py cache stats
  
  # 4. Run evaluation
  python main.py eval --ragas
  
  # 5. Start server
  python main.py serve &
  
  # 6. Test API
  curl -X POST "http://localhost:8000/api/v1/query" \
    -H "Content-Type: application/json" \
    -d '{"question": "What is AI?"}'
  ```

## Troubleshooting

If any test fails:

1. Check logs in `logs/` directory
2. Verify `.env` configuration
3. Check Redis is running (for cache tests)
4. Verify API keys are set
5. Check Python version (3.8+)
6. Reinstall dependencies: `pip install -r requirements.txt`

## Success Criteria

✅ All checkboxes above are checked
✅ No errors in logs
✅ Evaluation passes threshold
✅ API server responds correctly
✅ Cache hit rate > 0 (if Redis enabled)
✅ All imports work
✅ Documentation is complete

## Next Steps

Once all tests pass:

1. Configure for your use case
2. Ingest your documents
3. Tune parameters (TOP_K, thresholds, etc.)
4. Deploy to production
5. Set up monitoring
6. Run regular evaluations

## Notes

- Some tests require Redis (caching tests)
- Multi-hop tests work best with complex questions
- RAGAS evaluation may take several minutes
- Cache hit rate improves over time with repeated queries
