from typing import Dict, Any
from datetime import datetime
from .rule_peak_hours import get_peak_hour_multiplier
from ..services.logging_service import log_info, log_error

def calculate_price(
    base_price: float,
    slot_time: datetime,
    duration: int,
    consultant_data: Dict[str, Any],
    rules: Dict[str, Any]
) -> float:
    """
    Calculate the final price for a booking slot.
    
    Args:
        base_price: Base price per hour
        slot_time: Start time of the slot
        duration: Duration in minutes
        consultant_data: Consultant's pricing information
        rules: Dynamic pricing rules from MongoDB
        
    Returns:
        float: Calculated price
    """
    try:
        # Convert duration to hours
        hours = duration / 60
        
        # Get peak hour multiplier
        peak_multiplier = get_peak_hour_multiplier(slot_time, rules)
        
        # Get consultant's experience multiplier
        experience_multiplier = 1.0 + (consultant_data.get('years_experience', 0) * 0.1)
        
        # Calculate final price
        final_price = base_price * hours * peak_multiplier * experience_multiplier
        
        log_info(f"Calculated price: {final_price} for {duration} minutes")
        return round(final_price, 2)
        
    except Exception as e:
        log_error(f"Error calculating price: {str(e)}", "PRICING_ERROR")
        return base_price * (duration / 60)  # Fallback to simple calculation 