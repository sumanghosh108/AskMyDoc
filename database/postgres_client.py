"""
PostgreSQL Client
Connection pool manager and query execution utilities
"""

import psycopg2
from psycopg2 import pool, sql
from psycopg2.extras import RealDictCursor
import os
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from src.utils.logger import get_logger
from src.utils.exceptions import RAGException

log = get_logger(__name__)

# Database configuration
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")  # No default - must be set in .env
DB_NAME = os.getenv("POSTGRES_DB", "AskMyDocLOG")

# Connection pool configuration
MIN_CONNECTIONS = int(os.getenv("POSTGRES_MIN_CONN", "2"))
MAX_CONNECTIONS = int(os.getenv("POSTGRES_MAX_CONN", "10"))


class DatabaseError(RAGException):
    """Database operation error"""
    pass


class PostgresClient:
    """
    PostgreSQL connection pool manager.
    
    Provides connection pooling and query execution utilities.
    Thread-safe and production-ready.
    """
    
    _instance = None
    _connection_pool = None
    
    def __new__(cls):
        """Singleton pattern to ensure single connection pool"""
        if cls._instance is None:
            cls._instance = super(PostgresClient, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize connection pool"""
        if self._connection_pool is None:
            self._initialize_pool()
    
    def _initialize_pool(self):
        """Create connection pool"""
        try:
            self._connection_pool = psycopg2.pool.ThreadedConnectionPool(
                MIN_CONNECTIONS,
                MAX_CONNECTIONS,
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            log.info(
                "PostgreSQL connection pool created",
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                min_conn=MIN_CONNECTIONS,
                max_conn=MAX_CONNECTIONS
            )
        except psycopg2.Error as e:
            log.error(f"Failed to create connection pool: {e}")
            raise DatabaseError(
                "Failed to create database connection pool",
                details={"host": DB_HOST, "port": DB_PORT, "database": DB_NAME},
                original_error=e
            )
    
    @contextmanager
    def get_connection(self):
        """
        Get connection from pool (context manager).
        
        Usage:
            with client.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM table")
        
        Yields:
            psycopg2 connection
        """
        conn = None
        try:
            conn = self._connection_pool.getconn()
            yield conn
        except psycopg2.Error as e:
            log.error(f"Database connection error: {e}")
            if conn:
                conn.rollback()
            raise DatabaseError(
                "Database connection error",
                original_error=e
            )
        finally:
            if conn:
                self._connection_pool.putconn(conn)
    
    def execute_query(
        self,
        query: str,
        params: Optional[tuple] = None,
        fetch: bool = True
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Execute SQL query.
        
        Args:
            query: SQL query string
            params: Query parameters (tuple)
            fetch: Whether to fetch results
        
        Returns:
            List of dictionaries (if fetch=True), None otherwise
        
        Raises:
            DatabaseError: If query execution fails
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute(query, params)
                
                if fetch:
                    results = cursor.fetchall()
                    cursor.close()
                    return [dict(row) for row in results]
                else:
                    conn.commit()
                    cursor.close()
                    return None
                    
        except psycopg2.Error as e:
            log.error(f"Query execution failed: {e}", query=query[:100])
            raise DatabaseError(
                "Query execution failed",
                details={"query": query[:100]},
                original_error=e
            )
    
    def execute_many(
        self,
        query: str,
        params_list: List[tuple]
    ) -> int:
        """
        Execute query with multiple parameter sets (batch insert).
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
        
        Returns:
            Number of rows affected
        
        Raises:
            DatabaseError: If execution fails
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                row_count = cursor.rowcount
                conn.commit()
                cursor.close()
                return row_count
                
        except psycopg2.Error as e:
            log.error(f"Batch execution failed: {e}")
            raise DatabaseError(
                "Batch execution failed",
                details={"batch_size": len(params_list)},
                original_error=e
            )
    
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
        
        Raises:
            DatabaseError: If insert fails
        """
        try:
            columns = list(data.keys())
            values = list(data.values())
            placeholders = ["%s"] * len(values)
            
            query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                sql.Identifier(table),
                sql.SQL(", ").join(map(sql.Identifier, columns)),
                sql.SQL(", ").join(map(sql.SQL, placeholders))
            )
            
            if returning:
                query = sql.SQL("{} RETURNING {}").format(
                    query,
                    sql.Identifier(returning)
                )
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, values)
                
                result = None
                if returning:
                    result = cursor.fetchone()[0]
                
                conn.commit()
                cursor.close()
                return result
                
        except psycopg2.Error as e:
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
        
        Raises:
            DatabaseError: If insert fails
        """
        if not records:
            return 0
        
        try:
            # All records should have same columns
            columns = list(records[0].keys())
            placeholders = ["%s"] * len(columns)
            
            query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                sql.Identifier(table),
                sql.SQL(", ").join(map(sql.Identifier, columns)),
                sql.SQL(", ").join(map(sql.SQL, placeholders))
            )
            
            # Extract values in same order as columns
            params_list = [
                tuple(record[col] for col in columns)
                for record in records
            ]
            
            return self.execute_many(str(query), params_list)
            
        except psycopg2.Error as e:
            log.error(f"Batch insert failed: {e}", table=table, count=len(records))
            raise DatabaseError(
                "Batch insert failed",
                details={"table": table, "record_count": len(records)},
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
            where: Dictionary of column: value pairs for WHERE clause
        
        Returns:
            Number of rows updated
        
        Raises:
            DatabaseError: If update fails
        """
        try:
            set_clause = sql.SQL(", ").join(
                sql.SQL("{} = %s").format(sql.Identifier(col))
                for col in data.keys()
            )
            
            where_clause = sql.SQL(" AND ").join(
                sql.SQL("{} = %s").format(sql.Identifier(col))
                for col in where.keys()
            )
            
            query = sql.SQL("UPDATE {} SET {} WHERE {}").format(
                sql.Identifier(table),
                set_clause,
                where_clause
            )
            
            params = tuple(data.values()) + tuple(where.values())
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                row_count = cursor.rowcount
                conn.commit()
                cursor.close()
                return row_count
                
        except psycopg2.Error as e:
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
            where: Dictionary of column: value pairs for WHERE clause
        
        Returns:
            Number of rows deleted
        
        Raises:
            DatabaseError: If delete fails
        """
        try:
            where_clause = sql.SQL(" AND ").join(
                sql.SQL("{} = %s").format(sql.Identifier(col))
                for col in where.keys()
            )
            
            query = sql.SQL("DELETE FROM {} WHERE {}").format(
                sql.Identifier(table),
                where_clause
            )
            
            params = tuple(where.values())
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                row_count = cursor.rowcount
                conn.commit()
                cursor.close()
                return row_count
                
        except psycopg2.Error as e:
            log.error(f"Delete failed: {e}", table=table)
            raise DatabaseError(
                "Delete operation failed",
                details={"table": table},
                original_error=e
            )
    
    def close_all_connections(self):
        """Close all connections in pool"""
        if self._connection_pool:
            self._connection_pool.closeall()
            log.info("All database connections closed")
    
    def get_pool_status(self) -> Dict[str, int]:
        """
        Get connection pool status.
        
        Returns:
            Dictionary with pool statistics
        """
        if not self._connection_pool:
            return {"status": "not_initialized"}
        
        # Note: ThreadedConnectionPool doesn't expose these directly
        # This is a simplified version
        return {
            "min_connections": MIN_CONNECTIONS,
            "max_connections": MAX_CONNECTIONS,
            "status": "active"
        }


# Global client instance
_client = None


def get_client() -> PostgresClient:
    """
    Get global PostgreSQL client instance (singleton).
    
    Returns:
        PostgresClient instance
    """
    global _client
    if _client is None:
        _client = PostgresClient()
    return _client
