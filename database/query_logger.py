"""
Query Logger
Logs query execution metrics to Supabase (PostgreSQL)
"""

from typing import Dict, Any, Optional
from datetime import datetime

from .supabase_client import get_client, DatabaseError
from src.utils.logger import get_logger

log = get_logger(__name__)


class QueryLogger:
    """
    Logs RAG query execution metrics to Supabase.

    Tracks latency, chunk counts, model usage, and other metrics.
    """

    def __init__(self):
        """Initialize query logger"""
        self.client = get_client()

    def log_query(
        self,
        query_text: str,
        total_latency: float,
        retrieval_latency: Optional[float] = None,
        rerank_latency: Optional[float] = None,
        llm_latency: Optional[float] = None,
        retrieved_chunks: Optional[int] = None,
        reranked_chunks: Optional[int] = None,
        model_used: Optional[str] = None,
        embedding_model: Optional[str] = None,
        query_rewriting_enabled: bool = False,
        multi_hop_enabled: bool = False,
        cache_hit: bool = False,
        answer_length: Optional[int] = None,
        source_count: Optional[int] = None,
        **kwargs
    ) -> Optional[int]:
        """
        Log query execution metrics.

        Args:
            query_text: The user's query
            total_latency: Total pipeline latency (ms)
            retrieval_latency: Retrieval latency (ms)
            rerank_latency: Reranking latency (ms)
            llm_latency: LLM generation latency (ms)
            retrieved_chunks: Number of chunks retrieved
            reranked_chunks: Number of chunks after reranking
            model_used: LLM model name
            embedding_model: Embedding model name
            query_rewriting_enabled: Whether query rewriting was used
            multi_hop_enabled: Whether multi-hop was used
            cache_hit: Whether cache was hit
            answer_length: Length of generated answer
            source_count: Number of sources cited
            **kwargs: Additional metadata

        Returns:
            Inserted record ID, or None if failed
        """
        try:
            data = {
                "timestamp": datetime.utcnow().isoformat(),
                "query_text": query_text,
                "total_latency": total_latency,
                "retrieval_latency": retrieval_latency,
                "rerank_latency": rerank_latency,
                "llm_latency": llm_latency,
                "retrieved_chunks": retrieved_chunks,
                "reranked_chunks": reranked_chunks,
                "model_used": model_used,
                "embedding_model": embedding_model,
                "query_rewriting_enabled": query_rewriting_enabled,
                "multi_hop_enabled": multi_hop_enabled,
                "cache_hit": cache_hit,
                "answer_length": answer_length,
                "source_count": source_count,
            }

            # Remove None values
            data = {k: v for k, v in data.items() if v is not None}

            record_id = self.client.insert_record(
                table="rag_query_logs",
                data=data,
                returning="id"
            )

            log.debug(
                "Query logged to database",
                record_id=record_id,
                query_length=len(query_text),
                total_latency=total_latency
            )

            return record_id

        except DatabaseError as e:
            log.error(f"Failed to log query: {e.message}", details=e.details)
            return None
        except Exception as e:
            log.error(f"Unexpected error logging query: {e}")
            return None

    def log_component_latency(
        self,
        query_log_id: int,
        component_name: str,
        latency_ms: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[int]:
        """
        Log individual component latency.

        Args:
            query_log_id: ID from rag_query_logs table
            component_name: Name of the component
            latency_ms: Latency in milliseconds
            metadata: Additional metadata (stored as JSONB)

        Returns:
            Inserted record ID, or None if failed
        """
        try:
            import json

            data = {
                "query_log_id": query_log_id,
                "timestamp": datetime.utcnow().isoformat(),
                "component_name": component_name,
                "latency_ms": latency_ms,
            }

            if metadata:
                data["metadata"] = json.dumps(metadata)

            record_id = self.client.insert_record(
                table="rag_component_latency",
                data=data,
                returning="id"
            )

            log.debug(
                "Component latency logged",
                component=component_name,
                latency=latency_ms
            )

            return record_id

        except DatabaseError as e:
            log.error(f"Failed to log component latency: {e.message}")
            return None
        except Exception as e:
            log.error(f"Unexpected error logging component latency: {e}")
            return None

    def log_cache_stats(
        self,
        cache_type: str,
        hit_count: int,
        miss_count: int,
        window_start: Optional[datetime] = None,
        window_end: Optional[datetime] = None
    ) -> Optional[int]:
        """
        Log cache statistics.

        Args:
            cache_type: Type of cache ('retrieval', 'response', 'embedding')
            hit_count: Number of cache hits
            miss_count: Number of cache misses
            window_start: Start of time window
            window_end: End of time window

        Returns:
            Inserted record ID, or None if failed
        """
        try:
            data = {
                "timestamp": datetime.utcnow().isoformat(),
                "cache_type": cache_type,
                "hit_count": hit_count,
                "miss_count": miss_count,
            }

            if window_start:
                data["window_start"] = window_start.isoformat()
            if window_end:
                data["window_end"] = window_end.isoformat()

            record_id = self.client.insert_record(
                table="rag_cache_stats",
                data=data,
                returning="id"
            )

            log.debug(
                "Cache stats logged",
                cache_type=cache_type,
                hit_count=hit_count,
                miss_count=miss_count
            )

            return record_id

        except DatabaseError as e:
            log.error(f"Failed to log cache stats: {e.message}")
            return None
        except Exception as e:
            log.error(f"Unexpected error logging cache stats: {e}")
            return None

    def get_recent_queries(
        self,
        limit: int = 10,
        slow_only: bool = False
    ) -> list:
        """
        Get recent queries from database.

        Args:
            limit: Maximum number of queries to return
            slow_only: If True, only return slow queries

        Returns:
            List of query records
        """
        try:
            query = self.client.client.table("rag_query_logs").select("*")

            if slow_only:
                query = query.eq("is_slow_query", True)

            query = query.order("timestamp", desc=True).limit(limit)
            result = query.execute()
            return result.data if result.data else []

        except Exception as e:
            log.error(f"Failed to get recent queries: {e}")
            return []

    def get_latency_stats(
        self,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get latency statistics for time period.

        Uses Supabase RPC for complex aggregation queries.

        Args:
            hours: Number of hours to look back

        Returns:
            Dictionary with latency statistics
        """
        try:
            result = self.client.rpc("get_latency_stats", {"hours_back": hours})
            if result and len(result) > 0:
                return result[0]
            return {}

        except Exception as e:
            log.error(f"Failed to get latency stats: {e}")
            return {}

    def get_model_performance(self) -> list:
        """
        Get performance comparison by model.

        Returns:
            List of model performance records
        """
        try:
            result = self.client.rpc("get_model_performance", {})
            return result if result else []

        except Exception as e:
            log.error(f"Failed to get model performance: {e}")
            return []


# Global logger instance
_logger = None


def get_query_logger() -> QueryLogger:
    """
    Get global query logger instance (singleton).

    Returns:
        QueryLogger instance
    """
    global _logger
    if _logger is None:
        _logger = QueryLogger()
    return _logger
