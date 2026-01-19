"""
Authentication API endpoints
"""

from flask import Blueprint, request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.services.auth_service import AuthService

# Flask Blueprint for API routes
bp = Blueprint('auth_api', __name__)

# Flask-RESTX Namespace for documentation
auth_ns = Namespace('auth', description='Authentication operations')

auth_service = AuthService()

login_model = auth_ns.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

register_model = auth_ns.model('Register', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
    'first_name': fields.String(required=True, description='First name'),
    'last_name': fields.String(required=True, description='Last name'),
    'phone': fields.String(description='Phone number'),
    'role': fields.String(description='User role', enum=['customer', 'provider'])
})

token_model = auth_ns.model('Token', {
    'access_token': fields.String(description='JWT access token'),
    'refresh_token': fields.String(description='JWT refresh token'),
    'user': fields.Raw(description='User information')
})

@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(register_model)
    @auth_ns.response(201, 'User registered successfully')
    @auth_ns.response(400, 'Validation error')
    def post(self):
        """Register a new user"""
        data = request.get_json()
        
        user, error = auth_service.register_user(
            email=data.get('email'),
            password=data.get('password'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            role=data.get('role', 'customer'),
            phone=data.get('phone')
        )
        
        if error:
            return {'message': error}, 400
        
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return {
            'message': 'User registered successfully',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }, 201

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.marshal_with(token_model)
    @auth_ns.response(200, 'Login successful')
    @auth_ns.response(401, 'Invalid credentials')
    def post(self):
        """Login with email and password"""
        data = request.get_json()
        
        user, error = auth_service.login_user(
            email=data.get('email'),
            password=data.get('password')
        )
        
        if error:
            return {'message': error}, 401
        
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }

@auth_ns.route('/refresh')
class RefreshToken(Resource):
    @jwt_required(refresh=True)
    @auth_ns.response(200, 'Token refreshed')
    def post(self):
        """Refresh access token"""
        current_user_id = get_jwt_identity()
        access_token = create_access_token(identity=current_user_id)
        
        return {'access_token': access_token}

@auth_ns.route('/me')
class CurrentUser(Resource):
    @jwt_required()
    @auth_ns.response(200, 'Current user information')
    @auth_ns.response(401, 'Unauthorized')
    def get(self):
        """Get current user information"""
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if not user:
            return {'message': 'User not found'}, 404
        
        return user.to_dict(include_sensitive=True)

# Flask routes for API
@bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    user, error = auth_service.register_user(
        email=data.get('email'),
        password=data.get('password'),
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        role=data.get('role', 'customer'),
        phone=data.get('phone')
    )
    
    if error:
        return {'message': error}, 400
    
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return {
        'message': 'User registered successfully',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }, 201

@bp.route('/login', methods=['POST'])
def login():
    """Login with email and password"""
    data = request.get_json()
    
    user, error = auth_service.login_user(
        email=data.get('email'),
        password=data.get('password')
    )
    
    if error:
        return {'message': error}, 401
    
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }
