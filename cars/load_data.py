"""
Import car data from CSV files into the database,
including data cleaning and validation.
"""

import csv
import os
from typing import Dict, Any, Optional, List, Set

from django.db import transaction

from cars.utils.tag_helpers import create_or_update_car_tags
from cars.utils.data_cleaners import (
    get_value_at_index,
    clean_car_data,
    CarData,
)
from cars.utils.car_helpers import create_or_update_car
from .models import (
    Car,
    Brand,
    Performance,
    FuelType,
    Engine,
    Tag,
    TagCategory,
)


def _create_performance(performance_data: Dict[str, Any]) -> Optional[Performance]:
    """Create a Performance object from cleaned data.

    Args:
        performance_data: Dictionary containing top_speed and acceleration values

    Returns:
        Performance object
    """
    try:
        return Performance.objects.create(
            top_speed=performance_data["top_speed"],
            acceleration_min=performance_data["acceleration"][0],
            acceleration_max=performance_data["acceleration"][1],
        )
    except Exception as e:
        raise Exception(f"Failed to create performance record: {str(e)}") from e


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
            config = get_value_at_index(engine_data["configs"], i)
            Engine.objects.create(
                car=car,
                cylinder_layout=config.cylinder_layout if config else None,
                cylinder_count=config.cylinder_count if config else None,
                aspiration=config.aspiration if config else None,
                engine_capacity=get_value_at_index(engine_data["engine_capacities"], i),
                battery_capacity=get_value_at_index(
                    engine_data["battery_capacities"], i
                ),
                horsepower=get_value_at_index(engine_data["horsepowers"], i),
                torque=get_value_at_index(engine_data["torques"], i),
            )
    except Exception as e:
        raise Exception(f"Failed to create engines for car {car.name}: {str(e)}") from e


def _create_car(data: CarData) -> Optional[Car]:
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


def _clean_all_tables():
    """Delete all records from all tables in the correct order to handle dependencies."""
    Tag.objects.all().delete()
    TagCategory.objects.all().delete()
    Engine.objects.all().delete()
    Car.objects.all().delete()
    Performance.objects.all().delete()
    FuelType.objects.all().delete()
    Brand.objects.all().delete()


@transaction.atomic
def load_data(csv_file_path: str) -> None:
    """Load car data from CSV and store in database.

    Args:
        csv_file_path: Path to CSV file containing car data
    """
    # Clean all existing data first
    _clean_all_tables()

    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"CSV file not found: {csv_file_path}")

    with open(csv_file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        processed_cars: Set[str] = set()

        for row in reader:
            car_identifier = f"{row['Company Names'].strip().lower()} {row['Cars Names'].strip().lower()}"

            if car_identifier in processed_cars:  # to avoid duplicates
                continue

            try:
                car_data = clean_car_data(row)
                _create_car(car_data)
                processed_cars.add(car_identifier)
            except Exception as e:
                raise Exception(f"Failed to process car data: {str(e)}") from e
