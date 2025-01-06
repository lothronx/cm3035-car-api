"""
Service module for calculating brand statistics.
"""

from django.db.models import Avg, Count, F
from cars.models import Engine, Tag


def get_average_price(cars):
    """Calculate the average price for a set of cars."""
    avg_price = cars.aggregate(avg_price=Avg(F("price_min") + F("price_max")) / 2)[
        "avg_price"
    ]
    return f"${round(avg_price, 2) if avg_price else None}"


def calculate_average_metric(queryset, field_path, decimal_places=2, unit=""):
    """
    Calculate the average value for a specific metric from a queryset.

    Args:
        queryset: Django queryset containing the data
        field_path: String path to the field to average
        decimal_places: Number of decimal places to round to (default: 2)
        unit: Unit of measurement to append to the result (default: "")

    Returns:
        str: Formatted string with the average value and unit, or None if no data
    """
    avg_value = queryset.aggregate(avg=Avg(field_path))["avg"]
    if avg_value is None:
        return None
    return f"{round(avg_value, decimal_places)} {unit}".strip()


def calculate_average_range_metric(queryset, min_field, max_field, decimal_places=2, unit=""):
    """
    Calculate the average of a range metric (using min and max fields).

    Args:
        queryset: Django queryset containing the data
        min_field: Field name for minimum value
        max_field: Field name for maximum value
        decimal_places: Number of decimal places to round to (default: 2)
        unit: Unit of measurement to append to the result (default: "")

    Returns:
        str: Formatted string with the average value and unit, or None if no data
    """
    avg_value = queryset.aggregate(
        avg=(Avg(min_field) + Avg(max_field)) / 2
    )["avg"]
    if avg_value is None:
        return None
    return f"{round(avg_value, decimal_places)} {unit}".strip()


def get_performance_metrics(cars):
    """
    Calculate average performance metrics for a set of cars.

    This function computes two key performance indicators:
    1. Average top speed across all cars
    2. Average acceleration (mean of min and max acceleration)

    Args:
        cars: QuerySet of Car objects

    Returns:
        dict: Dictionary containing:
            - average_top_speed: Formatted string with speed in km/h
            - average_acceleration: Formatted string with time in seconds
    """
    return {
        "average_top_speed": calculate_average_metric(
            cars, 
            "performance__top_speed", 
            unit="km/h"
        ),
        "average_acceleration": calculate_average_range_metric(
            cars,
            "performance__acceleration_min",
            "performance__acceleration_max",
            unit="seconds"
        ),
    }


def get_popular_engine_types(cars, limit=3):
    """Get the most popular engine types for a set of cars."""
    engines = (
        Engine.objects.filter(car__in=cars)
        .values("cylinder_layout", "cylinder_count", "aspiration")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    popular_engine_types = []
    for engine in engines:
        if len(popular_engine_types) >= limit:
            break

        description = ""
        layout_display = dict(Engine.CYLINDER_LAYOUTS).get(engine["cylinder_layout"])
        aspiration_display = dict(Engine.ASPIRATION_TYPES).get(engine["aspiration"])

        if engine["cylinder_layout"] and engine["cylinder_count"]:
            description += f"{engine['cylinder_layout']}{engine['cylinder_count']}"
        elif engine["cylinder_layout"]:
            description += f"Unspecified {layout_display} Engine"
        elif engine["cylinder_count"]:
            description += f"{engine['cylinder_count']}-Cylinder"

        if engine["aspiration"]:
            description += f" {aspiration_display}"
        if description:
            popular_engine_types.append({"type": description, "count": engine["count"]})

    return popular_engine_types


def get_popular_tags(cars):
    """Get the most popular tag for each category across a set of cars."""
    category_max_counts = (
        Tag.objects.filter(cars__in=cars)
        .exclude(category__name="Brand")
        .values("category__name")
        .annotate(max_count=Count("cars", distinct=True))
    )

    popular_tags = []
    for category_count in category_max_counts:
        category_name = category_count["category__name"]
        most_popular = (
            Tag.objects.filter(cars__in=cars, category__name=category_name)
            .values("category__name", "value")
            .annotate(count=Count("cars", distinct=True))
            .order_by("-count")
            .first()
        )
        if most_popular:
            popular_tags.append(most_popular)

    return popular_tags


def get_brand_statistics(brand):
    """Get comprehensive statistics for a brand."""
    cars = brand.car_set.all()
    car_count = cars.count()

    return {
        "car_count": car_count,
        "average_price": get_average_price(cars),
        **get_performance_metrics(cars),
        "popular_engine_types": get_popular_engine_types(cars),
        "popular_tags": get_popular_tags(cars),
    }
