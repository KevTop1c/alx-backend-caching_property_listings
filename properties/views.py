"""Custom Views"""

from django.views.decorators.cache import cache_page
from django.http import JsonResponse
from .models import Property
from .utils import get_all_properties, get_redis_cache_metrics


# pylint: disable=no-member
# pylint: disable=unused-argument
@cache_page(60 * 15)  # Cache for 15 minutes (900 seconds)
def property_list(request):
    """
    Returns a list of all properties in JSON format.
    Response is cached in Redis for 15 minutes.
    """
    properties = Property.objects.all().values(
        "id",
        "title",
        "description",
        "price",
        "location",
        "created_at",
    )

    # Get properties using the cached utility function
    properties = get_all_properties()

    return JsonResponse(
        {
            "status": "success",
            "count": len(properties),
            "data": properties,
            "cache_info": "Data cached in Redis for 1 hour via get_all_properties()",
        },
        safe=False,
    )


def cache_metrics(request):
    """
    Returns Redis cache hit/miss metrics in JSON format.

    This endpoint provides real-time cache performance statistics including:
    - keyspace_hits: Total number of successful cache lookups
    - keyspace_misses: Total number of failed cache lookups
    - hit_ratio: Percentage of successful lookups
    - total_requests: Total cache requests

    Example response:
    {
        "status": "success",
        "keyspace_hits": 1250,
        "keyspace_misses": 350,
        "total_requests": 1600,
        "hit_ratio": 78.13
    }
    """
    metrics = get_redis_cache_metrics()
    return JsonResponse(metrics)
