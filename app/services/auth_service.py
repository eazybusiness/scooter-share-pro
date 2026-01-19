"""
Authentication service for user management and authentication
"""

from typing import Optional, Tuple
from flask import current_app
from app.repositories.user_repository import UserRepository
from app.models.user import User

class AuthService:
    """Service for authentication and user management"""
    
    def __init__(self):
        self.user_repo = UserRepository()
    
    def register_user(self, email: str, password: str, first_name: str, 
                     last_name: str, role: str = 'customer', **kwargs) -> Tuple[Optional[User], Optional[str]]:
        """
        Register a new user
        Returns: (User, error_message)
        """
        if self.user_repo.exists(email):
            return None, 'User with this email already exists'
        
        if len(password) < 8:
            return None, 'Password must be at least 8 characters long'
        
        if role not in ['admin', 'provider', 'customer']:
            return None, 'Invalid role'
        
        try:
            user = self.user_repo.create(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                **kwargs
            )
            return user, None
        except Exception as e:
            return None, str(e)
    
    def login_user(self, email: str, password: str) -> Tuple[Optional[User], Optional[str]]:
        """
        Authenticate user with email and password
        Returns: (User, error_message)
        """
        user = self.user_repo.get_by_email(email)
        
        if not user:
            return None, 'Invalid email or password'
        
        if not user.is_active:
            return None, 'Account is deactivated'
        
        if not user.check_password(password):
            return None, 'Invalid email or password'
        
        user.update_last_login()
        return user, None
    
    def change_password(self, user: User, old_password: str, 
                       new_password: str) -> Tuple[bool, Optional[str]]:
        """
        Change user password
        Returns: (success, error_message)
        """
        if not user.check_password(old_password):
            return False, 'Current password is incorrect'
        
        if len(new_password) < 8:
            return False, 'New password must be at least 8 characters long'
        
        user.set_password(new_password)
        self.user_repo.update(user)
        return True, None
    
    def reset_password(self, email: str, new_password: str) -> Tuple[bool, Optional[str]]:
        """
        Reset user password (admin function)
        Returns: (success, error_message)
        """
        user = self.user_repo.get_by_email(email)
        
        if not user:
            return False, 'User not found'
        
        if len(new_password) < 8:
            return False, 'Password must be at least 8 characters long'
        
        user.set_password(new_password)
        self.user_repo.update(user)
        return True, None
    
    def update_profile(self, user: User, **kwargs) -> Tuple[Optional[User], Optional[str]]:
        """
        Update user profile
        Returns: (User, error_message)
        """
        allowed_fields = ['first_name', 'last_name', 'phone', 'email']
        
        update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not update_data:
            return None, 'No valid fields to update'
        
        # Check if email is being changed and if it already exists
        if 'email' in update_data and update_data['email'] != user.email:
            if self.user_repo.exists(update_data['email']):
                return None, 'Email address already in use'
        
        try:
            updated_user = self.user_repo.update(user, **update_data)
            return updated_user, None
        except Exception as e:
            return None, str(e)
    
    def deactivate_user(self, user: User) -> bool:
        """Deactivate user account"""
        return self.user_repo.delete(user)
    
    def activate_user(self, user: User) -> User:
        """Activate user account"""
        return self.user_repo.update(user, is_active=True)
    
    def verify_user(self, user: User) -> User:
        """Verify user account"""
        return self.user_repo.verify_user(user)
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.user_repo.get_by_id(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.user_repo.get_by_email(email)
    
    def search_users(self, query: str, limit: int = 50) -> list:
        """Search users"""
        return self.user_repo.search(query, limit)
    
    def get_all_users(self, limit: int = 100, offset: int = 0) -> list:
        """Get all users"""
        return self.user_repo.get_all(limit, offset)
    
    def get_users_by_role(self, role: str, limit: int = 100) -> list:
        """Get users by role"""
        return self.user_repo.get_by_role(role, limit)
    
    def promote_to_provider(self, user: User) -> Tuple[Optional[User], Optional[str]]:
        """Promote customer to provider"""
        if user.role == 'provider':
            return None, 'User is already a provider'
        
        if user.role == 'admin':
            return None, 'Cannot change admin role'
        
        updated_user = self.user_repo.update(user, role='provider')
        return updated_user, None
    
    def demote_to_customer(self, user: User) -> Tuple[Optional[User], Optional[str]]:
        """Demote provider to customer"""
        if user.role == 'customer':
            return None, 'User is already a customer'
        
        if user.role == 'admin':
            return None, 'Cannot change admin role'
        
        if user.scooters.count() > 0:
            return None, 'Provider has active scooters. Remove scooters first.'
        
        updated_user = self.user_repo.update(user, role='customer')
        return updated_user, None
    
    def validate_admin(self, user: User) -> bool:
        """Check if user is admin"""
        return user.is_admin()
    
    def validate_provider(self, user: User) -> bool:
        """Check if user is provider or admin"""
        return user.can_manage_scooters()
