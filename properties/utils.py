import logging
from django.core.cache import cache
from django_redis import get_redis_connection

from .models import Property

logger = logging.getLogger(__name__)


# pylint: disable=no-member
# pylint: disable=broad-exception-caught
def get_all_properties():
    """
    Retrieves all properties from cache or database.

    This function implements a caching strategy using Django's low-level cache API:
    1. First checks if 'all_properties' exists in Redis cache
    2. If found, returns the cached queryset (cache hit)
    3. If not found, fetches from database and caches for 1 hour (cache miss)

    Cache Duration: 3600 seconds (1 hour)
    Cache Key: 'all_properties'

    Returns:
        QuerySet: All Property objects
    """
    # Define the cache key
    cache_key = "all_properties"

    # Try to get the data from cache
    properties = cache.get(cache_key)

    if properties is not None:
        # Cache hit - data found in Redis
        print(f"Cache HIT: Retrieved {len(properties)} properties from Redis")
        return properties

    # Cache miss - data not in cache, fetch from database
    print("Cache MISS: Fetching properties from database")
    properties = list(
        Property.objects.all().values(
            "id",
            "title",
            "description",
            "price",
            "location",
            "created_at",
        )
    )

    # Store the queryset in Redis cache for 1 hour (3600 seconds)
    cache.set(cache_key, properties, 3600)
    print(f"Cached {len(properties)} properties in Redis for 1 hour")

    return properties


def get_redis_cache_metrics():
    """
    Retrieve and analyze Redis cache hit/miss metrics.

    This function connects to Redis through django-redis and retrieves
    performance metrics including cache hits, misses, and hit ratio.

    Returns:
        dict: Dictionary containing:
            - keyspace_hits (int): Total number of successful key lookups
            - keyspace_misses (int): Total number of failed key lookups
            - hit_ratio (float): Percentage of successful lookups (0-100)
            - total_requests (int): Total cache requests (hits + misses)
            - status (str): Success or error status

    Example:
        >>> metrics = get_redis_cache_metrics()
        >>> print(f"Hit Ratio: {metrics['hit_ratio']:.2f}%")
    """
    try:
        # Get the Redis client from django-redis

        redis_client = get_redis_connection("default")

        # Get Redis INFO statistics
        redis_info = redis_client.info("stats")

        # Extract keyspace metrics
        keyspace_hits = redis_info.get("keyspace_hits", 0)
        keyspace_misses = redis_info.get("keyspace_misses", 0)
        total_requests = keyspace_hits + keyspace_misses

        # Calculate hit ratio (avoid division by zero)
        if total_requests > 0:
            hit_ratio = (keyspace_hits / total_requests) * 100
        else:
            hit_ratio = 0.0

        # Prepare metrics dictionary
        metrics = {
            "keyspace_hits": keyspace_hits,
            "keyspace_misses": keyspace_misses,
            "total_requests": total_requests,
            "hit_ratio": round(hit_ratio, 2),
            "status": "success",
        }

        # Log the metrics
        logger.info(
            "Redis Cache Metrics - Hits: %s, Misses: %s, Hit Ratio: %.2f%%, Total Requests: %s",
            keyspace_hits,
            keyspace_misses,
            hit_ratio,
            total_requests,
        )

        # Print metrics for visibility
        print("\n" + "=" * 60)
        print("Redis Cache Metrics")
        print("=" * 60)
        print(f"Keyspace Hits:     {keyspace_hits:,}")
        print(f"Keyspace Misses:   {keyspace_misses:,}")
        print(f"Total Requests:    {total_requests:,}")
        print(f"Hit Ratio:         {hit_ratio:.2f}%")
        print("=" * 60 + "\n")

        return metrics

    except ImportError as e:
        error_msg = "django-redis is not properly installed or configured"
        logger.error("%s : %s", error_msg, e)
        return {
            "status": "error",
            "error": error_msg,
            "keyspace_hits": 0,
            "keyspace_misses": 0,
            "total_requests": 0,
            "hit_ratio": 0.0,
        }

    except Exception as e:
        error_msg = f"Failed to retrieve Redis cache metrics: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "error": error_msg,
            "keyspace_hits": 0,
            "keyspace_misses": 0,
            "total_requests": 0,
            "hit_ratio": 0.0,
        }
