from datetime import timedelta
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash, check_password_hash
from ..models.postgresql.models import User, db
from .logging_service import log_event

def register_user(email, password, name):
    """
    Register a new user
    
    Args:
        email (str): User's email
        password (str): User's password
        name (str): User's name
        
    Returns:
        tuple: (success, message, user)
    """
    try:
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return False, "Email already registered", None
            
        # Create new user
        hashed_password = generate_password_hash(password)
        user = User(
            email=email,
            password=hashed_password,
            name=name
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Log registration event
        log_event('user_registration', {
            'user_id': user.id,
            'email': email,
            'name': name
        })
        
        return True, "User registered successfully", user
        
    except Exception as e:
        db.session.rollback()
        return False, str(e), None

def authenticate_user(email, password):
    """
    Authenticate a user
    
    Args:
        email (str): User's email
        password (str): User's password
        
    Returns:
        tuple: (success, message, tokens)
    """
    try:
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password, password):
            return False, "Invalid email or password", None
            
        # Create tokens
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(minutes=15)
        )
        refresh_token = create_refresh_token(
            identity=user.id,
            expires_delta=timedelta(days=7)
        )
        
        # Log login event
        log_event('user_login', {
            'user_id': user.id,
            'email': email
        })
        
        return True, "Login successful", {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        
    except Exception as e:
        return False, str(e), None

def refresh_token(user_id):
    """
    Create a new access token for a user
    
    Args:
        user_id (int): User's ID
        
    Returns:
        tuple: (success, message, token)
    """
    try:
        access_token = create_access_token(
            identity=user_id,
            expires_delta=timedelta(minutes=15)
        )
        
        return True, "Token refreshed successfully", {
            'access_token': access_token
        }
        
    except Exception as e:
        return False, str(e), None 