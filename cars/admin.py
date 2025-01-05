from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Brand)
admin.site.register(FuelType)
admin.site.register(TagCategory)


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ("brand", "name", "price_min", "price_max")


@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ("top_speed", "acceleration_min", "acceleration_max")


@admin.register(Engine)
class EngineAdmin(admin.ModelAdmin):
    list_display = (
        "engine",
        "aspiration",
        "engine_capacity",
        "battery_capacity",
        "horsepower",
        "torque",
    )

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("category", "value")