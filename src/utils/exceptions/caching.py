"""
Caching Exception Classes
Exceptions related to caching operations
"""

from .base import RAGException


class CacheError(RAGException):
    """
    Base exception for caching-related errors.
    
    Raised during cache operations (get, set, delete).
    """
    pass


class CacheConnectionError(CacheError):
    """
    Raised when cache connection fails.
    
    Examples:
        - Redis server not running
        - Connection timeout
        - Authentication failed
        - Network error
    """
    pass


class CacheOperationError(CacheError):
    """
    Raised when cache operations fail.
    
    Examples:
        - Set operation failed
        - Get operation failed
        - Delete operation failed
        - Serialization error
        - Memory full
    """
    pass
