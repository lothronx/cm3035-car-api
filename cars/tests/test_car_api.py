import factory
from rest_framework.test import APITestCase
from cars.models import Car, Brand, Performance, FuelType, Engine
from .factories import BrandFactory, CarFactory, PerformanceFactory


class CarAPITest(APITestCase):
    """Test cases for the Car API endpoints."""

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

    def test_get_car_list_success(self):
        """Test successful retrieval of car list."""
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, 200)

        # Check response data structure
        data = response.json()
        self.assertIn("results", data)  # DRF pagination
        results = data["results"]
        self.assertTrue(isinstance(results, list))
        self.assertEqual(len(results), 2)

        # Verify first car data
        first_car = results[0]
        self.assertIn("url", first_car)
        self.assertIn("name", first_car)
        self.assertIn("brand", first_car)
        self.assertIn("price", first_car)
        self.assertIn("tags", first_car)

        # Verify specific car data
        cars = [car["name"] for car in results]
        self.assertIn("Camry", cars)
        self.assertIn("Accord", cars)

    def test_get_car_list_search(self):
        """Test car list search functionality."""
        response = self.client.get(f"{self.url}?search=Toyota", format="json")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        results = data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["brand"], "Toyota")

    def test_get_car_list_empty(self):
        """Test car list when no cars exist."""
        Car.objects.all().delete()
        response = self.client.get(self.url, format="json")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 0)
        self.assertEqual(data["results"], [])

    def test_create_car_success(self):
        """Test successful car creation."""
        # Create a fuel type for testing
        fuel_type = FuelType.objects.create(fuel_type="P")  # Petrol

        data = {
            "name": "New Car",
            "brand": "Tesla",
            "year": 2024,
            "fuel_type": [fuel_type.id],
            "price_min": 45000,
            "price_max": 55000,
            "seats": "5",
            "performance": {
                "top_speed": 250,
                "acceleration_min": 3.5,
                "acceleration_max": 4.0,
            },
        }

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 303)
        self.assertIn("Location", response)

        # Get the created car from the database
        car = Car.objects.get(name="New Car")
        self.assertEqual(car.brand.name, "Tesla")
        self.assertEqual(car.year, 2024)
        self.assertEqual(car.seats, "5")
        self.assertEqual(car.price_min, 45000)
        self.assertEqual(car.price_max, 55000)

        # Verify performance data
        self.assertEqual(car.performance.top_speed, 250)
        self.assertEqual(car.performance.acceleration_min, 3.5)
        self.assertEqual(car.performance.acceleration_max, 4.0)

    def test_create_car_missing_required_fields(self):
        """Test car creation with missing required fields."""
        data = {
            "name": "Incomplete Car"
            # Missing other required fields
        }

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 400)

        errors = response.json()
        self.assertIn("brand", errors)
        self.assertIn("fuel_type", errors)
        self.assertIn("seats", errors)

    def test_create_car_invalid_data(self):
        """Test car creation with invalid data."""
        data = {
            "name": "Invalid Car",
            "brand": "Tesla",
            "year": 3000,  # Invalid year
            "seats": "5",
            "price_min": -1000,  # Invalid price
            "price_max": "invalid",  # Invalid price type
            "performance": {
                "top_speed": -100,  # Invalid speed
                "acceleration_min": 50.0,  # Invalid acceleration
            },
        }

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 400)

        errors = response.json()
        self.assertIn("year", errors)
        self.assertIn("price_min", errors)
        self.assertIn("price_max", errors)

    def test_create_car_duplicate_name_year(self):
        """Test creating a car with duplicate name and year for same brand."""
        fuel_type = FuelType.objects.create(fuel_type="P")

        # Create first car
        data = {
            "name": "Model 3",
            "brand": "Tesla",
            "year": 2024,
            "fuel_type": [fuel_type.id],
            "seats": "5",
            "price_min": 45000,
            "price_max": 55000,
        }

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 303)
        self.assertIn("Location", response)

        # Try to create second car with same details
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 400)

        errors = response.json()
        self.assertIn("non_field_errors", errors)  # Should contain uniqueness error

    def test_get_car_detail_success(self):
        """Test successful retrieval of car detail."""
        # Get the slug from an existing car
        car = Car.objects.get(name="Camry")
        url = f"{self.url}{car.slug}/"

        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

        # Verify response structure
        data = response.json()
        self.assertEqual(data["name"], "Camry")
        self.assertEqual(data["brand"], "Toyota")
        self.assertEqual(data["year"], 2024)
        self.assertIn("performance", data)
        self.assertIn("engines", data)
        self.assertIn("fuel_types", data)

    def test_get_car_detail_not_found(self):
        """Test car detail retrieval with non-existent slug."""
        url = f"{self.url}non-existent-car/"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 404)

    def test_update_car_success(self):
        """Test successful car update."""
        # Get existing car
        car = Car.objects.get(name="Camry")
        url = f"{self.url}{car.slug}/"

        # Create a new fuel type for testing
        fuel_type = FuelType.objects.create(fuel_type="E")  # Electric

        update_data = {
            "name": "Camry Updated",
            "brand": "Toyota",
            "year": 2025,
            "fuel_type": [fuel_type.id],
            "seats": "7",
            "price_min": 35000,
            "price_max": 45000,
            "performance": {
                "top_speed": 220,
                "acceleration_min": 4.5,
                "acceleration_max": 5.0,
            },
        }

        response = self.client.put(url, update_data, format="json")
        self.assertEqual(response.status_code, 200)

        # Verify database update
        car.refresh_from_db()
        self.assertEqual(car.name, "Camry Updated")
        self.assertEqual(car.year, 2025)
        self.assertEqual(car.seats, "7")
        self.assertEqual(car.price_min, 35000)
        self.assertEqual(car.price_max, 45000)

        # Verify performance update
        self.assertEqual(car.performance.top_speed, 220)
        self.assertEqual(car.performance.acceleration_min, 4.5)
        self.assertEqual(car.performance.acceleration_max, 5.0)

    def test_update_car_invalid_data(self):
        """Test car update with invalid data."""
        car = Car.objects.get(name="Camry")
        url = f"{self.url}{car.slug}/"

        update_data = {
            "year": 3000,  # Invalid year
            "price_min": -1000,  # Invalid price
            "performance": {
                "top_speed": -100,  # Invalid speed
            },
        }

        response = self.client.put(url, update_data, format="json")
        self.assertEqual(response.status_code, 400)

        errors = response.json()
        self.assertIn("year", errors)
        self.assertIn("price_min", errors)

    def test_partial_update_car_success(self):
        """Test successful partial car update."""
        car = Car.objects.get(name="Camry")
        url = f"{self.url}{car.slug}/"

        update_data = {"year": 2025, "seats": "7"}

        response = self.client.patch(url, update_data, format="json")
        self.assertEqual(response.status_code, 200)

        # Verify partial update
        car.refresh_from_db()
        self.assertEqual(car.year, 2025)
        self.assertEqual(car.seats, "7")
        # Original name should remain unchanged
        self.assertEqual(car.name, "Camry")

    def test_delete_car_success(self):
        """Test successful car deletion."""
        car = Car.objects.get(name="Camry")
        url = f"{self.url}{car.slug}/"

        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

        # Verify car is deleted
        self.assertFalse(Car.objects.filter(name="Camry").exists())

    def test_delete_car_not_found(self):
        """Test car deletion with non-existent slug."""
        url = f"{self.url}non-existent-car/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)
