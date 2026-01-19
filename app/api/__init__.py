"""
API Blueprint for RESTful endpoints
"""

from flask import Blueprint

bp = Blueprint('api', __name__)

# Import and register API routes
from app.api.auth import bp as auth_bp
from app.api.scooters import bp as scooters_bp
from app.api.rentals import bp as rentals_bp
from app.api.users import bp as users_bp

# Register blueprints
bp.register_blueprint(auth_bp, url_prefix='/auth')
bp.register_blueprint(scooters_bp, url_prefix='/scooters')
bp.register_blueprint(rentals_bp, url_prefix='/rentals')
bp.register_blueprint(users_bp, url_prefix='/users')

from app.api import auth, scooters, rentals, users

# Export namespaces for documentation
from app.api.auth import auth_ns
from app.api.scooters import scooters_ns
from app.api.rentals import rentals_ns
from app.api.users import users_ns

__all__ = ['bp', 'auth_ns', 'scooters_ns', 'rentals_ns', 'users_ns']
