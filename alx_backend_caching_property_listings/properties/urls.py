"""Custom endpoints"""

from django.urls import path
from . import views

urlpatterns = [
    path("", views.PropertyListView.as_view(), name="property-list"),
]
