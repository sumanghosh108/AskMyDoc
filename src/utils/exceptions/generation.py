"""
Generation Exception Classes
Exceptions related to answer generation and LLM operations
"""

from .base import RAGException


class GenerationError(RAGException):
    """
    Base exception for generation-related errors.
    
    Raised during answer generation, prompt formatting, or context building.
    """
    pass


class LLMError(GenerationError):
    """
    Raised when LLM API calls fail.
    
    Examples:
        - API key invalid
        - Rate limit exceeded
        - Model not available
        - Network timeout
        - Invalid response format
        - Content filtering triggered
    """
    pass


class PromptError(GenerationError):
    """
    Raised when prompt formatting or loading fails.
    
    Examples:
        - Prompt template not found
        - Invalid template format
        - Missing template variables
        - Prompt too long
    """
    pass


class ContextBuildError(GenerationError):
    """
    Raised when context building fails.
    
    Examples:
        - Token limit exceeded
        - Invalid document format
        - Deduplication error
        - Sorting error
    """
    pass
