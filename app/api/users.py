"""
User API endpoints
"""

from flask import Blueprint, request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.auth_service import AuthService

# Flask Blueprint for API routes
bp = Blueprint('users_api', __name__)

# Flask-RESTX Namespace for documentation
users_ns = Namespace('users', description='User operations')

auth_service = AuthService()

user_model = users_ns.model('User', {
    'id': fields.Integer(description='User ID'),
    'email': fields.String(description='Email'),
    'first_name': fields.String(description='First name'),
    'last_name': fields.String(description='Last name'),
    'full_name': fields.String(description='Full name'),
    'role': fields.String(description='Role'),
    'is_active': fields.Boolean(description='Is active'),
    'created_at': fields.String(description='Created at')
})

update_profile_model = users_ns.model('UpdateProfile', {
    'first_name': fields.String(description='First name'),
    'last_name': fields.String(description='Last name'),
    'phone': fields.String(description='Phone number')
})

change_password_model = users_ns.model('ChangePassword', {
    'old_password': fields.String(required=True, description='Current password'),
    'new_password': fields.String(required=True, description='New password')
})

@users_ns.route('/')
class UserList(Resource):
    @jwt_required()
    @users_ns.response(200, 'Success')
    @users_ns.response(403, 'Forbidden')
    def get(self):
        """Get all users (admin only)"""
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if not user.is_admin():
            return {'message': 'Admin access required'}, 403
        
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        role = request.args.get('role')
        
        if role:
            users = auth_service.get_users_by_role(role, limit)
        else:
            users = auth_service.get_all_users(limit, offset)
        
        return [u.to_dict() for u in users]

@users_ns.route('/<int:user_id>')
class UserDetail(Resource):
    @jwt_required()
    @users_ns.response(200, 'Success')
    @users_ns.response(403, 'Forbidden')
    @users_ns.response(404, 'User not found')
    def get(self, user_id):
        """Get user by ID"""
        current_user_id = get_jwt_identity()
        current_user = auth_service.get_user_by_id(current_user_id)
        
        user = auth_service.get_user_by_id(user_id)
        
        if not user:
            return {'message': 'User not found'}, 404
        
        if not current_user.is_admin() and current_user_id != user_id:
            return {'message': 'Not authorized'}, 403
        
        include_sensitive = current_user.is_admin() or current_user_id == user_id
        
        return user.to_dict(include_sensitive=include_sensitive)

@users_ns.route('/me')
class CurrentUserProfile(Resource):
    @jwt_required()
    @users_ns.response(200, 'Success')
    def get(self):
        """Get current user profile"""
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        return user.to_dict(include_sensitive=True)
    
    @jwt_required()
    @users_ns.expect(update_profile_model)
    @users_ns.response(200, 'Profile updated')
    @users_ns.response(400, 'Validation error')
    def put(self):
        """Update current user profile"""
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        data = request.get_json()
        
        updated_user, error = auth_service.update_profile(user, **data)
        
        if error:
            return {'message': error}, 400
        
        return updated_user.to_dict(include_sensitive=True)

@users_ns.route('/me/password')
class ChangePassword(Resource):
    @jwt_required()
    @users_ns.expect(change_password_model)
    @users_ns.response(200, 'Password changed')
    @users_ns.response(400, 'Validation error')
    def put(self):
        """Change current user password"""
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        data = request.get_json()
        
        success, error = auth_service.change_password(
            user=user,
            old_password=data.get('old_password'),
            new_password=data.get('new_password')
        )
        
        if error:
            return {'message': error}, 400
        
        return {'message': 'Password changed successfully'}

@users_ns.route('/search')
class SearchUsers(Resource):
    @jwt_required()
    @users_ns.response(200, 'Success')
    @users_ns.response(403, 'Forbidden')
    def get(self):
        """Search users (admin only)"""
        current_user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(current_user_id)
        
        if not user.is_admin():
            return {'message': 'Admin access required'}, 403
        
        query = request.args.get('q', '')
        limit = request.args.get('limit', 50, type=int)
        
        users = auth_service.search_users(query, limit)
        
        return [u.to_dict() for u in users]

@users_ns.route('/<int:user_id>/activate')
class ActivateUser(Resource):
    @jwt_required()
    @users_ns.response(200, 'User activated')
    @users_ns.response(403, 'Forbidden')
    @users_ns.response(404, 'User not found')
    def post(self, user_id):
        """Activate user (admin only)"""
        current_user_id = get_jwt_identity()
        current_user = auth_service.get_user_by_id(current_user_id)
        
        if not current_user.is_admin():
            return {'message': 'Admin access required'}, 403
        
        user = auth_service.get_user_by_id(user_id)
        
        if not user:
            return {'message': 'User not found'}, 404
        
        auth_service.activate_user(user)
        
        return {'message': 'User activated successfully'}

@users_ns.route('/<int:user_id>/deactivate')
class DeactivateUser(Resource):
    @jwt_required()
    @users_ns.response(200, 'User deactivated')
    @users_ns.response(403, 'Forbidden')
    @users_ns.response(404, 'User not found')
    def post(self, user_id):
        """Deactivate user (admin only)"""
        current_user_id = get_jwt_identity()
        current_user = auth_service.get_user_by_id(current_user_id)
        
        if not current_user.is_admin():
            return {'message': 'Admin access required'}, 403
        
        user = auth_service.get_user_by_id(user_id)
        
        if not user:
            return {'message': 'User not found'}, 404
        
        auth_service.deactivate_user(user)
        
        return {'message': 'User deactivated successfully'}
