from datetime import datetime, timedelta
from typing import Dict, List, Optional
from ..models.mongodb.rules import RuleEngine
from ..models.postgresql.models import Appointment, SlotHold, Consultant

class SchedulingRuleEngine:
    def __init__(self, rule_engine: RuleEngine):
        self.rule_engine = rule_engine

    def check_availability(self, consultant_id: int, start_time: datetime, 
                         end_time: datetime) -> bool:
        """Check if a time slot is available for booking"""
        # Check for existing appointments
        existing_appointments = Appointment.query.filter(
            Appointment.consultant_id == consultant_id,
            Appointment.start_time < end_time,
            Appointment.end_time > start_time,
            Appointment.status.in_(['confirmed', 'pending'])
        ).count()

        # Check for active slot holds
        active_holds = SlotHold.query.filter(
            SlotHold.consultant_id == consultant_id,
            SlotHold.start_time < end_time,
            SlotHold.end_time > start_time,
            SlotHold.status == 'active'
        ).count()

        return existing_appointments == 0 and active_holds == 0

    def calculate_hold_time(self, consultant: Consultant, 
                          start_time: datetime) -> int:
        """Calculate the hold time based on consultant type and peak hours"""
        base_hold_time = self.rule_engine.get_consultant_hold_time(
            consultant.specialization,
            consultant.is_preferred
        )

        # Check if it's a peak hour
        day = start_time.strftime('%A')
        multiplier = self.rule_engine.get_peak_hour_multiplier(day, start_time)
        
        # Extend hold time during peak hours for preferred consultants
        if multiplier > 1.0 and consultant.is_preferred:
            return int(base_hold_time * 1.5)  # 50% longer hold time
        
        return base_hold_time

    def validate_slot_hold(self, slot_hold: SlotHold) -> bool:
        """Validate if a slot hold is still valid"""
        if slot_hold.status != 'active':
            return False
            
        if datetime.utcnow() > slot_hold.expires_at:
            slot_hold.status = 'expired'
            return False
            
        return True

    def get_available_slots(self, consultant_id: int, date: datetime, 
                          duration: int) -> List[Dict]:
        """Get available time slots for a consultant on a specific date"""
        consultant = Consultant.query.get(consultant_id)
        if not consultant:
            return []

        # Get consultant's working hours from availability JSON
        working_hours = consultant.availability.get(str(date.weekday()), {})
        start_hour = working_hours.get('start', 9)  # Default 9 AM
        end_hour = working_hours.get('end', 17)    # Default 5 PM

        available_slots = []
        current_time = datetime.combine(date.date(), datetime.min.time())
        current_time = current_time.replace(hour=start_hour)
        end_time = current_time.replace(hour=end_hour)

        while current_time + timedelta(minutes=duration) <= end_time:
            slot_end = current_time + timedelta(minutes=duration)
            
            if self.check_availability(consultant_id, current_time, slot_end):
                is_peak = self.rule_engine.get_peak_hour_multiplier(
                    current_time.strftime('%A'),
                    current_time
                ) > 1.0
                
                available_slots.append({
                    'start_time': current_time,
                    'end_time': slot_end,
                    'is_peak_hour': is_peak
                })
            
            current_time += timedelta(minutes=15)  # Move to next 15-minute slot

        return available_slots

    def match_consultant(self, specialization: str, 
                        preferred_only: bool = False) -> List[Consultant]:
        """Match consultants based on specialization and preferences"""
        query = Consultant.query.filter(
            Consultant.specialization == specialization,
            Consultant.is_active == True
        )
        
        if preferred_only:
            query = query.filter(Consultant.is_preferred == True)
            
        return query.all() 