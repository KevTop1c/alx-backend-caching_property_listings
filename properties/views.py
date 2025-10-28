"""Custom Views"""

from django.views.decorators.cache import cache_page
from django.http import JsonResponse
from .models import Property
from .utils import get_all_properties


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

    return JsonResponse({
            "status": "success",
            "count": len(properties),
            "data": properties,
            "cache_info": "Data cached in Redis for 1 hour via get_all_properties()",
    }, safe=False)
