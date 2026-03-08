"""
Retrieval Exception Classes
Exceptions related to document retrieval and reranking
"""

from .base import RAGException


class RetrievalError(RAGException):
    """
    Base exception for retrieval-related errors.
    
    Raised during vector search, BM25 search, or reranking.
    """
    pass


class VectorSearchError(RetrievalError):
    """
    Raised when vector similarity search fails.
    
    Examples:
        - Vector store unavailable
        - Invalid query embedding
        - Search timeout
        - Index not found
    """
    pass


class BM25SearchError(RetrievalError):
    """
    Raised when BM25 keyword search fails.
    
    Examples:
        - Index not initialized
        - Invalid query format
        - Search timeout
    """
    pass


class HybridRetrievalError(RetrievalError):
    """
    Raised when hybrid retrieval fails.
    
    Examples:
        - Both vector and BM25 failed
        - RRF fusion error
        - Result merging failure
    """
    pass


class RerankingError(RetrievalError):
    """
    Raised when cross-encoder reranking fails.
    
    Examples:
        - Model loading error
        - API error (for Cohere)
        - Scoring timeout
        - Invalid input format
    """
    pass
