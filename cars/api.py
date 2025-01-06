from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet

from .models import *
from .serializers import *


class CarViewSet(ModelViewSet):

    queryset = (
        Car.objects.prefetch_related(
            "tag_set__category",
            "brand",
            "fuel_type",
            "engine_set",
        )
        .select_related("performance")
        .all()
    )

    filter_backends = [SearchFilter]
    search_fields = ["name", "brand__name"]
    lookup_field = 'slug'

    def get_serializer_class(self):
        """Return appropriate serializer class based on the action."""
        if self.action == "list":
            return CarListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return CarFormSerializer
        return CarDetailSerializer

    def get_view_name(self):
        """Return custom view name for the car detail view."""
        if hasattr(self, "kwargs") and "slug" in self.kwargs:
            obj = self.get_object()
            return f"{obj.brand.name} - {obj.name}"
        return super().get_view_name()


class CarEngineViewSet(ModelViewSet):
    serializer_class = CarEngineSerializer
    lookup_field = "pk"

    def get_queryset(self):
        car_slug = self.kwargs.get("car_slug")
        engines = Engine.objects.filter(car__slug=car_slug)
        return engines
