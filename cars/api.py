"""API views for the cars application.

This module contains the ViewSet classes that handle the REST API endpoints
for cars, engines, and brands. Each ViewSet follows the Single Responsibility
Principle and provides specific functionality for its respective model.
"""

from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

from .models import Car, Engine, Brand
from .serializers import (
    CarListSerializer,
    CarDetailSerializer,
    CarFormSerializer,
    CarEngineSerializer,
    BrandSerializer,
)
from .services.brand_statistics import get_brand_statistics
from .services.car_recommendations import get_similar_cars


class CarViewSet(ModelViewSet):
    """ViewSet for managing car objects.

    Follows the Single Responsibility Principle by delegating business logic
    to the CarService class. Provides CRUD operations and custom actions
    for car-related operations.
    """

    lookup_field = "slug"
    filter_backends = [SearchFilter]
    search_fields = ["name", "brand__name"]

    def get_queryset(self):
        """Return an optimized queryset for car objects."""
        return (
            Car.objects.prefetch_related(
                "tag_set__category",
                "brand",
                "fuel_type",
                "engine_set",
            )
            .select_related("performance")
            .all()
        )

    def get_serializer_class(self):
        """Return appropriate serializer class based on the action."""
        if self.action == "list":
            return CarListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return CarFormSerializer
        return CarDetailSerializer

    def create(self, request, *args, **kwargs):
        """Create a new car instance."""
        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            response.status_code = status.HTTP_303_SEE_OTHER
            response["Location"] = request.path
        return response

    @action(detail=True, methods=["get"])
    def recommendation(self, request, slug=None):
        """Retrieve similar cars based on the current car's attributes."""
        car = self.get_object()
        similar_cars = get_similar_cars(car)
        serializer = CarListSerializer(
            similar_cars, many=True, context={"request": request}
        )
        return Response(serializer.data)


class CarEngineViewSet(ModelViewSet):
    """ViewSet for managing car engine objects.

    Provides CRUD operations for car engines with proper validation
    and error handling.
    """

    serializer_class = CarEngineSerializer
    queryset = Engine.objects.none()  # Start with empty queryset

    def get_queryset(self):
        """Filter engines by car if car_slug is provided."""
        car_slug = self.kwargs.get("car_slug")
        if car_slug:
            # Check if car exists first
            try:
                car = Car.objects.get(slug=car_slug)
                return Engine.objects.filter(car=car).order_by('id')  # Order by id for consistent results
            except Car.DoesNotExist:
                from rest_framework.exceptions import NotFound
                raise NotFound(f"Car with slug '{car_slug}' does not exist")
        return Engine.objects.none()  # Return empty queryset if no car_slug

    def get_serializer_context(self):
        """Add car_slug to serializer context."""
        context = super().get_serializer_context()
        context["car_slug"] = self.kwargs.get("car_slug")
        return context

    def create(self, request, *args, **kwargs):
        """Create a new engine instance."""
        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            response.status_code = status.HTTP_303_SEE_OTHER
            response["Location"] = request.path
        return response


class BrandViewSet(ReadOnlyModelViewSet):
    """ViewSet for retrieving brand information.

    Provides read-only access to brand data with additional statistics
    through the retrieve action.
    """

    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    lookup_field = "slug"

    def retrieve(self, request, *args, **kwargs):
        """Retrieve a brand instance with its statistics."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        data["statistics"] = get_brand_statistics(instance)
        return Response(data)
