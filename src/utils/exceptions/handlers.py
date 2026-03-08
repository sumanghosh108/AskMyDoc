"""
Exception Handlers
Utilities for handling and logging exceptions
"""

import traceback
from typing import Optional, Callable, Any
from functools import wraps

from src.utils.logger import get_logger
from .base import RAGException

log = get_logger(__name__)


def handle_exception(
    exception: Exception,
    context: Optional[str] = None,
    reraise: bool = True,
    default_return: Any = None
) -> Any:
    """
    Handle an exception with logging and optional re-raising.
    
    Args:
        exception: The exception to handle
        context: Additional context about where the error occurred
        reraise: Whether to re-raise the exception after logging
        default_return: Value to return if not re-raising
    
    Returns:
        default_return if reraise=False, otherwise raises exception
    
    Raises:
        Exception: The original exception if reraise=True
    """
    # Log the exception
    if isinstance(exception, RAGException):
        log.error(
            f"RAG Exception: {exception.message}",
            error_type=exception.__class__.__name__,
            details=exception.details,
            context=context,
            original_error=str(exception.original_error) if exception.original_error else None
        )
    else:
        log.error(
            f"Unexpected exception: {str(exception)}",
            error_type=exception.__class__.__name__,
            context=context,
            traceback=traceback.format_exc()
        )
    
    if reraise:
        raise exception
    
    return default_return


def exception_handler(
    default_return: Any = None,
    log_traceback: bool = True,
    context: Optional[str] = None
):
    """
    Decorator for handling exceptions in functions.
    
    Args:
        default_return: Value to return if exception occurs
        log_traceback: Whether to log full traceback
        context: Additional context for logging
    
    Example:
        @exception_handler(default_return=[], context="retrieval")
        def retrieve_documents(query):
            # Function implementation
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except RAGException as e:
                log.error(
                    f"RAG Exception in {func.__name__}: {e.message}",
                    function=func.__name__,
                    error_type=e.__class__.__name__,
                    details=e.details,
                    context=context or func.__name__
                )
                if log_traceback:
                    log.debug("Traceback", traceback=traceback.format_exc())
                return default_return
            except Exception as e:
                log.error(
                    f"Unexpected exception in {func.__name__}: {str(e)}",
                    function=func.__name__,
                    error_type=e.__class__.__name__,
                    context=context or func.__name__
                )
                if log_traceback:
                    log.error("Traceback", traceback=traceback.format_exc())
                return default_return
        
        return wrapper
    return decorator


def safe_execute(
    func: Callable,
    *args,
    default_return: Any = None,
    error_message: str = "Operation failed",
    **kwargs
) -> Any:
    """
    Safely execute a function with exception handling.
    
    Args:
        func: Function to execute
        *args: Positional arguments for the function
        default_return: Value to return if exception occurs
        error_message: Custom error message for logging
        **kwargs: Keyword arguments for the function
    
    Returns:
        Function result or default_return if exception occurs
    
    Example:
        result = safe_execute(
            risky_function,
            arg1, arg2,
            default_return=[],
            error_message="Failed to process data"
        )
    """
    try:
        return func(*args, **kwargs)
    except RAGException as e:
        log.error(
            f"{error_message}: {e.message}",
            function=func.__name__,
            error_type=e.__class__.__name__,
            details=e.details
        )
        return default_return
    except Exception as e:
        log.error(
            f"{error_message}: {str(e)}",
            function=func.__name__,
            error_type=e.__class__.__name__
        )
        return default_return


def retry_on_exception(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for retrying functions on exception.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry
    
    Example:
        @retry_on_exception(max_retries=3, delay=1.0, backoff=2.0)
        def fetch_data():
            # Function that might fail temporarily
            pass
    """
    import time
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        log.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}, retrying in {current_delay}s",
                            function=func.__name__,
                            error=str(e),
                            attempt=attempt + 1,
                            max_retries=max_retries
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        log.error(
                            f"All {max_retries} retry attempts failed for {func.__name__}",
                            function=func.__name__,
                            error=str(e)
                        )
            
            # All retries exhausted, raise the last exception
            raise last_exception
        
        return wrapper
    return decorator


class ExceptionContext:
    """
    Context manager for handling exceptions with custom behavior.
    
    Example:
        with ExceptionContext("loading documents", default_return=[]):
            documents = load_documents(path)
    """
    
    def __init__(
        self,
        context: str,
        default_return: Any = None,
        reraise: bool = False,
        log_level: str = "error"
    ):
        """
        Initialize exception context.
        
        Args:
            context: Description of the operation
            default_return: Value to return if exception occurs
            reraise: Whether to re-raise the exception
            log_level: Logging level (error, warning, info)
        """
        self.context = context
        self.default_return = default_return
        self.reraise = reraise
        self.log_level = log_level
        self.exception = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.exception = exc_val
            
            # Log the exception
            log_func = getattr(log, self.log_level)
            if isinstance(exc_val, RAGException):
                log_func(
                    f"Exception in {self.context}: {exc_val.message}",
                    error_type=exc_type.__name__,
                    details=exc_val.details,
                    context=self.context
                )
            else:
                log_func(
                    f"Exception in {self.context}: {str(exc_val)}",
                    error_type=exc_type.__name__,
                    context=self.context
                )
            
            # Return True to suppress exception, False to propagate
            return not self.reraise
        
        return False
    
    def get_result(self):
        """Get the default return value if exception occurred."""
        return self.default_return if self.exception else None
