"""
API Exception Classes
Exceptions related to REST API operations
"""

from .base import RAGException


class APIError(RAGException):
    """
    Base exception for API-related errors.
    
    Raised during API request processing.
    """
    
    def __init__(self, message: str, status_code: int = 500, **kwargs):
        """
        Initialize API exception.
        
        Args:
            message: Error message
            status_code: HTTP status code
            **kwargs: Additional details
        """
        super().__init__(message, **kwargs)
        self.status_code = status_code


class InvalidRequestError(APIError):
    """
    Raised when API request is invalid.
    
    Examples:
        - Missing required fields
        - Invalid field values
        - Invalid JSON format
        - Invalid content type
    """
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, status_code=400, **kwargs)


class ResourceNotFoundError(APIError):
    """
    Raised when requested resource is not found.
    
    Examples:
        - Document not found
        - Endpoint not found
        - Collection not found
    """
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, status_code=404, **kwargs)


class RateLimitError(APIError):
    """
    Raised when rate limit is exceeded.
    
    Examples:
        - Too many requests
        - Quota exceeded
    """
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, status_code=429, **kwargs)
