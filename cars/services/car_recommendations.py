"""
Service for generating car recommendations based on similarity metrics
including price, performance, brand, and tags. 
"""

from django.db.models import F, Q, Case, When, Count, FloatField
from django.db.models.functions import Abs
from cars.models import Car


def calculate_average_price(car):
    """
    Calculate the average price for a car if both min and max prices are available.

    Args:
        car (Car): The car object to calculate average price for

    Returns:
        float|None: Average price if both min and max prices exist, None otherwise
    """
    if car.price_min and car.price_max:
        return (car.price_min + car.price_max) / 2
    return None


def get_price_similarity_annotation(reference_car):
    """
    Generate annotation for calculating price similarity between cars.

    Args:
        reference_car (Car): The reference car to compare prices against

    Returns:
        Case: Django ORM annotation for price similarity calculation
    """
    car_avg_price = calculate_average_price(reference_car)
    if not car_avg_price:
        return Case(default=0, output_field=FloatField())

    return Case(
        When(
            price_min__isnull=False,
            price_max__isnull=False,
            then=1.0
            - Abs((F("price_min") + F("price_max")) / 2 - car_avg_price)
            / car_avg_price,
        ),
        default=0,
        output_field=FloatField(),
    )


def get_performance_similarity_annotation(reference_car):
    """
    Generate annotation for calculating performance similarity between cars.

    Args:
        reference_car (Car): The reference car to compare performance against

    Returns:
        Case: Django ORM annotation for performance similarity calculation
    """
    if not reference_car.performance:
        return Case(default=0, output_field=FloatField())

    return Case(
        When(
            performance__isnull=False,
            then=(
                (
                    1.0
                    - Abs(
                        F("performance__top_speed")
                        - reference_car.performance.top_speed
                    )
                    / reference_car.performance.top_speed
                    if reference_car.performance.top_speed
                    else 0
                )
                + (
                    1.0
                    - Abs(
                        F("performance__acceleration_min")
                        - reference_car.performance.acceleration_min
                    )
                    / reference_car.performance.acceleration_min
                    if reference_car.performance.acceleration_min
                    else 0
                )
            )
            / 2,
        ),
        default=0,
        output_field=FloatField(),
    )


def get_brand_similarity_annotation(reference_car):
    """
    Generate annotation for brand similarity (exact match only).

    Args:
        reference_car (Car): The reference car to compare brand against

    Returns:
        Case: Django ORM annotation for brand similarity calculation
    """
    return Case(
        When(brand=reference_car.brand, then=1.0),
        default=0,
        output_field=FloatField(),
    )


def get_tag_similarity_annotation(reference_car):
    """
    Generate annotation for calculating tag similarity between cars.

    Args:
        reference_car (Car): The reference car to compare tags against

    Returns:
        Case: Django ORM annotation for tag similarity calculation
    """
    tag_count = reference_car.tag_set.count()
    if not tag_count:
        return Case(default=0, output_field=FloatField())

    return Case(
        When(matching_tags__gt=0, then=F("matching_tags") * 1.0 / tag_count),
        default=0,
        output_field=FloatField(),
    )


def calculate_similarity_score(price_sim, perf_sim, brand_sim, tag_sim, weights=None):
    """
    Calculate the overall similarity score based on individual metrics.

    Args:
        price_sim (float): Price similarity score
        perf_sim (float): Performance similarity score
        brand_sim (float): Brand similarity score
        tag_sim (float): Tag similarity score
        weights (dict, optional): Custom weights for each metric.
                                Defaults to predefined weights.

    Returns:
        float: Overall similarity score
    """
    if weights is None:
        weights = {"price": 0.3, "performance": 0.3, "brand": 0.2, "tags": 0.2}

    return (
        price_sim * weights["price"]
        + perf_sim * weights["performance"]
        + brand_sim * weights["brand"]
        + tag_sim * weights["tags"]
    )


def get_similar_cars(car, limit=5, weights=None):
    """
    Get similar cars based on multiple similarity metrics.

    This function calculates similarity scores based on price, performance,
    brand, and tags, then returns the most similar cars ordered by their
    overall similarity score.

    Args:
        car (Car): Reference car to find similarities for
        limit (int, optional): Maximum number of similar cars to return. Defaults to 5.
        weights (dict, optional): Custom weights for similarity metrics.
                                Defaults to predefined weights.

    Returns:
        QuerySet: Similar cars ordered by similarity score
    """
    recommendations = (
        Car.objects.exclude(id=car.id)
        .annotate(
            matching_tags=Count("tag", filter=Q(tag__in=car.tag_set.all())),
            price_similarity=get_price_similarity_annotation(car),
            performance_similarity=get_performance_similarity_annotation(car),
            brand_similarity=get_brand_similarity_annotation(car),
            tag_similarity=get_tag_similarity_annotation(car),
            similarity_score=calculate_similarity_score(
                F("price_similarity"),
                F("performance_similarity"),
                F("brand_similarity"),
                F("tag_similarity"),
                weights,
            ),
        )
        .order_by("-similarity_score")[:limit]
    )

    return recommendations
