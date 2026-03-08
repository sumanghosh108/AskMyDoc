# Exception Handling Guide
## Comprehensive Error Management in RAG System

---

## Table of Contents

1. [Overview](#overview)
2. [Exception Hierarchy](#exception-hierarchy)
3. [Exception Classes](#exception-classes)
4. [Usage Examples](#usage-examples)
5. [Best Practices](#best-practices)
6. [Error Handling Patterns](#error-handling-patterns)
7. [API Error Responses](#api-error-responses)
8. [Logging Integration](#logging-integration)

---

## Overview

The RAG system implements a comprehensive exception handling system with:

- **Hierarchical exception classes** for different error types
- **Detailed error context** with metadata
- **Graceful degradation** where possible
- **Consistent error logging** across all modules
- **API-friendly error responses** with proper HTTP status codes

### Benefits

✅ **Clear error messages** - Easy to understand what went wrong  
✅ **Detailed context** - Additional information for debugging  
✅ **Consistent handling** - Same pattern across all modules  
✅ **Graceful degradation** - System continues when possible  
✅ **Production-ready** - Proper logging and monitoring  

---

## Exception Hierarchy

```
Exception (Python built-in)
│
└── RAGException (Base for all RAG exceptions)
    │
    ├── ConfigurationError
    ├── ValidationError
    │
    ├── IngestionError
    │   ├── DocumentLoadError
    │   ├── ChunkingError
    │   ├── EmbeddingError
    │   └── VectorStoreError
    │
    ├── RetrievalError
    │   ├── VectorSearchError
    │   ├── BM25SearchError
    │   ├── HybridRetrievalError
    │   └── RerankingError
    │
    ├── GenerationError
    │   ├── LLMError
    │   ├── PromptError
    │   └── ContextBuildError
    │
    ├── CacheError
    │   ├── CacheConnectionError
    │   └── CacheOperationError
    │
    └── APIError
        ├── InvalidRequestError (400)
        ├── ResourceNotFoundError (404)
        └── RateLimitError (429)
```

---

## Exception Classes

### Base Exceptions

#### `RAGException`
**Purpose:** Base class for all RAG system exceptions

**Attributes:**
- `message`: Human-readable error message
- `details`: Dictionary with additional context
- `original_error`: Original exception if this is a wrapped error

**Methods:**
- `to_dict()`: Convert to dictionary for logging/API responses

**Example:**
```python
from src.utils.exceptions import RAGException

raise RAGException(
    "Operation failed",
    details={"operation": "search", "query": "test"},
    original_error=original_exception
)
```

---

#### `ConfigurationError`
**Purpose:** Configuration-related errors

**When to use:**
- Missing environment variables
- Invalid configuration values
- Conflicting settings

**Example:**
```python
from src.utils.exceptions import ConfigurationError

if not OPENROUTER_API_KEY:
    raise ConfigurationError(
        "OpenRouter API key not configured",
        details={"env_var": "OPENROUTER_API_KEY"}
    )
```

---

#### `ValidationError`
**Purpose:** Input validation errors

**When to use:**
- Invalid query format
- Invalid document format
- Invalid parameter values

**Example:**
```python
from src.utils.exceptions import ValidationError

if top_k <= 0:
    raise ValidationError(
        "top_k must be positive",
        details={"top_k": top_k, "min": 1}
    )
```

---

### Ingestion Exceptions

#### `IngestionError`
**Purpose:** Base for ingestion-related errors

**Child classes:**
- `DocumentLoadError` - Document loading failures
- `ChunkingError` - Text chunking failures
- `EmbeddingError` - Embedding generation failures
- `VectorStoreError` - Vector store operation failures

**Example:**
```python
from src.utils.exceptions import DocumentLoadError

try:
    documents = load_documents(source)
except Exception as e:
    raise DocumentLoadError(
        "Failed to load document",
        details={"source": source, "type": "pdf"},
        original_error=e
    )
```

---

### Retrieval Exceptions

#### `RetrievalError`
**Purpose:** Base for retrieval-related errors

**Child classes:**
- `VectorSearchError` - Vector similarity search failures
- `BM25SearchError` - Keyword search failures
- `HybridRetrievalError` - Hybrid retrieval failures
- `RerankingError` - Reranking failures

**Example:**
```python
from src.utils.exceptions import VectorSearchError

try:
    results = vector_store.similarity_search(query)
except Exception as e:
    raise VectorSearchError(
        "Vector search failed",
        details={"query": query, "top_k": top_k},
        original_error=e
    )
```

---

### Generation Exceptions

#### `GenerationError`
**Purpose:** Base for generation-related errors

**Child classes:**
- `LLMError` - LLM API call failures
- `PromptError` - Prompt formatting failures
- `ContextBuildError` - Context building failures

**Example:**
```python
from src.utils.exceptions import LLMError

try:
    response = llm.invoke(prompt)
except Exception as e:
    raise LLMError(
        "LLM API call failed",
        details={"model": model_name, "prompt_length": len(prompt)},
        original_error=e
    )
```

---

### Caching Exceptions

#### `CacheError`
**Purpose:** Base for caching-related errors

**Child classes:**
- `CacheConnectionError` - Redis connection failures
- `CacheOperationError` - Cache operation failures

**Example:**
```python
from src.utils.exceptions import CacheConnectionError

try:
    redis_client.ping()
except Exception as e:
    raise CacheConnectionError(
        "Failed to connect to Redis",
        details={"host": REDIS_HOST, "port": REDIS_PORT},
        original_error=e
    )
```

---

### API Exceptions

#### `APIError`
**Purpose:** Base for API-related errors

**Attributes:**
- `status_code`: HTTP status code

**Child classes:**
- `InvalidRequestError` (400) - Invalid request
- `ResourceNotFoundError` (404) - Resource not found
- `RateLimitError` (429) - Rate limit exceeded

**Example:**
```python
from src.utils.exceptions import InvalidRequestError

if not request.question:
    raise InvalidRequestError(
        "Question is required",
        details={"field": "question"}
    )
```

---

## Usage Examples

### Basic Exception Handling

```python
from src.utils.exceptions import DocumentLoadError

try:
    documents = load_documents(source)
except DocumentLoadError as e:
    log.error(f"Failed to load documents: {e.message}", details=e.details)
    # Handle error gracefully
    return []
```

---

### Exception with Context

```python
from src.utils.exceptions import ChunkingError

try:
    chunks = chunk_documents(documents, chunk_size=800)
except Exception as e:
    raise ChunkingError(
        "Failed to chunk documents",
        details={
            "doc_count": len(documents),
            "chunk_size": 800,
            "chunk_overlap": 100
        },
        original_error=e
    )
```

---

### Using Exception Handler Decorator

```python
from src.utils.exceptions.handlers import exception_handler

@exception_handler(default_return=[], context="retrieval")
def retrieve_documents(query: str, top_k: int = 5):
    """
    Retrieve documents with automatic exception handling.
    Returns empty list if any error occurs.
    """
    # Implementation
    return results
```

---

### Using Exception Context Manager

```python
from src.utils.exceptions.handlers import ExceptionContext

with ExceptionContext("loading documents", default_return=[]):
    documents = load_documents(source)

# If exception occurred, documents will be []
```

---

### Retry on Exception

```python
from src.utils.exceptions.handlers import retry_on_exception
from src.utils.exceptions import LLMError

@retry_on_exception(
    max_retries=3,
    delay=1.0,
    backoff=2.0,
    exceptions=(LLMError,)
)
def call_llm(prompt: str):
    """
    Call LLM with automatic retry on failure.
    Retries 3 times with exponential backoff.
    """
    return llm.invoke(prompt)
```

---

### Safe Execute

```python
from src.utils.exceptions.handlers import safe_execute

result = safe_execute(
    risky_function,
    arg1, arg2,
    default_return=[],
    error_message="Failed to process data"
)
```

---

## Best Practices

### 1. Always Provide Context

❌ **Bad:**
```python
raise DocumentLoadError("Failed to load document")
```

✅ **Good:**
```python
raise DocumentLoadError(
    "Failed to load document",
    details={"source": source, "type": "pdf", "size_mb": file_size},
    original_error=e
)
```

---

### 2. Wrap External Exceptions

❌ **Bad:**
```python
try:
    result = external_api_call()
except Exception:
    pass  # Silent failure
```

✅ **Good:**
```python
try:
    result = external_api_call()
except Exception as e:
    raise LLMError(
        "External API call failed",
        details={"api": "openrouter", "endpoint": "/chat/completions"},
        original_error=e
    )
```

---

### 3. Use Specific Exceptions

❌ **Bad:**
```python
raise Exception("Something went wrong")
```

✅ **Good:**
```python
raise VectorSearchError(
    "Vector search failed",
    details={"query": query, "top_k": top_k}
)
```

---

### 4. Log Before Re-raising

✅ **Good:**
```python
try:
    result = operation()
except OperationError as e:
    log.error(f"Operation failed: {e.message}", details=e.details)
    raise  # Re-raise for caller to handle
```

---

### 5. Graceful Degradation

✅ **Good:**
```python
try:
    cached_result = cache.get(key)
    if cached_result:
        return cached_result
except CacheError as e:
    log.warning(f"Cache unavailable: {e.message}")
    # Continue without cache
    pass

# Proceed with normal operation
result = expensive_operation()
```

---

## Error Handling Patterns

### Pattern 1: Try-Except-Raise

**Use when:** You need to add context to an exception

```python
try:
    result = operation()
except Exception as e:
    raise CustomError(
        "Operation failed",
        details={"context": "value"},
        original_error=e
    )
```

---

### Pattern 2: Try-Except-Log-Return

**Use when:** You want to handle error gracefully

```python
try:
    result = operation()
except CustomError as e:
    log.error(f"Operation failed: {e.message}", details=e.details)
    return default_value
```

---

### Pattern 3: Try-Except-Retry

**Use when:** Operation might succeed on retry

```python
@retry_on_exception(max_retries=3, delay=1.0)
def operation():
    # Implementation
    pass
```

---

### Pattern 4: Context Manager

**Use when:** You want automatic cleanup

```python
with ExceptionContext("operation", default_return=None):
    result = operation()
```

---

## API Error Responses

### FastAPI Integration

```python
from fastapi import HTTPException
from src.utils.exceptions import APIError, InvalidRequestError

@app.post("/query")
async def query(request: QueryRequest):
    try:
        result = generate_answer(request.question)
        return result
    except InvalidRequestError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.to_dict()
        )
    except APIError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.to_dict()
        )
    except Exception as e:
        log.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error"}
        )
```

---

### Error Response Format

```json
{
  "error_type": "DocumentLoadError",
  "message": "Failed to load document",
  "details": {
    "source": "/path/to/doc.pdf",
    "type": "pdf",
    "size_mb": 5.2
  },
  "original_error": "FileNotFoundError: No such file or directory"
}
```

---

## Logging Integration

### Automatic Logging

All exceptions are automatically logged with structured data:

```python
log.error(
    "RAG Exception: Failed to load document",
    error_type="DocumentLoadError",
    details={"source": "/path/to/doc.pdf", "type": "pdf"},
    context="ingestion",
    original_error="FileNotFoundError: ..."
)
```

---

### Log Levels

- **ERROR**: For exceptions that prevent operation completion
- **WARNING**: For exceptions that are handled gracefully
- **DEBUG**: For detailed traceback information

---

### Example Log Output

```json
{
  "timestamp": "2026-03-08T14:30:00Z",
  "level": "ERROR",
  "message": "RAG Exception: Failed to load document",
  "error_type": "DocumentLoadError",
  "details": {
    "source": "/path/to/doc.pdf",
    "type": "pdf"
  },
  "context": "ingestion",
  "original_error": "FileNotFoundError: No such file or directory",
  "run_id": "2026-03-08_14-30-00"
}
```

---

## Testing Exceptions

### Unit Test Example

```python
import pytest
from src.utils.exceptions import DocumentLoadError

def test_document_load_error():
    with pytest.raises(DocumentLoadError) as exc_info:
        load_documents("/nonexistent/file.pdf")
    
    assert "Failed to load document" in str(exc_info.value)
    assert exc_info.value.details["source"] == "/nonexistent/file.pdf"
```

---

### Integration Test Example

```python
def test_ingestion_with_invalid_file():
    with pytest.raises(IngestionError) as exc_info:
        ingest_documents("/invalid/file.txt")
    
    # Check exception details
    assert exc_info.value.details["step"] == "load"
    assert isinstance(exc_info.value.original_error, DocumentLoadError)
```

---

## Migration Guide

### Updating Existing Code

**Before:**
```python
def load_documents(source):
    try:
        # Load documents
        pass
    except Exception as e:
        log.error(f"Error: {str(e)}")
        raise
```

**After:**
```python
from src.utils.exceptions import DocumentLoadError

def load_documents(source):
    try:
        # Load documents
        pass
    except Exception as e:
        raise DocumentLoadError(
            "Failed to load documents",
            details={"source": source},
            original_error=e
        )
```

---

## Summary

The exception handling system provides:

✅ **Hierarchical exception classes** for different error types  
✅ **Detailed error context** with metadata  
✅ **Consistent error handling** across all modules  
✅ **Graceful degradation** where possible  
✅ **Production-ready logging** and monitoring  
✅ **API-friendly error responses** with proper HTTP status codes  
✅ **Retry mechanisms** for transient failures  
✅ **Context managers** for automatic cleanup  

**Result:** Robust, maintainable, and production-ready error handling throughout the RAG system.
