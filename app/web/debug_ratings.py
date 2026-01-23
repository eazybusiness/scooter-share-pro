"""
Debug endpoint to check ratings in database
"""

from flask import jsonify, request
from app.web import bp
from app import db
from app.models.rental import Rental


@bp.route('/debug/ratings')
def debug_ratings():
    """Debug endpoint to check ratings data"""
    
    # Get specific rentals
    rentals_13_14 = db.session.query(Rental).filter(Rental.id.in_([13, 14])).all()
    
    result = {
        'rentals_13_14': [],
        'all_with_feedback': []
    }
    
    for rental in rentals_13_14:
        result['rentals_13_14'].append({
            'id': rental.id,
            'rental_code': rental.rental_code,
            'rating': rental.rating,
            'feedback': rental.feedback,
            'status': rental.status,
            'user_id': rental.user_id,
            'scooter_id': rental.scooter_id
        })
    
    # Get all rentals with feedback
    all_feedback = db.session.query(Rental).filter(
        (Rental.feedback.isnot(None)) | (Rental.rating.isnot(None))
    ).limit(10).all()
    
    for rental in all_feedback:
        result['all_with_feedback'].append({
            'id': rental.id,
            'rental_code': rental.rental_code,
            'rating': rental.rating,
            'feedback': rental.feedback[:100] + ('...' if rental.feedback and len(rental.feedback) > 100 else ''),
            'status': rental.status
        })
    
    return jsonify(result)
