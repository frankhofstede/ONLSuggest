"""
Redis client for caching and session management.
"""
import redis
from app.core.config import settings


def get_redis() -> redis.Redis:
    """
    Create and return a Redis client instance.

    Returns:
        redis.Redis: Configured Redis client with decode_responses=True
    """
    # Parse Redis URL (format: redis://localhost:6379/0)
    return redis.from_url(
        settings.redis_url,
        decode_responses=True  # Auto-decode bytes to strings
    )


# Global Redis client instance
redis_client = get_redis()
