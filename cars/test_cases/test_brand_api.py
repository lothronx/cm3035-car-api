import factory
from rest_framework.test import APITestCase
from cars.models import Car, Brand, Performance, FuelType, Engine
from .factories import BrandFactory, CarFactory, PerformanceFactory

class BrandAPITest(APITestCase):
    """Test cases for the Brand API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.brand = BrandFactory.create(name="Toyota")

        # Create multiple cars for the brand with varying specifications
        self.car1 = CarFactory(
            name="Camry",
            brand=self.brand,
            year=2024,
            price_min=25000,
            price_max=35000,
        )
        self.car1.performance.top_speed = 200
        self.car1.performance.acceleration_min = 7.0
        self.car1.performance.acceleration_max = 8.0
        self.car1.performance.save()

        self.car2 = CarFactory(
            name="Supra",
            brand=self.brand,
            year=2024,
            price_min=50000,
            price_max=60000,
        )
        self.car2.performance.top_speed = 250
        self.car2.performance.acceleration_min = 4.0
        self.car2.performance.acceleration_max = 5.0
        self.car2.performance.save()

        # Create engines for the cars
        self.engine1 = Engine.objects.create(
            car=self.car1,
            cylinder_layout="I",
            cylinder_count=4,
            aspiration="T",
            engine_capacity=2000,
            horsepower=200,
            torque=300,
        )

        self.engine2 = Engine.objects.create(
            car=self.car2,
            cylinder_layout="I",
            cylinder_count=6,
            aspiration="T",
            engine_capacity=3000,
            horsepower=380,
            torque=500,
        )

        self.url = "/api/brands/"

    def tearDown(self):
        """Clean up test data."""
        Engine.objects.all().delete()
        Car.objects.all().delete()
        Brand.objects.all().delete()

        # Reset factory sequences
        BrandFactory.reset_sequence(0)
        CarFactory.reset_sequence(0)

    def test_get_brand_detail_success(self):
        """Test successful retrieval of brand details with statistics."""
        url = f"{self.url}{self.brand.slug}/"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["name"], "Toyota")
        self.assertEqual(data["slug"], "toyota")

        # Verify statistics are included
        self.assertIn("statistics", data)
        stats = data["statistics"]

        # Verify car count
        self.assertEqual(stats["car_count"], 2)

        # Verify average price (should be around $42,500)
        self.assertIn("average_price", stats)
        self.assertEqual(stats["average_price"], "$42500.0")

        # Verify performance metrics
        self.assertIn("average_top_speed", stats)
        self.assertEqual(stats["average_top_speed"], "225.0 km/h")
        self.assertIn("average_acceleration", stats)
        self.assertEqual(stats["average_acceleration"], "6.0 seconds")

        # Verify engine types
        self.assertIn("popular_engine_types", stats)
        engines = stats["popular_engine_types"]
        self.assertTrue(isinstance(engines, list))
        self.assertEqual(len(engines), 2)
        # Verify first engine type
        self.assertEqual(engines[0]["type"], "I4 Turbocharged")
        self.assertEqual(engines[0]["count"], 1)
        # Verify second engine type
        self.assertEqual(engines[1]["type"], "I6 Turbocharged")
        self.assertEqual(engines[1]["count"], 1)

        # Verify popular tags
        self.assertIn("popular_tags", stats)
        self.assertTrue(isinstance(stats["popular_tags"], list))

    def test_get_brand_detail_not_found(self):
        """Test brand detail retrieval with non-existent slug."""
        url = f"{self.url}non-existent-brand/"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 404)

    def test_get_brand_detail_no_cars(self):
        """Test brand detail retrieval when brand has no cars."""
        # Create a new brand without cars
        empty_brand = BrandFactory.create(name="Empty Brand")

        url = f"{self.url}{empty_brand.slug}/"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["name"], "Empty Brand")

        # Verify statistics with no data
        stats = data["statistics"]
        self.assertEqual(stats["car_count"], 0)
        self.assertEqual(stats["average_price"], "$None")
        self.assertIsNone(stats["average_top_speed"])
        self.assertIsNone(stats["average_acceleration"])
        self.assertEqual(stats["popular_engine_types"], [])
        self.assertEqual(stats["popular_tags"], [])
