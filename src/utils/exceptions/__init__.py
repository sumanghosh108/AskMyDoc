"""
Exception Handling Module
Centralized exception definitions for the RAG system
"""

from .base import (
    RAGException,
    ConfigurationError,
    ValidationError,
)

from .ingestion import (
    IngestionError,
    DocumentLoadError,
    ChunkingError,
    EmbeddingError,
    VectorStoreError,
)

from .retrieval import (
    RetrievalError,
    VectorSearchError,
    BM25SearchError,
    HybridRetrievalError,
    RerankingError,
)

from .generation import (
    GenerationError,
    LLMError,
    PromptError,
    ContextBuildError,
)

from .caching import (
    CacheError,
    CacheConnectionError,
    CacheOperationError,
)

from .api import (
    APIError,
    InvalidRequestError,
    ResourceNotFoundError,
    RateLimitError,
)

__all__ = [
    # Base exceptions
    'RAGException',
    'ConfigurationError',
    'ValidationError',
    
    # Ingestion exceptions
    'IngestionError',
    'DocumentLoadError',
    'ChunkingError',
    'EmbeddingError',
    'VectorStoreError',
    
    # Retrieval exceptions
    'RetrievalError',
    'VectorSearchError',
    'BM25SearchError',
    'HybridRetrievalError',
    'RerankingError',
    
    # Generation exceptions
    'GenerationError',
    'LLMError',
    'PromptError',
    'ContextBuildError',
    
    # Caching exceptions
    'CacheError',
    'CacheConnectionError',
    'CacheOperationError',
    
    # API exceptions
    'APIError',
    'InvalidRequestError',
    'ResourceNotFoundError',
    'RateLimitError',
]
