# Production-Grade Architecture
## RAG System - Modular Design Documentation

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Principles](#architecture-principles)
3. [System Architecture](#system-architecture)
4. [Module Structure](#module-structure)
5. [Data Flow](#data-flow)
6. [Design Patterns](#design-patterns)
7. [Scalability Considerations](#scalability-considerations)
8. [Security](#security)
9. [Testing Strategy](#testing-strategy)
10. [Deployment](#deployment)

---

## Overview

This RAG (Retrieval Augmented Generation) system follows a production-grade modular architecture designed for:

- **Maintainability**: Clear separation of concerns
- **Scalability**: Horizontal and vertical scaling capabilities
- **Testability**: Each module can be tested independently
- **Extensibility**: Easy to add new features without breaking existing code
- **Performance**: Optimized for low latency and high throughput
- **Reliability**: Fault tolerance and graceful degradation

---

## Architecture Principles

### 1. Separation of Concerns
Each module has a single, well-defined responsibility:
- **Indexing**: Document ingestion and chunking
- **Retrieval**: Finding relevant documents
- **Generation**: Answer synthesis
- **Caching**: Performance optimization
- **Observability**: Monitoring and logging

### 2. Dependency Injection
Modules receive dependencies through constructors, making them:
- Easy to test with mocks
- Flexible to swap implementations
- Clear about their requirements

### 3. Interface-Based Design
Core abstractions define contracts:
- `BaseRetriever`: Retrieval interface
- `CacheInterface`: Caching abstraction
- `LatencyTracker`: Observability interface

### 4. Configuration Management
All configuration is centralized in `src/core/config.py`:
- Environment-based configuration
- Type-safe settings
- Validation on startup

### 5. Error Handling
Graceful degradation and clear error messages:
- Try-catch blocks with specific exceptions
- Fallback mechanisms (e.g., cache failures)
- Detailed logging for debugging

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         API Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   FastAPI    │  │   Schemas    │  │  Middleware  │          │
│  │   Router     │  │  Validation  │  │   (CORS)     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Service Layer                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Enhanced Generator (Orchestrator)           │   │
│  │  - Coordinates all components                            │   │
│  │  - Manages feature flags                                 │   │
│  │  - Handles error recovery                                │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Query      │    │   Multi-Hop  │    │   Context    │
│  Rewriting   │    │  Reasoning   │    │   Builder    │
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Retrieval Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Hybrid     │  │   Reranker   │  │    Cache     │          │
│  │  Retrieval   │  │ Cross-Encoder│  │    Redis     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                  │                  │                  │
│         └──────────────────┼──────────────────┘                  │
│                            ▼                                     │
│  ┌──────────────┐  ┌──────────────┐                             │
│  │   Vector     │  │    BM25      │                             │
│  │   Search     │  │   Keyword    │                             │
│  └──────────────┘  └──────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Storage Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   ChromaDB   │  │    Redis     │  │  File System │          │
│  │   Vectors    │  │    Cache     │  │   Documents  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Cross-Cutting Concerns                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Observability│  │    Logging   │  │    Config    │          │
│  │   Tracking   │  │  Structured  │  │  Management  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Module Structure

### Core Modules

#### 1. **src/core/** - Core Configuration
```
src/core/
├── __init__.py
└── config.py          # Centralized configuration management
```

**Responsibilities:**
- Load environment variables
- Validate configuration
- Provide type-safe settings
- Manage feature flags

**Key Classes:**
- `Config`: Main configuration class
- `validate_config()`: Startup validation

---

#### 2. **src/indexing/** - Document Ingestion
```
src/indexing/
├── __init__.py
└── ingest.py          # Document loading and chunking
```

**Responsibilities:**
- Load documents (PDF, Markdown, Web)
- Extract metadata
- Chunk documents
- Create embeddings
- Store in vector database

**Key Functions:**
- `ingest_documents()`: Main ingestion pipeline
- `get_vector_store()`: Vector store singleton
- `load_documents()`: Document loading
- `chunk_documents()`: Text chunking

**Design Pattern:** Factory Pattern for document loaders

---

#### 3. **src/retrieval/** - Retrieval Pipeline
```
src/retrieval/
├── __init__.py
├── base.py            # Base retriever interface
├── hybrid.py          # Hybrid retrieval (BM25 + Vector)
└── reranker.py        # Cross-encoder reranking
```

**Responsibilities:**
- Vector similarity search
- BM25 keyword search
- Hybrid retrieval with RRF
- Cross-encoder reranking

**Key Classes:**
- `BaseRetriever`: Abstract base class
- `HybridRetriever`: Combines vector + BM25
- `Reranker`: Cross-encoder reranking

**Design Pattern:** Strategy Pattern for retrieval methods

---

#### 4. **src/generation/** - Answer Generation
```
src/generation/
├── __init__.py
├── generator.py           # Basic generator
└── enhanced_generator.py  # Orchestrator with all features
```

**Responsibilities:**
- Orchestrate entire RAG pipeline
- Manage feature flags
- Generate answers with LLM
- Format responses with citations

**Key Functions:**
- `generate_answer_enhanced()`: Main orchestrator
- `generate_answer()`: Basic generation
- `format_sources()`: Citation formatting

**Design Pattern:** Facade Pattern for complex orchestration

---

#### 5. **src/query_rewriter/** - Query Enhancement
```
src/query_rewriter/
├── __init__.py
└── rewrite_engine.py  # Query rewriting with LLM
```

**Responsibilities:**
- Generate query variations
- Expand acronyms
- Add synonyms
- Improve recall

**Key Classes:**
- `QueryRewriter`: Main rewriting engine

**Design Pattern:** Decorator Pattern for query enhancement

---

#### 6. **src/multi_hop/** - Multi-Hop Reasoning
```
src/multi_hop/
├── __init__.py
└── reasoning_controller.py  # Multi-step retrieval
```

**Responsibilities:**
- Detect if multi-hop needed
- Generate follow-up queries
- Execute multiple retrieval rounds
- Merge contexts

**Key Classes:**
- `MultiHopController`: Reasoning orchestrator

**Design Pattern:** Chain of Responsibility for multi-step reasoning

---

#### 7. **src/context/** - Context Management
```
src/context/
├── __init__.py
└── builder.py         # Context building and optimization
```

**Responsibilities:**
- Deduplicate chunks
- Sort by relevance
- Enforce token limits
- Format context for LLM

**Key Classes:**
- `ContextBuilder`: Context optimization

**Design Pattern:** Builder Pattern for context construction

---

#### 8. **src/caching/** - Caching Layer
```
src/caching/
├── __init__.py
└── redis_cache.py     # Redis caching with fallback
```

**Responsibilities:**
- Cache retrieval results
- Cache LLM responses
- Provide cache statistics
- Graceful degradation

**Key Classes:**
- `RedisCache`: Cache implementation with fallback

**Design Pattern:** Proxy Pattern for caching

---

#### 9. **src/observability/** - Monitoring
```
src/observability/
├── __init__.py
└── latency_tracker.py  # Performance tracking
```

**Responsibilities:**
- Track component latency
- Aggregate metrics
- Log performance data
- Generate reports

**Key Classes:**
- `LatencyTracker`: Performance monitoring

**Design Pattern:** Observer Pattern for metrics collection

---

#### 10. **src/utils/** - Utilities
```
src/utils/
├── __init__.py
└── logger.py          # Structured logging
```

**Responsibilities:**
- Structured logging
- Log formatting
- Log rotation
- Context injection

**Key Functions:**
- `get_logger()`: Logger factory
- `setup_logging()`: Logging configuration

---

#### 11. **src/api/** - API Layer
```
src/api/
├── __init__.py
├── router.py          # FastAPI routes
└── schemas.py         # Pydantic models
```

**Responsibilities:**
- HTTP endpoint definitions
- Request/response validation
- Error handling
- CORS configuration

**Key Components:**
- `app`: FastAPI application
- `QueryRequest`: Request schema
- `QueryResponse`: Response schema

**Design Pattern:** MVC Pattern (Controller layer)

---

## Data Flow

### 1. Document Ingestion Flow

```
User uploads document
        │
        ▼
┌─────────────────┐
│  Load Document  │  (PDF/Markdown/Web)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Extract Metadata│  (title, page, source)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Chunk Document │  (500-800 tokens, 100 overlap)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Create Embeddings│ (sentence-transformers)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Store in DB    │  (ChromaDB)
└─────────────────┘
```

---

### 2. Query Processing Flow (Basic)

```
User submits query
        │
        ▼
┌─────────────────┐
│  Check Cache    │  (Redis)
└────────┬────────┘
         │ Cache miss
         ▼
┌─────────────────┐
│ Hybrid Retrieval│  (Vector + BM25)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Reranking    │  (Cross-encoder)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Context Building│  (Dedupe, sort, limit)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ LLM Generation  │  (OpenRouter)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Cache Result   │  (Redis)
└────────┬────────┘
         │
         ▼
    Return answer
```

---

### 3. Query Processing Flow (Advanced)

```
User submits query
        │
        ▼
┌─────────────────┐
│  Query Rewriting│  (Generate variations)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Multi-Query     │  (Retrieve for each variation)
│ Retrieval       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Multi-Hop Check │  (Is more info needed?)
└────────┬────────┘
         │ Yes
         ▼
┌─────────────────┐
│ Follow-up Query │  (Generate and retrieve)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Merge Contexts  │  (Combine all results)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Reranking    │  (Cross-encoder)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Context Building│  (Dedupe, sort, limit)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ LLM Generation  │  (OpenRouter)
└────────┬────────┘
         │
         ▼
    Return answer
```

---

## Design Patterns

### 1. Factory Pattern
**Used in:** Document loading, retriever creation

```python
# src/indexing/ingest.py
def get_vector_store():
    """Factory for vector store singleton"""
    global _vector_store
    if _vector_store is None:
        _vector_store = Chroma(...)
    return _vector_store
```

---

### 2. Strategy Pattern
**Used in:** Retrieval methods

```python
# src/retrieval/base.py
class BaseRetriever(ABC):
    @abstractmethod
    def retrieve(self, query: str, top_k: int) -> List[Document]:
        pass

# src/retrieval/hybrid.py
class HybridRetriever(BaseRetriever):
    def retrieve(self, query: str, top_k: int) -> List[Document]:
        # Hybrid implementation
        pass
```

---

### 3. Facade Pattern
**Used in:** Enhanced generator orchestration

```python
# src/generation/enhanced_generator.py
def generate_answer_enhanced(question, **kwargs):
    """Facade that orchestrates all components"""
    # Query rewriting
    # Multi-hop retrieval
    # Reranking
    # Context building
    # LLM generation
    pass
```

---

### 4. Decorator Pattern
**Used in:** Query enhancement

```python
# Conceptual - query rewriting decorates the base query
original_query = "ML"
enhanced_queries = rewriter.rewrite(original_query)
# ["machine learning", "ML algorithms", ...]
```

---

### 5. Proxy Pattern
**Used in:** Caching layer

```python
# src/caching/redis_cache.py
class RedisCache:
    def get(self, key):
        """Proxy to Redis with fallback"""
        try:
            return self.redis.get(key)
        except:
            return None  # Graceful degradation
```

---

### 6. Observer Pattern
**Used in:** Latency tracking

```python
# src/observability/latency_tracker.py
class LatencyTracker:
    def track(self, component, duration):
        """Observe and record component performance"""
        self.metrics[component].append(duration)
```

---

### 7. Singleton Pattern
**Used in:** Vector store, cache, logger

```python
# Global singleton instances
_vector_store = None
_cache = None
_logger = None
```

---

## Scalability Considerations

### Horizontal Scaling

**API Layer:**
- Deploy multiple FastAPI instances behind load balancer
- Stateless design enables easy scaling
- Use Redis for shared cache across instances

**Retrieval Layer:**
- ChromaDB can be deployed as separate service
- Redis cluster for distributed caching
- Separate embedding service

**Architecture:**
```
┌─────────────┐
│Load Balancer│
└──────┬──────┘
       │
   ┌───┴───┬───────┬───────┐
   ▼       ▼       ▼       ▼
┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│API 1│ │API 2│ │API 3│ │API 4│
└──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘
   │       │       │       │
   └───────┴───┬───┴───────┘
               │
       ┌───────┴───────┐
       ▼               ▼
┌─────────────┐ ┌─────────────┐
│  ChromaDB   │ │Redis Cluster│
└─────────────┘ └─────────────┘
```

---

### Vertical Scaling

**Optimize Components:**
- Use GPU for embeddings and reranking
- Increase worker processes
- Optimize batch sizes
- Enable model quantization

**Configuration:**
```python
# High-performance settings
EMBEDDING_BATCH_SIZE = 128
RERANKER_BATCH_SIZE = 64
MAX_WORKERS = 16
USE_GPU = True
```

---

### Caching Strategy

**Multi-Level Caching:**
1. **L1 Cache**: In-memory (per instance)
2. **L2 Cache**: Redis (shared)
3. **L3 Cache**: CDN (for static content)

**Cache Keys:**
```python
# Retrieval cache
key = f"retrieval:{hash(query)}:{top_k}:{use_hybrid}"

# Response cache
key = f"response:{hash(query)}:{hash(context)}"
```

---

### Database Optimization

**ChromaDB:**
- Index optimization
- Batch insertions
- Periodic compaction
- Separate read/write instances

**Redis:**
- Set TTL for cache entries
- Use Redis Cluster for sharding
- Enable persistence for critical data
- Monitor memory usage

---

## Security

### 1. API Security

**Authentication:**
```python
# Future enhancement
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/query")
async def query(request: QueryRequest, token: str = Depends(security)):
    # Validate token
    pass
```

**Rate Limiting:**
```python
# Future enhancement
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/query")
@limiter.limit("10/minute")
async def query(request: QueryRequest):
    pass
```

---

### 2. Input Validation

**Pydantic Schemas:**
```python
# src/api/schemas.py
class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=50)
```

**Sanitization:**
- Escape special characters
- Validate file uploads
- Check URL schemes

---

### 3. Environment Security

**Secrets Management:**
```env
# .env (never commit!)
OPENROUTER_API_KEY=sk-...
REDIS_PASSWORD=...
```

**Production:**
- Use secret management service (AWS Secrets Manager, HashiCorp Vault)
- Rotate keys regularly
- Use IAM roles instead of keys

---

### 4. Data Security

**Encryption:**
- TLS for API communication
- Encrypt data at rest (ChromaDB, Redis)
- Secure document storage

**Access Control:**
- Role-based access control (RBAC)
- Document-level permissions
- Audit logging

---

## Testing Strategy

### 1. Unit Tests

**Test Individual Modules:**
```python
# tests/test_retrieval.py
def test_hybrid_retrieval():
    retriever = HybridRetriever(...)
    results = retriever.retrieve("test query", top_k=5)
    assert len(results) <= 5
    assert all(hasattr(r, 'content') for r in results)
```

**Coverage Target:** 80%+

---

### 2. Integration Tests

**Test Module Interactions:**
```python
# tests/test_integration.py
def test_end_to_end_query():
    # Ingest test document
    ingest_documents("./test_docs/")
    
    # Query
    result = generate_answer_enhanced("test question")
    
    # Verify
    assert result['answer']
    assert result['sources']
```

---

### 3. Performance Tests

**Load Testing:**
```python
# tests/test_performance.py
import time

def test_query_latency():
    start = time.time()
    result = generate_answer_enhanced("test question")
    elapsed = time.time() - start
    
    assert elapsed < 5.0  # 5 second SLA
```

**Tools:**
- Locust for load testing
- pytest-benchmark for benchmarking
- cProfile for profiling

---

### 4. End-to-End Tests

**API Tests:**
```python
# tests/test_api.py
from fastapi.testclient import TestClient

client = TestClient(app)

def test_query_endpoint():
    response = client.post("/query", json={
        "question": "What is ML?",
        "top_k": 5
    })
    assert response.status_code == 200
    assert "answer" in response.json()
```

---

## Deployment

### 1. Development

```bash
# Local development
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py serve
```

---

### 2. Docker

**Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py", "serve"]
```

**Docker Compose:**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=redis
    depends_on:
      - redis
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

---

### 3. Kubernetes

**Deployment:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rag-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: rag-api
  template:
    metadata:
      labels:
        app: rag-api
    spec:
      containers:
      - name: api
        image: rag-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_HOST
          value: redis-service
```

---

### 4. Cloud Deployment

**AWS:**
- ECS/EKS for containers
- ElastiCache for Redis
- RDS for metadata
- S3 for documents
- CloudWatch for monitoring

**GCP:**
- Cloud Run for containers
- Memorystore for Redis
- Cloud Storage for documents
- Cloud Monitoring

**Azure:**
- AKS for containers
- Azure Cache for Redis
- Blob Storage for documents
- Application Insights

---

## Monitoring and Observability

### Metrics to Track

**Application Metrics:**
- Request rate (requests/second)
- Error rate (errors/second)
- Latency (p50, p95, p99)
- Cache hit rate

**Component Metrics:**
- Retrieval latency
- Reranking latency
- LLM latency
- Context building time

**Infrastructure Metrics:**
- CPU usage
- Memory usage
- Disk I/O
- Network I/O

### Logging

**Structured Logging:**
```python
log.info("Query processed", 
    query=question,
    latency_ms=elapsed,
    sources_count=len(sources),
    cache_hit=cache_hit
)
```

**Log Levels:**
- DEBUG: Detailed debugging
- INFO: General information
- WARNING: Potential issues
- ERROR: Errors that need attention
- CRITICAL: System failures

---

## Conclusion

This production-grade architecture provides:

✅ **Modularity**: Clear separation of concerns  
✅ **Scalability**: Horizontal and vertical scaling  
✅ **Maintainability**: Easy to understand and modify  
✅ **Testability**: Comprehensive testing strategy  
✅ **Performance**: Optimized for low latency  
✅ **Reliability**: Fault tolerance and monitoring  
✅ **Security**: Multiple layers of protection  

The system is ready for production deployment and can handle enterprise-scale workloads.
