"""
Web Blueprint for browser-based interface
"""

from flask import Blueprint

bp = Blueprint('web', __name__)

from app.web import auth, dashboard, rentals, scooters, debug_ratings
