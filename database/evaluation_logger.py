"""
Evaluation Logger
Logs RAGAS and other evaluation metrics to PostgreSQL
"""

from typing import Optional, Dict, Any
from datetime import datetime

from .postgres_client import get_client, DatabaseError
from src.utils.logger import get_logger

log = get_logger(__name__)


class EvaluationLogger:
    """
    Logs RAG evaluation metrics to PostgreSQL.
    
    Tracks RAGAS metrics and other evaluation scores.
    """
    
    def __init__(self):
        """Initialize evaluation logger"""
        self.client = get_client()
    
    def log_evaluation(
        self,
        faithfulness_score: Optional[float] = None,
        answer_correctness: Optional[float] = None,
        context_precision: Optional[float] = None,
        context_recall: Optional[float] = None,
        test_query: Optional[str] = None,
        expected_answer: Optional[str] = None,
        actual_answer: Optional[str] = None,
        evaluation_run_id: Optional[str] = None,
        dataset_name: Optional[str] = None,
        passed_threshold: Optional[bool] = None
    ) -> Optional[int]:
        """
        Log evaluation metrics.
        
        Args:
            faithfulness_score: RAGAS faithfulness score (0-1)
            answer_correctness: RAGAS answer correctness score (0-1)
            context_precision: RAGAS context precision score (0-1)
            context_recall: RAGAS context recall score (0-1)
            test_query: Test query text
            expected_answer: Expected/ground truth answer
            actual_answer: Actual generated answer
            evaluation_run_id: Unique ID for evaluation run
            dataset_name: Name of evaluation dataset
            passed_threshold: Whether evaluation passed threshold
        
        Returns:
            Inserted record ID, or None if failed
        """
        try:
            data = {
                "timestamp": datetime.utcnow(),
                "faithfulness_score": faithfulness_score,
                "answer_correctness": answer_correctness,
                "context_precision": context_precision,
                "context_recall": context_recall,
                "test_query": test_query,
                "expected_answer": expected_answer,
                "actual_answer": actual_answer,
                "evaluation_run_id": evaluation_run_id,
                "dataset_name": dataset_name,
                "passed_threshold": passed_threshold,
            }
            
            # Remove None values
            data = {k: v for k, v in data.items() if v is not None}
            
            record_id = self.client.insert_record(
                table="rag_evaluation_metrics",
                data=data,
                returning="id"
            )
            
            log.debug(
                "Evaluation metrics logged",
                record_id=record_id,
                run_id=evaluation_run_id
            )
            
            return record_id
            
        except DatabaseError as e:
            log.error(f"Failed to log evaluation: {e.message}", details=e.details)
            return None
        except Exception as e:
            log.error(f"Unexpected error logging evaluation: {e}")
            return None
    
    def log_batch_evaluation(
        self,
        evaluations: list,
        evaluation_run_id: str,
        dataset_name: Optional[str] = None
    ) -> int:
        """
        Log multiple evaluation results in batch.
        
        Args:
            evaluations: List of evaluation dictionaries
            evaluation_run_id: Unique ID for this evaluation run
            dataset_name: Name of evaluation dataset
        
        Returns:
            Number of records inserted
        """
        try:
            records = []
            for eval_data in evaluations:
                record = {
                    "timestamp": datetime.utcnow(),
                    "evaluation_run_id": evaluation_run_id,
                    "dataset_name": dataset_name,
                    **eval_data
                }
                records.append(record)
            
            count = self.client.insert_many(
                table="rag_evaluation_metrics",
                records=records
            )
            
            log.info(
                "Batch evaluation logged",
                count=count,
                run_id=evaluation_run_id
            )
            
            return count
            
        except DatabaseError as e:
            log.error(f"Failed to log batch evaluation: {e.message}")
            return 0
        except Exception as e:
            log.error(f"Unexpected error logging batch evaluation: {e}")
            return 0
    
    def get_evaluation_summary(
        self,
        evaluation_run_id: Optional[str] = None,
        dataset_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get evaluation summary statistics.
        
        Args:
            evaluation_run_id: Filter by evaluation run ID
            dataset_name: Filter by dataset name
        
        Returns:
            Dictionary with evaluation statistics
        """
        try:
            conditions = []
            params = []
            
            if evaluation_run_id:
                conditions.append("evaluation_run_id = %s")
                params.append(evaluation_run_id)
            
            if dataset_name:
                conditions.append("dataset_name = %s")
                params.append(dataset_name)
            
            where_clause = " AND ".join(conditions) if conditions else "TRUE"
            
            query = f"""
                SELECT 
                    COUNT(*) as total_evaluations,
                    AVG(faithfulness_score) as avg_faithfulness,
                    AVG(answer_correctness) as avg_correctness,
                    AVG(context_precision) as avg_precision,
                    AVG(context_recall) as avg_recall,
                    AVG(overall_score) as avg_overall_score,
                    COUNT(*) FILTER (WHERE passed_threshold) as passed_count,
                    COUNT(*) FILTER (WHERE NOT passed_threshold) as failed_count
                FROM rag_evaluation_metrics
                WHERE {where_clause}
            """
            
            results = self.client.execute_query(query, tuple(params) if params else None)
            
            if results and len(results) > 0:
                return results[0]
            else:
                return {}
                
        except DatabaseError as e:
            log.error(f"Failed to get evaluation summary: {e.message}")
            return {}
        except Exception as e:
            log.error(f"Unexpected error getting evaluation summary: {e}")
            return {}
    
    def get_recent_evaluations(
        self,
        limit: int = 10,
        evaluation_run_id: Optional[str] = None
    ) -> list:
        """
        Get recent evaluation results.
        
        Args:
            limit: Maximum number of results to return
            evaluation_run_id: Filter by evaluation run ID
        
        Returns:
            List of evaluation records
        """
        try:
            if evaluation_run_id:
                query = """
                    SELECT * FROM rag_evaluation_metrics 
                    WHERE evaluation_run_id = %s
                    ORDER BY timestamp DESC 
                    LIMIT %s
                """
                params = (evaluation_run_id, limit)
            else:
                query = """
                    SELECT * FROM rag_evaluation_metrics 
                    ORDER BY timestamp DESC 
                    LIMIT %s
                """
                params = (limit,)
            
            results = self.client.execute_query(query, params)
            return results or []
            
        except DatabaseError as e:
            log.error(f"Failed to get recent evaluations: {e.message}")
            return []
        except Exception as e:
            log.error(f"Unexpected error getting recent evaluations: {e}")
            return []
    
    def get_evaluation_trends(
        self,
        days: int = 7
    ) -> list:
        """
        Get evaluation trends over time.
        
        Args:
            days: Number of days to look back
        
        Returns:
            List of daily evaluation statistics
        """
        try:
            query = """
                SELECT 
                    DATE(timestamp) as evaluation_date,
                    COUNT(*) as evaluation_count,
                    AVG(overall_score) as avg_score,
                    AVG(faithfulness_score) as avg_faithfulness,
                    AVG(answer_correctness) as avg_correctness,
                    COUNT(*) FILTER (WHERE passed_threshold) as passed_count
                FROM rag_evaluation_metrics
                WHERE timestamp > NOW() - INTERVAL '%s days'
                GROUP BY DATE(timestamp)
                ORDER BY evaluation_date DESC
            """
            
            results = self.client.execute_query(query, (days,))
            return results or []
            
        except DatabaseError as e:
            log.error(f"Failed to get evaluation trends: {e.message}")
            return []
        except Exception as e:
            log.error(f"Unexpected error getting evaluation trends: {e}")
            return []


# Global logger instance
_eval_logger = None


def get_evaluation_logger() -> EvaluationLogger:
    """
    Get global evaluation logger instance (singleton).
    
    Returns:
        EvaluationLogger instance
    """
    global _eval_logger
    if _eval_logger is None:
        _eval_logger = EvaluationLogger()
    return _eval_logger
