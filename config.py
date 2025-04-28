import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Common settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret')
    
    # Database settings with Railway private network support
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', os.getenv('POSTGRES_URL'))
    MONGODB_URI = os.getenv('MONGODB_URI', os.getenv('MONGO_URL'))
    REDIS_URL = os.getenv('REDIS_URL')
    
    # Ensure private network connections
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Security settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')
    RATE_LIMIT = os.getenv('RATE_LIMIT', '100/minute')

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    
    # Production database settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 20,
        'max_overflow': 10,
    }

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    
class TestingConfig(Config):
    DEBUG = True
    TESTING = True 