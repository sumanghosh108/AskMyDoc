"""
Error Logger
Logs pipeline errors and failures to Supabase (PostgreSQL)
"""

from typing import Optional, Dict, Any
from datetime import datetime
import traceback
import json

from .supabase_client import get_client, DatabaseError
from src.utils.logger import get_logger

log = get_logger(__name__)


class ErrorLogger:
    """
    Logs RAG pipeline errors to Supabase.

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
                "timestamp": datetime.utcnow().isoformat(),
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
            query = self.client.client.table("rag_error_logs").select("*")

            if stage:
                query = query.eq("pipeline_stage", stage)
            if severity:
                query = query.eq("severity", severity)

            query = query.order("timestamp", desc=True).limit(limit)
            result = query.execute()
            return result.data if result.data else []

        except Exception as e:
            log.error(f"Failed to get recent errors: {e}")
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
            result = self.client.rpc("get_error_summary", {"hours_back": hours})
            if result and len(result) > 0:
                return result[0]
            return {}

        except Exception as e:
            log.error(f"Failed to get error summary: {e}")
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
            result = self.client.rpc("get_errors_by_stage", {"hours_back": hours})
            return result if result else []

        except Exception as e:
            log.error(f"Failed to get errors by stage: {e}")
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
            result = self.client.rpc("get_top_errors", {"hours_back": hours, "max_results": limit})
            return result if result else []

        except Exception as e:
            log.error(f"Failed to get top errors: {e}")
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
