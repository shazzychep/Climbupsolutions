import redis
from typing import Dict, Optional
from datetime import datetime, timedelta
import json
from ..logging_service import log_error, log_info

class PaymentService:
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.payment_expiry = 900  # 15 minutes in seconds

    def store_payment_data(self, payment_id: str, data: Dict) -> bool:
        """
        Store temporary payment data in Redis with 15-minute expiry.
        
        Args:
            payment_id: Unique identifier for the payment
            data: Payment data to store
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.redis_client.setex(
                f"payment:{payment_id}",
                self.payment_expiry,
                json.dumps(data)
            )
            log_info(f"Stored payment data for {payment_id}")
            return True
        except Exception as e:
            log_error(f"Failed to store payment data: {str(e)}")
            return False

    def get_payment_data(self, payment_id: str) -> Optional[Dict]:
        """
        Retrieve payment data from Redis.
        
        Args:
            payment_id: Unique identifier for the payment
            
        Returns:
            Optional[Dict]: Payment data if found, None otherwise
        """
        try:
            data = self.redis_client.get(f"payment:{payment_id}")
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            log_error(f"Failed to retrieve payment data: {str(e)}")
            return None

    def verify_payment(self, payment_id: str, amount: float) -> bool:
        """
        Verify payment and trigger admin alerts if needed.
        
        Args:
            payment_id: Unique identifier for the payment
            amount: Expected payment amount
            
        Returns:
            bool: True if payment is verified, False otherwise
        """
        payment_data = self.get_payment_data(payment_id)
        if not payment_data:
            log_error(f"Payment data not found for {payment_id}")
            return False

        if payment_data.get("amount") != amount:
            log_error(f"Payment amount mismatch for {payment_id}")
            return False

        # Trigger admin alert for manual verification
        log_info(f"Payment verification required for {payment_id}")
        return True 