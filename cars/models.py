"""
Data models for the cars app.
"""

from django.db import models
from django.core.exceptions import ValidationError



# Create your models here.
class Brand(models.Model):
    """
    Represents a car manufacturer or brand.

    Attributes:
        name (CharField): The unique name of the brand, limited to 100 characters.
    """

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ["name"]


class FuelType(models.Model):
    """
    Represents different types of fuel that can power a vehicle.

    Attributes:
        fuel_type (CharField): Single character code representing the fuel type.
    """

    FUEL_TYPES = (
        ("P", "Petrol"),
        ("D", "Diesel"),
        ("E", "Electric"),
        ("H", "Hydrogen"),
        ("C", "Compressed Natural Gas"),
        ("X", "Hybrid"),
    )
    fuel_type = models.CharField(max_length=1, choices=FUEL_TYPES)

    def __str__(self):
        return dict(self.FUEL_TYPES)[self.fuel_type]

    class Meta:
        ordering = ["fuel_type"]


class Performance(models.Model):
    """
    Stores performance metrics for a car.

    Attributes:
        top_speed (int): Maximum speed of the car in km/h
        acceleration_min (float): Minimum time from 0 to 100 km/h in seconds
        acceleration_max (float): Maximum time from 0 to 100 km/h in seconds
    """

    top_speed = models.IntegerField(null=True, help_text="Unit: km/h")
    acceleration_min = models.FloatField(
        null=True,
        help_text="Unit: seconds",
    )
    acceleration_max = models.FloatField(
        null=True,
        help_text="Unit: seconds",
    )

    @property
    def acceleration(self):
        return (
            self.acceleration_min
            if self.acceleration_min == self.acceleration_max
            else f"{self.acceleration_min}-{self.acceleration_max}"
        )

    def __str__(self):
        return f"Top Speed: {self.top_speed} km/h, Acceleration: {self.acceleration} seconds"


class Car(models.Model):
    """
    Represents a car model with its specifications and relationships.

    Attributes:
        name (CharField): Unique name of the car model
        slug (SlugField): URL-friendly version of the name
        brand (ForeignKey): Reference to the car's manufacturer
        fuel_type (ManyToManyField): Types of fuel the car can use
        performance (OneToOneField): Car's performance specifications
        seats (CharField): Seating configuration
        year (IntegerField): Manufacturing year
        price_min (IntegerField): Minimum price of the car
        price_max (IntegerField): Maximum price of the car
    """

    name = models.CharField(max_length=100)
    slug = models.SlugField()
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)
    fuel_type = models.ManyToManyField(FuelType)
    performance = models.OneToOneField(Performance, on_delete=models.PROTECT, null=True)
    seats = models.CharField(max_length=10)
    year = models.IntegerField(default=2024)
    price_min = models.IntegerField(null=True)
    price_max = models.IntegerField(null=True)

    @property
    def price(self):
        return (
            f"${self.price_min}"
            if self.price_min == self.price_max
            else f"${self.price_min}-{self.price_max}"
        )

    def __str__(self):
        return f"{self.brand.name} {self.name}"

    class Meta:
        unique_together = ["brand", "name"]
        ordering = ["brand", "name"]


class Engine(models.Model):
    """
    Represents an engine configuration for a car.

    Attributes:
        cylinder_layout (CharField): Single letter code for the cylinder layout
        cylinder_count (PositiveSmallIntegerField): Number of cylinders
        aspiration (CharField): Single letter code for the engine aspiration
        engine_capacity (PositiveIntegerField): Engine displacement in cc
        battery_capacity (FloatField): Battery capacity in kWh for electric/hybrid
        horsepower (PositiveIntegerField): Engine power output in hp
        torque (PositiveIntegerField): Engine torque in Nm
        car (ForeignKey): Associated car model
    """

    CYLINDER_LAYOUTS = (
        ("I", "Inline/Straight"),
        ("V", "V"),
        ("F", "Flat/Boxer"),
        ("W", "W"),
        ("R", "Rotary/Wankel"),
    )

    ASPIRATION_TYPES = (
        ("T", "Turbocharged"),
        ("S", "Supercharged"),
        ("W", "Twin Turbo"),
        ("Q", "Quad Turbo"),
        ("N", "Naturally Aspirated"),
    )

    cylinder_layout = models.CharField(
        max_length=1, choices=CYLINDER_LAYOUTS, null=True
    )
    cylinder_count = models.PositiveSmallIntegerField(null=True)
    aspiration = models.CharField(max_length=1, choices=ASPIRATION_TYPES, null=True)
    engine_capacity = models.PositiveIntegerField(null=True, help_text="Unit: cc")
    battery_capacity = models.FloatField(null=True, help_text="Unit: kWh")
    horsepower = models.PositiveIntegerField(null=True, help_text="Unit: hp")
    torque = models.PositiveIntegerField(null=True, help_text="Unit: Nm")
    car = models.ForeignKey(Car, on_delete=models.CASCADE)

    @property
    def engine(self):
        """Generates a string representation of the engine configuration."""
        engine = ""
        if self.cylinder_layout and self.cylinder_count:
            engine += f"{self.cylinder_layout}{self.cylinder_count}"
        elif self.cylinder_layout:
            engine += f"{self.get_cylinder_layout_display()} Engine"
        elif self.cylinder_count:
            engine += f"{self.cylinder_count}-Cylinder"
        return engine

    def __str__(self):
        parts = []
        if self.engine:
            parts.append(self.engine)
        if self.aspiration:
            parts.append(self.get_aspiration_display())
        if self.engine_capacity:
            parts.append(f"Displacement: {self.engine_capacity} cc")
        if self.battery_capacity:
            parts.append(f"Battery Capacity: {self.battery_capacity} kWh")
        if self.horsepower:
            parts.append(f"Horsepower: {self.horsepower} hp")
        if self.torque:
            parts.append(f"Torque: {self.torque} Nm")
        return ", ".join(parts) if parts else "No engine data available"

    class Meta:
        ordering = ["-cylinder_layout", "-cylinder_count", "-aspiration"]


class TagCategory(models.Model):
    """
    Defines categories for car tags and their allowed values.

    Attributes:
        name (str): Name of the tag category
    """

    # Category choices and their associated value choices
    CATEGORY_CHOICES = [
        ("Brand", "Brand"),
        ("Fuel Type", "Fuel Type"),
        ("Engine", "Engine"),
        ("Seats", "Seats"),
        ("Price Range", "Price Range"),
        ("Displacement", "Displacement"),
        ("Performance Metrics", "Performance Metrics"),
    ]

    # Value choices for specific categories
    CATEGORY_VALUE_CHOICES = {
        "price_range": [
            ("Economy", "Economy (Under $30k)"),
            ("Mid-Range", "Mid-Range ($30k-$60k)"),
            ("Premium", "Premium ($60k-$100k)"),
            ("Luxury", "Luxury ($100k-$200k)"),
            ("Ultra Luxury", "Ultra Luxury ($200k+)"),
        ],
        "displacement": [
            ("Small", "Small (0 - 1.0L)"),
            ("Low-Mid", "Low-Mid (1.0 - 1.6L)"),
            ("Mid", "Mid (1.6 - 2.5L)"),
            ("Large", "Large (2.5 - 4.0L)"),
            ("Very Large", "Very Large (4.0 - 6.0L)"),
            ("Extreme", "Extreme (6.0L+)"),
        ],
        "performance_metrics": [
            ("High Torque", "High Torque"),
            ("Fast Acceleration", "Fast Acceleration"),
            ("Top Speed", "Top Speed"),
        ],
    }

    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True)

    def get_allowed_values(self):
        """Get the allowed values for this category"""
        return dict(self.CATEGORY_VALUE_CHOICES.get(self.name, []))

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ["name"]


class Tag(models.Model):
    """
    Represents a tag that can be associated with cars.

    Attributes:
        category (ForeignKey): The category this tag belongs to
        value (CharField): The specific value of this tag
        cars (ManyToManyField): Cars associated with this tag
    """

    category = models.ForeignKey(TagCategory, on_delete=models.CASCADE)
    value = models.CharField(max_length=50)
    cars = models.ManyToManyField(Car)

    def clean(self):
        """Validates that the tag value is allowed for its category."""
        allowed_values = self.category.get_allowed_values()
        if allowed_values and self.value not in allowed_values:
            raise ValidationError(
                f"Invalid value '{self.value}' for category '{self.category.name}'"
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category.name}: {self.value}"

    class Meta:
        unique_together = ["category", "value"]
        ordering = ["category", "value"]
