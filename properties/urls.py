"""Custom endpoints"""

from django.urls import path
from . import views

urlpatterns = [
    path("", views.property_list, name="property-list"),
    path("metrics/", views.cache_metrics, name="property-list"),
]
