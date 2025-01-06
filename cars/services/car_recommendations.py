"""
Service for generating car recommendations based on similarity metrics.
"""

from django.db.models import F, Q, Case, When, Count, FloatField
from django.db.models.functions import Abs
from ..models import Car


class CarSimilarityCalculator:
    """
    Calculates similarity scores between cars based on various metrics.
    """
    
    def __init__(self, reference_car):
        """
        Initialize calculator with a reference car.
        
        Args:
            reference_car (Car): The car to find similarities for
        """
        self.reference_car = reference_car
        self.weights = {
            'price': 0.3,
            'performance': 0.3,
            'brand': 0.2,
            'tags': 0.2
        }
    
    def _get_average_price(self):
        """Calculate average price for the reference car."""
        if self.reference_car.price_min and self.reference_car.price_max:
            return (self.reference_car.price_min + self.reference_car.price_max) / 2
        return None

    def _get_price_similarity_annotation(self):
        """Generate annotation for price similarity."""
        car_avg_price = self._get_average_price()
        return Case(
            When(
                price_min__isnull=False,
                price_max__isnull=False,
                then=Case(
                    When(
                        Q(price_min__isnull=False) & 
                        Q(price_max__isnull=False) & 
                        Q(avg_price__gt=0),
                        then=1.0 - Abs(F('avg_price') - car_avg_price) / car_avg_price if car_avg_price else 0
                    ),
                    default=0,
                    output_field=FloatField(),
                )
            ),
            default=0,
            output_field=FloatField(),
        )

    def _get_performance_similarity_annotation(self):
        """Generate annotation for performance similarity."""
        return Case(
            When(
                performance__isnull=False,
                then=(
                    (1.0 - Abs(F('performance__top_speed') - self.reference_car.performance.top_speed) 
                     / self.reference_car.performance.top_speed 
                     if self.reference_car.performance and self.reference_car.performance.top_speed else 0) +
                    (1.0 - Abs(F('performance__acceleration_min') - self.reference_car.performance.acceleration_min) 
                     / self.reference_car.performance.acceleration_min 
                     if self.reference_car.performance and self.reference_car.performance.acceleration_min else 0)
                ) / 2,
            ),
            default=0,
            output_field=FloatField(),
        )

    def _get_brand_similarity_annotation(self):
        """Generate annotation for brand similarity."""
        return Case(
            When(brand=self.reference_car.brand, then=1.0),
            default=0,
            output_field=FloatField(),
        )

    def _get_tag_similarity_annotation(self):
        """Generate annotation for tag similarity."""
        return Case(
            When(
                Q(matching_tags__gt=0) & Q(tag__isnull=False),
                then=F('matching_tags') * 1.0 / self.reference_car.tag_set.count() 
                     if self.reference_car.tag_set.exists() else 0
            ),
            default=0,
            output_field=FloatField(),
        )


def get_similar_cars(car, limit=5):
    """
    Get similar cars based on multiple similarity metrics.
    
    Args:
        car (Car): Reference car to find similarities for
        limit (int): Maximum number of similar cars to return
        
    Returns:
        QuerySet: Similar cars ordered by similarity score
    """
    calculator = CarSimilarityCalculator(car)
    
    return (
        Car.objects.exclude(id=car.id)
        .annotate(
            # Calculate average price for comparison
            avg_price=(F('price_min') + F('price_max')) / 2,
            # Similarity metrics
            price_similarity=calculator._get_price_similarity_annotation(),
            performance_similarity=calculator._get_performance_similarity_annotation(),
            brand_similarity=calculator._get_brand_similarity_annotation(),
            # Tag similarity (percentage of matching tags)
            matching_tags=Count('tag', filter=Q(tag__in=car.tag_set.all())),
            tag_similarity=calculator._get_tag_similarity_annotation(),
        )
        .annotate(
            # Calculate overall similarity score (weighted average)
            similarity_score=(
                F('price_similarity') * calculator.weights['price'] +
                F('performance_similarity') * calculator.weights['performance'] +
                F('brand_similarity') * calculator.weights['brand'] +
                F('tag_similarity') * calculator.weights['tags']
            )
        )
        .order_by('-similarity_score')[:limit]
    )
