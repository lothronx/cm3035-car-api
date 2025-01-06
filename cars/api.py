from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.response import Response
from .models import *
from .serializers import *
from .services.brand_statistics import get_brand_statistics


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
    lookup_field = "slug"

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

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # After successful creation, return a 303 See Other response
        # This will make the browser do a GET request to the list endpoint
        response.status_code = 303
        response["Location"] = request.path
        return response


class CarEngineViewSet(ModelViewSet):
    serializer_class = CarEngineSerializer
    lookup_field = "pk"

    def get_queryset(self):
        car_slug = self.kwargs.get("car_slug")
        engines = Engine.objects.filter(car__slug=car_slug)
        return engines

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # After successful creation, return a 303 See Other response
        # This will make the browser do a GET request to the list endpoint
        response.status_code = 303
        response["Location"] = request.path
        return response


class BrandViewSet(ReadOnlyModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    lookup_field = "slug"

    def retrieve(self, request, *args, **kwargs):
        brand = self.get_object()
        return Response(get_brand_statistics(brand))
