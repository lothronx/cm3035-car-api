import factory
from rest_framework.test import APITestCase
from cars.models import Car, Brand, Performance, FuelType, Engine
from .factories import BrandFactory, CarFactory, PerformanceFactory


class CarRecommendationAPITest(APITestCase):
    """Test cases for the Car Recommendation API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.brand1 = BrandFactory.create(name="Toyota")
        self.brand2 = BrandFactory.create(name="Honda")

        self.car1 = CarFactory(
            name="Camry", brand=self.brand1, year=2024, price_min=25000, price_max=35000
        )

        self.car2 = CarFactory(
            name="Accord",
            brand=self.brand2,
            year=2024,
            price_min=27000,
            price_max=37000,
        )

        # Update URL to match router configuration
        self.url = "/api/cars/"

    def tearDown(self):
        """Clean up test data."""
        Car.objects.all().delete()
        Brand.objects.all().delete()
        Performance.objects.all().delete()

        # Reset factory sequences
        BrandFactory.reset_sequence(0)
        PerformanceFactory.reset_sequence(0)
        CarFactory.reset_sequence(0)

    def test_get_car_recommendation_success(self):
        """Test successful retrieval of car recommendations."""
        # Create additional test cars with varying similarities
        similar_car = CarFactory(
            name="Similar Car",
            brand=self.brand1,  # Same brand as car1
            year=2024,
            price_min=27000,  # Similar price range
            price_max=37000,
        )
        similar_car.performance.top_speed = 210  # Similar performance
        similar_car.performance.save()

        different_car = CarFactory(
            name="Different Car",
            brand=BrandFactory(name="Different Brand"),
            year=2024,
            price_min=80000,  # Very different price range
            price_max=90000,
        )
        different_car.performance.top_speed = 300  # Very different performance
        different_car.performance.save()

        # Get recommendations for car1
        url = f"{self.url}{self.car1.slug}/recommendation/"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(isinstance(data, list))
        self.assertTrue(len(data) > 0)

        # Verify similar car is in recommendations
        recommended_car_names = [car["name"] for car in data]
        self.assertIn("Similar Car", recommended_car_names)

        # Verify order - similar car should appear before different car
        if "Different Car" in recommended_car_names:
            similar_car_index = recommended_car_names.index("Similar Car")
            different_car_index = recommended_car_names.index("Different Car")
            self.assertLess(similar_car_index, different_car_index)

    def test_get_car_recommendation_not_found(self):
        """Test recommendations for non-existent car."""
        url = f"{self.url}non-existent-car/recommendation/"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 404)

    def test_get_car_recommendation_no_similar_cars(self):
        """Test recommendations when there are no other cars."""
        # Delete all cars except car1
        Car.objects.exclude(pk=self.car1.pk).delete()

        url = f"{self.url}{self.car1.slug}/recommendation/"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), 0)  # Should return empty list
