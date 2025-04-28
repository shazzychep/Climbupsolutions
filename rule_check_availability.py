from datetime import datetime, timedelta
from models import PeakHourRule, SlotHoldRule, ConsultantPreferenceRule
from flask import current_app
import logging

logger = logging.getLogger(__name__)

def check_peak_hour(slot_time):
    """Check if the given time slot falls within peak hours."""
    try:
        day_name = slot_time.strftime('%A')
        time_str = slot_time.strftime('%H:%M')
        
        peak_rule = PeakHourRule.objects(
            day=day_name,
            start_time__lte=time_str,
            end_time__gte=time_str,
            is_active=True
        ).first()
        
        if peak_rule:
            logger.info(f"Peak hour detected: {day_name} {time_str}")
            return True, peak_rule.multiplier
        return False, 1.0
    except Exception as e:
        logger.error(f"Error checking peak hour: {str(e)}")
        return False, 1.0

def get_slot_hold_duration(consultant, is_peak_hour):
    """Get the slot hold duration based on consultant preferences and peak hours."""
    try:
        base_hold = SlotHoldRule.objects(is_active=True).first()
        if not base_hold:
            return 600  # Default 10 minutes
        
        hold_duration = base_hold.hold_duration
        
        # Extend hold time for preferred consultants during peak hours
        if is_peak_hour and consultant.is_preferred:
            hold_duration = int(hold_duration * 1.5)
            logger.info(f"Extended hold time for preferred consultant during peak hours: {hold_duration}s")
        
        return hold_duration
    except Exception as e:
        logger.error(f"Error getting slot hold duration: {str(e)}")
        return 600

def check_consultant_preferences(consultant, client_preferences):
    """Check if consultant matches client preferences."""
    try:
        if not client_preferences:
            return True
        
        preference_rules = ConsultantPreferenceRule.objects(is_active=True)
        total_weight = 0
        matched_weight = 0
        
        for rule in preference_rules:
            if rule.preference_type == 'specialization':
                if consultant.specialization.lower() == rule.value.lower():
                    matched_weight += rule.weight
                total_weight += rule.weight
        
        if total_weight == 0:
            return True
            
        match_percentage = (matched_weight / total_weight) * 100
        logger.info(f"Consultant preference match percentage: {match_percentage}%")
        
        return match_percentage >= 70  # At least 70% match required
    except Exception as e:
        logger.error(f"Error checking consultant preferences: {str(e)}")
        return True

def is_slot_available(consultant, start_time, end_time, client_preferences=None):
    """Check if a time slot is available for booking."""
    try:
        # Check if slot is in the past
        if start_time < datetime.utcnow():
            logger.warning("Attempted to book slot in the past")
            return False, "Cannot book slots in the past"
        
        # Check peak hours
        is_peak, multiplier = check_peak_hour(start_time)
        
        # Get slot hold duration
        hold_duration = get_slot_hold_duration(consultant, is_peak)
        
        # Check consultant preferences
        if not check_consultant_preferences(consultant, client_preferences):
            return False, "Consultant does not match your preferences"
        
        # Check for existing appointments
        from models import Appointment
        existing_appointment = Appointment.query.filter(
            Appointment.consultant_id == consultant.id,
            Appointment.status != 'cancelled',
            (
                (Appointment.start_time <= start_time) & 
                (Appointment.end_time > start_time)
            ) | (
                (Appointment.start_time < end_time) & 
                (Appointment.end_time >= end_time)
            )
        ).first()
        
        if existing_appointment:
            logger.warning(f"Slot conflict found with appointment {existing_appointment.id}")
            return False, "This time slot is already booked"
        
        return True, "Slot is available"
    except Exception as e:
        logger.error(f"Error checking slot availability: {str(e)}")
        return False, "An error occurred while checking slot availability" 