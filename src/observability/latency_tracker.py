"""
Latency tracking module for RAG pipeline observability.
Tracks timing across all components with structured logging.
"""

import time
from typing import Optional, Any
from contextlib import contextmanager

from src.utils.logger import get_logger

log = get_logger(__name__)


class LatencyTracker:
    """
    Tracks latency across RAG pipeline components.
    
    Components tracked:
    - Query rewriting
    - Retrieval (vector, BM25, hybrid)
    - Reranking
    - Multi-hop reasoning
    - Context building
    - LLM generation
    - Total end-to-end
    """

    def __init__(self, query_log_id: Optional[int] = None):
        """
        Initialize latency tracker.
        
        Args:
            query_log_id: Optional ID from rag_query_logs table for PostgreSQL logging
        """
        self.timings = {}
        self.start_time = None
        self.end_time = None
        self.query_log_id = query_log_id
        self.query_logger = None
        
        # Initialize query logger if query_log_id provided
        if query_log_id is not None:
            try:
                from database.query_logger import get_query_logger
                self.query_logger = get_query_logger()
            except Exception as e:
                log.warning("Failed to initialize query logger for latency tracking", error=str(e))

    def start(self):
        """Start tracking total pipeline time."""
        self.start_time = time.time()
        self.timings = {}

    def end(self):
        """End tracking total pipeline time."""
        self.end_time = time.time()

    @contextmanager
    def track(self, component: str, **metadata):
        """
        Context manager to track a component's execution time.

        Usage:
            with tracker.track("retrieval", method="hybrid"):
                # ... retrieval code ...
                pass

        Args:
            component: Name of the component being tracked.
            **metadata: Additional metadata to log.
        """
        start = time.time()
        
        try:
            yield
        finally:
            elapsed = time.time() - start
            duration_ms = round(elapsed * 1000, 2)
            
            # Store timing
            if component not in self.timings:
                self.timings[component] = []
            
            self.timings[component].append({
                "duration_ms": duration_ms,
                "metadata": metadata
            })
            
            # Log to console
            log.info(
                f"{component} completed",
                component=component,
                duration_ms=duration_ms,
                **metadata
            )
            
            # Log to PostgreSQL if enabled
            if self.query_logger and self.query_log_id:
                try:
                    self.query_logger.log_component_latency(
                        query_log_id=self.query_log_id,
                        component_name=component,
                        latency_ms=duration_ms,
                        metadata=metadata if metadata else None
                    )
                except Exception as e:
                    log.warning("Failed to log component latency to PostgreSQL", 
                               component=component, error=str(e))

    def get_summary(self) -> dict:
        """
        Get summary of all tracked timings.

        Returns:
            Dictionary with timing statistics.
        """
        if self.start_time is None:
            return {"error": "Tracking not started"}

        total_time = (
            (self.end_time or time.time()) - self.start_time
        ) * 1000  # Convert to ms

        summary = {
            "total_time_ms": round(total_time, 2),
            "components": {}
        }

        for component, timings in self.timings.items():
            durations = [t["duration_ms"] for t in timings]
            
            summary["components"][component] = {
                "count": len(durations),
                "total_ms": round(sum(durations), 2),
                "avg_ms": round(sum(durations) / len(durations), 2),
                "min_ms": round(min(durations), 2),
                "max_ms": round(max(durations), 2),
            }

        return summary

    def log_summary(self, query: Optional[str] = None):
        """
        Log the complete timing summary.

        Args:
            query: Optional query string for context.
        """
        summary = self.get_summary()
        
        log.info(
            "Pipeline timing summary",
            query=query[:100] if query else None,
            **summary
        )

    def get_breakdown(self) -> dict:
        """
        Get detailed breakdown of time spent in each component.

        Returns:
            Dictionary with percentage breakdown.
        """
        summary = self.get_summary()
        
        if "error" in summary:
            return summary

        total_time = summary["total_time_ms"]
        breakdown = {}

        for component, stats in summary["components"].items():
            component_time = stats["total_ms"]
            percentage = (component_time / total_time * 100) if total_time > 0 else 0
            
            breakdown[component] = {
                "time_ms": component_time,
                "percentage": round(percentage, 1),
                "count": stats["count"]
            }

        return {
            "total_time_ms": total_time,
            "breakdown": breakdown
        }


class PipelineMetrics:
    """
    Aggregates metrics across multiple pipeline executions.
    Useful for monitoring and alerting.
    """

    def __init__(self):
        self.executions = []

    def record(self, tracker: LatencyTracker, query: str, success: bool):
        """
        Record metrics from a pipeline execution.

        Args:
            tracker: LatencyTracker instance with timing data.
            query: The query that was processed.
            success: Whether the execution succeeded.
        """
        summary = tracker.get_summary()
        
        self.executions.append({
            "timestamp": time.time(),
            "query": query[:100],
            "success": success,
            "total_time_ms": summary.get("total_time_ms", 0),
            "components": summary.get("components", {})
        })

    def get_stats(self, last_n: Optional[int] = None) -> dict:
        """
        Get aggregate statistics.

        Args:
            last_n: Only consider last N executions (None for all).

        Returns:
            Dictionary with aggregate stats.
        """
        if not self.executions:
            return {"error": "No executions recorded"}

        executions = self.executions[-last_n:] if last_n else self.executions

        total_times = [e["total_time_ms"] for e in executions]
        success_count = sum(1 for e in executions if e["success"])

        stats = {
            "total_executions": len(executions),
            "success_count": success_count,
            "failure_count": len(executions) - success_count,
            "success_rate": round(success_count / len(executions), 3),
            "latency": {
                "avg_ms": round(sum(total_times) / len(total_times), 2),
                "min_ms": round(min(total_times), 2),
                "max_ms": round(max(total_times), 2),
                "p50_ms": round(sorted(total_times)[len(total_times) // 2], 2),
                "p95_ms": round(sorted(total_times)[int(len(total_times) * 0.95)], 2),
                "p99_ms": round(sorted(total_times)[int(len(total_times) * 0.99)], 2),
            }
        }

        return stats

    def log_stats(self, last_n: Optional[int] = None):
        """
        Log aggregate statistics.

        Args:
            last_n: Only consider last N executions.
        """
        stats = self.get_stats(last_n)
        log.info("Pipeline metrics", **stats)


# Global metrics instance
_metrics_instance = None


def get_metrics() -> PipelineMetrics:
    """Get or create the global metrics instance."""
    global _metrics_instance
    
    if _metrics_instance is None:
        _metrics_instance = PipelineMetrics()
    
    return _metrics_instance
