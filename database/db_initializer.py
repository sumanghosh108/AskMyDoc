"""
Database Initializer
Idempotent database and table creation for RAG logging system
"""

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from pathlib import Path
from typing import Optional

from src.utils.logger import get_logger

log = get_logger(__name__)

# Database configuration from environment
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")  # No default - must be set in .env
DB_NAME = os.getenv("POSTGRES_DB", "AskMyDocLOG")


def check_database_exists(cursor, db_name: str) -> bool:
    """
    Check if database exists.
    
    Args:
        cursor: PostgreSQL cursor
        db_name: Database name to check
    
    Returns:
        True if database exists, False otherwise
    """
    cursor.execute(
        "SELECT 1 FROM pg_database WHERE datname = %s",
        (db_name,)
    )
    return cursor.fetchone() is not None


def create_database(db_name: str) -> bool:
    """
    Create database if it doesn't exist.
    
    Args:
        db_name: Name of the database to create
    
    Returns:
        True if database was created, False if it already existed
    """
    try:
        # Connect to PostgreSQL server (not to specific database)
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database="postgres"  # Connect to default postgres database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        if check_database_exists(cursor, db_name):
            log.info(f"Database '{db_name}' already exists, reusing it")
            cursor.close()
            conn.close()
            return False
        
        # Create database
        log.info(f"Creating database '{db_name}'...")
        cursor.execute(
            sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name))
        )
        log.info(f"Database '{db_name}' created successfully")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        log.error(f"Error creating database: {e}")
        raise
    except Exception as e:
        log.error(f"Unexpected error creating database: {e}")
        raise


def check_table_exists(cursor, table_name: str) -> bool:
    """
    Check if table exists in current database.
    
    Args:
        cursor: PostgreSQL cursor
        table_name: Table name to check
    
    Returns:
        True if table exists, False otherwise
    """
    cursor.execute(
        """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = %s
        )
        """,
        (table_name,)
    )
    return cursor.fetchone()[0]


def execute_schema_file(cursor, schema_file_path: str):
    """
    Execute SQL schema file.
    
    Args:
        cursor: PostgreSQL cursor
        schema_file_path: Path to schema SQL file
    """
    try:
        with open(schema_file_path, 'r') as f:
            schema_sql = f.read()
        
        # Execute the schema
        cursor.execute(schema_sql)
        log.info(f"Schema from '{schema_file_path}' executed successfully")
        
    except FileNotFoundError:
        log.error(f"Schema file not found: {schema_file_path}")
        raise
    except psycopg2.Error as e:
        log.error(f"Error executing schema: {e}")
        raise


def create_tables(db_name: str) -> bool:
    """
    Create tables if they don't exist.
    
    Args:
        db_name: Database name
    
    Returns:
        True if tables were created, False if they already existed
    """
    try:
        # Connect to the specific database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=db_name
        )
        cursor = conn.cursor()
        
        # Check if main tables exist
        tables_to_check = [
            'rag_query_logs',
            'rag_error_logs',
            'rag_evaluation_metrics',
            'rag_component_latency',
            'rag_cache_stats',
            'rag_system_health'
        ]
        
        existing_tables = []
        missing_tables = []
        
        for table in tables_to_check:
            if check_table_exists(cursor, table):
                existing_tables.append(table)
            else:
                missing_tables.append(table)
        
        if not missing_tables:
            log.info(f"All tables already exist in database '{db_name}'")
            cursor.close()
            conn.close()
            return False
        
        log.info(f"Creating missing tables: {missing_tables}")
        
        # Get schema file path
        schema_file = Path(__file__).parent / "schema.sql"
        
        # Execute schema file (it's idempotent with CREATE TABLE IF NOT EXISTS)
        execute_schema_file(cursor, str(schema_file))
        
        # Commit changes
        conn.commit()
        
        log.info(f"Tables created successfully in database '{db_name}'")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        log.error(f"Error creating tables: {e}")
        if conn:
            conn.rollback()
        raise
    except Exception as e:
        log.error(f"Unexpected error creating tables: {e}")
        if conn:
            conn.rollback()
        raise


def verify_database_setup(db_name: str, silent: bool = False) -> dict:
    """
    Verify database and tables are properly set up.
    
    Args:
        db_name: Database name
        silent: If True, skip logging to reduce noise (useful for health checks)
    
    Returns:
        Dictionary with verification results
    """
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=db_name
        )
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        # Check views
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        views = [row[0] for row in cursor.fetchall()]
        
        # Check functions
        cursor.execute("""
            SELECT routine_name 
            FROM information_schema.routines 
            WHERE routine_schema = 'public' 
            AND routine_type = 'FUNCTION'
            ORDER BY routine_name
        """)
        functions = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        result = {
            "database": db_name,
            "tables": tables,
            "views": views,
            "functions": functions,
            "status": "healthy"
        }
        
        if not silent:
            log.info(f"Database verification complete", 
                     tables_count=len(tables),
                     views_count=len(views),
                     functions_count=len(functions))
        
        return result
        
    except psycopg2.Error as e:
        if not silent:
            log.error(f"Error verifying database: {e}")
        return {
            "database": db_name,
            "status": "error",
            "error": str(e)
        }


def initialize_database(
    db_name: Optional[str] = None,
    force_recreate: bool = False
) -> dict:
    """
    Initialize database with idempotent operations.
    
    This function:
    1. Checks if database exists, creates if missing
    2. Checks if tables exist, creates if missing
    3. Verifies setup
    
    Args:
        db_name: Database name (defaults to env variable)
        force_recreate: If True, drop and recreate database (USE WITH CAUTION)
    
    Returns:
        Dictionary with initialization results
    """
    db_name = db_name or DB_NAME
    
    log.info(f"Initializing database '{db_name}'...")
    log.info(f"Connection: {DB_USER}@{DB_HOST}:{DB_PORT}")
    
    try:
        # Step 1: Handle force recreate if requested
        if force_recreate:
            log.warning(f"Force recreate requested - dropping database '{db_name}'")
            try:
                conn = psycopg2.connect(
                    host=DB_HOST,
                    port=DB_PORT,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    database="postgres"
                )
                conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                cursor = conn.cursor()
                
                # Terminate existing connections
                cursor.execute(f"""
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = '{db_name}'
                    AND pid <> pg_backend_pid()
                """)
                
                # Drop database
                cursor.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(
                    sql.Identifier(db_name)
                ))
                log.info(f"Database '{db_name}' dropped")
                
                cursor.close()
                conn.close()
            except Exception as e:
                log.error(f"Error dropping database: {e}")
        
        # Step 2: Create database if it doesn't exist
        db_created = create_database(db_name)
        
        # Step 3: Create tables if they don't exist
        tables_created = create_tables(db_name)
        
        # Step 4: Verify setup
        verification = verify_database_setup(db_name)
        
        # Step 5: Return results
        result = {
            "success": True,
            "database_created": db_created,
            "tables_created": tables_created,
            "verification": verification,
            "message": "Database initialized successfully"
        }
        
        log.info(f"Database initialization complete", 
                 db_created=db_created,
                 tables_created=tables_created)
        
        return result
        
    except Exception as e:
        log.error(f"Database initialization failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Database initialization failed"
        }


def get_database_stats(db_name: Optional[str] = None) -> dict:
    """
    Get database statistics.
    
    Args:
        db_name: Database name
    
    Returns:
        Dictionary with database statistics
    """
    db_name = db_name or DB_NAME
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=db_name
        )
        cursor = conn.cursor()
        
        stats = {}
        
        # Query logs count
        cursor.execute("SELECT COUNT(*) FROM rag_query_logs")
        stats['query_logs_count'] = cursor.fetchone()[0]
        
        # Error logs count
        cursor.execute("SELECT COUNT(*) FROM rag_error_logs")
        stats['error_logs_count'] = cursor.fetchone()[0]
        
        # Evaluation metrics count
        cursor.execute("SELECT COUNT(*) FROM rag_evaluation_metrics")
        stats['evaluation_metrics_count'] = cursor.fetchone()[0]
        
        # Recent queries (last 24 hours)
        cursor.execute("""
            SELECT COUNT(*) FROM rag_query_logs 
            WHERE timestamp > NOW() - INTERVAL '24 hours'
        """)
        stats['queries_last_24h'] = cursor.fetchone()[0]
        
        # Average latency (last 24 hours)
        cursor.execute("""
            SELECT AVG(total_latency) FROM rag_query_logs 
            WHERE timestamp > NOW() - INTERVAL '24 hours'
        """)
        result = cursor.fetchone()[0]
        stats['avg_latency_24h'] = float(result) if result else 0.0
        
        # Database size
        cursor.execute(f"""
            SELECT pg_size_pretty(pg_database_size('{db_name}'))
        """)
        stats['database_size'] = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return stats
        
    except Exception as e:
        log.error(f"Error getting database stats: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    # Initialize database when run directly
    result = initialize_database()
    
    if result['success']:
        print("✅ Database initialized successfully")
        print(f"   Database: {DB_NAME}")
        print(f"   Tables: {len(result['verification']['tables'])}")
        print(f"   Views: {len(result['verification']['views'])}")
        print(f"   Functions: {len(result['verification']['functions'])}")
        
        # Get stats
        stats = get_database_stats()
        print(f"\n📊 Database Statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
    else:
        print(f"❌ Database initialization failed: {result.get('error')}")
