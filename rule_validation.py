from typing import Dict, Any
from datetime import datetime, timedelta
from ..services.logging_service import log_info, log_error

def validate_booking(
    booking_data: Dict[str, Any],
    consultant_data: Dict[str, Any],
    rules: Dict[str, Any]
) -> tuple[bool, str]:
    """
    Validate a booking request against business rules.
    
    Args:
        booking_data: Booking request data
        consultant_data: Consultant's information
        rules: Business rules from MongoDB
        
    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    try:
        # Check minimum notice period
        min_notice = rules.get('min_notice_hours', 24)
        booking_time = booking_data['start_time']
        if (booking_time - datetime.now()).total_seconds() < min_notice * 3600:
            return False, "Booking must be made at least 24 hours in advance"
            
        # Check maximum booking duration
        max_duration = rules.get('max_duration_minutes', 120)
        duration = booking_data['duration']
        if duration > max_duration:
            return False, f"Maximum booking duration is {max_duration} minutes"
            
        # Check consultant's working hours
        work_hours = consultant_data.get('working_hours', {})
        day_of_week = booking_time.strftime('%A').lower()
        if day_of_week not in work_hours:
            return False, "Consultant is not available on this day"
            
        # Check if within working hours
        start_time = work_hours[day_of_week]['start']
        end_time = work_hours[day_of_week]['end']
        booking_end = booking_time + timedelta(minutes=duration)
        
        if (booking_time.time() < datetime.strptime(start_time, '%H:%M').time() or
            booking_end.time() > datetime.strptime(end_time, '%H:%M').time()):
            return False, "Booking time is outside consultant's working hours"
            
        log_info(f"Booking validation successful for {booking_time}")
        return True, ""
        
    except Exception as e:
        log_error(f"Error validating booking: {str(e)}", "VALIDATION_ERROR")
        return False, "An error occurred while validating the booking" 