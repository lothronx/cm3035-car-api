from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.
class Companies(models.Model):
    name = models.CharField(max_length=100, unique=True)


class Cars(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    company = models.ForeignKey(Companies, on_delete=models.PROTECT)
    engine = models.ManyToManyField("Engines")
    price_min = models.IntegerField()
    price_max = models.IntegerField()
    seats = models.CharField(max_length=10)
    year = models.IntegerField(default=2024)


class Engines(models.Model):
    FUEL_TYPES = (
        ("P", "Petrol"),
        ("D", "Diesel"),
        ("E", "Electric"),
        ("H", "Hydrogen"),
        ("C", "Compressed Natural Gas"),
        ("X", "Hybrid"),
    )
    CYLINDER_LAYOUTS = (
        ("I", "Inline/Straight"),
        ("V", "V Engine"),
        ("F", "Flat/Boxer"),
        ("W", "W Engine"),
        ("R", "Rotary/Wankel"),
    )
    ASPIRATION_TYPES = (
        ("T", "Turbocharged"),
        ("S", "Supercharged"),
        ("W", "Twin Turbo"),
        ("Q", "Quad Turbo"),
        ("N", "Naturally Aspirated"),
    )

    fuel_type = models.CharField(max_length=1, choices=FUEL_TYPES)
    cylinder_layout = models.CharField(
        max_length=1, choices=CYLINDER_LAYOUTS, null=True
    )
    cylinder_count = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(32)], null=True
    )
    aspiration = models.CharField(max_length=1, choices=ASPIRATION_TYPES, null=True)
    other_configs = models.CharField(max_length=100, null=True)
    cc_capacity = models.IntegerField(null=True, help_text="Engine capacity in cc")
    battery_capacity = models.FloatField(null=True, help_text="Battery capacity in kWh")
    horsepower = models.IntegerField(help_text="Horsepower in hp")
    torque = models.IntegerField(help_text="Torque in Nm")

    @property
    def engine(self):
        engine = ""
        if self.cylinder_layout and self.cylinder_count:
            engine += f"{self.cylinder_layout}{self.cylinder_count}"
        elif self.cylinder_layout:
            engine += self.get_cylinder_layout_display()
        elif self.cylinder_count:
            engine += f"{self.cylinder_count}-cylinders"
        return engine


class Performances(models.Model):
    top_speed = models.IntegerField(help_text="Top speed in km/h")
    acceleration = models.FloatField(
        validators=[MinValueValidator(0.1), MaxValueValidator(30)],
        help_text="Acceleration time from 0 to 100 km/h in seconds",
    )
    car = models.ForeignKey(Cars, on_delete=models.CASCADE)

    @property
    def performance_score(self):
        return (1000 / self.acceleration) * (self.top_speed / 100)


class Tags(models.Model):
    PERFORMANCE_TAGS = [
        ("HIGH_PERFORMANCE", "High Performance"),
        ("SUPER_FAST", "Super Fast"),
        ("LUXURY_PERFORMANCE", "Luxury Performance"),
    ]

    PRICE_RANGE_TAGS = [
        ("LUXURY", "Luxury"),
        ("PREMIUM", "Premium"),
        ("MID_RANGE", "Mid-range"),
        ("ECONOMY", "Economy"),
    ]

    POWER_TAGS = [
        ("ULTRA_HIGH_POWER", "Ultra High Power"),
        ("HIGH_POWER", "High Power"),
        ("MEDIUM_POWER", "Medium Power"),
        ("STANDARD_POWER", "Standard Power"),
    ]

    CATEGORY_CHOICES = [
        ("PERFORMANCE", "Performance"),
        ("PRICE", "Price Range"),
        ("POWER", "Power Category"),
    ]
