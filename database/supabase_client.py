"""
Supabase Client
Connection manager and query execution utilities for Supabase.
Replaces the previous PostgreSQL direct connection with Supabase SDK.
"""

from typing import Optional, List, Dict, Any

from src.utils.logger import get_logger
from src.utils.exceptions import RAGException
from src.core.config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

log = get_logger(__name__)


class DatabaseError(RAGException):
    """Database operation error"""
    pass


class SupabaseClient:
    """
    Supabase client wrapper for database operations.

    Uses the Supabase Python SDK with service_role key
    for full access to logging tables (bypasses RLS).
    """

    _instance = None
    _client = None

    def __new__(cls):
        """Singleton pattern to ensure single client instance."""
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize Supabase client."""
        if self._client is None:
            self._initialize_client()

    def _initialize_client(self):
        """Create Supabase client connection."""
        try:
            from supabase import create_client

            if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
                raise DatabaseError(
                    "Supabase credentials not configured",
                    details={"url_set": bool(SUPABASE_URL), "key_set": bool(SUPABASE_SERVICE_ROLE_KEY)}
                )

            self._client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
            log.info(
                "Supabase client initialized",
                url=SUPABASE_URL[:40] + "...",
            )
        except DatabaseError:
            raise
        except Exception as e:
            log.error(f"Failed to create Supabase client: {e}")
            raise DatabaseError(
                "Failed to create Supabase client",
                details={"url": SUPABASE_URL[:40] if SUPABASE_URL else "not set"},
                original_error=e
            )

    @property
    def client(self):
        """Get the underlying Supabase client."""
        return self._client

    def insert_record(
        self,
        table: str,
        data: Dict[str, Any],
        returning: Optional[str] = "id"
    ) -> Optional[Any]:
        """
        Insert single record into table.

        Args:
            table: Table name
            data: Dictionary of column: value pairs
            returning: Column to return (e.g., 'id'), None for no return

        Returns:
            Value of returning column, or None
        """
        try:
            # Convert datetime objects to ISO format strings for JSON serialization
            serialized_data = {}
            for k, v in data.items():
                if hasattr(v, 'isoformat'):
                    serialized_data[k] = v.isoformat()
                else:
                    serialized_data[k] = v

            result = self._client.table(table).insert(serialized_data).execute()

            if result.data and returning:
                return result.data[0].get(returning)
            return None

        except Exception as e:
            log.error(f"Insert failed: {e}", table=table)
            raise DatabaseError(
                "Insert operation failed",
                details={"table": table, "columns": list(data.keys())},
                original_error=e
            )

    def insert_many(
        self,
        table: str,
        records: List[Dict[str, Any]]
    ) -> int:
        """
        Insert multiple records into table.

        Args:
            table: Table name
            records: List of dictionaries (column: value pairs)

        Returns:
            Number of rows inserted
        """
        if not records:
            return 0

        try:
            # Serialize datetime objects
            serialized_records = []
            for record in records:
                serialized = {}
                for k, v in record.items():
                    if hasattr(v, 'isoformat'):
                        serialized[k] = v.isoformat()
                    else:
                        serialized[k] = v
                serialized_records.append(serialized)

            result = self._client.table(table).insert(serialized_records).execute()
            return len(result.data) if result.data else 0

        except Exception as e:
            log.error(f"Batch insert failed: {e}", table=table, count=len(records))
            raise DatabaseError(
                "Batch insert failed",
                details={"table": table, "record_count": len(records)},
                original_error=e
            )

    def execute_query(
        self,
        table: str,
        select: str = "*",
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = True,
        limit: Optional[int] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Execute a select query on a table.

        Args:
            table: Table name
            select: Columns to select (default "*")
            filters: Dictionary of column: value equality filters
            order_by: Column to order by
            order_desc: Whether to order descending
            limit: Maximum rows to return

        Returns:
            List of dictionaries, or None
        """
        try:
            query = self._client.table(table).select(select)

            if filters:
                for col, val in filters.items():
                    query = query.eq(col, val)

            if order_by:
                query = query.order(order_by, desc=order_desc)

            if limit:
                query = query.limit(limit)

            result = query.execute()
            return result.data if result.data else []

        except Exception as e:
            log.error(f"Query execution failed: {e}", table=table)
            raise DatabaseError(
                "Query execution failed",
                details={"table": table, "select": select},
                original_error=e
            )

    def update_record(
        self,
        table: str,
        data: Dict[str, Any],
        where: Dict[str, Any]
    ) -> int:
        """
        Update records in table.

        Args:
            table: Table name
            data: Dictionary of column: value pairs to update
            where: Dictionary of column: value pairs for filter

        Returns:
            Number of rows updated
        """
        try:
            query = self._client.table(table).update(data)

            for col, val in where.items():
                query = query.eq(col, val)

            result = query.execute()
            return len(result.data) if result.data else 0

        except Exception as e:
            log.error(f"Update failed: {e}", table=table)
            raise DatabaseError(
                "Update operation failed",
                details={"table": table},
                original_error=e
            )

    def delete_records(
        self,
        table: str,
        where: Dict[str, Any]
    ) -> int:
        """
        Delete records from table.

        Args:
            table: Table name
            where: Dictionary of column: value pairs for filter

        Returns:
            Number of rows deleted
        """
        try:
            query = self._client.table(table).delete()

            for col, val in where.items():
                query = query.eq(col, val)

            result = query.execute()
            return len(result.data) if result.data else 0

        except Exception as e:
            log.error(f"Delete failed: {e}", table=table)
            raise DatabaseError(
                "Delete operation failed",
                details={"table": table},
                original_error=e
            )

    def rpc(self, function_name: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Call a Supabase RPC (stored function).

        Args:
            function_name: Name of the PostgreSQL function
            params: Parameters to pass to the function

        Returns:
            Result data from the function
        """
        try:
            result = self._client.rpc(function_name, params or {}).execute()
            return result.data

        except Exception as e:
            log.error(f"RPC call failed: {e}", function=function_name)
            raise DatabaseError(
                "RPC call failed",
                details={"function": function_name},
                original_error=e
            )

    def health_check(self) -> Dict[str, Any]:
        """
        Check Supabase connection health.

        Returns:
            Dictionary with health status
        """
        try:
            # Try to query a table to verify connection
            result = self._client.table("rag_query_logs").select("id").limit(1).execute()
            return {
                "status": "healthy",
                "connected": True,
                "provider": "supabase",
                "url": SUPABASE_URL[:40] + "..." if SUPABASE_URL else "not set"
            }
        except Exception as e:
            error_str = str(e)
            # PGRST205 means table not found — connection works but tables missing
            if "PGRST205" in error_str:
                return {
                    "status": "healthy",
                    "connected": True,
                    "tables_missing": True,
                    "provider": "supabase",
                    "url": SUPABASE_URL[:40] + "..." if SUPABASE_URL else "not set",
                    "note": "Tables not yet created. Run database/supabase_migration.sql"
                }
            return {
                "status": "unhealthy",
                "connected": False,
                "provider": "supabase",
                "error": error_str
            }


# Global client instance
_client = None


def get_client() -> SupabaseClient:
    """
    Get global Supabase client instance (singleton).

    Returns:
        SupabaseClient instance
    """
    global _client
    if _client is None:
        _client = SupabaseClient()
    return _client
