import os
from django.core.management.base import BaseCommand
from cars.load_data import load_data


class Command(BaseCommand):
    help = "Load car data from CSV file into the database"

    def handle(self, *args, **options):
        csv_file_path = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            ),
            "data",
            "The Ultimate Cars Dataset 2024.csv",
        )

        if not os.path.exists(csv_file_path):
            self.stderr.write(
                self.style.ERROR(f"CSV file not found at {csv_file_path}")
            )
            return

        try:
            load_data(csv_file_path)
            self.stdout.write(self.style.SUCCESS("Successfully loaded car data"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error loading car data: {str(e)}"))
