"""
Django management command to load car data into the database.
"""

import csv
import os
from typing import Dict, Any
from django.core.management.base import BaseCommand
from django.db import transaction
from cars.utils.car_helpers import create_car
from cars.utils.data_cleaners import clean_car_data
from cars.models import Car, Brand, Performance, FuelType, Engine, Tag, TagCategory


class DatabaseCleaner:
    """Handles cleaning of database tables."""

    @staticmethod
    def clean_all_tables() -> None:
        """Delete all records from all tables in the correct order to handle dependencies."""
        tables = [Tag, TagCategory, Engine, Car, Performance, FuelType, Brand]
        for table in tables:
            table.objects.all().delete()


class CarDataLoader:
    """Handles loading of car data from file to database."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.processed_cars = set()

    def validate_file(self) -> None:
        """Validate that the data file exists."""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Data file not found: {self.file_path}")

    def is_duplicate(self, row: Dict[str, Any]) -> bool:
        """Check if a car record is a duplicate.

        Args:
            row: Dictionary containing car data

        Returns:
            bool: True if car is already processed, False otherwise
        """
        car_identifier = f"{row['Company Names'].strip().lower()} {row['Cars Names'].strip().lower()}"
        if car_identifier in self.processed_cars:
            return True
        self.processed_cars.add(car_identifier)
        return False

    def process_row(self, row: Dict[str, Any]) -> None:
        """Process a single row of car data.

        Args:
            row: Dictionary containing car data
        """
        if self.is_duplicate(row):
            return

        car_data = clean_car_data(row)
        create_car(car_data)

    @transaction.atomic
    def load(self) -> None:
        """Load car data from file into database."""
        self.validate_file()
        DatabaseCleaner.clean_all_tables()

        with open(self.file_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    self.process_row(row)
                except Exception as e:
                    raise Exception(f"Failed to process car: {str(e)}") from e


class Command(BaseCommand):
    """Django command to load car data into the database."""

    help = "Load car data from file into the database"

    def get_data_file_path(self) -> str:
        """Get the path to the data file."""
        base_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        )
        return os.path.join(base_dir, "data", "The Ultimate Cars Dataset 2024.csv")

    def handle(self, *args, **options) -> None:
        """Handle the command execution."""
        file_path = self.get_data_file_path()

        try:
            loader = CarDataLoader(file_path)
            loader.load()
            self.stdout.write(self.style.SUCCESS("Successfully loaded car data"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error: {str(e)}"))
