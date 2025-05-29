import aioredis
import json
from typing import Optional, Any
from app.config import settings

class CacheService:
    def __init__(self):
        self.redis_client = None
    
    async def _get_redis_client(self):
        """Get Redis client with lazy initialization"""
        if self.redis_client is None:
            self.redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
        return self.redis_client
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            redis = await self._get_redis_client()
            value = await redis.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache with TTL"""
        try:
            redis = await self._get_redis_client()
            ttl = ttl or settings.cache_ttl
            serialized_value = json.dumps(value, default=str)
            return await redis.setex(key, ttl, serialized_value)
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            redis = await self._get_redis_client()
            return bool(await redis.delete(key))
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            redis = await self._get_redis_client()
            return bool(await redis.exists(key))
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False

cache_service = CacheService()
