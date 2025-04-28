import logging
from typing import Optional
from datetime import datetime
from ..models.mongodb.models import db as mongo_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

class LoggingService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def log_error(self, message: str, error_code: Optional[str] = None) -> None:
        """
        Log error messages with optional error code.
        
        Args:
            message: Error message to log
            error_code: Optional error code for categorization
        """
        if error_code:
            self.logger.error(f"[{error_code}] {message}")
        else:
            self.logger.error(message)

    def log_info(self, message: str) -> None:
        """
        Log informational messages.
        
        Args:
            message: Info message to log
        """
        self.logger.info(message)

    def log_warning(self, message: str) -> None:
        """
        Log warning messages.
        
        Args:
            message: Warning message to log
        """
        self.logger.warning(message)

    def get_user_friendly_message(self, error_code: str) -> str:
        """
        Convert error codes to user-friendly messages.
        
        Args:
            error_code: Error code to convert
            
        Returns:
            str: User-friendly error message
        """
        error_messages = {
            "SLOT_EXPIRED": "Slot expired. Please pick another time",
            "PAYMENT_FAILED": "Payment failed. Please try again",
            "INVALID_SLOT": "Selected time slot is not available",
            "SYSTEM_ERROR": "An unexpected error occurred. Please try again later"
        }
        return error_messages.get(error_code, "An error occurred. Please try again")

# Create a singleton instance
logging_service = LoggingService()

# Convenience functions
def log_error(message: str, error_code: Optional[str] = None) -> None:
    logging_service.log_error(message, error_code)

def log_info(message: str) -> None:
    logging_service.log_info(message)

def log_warning(message: str) -> None:
    logging_service.log_warning(message)

def log_event(event_type, data):
    """
    Log system events to MongoDB
    
    Args:
        event_type (str): Type of event (e.g., 'user_login', 'user_registration')
        data (dict): Event-specific data
    """
    try:
        log_entry = {
            'event_type': event_type,
            'data': data,
            'timestamp': datetime.utcnow()
        }
        
        mongo_db.logs.insert_one(log_entry)
        
        # Also log to application logger
        logger = logging.getLogger(__name__)
        logger.info(f"{event_type}: {data}")
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to log event: {str(e)}")
        
def get_event_logs(event_type=None, start_date=None, end_date=None, limit=100):
    """
    Retrieve event logs with optional filtering
    
    Args:
        event_type (str, optional): Filter by event type
        start_date (datetime, optional): Filter by start date
        end_date (datetime, optional): Filter by end date
        limit (int): Maximum number of logs to return
        
    Returns:
        list: List of log entries
    """
    try:
        query = {}
        
        if event_type:
            query['event_type'] = event_type
            
        if start_date or end_date:
            query['timestamp'] = {}
            if start_date:
                query['timestamp']['$gte'] = start_date
            if end_date:
                query['timestamp']['$lte'] = end_date
                
        logs = mongo_db.logs.find(query).sort('timestamp', -1).limit(limit)
        
        return [{
            'event_type': log['event_type'],
            'data': log['data'],
            'timestamp': log['timestamp']
        } for log in logs]
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to retrieve logs: {str(e)}")
        return [] 