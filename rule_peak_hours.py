from datetime import datetime, time
from typing import Dict, Any

def is_peak_hour(slot_time: datetime, rules: Dict[str, Any]) -> bool:
    """
    Check if the given time slot falls within peak hours based on rules.
    
    Args:
        slot_time: The time slot to check
        rules: Dictionary containing peak hour rules from MongoDB
        
    Returns:
        bool: True if the slot is during peak hours, False otherwise
    """
    day_of_week = slot_time.strftime("%A")
    current_time = slot_time.time()
    
    # Get peak hours for the specific day
    peak_hours = rules.get("peak_hours", {}).get(day_of_week, [])
    
    for peak_range in peak_hours:
        start_time = datetime.strptime(peak_range["start"], "%H:%M").time()
        end_time = datetime.strptime(peak_range["end"], "%H:%M").time()
        
        if start_time <= current_time <= end_time:
            return True
            
    return False

def get_peak_hour_multiplier(slot_time: datetime, rules: Dict[str, Any]) -> float:
    """
    Get the price multiplier for peak hours.
    
    Args:
        slot_time: The time slot to check
        rules: Dictionary containing peak hour rules from MongoDB
        
    Returns:
        float: Price multiplier (1.0 for non-peak, >1.0 for peak)
    """
    if is_peak_hour(slot_time, rules):
        return rules.get("peak_hour_multiplier", 1.2)
    return 1.0 