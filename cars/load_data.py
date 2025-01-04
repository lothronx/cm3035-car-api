"""
Load and store car data from CSV files into the database.
"""

import csv
import os
from typing import Dict, Any, Optional, List

from django.db import transaction
from django.utils.text import slugify

from cars.models import Brand, Car, Engine, Performance, FuelType
from cars.data_cleaners import (
    clean_top_speed,
    clean_acceleration,
    clean_price,
    clean_fuel_type,
    clean_power_values,
    clean_capacity,
    parse_engine,
    _get_value_at_index,
)


def create_performance(performance_data: Dict[str, Any]) -> Optional[Performance]:
    """Create a Performance object from cleaned data.

    Args:
        performance_data: Dictionary containing top_speed and acceleration values

    Returns:
        Performance object or None if data is invalid
    """
    if not performance_data.get("top_speed") or not all(
        performance_data.get("acceleration")
    ):
        return None

    return Performance.objects.create(
        top_speed=performance_data["top_speed"],
        acceleration_min=performance_data["acceleration"][0],
        acceleration_max=performance_data["acceleration"][1],
    )


def create_fuel_types(fuel_codes: List[str]) -> List[FuelType]:
    """Create or get FuelType objects for given codes.

    Args:
        fuel_codes: List of fuel type codes (P, D, E, etc.)

    Returns:
        List of FuelType objects
    """
    return [FuelType.objects.get_or_create(fuel_type=code)[0] for code in fuel_codes]


def create_engines(car: Car, engine_data: Dict[str, Any]) -> None:
    """Create Engine objects for a car.

    Args:
        car: Car object to associate engines with
        engine_data: Dictionary containing engine specifications
    """
    # Get maximum number of engines from data
    num_engines = max(len(values) for values in engine_data.values())

    # Create engines
    for i in range(num_engines):
        config = _get_value_at_index(engine_data["configs"], i)
        Engine.objects.create(
            car=car,
            cylinder_layout=config[0],
            cylinder_count=config[1],
            aspiration=config[2],
            engine_capacity=_get_value_at_index(engine_data["engine_capacities"], i),
            battery_capacity=_get_value_at_index(engine_data["battery_capacities"], i),
            horsepower=_get_value_at_index(engine_data["horsepowers"], i),
            torque=_get_value_at_index(engine_data["torques"], i),
        )


@transaction.atomic
def load_data(csv_file_path: str) -> None:
    """Load car data from CSV and store in database.

    Args:
        csv_file_path: Path to CSV file containing car data
    """
    with open(csv_file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            # Create or get brand
            brand = Brand.objects.get_or_create(
                name=row["Company Names"].strip().title()
            )[0]

            # Clean and prepare performance data
            performance_data = {
                "top_speed": clean_top_speed(row["Total Speed"]),
                "acceleration": clean_acceleration(row["Performance(0 - 100 )KM/H"]),
            }
            performance = create_performance(performance_data)

            # Clean and prepare price data
            price_min, price_max = clean_price(row["Cars Prices"])

            # Add fuel types
            fuel_types = create_fuel_types(clean_fuel_type(row["Fuel Types"]))

            # Create car
            car = Car.objects.create(
                name=row["Cars Names"].strip(),
                slug=slugify(row["Cars Names"].strip()),
                brand=brand,
                performance=performance,
                seats=row["Seats"].strip(),
                price_min=price_min,
                price_max=price_max,
            )
            car.fuel_type.set(fuel_types)

            # Clean and prepare engine data
            engine_data = {
                "configs": parse_engine(row["Engines"]),
                "engine_capacities": clean_capacity(row["CC/Battery Capacity"])[0],
                "battery_capacities": clean_capacity(row["CC/Battery Capacity"])[1],
                "horsepowers": clean_power_values(row["HorsePower"]),
                "torques": row["Torque"],
            }
            create_engines(car, engine_data)
