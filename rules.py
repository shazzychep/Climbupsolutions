from pymongo import MongoClient
from datetime import datetime
from typing import Dict, List, Optional

class RuleEngine:
    def __init__(self, mongo_uri: str):
        self.client = MongoClient(mongo_uri)
        self.db = self.client.climbup_rules
        
        # Collections
        self.peak_hours = self.db.peak_hours
        self.consultant_rules = self.db.consultant_rules
        self.slot_hold_rules = self.db.slot_hold_rules
        self.payment_rules = self.db.payment_rules

    def initialize_collections(self):
        # Peak hours rules
        self.peak_hours.create_index([("day", 1), ("time_range", 1)])
        
        # Consultant matching rules
        self.consultant_rules.create_index([("specialization", 1), ("is_preferred", 1)])
        
        # Slot hold rules
        self.slot_hold_rules.create_index([("rule_type", 1)])
        
        # Payment verification rules
        self.payment_rules.create_index([("payment_type", 1)])

    def add_peak_hour_rule(self, day: str, time_range: str, multiplier: float):
        """Add a peak hour rule with time range and rate multiplier"""
        self.peak_hours.insert_one({
            "day": day,
            "time_range": time_range,
            "multiplier": multiplier,
            "created_at": datetime.utcnow()
        })

    def get_peak_hour_multiplier(self, day: str, time: datetime) -> float:
        """Get the rate multiplier for a specific time"""
        rule = self.peak_hours.find_one({
            "day": day,
            "time_range": {
                "$regex": f"^{time.hour}:{time.minute}"
            }
        })
        return rule["multiplier"] if rule else 1.0

    def add_consultant_rule(self, specialization: str, is_preferred: bool, 
                          hold_time: int, max_daily_sessions: int):
        """Add rules for consultant matching and slot holds"""
        self.consultant_rules.insert_one({
            "specialization": specialization,
            "is_preferred": is_preferred,
            "hold_time": hold_time,  # in seconds
            "max_daily_sessions": max_daily_sessions,
            "created_at": datetime.utcnow()
        })

    def get_consultant_hold_time(self, specialization: str, is_preferred: bool) -> int:
        """Get the hold time for a specific consultant type"""
        rule = self.consultant_rules.find_one({
            "specialization": specialization,
            "is_preferred": is_preferred
        })
        return rule["hold_time"] if rule else 900  # Default 15 minutes

    def add_payment_rule(self, payment_type: str, verification_time: int, 
                        notification_channels: List[str]):
        """Add rules for payment verification"""
        self.payment_rules.insert_one({
            "payment_type": payment_type,
            "verification_time": verification_time,  # in minutes
            "notification_channels": notification_channels,
            "created_at": datetime.utcnow()
        })

    def get_payment_verification_time(self, payment_type: str) -> int:
        """Get the verification time for a specific payment type"""
        rule = self.payment_rules.find_one({"payment_type": payment_type})
        return rule["verification_time"] if rule else 15  # Default 15 minutes 