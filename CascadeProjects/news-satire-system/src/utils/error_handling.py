import logging
import time
import functools
from typing import Callable, Any, Optional
from ..utils.config import Config

logger = logging.getLogger(__name__)

def retry_with_backoff(max_retries: int = 3, delay: int = 60, backoff_factor: float = 2.0):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff_factor: Multiplier for exponential backoff
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries: {str(e)}")
                        raise
                    
                    wait_time = delay * (backoff_factor ** attempt)
                    logger.warning(f"Function {func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {str(e)}. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
            
            # This should never be reached, but just in case
            raise last_exception
        
        return wrapper
    return decorator

class SatireSystemError(Exception):
    """Base exception for the satire system."""
    pass

class NewsFetchError(SatireSystemError):
    """Raised when news fetching fails."""
    pass

class ComicFetchError(SatireSystemError):
    """Raised when comic fetching fails."""
    pass

class ContentGenerationError(SatireSystemError):
    """Raised when content generation fails."""
    pass

class QualityControlError(SatireSystemError):
    """Raised when quality control fails."""
    pass

class PublishingError(SatireSystemError):
    """Raised when publishing fails."""
    pass

class StorageError(SatireSystemError):
    """Raised when storage operations fail."""
    pass

def handle_api_error(func: Callable) -> Callable:
    """
    Decorator to handle API errors consistently.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"API error in {func.__name__}: {str(e)}")
            # You could add alerting logic here
            raise
    return wrapper

def log_function_call(func: Callable) -> Callable:
    """
    Decorator to log function calls for debugging.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed: {str(e)}")
            raise
    return wrapper

class ErrorContext:
    """
    Context manager for handling errors with logging and cleanup.
    """
    def __init__(self, operation_name: str, cleanup_func: Optional[Callable] = None):
        self.operation_name = operation_name
        self.cleanup_func = cleanup_func
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        logger.info(f"Starting operation: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if exc_type is None:
            logger.info(f"Operation '{self.operation_name}' completed successfully in {duration:.2f}s")
        else:
            logger.error(f"Operation '{self.operation_name}' failed after {duration:.2f}s: {str(exc_val)}")
            
            # Perform cleanup if provided
            if self.cleanup_func:
                try:
                    self.cleanup_func()
                except Exception as cleanup_error:
                    logger.error(f"Cleanup failed: {str(cleanup_error)}")
        
        return False  # Don't suppress exceptions
