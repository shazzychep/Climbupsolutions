import pytest
from flask import Flask
from flask_jwt_extended import JWTManager
from ..routes.auth import bp as auth_bp
from ..models.postgresql.models import db, User
from ..config import TestConfig

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = Flask(__name__)
    app.config.from_object(TestConfig)
    
    # Initialize extensions
    db.init_app(app)
    JWTManager(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Create all tables
    with app.app_context():
        db.create_all()
        
    yield app
    
    # Clean up
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

def test_register_success(client):
    """Test successful user registration"""
    response = client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': 'testpass123',
        'name': 'Test User'
    })
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] is True
    assert 'user' in data
    assert data['user']['email'] == 'test@example.com'
    assert data['user']['name'] == 'Test User'

def test_register_duplicate_email(client):
    """Test registration with duplicate email"""
    # First registration
    client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': 'testpass123',
        'name': 'Test User'
    })
    
    # Second registration with same email
    response = client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': 'testpass123',
        'name': 'Test User 2'
    })
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'Email already registered' in data['message']

def test_register_missing_fields(client):
    """Test registration with missing fields"""
    response = client.post('/auth/register', json={
        'email': 'test@example.com'
        # Missing password and name
    })
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'Missing required fields' in data['message']

def test_login_success(client):
    """Test successful login"""
    # First register a user
    client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': 'testpass123',
        'name': 'Test User'
    })
    
    # Then try to login
    response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'tokens' in data
    assert 'access_token' in data['tokens']
    assert 'refresh_token' in data['tokens']

def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post('/auth/login', json={
        'email': 'wrong@example.com',
        'password': 'wrongpass'
    })
    
    assert response.status_code == 401
    data = response.get_json()
    assert data['success'] is False
    assert 'Invalid email or password' in data['message']

def test_refresh_token(client):
    """Test token refresh"""
    # First register and login
    client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': 'testpass123',
        'name': 'Test User'
    })
    
    login_response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    
    refresh_token = login_response.get_json()['tokens']['refresh_token']
    
    # Try to refresh token
    response = client.post('/auth/refresh', 
        headers={'Authorization': f'Bearer {refresh_token}'}
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'token' in data
    assert 'access_token' in data['token']

def test_refresh_token_invalid(client):
    """Test refresh token with invalid token"""
    response = client.post('/auth/refresh', 
        headers={'Authorization': 'Bearer invalid_token'}
    )
    
    assert response.status_code == 401
    data = response.get_json()
    assert data['success'] is False 