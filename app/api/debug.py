"""
Debug API endpoints for troubleshooting
"""

from flask import jsonify, request
from flask_restx import Namespace, Resource
from app import db
from sqlalchemy import text
from flask_jwt_extended import jwt_required, get_jwt_identity

debug_ns = Namespace('debug', description='Debug endpoints')

@debug_ns.route('/ratings')
class RatingDebug(Resource):
    @jwt_required()
    def get(self):
        """Debug endpoint to check ratings in database"""
        try:
            # Get current user
            current_user_id = get_jwt_identity()
            
            # Check all rentals with feedback for this user
            result = db.session.execute(text("""
                SELECT id, rental_code, rating, feedback, status, created_at
                FROM rentals
                WHERE user_id = :user_id AND (feedback IS NOT NULL OR rating IS NOT NULL)
                ORDER BY created_at DESC
                LIMIT 10
            """), {'user_id': current_user_id})
            
            rentals = []
            for row in result:
                rentals.append({
                    'id': row.id,
                    'rental_code': row.rental_code,
                    'rating': row.rating,
                    'rating_type': str(type(row.rating)),
                    'feedback': row.feedback,
                    'status': row.status,
                    'created_at': row.created_at.isoformat() if row.created_at else None
                })
            
            # Check specific rental if provided
            rental_id = request.args.get('rental_id', type=int)
            specific_rental = None
            if rental_id:
                result = db.session.execute(text("""
                    SELECT id, rental_code, rating, feedback, status, user_id, scooter_id
                    FROM rentals
                    WHERE id = :rental_id AND user_id = :user_id
                """), {'rental_id': rental_id, 'user_id': current_user_id})
                
                row = result.first()
                if row:
                    specific_rental = {
                        'id': row.id,
                        'rental_code': row.rental_code,
                        'rating': row.rating,
                        'rating_type': str(type(row.rating)),
                        'feedback': row.feedback,
                        'status': row.status,
                        'user_id': row.user_id,
                        'scooter_id': row.scooter_id
                    }
            
            return jsonify({
                'user_rentals_with_ratings': rentals,
                'specific_rental': specific_rental,
                'message': 'Debug data retrieved successfully'
            })
            
        except Exception as e:
            return jsonify({
                'error': str(e),
                'message': 'Failed to retrieve debug data'
            }), 500

@debug_ns.route('/rating-test')
class RatingTest(Resource):
    @jwt_required()
    def post(self):
        """Test endpoint to simulate rating submission"""
        try:
            from app.services.rental_service import RentalService
            
            rental_service = RentalService()
            current_user_id = get_jwt_identity()
            
            # Get a completed rental for this user
            result = db.session.execute(text("""
                SELECT id FROM rentals 
                WHERE user_id = :user_id AND status = 'completed' AND rating IS NULL
                LIMIT 1
            """), {'user_id': current_user_id})
            
            row = result.first()
            if not row:
                return jsonify({
                    'message': 'No completed rental found without rating'
                }), 400
            
            # Add a test rating
            success, error = rental_service.add_rating(row.id, 5, "Test rating from debug endpoint")
            
            if error:
                return jsonify({
                    'error': error,
                    'rental_id': row.id
                }), 400
            
            return jsonify({
                'message': 'Test rating added successfully',
                'rental_id': row.id,
                'rating': 5,
                'feedback': 'Test rating from debug endpoint'
            })
            
        except Exception as e:
            return jsonify({
                'error': str(e),
                'message': 'Failed to add test rating'
            }), 500
