from flask import Blueprint, request, jsonify, current_app
from models import Payment, Appointment
from datetime import datetime, timedelta
import redis
import logging
import json

bp = Blueprint('payment', __name__)
logger = logging.getLogger(__name__)

# Initialize Redis client
redis_client = redis.Redis(
    host=current_app.config['REDIS_HOST'],
    port=current_app.config['REDIS_PORT'],
    db=0,
    decode_responses=True
)

@bp.route('/verify-payment', methods=['POST'])
def verify_payment():
    """Webhook endpoint for payment verification."""
    try:
        data = request.get_json()
        payment_id = data.get('payment_id')
        status = data.get('status')
        
        if not payment_id or not status:
            logger.error("Missing payment_id or status in webhook payload")
            return jsonify({"error": "Missing required fields"}), 400
        
        # Check Redis cache first
        cache_key = f"payment:{payment_id}"
        cached_data = redis_client.get(cache_key)
        
        if cached_data:
            payment_data = json.loads(cached_data)
            logger.info(f"Found payment data in cache: {payment_id}")
        else:
            # Get payment from database
            payment = Payment.query.get(payment_id)
            if not payment:
                logger.error(f"Payment not found: {payment_id}")
                return jsonify({"error": "Payment not found"}), 404
            
            payment_data = {
                "id": payment.id,
                "appointment_id": payment.appointment_id,
                "amount": float(payment.amount),
                "status": payment.status
            }
            
            # Cache payment data for 15 minutes
            redis_client.setex(
                cache_key,
                timedelta(minutes=15),
                json.dumps(payment_data)
            )
        
        # Update payment status
        payment = Payment.query.get(payment_id)
        payment.status = status
        payment.verified_at = datetime.utcnow()
        
        # Update appointment status based on payment
        appointment = Appointment.query.get(payment.appointment_id)
        if status == 'completed':
            appointment.status = 'confirmed'
            logger.info(f"Appointment {appointment.id} confirmed after payment")
        elif status == 'failed':
            appointment.status = 'cancelled'
            logger.warning(f"Appointment {appointment.id} cancelled due to failed payment")
        
        # Clear cache after status update
        redis_client.delete(cache_key)
        
        return jsonify({
            "message": "Payment status updated successfully",
            "payment_id": payment_id,
            "status": status
        }), 200
        
    except Exception as e:
        logger.error(f"Error in payment verification: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500 