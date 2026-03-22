"""
PostgreSQL Client - Backwards Compatibility Layer

This module now redirects to the Supabase client.
All database operations are handled through Supabase SDK.
"""

# Re-export from supabase_client for backwards compatibility
from .supabase_client import SupabaseClient as PostgresClient
from .supabase_client import DatabaseError
from .supabase_client import get_client

__all__ = ['PostgresClient', 'DatabaseError', 'get_client']
