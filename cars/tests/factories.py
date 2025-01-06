"""Test factories for creating test data."""

import factory
from cars.models import Brand, Performance, Car


class BrandFactory(factory.django.DjangoModelFactory):
    """Factory for creating test Brand instances."""

    class Meta:
        model = Brand

    name = "Test Brand"
    slug = factory.LazyAttribute(lambda obj: obj.name.lower().replace(" ", "-"))


class PerformanceFactory(factory.django.DjangoModelFactory):
    """Factory for creating test Performance instances."""

    class Meta:
        model = Performance

    top_speed = 200
    acceleration_min = 5.0
    acceleration_max = 6.0


class CarFactory(factory.django.DjangoModelFactory):
    """Factory for creating test Car instances."""

    class Meta:
        model = Car

    name = "Test Car"
    slug = factory.LazyAttribute(lambda obj: obj.name.lower().replace(" ", "-"))
    brand = factory.SubFactory(BrandFactory)
    performance = factory.SubFactory(PerformanceFactory)
    seats = "5"
    year = 2024
    price_min = 30000
    price_max = 40000
