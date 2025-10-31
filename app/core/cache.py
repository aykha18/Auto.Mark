"""
Redis cache configuration and management
"""

import redis.asyncio as redis
from typing import Optional, Any
import json
import structlog

from app.core.config import get_settings

settings = get_settings()
logger = structlog.get_logger(__name__)

# Global Redis connection
redis_client: Optional[redis.Redis] = None


async def setup_redis():
    """Setup Redis connection"""
    global redis_client
    
    try:
        redis_client = redis.from_url(
            settings.redis.url,
            db=settings.redis.db,
            password=settings.redis.password,
            decode_responses=True
        )
        
        # Test connection
        await redis_client.ping()
        logger.info("Redis connection established")
        
    except Exception as e:
        logger.error("Failed to connect to Redis", error=str(e))
        redis_client = None


async def get_redis() -> Optional[redis.Redis]:
    """Get Redis client"""
    return redis_client


async def cache_set(key: str, value: Any, expire: int = 3600):
    """Set cache value"""
    if not redis_client:
        return False
    
    try:
        serialized_value = json.dumps(value) if not isinstance(value, str) else value
        await redis_client.setex(key, expire, serialized_value)
        return True
    except Exception as e:
        logger.error("Cache set failed", key=key, error=str(e))
        return False


async def cache_get(key: str) -> Optional[Any]:
    """Get cache value"""
    if not redis_client:
        return None
    
    try:
        value = await redis_client.get(key)
        if value is None:
            return None
        
        # Try to deserialize JSON
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    except Exception as e:
        logger.error("Cache get failed", key=key, error=str(e))
        return None


async def cache_delete(key: str) -> bool:
    """Delete cache value"""
    if not redis_client:
        return False
    
    try:
        await redis_client.delete(key)
        return True
    except Exception as e:
        logger.error("Cache delete failed", key=key, error=str(e))
        return False
