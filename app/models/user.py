"""
User model for Scooter Share Pro
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    """User model with authentication and authorization"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    
    # Role-based access control
    role = db.Column(db.Enum('admin', 'provider', 'customer', name='user_roles'), 
                     default='customer', nullable=False)
    
    # Account status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                          onupdate=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    scooters = db.relationship('Scooter', backref='provider', lazy='dynamic',
                              cascade='all, delete-orphan')
    rentals = db.relationship('Rental', backref='user', lazy='dynamic',
                              cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='user', lazy='dynamic',
                               cascade='all, delete-orphan')
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_user_email_active', 'email', 'is_active'),
        db.Index('idx_user_role_created', 'role', 'created_at'),
    )
    
    def __init__(self, email, password, first_name, last_name, role='customer'):
        self.email = email.lower()
        self.set_password(password)
        self.first_name = first_name.title()
        self.last_name = last_name.title()
        self.role = role
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def get_full_name(self):
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def is_provider(self):
        """Check if user is a provider"""
        return self.role == 'provider'
    
    def is_admin(self):
        """Check if user is an admin"""
        return self.role == 'admin'
    
    def can_manage_scooters(self):
        """Check if user can manage scooters"""
        return self.role in ['admin', 'provider']
    
    def get_active_rentals(self):
        """Get currently active rentals"""
        return self.rentals.filter_by(status='active').all()
    
    def get_rental_history(self, limit=10):
        """Get rental history"""
        return self.rentals.order_by(Rental.created_at.desc()).limit(limit).all()
    
    def get_total_spent(self):
        """Calculate total amount spent on rentals"""
        from sqlalchemy import func
        result = db.session.query(func.sum(Payment.amount))\
                          .join(Rental, Payment.rental_id == Rental.id)\
                          .filter(Rental.user_id == self.id)\
                          .scalar()
        return float(result) if result else 0.0
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'role': self.role,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        
        if include_sensitive:
            data.update({
                'phone': self.phone,
                'scooter_count': self.scooters.count(),
                'rental_count': self.rentals.count(),
                'total_spent': self.get_total_spent()
            })
        
        return data
    
    def __repr__(self):
        return f'<User {self.email}>'
