from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


# Create your models here.
class Company(models.Model):
    name = models.CharField(max_length=100, unique=True)


class Fuel_Type(models.Model):
    FUEL_TYPES = (
        ("P", "Petrol"),
        ("D", "Diesel"),
        ("E", "Electric"),
        ("H", "Hydrogen"),
        ("C", "Compressed Natural Gas"),
        ("X", "Hybrid"),
    )
    fuel_type = models.CharField(max_length=1, choices=FUEL_TYPES)


class Car(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField()
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    fuel_type = models.ManyToManyField(Fuel_Type)
    seats = models.CharField(max_length=10)
    year = models.IntegerField(default=2024)
    price_min = models.IntegerField()
    price_max = models.IntegerField()

    def clean(self):
        if self.price_max < self.price_min:
            raise ValidationError("Maximum price cannot be less than minimum price")


class Engine(models.Model):
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
        engine = ""
        if self.cylinder_layout and self.cylinder_count:
            engine += f"{self.cylinder_layout}{self.cylinder_count}"
        elif self.cylinder_layout:
            engine += f"{self.get_cylinder_layout_display()} Engine"
        elif self.cylinder_count:
            engine += f"{self.cylinder_count}-cylinders"
        return engine


class Performance(models.Model):
    top_speed = models.IntegerField(help_text="Top speed in km/h")
    acceleration_min = models.FloatField(
        validators=[MinValueValidator(0.1), MaxValueValidator(30)],
        help_text="Minimal acceleration time from 0 to 100 km/h in seconds",
    )
    acceleration_max = models.FloatField(
        validators=[MinValueValidator(0.1), MaxValueValidator(30)],
        help_text="Maximal acceleration time from 0 to 100 km/h in seconds",
    )
    car = models.OneToOneField(Car, on_delete=models.CASCADE)

    def clean(self):
        if self.acceleration_max < self.acceleration_min:
            raise ValidationError(
                "Maximum acceleration time cannot be less than minimum acceleration time"
            )


class TagCategory(models.Model):
    CATEGORY_CHOICES = [
        ("company", "Company"),
        ("fuel_type", "Fuel Type"),
        ("engine", "Engine"),
        ("seats", "Seats"),
        ("price_range", "Price Range"),
        ("displacement", "Displacement"),
        ("performance_metrics", "Performance Metrics"),
    ]
    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True)


class Tag(models.Model):
    # Price range tags
    PRICE_RANGE_CHOICES = [
        ("ECONOMY", "Economy (Under $30k)"),
        ("MID_RANGE", "Mid-Range ($30k-$60k)"),
        ("PREMIUM", "Premium ($60k-$100k)"),
        ("LUXURY", "Luxury ($100k-$200k)"),
        ("ULTRA_LUXURY", "Ultra Luxury ($200k+)"),
    ]

    # Displacement tags
    DISPLACEMENT_CHOICES = [
        ("SMALL", "Small (0 - 1.0L)"),
        ("LOW_MID", "Low-Mid (1.0 - 1.6L)"),
        ("MID", "Mid (1.6 - 2.5L)"),
        ("LARGE", "Large (2.5 - 4.0L)"),
        ("VERY_LARGE", "Very Large (4.0 - 6.0L)"),
        ("EXTREME", "Extreme (6.0L+)"),
    ]

    # Performance Metrics Tags
    PERFORMANCE_METRICS_CHOICES = [
        ("HIGH_TORQUE", "High Torque"),
        ("FAST_ACCELERATION", "Fast Acceleration"),
        ("TOP_SPEED", "Top Speed"),
    ]

    category = models.ForeignKey(TagCategory, on_delete=models.CASCADE)
    value = models.CharField(max_length=50)
    cars = models.ManyToManyField("Car")

    def clean(self):
        if self.category.name == "price_range" and self.value not in dict(
            self.PRICE_RANGE_CHOICES
        ):
            raise ValidationError("Invalid price range value")
        elif self.category.name == "displacement" and self.value not in dict(
            self.DISPLACEMENT_CHOICES
        ):
            raise ValidationError("Invalid displacement value")
        elif self.category.name == "performance_metrics" and self.value not in dict(
            self.PERFORMANCE_METRICS_CHOICES
        ):
            raise ValidationError("Invalid performance metrics value")
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ["value", "category"]
