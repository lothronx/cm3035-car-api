"""Helper functions for car creation and updates."""

from typing import Dict, Any, Optional, List

from django.db import transaction
from rest_framework import serializers

from cars.models import Car, Brand, Performance, FuelType
from cars.utils.tag_helpers import create_or_update_car_tags


def get_or_create_brand(name: str) -> Brand:
    """Get or create a brand by name.

    Args:
        name: Brand name

    Returns:
        Brand instance

    Raises:
        serializers.ValidationError: If name is empty or None
    """
    if not name or not name.strip():
        raise serializers.ValidationError("Brand name is required")
    return Brand.objects.get_or_create(name=name.strip())[0]


@transaction.atomic
def create_or_update_car(
    data: Dict[str, Any],
    instance: Optional[Car] = None,
) -> Car:
    """Create or update a car and its related objects.

    Args:
        data: Dictionary containing car data
        instance: Existing Car instance if updating, None if creating new

    Returns:
        Created or updated Car object
    """
    fuel_type_data = data.pop("fuel_type", None)
    performance_data = data.pop("performance", None)
    brand_name = data.pop("brand", None) if isinstance(data.get("brand"), str) else None

    try:
        # Handle brand
        if brand_name and not instance:
            brand = get_or_create_brand(brand_name)
            data["brand"] = brand

        # Create or update car
        if instance:
            for attr, value in data.items():
                setattr(instance, attr, value)
            car = instance
            car.save()
        else:
            car = Car.objects.create(**data)

        # Handle fuel types
        if fuel_type_data is not None:
            car.fuel_type.set(fuel_type_data)

        # Handle performance
        if performance_data:
            if instance and instance.performance:
                for attr, value in performance_data.items():
                    setattr(instance.performance, attr, value)
                instance.performance.save()
            else:
                performance = Performance.objects.create(**performance_data)
                car.performance = performance
                car.save()

        return car
    except Exception as e:
        raise Exception(
            f'Failed to {"update" if instance else "create"} car: {str(e)}'
        ) from e
