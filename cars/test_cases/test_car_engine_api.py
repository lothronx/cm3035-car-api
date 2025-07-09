import factory
from rest_framework.test import APITestCase
from cars.models import Car, Brand, Performance, FuelType, Engine
from .factories import BrandFactory, CarFactory, PerformanceFactory

class CarEngineAPITest(APITestCase):
    """Test cases for the Car Engine API endpoints."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data for all tests."""
        # Clean up any existing data
        Engine.objects.all().delete()
        Car.objects.all().delete()
        Brand.objects.all().delete()

    def setUp(self):
        """Set up test data."""
        # Create test brand and car
        self.brand = BrandFactory.create(name="Toyota")
        self.car = CarFactory.create(
            name="Supra", brand=self.brand, year=2024, price_min=50000, price_max=60000
        )

        # Create test engines for our car
        self.engine1 = Engine.objects.create(
            car=self.car,
            cylinder_layout="I",  # Inline
            cylinder_count=6,
            aspiration="T",  # Turbocharged
            engine_capacity=2998,  # 3.0L
            horsepower=382,
            torque=500,
        )

        self.engine2 = Engine.objects.create(
            car=self.car,
            cylinder_layout="I",
            cylinder_count=6,
            aspiration="W",  # Twin Turbo
            engine_capacity=2998,
            horsepower=450,
            torque=550,
        )

        self.base_url = "/api/cars"
        self.url = f"{self.base_url}/{self.car.slug}/engines/"

    def tearDown(self):
        """Clean up test data."""
        Engine.objects.all().delete()
        Car.objects.all().delete()
        Brand.objects.all().delete()

        # Reset factory sequences
        BrandFactory.reset_sequence(0)
        CarFactory.reset_sequence(0)

    def test_get_car_engines_not_found(self):
        """Test engines retrieval for non-existent car."""
        url = f"{self.base_url}/non-existent-car/engines/"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 404)

    def test_create_car_engine_success(self):
        """Test successful engine creation."""
        data = {
            "cylinder_layout": "V",
            "cylinder_count": 8,
            "aspiration": "S",  # Supercharged
            "engine_capacity": 6200,
            "horsepower": 650,
            "torque": 850,
        }

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 303)  # Redirects after creation
        self.assertIn("Location", response)

        # Verify database entry
        engine = Engine.objects.get(car=self.car, cylinder_layout="V", cylinder_count=8)
        self.assertEqual(engine.aspiration, "S")
        self.assertEqual(engine.engine_capacity, 6200)
        self.assertEqual(engine.horsepower, 650)
        self.assertEqual(engine.torque, 850)

    def test_create_car_engine_missing_fields(self):
        """Test engine creation with missing required fields."""
        data = {
            "cylinder_layout": "V"
            # Missing other fields
        }

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(
            response.status_code, 303
        )  # Should succeed since fields are nullable
        self.assertIn("Location", response)

        # Verify that missing fields are null
        engine = Engine.objects.latest("id")
        self.assertEqual(engine.cylinder_layout, "V")
        self.assertIsNone(engine.cylinder_count)
        self.assertIsNone(engine.aspiration)
        self.assertIsNone(engine.engine_capacity)
        self.assertIsNone(engine.horsepower)
        self.assertIsNone(engine.torque)

    def test_get_car_engine_success(self):
        """Test successful retrieval of a specific engine."""
        url = f"{self.url}{self.engine1.id}/"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["cylinder_layout"], "I")
        self.assertEqual(data["cylinder_count"], 6)
        self.assertEqual(data["aspiration"], "T")
        self.assertEqual(data["engine_capacity"], 2998)
        self.assertEqual(data["horsepower"], 382)
        self.assertEqual(data["torque"], 500)

    def test_get_car_engine_not_found(self):
        """Test engine retrieval with non-existent ID."""
        url = f"{self.url}99999/"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 404)

    def test_update_car_engine_success(self):
        """Test successful engine update."""
        url = f"{self.url}{self.engine1.id}/"
        data = {
            "cylinder_layout": "V",
            "cylinder_count": 8,
            "aspiration": "W",
            "engine_capacity": 4000,
            "horsepower": 500,
            "torque": 700,
        }

        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, 200)

        # Verify database update
        self.engine1.refresh_from_db()
        self.assertEqual(self.engine1.cylinder_layout, "V")
        self.assertEqual(self.engine1.cylinder_count, 8)
        self.assertEqual(self.engine1.aspiration, "W")
        self.assertEqual(self.engine1.engine_capacity, 4000)
        self.assertEqual(self.engine1.horsepower, 500)
        self.assertEqual(self.engine1.torque, 700)

    def test_update_car_engine_invalid_data(self):
        """Test engine update with invalid data."""
        url = f"{self.url}{self.engine1.id}/"
        data = {
            "cylinder_layout": "X",  # Invalid layout
            "cylinder_count": -1,  # Invalid count
            "aspiration": "Z",  # Invalid aspiration
        }

        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, 400)

        errors = response.json()
        self.assertIn("cylinder_layout", errors)
        self.assertIn("cylinder_count", errors)
        self.assertIn("aspiration", errors)

    def test_partial_update_car_engine_success(self):
        """Test successful partial engine update."""
        url = f"{self.url}{self.engine1.id}/"
        data = {
            "horsepower": 400,
            "torque": 550,
        }

        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, 200)

        # Verify partial update
        self.engine1.refresh_from_db()
        self.assertEqual(self.engine1.horsepower, 400)
        self.assertEqual(self.engine1.torque, 550)
        # Original values should remain unchanged
        self.assertEqual(self.engine1.cylinder_layout, "I")
        self.assertEqual(self.engine1.cylinder_count, 6)

    def test_delete_car_engine_success(self):
        """Test successful engine deletion."""
        url = f"{self.url}{self.engine1.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

        # Verify engine is deleted
        self.assertFalse(Engine.objects.filter(id=self.engine1.id).exists())

    def test_delete_car_engine_not_found(self):
        """Test engine deletion with non-existent ID."""
        url = f"{self.url}99999/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)
