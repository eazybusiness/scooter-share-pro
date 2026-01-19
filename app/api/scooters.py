"""
Scooter API endpoints
"""

from flask import Blueprint, request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.scooter_service import ScooterService
from app.services.auth_service import AuthService

# Flask Blueprint for API routes
bp = Blueprint('scooters_api', __name__)

# Flask-RESTX Namespace for documentation
scooters_ns = Namespace('scooters', description='Scooter operations')

scooter_service = ScooterService()
auth_service = AuthService()

scooter_model = scooters_ns.model('Scooter', {
    'id': fields.Integer(description='Scooter ID'),
    'identifier': fields.String(required=True, description='Scooter identifier'),
    'model': fields.String(required=True, description='Scooter model'),
    'brand': fields.String(required=True, description='Scooter brand'),
    'latitude': fields.Float(required=True, description='Latitude'),
    'longitude': fields.Float(required=True, description='Longitude'),
    'address': fields.String(description='Address'),
    'status': fields.String(description='Status'),
    'battery_level': fields.Integer(description='Battery level'),
    'is_available': fields.Boolean(description='Is available')
})

create_scooter_model = scooters_ns.model('CreateScooter', {
    'identifier': fields.String(required=True, description='Scooter identifier'),
    'model': fields.String(required=True, description='Scooter model'),
    'brand': fields.String(required=True, description='Scooter brand'),
    'latitude': fields.Float(required=True, description='Latitude'),
    'longitude': fields.Float(required=True, description='Longitude'),
    'address': fields.String(description='Address'),
    'battery_level': fields.Integer(description='Battery level'),
    'max_speed': fields.Integer(description='Max speed in km/h'),
    'range_km': fields.Integer(description='Range in km')
})

update_location_model = scooters_ns.model('UpdateLocation', {
    'latitude': fields.Float(required=True, description='Latitude'),
    'longitude': fields.Float(required=True, description='Longitude'),
    'address': fields.String(description='Address')
})

@scooters_ns.route('/')
class ScooterList(Resource):
    @jwt_required()
    @scooters_ns.response(200, 'Success')
    def get(self):
        """Get all scooters"""
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        status = request.args.get('status')
        
        if status:
            scooters = scooter_service.scooter_repo.get_by_status(status, limit)
        else:
            scooters = scooter_service.get_all_scooters(limit, offset)
        
        return [s.to_dict() for s in scooters]
    
    @jwt_required()
    @scooters_ns.expect(create_scooter_model)
    @scooters_ns.response(201, 'Scooter created')
    @scooters_ns.response(400, 'Validation error')
    @scooters_ns.response(403, 'Forbidden')
    def post(self):
        """Create a new scooter"""
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if not user.can_manage_scooters():
            return {'message': 'Not authorized to create scooters'}, 403
        
        data = request.get_json()
        
        scooter, error = scooter_service.create_scooter(
            identifier=data.get('identifier'),
            model=data.get('model'),
            brand=data.get('brand'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            provider_id=current_user_id,
            address=data.get('address'),
            battery_level=data.get('battery_level', 100),
            max_speed=data.get('max_speed'),
            range_km=data.get('range_km')
        )
        
        if error:
            return {'message': error}, 400
        
        return scooter.to_dict(include_sensitive=True), 201

@scooters_ns.route('/<int:scooter_id>')
class ScooterDetail(Resource):
    @jwt_required()
    @scooters_ns.response(200, 'Success')
    @scooters_ns.response(404, 'Scooter not found')
    def get(self, scooter_id):
        """Get scooter by ID"""
        scooter = scooter_service.get_scooter_by_id(scooter_id)
        
        if not scooter:
            return {'message': 'Scooter not found'}, 404
        
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        include_sensitive = user.is_admin() or scooter.provider_id == user.id
        
        return scooter.to_dict(include_sensitive=include_sensitive)
    
    @jwt_required()
    @scooters_ns.response(200, 'Scooter updated')
    @scooters_ns.response(403, 'Forbidden')
    @scooters_ns.response(404, 'Scooter not found')
    def put(self, scooter_id):
        """Update scooter"""
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        scooter = scooter_service.get_scooter_by_id(scooter_id)
        if not scooter:
            return {'message': 'Scooter not found'}, 404
        
        data = request.get_json()
        
        updated_scooter, error = scooter_service.update_scooter(scooter, user, **data)
        
        if error:
            return {'message': error}, 403
        
        return updated_scooter.to_dict(include_sensitive=True)
    
    @jwt_required()
    @scooters_ns.response(200, 'Scooter deleted')
    @scooters_ns.response(403, 'Forbidden')
    @scooters_ns.response(404, 'Scooter not found')
    def delete(self, scooter_id):
        """Delete scooter"""
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        scooter = scooter_service.get_scooter_by_id(scooter_id)
        if not scooter:
            return {'message': 'Scooter not found'}, 404
        
        success, error = scooter_service.delete_scooter(scooter, user)
        
        if error:
            return {'message': error}, 403
        
        return {'message': 'Scooter deleted successfully'}

@scooters_ns.route('/available')
class AvailableScooters(Resource):
    @jwt_required()
    @scooters_ns.response(200, 'Success')
    def get(self):
        """Get available scooters"""
        limit = request.args.get('limit', 100, type=int)
        scooters = scooter_service.get_available_scooters(limit)
        
        return [s.to_dict() for s in scooters]

@scooters_ns.route('/nearby')
class NearbyScooters(Resource):
    @jwt_required()
    @scooters_ns.response(200, 'Success')
    @scooters_ns.response(400, 'Missing parameters')
    def get(self):
        """Get nearby scooters"""
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        radius = request.args.get('radius', 5.0, type=float)
        limit = request.args.get('limit', 50, type=int)
        
        if latitude is None or longitude is None:
            return {'message': 'Latitude and longitude are required'}, 400
        
        scooters = scooter_service.get_nearby_scooters(latitude, longitude, radius, limit)
        
        return [s.to_dict() for s in scooters]

@scooters_ns.route('/<int:scooter_id>/location')
class UpdateScooterLocation(Resource):
    @jwt_required()
    @scooters_ns.expect(update_location_model)
    @scooters_ns.response(200, 'Location updated')
    @scooters_ns.response(403, 'Forbidden')
    @scooters_ns.response(404, 'Scooter not found')
    def put(self, scooter_id):
        """Update scooter location"""
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        scooter = scooter_service.get_scooter_by_id(scooter_id)
        if not scooter:
            return {'message': 'Scooter not found'}, 404
        
        if not user.is_admin() and scooter.provider_id != user.id:
            return {'message': 'Not authorized'}, 403
        
        data = request.get_json()
        
        success, error = scooter_service.update_location(
            scooter,
            data.get('latitude'),
            data.get('longitude'),
            data.get('address')
        )
        
        if error:
            return {'message': error}, 400
        
        return {'message': 'Location updated successfully'}

@scooters_ns.route('/<int:scooter_id>/status')
class UpdateScooterStatus(Resource):
    @jwt_required()
    @scooters_ns.response(200, 'Status updated')
    @scooters_ns.response(403, 'Forbidden')
    @scooters_ns.response(404, 'Scooter not found')
    def put(self, scooter_id):
        """Update scooter status"""
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        scooter = scooter_service.get_scooter_by_id(scooter_id)
        if not scooter:
            return {'message': 'Scooter not found'}, 404
        
        data = request.get_json()
        status = data.get('status')
        
        success, error = scooter_service.set_status(scooter, status, user)
        
        if error:
            return {'message': error}, 403
        
        return {'message': 'Status updated successfully'}
