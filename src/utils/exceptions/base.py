"""
Base Exception Classes
Root exception hierarchy for the RAG system
"""

from typing import Optional, Dict, Any


class RAGException(Exception):
    """
    Base exception for all RAG system errors.
    
    All custom exceptions should inherit from this class.
    """
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        """
        Initialize RAG exception.
        
        Args:
            message: Human-readable error message
            details: Additional context about the error
            original_error: Original exception if this is a wrapped error
        """
        self.message = message
        self.details = details or {}
        self.original_error = original_error
        
        # Build full message
        full_message = message
        if details:
            details_str = ", ".join(f"{k}={v}" for k, v in details.items())
            full_message = f"{message} ({details_str})"
        
        super().__init__(full_message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/API responses."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details,
            "original_error": str(self.original_error) if self.original_error else None
        }


class ConfigurationError(RAGException):
    """
    Raised when there's a configuration error.
    
    Examples:
        - Missing required environment variables
        - Invalid configuration values
        - Conflicting settings
    """
    pass


class ValidationError(RAGException):
    """
    Raised when input validation fails.
    
    Examples:
        - Invalid query format
        - Invalid document format
        - Invalid parameter values
    """
    pass
