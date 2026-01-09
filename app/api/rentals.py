"""
Rental API endpoints
"""

from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.rental_service import RentalService
from app.services.auth_service import AuthService

rentals_ns = Namespace('rentals', description='Rental operations')

rental_service = RentalService()
auth_service = AuthService()

rental_model = rentals_ns.model('Rental', {
    'id': fields.Integer(description='Rental ID'),
    'rental_code': fields.String(description='Rental code'),
    'user_id': fields.Integer(description='User ID'),
    'scooter_id': fields.Integer(description='Scooter ID'),
    'status': fields.String(description='Status'),
    'start_time': fields.String(description='Start time'),
    'end_time': fields.String(description='End time'),
    'duration_minutes': fields.Integer(description='Duration in minutes'),
    'total_cost': fields.Float(description='Total cost')
})

start_rental_model = rentals_ns.model('StartRental', {
    'scooter_id': fields.Integer(required=True, description='Scooter ID'),
    'start_latitude': fields.Float(required=True, description='Start latitude'),
    'start_longitude': fields.Float(required=True, description='Start longitude')
})

end_rental_model = rentals_ns.model('EndRental', {
    'end_latitude': fields.Float(description='End latitude'),
    'end_longitude': fields.Float(description='End longitude')
})

rating_model = rentals_ns.model('Rating', {
    'rating': fields.Integer(required=True, description='Rating (1-5)', min=1, max=5),
    'feedback': fields.String(description='Feedback text')
})

@rentals_ns.route('/')
class RentalList(Resource):
    @jwt_required()
    @rentals_ns.response(200, 'Success')
    def get(self):
        """Get rentals"""
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        limit = request.args.get('limit', 100, type=int)
        status = request.args.get('status')
        
        if user.is_admin():
            if status:
                rentals = rental_service.rental_repo.get_by_status(status, limit)
            else:
                rentals = rental_service.get_all_rentals(limit)
        else:
            rentals = rental_service.get_user_rentals(current_user_id, limit)
            if status:
                rentals = [r for r in rentals if r.status == status]
        
        return [r.to_dict() for r in rentals]
    
    @jwt_required()
    @rentals_ns.expect(start_rental_model)
    @rentals_ns.response(201, 'Rental started')
    @rentals_ns.response(400, 'Validation error')
    def post(self):
        """Start a new rental"""
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        rental, error = rental_service.start_rental(
            user_id=current_user_id,
            scooter_id=data.get('scooter_id'),
            start_latitude=data.get('start_latitude'),
            start_longitude=data.get('start_longitude')
        )
        
        if error:
            return {'message': error}, 400
        
        return rental.to_dict(include_sensitive=True), 201

@rentals_ns.route('/<int:rental_id>')
class RentalDetail(Resource):
    @jwt_required()
    @rentals_ns.response(200, 'Success')
    @rentals_ns.response(403, 'Forbidden')
    @rentals_ns.response(404, 'Rental not found')
    def get(self, rental_id):
        """Get rental by ID"""
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        rental = rental_service.get_rental_by_id(rental_id)
        
        if not rental:
            return {'message': 'Rental not found'}, 404
        
        if not rental_service.validate_rental_access(rental, user):
            return {'message': 'Not authorized to access this rental'}, 403
        
        include_sensitive = user.is_admin() or rental.user_id == user.id
        
        return rental.to_dict(include_sensitive=include_sensitive)

@rentals_ns.route('/<int:rental_id>/end')
class EndRental(Resource):
    @jwt_required()
    @rentals_ns.expect(end_rental_model)
    @rentals_ns.response(200, 'Rental ended')
    @rentals_ns.response(400, 'Validation error')
    @rentals_ns.response(403, 'Forbidden')
    @rentals_ns.response(404, 'Rental not found')
    def post(self, rental_id):
        """End an active rental"""
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        rental = rental_service.get_rental_by_id(rental_id)
        
        if not rental:
            return {'message': 'Rental not found'}, 404
        
        if not rental_service.can_end_rental(rental, user):
            return {'message': 'Not authorized to end this rental'}, 403
        
        data = request.get_json() or {}
        
        rental, error = rental_service.end_rental(
            rental_id=rental_id,
            end_latitude=data.get('end_latitude'),
            end_longitude=data.get('end_longitude')
        )
        
        if error:
            return {'message': error}, 400
        
        return rental.to_dict(include_sensitive=True)

@rentals_ns.route('/<int:rental_id>/cancel')
class CancelRental(Resource):
    @jwt_required()
    @rentals_ns.response(200, 'Rental cancelled')
    @rentals_ns.response(400, 'Validation error')
    @rentals_ns.response(403, 'Forbidden')
    @rentals_ns.response(404, 'Rental not found')
    def post(self, rental_id):
        """Cancel an active rental"""
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        rental = rental_service.get_rental_by_id(rental_id)
        
        if not rental:
            return {'message': 'Rental not found'}, 404
        
        if not user.is_admin() and rental.user_id != user.id:
            return {'message': 'Not authorized to cancel this rental'}, 403
        
        data = request.get_json() or {}
        reason = data.get('reason')
        
        rental, error = rental_service.cancel_rental(rental_id, reason)
        
        if error:
            return {'message': error}, 400
        
        return rental.to_dict(include_sensitive=True)

@rentals_ns.route('/<int:rental_id>/rating')
class RateRental(Resource):
    @jwt_required()
    @rentals_ns.expect(rating_model)
    @rentals_ns.response(200, 'Rating added')
    @rentals_ns.response(400, 'Validation error')
    @rentals_ns.response(403, 'Forbidden')
    @rentals_ns.response(404, 'Rental not found')
    def post(self, rental_id):
        """Add rating to a completed rental"""
        current_user_id = get_jwt_identity()
        
        rental = rental_service.get_rental_by_id(rental_id)
        
        if not rental:
            return {'message': 'Rental not found'}, 404
        
        if rental.user_id != current_user_id:
            return {'message': 'Not authorized to rate this rental'}, 403
        
        data = request.get_json()
        
        success, error = rental_service.add_rating(
            rental_id=rental_id,
            rating=data.get('rating'),
            feedback=data.get('feedback')
        )
        
        if error:
            return {'message': error}, 400
        
        return {'message': 'Rating added successfully'}

@rentals_ns.route('/active')
class ActiveRentals(Resource):
    @jwt_required()
    @rentals_ns.response(200, 'Success')
    def get(self):
        """Get active rentals"""
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if user.is_admin():
            rentals = rental_service.get_active_rentals()
        else:
            rental = rental_service.get_active_rental_for_user(current_user_id)
            rentals = [rental] if rental else []
        
        return [r.to_dict() for r in rentals]

@rentals_ns.route('/statistics')
class RentalStatistics(Resource):
    @jwt_required()
    @rentals_ns.response(200, 'Success')
    @rentals_ns.response(403, 'Forbidden')
    def get(self):
        """Get rental statistics"""
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if not user.is_admin():
            return {'message': 'Admin access required'}, 403
        
        stats = rental_service.get_rental_statistics()
        
        return stats
