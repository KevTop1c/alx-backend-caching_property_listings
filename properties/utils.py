from django.core.cache import cache
from .models import Property


# pylint: disable=no-member
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
