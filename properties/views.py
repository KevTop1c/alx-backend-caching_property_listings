"""Custom Views"""

from django.views.decorators.cache import cache_page
from django.http import JsonResponse
from .models import Property


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

    # Convert queryset to list for JSON serialization
    properties_list = list(properties)

    return JsonResponse(
        {
            "status": "success",
            "count": len(properties_list),
            "data": properties_list,
        },
    )
