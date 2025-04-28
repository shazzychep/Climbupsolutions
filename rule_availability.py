from datetime import datetime, timedelta
from typing import Dict, Any, List
from ..services.logging_service import log_info, log_error

def check_availability(
    consultant_id: str,
    slot_time: datetime,
    duration: int,
    existing_bookings: List[Dict[str, Any]]
) -> bool:
    """
    Check if a time slot is available for booking.
    
    Args:
        consultant_id: ID of the consultant
        slot_time: Start time of the slot
        duration: Duration in minutes
        existing_bookings: List of existing bookings
        
    Returns:
        bool: True if slot is available, False otherwise
    """
    try:
        slot_end = slot_time + timedelta(minutes=duration)
        
        for booking in existing_bookings:
            booking_start = booking['start_time']
            booking_end = booking['end_time']
            
            # Check for overlap
            if (slot_time < booking_end and slot_end > booking_start):
                log_info(f"Slot {slot_time} overlaps with existing booking")
                return False
                
        return True
        
    except Exception as e:
        log_error(f"Error checking availability: {str(e)}", "AVAILABILITY_ERROR")
        return False 