"""
Caching system with Redis and in-memory fallback.
"""
import json
import time
import hashlib
from typing import Any, Optional, Union, Dict
from datetime import datetime, timedelta
import logging

from config.settings import settings

logger = logging.getLogger(__name__)

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, using in-memory cache only")


class CacheManager:
    """Unified caching interface with Redis and in-memory fallback."""
    
    def __init__(self):
        self.redis_client = None
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = settings.performance.cache_ttl
        self.max_memory_cache_size = settings.performance.max_cache_size
        
        # Initialize Redis if available and configured
        if REDIS_AVAILABLE and settings.redis.url:
            try:
                self.redis_client = redis.from_url(
                    settings.redis.url,
                    max_connections=settings.redis.max_connections,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                # Test connection
                self.redis_client.ping()
                logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}, falling back to memory cache")
                self.redis_client = None
    
    def _make_key(self, key: str) -> str:
        """Create a prefixed cache key."""
        return f"{settings.redis.key_prefix}:{key}"
    
    def _serialize_value(self, value: Any) -> str:
        """Serialize value for storage."""
        return json.dumps({
            "data": value,
            "timestamp": time.time(),
            "type": type(value).__name__
        })
    
    def _deserialize_value(self, serialized: str) -> Any:
        """Deserialize value from storage."""
        try:
            data = json.loads(serialized)
            return data["data"]
        except (json.JSONDecodeError, KeyError):
            return None
    
    def _is_expired(self, timestamp: float, ttl: int) -> bool:
        """Check if cached item is expired."""
        return time.time() - timestamp > ttl
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in cache with optional TTL."""
        if ttl is None:
            ttl = self.default_ttl
        
        cache_key = self._make_key(key)
        serialized = self._serialize_value(value)
        
        # Try Redis first
        if self.redis_client:
            try:
                self.redis_client.setex(cache_key, ttl, serialized)
                logger.debug(f"Cached key '{key}' in Redis with TTL {ttl}s")
                return True
            except Exception as e:
                logger.warning(f"Redis set failed for key '{key}': {e}")
        
        # Fallback to memory cache
        self._cleanup_memory_cache()
        self.memory_cache[cache_key] = {
            "value": serialized,
            "expires_at": time.time() + ttl
        }
        logger.debug(f"Cached key '{key}' in memory with TTL {ttl}s")
        return True
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        cache_key = self._make_key(key)
        
        # Try Redis first
        if self.redis_client:
            try:
                value = self.redis_client.get(cache_key)
                if value:
                    logger.debug(f"Cache hit for key '{key}' in Redis")
                    return self._deserialize_value(value)
            except Exception as e:
                logger.warning(f"Redis get failed for key '{key}': {e}")
        
        # Try memory cache
        if cache_key in self.memory_cache:
            cached_item = self.memory_cache[cache_key]
            if time.time() < cached_item["expires_at"]:
                logger.debug(f"Cache hit for key '{key}' in memory")
                return self._deserialize_value(cached_item["value"])
            else:
                # Remove expired item
                del self.memory_cache[cache_key]
        
        logger.debug(f"Cache miss for key '{key}'")
        return None
    
    def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        cache_key = self._make_key(key)
        deleted = False
        
        # Delete from Redis
        if self.redis_client:
            try:
                deleted = self.redis_client.delete(cache_key) > 0
            except Exception as e:
                logger.warning(f"Redis delete failed for key '{key}': {e}")
        
        # Delete from memory cache
        if cache_key in self.memory_cache:
            del self.memory_cache[cache_key]
            deleted = True
        
        if deleted:
            logger.debug(f"Deleted key '{key}' from cache")
        
        return deleted
    
    def clear(self) -> bool:
        """Clear all cache entries."""
        success = True
        
        # Clear Redis (only our keys)
        if self.redis_client:
            try:
                pattern = f"{settings.redis.key_prefix}:*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
                logger.info(f"Cleared {len(keys)} keys from Redis")
            except Exception as e:
                logger.warning(f"Redis clear failed: {e}")
                success = False
        
        # Clear memory cache
        self.memory_cache.clear()
        logger.info("Cleared memory cache")
        
        return success
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {
            "backend": "redis" if self.redis_client else "memory",
            "memory_cache_size": len(self.memory_cache),
            "max_memory_cache_size": self.max_memory_cache_size,
            "default_ttl": self.default_ttl
        }
        
        if self.redis_client:
            try:
                info = self.redis_client.info()
                stats["redis"] = {
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory": info.get("used_memory", 0),
                    "used_memory_human": info.get("used_memory_human", "0B"),
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0)
                }
                
                # Calculate hit ratio
                hits = stats["redis"]["keyspace_hits"]
                misses = stats["redis"]["keyspace_misses"]
                total = hits + misses
                stats["redis"]["hit_ratio"] = hits / total if total > 0 else 0
                
            except Exception as e:
                stats["redis_error"] = str(e)
        
        return stats
    
    def _cleanup_memory_cache(self):
        """Clean up expired entries and enforce size limits."""
        now = time.time()
        
        # Remove expired entries
        expired_keys = [
            key for key, item in self.memory_cache.items()
            if now >= item["expires_at"]
        ]
        for key in expired_keys:
            del self.memory_cache[key]
        
        # Enforce size limit (LRU-style by removing oldest)
        if len(self.memory_cache) >= self.max_memory_cache_size:
            # Sort by expiration time and remove the ones expiring soonest
            sorted_items = sorted(
                self.memory_cache.items(),
                key=lambda x: x[1]["expires_at"]
            )
            
            # Remove 10% of items to make room
            remove_count = max(1, int(self.max_memory_cache_size * 0.1))
            for key, _ in sorted_items[:remove_count]:
                del self.memory_cache[key]


def cache_result(key_func: Optional[callable] = None, ttl: Optional[int] = None):
    """Decorator for caching function results."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                key_parts = [func.__name__]
                if args:
                    key_parts.extend(str(arg) for arg in args)
                if kwargs:
                    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = hashlib.md5("|".join(key_parts).encode()).hexdigest()
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            return result
        
        # Preserve function metadata
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    
    return decorator


async def async_cache_result(key_func: Optional[callable] = None, ttl: Optional[int] = None):
    """Async decorator for caching function results."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                key_parts = [func.__name__]
                if args:
                    key_parts.extend(str(arg) for arg in args)
                if kwargs:
                    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = hashlib.md5("|".join(key_parts).encode()).hexdigest()
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            return result
        
        # Preserve function metadata
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    
    return decorator


# Global cache manager instance
cache_manager = CacheManager()