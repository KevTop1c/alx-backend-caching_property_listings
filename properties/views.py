"""Custom Views"""

from django.views.generic import ListView
from django.core.cache import cache
from .models import Property

# pylint: disable=no-member
class PropertyListView(ListView):
    """Property List view"""

    model = Property
    template_name = "properties/property_list.html"
    context_object_name = "properties"

    def get_queryset(self):
        # Use cache
        cached_properties = cache.get("all_properties")
        if cached_properties is not None:
            return cached_properties

        qs = Property.objects.all()
        cache.set("all_properties", qs, timeout=60 * 15)  # 15 minutes
        return qs
