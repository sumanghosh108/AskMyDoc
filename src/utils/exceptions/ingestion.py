"""
Ingestion Exception Classes
Exceptions related to document ingestion and indexing
"""

from .base import RAGException


class IngestionError(RAGException):
    """
    Base exception for ingestion-related errors.
    
    Raised during document loading, chunking, embedding, or storage.
    """
    pass


class DocumentLoadError(IngestionError):
    """
    Raised when document loading fails.
    
    Examples:
        - File not found
        - Unsupported file format
        - Corrupted file
        - Permission denied
        - Network error (for URLs)
    """
    pass


class ChunkingError(IngestionError):
    """
    Raised when document chunking fails.
    
    Examples:
        - Invalid chunk size
        - Text splitting error
        - Metadata extraction failure
    """
    pass


class EmbeddingError(IngestionError):
    """
    Raised when embedding generation fails.
    
    Examples:
        - API key invalid
        - API rate limit exceeded
        - Model not available
        - Network timeout
        - Invalid input text
    """
    pass


class VectorStoreError(IngestionError):
    """
    Raised when vector store operations fail.
    
    Examples:
        - Connection error
        - Storage full
        - Index corruption
        - Query timeout
    """
    pass
