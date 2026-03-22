"""
Database Initializer for Supabase
Verifies that required tables exist in Supabase and provides health checks.

Tables must be created in Supabase SQL Editor using the migration file:
  database/supabase_migration.sql
"""

from typing import Optional

from src.utils.logger import get_logger

log = get_logger(__name__)


def verify_database_setup(db_name: str = "supabase", silent: bool = False) -> dict:
    """
    Verify Supabase database tables are properly set up.

    Args:
        db_name: Database identifier (for compatibility)
        silent: If True, skip logging to reduce noise (useful for health checks)

    Returns:
        Dictionary with verification results
    """
    try:
        from .supabase_client import get_client

        client = get_client()
        health = client.health_check()

        if health.get("connected"):
            # Try to check each expected table
            expected_tables = [
                "rag_query_logs",
                "rag_error_logs",
                "rag_evaluation_metrics",
                "rag_component_latency",
                "rag_cache_stats",
                "rag_system_health",
            ]

            verified_tables = []
            missing_tables = []

            for table in expected_tables:
                try:
                    client.client.table(table).select("id").limit(1).execute()
                    verified_tables.append(table)
                except Exception as table_err:
                    # PGRST205 = table not found in schema cache (table doesn't exist)
                    if "PGRST205" in str(table_err):
                        missing_tables.append(table)
                    else:
                        # Other errors (permissions etc.) — assume table exists but has issues
                        missing_tables.append(table)

            result = {
                "database": "supabase",
                "tables": verified_tables,
                "missing_tables": missing_tables,
                "status": "healthy" if not missing_tables else "partial",
            }

            if missing_tables and not silent:
                log.warning(
                    "Some tables are missing in Supabase. "
                    "Run the SQL in database/supabase_migration.sql in your Supabase SQL Editor.",
                    missing=missing_tables,
                )

            if not silent:
                log.info(
                    "Database verification complete",
                    tables_count=len(verified_tables),
                    missing_count=len(missing_tables),
                )

            return result

        else:
            if not silent:
                log.error("Supabase connection unhealthy", error=health.get("error"))
            return {
                "database": "supabase",
                "status": "error",
                "error": health.get("error", "Connection failed"),
            }

    except Exception as e:
        if not silent:
            log.error(f"Error verifying database: {e}")
        return {
            "database": "supabase",
            "status": "error",
            "error": str(e),
        }


def initialize_database(
    db_name: Optional[str] = None,
    force_recreate: bool = False
) -> dict:
    """
    Initialize / verify Supabase database setup.

    Unlike the previous PostgreSQL approach, tables are created via
    Supabase SQL Editor or migrations. This function verifies the setup.

    Args:
        db_name: Database name (ignored, kept for API compatibility)
        force_recreate: Not supported with Supabase (ignored)

    Returns:
        Dictionary with initialization results
    """
    log.info("Verifying Supabase database setup...")

    try:
        verification = verify_database_setup(silent=False)

        if verification.get("status") == "error":
            return {
                "success": False,
                "error": verification.get("error", "Unknown error"),
                "message": "Supabase connection failed. Check SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.",
            }

        missing = verification.get("missing_tables", [])

        if missing:
            return {
                "success": True,
                "database_created": False,
                "tables_created": False,
                "verification": verification,
                "message": (
                    f"Supabase connected but {len(missing)} tables are missing: {missing}. "
                    "Run database/supabase_migration.sql in Supabase SQL Editor."
                ),
            }

        result = {
            "success": True,
            "database_created": False,
            "tables_created": False,
            "verification": verification,
            "message": "Supabase database verified successfully",
        }

        log.info("Supabase database verification complete")
        return result

    except Exception as e:
        log.error(f"Database initialization failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Database initialization failed",
        }


def get_database_stats(db_name: Optional[str] = None) -> dict:
    """
    Get database statistics from Supabase.

    Args:
        db_name: Ignored (kept for compatibility)

    Returns:
        Dictionary with database statistics
    """
    try:
        from .supabase_client import get_client

        client = get_client()
        stats = {}

        # Query logs count
        result = client.client.table("rag_query_logs").select("id", count="exact").execute()
        stats["query_logs_count"] = result.count if result.count is not None else 0

        # Error logs count
        result = client.client.table("rag_error_logs").select("id", count="exact").execute()
        stats["error_logs_count"] = result.count if result.count is not None else 0

        # Evaluation metrics count
        result = client.client.table("rag_evaluation_metrics").select("id", count="exact").execute()
        stats["evaluation_metrics_count"] = result.count if result.count is not None else 0

        stats["provider"] = "supabase"

        return stats

    except Exception as e:
        log.error(f"Error getting database stats: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    # Verify database when run directly
    result = initialize_database()

    if result["success"]:
        print("Database verification complete")
        verification = result.get("verification", {})
        print(f"  Provider: Supabase")
        print(f"  Tables found: {len(verification.get('tables', []))}")
        missing = verification.get("missing_tables", [])
        if missing:
            print(f"  Missing tables: {missing}")
            print(f"  Run database/supabase_migration.sql in Supabase SQL Editor")

        # Get stats
        stats = get_database_stats()
        print(f"\nDatabase Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    else:
        print(f"Database verification failed: {result.get('error')}")
