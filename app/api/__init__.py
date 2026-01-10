"""
API Blueprint for RESTful endpoints
"""

from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import auth, scooters, rentals, users

# Export namespaces for registration
from app.api.auth import auth_ns
from app.api.scooters import scooters_ns
from app.api.rentals import rentals_ns
from app.api.users import users_ns

__all__ = ['bp', 'auth_ns', 'scooters_ns', 'rentals_ns', 'users_ns']
