"""
Redis caching layer for RAG system.
Caches retrieval results and generated responses to reduce latency and cost.
"""

import json
import hashlib
from typing import Optional, Any
from langchain_core.documents import Document

from src.utils.logger import get_logger

log = get_logger(__name__)

# Redis is optional - gracefully degrade if not available
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    log.warning("Redis not installed. Caching will be disabled. Install with: pip install redis")


class RedisCache:
    """
    Redis-based caching for RAG pipeline.
    
    Caches:
    1. Retrieval results (query -> documents)
    2. Generated responses (query + context -> answer)
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        ttl: int = 3600,
        enabled: bool = True
    ):
        self.host = host
        self.port = port
        self.db = db
        self.ttl = ttl  # Time to live in seconds
        self.enabled = enabled and REDIS_AVAILABLE
        self._client = None

        if not REDIS_AVAILABLE and enabled:
            log.warning("Redis caching requested but redis package not available")

    def _get_client(self):
        """Lazy-load Redis client."""
        if not self.enabled:
            return None

        if self._client is None:
            try:
                self._client = redis.Redis(
                    host=self.host,
                    port=self.port,
                    db=self.db,
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2
                )
                # Test connection
                self._client.ping()
                log.info("Redis cache connected", host=self.host, port=self.port)
            except Exception as e:
                log.error("Failed to connect to Redis", error=str(e))
                self.enabled = False
                self._client = None

        return self._client

    def _make_key(self, prefix: str, *args) -> str:
        """
        Generate a cache key from arguments.

        Args:
            prefix: Key prefix (e.g., "retrieval", "response").
            *args: Values to hash into the key.

        Returns:
            Cache key string.
        """
        # Combine all args into a single string
        combined = "|".join(str(arg) for arg in args)
        
        # Hash for consistent key length
        hash_obj = hashlib.sha256(combined.encode())
        key_hash = hash_obj.hexdigest()[:16]
        
        return f"rag:{prefix}:{key_hash}"

    def get_retrieval(self, query: str, retrieval_config: dict) -> Optional[list[Document]]:
        """
        Get cached retrieval results.

        Args:
            query: The search query.
            retrieval_config: Configuration dict (top_k, use_hybrid, etc.).

        Returns:
            List of Documents if cached, None otherwise.
        """
        if not self.enabled:
            return None

        client = self._get_client()
        if client is None:
            return None

        try:
            config_str = json.dumps(retrieval_config, sort_keys=True)
            key = self._make_key("retrieval", query, config_str)
            
            cached = client.get(key)
            if cached:
                data = json.loads(cached)
                documents = [
                    Document(
                        page_content=doc["page_content"],
                        metadata=doc["metadata"]
                    )
                    for doc in data
                ]
                log.info("Retrieval cache hit", query=query[:50])
                return documents
            
            log.debug("Retrieval cache miss", query=query[:50])
            return None
            
        except Exception as e:
            log.error("Retrieval cache get failed", error=str(e))
            return None

    def set_retrieval(
        self,
        query: str,
        retrieval_config: dict,
        documents: list[Document]
    ) -> bool:
        """
        Cache retrieval results.

        Args:
            query: The search query.
            retrieval_config: Configuration dict.
            documents: Retrieved documents to cache.

        Returns:
            True if cached successfully, False otherwise.
        """
        if not self.enabled:
            return False

        client = self._get_client()
        if client is None:
            return False

        try:
            config_str = json.dumps(retrieval_config, sort_keys=True)
            key = self._make_key("retrieval", query, config_str)
            
            # Serialize documents
            data = [
                {
                    "page_content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in documents
            ]
            
            client.setex(key, self.ttl, json.dumps(data))
            log.info("Retrieval cached", query=query[:50], doc_count=len(documents))
            return True
            
        except Exception as e:
            log.error("Retrieval cache set failed", error=str(e))
            return False

    def get_response(
        self,
        query: str,
        context_hash: str,
        generation_config: dict
    ) -> Optional[dict]:
        """
        Get cached generated response.

        Args:
            query: The user's question.
            context_hash: Hash of the context used.
            generation_config: Generation configuration.

        Returns:
            Response dict if cached, None otherwise.
        """
        if not self.enabled:
            return None

        client = self._get_client()
        if client is None:
            return None

        try:
            config_str = json.dumps(generation_config, sort_keys=True)
            key = self._make_key("response", query, context_hash, config_str)
            
            cached = client.get(key)
            if cached:
                response = json.loads(cached)
                log.info("Response cache hit", query=query[:50])
                return response
            
            log.debug("Response cache miss", query=query[:50])
            return None
            
        except Exception as e:
            log.error("Response cache get failed", error=str(e))
            return None

    def set_response(
        self,
        query: str,
        context_hash: str,
        generation_config: dict,
        response: dict
    ) -> bool:
        """
        Cache generated response.

        Args:
            query: The user's question.
            context_hash: Hash of the context used.
            generation_config: Generation configuration.
            response: Response dict to cache.

        Returns:
            True if cached successfully, False otherwise.
        """
        if not self.enabled:
            return False

        client = self._get_client()
        if client is None:
            return False

        try:
            config_str = json.dumps(generation_config, sort_keys=True)
            key = self._make_key("response", query, context_hash, config_str)
            
            client.setex(key, self.ttl, json.dumps(response))
            log.info("Response cached", query=query[:50])
            return True
            
        except Exception as e:
            log.error("Response cache set failed", error=str(e))
            return False

    def clear_all(self) -> bool:
        """
        Clear all RAG-related cache entries.

        Returns:
            True if successful, False otherwise.
        """
        if not self.enabled:
            return False

        client = self._get_client()
        if client is None:
            return False

        try:
            # Find all keys with our prefix
            keys = client.keys("rag:*")
            if keys:
                client.delete(*keys)
                log.info("Cache cleared", keys_deleted=len(keys))
            else:
                log.info("Cache already empty")
            return True
            
        except Exception as e:
            log.error("Cache clear failed", error=str(e))
            return False

    def get_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats.
        """
        if not self.enabled:
            return {"enabled": False}

        client = self._get_client()
        if client is None:
            return {"enabled": False, "connected": False}

        try:
            info = client.info("stats")
            keys = client.keys("rag:*")
            
            return {
                "enabled": True,
                "connected": True,
                "total_rag_keys": len(keys),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": (
                    info.get("keyspace_hits", 0) / 
                    max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1)
                )
            }
        except Exception as e:
            log.error("Failed to get cache stats", error=str(e))
            return {"enabled": True, "connected": False, "error": str(e)}


# Global cache instance
_cache_instance = None


def get_cache(
    host: str = "localhost",
    port: int = 6379,
    enabled: bool = True
) -> RedisCache:
    """
    Get or create the global cache instance.

    Args:
        host: Redis host.
        port: Redis port.
        enabled: Whether caching is enabled.

    Returns:
        RedisCache instance.
    """
    global _cache_instance
    
    if _cache_instance is None:
        _cache_instance = RedisCache(host=host, port=port, enabled=enabled)
    
    return _cache_instance
