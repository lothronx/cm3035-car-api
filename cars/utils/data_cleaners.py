"""
Data cleaning utilities for processing car data from CSV files.
Each function handles cleaning a specific type of data field.
"""

import re
from typing import Optional, Tuple, List, Any, Dict, Set
from dataclasses import dataclass


# Type aliases for better readability
PowerValue = Optional[List[int]]
PriceRange = Tuple[Optional[int], Optional[int]]
AccelerationRange = Tuple[Optional[float], Optional[float]]
CapacityRange = Tuple[Optional[List[int]], Optional[List[int]]]


@dataclass
class EngineConfig:
    """Represents an engine configuration with its components."""

    cylinder_layout: Optional[str]  # I, V, F, W, R
    cylinder_count: Optional[int]  # Number of cylinders
    aspiration: Optional[str]  # N, T, S, W, Q


@dataclass
class CarData:
    """Represents a car's data."""

    name: str
    brand_name: str
    performance_data: Dict[str, Any]
    price_data: PriceRange
    fuel_codes: List[str]
    seats: str
    engine_data: Dict[str, Any]


def clean_car_data(row: Dict[str, str]) -> CarData:
    """Clean and prepare car data from a CSV row.

    Args:
        row: Dictionary containing raw car data from CSV

    Returns:
        CarData object containing cleaned data
    """
    acceleration = _clean_acceleration(row["Performance(0 - 100 )KM/H"])
    performance_data = {
        "top_speed": _clean_top_speed(row["Total Speed"]),
        "acceleration_min": acceleration[0],
        "acceleration_max": acceleration[1],
    }

    engine_data = {
        "configs": _parse_engine(row["Engines"]),
        "engine_capacities": _clean_capacity(row["CC/Battery Capacity"])[0],
        "battery_capacities": _clean_capacity(row["CC/Battery Capacity"])[1],
        "horsepowers": _clean_power_values(row["HorsePower"]),
        "torques": _clean_power_values(row["Torque"]),
    }

    return CarData(
        name=row["Cars Names"].strip(),
        brand_name=row["Company Names"].strip().title(),
        performance_data=performance_data,
        price_data=_clean_price(row["Cars Prices"]),
        fuel_codes=_clean_fuel_type(row["Fuel Types"]),
        seats=row["Seats"].strip(),
        engine_data=engine_data,
    )





def _parse_number_with_commas(value_str: str) -> int:
    """Convert a number string with optional thousands separators to an integer.

    Args:
        value_str: String containing a number with optional commas (e.g., "1,234")

    Returns:
        Integer value
    """
    return int(value_str.replace(",", ""))


def _clean_top_speed(speed_str: str) -> Optional[int]:
    """Extract top speed value from string.

    Args:
        speed_str: String containing speed information

    Returns:
        Integer speed value or None if no valid speed found
    """
    if not speed_str:
        return None

    SPEED_PATTERN = r"\d+"  # number
    numbers = re.findall(SPEED_PATTERN, speed_str)
    return int(numbers[0]) if numbers else None


def _clean_acceleration(acceleration_str: str) -> AccelerationRange:
    """Extract min and max acceleration values from string.

    Args:
        acceleration_str: String containing acceleration information

    Returns:
        Tuple of (min_acceleration, max_acceleration) in seconds
    """
    if not acceleration_str:
        return (None, None)

    DECIMAL_NUMBER_PATTERN = r"\d+\.\d+"  # decimal number
    normalized_str = acceleration_str.replace(" ", "")
    numbers = re.findall(DECIMAL_NUMBER_PATTERN, normalized_str)

    if not numbers:
        return (None, None)

    accelerations = [float(num) for num in numbers]
    return (min(accelerations), max(accelerations))


def _clean_price(price_str: str) -> PriceRange:
    """Extract min and max price values from string.

    Args:
        price_str: String containing price information

    Returns:
        Tuple of (min_price, max_price) in dollars
    """
    if not price_str:
        return (None, None)

    PRICE_PATTERN = r"\$?\s*(\d{1,3}(?:,\d{3})*|\d+)"  # e.g., $1,000,000 or 100
    numbers = re.findall(PRICE_PATTERN, price_str)

    if not numbers:
        return (None, None)

    prices = [_parse_number_with_commas(num) for num in numbers]
    return (min(prices), max(prices))


def _clean_fuel_type(fuel_type_str: str) -> List[str]:
    """Map fuel type strings to standard codes.

    Args:
        fuel_type_str: String containing fuel type information. Supports formats like:
            - "Petrol, Diesel"
            - "Hybrid (Petrol)"
            - "CNG/Petrol"
            - "Electric"

    Returns:
        List of fuel type codes sorted alphabetically:
            - P: Petrol
            - D: Diesel
            - E: Electric
            - H: Hydrogen
            - C: CNG
            - X: Hybrid
    """
    FUEL_TYPE_MAPPING: Dict[str, str] = {
        "petrol": "P",
        "diesel": "D",
        "electric": "E",
        "ev": "E",
        "hydrogen": "H",
        "cng": "C",
        "hybrid": "X",
    }

    if not fuel_type_str:
        return []

    fuel_types: Set[str] = set()

    normalized_str = re.sub(r"[/,()]", " ", fuel_type_str.lower())
    parts = normalized_str.split()

    for part in parts:
        if part in FUEL_TYPE_MAPPING:
            fuel_types.add(FUEL_TYPE_MAPPING[part])

    return sorted(list(fuel_types))


def _clean_power_values(value_str: str) -> PowerValue:
    """Extract numeric values from horsepower or torque strings.

    Args:
        value_str: String containing power values

    Returns:
        List of integer values or None if no valid values found
    """
    if not value_str:
        return None

    NUMBER_PATTERN = r"\d+"  # number
    normalized_str = value_str.replace(",", "")
    numbers = re.findall(NUMBER_PATTERN, normalized_str)
    return [int(num) for num in numbers] if numbers else None


def _clean_capacity(capacity_str: str) -> CapacityRange:
    """Extract engine and battery capacity values.

    Args:
        capacity_str: String containing capacity information

    Returns:
        Tuple of (engine_capacities, battery_capacities) in cc and kWh
    """
    if not capacity_str:
        return (None, None)

    engine_capacities: Set[int] = set()
    battery_capacities: Set[int] = set()
    normalized_str = capacity_str.lower()

    RANGE_PATTERN = r"(\d+(?:,\d{3})*)\s*-\s*(\d+(?:,\d{3})*)\s*(cc|kwh)"
    SINGLE_PATTERN = r"(\d+(?:,\d{3})*)\s*(cc|kwh)"

    # Handle ranges like "1,000-2,000cc" or "50-75kWh"
    for match in re.finditer(RANGE_PATTERN, normalized_str):
        start = _parse_number_with_commas(match.group(1))
        end = _parse_number_with_commas(match.group(2))
        unit = match.group(3)

        if unit == "cc":
            engine_capacities.update([start, end])
        else:
            battery_capacities.update([start, end])

    # Handle single values like "2,000cc" or "75kWh"
    for match in re.finditer(SINGLE_PATTERN, normalized_str):
        value = _parse_number_with_commas(match.group(1))
        unit = match.group(2)

        if unit == "cc":
            engine_capacities.add(value)
        else:
            battery_capacities.add(value)

    return (
        sorted(list(engine_capacities)) if engine_capacities else None,
        sorted(list(battery_capacities)) if battery_capacities else None,
    )


def _extract_cylinder_count(engine: str) -> Optional[int]:
    """Extract the number of cylinders from an engine description.

    Args:
        engine: Engine description string (e.g., "4-CYLINDER", "V8", "INLINE-6")

    Returns:
        Number of cylinders as an integer, or None if not found
    """
    CYLINDER_COUNT_PATTERN = (
        r"(\d+)[-\s]?CYLINDER|\b[IVFWR](\d+)\b"  # e.g., 4-CYLINDER or V8
    )
    count_match = re.search(CYLINDER_COUNT_PATTERN, engine)
    if count_match:
        return int(count_match.group(1) or count_match.group(2))
    return None


def _extract_cylinder_layout(engine: str) -> Optional[str]:
    """Extract the cylinder layout configuration from an engine description.

    Args:
        engine: Engine description string (e.g., "INLINE-4", "V8", "FLAT-6")

    Returns:
        Single letter code for the layout:
        - I: Inline/Straight
        - V: V-configuration
        - F: Flat/Boxer
        - W: W-configuration
        - R: Rotary/Wankel
        Returns None if layout not found
    """
    CYLINDER_LAYOUT_MAPPING = {
        "INLINE": "I",
        "STRAIGHT": "I",
        "V": "V",
        "FLAT": "F",
        "BOXER": "F",
        "W": "W",
        "ROTARY": "R",
        "WANKEL": "R",
    }
    for layout, abbrev in CYLINDER_LAYOUT_MAPPING.items():
        CYLINDER_LAYOUT_PATTERN = (
            rf"\b{layout}(?:[-\s]\d+)?\b|\b{abbrev}(?:\d+)?\b"  # e.g., INLINE-4 or V8
        )
        if re.search(CYLINDER_LAYOUT_PATTERN, engine):
            return abbrev
    return None


def _extract_aspiration(engine: str) -> Optional[str]:
    """Extract the engine aspiration type from an engine description.

    Args:
        engine: Engine description string (e.g., "TWIN TURBO", "NATURALLY ASPIRATED")

    Returns:
        Single letter code for the aspiration:
        - N: Naturally Aspirated
        - Q: Quad Turbo
        - W: Twin Turbo
        - T: Single Turbo
        - S: Supercharged
        Returns None if aspiration not found
    """
    ASPIRATION_MAPPING = {
        "NATURALLY ASPIRATED": "N",
        "QUAD TURBO": "Q",
        "QUAD-TURBO": "Q",
        "TWIN TURBO": "W",
        "TWIN-TURBO": "W",
        "TURBO": "T",
        "SUPERCHARGED": "S",
    }
    for asp, abbrev in ASPIRATION_MAPPING.items():
        if asp in engine:
            return abbrev
    return None


def _parse_engine(engine_str: str) -> List[EngineConfig]:
    """Parse engine configuration strings into structured data.

    Args:
        engine_str: String containing engine configuration information

    Returns:
        List of EngineConfig objects containing cylinder layout, count, and aspiration
    """
    if not engine_str:
        return None

    engine_configs: List[EngineConfig] = []

    engines = re.split(r"\s*/\s*|\s+OR\s+", engine_str.upper())  # Split by "OR" or "/"

    for engine in engines:
        cylinder_layout = _extract_cylinder_layout(engine)
        cylinder_count = _extract_cylinder_count(engine)
        aspiration = _extract_aspiration(engine)

        if cylinder_count or cylinder_layout or aspiration:
            engine_configs.append(
                EngineConfig(cylinder_layout, cylinder_count, aspiration)
            )

    if not engine_configs:
        return None

    return engine_configs
