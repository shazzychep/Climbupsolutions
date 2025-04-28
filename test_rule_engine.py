import pytest
from datetime import datetime, timedelta
from ..rule_engine.rule_peak_hours import is_peak_hour, get_peak_hour_multiplier
from ..rule_engine.rule_availability import check_availability
from ..rule_engine.rule_pricing import calculate_price
from ..rule_engine.rule_validation import validate_booking

# Test data
PEAK_HOURS_RULES = {
    "peak_hours": {
        "Monday": [{"start": "09:00", "end": "11:00"}],
        "Tuesday": [{"start": "14:00", "end": "16:00"}]
    },
    "peak_hour_multiplier": 1.2
}

@pytest.mark.parametrize("time,expected", [
    (datetime(2023, 1, 2, 10, 0), True),  # Monday 10 AM
    (datetime(2023, 1, 2, 8, 0), False),  # Monday 8 AM
    (datetime(2023, 1, 3, 15, 0), True),  # Tuesday 3 PM
])
def test_is_peak_hour(time, expected):
    assert is_peak_hour(time, PEAK_HOURS_RULES) == expected

def test_get_peak_hour_multiplier():
    peak_time = datetime(2023, 1, 2, 10, 0)
    off_peak_time = datetime(2023, 1, 2, 8, 0)
    
    assert get_peak_hour_multiplier(peak_time, PEAK_HOURS_RULES) == 1.2
    assert get_peak_hour_multiplier(off_peak_time, PEAK_HOURS_RULES) == 1.0

def test_check_availability():
    slot_time = datetime(2023, 1, 2, 10, 0)
    existing_bookings = [
        {"start_time": datetime(2023, 1, 2, 9, 0), "end_time": datetime(2023, 1, 2, 10, 30)},
        {"start_time": datetime(2023, 1, 2, 11, 0), "end_time": datetime(2023, 1, 2, 12, 0)}
    ]
    
    # Test overlapping slot
    assert not check_availability("consultant1", slot_time, 60, existing_bookings)
    
    # Test available slot
    assert check_availability("consultant1", datetime(2023, 1, 2, 13, 0), 60, existing_bookings)

def test_calculate_price():
    base_price = 100.0
    slot_time = datetime(2023, 1, 2, 10, 0)  # Peak hour
    consultant_data = {"years_experience": 5}
    
    # Test peak hour pricing
    price = calculate_price(base_price, slot_time, 60, consultant_data, PEAK_HOURS_RULES)
    assert price == round(100 * 1.2 * 1.5, 2)  # base * peak_multiplier * experience_multiplier
    
    # Test off-peak pricing
    off_peak_time = datetime(2023, 1, 2, 8, 0)
    price = calculate_price(base_price, off_peak_time, 60, consultant_data, PEAK_HOURS_RULES)
    assert price == round(100 * 1.0 * 1.5, 2)

def test_validate_booking():
    booking_data = {
        "start_time": datetime.now() + timedelta(hours=25),
        "duration": 60
    }
    
    consultant_data = {
        "working_hours": {
            "monday": {"start": "09:00", "end": "17:00"},
            "tuesday": {"start": "09:00", "end": "17:00"}
        }
    }
    
    rules = {
        "min_notice_hours": 24,
        "max_duration_minutes": 120
    }
    
    # Test valid booking
    is_valid, message = validate_booking(booking_data, consultant_data, rules)
    assert is_valid
    assert message == ""
    
    # Test booking with insufficient notice
    booking_data["start_time"] = datetime.now() + timedelta(hours=23)
    is_valid, message = validate_booking(booking_data, consultant_data, rules)
    assert not is_valid
    assert "24 hours in advance" in message
    
    # Test booking outside working hours
    booking_data["start_time"] = datetime.now().replace(hour=8, minute=0) + timedelta(days=1)
    is_valid, message = validate_booking(booking_data, consultant_data, rules)
    assert not is_valid
    assert "working hours" in message 