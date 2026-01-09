"""
Rental model for Scooter Share Pro
"""

from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from app import db
from app.models.payment import Payment

class Rental(db.Model):
    """Rental model tracking scooter usage and billing"""
    __tablename__ = 'rentals'
    
    id = db.Column(db.Integer, primary_key=True)
    rental_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Rental relationships
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    scooter_id = db.Column(db.Integer, db.ForeignKey('scooters.id'), nullable=False)
    
    # Timing information
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Integer, default=0)
    
    # Location tracking
    start_latitude = db.Column(db.Numeric(10, 8), nullable=False)
    start_longitude = db.Column(db.Numeric(11, 8), nullable=False)
    end_latitude = db.Column(db.Numeric(10, 8))
    end_longitude = db.Column(db.Numeric(11, 8))
    
    # Status tracking
    status = db.Column(db.Enum('active', 'completed', 'cancelled', 'overdue', 
                              name='rental_status'), 
                      default='active', nullable=False, index=True)
    
    # Pricing information
    base_fee = db.Column(db.Numeric(10, 2), default=0.00)
    per_minute_rate = db.Column(db.Numeric(10, 2), default=0.25)
    total_cost = db.Column(db.Numeric(10, 2), default=0.00)
    
    # Additional information
    notes = db.Column(db.Text)
    rating = db.Column(db.Integer)  # 1-5 stars
    feedback = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                          onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    payments = db.relationship('Payment', backref='rental', lazy='dynamic',
                              cascade='all, delete-orphan')
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_rental_user_status', 'user_id', 'status'),
        db.Index('idx_rental_scooter_status', 'scooter_id', 'status'),
        db.Index('idx_rental_time_range', 'start_time', 'end_time'),
        db.CheckConstraint('duration_minutes >= 0', name='check_duration_positive'),
        db.CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
    )
    
    def __init__(self, user_id, scooter_id, start_latitude, start_longitude):
        self.user_id = user_id
        self.scooter_id = scooter_id
        self.start_latitude = start_latitude
        self.start_longitude = start_longitude
        self.start_time = datetime.utcnow()
        self.rental_code = self.generate_rental_code()
        
        # Set default pricing (can be overridden)
        from flask import current_app
        self.base_fee = current_app.config.get('START_FEE', 1.0)
        self.per_minute_rate = current_app.config.get('BASE_PRICE_PER_MINUTE', 0.25)
    
    def generate_rental_code(self):
        """Generate unique rental code"""
        import uuid
        return f"R-{uuid.uuid4().hex[:8].upper()}"
    
    def start_rental(self):
        """Start the rental process"""
        from app.models.scooter import Scooter
        
        scooter = Scooter.query.get(self.scooter_id)
        if not scooter or not scooter.is_available():
            raise ValueError("Scooter is not available for rental")
        
        scooter.set_status('in_use')
        self.status = 'active'
        db.session.commit()
    
    def end_rental(self, end_latitude=None, end_longitude=None):
        """End the rental and calculate costs"""
        from app.models.scooter import Scooter
        
        if self.status != 'active':
            raise ValueError("Rental is not active")
        
        # Update timing
        self.end_time = datetime.utcnow()
        self.duration_minutes = int((self.end_time - self.start_time).total_seconds() / 60)
        
        # Update end location
        if end_latitude and end_longitude:
            self.end_latitude = end_latitude
            self.end_longitude = end_longitude
            
            # Update scooter location
            scooter = Scooter.query.get(self.scooter_id)
            scooter.update_location(end_latitude, end_longitude)
        
        # Calculate total cost
        self.calculate_cost()
        
        # Update status
        self.status = 'completed'
        
        # Make scooter available again
        scooter = Scooter.query.get(self.scooter_id)
        scooter.set_status('available')
        
        db.session.commit()
    
    def calculate_cost(self):
        """Calculate total rental cost"""
        if self.duration_minutes <= 0:
            self.total_cost = self.base_fee
        else:
            self.total_cost = self.base_fee + (self.duration_minutes * self.per_minute_rate)
    
    def cancel_rental(self, reason=None):
        """Cancel an active rental"""
        if self.status != 'active':
            raise ValueError("Only active rentals can be cancelled")
        
        from app.models.scooter import Scooter
        
        # Update timing
        self.end_time = datetime.utcnow()
        self.duration_minutes = int((self.end_time - self.start_time).total_seconds() / 60)
        
        # Calculate partial cost (cancellation fee)
        self.total_cost = self.base_fee  # Only charge base fee for cancellation
        self.notes = reason or "Cancelled by user"
        self.status = 'cancelled'
        
        # Make scooter available again
        scooter = Scooter.query.get(self.scooter_id)
        scooter.set_status('available')
        
        db.session.commit()
    
    def is_overdue(self):
        """Check if rental is overdue"""
        from flask import current_app
        
        max_hours = current_app.config.get('MAX_RENTAL_TIME_HOURS', 24)
        max_time = self.start_time + timedelta(hours=max_hours)
        
        return self.status == 'active' and datetime.utcnow() > max_time
    
    def check_overdue_status(self):
        """Check and update overdue status"""
        if self.is_overdue():
            self.status = 'overdue'
            db.session.commit()
            return True
        return False
    
    def add_rating(self, rating, feedback=None):
        """Add rating and feedback for completed rental"""
        if self.status != 'completed':
            raise ValueError("Only completed rentals can be rated")
        
        if not (1 <= rating <= 5):
            raise ValueError("Rating must be between 1 and 5")
        
        self.rating = rating
        self.feedback = feedback
        db.session.commit()
    
    def get_payment_status(self):
        """Check payment status"""
        paid_amount = sum(p.amount for p in self.payments if p.status == 'completed')
        return {
            'total_cost': float(self.total_cost),
            'paid_amount': float(paid_amount),
            'outstanding': float(self.total_cost - paid_amount),
            'is_fully_paid': paid_amount >= self.total_cost
        }
    
    def get_duration_minutes(self):
        """Get current duration in minutes for active rentals"""
        if self.status == 'active':
            # Calculate live duration for active rentals
            return int((datetime.utcnow() - self.start_time).total_seconds() / 60)
        else:
            # Return stored duration for completed/cancelled rentals
            return self.duration_minutes or 0
    
    def get_duration_formatted(self):
        """Get formatted duration string"""
        minutes = self.get_duration_minutes()
        if minutes < 60:
            return f"{minutes} minutes"
        else:
            hours = minutes // 60
            mins = minutes % 60
            return f"{hours}h {mins}m"
    
    def to_dict(self, include_sensitive=False):
        """Convert rental to dictionary"""
        data = {
            'id': self.id,
            'rental_code': self.rental_code,
            'user_id': self.user_id,
            'scooter_id': self.scooter_id,
            'status': self.status,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_minutes': self.duration_minutes,
            'duration_formatted': self.get_duration_formatted(),
            'start_location': {
                'latitude': float(self.start_latitude),
                'longitude': float(self.start_longitude)
            },
            'total_cost': float(self.total_cost),
            'created_at': self.created_at.isoformat()
        }
        
        if self.end_latitude and self.end_longitude:
            data['end_location'] = {
                'latitude': float(self.end_latitude),
                'longitude': float(self.end_longitude)
            }
        
        if include_sensitive:
            data.update({
                'base_fee': float(self.base_fee),
                'per_minute_rate': float(self.per_minute_rate),
                'rating': self.rating,
                'feedback': self.feedback,
                'notes': self.notes,
                'user_name': self.user.get_full_name(),
                'scooter_identifier': self.scooter.identifier,
                'scooter_model': f"{self.scooter.brand} {self.scooter.model}",
                'payment_status': self.get_payment_status(),
                'is_overdue': self.is_overdue()
            })
        
        return data
    
    def __repr__(self):
        return f'<Rental {self.rental_code}>'
