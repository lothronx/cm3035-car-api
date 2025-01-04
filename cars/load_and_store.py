import csv
import re
import os
import sys
from decimal import Decimal
import django
from django.utils.text import slugify
from django.db import transaction
from cars.models import Brand, Car, Engine, Performance, Fuel_Type


def clean_top_speed(speed_str) -> int:
    # Find the numeric part of the string
    numbers = re.findall(r"\d+", speed_str)
    # Convert to integer if there is a number, otherwise return None
    return int(numbers[0]) if numbers else None


def clean_acceleration(acceleration_str) -> tuple[float, float]:
    # Find all decimal numbers in the string
    numbers = re.findall(r"\d+\.\d+", acceleration_str)

    # Return None for invalid accelerations like "N/A"
    if not numbers:
        return (None, None)

    # Convert found numbers to floats
    accelerations = (float(num) for num in numbers)

    # Return tuple of (min_acceleration, max_acceleration)
    return (min(accelerations), max(accelerations))


def clean_price(price_str) -> tuple[int, int]:
    numbers = re.findall(r"\$?(\d+)", price_str.replace(",", ""))
    if not numbers:
        return (None, None)
    prices = (int(num) for num in numbers)
    # Return tuple of (min_price, max_price)
    return (min(prices), max(prices))


def clean_fuel_type(fuel_type_str) -> list[str]:
    # Map common fuel types to their abbreviations
    FUEL_TYPE_MAPPING = {
        "petrol": "P",
        "diesel": "D",
        "electric": "E",
        "ev": "E",
        "hydrogen": "H",
        "cng": "C",
        "hybrid": "X",
    }

    # Initialize set to hold unique fuel types
    fuel_types = set()

    # Split the string into individual parts
    parts = re.findall(r"\w+", fuel_type_str.lower())

    # Check each part against our mapping
    for part in parts:
        if part in FUEL_TYPE_MAPPING:
            fuel_types.add(FUEL_TYPE_MAPPING[part])

    # Convert set to sorted list for consistency
    return sorted(list(fuel_types))


def clean_horsepower(horsepower_str) -> list[int]:
    numbers = re.findall(r"\d+", horsepower_str.replace(",", ""))
    if not numbers:
        return []
    return [int(num) for num in numbers]


def clean_torque(torque_str) -> list[int]:
    numbers = re.findall(r"\d+", torque_str.replace(",", ""))
    if not numbers:
        return []
    return [int(num) for num in numbers]


def clean_capacity(capacity_str) -> tuple[list[int], list[int]]:
    # Initialize sets to hold capacities
    engine_capacities = set()
    battery_capacities = set()

    # Convert to lowercase for consistent processing
    capacity_str = capacity_str.lower()

    # Use regex to find all capacity-related parts, including ranges
    # First, handle ranges
    range_pattern = r"(\d+(?:,\d{3})*)\s*-\s*(\d+(?:,\d{3})*)\s*(?:cc|kwh)"
    for match in re.finditer(range_pattern, capacity_str):
        start = int(match.group(1).replace(",", ""))
        end = int(match.group(2).replace(",", ""))
        if "cc" in match.group():
            engine_capacities.add(start)
            engine_capacities.add(end)
        else:
            battery_capacities.add(start)
            battery_capacities.add(end)

    # Then handle single values
    single_pattern = r"(\d+(?:,\d{3})*)\s*(?:cc|kwh)"
    for match in re.finditer(single_pattern, capacity_str):
        value = int(match.group(1).replace(",", ""))
        if "cc" in match.group():
            engine_capacities.add(value)
        else:
            battery_capacities.add(value)

    # Remove duplicates and sort
    engine_capacities = sorted(list(engine_capacities))
    battery_capacities = sorted(list(battery_capacities))

    # Return the capacities
    return (engine_capacities, battery_capacities)


def parse_engine(engine_str) -> list[tuple[str, int, str]]:
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

    ENGINE_PATTERNS = [
        r"(\d+)-CYLINDER",  # e.g., "4-CYLINDER"
        r"\b\(?[IVFWR](\d+)\)?\b",  # e.g., "V8", "(I4)"
        r"\b(?:INLINE|STRAIGHT|BOXER|FLAT|ROTARY|WANKEL)-(\d+)\b",  # e.g., "INLINE-4", "BOXER-4"
    ]

    # Initialize an empty list to hold the parsed engines
    engine_list = []

    # Split the engine string into parts. The separator can be either "/" or "OR"
    engines = re.split(r"\s*/\s*|\s+OR\s+", engine_str)

    for engine in engines:
        # Initialize variables
        cylinder_layout = None
        cylinder_count = None
        aspiration = None

        # Convert to uppercase and clean the string
        engine = engine.upper().replace(",", " ")

        # Extract cylinder count
        for pattern in ENGINE_PATTERNS:
            match = re.search(pattern, engine)
            if match:
                cylinder_count = int(match.group(1))
                break

        # Extract cylinder layout
        for layout, abbrev in CYLINDER_LAYOUT_MAPPING.items():
            if re.search(rf"\b{layout}(?:\d+|-\d+)?\b", engine) or re.search(
                rf"\b{abbrev}(?:\d+)?\b", engine
            ):
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


@transaction.atomic
def load_and_store(csv_file_path):
    with open(csv_file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            # For the Brand table: Get or create the brand
            brand, _ = Brand.objects.get_or_create(
                name=row["Company Names"].strip().title()
            )

            # For the Performance table: Create the performance
            acc_min, acc_max = clean_acceleration(row["Performance(0 - 100 )KM/H"])
            performance = Performance.objects.create(
                top_speed=clean_top_speed(row["Top Speed"]),
                acceleration_min=acc_min,
                acceleration_max=acc_max,
            )

            # For the Car table: Create the car
            price_min, price_max = clean_price(row["Price"])
            car = Car.objects.create(
                name=row["Cars Names"].strip(),
                slug=slugify(row["Cars Names"].strip()),
                brand=brand,
                performance=performance,
                seats=row["Seats"].strip(),
                price_min=price_min,
                price_max=price_max,
            )

            # For the Fuel_Type table: Get or create the fuel types and add them to the car
            fuel_types = clean_fuel_type(row["Fuel Types"])
            for fuel_type in fuel_types:
                fuel_type, _ = Fuel_Type.objects.get_or_create(fuel_type=fuel_type)
                car.fuel_type.add(fuel_type)

            # For the Engine table: Create the engines and add them to the car
            engines = parse_engine(row["Engine"])
            engine_capacities, battery_capacities = clean_capacity(row["Capacity"])
            torques = clean_torque(row["Torque"])
            horsepowers = clean_horsepower(row["Horsepower"])


if __name__ == "__main__":
    csv_file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data/The Ultimate Cars Dataset 2024.csv",
    )
    load_and_store(csv_file_path)
    print("Data loading completed successfully!")
