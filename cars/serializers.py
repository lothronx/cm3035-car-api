"""Serializers for the cars application.

This module contains the serializer classes that handle the conversion
of complex data types, such as Django models, to Python native datatypes
that can then be easily rendered into JSON, XML or other content types.
"""

from rest_framework import serializers
from .models import Car, Performance, FuelType, Engine, Tag, Brand
from .utils.car_helpers import create_or_update_car, get_or_create_brand
from .utils.tag_helpers import create_or_update_car_tags


class TagSerializer(serializers.ModelSerializer):
    """Serializer for the Tag model.

    Provides a simplified representation of tags, including their category
    and value as readable strings.
    """

    category = serializers.CharField(source="category.name", read_only=True)
    name = serializers.CharField(source="value", read_only=True)

    class Meta:
        model = Tag
        fields = ["category", "name"]


class PerformanceSerializer(serializers.ModelSerializer):
    """Serializer for the Performance model.

    Handles the serialization of car performance metrics.
    """

    class Meta:
        model = Performance
        fields = ["top_speed", "acceleration_min", "acceleration_max"]


class PriceFormattingMixin:
    """Mixin for formatting price ranges in car serializers.

    Provides a method to format price ranges in a human-readable format,
    with proper currency symbols and thousand separators.
    """

    def get_price(self, obj):
        """Format the price range as a string.

        Returns:
            str: Formatted price string (e.g., "$50,000" or "$50,000-$60,000")
            None: If no price data is available
        """
        if not (obj.price_min or obj.price_max):
            return None
        return (
            f"${obj.price_min:,}"
            if obj.price_min == obj.price_max
            else f"${obj.price_min:,}-${obj.price_max:,}"
        )


class CarListSerializer(PriceFormattingMixin, serializers.ModelSerializer):
    """Serializer for the Car model list view.

    Provides a simplified representation of cars for list views,
    including URLs for navigation and formatted price ranges.
    """

    # Generate URLs for car detail views
    url = serializers.HyperlinkedIdentityField(
        view_name="cars:car-detail", lookup_field="slug", lookup_url_kwarg="slug"
    )
    brand = serializers.CharField(source="brand.name")
    brand_url = serializers.HyperlinkedRelatedField(
        source="brand",
        view_name="cars:brand-detail",
        lookup_field="slug",
        read_only=True,
    )
    price = serializers.SerializerMethodField()
    tags = TagSerializer(source="tag_set", many=True)

    class Meta:
        model = Car
        fields = ["url", "name", "brand", "brand_url", "price", "tags"]


class CarDetailSerializer(PriceFormattingMixin, serializers.ModelSerializer):
    """Serializer for the Car model detail view.

    Provides a detailed representation of cars, including performance metrics,
    fuel types, and formatted price ranges.
    """

    brand = serializers.CharField(source="brand.name")
    brand_url = serializers.HyperlinkedRelatedField(
        source="brand",
        view_name="cars:brand-detail",
        lookup_field="slug",
        read_only=True,
    )
    fuel_type = serializers.StringRelatedField(many=True)
    engines = serializers.StringRelatedField(source="engine_set", many=True)
    top_speed = serializers.SerializerMethodField()
    acceleration = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Car
        fields = [
            "id",
            "name",
            "brand",
            "brand_url",
            "year",
            "fuel_type",
            "price",
            "seats",
            "top_speed",
            "acceleration",
            "engines",
        ]

    def get_top_speed(self, obj):
        """Format the top speed as a string.

        Returns:
            str: Formatted top speed string (e.g., "250 km/h")
            None: If no top speed data is available
        """
        return (
            f"{obj.performance.top_speed} km/h"
            if obj.performance and obj.performance.top_speed
            else None
        )

    def get_acceleration(self, obj):
        """Format the acceleration as a string.

        Returns:
            str: Formatted acceleration string (e.g., "3.5 seconds" or "3.5-4.5 seconds")
            None: If no acceleration data is available
        """
        if not obj.performance or not (
            obj.performance.acceleration_min or obj.performance.acceleration_max
        ):
            return None

        acc_min = obj.performance.acceleration_min
        acc_max = obj.performance.acceleration_max

        return (
            f"{acc_min:.1f} seconds"
            if acc_min == acc_max
            else f"{acc_min:.1f}-{acc_max:.1f} seconds"
        )


class BrandField(serializers.CharField):
    """Custom field for handling brand names.

    Provides a way to serialize and deserialize brand names, using the
    get_or_create_brand utility function.
    """

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


class BrandSerializer(serializers.ModelSerializer):
    """Serializer for the Brand model.

    Provides a simple representation of brands, including their name and slug.
    """

    class Meta:
        model = Brand
        fields = ["name", "slug"]
        lookup_field = "slug"


class CarFormSerializer(serializers.ModelSerializer):
    """Serializer for the Car model form view.

    Provides a way to serialize and deserialize car data, including brand,
    fuel types, and performance metrics.
    """

    url = serializers.HyperlinkedIdentityField(
        view_name="cars:car-detail", lookup_field="slug", lookup_url_kwarg="slug"
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


class CarEngineSerializer(serializers.ModelSerializer):
    """Serializer for the Engine model.

    Provides a way to serialize and deserialize engine data, including
    cylinder layout, capacity, and horsepower.
    """

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

    def _process_engine(self, validated_data, instance=None):
        """Process the engine data.

        Returns:
            Engine: Engine instance
        """
        car_slug = self.context["view"].kwargs.get("car_slug")
        car = Car.objects.get(slug=car_slug)

        if instance:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            engine = instance
        else:
            engine = Engine.objects.create(car=car, **validated_data)

        create_or_update_car_tags(car)
        return engine

    def create(self, validated_data):
        """Create a new engine instance.

        Returns:
            Engine: Engine instance
        """
        return self._process_engine(validated_data)

    def update(self, instance, validated_data):
        """Update an existing engine instance.

        Returns:
            Engine: Engine instance
        """
        return self._process_engine(validated_data, instance)
