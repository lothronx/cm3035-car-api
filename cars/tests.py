
"""
Tests for the cars API endpoints using hypothesis for property-based testing.
"""
from hypothesis import given, strategies as st
from hypothesis.extra.django import TestCase, from_model
from rest_framework.test import APIClient
from django.urls import reverse
from cars.models import Car, Brand, Performance, FuelType, Tag, TagCategory
from cars.serializers import CarListSerializer, CarDetailSerializer


class CarAPITest(TestCase):
    """Test suite for Car API endpoints."""

    def setUp(self):
        """Set up test client and common test data."""
        self.client = APIClient()
        # Create common test data
        self.brand = Brand.objects.create(name="Test Brand")
        self.performance = Performance.objects.create(
            top_speed=200, acceleration_min=5.0, acceleration_max=6.0
        )
        self.fuel_type = FuelType.objects.create(fuel_type="P")

        # Create tag categories
        self.price_category = TagCategory.objects.create(name="Price Range")
        self.performance_category = TagCategory.objects.create(
            name="Performance Metrics"
        )

    @given(
        name=st.text(min_size=1, max_size=100),
        seats=st.text(min_size=1, max_size=10),
        year=st.integers(min_value=1900, max_value=2100),
        price_min=st.integers(min_value=0, max_value=1000000),
        price_max=st.integers(min_value=0, max_value=1000000),
    )
    def test_create_car(self, name, seats, year, price_min, price_max):
        """Test car creation endpoint with various valid inputs."""
        # Ensure price_max is greater than price_min
        price_max = max(price_min, price_max)

        data = {
            "name": name,
            "brand": self.brand.id,
            "seats": seats,
            "year": year,
            "price_min": price_min,
            "price_max": price_max,
            "fuel_type": [self.fuel_type.id],
            "performance": self.performance.id,
        }

        response = self.client.post(reverse("cars:car-list"), data)
        self.assertEqual(response.status_code, 303)  # Redirect after creation

        # Verify car was created
        self.assertTrue(Car.objects.filter(name=name).exists())

    @given(from_model(Car))
    def test_get_car_detail(self, car):
        """Test retrieving car details."""
        response = self.client.get(
            reverse("cars:car-detail", kwargs={"slug": car.slug})
        )
        self.assertEqual(response.status_code, 200)

        # Verify response data matches serializer output
        serializer = CarDetailSerializer(
            car, context={"request": response.wsgi_request}
        )
        self.assertEqual(response.data, serializer.data)

    def test_get_car_list(self):
        """Test car list endpoint."""
        # Create multiple cars using hypothesis
        cars = from_model(Car).example()

        response = self.client.get(reverse("cars:car-list"))
        self.assertEqual(response.status_code, 200)

        # Verify response format
        self.assertIsInstance(response.data, list)
        if response.data:
            self.assertIn("url", response.data[0])
            self.assertIn("name", response.data[0])
            self.assertIn("brand", response.data[0])

    @given(from_model(Car))
    def test_get_car_recommendations(self, car):
        """Test car recommendations endpoint."""
        # Create some similar cars
        similar_brand = from_model(Car, brand=car.brand).example()

        response = self.client.get(
            reverse("cars:car-recommendation", kwargs={"slug": car.slug})
        )
        self.assertEqual(response.status_code, 200)

        # Verify response format
        self.assertIsInstance(response.data, list)
        if response.data:
            self.assertIn("url", response.data[0])
            self.assertIn("name", response.data[0])
            self.assertIn("brand", response.data[0])

    @given(
        st.text(min_size=1, max_size=100),  # search query
        st.integers(min_value=1, max_value=10),  # number of cars
    )
    def test_search_cars(self, query, num_cars):
        """Test car search functionality."""
        # Create test cars
        for _ in range(num_cars):
            car = from_model(Car).example()

        response = self.client.get(reverse("cars:car-list"), {"search": query})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)


class BrandAPITest(TestCase):
    """Test suite for Brand API endpoints."""

    def setUp(self):
        self.client = APIClient()

    @given(name=st.text(min_size=1, max_size=100).filter(lambda x: len(x.strip()) > 0))
    def test_create_brand(self, name):
        """Test brand creation with various valid names."""
        data = {"name": name}
        response = self.client.post(reverse("cars:brand-list"), data)
        self.assertEqual(response.status_code, 201)

        # Verify brand was created
        self.assertTrue(Brand.objects.filter(name=name).exists())

    @given(from_model(Brand))
    def test_get_brand_detail(self, brand):
        """Test retrieving brand details."""
        response = self.client.get(
            reverse("cars:brand-detail", kwargs={"slug": brand.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], brand.name)

    def test_get_brand_list(self):
        """Test brand list endpoint."""
        # Create multiple brands using hypothesis
        brands = from_model(Brand).example()

        response = self.client.get(reverse("cars:brand-list"))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        if response.data:
            self.assertIn("name", response.data[0])
            self.assertIn("slug", response.data[0])
