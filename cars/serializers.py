from rest_framework import serializers
from .models import Car, Brand, Performance, FuelType, Engine, Tag, TagCategory
from .utils.car_helpers import create_or_update_car, get_or_create_brand
from .utils.tag_helpers import create_or_update_car_tags

class TagSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.name", read_only=True)
    name = serializers.CharField(source="value", read_only=True)

    class Meta:
        model = Tag
        fields = ["category", "name"]


class PerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Performance
        fields = ["top_speed", "acceleration_min", "acceleration_max"]


class CarListSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="cars:car-detail", lookup_field="slug", lookup_url_kwarg="slug"
    )
    brand = serializers.CharField(source="brand.name")
    tags = TagSerializer(source="tag_set", many=True)
    price = serializers.SerializerMethodField()

    class Meta:
        model = Car
        fields = ["url", "name", "brand", "price", "tags"]

    def get_price(self, obj):
        if not (obj.price_min or obj.price_max):
            return None
        return (
            f"${obj.price_min:,}"
            if obj.price_min == obj.price_max
            else f"${obj.price_min:,}-${obj.price_max:,}"
        )


class CarDetailSerializer(serializers.ModelSerializer):
    brand = serializers.CharField(source="brand.name")
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
            "year",
            "fuel_type",
            "price",
            "seats",
            "top_speed",
            "acceleration",
            "engines",
        ]

    def get_top_speed(self, obj):
        return (
            f"{obj.performance.top_speed} km/h"
            if obj.performance and obj.performance.top_speed
            else None
        )

    def get_acceleration(self, obj):
        if not obj.performance or not (obj.performance.acceleration_min or obj.performance.acceleration_max):
            return None
        
        acc_min = obj.performance.acceleration_min
        acc_max = obj.performance.acceleration_max
        
        return (
            f"{acc_min:.1f} seconds"
            if acc_min == acc_max
            else f"{acc_min:.1f}-{acc_max:.1f} seconds"
        )

    def get_price(self, obj):
        if not (obj.price_min or obj.price_max):
            return None
        return (
            f"${obj.price_min:,}"
            if obj.price_min == obj.price_max
            else f"${obj.price_min:,}-${obj.price_max:,}"
        )


class BrandField(serializers.CharField):
    def to_representation(self, value):
        return value.name if value else None

    def to_internal_value(self, data):
        return get_or_create_brand(data)


class CarFormSerializer(serializers.ModelSerializer):
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
        car = create_or_update_car(validated_data)
        create_or_update_car_tags(car)
        return car

    def update(self, instance, validated_data):
        car = create_or_update_car(validated_data, instance)
        create_or_update_car_tags(car)
        return car


class CarEngineSerializer(serializers.ModelSerializer):
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
        car_slug = self.context["view"].kwargs.get("car_slug")
        car = Car.objects.get(slug=car_slug)
        engine = Engine.objects.create(car=car, **validated_data)
        create_or_update_car_tags(car)
        return engine

    def update(self, instance, validated_data):
        car_slug = self.context["view"].kwargs.get("car_slug")
        car = Car.objects.get(slug=car_slug)
        engine = Engine.objects.update(car=car, **validated_data)
        create_or_update_car_tags(car)
        return engine
