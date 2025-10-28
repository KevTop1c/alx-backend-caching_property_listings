"""
Signal handlers for automatic cache invalidation.

These signals ensure that the 'all_properties' cache is automatically
cleared whenever a Property instance is created, updated, or deleted,
maintaining data consistency between the cache and database.
"""

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Property

logger = logging.getLogger(__name__)


# pylint: disable=unused-argument
@receiver(post_save, sender=Property)
def invalidate_property_cache_on_save(sender, instance, created, **kwargs):
    """
    Invalidate the all_properties cache when a Property is created or updated.

    Args:
        sender: The model class (Property)
        instance: The actual Property instance being saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    cache_key = "all_properties"
    cache.delete(cache_key)

    action = "created" if created else "updated"
    logger.info(
        "Property '%s' was %s. Cache '%s' invalidated.",
        action,
        instance.title,
        cache_key,
    )
    print(f"✓ Cache invalidated: Property '{instance.title}' was {action}")


@receiver(post_delete, sender=Property)
def invalidate_property_cache_on_delete(sender, instance, **kwargs):
    """
    Invalidate the all_properties cache when a Property is deleted.

    Args:
        sender: The model class (Property)
        instance: The actual Property instance being deleted
        **kwargs: Additional keyword arguments
    """
    cache_key = "all_properties"
    cache.delete(cache_key)

    logger.info(
        "Property '%s' was deleted. Cache '%s' invalidated.", instance.title, cache_key
    )
    print(f"✓ Cache invalidated: Property '{instance.title}' was deleted")
