from functools import wraps
from typing import Any, Callable
import json
from datetime import datetime, timedelta
from cachetools import TTLCache
from app.core.config import settings

# Initialize cache with TTL (time-to-live)
cache = TTLCache(maxsize=100, ttl=settings.CACHE_TTL)

def cache_key_builder(*args, **kwargs) -> str:
    """Build a cache key from function arguments"""
    key_parts = [str(arg) for arg in args]
    key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
    return ":".join(key_parts)

def cache_response(ttl: int = None):
    """Cache decorator for API responses"""
    def decorator(func: Callable) -> Callable:
        if not settings.CACHE_ENABLED:
            return func

        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Build cache key
            cache_key = f"{func.__name__}:{cache_key_builder(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return json.loads(cached_result)
            
            # Get fresh result
            result = await func(*args, **kwargs)
            
            # Store in cache
            cache[cache_key] = json.dumps(result)
            return result
            
        return wrapper
    return decorator

def invalidate_cache(pattern: str = None):
    """Invalidate cache entries matching the pattern"""
    if pattern:
        keys_to_remove = [k for k in cache.keys() if pattern in k]
        for k in keys_to_remove:
            cache.pop(k, None)
    else:
        cache.clear()