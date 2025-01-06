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


def get_performance_metrics(cars):
    """Calculate average performance metrics for a set of cars."""
    avg_top_speed = cars.aggregate(avg_top_speed=Avg("performance__top_speed"))[
        "avg_top_speed"
    ]
    avg_top_speed = f"{round(avg_top_speed, 2) if avg_top_speed else None} km/h"

    avg_acceleration = cars.aggregate(
        avg_acceleration=(
            Avg("performance__acceleration_min") + Avg("performance__acceleration_max")
        )
        / 2
    )["avg_acceleration"]
    avg_acceleration = (
        f"{round(avg_acceleration, 2) if avg_acceleration else None} seconds"
    )

    return {
        "average_top_speed": avg_top_speed,
        "average_acceleration": avg_acceleration,
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
