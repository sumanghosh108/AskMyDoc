# PostgreSQL Logging and Observability System
## Production-Grade RAG Pipeline Monitoring

---

## Overview

This module provides a comprehensive PostgreSQL-based logging and observability system for the RAG platform. It tracks query execution, errors, latency metrics, and evaluation results with production-grade reliability.

### Features

✅ **Query Tracing** - Track all queries with detailed metrics  
✅ **Latency Tracking** - Component-level performance monitoring  
✅ **Error Logging** - Comprehensive error capture with stack traces  
✅ **Evaluation Metrics** - RAGAS and custom evaluation tracking  
✅ **Cache Statistics** - Cache performance monitoring  
✅ **System Health** - Overall system health metrics  
✅ **Idempotent Setup** - Safe to run multiple times  
✅ **Connection Pooling** - Efficient database connections  

---

## Quick Start

### 1. Install Dependencies

```bash
pip install psycopg2-binary
```

### 2. Configure Environment

⚠️ **SECURITY WARNING**: Never commit credentials to version control!

Add to your `.env` file (copy from `.env.example`):

```env
# PostgreSQL Configuration
# IMPORTANT: Change these credentials in production!
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password_here  # ⚠️ CHANGE THIS!
POSTGRES_DB=AskMyDocLOG
POSTGRES_MIN_CONN=2
POSTGRES_MAX_CONN=10
```

**Security Best Practices:**
- ✅ Use strong passwords (16+ characters, mixed case, numbers, symbols)
- ✅ Store credentials in `.env` file (already in `.gitignore`)
- ✅ Use different credentials for dev/staging/production
- ✅ Rotate passwords regularly
- ✅ Use environment-specific `.env` files
- ✅ Consider using secrets management (AWS Secrets Manager, HashiCorp Vault)
- ❌ Never hardcode credentials in source code
- ❌ Never commit `.env` to version control
- ❌ Never use default passwords in production

### 3. Initialize Database

```python
from database import initialize_database

# Initialize database and tables (idempotent)
result = initialize_database()

if result['success']:
    print("✅ Database initialized successfully")
else:
    print(f"❌ Initialization failed: {result['error']}")
```

Or run directly:

```bash
python database/db_initializer.py
```

### 4. Start Logging

```python
from database import QueryLogger, ErrorLogger

# Log a query
query_logger = QueryLogger()
query_logger.log_query(
    query_text="What is machine learning?",
    total_latency=1500.0,
    retrieval_latency=400.0,
    llm_latency=1000.0,
    model_used="gpt-4"
)

# Log an error
error_logger = ErrorLogger()
error_logger.log_error(
    pipeline_stage="retrieval",
    error_message="Vector database connection failed",
    query_text="What is ML?",
    severity="ERROR"
)
```

---

## Architecture

### Database Schema

```
AskMyDocLOG (Database)
├── rag_query_logs          # Query execution metrics
├── rag_error_logs          # Pipeline errors
├── rag_evaluation_metrics  # RAGAS and evaluation scores
├── rag_component_latency   # Component-level latency
├── rag_cache_stats         # Cache performance
└── rag_system_health       # System health metrics
```

### Module Structure

```
database/
├── __init__.py              # Package exports
├── README.md                # This file
├── schema.sql               # PostgreSQL schema
├── db_initializer.py        # Idempotent database setup
├── postgres_client.py       # Connection pool manager
├── query_logger.py          # Query metrics logging
├── error_logger.py          # Error logging
└── evaluation_logger.py     # Evaluation metrics logging
```

---

## Database Tables

### 1. rag_query_logs

Tracks all query executions with latency and performance metrics.

**Columns:**
- `id` - Primary key
- `timestamp` - Query execution time
- `query_text` - User query
- `retrieval_latency` - Retrieval time (ms)
- `rerank_latency` - Reranking time (ms)
- `llm_latency` - LLM generation time (ms)
- `total_latency` - Total pipeline time (ms)
- `retrieved_chunks` - Number of chunks retrieved
- `reranked_chunks` - Number of chunks after reranking
- `model_used` - LLM model name
- `embedding_model` - Embedding model name
- `query_rewriting_enabled` - Query rewriting flag
- `multi_hop_enabled` - Multi-hop flag
- `cache_hit` - Cache hit flag
- `answer_length` - Generated answer length
- `source_count` - Number of sources cited
- `is_slow_query` - Auto-computed (>2000ms)

**Indexes:**
- `idx_query_logs_timestamp` - Time-based queries
- `idx_query_logs_total_latency` - Latency analysis
- `idx_query_logs_slow_queries` - Slow query detection
- `idx_query_logs_model` - Model performance

---

### 2. rag_error_logs

Captures pipeline failures and errors for debugging.

**Columns:**
- `id` - Primary key
- `timestamp` - Error occurrence time
- `query_text` - Query that caused error
- `pipeline_stage` - Stage where error occurred
- `error_type` - Error class/type
- `error_message` - Error description
- `stack_trace` - Full stack trace
- `severity` - DEBUG, INFO, WARNING, ERROR, CRITICAL
- `user_id` - User identifier
- `session_id` - Session identifier
- `metadata` - Additional context (JSONB)

**Indexes:**
- `idx_error_logs_timestamp` - Time-based queries
- `idx_error_logs_stage` - Stage analysis
- `idx_error_logs_severity` - Severity filtering
- `idx_error_logs_error_type` - Error type analysis

---

### 3. rag_evaluation_metrics

Stores RAGAS and other evaluation metrics.

**Columns:**
- `id` - Primary key
- `timestamp` - Evaluation time
- `faithfulness_score` - RAGAS faithfulness (0-1)
- `answer_correctness` - RAGAS correctness (0-1)
- `context_precision` - RAGAS precision (0-1)
- `context_recall` - RAGAS recall (0-1)
- `overall_score` - Average of all metrics (computed)
- `test_query` - Test query text
- `expected_answer` - Ground truth answer
- `actual_answer` - Generated answer
- `evaluation_run_id` - Evaluation run identifier
- `dataset_name` - Dataset name
- `passed_threshold` - Pass/fail flag

**Indexes:**
- `idx_eval_metrics_timestamp` - Time-based queries
- `idx_eval_metrics_run_id` - Run-based queries
- `idx_eval_metrics_overall_score` - Score analysis

---

### 4. rag_component_latency

Detailed latency breakdown for each pipeline component.

**Columns:**
- `id` - Primary key
- `query_log_id` - Foreign key to rag_query_logs
- `timestamp` - Measurement time
- `component_name` - Component identifier
- `latency_ms` - Component latency (ms)
- `metadata` - Additional context (JSONB)

---

### 5. rag_cache_stats

Tracks cache performance and hit rates.

**Columns:**
- `id` - Primary key
- `timestamp` - Measurement time
- `cache_type` - retrieval, response, embedding
- `hit_count` - Number of cache hits
- `miss_count` - Number of cache misses
- `hit_rate` - Computed hit rate
- `window_start` - Time window start
- `window_end` - Time window end

---

### 6. rag_system_health

Overall system health metrics.

**Columns:**
- `id` - Primary key
- `timestamp` - Measurement time
- `total_queries` - Total query count
- `successful_queries` - Successful query count
- `failed_queries` - Failed query count
- `success_rate` - Computed success rate
- `avg_total_latency` - Average total latency
- `avg_retrieval_latency` - Average retrieval latency
- `avg_llm_latency` - Average LLM latency
- `cpu_usage_percent` - CPU usage
- `memory_usage_mb` - Memory usage
- `window_start` - Time window start
- `window_end` - Time window end

---

## Usage Examples

### Query Logging

```python
from database import get_query_logger

logger = get_query_logger()

# Log query with all metrics
query_id = logger.log_query(
    query_text="What is machine learning?",
    total_latency=1500.0,
    retrieval_latency=400.0,
    rerank_latency=200.0,
    llm_latency=900.0,
    retrieved_chunks=10,
    reranked_chunks=5,
    model_used="gpt-4",
    embedding_model="text-embedding-3-small",
    query_rewriting_enabled=True,
    multi_hop_enabled=False,
    cache_hit=False,
    answer_length=250,
    source_count=3
)

# Log component latency
logger.log_component_latency(
    query_log_id=query_id,
    component_name="query_rewriting",
    latency_ms=150.0,
    metadata={"variations_generated": 3}
)

# Get recent queries
recent = logger.get_recent_queries(limit=10)

# Get slow queries only
slow_queries = logger.get_recent_queries(limit=10, slow_only=True)

# Get latency statistics
stats = logger.get_latency_stats(hours=24)
print(f"Average latency: {stats['avg_total_latency']}ms")
print(f"P95 latency: {stats['p95_latency']}ms")
print(f"Slow queries: {stats['slow_query_count']}")

# Get model performance comparison
models = logger.get_model_performance()
for model in models:
    print(f"{model['model_used']}: {model['avg_latency']}ms avg")
```

---

### Error Logging

```python
from database import get_error_logger

error_logger = get_error_logger()

# Log error manually
error_logger.log_error(
    pipeline_stage="retrieval",
    error_message="Vector database connection failed",
    query_text="What is ML?",
    error_type="ConnectionError",
    severity="ERROR",
    metadata={"host": "localhost", "port": 6333}
)

# Log exception automatically
try:
    # Some operation
    result = risky_operation()
except Exception as e:
    error_logger.log_exception(
        exception=e,
        pipeline_stage="generation",
        query_text="What is NLP?",
        severity="ERROR"
    )

# Get recent errors
errors = error_logger.get_recent_errors(limit=10)

# Get errors by stage
errors_by_stage = error_logger.get_errors_by_stage(hours=24)

# Get error summary
summary = error_logger.get_error_summary(hours=24)
print(f"Total errors: {summary['total_errors']}")
print(f"Critical: {summary['critical_count']}")
print(f"Affected stages: {summary['affected_stages']}")

# Get top errors
top_errors = error_logger.get_top_errors(limit=10, hours=24)
```

---

### Evaluation Logging

```python
from database import get_evaluation_logger

eval_logger = get_evaluation_logger()

# Log single evaluation
eval_logger.log_evaluation(
    faithfulness_score=0.92,
    answer_correctness=0.88,
    context_precision=0.85,
    context_recall=0.90,
    test_query="What is machine learning?",
    expected_answer="ML is a subset of AI...",
    actual_answer="Machine learning is...",
    evaluation_run_id="run_2026_03_08",
    dataset_name="golden_dataset",
    passed_threshold=True
)

# Log batch evaluation
evaluations = [
    {
        "faithfulness_score": 0.92,
        "answer_correctness": 0.88,
        "test_query": "What is ML?",
        "passed_threshold": True
    },
    # ... more evaluations
]

count = eval_logger.log_batch_evaluation(
    evaluations=evaluations,
    evaluation_run_id="run_2026_03_08",
    dataset_name="golden_dataset"
)

# Get evaluation summary
summary = eval_logger.get_evaluation_summary(
    evaluation_run_id="run_2026_03_08"
)
print(f"Average faithfulness: {summary['avg_faithfulness']}")
print(f"Passed: {summary['passed_count']}/{summary['total_evaluations']}")

# Get evaluation trends
trends = eval_logger.get_evaluation_trends(days=7)
```

---

## Analytics Queries

### Average Latency

```sql
SELECT AVG(total_latency) as avg_latency
FROM rag_query_logs
WHERE timestamp > NOW() - INTERVAL '24 hours';
```

### Slow Queries

```sql
SELECT query_text, total_latency, timestamp
FROM rag_query_logs
WHERE is_slow_query = TRUE
ORDER BY total_latency DESC
LIMIT 10;
```

### Error Rate by Stage

```sql
SELECT 
    pipeline_stage,
    COUNT(*) as error_count,
    COUNT(DISTINCT error_type) as unique_errors
FROM rag_error_logs
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY pipeline_stage
ORDER BY error_count DESC;
```

### Model Performance

```sql
SELECT 
    model_used,
    COUNT(*) as query_count,
    AVG(llm_latency) as avg_latency,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY llm_latency) as p95_latency
FROM rag_query_logs
WHERE model_used IS NOT NULL
GROUP BY model_used
ORDER BY query_count DESC;
```

### Hourly Query Volume

```sql
SELECT 
    DATE_TRUNC('hour', timestamp) as hour,
    COUNT(*) as query_count,
    AVG(total_latency) as avg_latency
FROM rag_query_logs
WHERE timestamp > NOW() - INTERVAL '7 days'
GROUP BY DATE_TRUNC('hour', timestamp)
ORDER BY hour DESC;
```

---

## Performance Targets

| Metric | Target | Threshold |
|--------|--------|-----------|
| Average Pipeline Latency | < 2 seconds | 2000ms |
| Retrieval Latency | < 200ms | 500ms |
| LLM Generation Latency | < 1.5 seconds | 2000ms |
| Error Rate | < 1% | 5% |
| Cache Hit Rate | > 50% | 30% |

---

## Maintenance

### Cleanup Old Logs

```sql
-- Clean logs older than 90 days
SELECT * FROM cleanup_old_logs(90);
```

### Database Statistics

```python
from database.db_initializer import get_database_stats

stats = get_database_stats()
print(f"Query logs: {stats['query_logs_count']}")
print(f"Error logs: {stats['error_logs_count']}")
print(f"Database size: {stats['database_size']}")
```

### Connection Pool Status

```python
from database import get_client

client = get_client()
status = client.get_pool_status()
print(f"Min connections: {status['min_connections']}")
print(f"Max connections: {status['max_connections']}")
```

---

## Troubleshooting

### Database Connection Failed

**Error:** `Failed to create database connection pool`

**Solution:**
1. Check PostgreSQL is running
2. Verify credentials in `.env`
3. Check network connectivity
4. Verify database exists

```bash
# Check PostgreSQL status
psql -h localhost -U postgres -d AskMyDocLOG -c "SELECT 1"
```

### Tables Not Created

**Error:** `Table does not exist`

**Solution:**
```python
from database import initialize_database

# Force recreate (WARNING: deletes all data)
result = initialize_database(force_recreate=True)
```

### Connection Pool Exhausted

**Error:** `Connection pool exhausted`

**Solution:**
Increase max connections in `.env`:
```env
POSTGRES_MAX_CONN=20
```

---

## Best Practices

1. **Always initialize database on startup**
   ```python
   from database import initialize_database
   initialize_database()  # Idempotent, safe to call multiple times
   ```

2. **Use singleton instances**
   ```python
   from database import get_query_logger, get_error_logger
   
   query_logger = get_query_logger()  # Reuses same instance
   error_logger = get_error_logger()  # Reuses same instance
   ```

3. **Log errors without breaking pipeline**
   ```python
   try:
       result = operation()
   except Exception as e:
       error_logger.log_exception(e, "operation_stage")
       # Continue or handle gracefully
   ```

4. **Use batch operations for performance**
   ```python
   # Instead of multiple inserts
   eval_logger.log_batch_evaluation(evaluations, run_id)
   ```

5. **Monitor slow queries**
   ```python
   slow_queries = query_logger.get_recent_queries(slow_only=True)
   if len(slow_queries) > 10:
       alert_team("High number of slow queries")
   ```

---

## Integration with RAG Pipeline

See `docs/DATABASE_INTEGRATION.md` for complete integration examples.

---

## License

MIT License - See LICENSE file for details
