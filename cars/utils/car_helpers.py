"""Helper functions for car-related creation and updates."""

from typing import Dict, Any, Optional, List, Set

from django.db import transaction
from rest_framework import serializers

from cars.models import Car, Brand, Performance, FuelType, Engine, Tag, TagCategory
from cars.utils.tag_helpers import create_or_update_car_tags
from cars.utils.data_cleaners import CarData


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
        _handle_brand(brand_name, instance, data)
        car = _create_or_update_car_instance(data, instance)
        _handle_fuel_types(car, fuel_type_data)
        _handle_performance(car, performance_data)
        return car
    except Exception as e:
        raise Exception(
            f'Failed to {"update" if instance else "create"} car: {str(e)}'
        ) from e


def create_car(data: CarData) -> Optional[Car]:
    """Create a car and its related objects in the database.

    Args:
        data: CarData object containing cleaned car data

    Returns:
        Created Car object or None if creation failed
    """
    try:
        car_data = {
            "name": data.name,
            "brand": data.brand_name,
            "seats": data.seats,
            "price_min": data.price_data[0],
            "price_max": data.price_data[1],
            "performance": data.performance_data,
            "fuel_type": _create_fuel_types(data.fuel_codes),
        }

        car = create_or_update_car(car_data)
        _create_engines(car, data.engine_data)
        create_or_update_car_tags(car)
        return car

    except Exception as e:
        raise Exception(f'Failed to create car "{data.name}": {str(e)}') from e


def _get_value_at_index(lst: Optional[list], index: int) -> Any:
    """Get value at index, with special handling for empty lists and out of range indices.

    Args:
        lst: List of values or None
        index: Desired index

    Returns:
        Value at index, first value if index is 1 and out of range,
        last value for other out of range indices, or None if list is empty or None
    """
    if not lst:
        return None
    try:
        return lst[index]
    except IndexError:
        return lst[0] if index == 1 else lst[-1]


def _create_fuel_types(fuel_codes: List[str]) -> List[FuelType]:
    """Create or get FuelType objects for given codes.

    Args:
        fuel_codes: List of fuel type codes (P, D, E, etc.)

    Returns:
        List of FuelType objects
    """
    fuel_types = []
    for code in fuel_codes:
        try:
            fuel_type, _ = FuelType.objects.get_or_create(fuel_type=code)
            fuel_types.append(fuel_type)
        except Exception as e:
            raise Exception(f'Failed to create fuel type "{code}": {str(e)}') from e
    return fuel_types


def _create_engines(car: Car, engine_data: Dict[str, Any]) -> None:
    """Create Engine objects for a car.

    Args:
        car: Car object to associate engines with
        engine_data: Dictionary containing engine specifications
    """
    try:
        # Get maximum number of engines from non-None lists
        valid_lists = [values for values in engine_data.values() if values is not None]
        if not valid_lists:
            Engine.objects.create(car=car)
            return

        num_engines = max(len(values) for values in valid_lists)

        # Create engines
        for i in range(num_engines):
            config = _get_value_at_index(engine_data["configs"], i)
            Engine.objects.create(
                car=car,
                cylinder_layout=config.cylinder_layout if config else None,
                cylinder_count=config.cylinder_count if config else None,
                aspiration=config.aspiration if config else None,
                engine_capacity=_get_value_at_index(
                    engine_data["engine_capacities"], i
                ),
                battery_capacity=_get_value_at_index(
                    engine_data["battery_capacities"], i
                ),
                horsepower=_get_value_at_index(engine_data["horsepowers"], i),
                torque=_get_value_at_index(engine_data["torques"], i),
            )
    except Exception as e:
        raise Exception(f"Failed to create engines for car {car.name}: {str(e)}") from e


def _handle_brand(
    brand_name: Optional[str], instance: Optional[Car], data: Dict[str, Any]
) -> None:
    """Handle brand creation/update logic.

    Args:
        brand_name: Name of the brand
        instance: Existing Car instance if updating
        data: Dictionary containing car data
    """
    if brand_name and not instance:
        brand = get_or_create_brand(brand_name)
        data["brand"] = brand


def _create_or_update_car_instance(
    data: Dict[str, Any], instance: Optional[Car] = None
) -> Car:
    """Create new or update existing car instance.

    Args:
        data: Dictionary containing car data
        instance: Existing Car instance if updating

    Returns:
        Created or updated Car instance
    """
    if instance:
        for attr, value in data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    return Car.objects.create(**data)


def _handle_fuel_types(car: Car, fuel_type_data: Optional[list]) -> None:
    """Handle fuel types for a car.

    Args:
        car: Car instance
        fuel_type_data: List of fuel types
    """
    if fuel_type_data is not None:
        car.fuel_type.set(fuel_type_data)


def _handle_performance(car: Car, performance_data: Optional[Dict[str, Any]]) -> None:
    """Handle performance data for a car.

    Args:
        car: Car instance
        performance_data: Dictionary containing performance data
    """
    if not performance_data:
        return

    if car.performance:
        for attr, value in performance_data.items():
            setattr(car.performance, attr, value)
        car.performance.save()
    else:
        performance = Performance.objects.create(**performance_data)
        car.performance = performance
        car.save()
