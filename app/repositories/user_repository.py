"""
User repository for data access operations
"""

from typing import List, Optional
from app import db
from app.models.user import User

class UserRepository:
    """Repository for User model data access"""
    
    @staticmethod
    def create(email: str, password: str, first_name: str, last_name: str, 
               role: str = 'customer', **kwargs) -> User:
        """Create a new user"""
        user = User(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        
        if 'phone' in kwargs:
            user.phone = kwargs['phone']
        
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def get_by_id(user_id: int) -> Optional[User]:
        """Get user by ID"""
        return User.query.get(user_id)
    
    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        """Get user by email"""
        return User.query.filter_by(email=email.lower()).first()
    
    @staticmethod
    def get_all(limit: int = 100, offset: int = 0) -> List[User]:
        """Get all users with pagination"""
        return User.query.limit(limit).offset(offset).all()
    
    @staticmethod
    def get_by_role(role: str, limit: int = 100) -> List[User]:
        """Get users by role"""
        return User.query.filter_by(role=role).limit(limit).all()
    
    @staticmethod
    def get_active_users(limit: int = 100) -> List[User]:
        """Get active users"""
        return User.query.filter_by(is_active=True).limit(limit).all()
    
    @staticmethod
    def update(user: User, **kwargs) -> User:
        """Update user attributes"""
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        db.session.commit()
        return user
    
    @staticmethod
    def delete(user: User) -> bool:
        """Delete user (soft delete by setting is_active=False)"""
        user.is_active = False
        db.session.commit()
        return True
    
    @staticmethod
    def hard_delete(user: User) -> bool:
        """Permanently delete user"""
        db.session.delete(user)
        db.session.commit()
        return True
    
    @staticmethod
    def search(query: str, limit: int = 50) -> List[User]:
        """Search users by email, first name, or last name"""
        search_pattern = f"%{query}%"
        return User.query.filter(
            db.or_(
                User.email.ilike(search_pattern),
                User.first_name.ilike(search_pattern),
                User.last_name.ilike(search_pattern)
            )
        ).limit(limit).all()
    
    @staticmethod
    def count_by_role(role: str) -> int:
        """Count users by role"""
        return User.query.filter_by(role=role).count()
    
    @staticmethod
    def get_providers_with_scooters() -> List[User]:
        """Get providers who have scooters"""
        return User.query.filter(
            User.role == 'provider',
            User.scooters.any()
        ).all()
    
    @staticmethod
    def verify_user(user: User) -> User:
        """Mark user as verified"""
        user.is_verified = True
        db.session.commit()
        return user
    
    @staticmethod
    def exists(email: str) -> bool:
        """Check if user exists by email"""
        return User.query.filter_by(email=email.lower()).count() > 0
