from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from . import views
from . import api

router = DefaultRouter()
router.register("cars", api.CarViewSet, basename="car")

# Register nested routes for car engines
car_engine_router = NestedDefaultRouter(router, r'cars', lookup='car', trailing_slash=True)
car_engine_router.register(r'engines', api.CarEngineViewSet, basename='car-engines')

app_name = "cars"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("api/", include(router.urls)),
    path("api/", include(car_engine_router.urls)),
]
