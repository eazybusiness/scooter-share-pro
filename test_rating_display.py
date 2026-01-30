"""
Test script to check rental rating display
"""

from app import create_app, db
from app.models.rental import Rental

app = create_app('production')

with app.app_context():
    # Get rental 13
    rental = Rental.query.get(13)
    if rental:
        print(f"Rental ID: {rental.id}")
        print(f"User ID: {rental.user_id}")
        print(f"Rating: {rental.rating} (type: {type(rental.rating)})")
        print(f"Feedback: {rental.feedback}")
        print(f"Status: {rental.status}")
        
        # Check if rating evaluates to True in Jinja2
        print(f"\nJinja2 truthiness test:")
        print(f"  {% if rental.rating %} would be: {bool(rental.rating)}")
        print(f"  rental.rating is not none: {rental.rating is not None}")
        print(f"  rental.rating > 0: {rental.rating > 0 if rental.rating else False}")
    else:
        print("Rental 13 not found")
