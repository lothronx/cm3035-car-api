from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html, urlencode
from cars.utils.admin_filters import TagFilter
from cars.utils.tag_helpers import create_car_tags
from .models import (
    Brand,
    Car,
    Performance,
    FuelType,
    Engine,
    TagCategory,
    Tag,
)


# Register your models here.
admin.site.register(Brand)
admin.site.register(FuelType)
admin.site.register(TagCategory)


class EngineInline(admin.TabularInline):
    model = Engine
    extra = 0


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "price_min", "price_max")
    list_filter = (TagFilter,)
    search_fields = ("brand__name", "name")
    inlines = [EngineInline]

    def get_prepopulated_fields(self, request, obj=None):
        if obj:
            return {}
        return {"slug": ("brand", "name")}

    def save_model(self, request, obj, form, change):
        """Called when saving a Car object in the admin panel."""
        super().save_model(request, obj, form, change)
        form.save_m2m()
        create_car_tags(obj)


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
    list_display = ("__str__", "car_count")
    
    def get_prepopulated_fields(self, request, obj=None):
        if obj:
            return {}
        return {"slug": ("category__name", "value")}

    def car_count(self, obj):
        url = reverse("admin:cars_car_changelist") + f"?{urlencode({'tag': obj.id})}"
        return format_html('<a href="{}">{}</a>', url, obj.cars.count())
