"""Serializers for the cars application."""

from rest_framework import serializers
from .models import Car, Performance, FuelType, Engine, Tag, Brand
from .utils.price_formatter import format_price_range
from .utils.car_helpers import get_or_create_brand, create_or_update_car
from .utils.tag_helpers import create_or_update_car_tags


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags with minimal necessary fields."""

    class Meta:
        model = Tag
        fields = ["category", "value"]


class PerformanceSerializer(serializers.ModelSerializer):
    """Serializer for performance metrics."""

    class Meta:
        model = Performance
        fields = ["top_speed", "acceleration_min", "acceleration_max"]


class CarListSerializer(serializers.ModelSerializer):
    """Simplified serializer for car list view."""

    url = serializers.HyperlinkedIdentityField(
        view_name="cars:car-detail", lookup_field="slug"
    )
    brand = serializers.CharField(source="brand.name")
    price = serializers.SerializerMethodField()
    tags = TagSerializer(source="tag_set", many=True)

    class Meta:
        model = Car
        fields = ["url", "name", "brand", "price", "tags"]

    def get_price(self, obj):
        return format_price_range(obj.price_min, obj.price_max)


class CarDetailSerializer(serializers.ModelSerializer):
    """Detailed car serializer with all necessary fields."""

    brand = serializers.CharField(source="brand.name")
    price = serializers.SerializerMethodField()
    performance = PerformanceSerializer()
    engines = serializers.SerializerMethodField()
    fuel_types = serializers.StringRelatedField(source="fuel_type", many=True)

    class Meta:
        model = Car
        fields = [
            "name",
            "brand",
            "year",
            "price",
            "seats",
            "performance",
            "engines",
            "fuel_types",
        ]

    def get_price(self, obj):
        return format_price_range(obj.price_min, obj.price_max)

    def get_engines(self, obj):
        return [str(engine) for engine in obj.engine_set.all()]


class CarEngineSerializer(serializers.ModelSerializer):
    """Simplified engine serializer with validation."""

    class Meta:
        model = Engine
        fields = [
            "id",
            "cylinder_layout",
            "cylinder_count",
            "aspiration",
            "engine_capacity",
            "battery_capacity",
            "horsepower",
            "torque",
        ]

    def create(self, validated_data):
        """Create a new engine instance with car from context."""
        car_slug = self.context.get("car_slug")
        if not car_slug:
            raise serializers.ValidationError("Car slug is required")

        try:
            car = Car.objects.get(slug=car_slug)
        except Car.DoesNotExist:
            raise serializers.ValidationError(
                f"Car with slug '{car_slug}' does not exist"
            )

        return Engine.objects.create(car=car, **validated_data)


class BrandSerializer(serializers.ModelSerializer):
    """Simple brand serializer."""

    class Meta:
        model = Brand
        fields = ["name", "slug"]


class BrandField(serializers.CharField):
    """Custom field for handling brand names."""

    def to_representation(self, value):
        """Serialize the brand name.

        Returns:
            str: Brand name
        """
        return value.name if value else None

    def to_internal_value(self, data):
        """Deserialize the brand name.

        Returns:
            Brand: Brand instance
        """
        return get_or_create_brand(data)


class CarFormSerializer(serializers.ModelSerializer):
    """Serializer for the Car model form view."""

    url = serializers.HyperlinkedIdentityField(
        view_name="cars:car-detail", lookup_field="slug"
    )
    brand = BrandField()
    fuel_type = serializers.PrimaryKeyRelatedField(
        queryset=FuelType.objects.all(), many=True
    )
    performance = PerformanceSerializer(required=False)

    class Meta:
        model = Car
        fields = [
            "url",
            "id",
            "name",
            "brand",
            "year",
            "fuel_type",
            "price_min",
            "price_max",
            "seats",
            "performance",
        ]

    def create(self, validated_data):
        """Create a new car instance.

        Returns:
            Car: Car instance
        """
        car = create_or_update_car(validated_data)
        create_or_update_car_tags(car)
        return car

    def update(self, instance, validated_data):
        """Update an existing car instance.

        Returns:
            Car: Car instance
        """
        car = create_or_update_car(validated_data, instance)
        create_or_update_car_tags(car)
        return car
