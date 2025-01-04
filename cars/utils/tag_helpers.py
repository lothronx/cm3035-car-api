"""Helper functions for tag-related operations in the Car model."""


def create_car_tags(car):
    """
    Creates and associates all relevant tags for a car instance.

    Args:
        car: The car instance to create tags for
    """
    from cars.models import Tag, TagCategory

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
    _create_tag(car, categories["brand"], car.brand.name)

    # Create fuel type tags - now safe to access M2M field
    for fuel in car.fuel_type.all():
        _create_tag(car, categories["fuel_type"], fuel.get_fuel_type_display())

    # Create engine tags
    for engine in car.engine_set.all():
        if engine.engine:
            _create_tag(car, categories["engine"], engine.engine)

    # Create seats tag
    _create_tag(car, categories["seats"], f"{car.seats} seatings")

    # Create price range tag
    avg_price = (car.price_min + car.price_max) / 2
    price_range = _get_price_range(avg_price)
    _create_tag(car, categories["price_range"], price_range)

    # Create displacement tags
    for engine in car.engine_set.all():
        if engine.engine_capacity:
            displacement = _get_displacement_category(engine.engine_capacity)
            _create_tag(car, categories["displacement"], displacement)

    # Create performance tags
    _create_performance_tags(car, categories["performance_metrics"])


def _create_tag(car, category, value):
    """
    Creates and associates a tag with the car.

    Args:
        car: The car instance to associate the tag with
        category (TagCategory): The category of the tag
        value (str): The value for the tag

    Returns:
        Tag: The created or existing tag object
    """
    from cars.models import Tag

    tag, _ = Tag.objects.get_or_create(category=category, value=value)
    tag.cars.add(car)
    return tag


def _get_price_range(avg_price):
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


def _get_displacement_category(capacity):
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


def _create_performance_tags(car, category):
    """
    Creates performance-related tags based on car specifications.

    Args:
        car: The car instance to create tags for
        category (TagCategory): The performance metrics category
    """
    from cars.models import Tag

    # High Torque tag (check all engines)
    if any(engine.torque > 500 for engine in car.engine_set.all()):
        _create_tag(car, category, "HIGH_TORQUE")

    # Get performance metrics
    if car.performance is not None:
        # Fast Acceleration tag
        if car.performance.acceleration_min < 4.0:
            _create_tag(car, category, "FAST_ACCELERATION")

        # Top Speed tag
        if car.performance.top_speed > 250:
            _create_tag(car, category, "TOP_SPEED")
