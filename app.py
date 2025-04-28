from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_jwt_extended import JWTManager
from datetime import timedelta
import logging
from logging.handlers import RotatingFileHandler
import os
from flask_limiter.util import get_remote_address
import redis
import time
from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient
from config import ProductionConfig

from routes.auth import auth_bp
from routes.booking import booking_bp
from routes.admin import admin_bp
from routes.consultant import consultant_bp
from routes.payment import payment_bp
from routes.availability import availability_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('logs/app.log', maxBytes=10000000, backupCount=5),
        logging.StreamHandler()
    ]
)

# Initialize Redis connection
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=0
)

# Initialize MongoDB connection
mongo_client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/climbup'))
mongo_db = mongo_client.get_database()

app = Flask(__name__)
CORS(app)

# Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/climbup')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MONGODB_URI'] = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/climbup')
app.config['RATELIMIT_STORAGE_URL'] = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Initialize extensions
jwt = JWTManager(app)
db = SQLAlchemy(app)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri=app.config['RATELIMIT_STORAGE_URL']
)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth', decorators=[limiter.limit("50 per minute")])
app.register_blueprint(booking_bp, url_prefix='/api/booking', decorators=[limiter.limit("100 per minute")])
app.register_blueprint(admin_bp, url_prefix='/api/admin', decorators=[limiter.limit("100 per minute")])
app.register_blueprint(consultant_bp, url_prefix='/api/consultant', decorators=[limiter.limit("100 per minute")])
app.register_blueprint(payment_bp, url_prefix='/api/payment', decorators=[limiter.limit("100 per minute")])
app.register_blueprint(availability_bp, url_prefix='/api/availability', decorators=[limiter.limit("100 per minute")])

@app.route('/health', methods=['GET'])
def health_check():
    health_status = {
        'status': 'healthy',
        'timestamp': time.time(),
        'services': {}
    }
    
    # Test PostgreSQL connection with timeout
    postgres_start = time.time()
    try:
        db.engine.execute('SELECT 1')
        postgres_latency = (time.time() - postgres_start) * 1000
        health_status['services']['postgresql'] = {
            'status': 'healthy',
            'latency_ms': round(postgres_latency, 2)
        }
    except Exception as e:
        health_status['services']['postgresql'] = {
            'status': 'unhealthy',
            'error': str(e),
            'latency_ms': round((time.time() - postgres_start) * 1000, 2)
        }
        health_status['status'] = 'degraded'
    
    # Test MongoDB connection with timeout
    mongo_start = time.time()
    try:
        mongo_db.command('ping', serverSelectionTimeoutMS=5000)
        mongo_latency = (time.time() - mongo_start) * 1000
        health_status['services']['mongodb'] = {
            'status': 'healthy',
            'latency_ms': round(mongo_latency, 2)
        }
    except Exception as e:
        health_status['services']['mongodb'] = {
            'status': 'unhealthy',
            'error': str(e),
            'latency_ms': round((time.time() - mongo_start) * 1000, 2)
        }
        health_status['status'] = 'degraded'
    
    # Test Redis connection with timeout
    redis_start = time.time()
    try:
        redis_client.ping()
        redis_latency = (time.time() - redis_start) * 1000
        health_status['services']['redis'] = {
            'status': 'healthy',
            'latency_ms': round(redis_latency, 2)
        }
    except Exception as e:
        health_status['services']['redis'] = {
            'status': 'unhealthy',
            'error': str(e),
            'latency_ms': round((time.time() - redis_start) * 1000, 2)
        }
        health_status['status'] = 'degraded'
    
    # Return 200 even if some services are degraded
    return jsonify(health_status), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        'error': 'Too many requests',
        'message': 'Rate limit exceeded. Please try again later.',
        'retry_after': e.description
    }), 429

def create_app(config_class=ProductionConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configure logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/app.log',
                                         maxBytes=10240,
                                         backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Application startup')
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    
    # Initialize MongoDB connection with retry logic
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            mongo_client = MongoClient(
                app.config['MONGODB_URI'],
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000
            )
            app.mongo_db = mongo_client.get_default_database()
            app.logger.info('MongoDB connection established')
            break
        except Exception as e:
            if attempt == max_retries - 1:
                app.logger.error(f'MongoDB connection failed after {max_retries} attempts: {str(e)}')
                raise
            app.logger.warning(f'MongoDB connection attempt {attempt + 1} failed, retrying...')
            time.sleep(retry_delay)
    
    # Initialize Redis connection with retry logic
    for attempt in range(max_retries):
        try:
            redis_client = redis.from_url(
                app.config['REDIS_URL'],
                socket_timeout=5,
                socket_connect_timeout=5
            )
            app.redis_client = redis_client
            app.logger.info('Redis connection established')
            break
        except Exception as e:
            if attempt == max_retries - 1:
                app.logger.error(f'Redis connection failed after {max_retries} attempts: {str(e)}')
                raise
            app.logger.warning(f'Redis connection attempt {attempt + 1} failed, retrying...')
            time.sleep(retry_delay)
    
    # Register blueprints
    from api.auth import auth_bp
    from api.booking import booking_bp
    from api.payment import payment_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(booking_bp, url_prefix='/api/bookings')
    app.register_blueprint(payment_bp, url_prefix='/api/payments')
    
    # Health check endpoint with detailed status
    @app.route('/health')
    def health_check():
        status = {
            'status': 'healthy',
            'services': {}
        }
        
        try:
            # Check PostgreSQL
            start_time = time.time()
            db.engine.execute('SELECT 1')
            status['services']['postgresql'] = {
                'status': 'healthy',
                'latency_ms': round((time.time() - start_time) * 1000, 2)
            }
        except Exception as e:
            status['services']['postgresql'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            status['status'] = 'degraded'
        
        try:
            # Check MongoDB
            start_time = time.time()
            app.mongo_db.command('ping')
            status['services']['mongodb'] = {
                'status': 'healthy',
                'latency_ms': round((time.time() - start_time) * 1000, 2)
            }
        except Exception as e:
            status['services']['mongodb'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            status['status'] = 'degraded'
        
        try:
            # Check Redis
            start_time = time.time()
            app.redis_client.ping()
            status['services']['redis'] = {
                'status': 'healthy',
                'latency_ms': round((time.time() - start_time) * 1000, 2)
            }
        except Exception as e:
            status['services']['redis'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            status['status'] = 'degraded'
        
        return status, 200 if status['status'] == 'healthy' else 503
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True) 