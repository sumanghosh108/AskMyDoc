# Project Structure
## Production-Grade RAG System - Directory Organization

---

## Overview

This document describes the complete directory structure and organization of the RAG system, following production-grade best practices for modularity, maintainability, and scalability.

---

## Directory Tree

```
AskMyDoc/
├── .git/                          # Git version control
├── .venv/                         # Python virtual environment
├── .env                           # Environment variables (not in git)
├── .env.example                   # Example environment file
├── .gitignore                     # Git ignore rules
├── README.md                      # Project overview and quick start
├── requirements.txt               # Python dependencies
├── main.py                        # CLI entry point
├── task.md                        # Original task specification
│
├── chroma_db/                     # ChromaDB vector store data
│   ├── chroma.sqlite3            # SQLite database
│   └── [uuid]/                   # Vector index files
│       ├── data_level0.bin
│       ├── header.bin
│       ├── length.bin
│       └── link_lists.bin
│
├── config/                        # Configuration files
│   └── prompts_v1.yaml           # Prompt templates (versioned)
│
├── docs/                          # Documentation
│   ├── ARCHITECTURE.md           # System architecture and design
│   ├── API_GUIDE.md              # REST API documentation
│   ├── GETTING_STARTED.md        # Step-by-step setup guide
│   ├── IMPLEMENTATION_SUMMARY.md # Feature implementation details
│   ├── PROJECT_STRUCTURE.md      # This file
│   ├── QUICK_REFERENCE.md        # Command cheat sheet
│   ├── README.md                 # Original README (moved)
│   ├── USAGE_GUIDE.md            # Comprehensive usage guide
│   └── VERIFICATION_CHECKLIST.md # Quality assurance checklist
│
├── eval/                          # Evaluation pipeline
│   ├── evaluate.py               # Basic evaluation script
│   ├── golden_dataset.json       # Test dataset
│   └── ragas_evaluate.py         # RAGAS evaluation script
│
├── logs/                          # Application logs
│   ├── app.log                   # Main application log
│   └── run_*.log                 # Run-specific logs
│
├── sample_docs/                   # Sample documents for testing
│   ├── machine_learning_intro.md
│   └── nlp_overview.md
│
├── src/                           # Source code (modular architecture)
│   ├── __init__.py
│   │
│   ├── api/                       # REST API layer
│   │   ├── __init__.py
│   │   ├── router.py             # FastAPI routes and endpoints
│   │   └── schemas.py            # Pydantic request/response models
│   │
│   ├── caching/                   # Caching layer
│   │   ├── __init__.py
│   │   └── redis_cache.py        # Redis cache with fallback
│   │
│   ├── context/                   # Context management
│   │   ├── __init__.py
│   │   └── builder.py            # Context optimization and formatting
│   │
│   ├── core/                      # Core configuration
│   │   ├── __init__.py
│   │   └── config.py             # Centralized configuration management
│   │
│   ├── generation/                # Answer generation
│   │   ├── __init__.py
│   │   ├── generator.py          # Basic generator
│   │   └── enhanced_generator.py # Orchestrator with all features
│   │
│   ├── indexing/                  # Document ingestion
│   │   ├── __init__.py
│   │   └── ingest.py             # Document loading, chunking, embedding
│   │
│   ├── multi_hop/                 # Multi-hop reasoning
│   │   ├── __init__.py
│   │   └── reasoning_controller.py # Multi-step retrieval logic
│   │
│   ├── observability/             # Monitoring and metrics
│   │   ├── __init__.py
│   │   └── latency_tracker.py    # Performance tracking
│   │
│   ├── query_rewriter/            # Query enhancement
│   │   ├── __init__.py
│   │   └── rewrite_engine.py     # Query rewriting with LLM
│   │
│   ├── retrieval/                 # Retrieval pipeline
│   │   ├── __init__.py
│   │   ├── base.py               # Base retriever interface
│   │   ├── hybrid.py             # Hybrid retrieval (BM25 + Vector)
│   │   └── reranker.py           # Cross-encoder reranking
│   │
│   └── utils/                     # Utilities
│       ├── __init__.py
│       └── logger.py             # Structured logging
│
└── tests/                         # Test suite
    ├── __init__.py
    ├── test_api.py               # API endpoint tests
    ├── chat_api.py               # Interactive chat interface
    └── [future test files]
```

---

## Module Descriptions

### Root Level Files

#### `main.py`
**Purpose:** CLI entry point for the application

**Commands:**
- `ingest`: Ingest documents into vector store
- `query`: Ask questions
- `status`: Check vector store status
- `cache`: Manage cache (stats, clear)
- `eval`: Run evaluation pipeline
- `serve`: Start FastAPI server

**Usage:**
```bash
python main.py <command> [options]
```

---

#### `requirements.txt`
**Purpose:** Python package dependencies

**Key Dependencies:**
- `langchain`: Document processing
- `chromadb`: Vector database
- `sentence-transformers`: Embeddings and reranking
- `fastapi`: REST API framework
- `redis`: Caching (optional)
- `ragas`: Evaluation framework

---

#### `.env` / `.env.example`
**Purpose:** Environment configuration

**Required Variables:**
- `OPENROUTER_API_KEY`: LLM API key

**Optional Variables:**
- `OPENAI_API_KEY`: OpenAI embeddings
- `COHERE_API_KEY`: Cohere reranking
- `CACHE_ENABLED`: Enable/disable caching
- `REDIS_HOST`, `REDIS_PORT`: Redis configuration

---

### Source Code (`src/`)

#### `src/api/` - REST API Layer

**Files:**
- `router.py`: FastAPI application and route definitions
- `schemas.py`: Pydantic models for request/response validation

**Endpoints:**
- `GET /health`: Health check
- `POST /query`: Basic query
- `POST /query/advanced`: Advanced query with all features
- `GET /cache/stats`: Cache statistics
- `POST /cache/clear`: Clear cache
- `GET /metrics`: System metrics

**Design Pattern:** MVC (Controller layer)

---

#### `src/caching/` - Caching Layer

**Files:**
- `redis_cache.py`: Redis cache implementation with graceful fallback

**Features:**
- Retrieval result caching
- LLM response caching
- Cache statistics
- Automatic fallback if Redis unavailable

**Design Pattern:** Proxy Pattern

---

#### `src/context/` - Context Management

**Files:**
- `builder.py`: Context optimization and formatting

**Responsibilities:**
- Deduplicate retrieved chunks
- Sort by relevance score
- Enforce token limits
- Format context for LLM

**Design Pattern:** Builder Pattern

---

#### `src/core/` - Core Configuration

**Files:**
- `config.py`: Centralized configuration management

**Features:**
- Environment variable loading
- Configuration validation
- Type-safe settings
- Default values

**Key Classes:**
- `Config`: Main configuration class
- `validate_config()`: Startup validation

---

#### `src/generation/` - Answer Generation

**Files:**
- `generator.py`: Basic answer generation
- `enhanced_generator.py`: Orchestrator with all features

**Responsibilities:**
- Coordinate entire RAG pipeline
- Manage feature flags
- Generate answers with LLM
- Format responses with citations

**Design Pattern:** Facade Pattern

---

#### `src/indexing/` - Document Ingestion

**Files:**
- `ingest.py`: Document loading, chunking, and embedding

**Supported Formats:**
- PDF documents
- Markdown files
- Web pages (URLs)

**Pipeline:**
1. Load documents
2. Extract metadata
3. Chunk text (500-800 tokens, 100 overlap)
4. Create embeddings
5. Store in ChromaDB

**Design Pattern:** Factory Pattern

---

#### `src/multi_hop/` - Multi-Hop Reasoning

**Files:**
- `reasoning_controller.py`: Multi-step retrieval logic

**Features:**
- Detect if additional retrieval needed
- Generate follow-up queries
- Execute multiple retrieval rounds
- Merge contexts from all hops

**Design Pattern:** Chain of Responsibility

---

#### `src/observability/` - Monitoring

**Files:**
- `latency_tracker.py`: Performance tracking

**Metrics:**
- Component-level latency
- Aggregate statistics
- Feature usage tracking
- Context statistics

**Design Pattern:** Observer Pattern

---

#### `src/query_rewriter/` - Query Enhancement

**Files:**
- `rewrite_engine.py`: Query rewriting with LLM

**Features:**
- Generate query variations
- Expand acronyms
- Add synonyms
- Improve recall

**Design Pattern:** Decorator Pattern

---

#### `src/retrieval/` - Retrieval Pipeline

**Files:**
- `base.py`: Base retriever interface
- `hybrid.py`: Hybrid retrieval (BM25 + Vector)
- `reranker.py`: Cross-encoder reranking

**Retrieval Methods:**
- Vector similarity search (semantic)
- BM25 keyword search (lexical)
- Hybrid with Reciprocal Rank Fusion (RRF)
- Cross-encoder reranking

**Design Pattern:** Strategy Pattern

---

#### `src/utils/` - Utilities

**Files:**
- `logger.py`: Structured logging

**Features:**
- JSON-formatted logs
- Context injection
- Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- File and console output

---

### Configuration (`config/`)

#### `prompts_v1.yaml`
**Purpose:** Externalized prompt templates

**Structure:**
```yaml
version: "1.0"

prompts:
  answer_generation:
    system: "System prompt..."
    user_template: "User prompt template with {placeholders}"
  
  query_rewriting:
    system: "System prompt..."
    user_template: "Template..."
  
  multi_hop_analysis:
    system: "System prompt..."
    user_template: "Template..."
```

**Benefits:**
- Edit prompts without code changes
- Version control for prompts
- A/B testing different prompts
- Easy rollback

---

### Documentation (`docs/`)

#### User Guides
- **GETTING_STARTED.md**: Step-by-step setup for new users
- **USAGE_GUIDE.md**: Comprehensive usage examples
- **API_GUIDE.md**: REST API documentation with examples
- **QUICK_REFERENCE.md**: Command cheat sheet

#### Technical Documentation
- **ARCHITECTURE.md**: System architecture and design patterns
- **PROJECT_STRUCTURE.md**: This file - directory organization
- **IMPLEMENTATION_SUMMARY.md**: Feature implementation details
- **VERIFICATION_CHECKLIST.md**: Quality assurance checklist

---

### Evaluation (`eval/`)

#### `evaluate.py`
**Purpose:** Basic evaluation script

**Features:**
- Load golden dataset
- Run queries through system
- Compare with expected answers
- Calculate accuracy metrics

---

#### `ragas_evaluate.py`
**Purpose:** RAGAS-based evaluation

**Metrics:**
- Faithfulness: Answer grounded in context
- Answer Correctness: Semantic similarity to ground truth
- Context Recall: Relevant context retrieved
- Context Precision: Irrelevant context filtered

---

#### `golden_dataset.json`
**Purpose:** Test dataset for evaluation

**Format:**
```json
{
  "questions": [
    {
      "question": "What is machine learning?",
      "expected_answer": "Machine learning is...",
      "ground_truth_context": ["Context chunk 1", "Context chunk 2"]
    }
  ]
}
```

---

### Tests (`tests/`)

#### `test_api.py`
**Purpose:** Automated API test suite

**Tests:**
1. Health check
2. Basic query
3. Advanced query with all features
4. Cache statistics
5. System metrics

**Usage:**
```bash
python tests/test_api.py
```

---

#### `chat_api.py`
**Purpose:** Interactive chat interface

**Features:**
- Toggle basic/advanced modes
- View cache statistics
- Clear screen
- Built-in help

**Usage:**
```bash
python tests/chat_api.py
```

---

### Storage (`chroma_db/`)

#### ChromaDB Files
**Purpose:** Vector database storage

**Files:**
- `chroma.sqlite3`: Metadata database
- `[uuid]/`: Vector index files
  - `data_level0.bin`: Vector data
  - `header.bin`: Index header
  - `length.bin`: Vector lengths
  - `link_lists.bin`: HNSW graph

**Note:** This directory is auto-generated and should not be manually edited.

---

### Logs (`logs/`)

#### Log Files
**Purpose:** Application logging

**Files:**
- `app.log`: Main application log (rotated)
- `run_YYYY-MM-DD_HH-MM-SS.log`: Run-specific logs

**Format:** JSON-structured logs
```json
{
  "timestamp": "2026-03-08T12:00:00Z",
  "level": "INFO",
  "message": "Query processed",
  "query": "What is ML?",
  "latency_ms": 3450,
  "run_id": "2026-03-08_12-00-00"
}
```

---

## File Naming Conventions

### Python Files
- **Modules**: `lowercase_with_underscores.py`
- **Classes**: `PascalCase`
- **Functions**: `lowercase_with_underscores()`
- **Constants**: `UPPERCASE_WITH_UNDERSCORES`

### Documentation
- **User guides**: `UPPERCASE_TITLE.md`
- **Technical docs**: `UPPERCASE_TITLE.md`
- **Code comments**: Inline with `#` or docstrings with `"""`

### Configuration
- **YAML files**: `lowercase_with_version.yaml`
- **Environment**: `.env` (hidden file)

---

## Import Conventions

### Absolute Imports (Preferred)
```python
from src.retrieval.hybrid import HybridRetriever
from src.generation.enhanced_generator import generate_answer_enhanced
from src.core.config import Config
```

### Relative Imports (Within Package)
```python
# In src/retrieval/hybrid.py
from .base import BaseRetriever
from .reranker import Reranker
```

---

## Adding New Modules

### Step 1: Create Module Directory
```bash
mkdir src/new_module
touch src/new_module/__init__.py
touch src/new_module/implementation.py
```

### Step 2: Implement Module
```python
# src/new_module/implementation.py
from src.utils.logger import get_logger

log = get_logger(__name__)

class NewFeature:
    def __init__(self):
        log.info("NewFeature initialized")
    
    def process(self, data):
        log.info("Processing data", data_size=len(data))
        # Implementation
        return result
```

### Step 3: Export in `__init__.py`
```python
# src/new_module/__init__.py
from .implementation import NewFeature

__all__ = ['NewFeature']
```

### Step 4: Integrate with Orchestrator
```python
# src/generation/enhanced_generator.py
from src.new_module import NewFeature

def generate_answer_enhanced(..., use_new_feature=False):
    if use_new_feature:
        feature = NewFeature()
        result = feature.process(data)
```

### Step 5: Add CLI Support
```python
# main.py
query_parser.add_argument(
    "--new-feature",
    action="store_true",
    help="Enable new feature"
)
```

### Step 6: Add API Support
```python
# src/api/schemas.py
class QueryRequest(BaseModel):
    use_new_feature: bool = False

# src/api/router.py
@app.post("/query/advanced")
async def query_advanced(request: QueryRequest):
    result = generate_answer_enhanced(
        ...,
        use_new_feature=request.use_new_feature
    )
```

### Step 7: Document
- Add to `docs/ARCHITECTURE.md`
- Update `docs/USAGE_GUIDE.md`
- Update `docs/API_GUIDE.md`
- Update `README.md`

---

## Best Practices

### Code Organization
✅ **DO:**
- Keep modules focused on single responsibility
- Use clear, descriptive names
- Follow PEP 8 style guide
- Add docstrings to all public functions/classes
- Use type hints

❌ **DON'T:**
- Create circular dependencies
- Mix concerns in single module
- Use global state (except singletons)
- Hardcode configuration values

### Documentation
✅ **DO:**
- Document all public APIs
- Include usage examples
- Keep docs up-to-date with code
- Use clear, concise language

❌ **DON'T:**
- Document implementation details in user guides
- Duplicate information across files
- Use jargon without explanation

### Testing
✅ **DO:**
- Write tests for new features
- Test error cases
- Use meaningful test names
- Mock external dependencies

❌ **DON'T:**
- Test implementation details
- Write flaky tests
- Skip edge cases

---

## Maintenance

### Regular Tasks

**Daily:**
- Monitor logs for errors
- Check system metrics
- Review cache hit rates

**Weekly:**
- Update dependencies
- Review and rotate logs
- Backup vector database

**Monthly:**
- Evaluate system performance
- Update documentation
- Review and optimize prompts

---

## Conclusion

This modular, production-grade structure provides:

✅ Clear separation of concerns  
✅ Easy to navigate and understand  
✅ Scalable and maintainable  
✅ Well-documented  
✅ Test-friendly  
✅ Production-ready  

Follow these conventions when extending the system to maintain consistency and quality.
