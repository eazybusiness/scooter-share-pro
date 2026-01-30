"""
API Blueprint for RESTful endpoints
"""

from flask import Blueprint
from flask_restx import Api

bp = Blueprint('api', __name__)

# Import and register API routes
from .auth import auth_ns
from .scooters import scooters_ns
from .rentals import rentals_ns
from .users import users_ns
from .debug import debug_ns

# Create API instance
api = Api(
    version='1.0',
    title='Scooter Share Pro API',
    description='Enterprise E-Scooter Rental Platform API',
    doc='/api/docs/'
)

# Register all namespaces
api.add_namespace(auth_ns, path='/auth')
api.add_namespace(scooters_ns, path='/scooters')
api.add_namespace(rentals_ns, path='/rentals')
api.add_namespace(users_ns, path='/users')
api.add_namespace(debug_ns, path='/debug')

from app.api import auth, scooters, rentals, users

# Export namespaces for documentation
from app.api.auth import auth_ns
from app.api.scooters import scooters_ns
from app.api.rentals import rentals_ns
from app.api.users import users_ns
from app.api.debug import debug_ns

__all__ = ['bp', 'auth_ns', 'scooters_ns', 'rentals_ns', 'users_ns', 'debug_ns']
