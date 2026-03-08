"""
Error Logger
Logs pipeline errors and failures to PostgreSQL
"""

from typing import Optional, Dict, Any
from datetime import datetime
import traceback
import json

from .postgres_client import get_client, DatabaseError
from src.utils.logger import get_logger

log = get_logger(__name__)


class ErrorLogger:
    """
    Logs RAG pipeline errors to PostgreSQL.
    
    Captures error details, stack traces, and context for debugging.
    """
    
    def __init__(self):
        """Initialize error logger"""
        self.client = get_client()
    
    def log_error(
        self,
        pipeline_stage: str,
        error_message: str,
        query_text: Optional[str] = None,
        error_type: Optional[str] = None,
        stack_trace: Optional[str] = None,
        severity: str = "ERROR",
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[int]:
        """
        Log pipeline error.
        
        Args:
            pipeline_stage: Stage where error occurred
            error_message: Error message
            query_text: User query (if applicable)
            error_type: Type/class of error
            stack_trace: Full stack trace
            severity: Error severity (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            user_id: User identifier
            session_id: Session identifier
            metadata: Additional context (stored as JSONB)
        
        Returns:
            Inserted record ID, or None if failed
        """
        try:
            data = {
                "timestamp": datetime.utcnow(),
                "pipeline_stage": pipeline_stage,
                "error_message": error_message,
                "query_text": query_text,
                "error_type": error_type,
                "stack_trace": stack_trace,
                "severity": severity,
                "user_id": user_id,
                "session_id": session_id,
            }
            
            if metadata:
                data["metadata"] = json.dumps(metadata)
            
            # Remove None values
            data = {k: v for k, v in data.items() if v is not None}
            
            record_id = self.client.insert_record(
                table="rag_error_logs",
                data=data,
                returning="id"
            )
            
            log.debug(
                "Error logged to database",
                record_id=record_id,
                stage=pipeline_stage,
                severity=severity
            )
            
            return record_id
            
        except DatabaseError as e:
            log.error(f"Failed to log error: {e.message}", details=e.details)
            # Don't raise - error logging failure shouldn't break the pipeline
            return None
        except Exception as e:
            log.error(f"Unexpected error logging error: {e}")
            return None
    
    def log_exception(
        self,
        exception: Exception,
        pipeline_stage: str,
        query_text: Optional[str] = None,
        severity: str = "ERROR",
        **kwargs
    ) -> Optional[int]:
        """
        Log exception with automatic stack trace capture.
        
        Args:
            exception: The exception object
            pipeline_stage: Stage where error occurred
            query_text: User query (if applicable)
            severity: Error severity
            **kwargs: Additional metadata
        
        Returns:
            Inserted record ID, or None if failed
        """
        error_type = exception.__class__.__name__
        error_message = str(exception)
        stack_trace = traceback.format_exc()
        
        return self.log_error(
            pipeline_stage=pipeline_stage,
            error_message=error_message,
            query_text=query_text,
            error_type=error_type,
            stack_trace=stack_trace,
            severity=severity,
            metadata=kwargs if kwargs else None
        )
    
    def get_recent_errors(
        self,
        limit: int = 10,
        stage: Optional[str] = None,
        severity: Optional[str] = None
    ) -> list:
        """
        Get recent errors from database.
        
        Args:
            limit: Maximum number of errors to return
            stage: Filter by pipeline stage
            severity: Filter by severity
        
        Returns:
            List of error records
        """
        try:
            conditions = []
            params = []
            
            if stage:
                conditions.append("pipeline_stage = %s")
                params.append(stage)
            
            if severity:
                conditions.append("severity = %s")
                params.append(severity)
            
            where_clause = " AND ".join(conditions) if conditions else "TRUE"
            
            query = f"""
                SELECT * FROM rag_error_logs 
                WHERE {where_clause}
                ORDER BY timestamp DESC 
                LIMIT %s
            """
            params.append(limit)
            
            results = self.client.execute_query(query, tuple(params))
            return results or []
            
        except DatabaseError as e:
            log.error(f"Failed to get recent errors: {e.message}")
            return []
        except Exception as e:
            log.error(f"Unexpected error getting recent errors: {e}")
            return []
    
    def get_error_summary(
        self,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get error summary statistics.
        
        Args:
            hours: Number of hours to look back
        
        Returns:
            Dictionary with error statistics
        """
        try:
            query = """
                SELECT 
                    COUNT(*) as total_errors,
                    COUNT(DISTINCT pipeline_stage) as affected_stages,
                    COUNT(DISTINCT error_type) as unique_error_types,
                    COUNT(*) FILTER (WHERE severity = 'CRITICAL') as critical_count,
                    COUNT(*) FILTER (WHERE severity = 'ERROR') as error_count,
                    COUNT(*) FILTER (WHERE severity = 'WARNING') as warning_count
                FROM rag_error_logs
                WHERE timestamp > NOW() - INTERVAL '%s hours'
            """
            
            results = self.client.execute_query(query, (hours,))
            
            if results and len(results) > 0:
                return results[0]
            else:
                return {}
                
        except DatabaseError as e:
            log.error(f"Failed to get error summary: {e.message}")
            return {}
        except Exception as e:
            log.error(f"Unexpected error getting error summary: {e}")
            return {}
    
    def get_errors_by_stage(
        self,
        hours: int = 24
    ) -> list:
        """
        Get error counts grouped by pipeline stage.
        
        Args:
            hours: Number of hours to look back
        
        Returns:
            List of stage error counts
        """
        try:
            query = """
                SELECT 
                    pipeline_stage,
                    COUNT(*) as error_count,
                    COUNT(DISTINCT error_type) as unique_error_types,
                    MAX(timestamp) as last_error_time
                FROM rag_error_logs
                WHERE timestamp > NOW() - INTERVAL '%s hours'
                GROUP BY pipeline_stage
                ORDER BY error_count DESC
            """
            
            results = self.client.execute_query(query, (hours,))
            return results or []
            
        except DatabaseError as e:
            log.error(f"Failed to get errors by stage: {e.message}")
            return []
        except Exception as e:
            log.error(f"Unexpected error getting errors by stage: {e}")
            return []
    
    def get_top_errors(
        self,
        limit: int = 10,
        hours: int = 24
    ) -> list:
        """
        Get most frequent errors.
        
        Args:
            limit: Maximum number of error types to return
            hours: Number of hours to look back
        
        Returns:
            List of top error types with counts
        """
        try:
            query = """
                SELECT 
                    error_type,
                    error_message,
                    pipeline_stage,
                    COUNT(*) as occurrence_count,
                    MAX(timestamp) as last_occurrence
                FROM rag_error_logs
                WHERE timestamp > NOW() - INTERVAL '%s hours'
                GROUP BY error_type, error_message, pipeline_stage
                ORDER BY occurrence_count DESC
                LIMIT %s
            """
            
            results = self.client.execute_query(query, (hours, limit))
            return results or []
            
        except DatabaseError as e:
            log.error(f"Failed to get top errors: {e.message}")
            return []
        except Exception as e:
            log.error(f"Unexpected error getting top errors: {e}")
            return []


# Global logger instance
_error_logger = None


def get_error_logger() -> ErrorLogger:
    """
    Get global error logger instance (singleton).
    
    Returns:
        ErrorLogger instance
    """
    global _error_logger
    if _error_logger is None:
        _error_logger = ErrorLogger()
    return _error_logger
