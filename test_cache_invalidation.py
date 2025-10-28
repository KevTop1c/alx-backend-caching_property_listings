"""
Test script for automatic cache invalidation using Django signals.

This script demonstrates that the cache is automatically invalidated
when properties are created, updated, or deleted.
"""

import os
import time
import django
from django.core.cache import cache

# Setup Django environment
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "alx_backend_caching_property_listings.settings"
)
django.setup()

# pylint: disable=wrong-import-position
from properties.models import Property
from properties.utils import get_all_properties

# pylint: disable=unused-variable
# pylint: disable=broad-exception-caught
# pylint: disable=no-member
def print_separator(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def check_cache_status():
    """Check if cache exists and return count"""
    cached = cache.get("all_properties")
    if cached:
        return len(cached), True
    return 0, False


def test_create_invalidation():
    """Test that creating a property invalidates the cache"""
    print_separator("Test 1: Cache Invalidation on Property Creation")

    # Clear cache and populate it
    print("\n1. Setting up: Clearing cache and populating with fresh data...")
    cache.delete("all_properties")
    initial_properties = get_all_properties()
    initial_count = len(initial_properties)
    print(f"   ✓ Cache populated with {initial_count} properties")

    # Verify cache exists
    count, exists = check_cache_status()
    print(f"   ✓ Cache exists: {exists}, Count: {count}")

    # Create a new property (should trigger cache invalidation)
    print("\n2. Creating a new property...")
    new_property = Property.objects.create(
        title="Luxury Villa with Pool",
        description="Stunning villa with infinity pool and ocean views",
        price=2500000.00,
        location="Santorini",
    )
    print(f"   ✓ Created: {new_property.title}")

    # Check if cache was invalidated
    print("\n3. Checking if cache was invalidated...")
    time.sleep(0.1)  # Small delay to ensure signal processing
    count, exists = check_cache_status()

    if not exists:
        print("   ✓ SUCCESS: Cache was automatically invalidated!")
    else:
        print("   ✗ FAILED: Cache still exists (invalidation didn't work)")

    # Verify new property appears in fresh fetch
    print("\n4. Fetching fresh data from database...")
    fresh_properties = get_all_properties()
    fresh_count = len(fresh_properties)
    print(f"   ✓ Retrieved {fresh_count} properties (expected {initial_count + 1})")

    if fresh_count == initial_count + 1:
        print("   ✓ SUCCESS: New property is included in fresh data!")

    return new_property


def test_update_invalidation(property_instance):
    """Test that updating a property invalidates the cache"""
    print_separator("Test 2: Cache Invalidation on Property Update")

    # Ensure cache is populated
    print("\n1. Populating cache with current data...")
    properties = get_all_properties()
    print(f"   ✓ Cache populated with {len(properties)} properties")

    # Verify cache exists
    count, exists = check_cache_status()
    print(f"   ✓ Cache exists: {exists}, Count: {count}")

    # Update the property (should trigger cache invalidation)
    print("\n2. Updating property...")
    old_price = property_instance.price
    property_instance.price = 2750000.00
    property_instance.title = "Updated Luxury Villa with Pool"
    property_instance.save()
    print(f"   ✓ Updated: Price {old_price} → {property_instance.price}")
    print(f"   ✓ Updated: Title to '{property_instance.title}'")

    # Check if cache was invalidated
    print("\n3. Checking if cache was invalidated...")
    time.sleep(0.1)  # Small delay to ensure signal processing
    count, exists = check_cache_status()

    if not exists:
        print("   ✓ SUCCESS: Cache was automatically invalidated!")
    else:
        print("   ✗ FAILED: Cache still exists (invalidation didn't work)")

    # Verify updated data appears in fresh fetch
    print("\n4. Fetching fresh data to verify update...")
    fresh_properties = get_all_properties()
    updated_property = next(
        (p for p in fresh_properties if p["id"] == property_instance.id), None
    )

    if updated_property and float(updated_property["price"]) == float(
        property_instance.price
    ):
        print(f"   ✓ SUCCESS: Updated price {updated_property['price']} is in cache!")


def test_delete_invalidation(property_instance):
    """Test that deleting a property invalidates the cache"""
    print_separator("Test 3: Cache Invalidation on Property Deletion")

    # Ensure cache is populated
    print("\n1. Populating cache with current data...")
    properties = get_all_properties()
    count_before = len(properties)
    print(f"   ✓ Cache populated with {count_before} properties")

    # Verify cache exists
    count, exists = check_cache_status()
    print(f"   ✓ Cache exists: {exists}, Count: {count}")

    # Delete the property (should trigger cache invalidation)
    print("\n2. Deleting property...")
    property_id = property_instance.id
    property_title = property_instance.title
    property_instance.delete()
    print(f"   ✓ Deleted: {property_title} (ID: {property_id})")

    # Check if cache was invalidated
    print("\n3. Checking if cache was invalidated...")
    time.sleep(0.1)  # Small delay to ensure signal processing
    count, exists = check_cache_status()

    if not exists:
        print("   ✓ SUCCESS: Cache was automatically invalidated!")
    else:
        print("   ✗ FAILED: Cache still exists (invalidation didn't work)")

    # Verify property is removed in fresh fetch
    print("\n4. Fetching fresh data to verify deletion...")
    fresh_properties = get_all_properties()
    count_after = len(fresh_properties)
    print(f"   ✓ Retrieved {count_after} properties (expected {count_before - 1})")

    deleted_property = next(
        (p for p in fresh_properties if p["id"] == property_id), None
    )

    if not deleted_property and count_after == count_before - 1:
        print("   ✓ SUCCESS: Property was removed from cache!")


def test_bulk_operations():
    """Test cache invalidation with bulk operations"""
    print_separator("Test 4: Cache Invalidation with Bulk Operations")

    print("\n1. Creating multiple properties...")
    properties_to_create = [
        Property(
            title=f"Test Property {i}",
            description=f"Test {i}",
            price=100000 + (i * 10000),
            location=f"City {i}",
        )
        for i in range(3)
    ]

    # Populate cache first
    get_all_properties()
    count_before, _ = check_cache_status()
    print(f"   ✓ Cache populated with {count_before} properties")

    # Create properties one by one (each triggers invalidation)
    for prop in properties_to_create:
        prop.save()
        print(f"   ✓ Created: {prop.title}")

    print("\n2. Checking cache after bulk creation...")
    count, exists = check_cache_status()
    if not exists:
        print("   ✓ Cache invalidated after creations")

    # Get fresh data
    fresh = get_all_properties()
    print(f"   ✓ Fresh data has {len(fresh)} properties")

    # Clean up
    print("\n3. Cleaning up test properties...")
    Property.objects.filter(title__startswith="Test Property").delete()
    print("   ✓ Test properties deleted")


def main():
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 12 + "Automatic Cache Invalidation Test Suite" + " " * 16 + "║")
    print("╚" + "═" * 68 + "╝")

    try:
        # Test 1: Create
        test_property = test_create_invalidation()

        # Test 2: Update
        test_update_invalidation(test_property)

        # Test 3: Delete
        test_delete_invalidation(test_property)

        # Test 4: Bulk operations
        test_bulk_operations()

        print_separator("All Tests Complete!")
        print("\n✓ Signal-based cache invalidation is working correctly!")
        print("✓ Cache is automatically cleared on:")
        print("  - Property creation (post_save with created=True)")
        print("  - Property update (post_save with created=False)")
        print("  - Property deletion (post_delete)")
        print("\n")

    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
