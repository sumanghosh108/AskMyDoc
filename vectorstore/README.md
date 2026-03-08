# Vector Store Package

Standalone ChromaDB-based vector storage and retrieval package for RAG systems.

## Features

- **Persistent Storage**: All embeddings stored on disk in `vector_db/` directory
- **Automatic Embedding**: Uses Sentence Transformers for text embedding
- **Document Chunking**: Intelligent text splitting with overlap
- **Metadata Support**: Rich metadata for filtering and tracking
- **Similarity Search**: Fast vector similarity search with distance metrics
- **Batch Operations**: Efficient batch indexing and querying

## Architecture

```
vectorstore/                 # Standalone package (root level)
├── __init__.py             # Package exports
├── chroma_client.py        # ChromaDB client and operations
├── index_manager.py        # Document indexing and chunking
├── setup.py                # Package setup
└── README.md               # This file

vector_db/                  # Persistent storage (auto-created)
├── chroma.sqlite3          # ChromaDB SQLite database
└── collections/            # Collection data
```

## Installation

The vectorstore package is located at the root level and can be imported directly:

```python
# Import from root-level package
from vectorstore import get_chroma_client, get_index_manager
```

## Usage

### Initialize ChromaDB Client

```python
from vectorstore import get_chroma_client

# Get singleton client instance
client = get_chroma_client()

# Add documents
documents = ["Text 1", "Text 2", "Text 3"]
metadatas = [
    {"source": "doc1.txt", "category": "tech"},
    {"source": "doc2.txt", "category": "science"},
    {"source": "doc3.txt", "category": "tech"}
]

count = client.add_documents(documents, metadatas)
print(f"Added {count} documents")

# Query
results = client.query(
    query_text="What is technology?",
    n_results=5,
    where={"category": "tech"}  # Metadata filter
)

# Get stats
stats = client.get_collection_stats()
print(f"Total documents: {stats['document_count']}")
```

### Use Index Manager

```python
from vectorstore import get_index_manager

# Get singleton manager instance
manager = get_index_manager()

# Index a single document
count = manager.index_document(
    text="Long document text...",
    source="document.pdf",
    metadata={"author": "John Doe", "date": "2024-03-08"}
)

# Index multiple documents
documents = [
    {
        "text": "Document 1 text...",
        "source": "doc1.txt",
        "metadata": {"category": "tech"}
    },
    {
        "text": "Document 2 text...",
        "source": "doc2.txt",
        "metadata": {"category": "science"}
    }
]

total_chunks = manager.index_documents_batch(documents)

# Search with metadata filter
results = manager.search(
    query="machine learning",
    n_results=10,
    filter_metadata={"category": "tech"}
)

for result in results:
    print(f"Text: {result['text']}")
    print(f"Source: {result['metadata']['source']}")
    print(f"Relevance: {result['relevance_score']:.4f}")
```

## Integration with Other Packages

The vectorstore package is designed to be used by other packages in the project:

```python
# In src/indexing/ingest.py
from vectorstore import get_chroma_client, get_index_manager

# In src/retrieval/base.py
from vectorstore import get_chroma_client

# In src/api/router.py
from vectorstore import get_index_manager
```

## Configuration

Configure in `src/core/config.py`:

```python
# ChromaDB settings
CHROMA_PERSIST_DIR = "vector_db"
CHROMA_COLLECTION_NAME = "rag_documents"

# Embedding model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Chunking settings
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
```

## API Endpoints

### Upload and Ingest File

```bash
# Upload a file
curl -X POST "http://localhost:8000/api/v1/ingest/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"

# Response
{
  "status": "success",
  "chunks_ingested": 42,
  "sources": ["document.pdf"]
}
```

### Ingest from Path/URL

```bash
# Ingest from file path or URL
curl -X POST "http://localhost:8000/api/v1/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "sources": ["./docs/guide.md", "https://example.com/article"],
    "chunk_size": 500,
    "chunk_overlap": 50
  }'
```

## Storage Structure

```
vector_db/
├── chroma.sqlite3              # Main database file
└── 77f24081-fcb8-4ce4-a714-... # Collection UUID
    ├── data_level0.bin         # Vector data
    ├── header.bin              # Metadata
    ├── length.bin              # Document lengths
    └── link_lists.bin          # HNSW index
```

## Metadata Schema

Each document chunk includes:

```python
{
    "source": "document.pdf",           # Source file/URL
    "source_type": "pdf",               # File type
    "chunk_index": 0,                   # Chunk number
    "total_chunks": 10,                 # Total chunks from source
    "chunk_size": 450,                  # Actual chunk size
    "document_length": 5000,            # Original document length
    "indexed_at": "2024-03-08T10:30:00" # Indexing timestamp
}
```

## Testing

Run the test suite:

```bash
python test_vectorstore.py
```

Tests include:
- ChromaDB client initialization
- Document embedding and storage
- Similarity search
- Metadata filtering
- Batch indexing
- Statistics retrieval

## Performance

- **Embedding Speed**: ~1000 tokens/second
- **Search Latency**: <50ms for 10k documents
- **Storage**: ~1KB per document chunk
- **Memory**: ~100MB for 10k documents

## Troubleshooting

### Database Locked Error

If you see "database is locked":
```python
# Reset the database
from vectorstore import get_chroma_client
client = get_chroma_client()
client.reset_database()
```

### Slow Embedding

If embedding is slow:
- Use a smaller model: `sentence-transformers/all-MiniLM-L6-v2`
- Reduce chunk size in config
- Enable GPU if available

### Out of Memory

If running out of memory:
- Reduce `CHUNK_SIZE` in config
- Process documents in smaller batches
- Use a smaller embedding model

## Best Practices

1. **Chunking**: Use 400-600 tokens per chunk for best results
2. **Overlap**: 10-20% overlap prevents context loss
3. **Metadata**: Add rich metadata for better filtering
4. **Batch Size**: Index 100-1000 documents per batch
5. **Backup**: Regularly backup `vector_db/` directory

## Advanced Features

### Custom Embedding Model

```python
from vectorstore import get_chroma_client

client = get_chroma_client(
    embedding_model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
```

### Multiple Collections

```python
from vectorstore import get_chroma_client

# Create separate collections
tech_client = get_chroma_client(collection_name="tech_docs")
science_client = get_chroma_client(collection_name="science_docs")
```

### Metadata Filtering

```python
from vectorstore import get_index_manager

manager = get_index_manager()

# Complex metadata queries
results = manager.search(
    query="machine learning",
    filter_metadata={
        "$and": [
            {"category": "tech"},
            {"date": {"$gte": "2024-01-01"}}
        ]
    }
)
```

## Package Structure

```
vectorstore/                    # Root-level package
├── __init__.py                # Exports: get_chroma_client, get_index_manager
├── chroma_client.py           # ChromaClient class
├── index_manager.py           # IndexManager class
├── setup.py                   # Package setup
└── README.md                  # Documentation

Used by:
├── src/indexing/ingest.py     # Document ingestion
├── src/retrieval/base.py      # Vector retrieval
├── src/api/router.py          # API endpoints
└── test_vectorstore.py        # Test suite
```

## References

- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [LangChain Text Splitters](https://python.langchain.com/docs/modules/data_connection/document_transformers/)

## Features

- **Persistent Storage**: All embeddings stored on disk in `vector_db/` directory
- **Automatic Embedding**: Uses Sentence Transformers for text embedding
- **Document Chunking**: Intelligent text splitting with overlap
- **Metadata Support**: Rich metadata for filtering and tracking
- **Similarity Search**: Fast vector similarity search with distance metrics
- **Batch Operations**: Efficient batch indexing and querying

## Architecture

```
src/vectorstore/
├── chroma_client.py      # ChromaDB client and operations
├── index_manager.py      # Document indexing and chunking
└── __init__.py          # Module exports

vector_db/               # Persistent storage (auto-created)
├── chroma.sqlite3       # ChromaDB SQLite database
└── collections/         # Collection data
```

## Usage

### Initialize ChromaDB Client

```python
from src.vectorstore import get_chroma_client

# Get singleton client instance
client = get_chroma_client()

# Add documents
documents = ["Text 1", "Text 2", "Text 3"]
metadatas = [
    {"source": "doc1.txt", "category": "tech"},
    {"source": "doc2.txt", "category": "science"},
    {"source": "doc3.txt", "category": "tech"}
]

count = client.add_documents(documents, metadatas)
print(f"Added {count} documents")

# Query
results = client.query(
    query_text="What is technology?",
    n_results=5,
    where={"category": "tech"}  # Metadata filter
)

# Get stats
stats = client.get_collection_stats()
print(f"Total documents: {stats['document_count']}")
```

### Use Index Manager

```python
from src.vectorstore import get_index_manager

# Get singleton manager instance
manager = get_index_manager()

# Index a single document
count = manager.index_document(
    text="Long document text...",
    source="document.pdf",
    metadata={"author": "John Doe", "date": "2024-03-08"}
)

# Index multiple documents
documents = [
    {
        "text": "Document 1 text...",
        "source": "doc1.txt",
        "metadata": {"category": "tech"}
    },
    {
        "text": "Document 2 text...",
        "source": "doc2.txt",
        "metadata": {"category": "science"}
    }
]

total_chunks = manager.index_documents_batch(documents)

# Search with metadata filter
results = manager.search(
    query="machine learning",
    n_results=10,
    filter_metadata={"category": "tech"}
)

for result in results:
    print(f"Text: {result['text']}")
    print(f"Source: {result['metadata']['source']}")
    print(f"Relevance: {result['relevance_score']:.4f}")
```

## Configuration

Configure in `src/core/config.py`:

```python
# ChromaDB settings
CHROMA_PERSIST_DIR = "vector_db"
CHROMA_COLLECTION_NAME = "rag_documents"

# Embedding model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Chunking settings
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
```

## API Endpoints

### Upload and Ingest File

```bash
# Upload a file
curl -X POST "http://localhost:8000/api/v1/ingest/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"

# Response
{
  "status": "success",
  "chunks_ingested": 42,
  "sources": ["document.pdf"]
}
```

### Ingest from Path/URL

```bash
# Ingest from file path or URL
curl -X POST "http://localhost:8000/api/v1/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "sources": ["./docs/guide.md", "https://example.com/article"],
    "chunk_size": 500,
    "chunk_overlap": 50
  }'
```

## Storage Structure

```
vector_db/
├── chroma.sqlite3              # Main database file
└── 77f24081-fcb8-4ce4-a714-... # Collection UUID
    ├── data_level0.bin         # Vector data
    ├── header.bin              # Metadata
    ├── length.bin              # Document lengths
    └── link_lists.bin          # HNSW index
```

## Metadata Schema

Each document chunk includes:

```python
{
    "source": "document.pdf",           # Source file/URL
    "source_type": "pdf",               # File type
    "chunk_index": 0,                   # Chunk number
    "total_chunks": 10,                 # Total chunks from source
    "chunk_size": 450,                  # Actual chunk size
    "document_length": 5000,            # Original document length
    "indexed_at": "2024-03-08T10:30:00" # Indexing timestamp
}
```

## Testing

Run the test suite:

```bash
python test_vectorstore.py
```

Tests include:
- ChromaDB client initialization
- Document embedding and storage
- Similarity search
- Metadata filtering
- Batch indexing
- Statistics retrieval

## Performance

- **Embedding Speed**: ~1000 tokens/second
- **Search Latency**: <50ms for 10k documents
- **Storage**: ~1KB per document chunk
- **Memory**: ~100MB for 10k documents

## Troubleshooting

### Database Locked Error

If you see "database is locked":
```python
# Reset the database
client = get_chroma_client()
client.reset_database()
```

### Slow Embedding

If embedding is slow:
- Use a smaller model: `sentence-transformers/all-MiniLM-L6-v2`
- Reduce chunk size in config
- Enable GPU if available

### Out of Memory

If running out of memory:
- Reduce `CHUNK_SIZE` in config
- Process documents in smaller batches
- Use a smaller embedding model

## Best Practices

1. **Chunking**: Use 400-600 tokens per chunk for best results
2. **Overlap**: 10-20% overlap prevents context loss
3. **Metadata**: Add rich metadata for better filtering
4. **Batch Size**: Index 100-1000 documents per batch
5. **Backup**: Regularly backup `vector_db/` directory

## Advanced Features

### Custom Embedding Model

```python
client = get_chroma_client(
    embedding_model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
```

### Multiple Collections

```python
# Create separate collections
tech_client = get_chroma_client(collection_name="tech_docs")
science_client = get_chroma_client(collection_name="science_docs")
```

### Metadata Filtering

```python
# Complex metadata queries
results = manager.search(
    query="machine learning",
    filter_metadata={
        "$and": [
            {"category": "tech"},
            {"date": {"$gte": "2024-01-01"}}
        ]
    }
)
```

## References

- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [LangChain Text Splitters](https://python.langchain.com/docs/modules/data_connection/document_transformers/)
