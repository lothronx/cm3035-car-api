"""Formatting price ranges."""

def format_price_range(price_min: float, price_max: float) -> str | None:
    """Format a price range as a human-readable string.
    
    Args:
        price_min: Minimum price
        price_max: Maximum price
        
    Returns:
        Formatted price string (e.g., "$50,000" or "$50,000-$60,000")
        None if no price data is available
    """
    if not (price_min or price_max):
        return None
        
    return (
        f"${price_min:,}"
        if price_min == price_max
        else f"${price_min:,}-${price_max:,}"
    )
