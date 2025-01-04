"""
Data cleaning utilities for processing car data from CSV files.
Each function handles cleaning a specific type of data field.
"""

import re
from typing import Optional, Tuple, List, Any


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


def clean_top_speed(speed_str: str) -> Optional[int]:
    """Extract top speed value from string.

    Args:
        speed_str: String containing speed information

    Returns:
        Integer speed value or None if no valid speed found
    """
    if not speed_str:
        return None
    numbers = re.findall(r"\d+", speed_str)
    return int(numbers[0]) if numbers else None


def clean_acceleration(
    acceleration_str: str,
) -> Tuple[Optional[float], Optional[float]]:
    """Extract min and max acceleration values from string.

    Args:
        acceleration_str: String containing acceleration information

    Returns:
        Tuple of (min_acceleration, max_acceleration) in seconds
    """
    if not acceleration_str:
        return (None, None)

    acceleration_str = acceleration_str.replace(" ", "")
    numbers = re.findall(r"\d+\.\d+", acceleration_str)
    if not numbers:
        return (None, None)

    accelerations = [float(num) for num in numbers]
    return (min(accelerations), max(accelerations))


def clean_price(price_str: str) -> Tuple[Optional[int], Optional[int]]:
    """Extract min and max price values from string.

    Args:
        price_str: String containing price information

    Returns:
        Tuple of (min_price, max_price) in dollars
    """
    if not price_str:
        return (None, None)

    numbers = re.findall(r"\$?(\d+)", price_str.replace(",", ""))
    if not numbers:
        return (None, None)

    prices = [int(num) for num in numbers]
    return (min(prices), max(prices))


def clean_fuel_type(fuel_type_str: str) -> List[str]:
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
    FUEL_TYPE_MAPPING = {
        "petrol": "P",
        "diesel": "D",
        "electric": "E",
        "ev": "E",
        "hydrogen": "H",
        "cng": "C",
        "hybrid": "X",
    }

    if not fuel_type_str:
        return None

    # First replace separators and parentheses with spaces, then find all words
    # This handles formats like "CNG/Petrol", "Petrol, Diesel", "Hybrid (Petrol)"
    fuel_types = set()
    parts = re.findall(
        r"\b\w+(?:\(\w+\))?\b", re.sub(r"[/,()]", " ", fuel_type_str.lower())
    )

    for part in parts:
        if part in FUEL_TYPE_MAPPING:
            fuel_types.add(FUEL_TYPE_MAPPING[part])

    return sorted(list(fuel_types))


def clean_power_values(value_str: str) -> Optional[List[int]]:
    """Extract numeric values from horsepower or torque strings.

    Args:
        value_str: String containing power values

    Returns:
        List of integer values or None if no valid values found
    """
    if not value_str:
        return None

    numbers = re.findall(r"\d+", value_str.replace(",", ""))
    return [int(num) for num in numbers] if numbers else None


def clean_capacity(capacity_str: str) -> Tuple[Optional[List[int]], Optional[List[int]]]:
    """Extract engine and battery capacity values.

    Args:
        capacity_str: String containing capacity information

    Returns:
        Tuple of (engine_capacities, battery_capacities) in cc and kWh
    """
    if not capacity_str:
        return (None, None)

    engine_capacities = set()
    battery_capacities = set()

    capacity_str = capacity_str.lower()

    # Handle ranges like "1,000-2,000cc" or "50-75kWh"
    range_pattern = r"(\d+(?:,\d{3})*)\s*-\s*(\d+(?:,\d{3})*)\s*(?:cc|kwh)"
    for match in re.finditer(range_pattern, capacity_str):
        start = int(match.group(1).replace(",", ""))
        end = int(match.group(2).replace(",", ""))
        if "cc" in match.group():
            engine_capacities.update([start, end])
        else:
            battery_capacities.update([start, end])

    # Handle single values like "2,000cc" or "75kWh"
    single_pattern = r"(\d+(?:,\d{3})*)\s*(?:cc|kwh)"
    for match in re.finditer(single_pattern, capacity_str):
        value = int(match.group(1).replace(",", ""))
        if "cc" in match.group():
            engine_capacities.add(value)
        else:
            battery_capacities.add(value)

    return (sorted(list(engine_capacities)), sorted(list(battery_capacities)))


def parse_engine(
    engine_str: str,
) -> List[Tuple[Optional[str], Optional[int], Optional[str]]]:
    """Parse engine configuration strings into structured data.

    Args:
        engine_str: String containing engine configuration information

    Returns:
        List of tuples (cylinder_layout, cylinder_count, aspiration)
        where cylinder_layout is one of: I, V, F, W, R
        and aspiration is one of: N, T, S, W, Q
    """
    if not engine_str:
        return []

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

    ASPIRATION_MAPPING = {
        "NATURALLY ASPIRATED": "N",
        "QUAD TURBO": "Q",
        "QUAD-TURBO": "Q",
        "TWIN TURBO": "W",
        "TWIN-TURBO": "W",
        "TURBO": "T",
        "SUPERCHARGED": "S",
    }

    engine_list = []
    engines = re.split(r"\s*/\s*|\s+OR\s+", engine_str.upper())

    for engine in engines:
        cylinder_layout = None
        cylinder_count = None
        aspiration = None

        # Extract cylinder count
        count_match = re.search(r"(\d+)[-\s]?CYLINDER|\b[IVFWR](\d+)\b", engine)
        if count_match:
            cylinder_count = int(count_match.group(1) or count_match.group(2))

        # Extract cylinder layout
        for layout, abbrev in CYLINDER_LAYOUT_MAPPING.items():
            if re.search(rf"\b{layout}(?:\d+|-\d+)?\b|\b{abbrev}(?:\d+)?\b", engine):
                cylinder_layout = abbrev
                break

        # Extract aspiration
        for asp, abbrev in ASPIRATION_MAPPING.items():
            if asp in engine:
                aspiration = abbrev
                break

        if cylinder_count or cylinder_layout or aspiration:
            engine_list.append((cylinder_layout, cylinder_count, aspiration))

    return engine_list
