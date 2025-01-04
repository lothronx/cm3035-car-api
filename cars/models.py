"""
Data models for the cars app.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


# Create your models here.
class Brand(models.Model):
    """
    Represents a car manufacturer or brand.

    Attributes:
        name (CharField): The unique name of the brand, limited to 100 characters.
    """

    name = models.CharField(max_length=100, unique=True)


class FuelType(models.Model):
    """
    Represents different types of fuel that can power a vehicle.

    Attributes:
        fuel_type (CharField): Single character code representing the fuel type.
            Choices are:
            - P: Petrol
            - D: Diesel
            - E: Electric
            - H: Hydrogen
            - C: Compressed Natural Gas
            - X: Hybrid
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


class Performance(models.Model):
    """
    Stores performance metrics for a car.

    Attributes:
        top_speed (int): Maximum speed of the car in km/h
        acceleration_min (float): Minimum time from 0 to 100 km/h in seconds
        acceleration_max (float): Maximum time from 0 to 100 km/h in seconds
    """

    top_speed = models.IntegerField(help_text="Top speed in km/h")
    acceleration_min = models.FloatField(
        validators=[MinValueValidator(0.1), MaxValueValidator(30)],
        help_text="Minimal acceleration time from 0 to 100 km/h in seconds",
    )
    acceleration_max = models.FloatField(
        validators=[MinValueValidator(0.1), MaxValueValidator(30)],
        help_text="Maximal acceleration time from 0 to 100 km/h in seconds",
    )

    def clean(self):
        """
        Validates that the maximum acceleration time is not less than the minimum acceleration time.

        Raises:
            ValidationError: If acceleration_max is less than acceleration_min
        """
        if self.acceleration_max < self.acceleration_min:
            raise ValidationError(
                "Maximum acceleration time cannot be less than minimum acceleration time"
            )


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

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField()
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)
    fuel_type = models.ManyToManyField(FuelType)
    performance = models.OneToOneField(Performance, on_delete=models.PROTECT, null=True)
    seats = models.CharField(max_length=10)
    year = models.IntegerField(default=2024)
    price_min = models.IntegerField()
    price_max = models.IntegerField()

    def clean(self):
        """
        Validates that the maximum price is not less than the minimum price.

        Raises:
            ValidationError: If price_max is less than price_min
        """
        if self.price_max < self.price_min:
            raise ValidationError("Maximum price cannot be less than minimum price")

    def _create_tag(self, category, value):
        """
        Creates and associates a tag with the car.

        Args:
            category (TagCategory): The category of the tag
            value (str): The value for the tag

        Returns:
            Tag: The created or existing tag object
        """
        tag, _ = Tag.objects.get_or_create(category=category, value=value)
        tag.cars.add(self)
        return tag

    def _get_price_range(self, avg_price):
        """
        Determines the price range category based on average price.

        Args:
            avg_price (float): The average price of the car

        Returns:
            str: Price range category (ECONOMY, MID_RANGE, PREMIUM, LUXURY, or ULTRA_LUXURY)
        """
        ranges = [
            (30000, "ECONOMY"),
            (60000, "MID_RANGE"),
            (100000, "PREMIUM"),
            (200000, "LUXURY"),
            (float("inf"), "ULTRA_LUXURY"),
        ]
        for limit, category in ranges:
            if avg_price <= limit:
                return category

    def _get_displacement_category(self, capacity):
        """
        Determines the engine displacement category based on capacity.

        Args:
            capacity (int): Engine capacity in cc

        Returns:
            str: Displacement category (SMALL, LOW_MID, MID, LARGE, VERY_LARGE, or EXTREME)
        """
        ranges = [
            (1000, "SMALL"),
            (1600, "LOW_MID"),
            (2500, "MID"),
            (4000, "LARGE"),
            (6000, "VERY_LARGE"),
            (float("inf"), "EXTREME"),
        ]
        for limit, category in ranges:
            if capacity <= limit:
                return category

    def _create_performance_tags(self, category):
        """
        Creates performance-related tags based on car specifications.

        Args:
            category (TagCategory): The performance metrics category
        """
        # High Torque tag (check all engines)
        if any(engine.torque > 500 for engine in self.engine_set.all()):
            self._create_tag(category, "HIGH_TORQUE")

        # Get performance metrics
        if self.performance is not None:
            # Fast Acceleration tag
            if self.performance.acceleration_min < 4.0:
                self._create_tag(category, "FAST_ACCELERATION")

            # Top Speed tag
            if self.performance.top_speed > 250:
                self._create_tag(category, "TOP_SPEED")

    def save(self, *args, **kwargs):
        """
        Overrides the default save method to create associated tags.

        Creates tags for brand, fuel type, engine, seats, price range,
        displacement, and performance metrics.
        """
        # Run validation
        self.full_clean()
        # First save the car instance
        super().save(*args, **kwargs)

        # Get or create all tag categories
        categories = {
            "brand": None,
            "fuel_type": None,
            "engine": None,
            "seats": None,
            "price_range": None,
            "displacement": None,
            "performance_metrics": None,
        }

        for name in categories.keys():
            categories[name], _ = TagCategory.objects.get_or_create(name=name)

        # Create brand tag
        self._create_tag(categories["brand"], self.brand.name)

        # Create fuel type tags - now safe to access M2M field
        for fuel in self.fuel_type.all():
            self._create_tag(categories["fuel_type"], fuel.get_fuel_type_display())

        # Create engine tags
        for engine in self.engine_set.all():
            if engine.engine:
                self._create_tag(categories["engine"], engine.engine)

        # Create seats tag
        self._create_tag(categories["seats"], f"{self.seats} seatings")

        # Create price range tag
        avg_price = (self.price_min + self.price_max) / 2
        price_range = self._get_price_range(avg_price)
        self._create_tag(categories["price_range"], price_range)

        # Create displacement tags
        for engine in self.engine_set.all():
            if engine.engine_capacity:
                displacement = self._get_displacement_category(engine.engine_capacity)
                self._create_tag(categories["displacement"], displacement)

        # Create performance tags
        self._create_performance_tags(categories["performance_metrics"])


class Engine(models.Model):
    """
    Represents an engine configuration for a car.

    Attributes:
        cylinder_layout (CharField): Engine cylinder arrangement
            Choices are:
            - I: Inline/Straight
            - V: V
            - F: Flat/Boxer
            - W: W
            - R: Rotary/Wankel
        cylinder_count (PositiveSmallIntegerField): Number of cylinders
        aspiration (CharField): Engine aspiration type
            Choices are:
            - T: Turbocharged
            - S: Supercharged
            - W: Twin Turbo
            - Q: Quad Turbo
            - N: Naturally Aspirated
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
    cylinder_count = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(32)], null=True
    )
    aspiration = models.CharField(max_length=1, choices=ASPIRATION_TYPES, null=True)
    engine_capacity = models.PositiveIntegerField(
        null=True, help_text="Engine capacity in cc"
    )
    battery_capacity = models.FloatField(null=True, help_text="Battery capacity in kWh")
    horsepower = models.PositiveIntegerField(help_text="Horsepower in hp")
    torque = models.PositiveIntegerField(help_text="Torque in Nm")
    car = models.ForeignKey(Car, on_delete=models.CASCADE)

    @property
    def engine(self):
        """
        Generates a string representation of the engine configuration.

        Returns:
            str: Formatted string describing the engine layout and cylinder count.
                Examples:
                    "V8", "Inline Engine", or "4-Cylinders"
        """
        engine = ""
        if self.cylinder_layout and self.cylinder_count:
            engine += f"{self.cylinder_layout}{self.cylinder_count}"
        elif self.cylinder_layout:
            engine += f"{self.get_cylinder_layout_display()} Engine"
        elif self.cylinder_count:
            engine += f"{self.cylinder_count}-Cylinders"
        return engine


class TagCategory(models.Model):
    """
    Defines categories for car tags and their allowed values.

    Attributes:
        name (str): Name of the tag category
        allowed_values (list): List of permitted values for this category
    """

    # Category choices and their associated value choices
    CATEGORY_CHOICES = [
        ("brand", "Brand"),
        ("fuel_type", "Fuel Type"),
        ("engine", "Engine"),
        ("seats", "Seats"),
        ("price_range", "Price Range"),
        ("displacement", "Displacement"),
        ("performance_metrics", "Performance Metrics"),
    ]

    # Value choices for specific categories
    CATEGORY_VALUE_CHOICES = {
        "price_range": [
            ("ECONOMY", "Economy (Under $30k)"),
            ("MID_RANGE", "Mid-Range ($30k-$60k)"),
            ("PREMIUM", "Premium ($60k-$100k)"),
            ("LUXURY", "Luxury ($100k-$200k)"),
            ("ULTRA_LUXURY", "Ultra Luxury ($200k+)"),
        ],
        "displacement": [
            ("SMALL", "Small (0 - 1.0L)"),
            ("LOW_MID", "Low-Mid (1.0 - 1.6L)"),
            ("MID", "Mid (1.6 - 2.5L)"),
            ("LARGE", "Large (2.5 - 4.0L)"),
            ("VERY_LARGE", "Very Large (4.0 - 6.0L)"),
            ("EXTREME", "Extreme (6.0L+)"),
        ],
        "performance_metrics": [
            ("HIGH_TORQUE", "High Torque"),
            ("FAST_ACCELERATION", "Fast Acceleration"),
            ("TOP_SPEED", "Top Speed"),
        ],
    }

    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True)

    def get_allowed_values(self):
        """Get the allowed values for this category"""
        return dict(self.CATEGORY_VALUE_CHOICES.get(self.name, []))


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
        """
        Validates that the tag value is allowed for its category.

        Raises:
            ValidationError: If the tag value is not in the category's allowed values
        """
        allowed_values = self.category.get_allowed_values()
        if allowed_values and self.value not in allowed_values:
            raise ValidationError(
                f"Invalid value '{self.value}' for category '{self.category.name}'"
            )

    class Meta:
        unique_together = ["value", "category"]
