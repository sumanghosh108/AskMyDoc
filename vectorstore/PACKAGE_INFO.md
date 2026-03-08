# Vectorstore Package

**Version**: 1.0.0  
**Type**: Standalone Python Package  
**Location**: Root level (`/vectorstore`)

## Overview

The `vectorstore` package is a standalone, reusable ChromaDB-based vector storage system designed for RAG (Retrieval-Augmented Generation) applications. It provides persistent storage, automatic embedding, and efficient similarity search.

## Why Root Level?

The vectorstore package is placed at the root level (not in `src/`) because:

1. **Standalone Package**: Can be used independently by any part of the application
2. **Clear Separation**: Separates infrastructure (vectorstore) from application logic (src/)
3. **Reusability**: Can be easily extracted and used in other projects
4. **Import Simplicity**: Clean imports: `from vectorstore import get_chroma_client`
5. **Package Management**: Can be installed as a separate package if needed

## Package Structure

```
vectorstore/
├── __init__.py              # Public API exports
├── chroma_client.py         # ChromaDB client implementation
├── index_manager.py         # Document indexing and chunking
├── setup.py                 # Package installation config
├── README.md                # User documentation
└── PACKAGE_INFO.md          # This file
```

## Public API

The package exports two main functions:

```python
from vectorstore import get_chroma_client, get_index_manager

# Get ChromaDB client (singleton)
client = get_chroma_client()

# Get index manager (singleton)
manager = get_index_manager()
```

## Usage by Other Packages

### src/indexing/ingest.py
```python
from vectorstore import get_chroma_client
# Uses for document ingestion
```

### src/retrieval/base.py
```python
from vectorstore import get_chroma_client
# Uses for vector retrieval
```

### src/api/router.py
```python
from vectorstore import get_index_manager
# Uses for file upload and indexing
```

### database/
```python
from vectorstore import get_chroma_client
# Can use for storing embeddings with metadata
```

## Dependencies

Required packages (installed via `requirements.txt`):
- `chromadb>=0.5.0` - Vector database
- `sentence-transformers>=3.0.0` - Text embedding
- `langchain-text-splitters>=0.3.0` - Document chunking

## Configuration

Configuration is loaded from `src/core/config.py`:

```python
CHROMA_PERSIST_DIR = "vector_db"
CHROMA_COLLECTION_NAME = "rag_documents"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
```

## Data Storage

All vector data is stored in the `vector_db/` directory at the project root:

```
vector_db/
├── chroma.sqlite3           # Main database
└── collections/             # Collection data
    └── <collection-uuid>/
        ├── data_level0.bin  # Vectors
        ├── header.bin       # Metadata
        ├── length.bin       # Lengths
        └── link_lists.bin   # Index
```

## Features

- ✅ **Persistent Storage**: Data survives restarts
- ✅ **Automatic Embedding**: Sentence Transformers integration
- ✅ **Document Chunking**: Intelligent text splitting
- ✅ **Metadata Support**: Rich metadata for filtering
- ✅ **Similarity Search**: Fast vector search
- ✅ **Batch Operations**: Efficient bulk indexing
- ✅ **Singleton Pattern**: Single instance per application
- ✅ **Thread-Safe**: Safe for concurrent access

## Testing

Run the test suite:

```bash
python test_vectorstore.py
```

## Installation

The package is automatically available when the project is set up. No separate installation needed.

For standalone use in other projects:

```bash
cd vectorstore
pip install -e .
```

## Migration Notes

**Previous location**: `src/vectorstore/`  
**New location**: `vectorstore/` (root level)

**Import changes**:
```python
# Old (deprecated)
from src.vectorstore import get_chroma_client

# New (current)
from vectorstore import get_chroma_client
```

All imports have been automatically updated throughout the codebase.

## Maintenance

### Adding New Features

1. Add implementation to `chroma_client.py` or `index_manager.py`
2. Export in `__init__.py` if public API
3. Update `README.md` with usage examples
4. Add tests to `test_vectorstore.py`

### Version Updates

Update version in:
- `setup.py`
- This file (`PACKAGE_INFO.md`)

### Breaking Changes

If making breaking changes:
1. Update major version in `setup.py`
2. Document migration path in `README.md`
3. Update all usage examples
4. Search codebase for imports: `from vectorstore import`

## Support

For issues or questions:
- Check `README.md` for usage examples
- Run `python test_vectorstore.py` to verify setup
- Check `vector_db/` directory for data
- Review logs in `logs/` directory

## License

Same as parent project.
