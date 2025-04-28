from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.auth_service import register_user, authenticate_user, refresh_token

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(k in data for k in ['email', 'password', 'name']):
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400
            
        # Register user
        success, message, user = register_user(
            email=data['email'],
            password=data['password'],
            name=data['name']
        )
        
        if not success:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
        return jsonify({
            'success': True,
            'message': message,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name
            }
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and return JWT tokens
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(k in data for k in ['email', 'password']):
            return jsonify({
                'success': False,
                'message': 'Missing email or password'
            }), 400
            
        # Authenticate user
        success, message, tokens = authenticate_user(
            email=data['email'],
            password=data['password']
        )
        
        if not success:
            return jsonify({
                'success': False,
                'message': message
            }), 401
            
        return jsonify({
            'success': True,
            'message': message,
            'tokens': tokens
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token using refresh token
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Refresh token
        success, message, token = refresh_token(current_user_id)
        
        if not success:
            return jsonify({
                'success': False,
                'message': message
            }), 401
            
        return jsonify({
            'success': True,
            'message': message,
            'token': token
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500 