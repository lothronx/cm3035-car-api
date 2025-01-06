"""
URL configuration for the cars application.

This module defines the URL patterns and routing configuration for both the web views
and REST API endpoints. It uses Django REST Framework's DefaultRouter for the main API routes
and NestedDefaultRouter for nested resources like car engines.

URL Patterns:
    - /: Main index view for the web interface
    - /api/cars/: List and detail views for cars
    - /api/brands/: List and detail views for car brands
    - /api/cars/{car_id}/engines/: Nested views for car engines

Note: All API endpoints support standard REST operations (GET, POST, PUT, DELETE)
depending on the viewset configuration.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from . import views
from . import api

# Create a router for top-level API resources
router = DefaultRouter()
router.register("cars", api.CarViewSet, basename="car")
router.register("brands", api.BrandViewSet, basename="brand")

# Create a nested router for car-engine relationship
# This allows accessing engines through their parent car resource
car_engine_router = NestedDefaultRouter(router, r'cars', lookup='car', trailing_slash=True)
car_engine_router.register(r'engines', api.CarEngineViewSet, basename='car-engines')

# Application namespace for URL reversing
app_name = "cars"

# Define URL patterns combining both web views and API endpoints
urlpatterns = [
    # Web interface URL
    path("", views.IndexView.as_view(), name="index"),
    # API URLs including both main and nested routes
    path("api/", include(router.urls)),
    path("api/", include(car_engine_router.urls)),
]
