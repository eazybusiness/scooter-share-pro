"""
Scooter model for Scooter Share Pro
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import db

class Scooter(db.Model):
    """Scooter model with location and status tracking"""
    __tablename__ = 'scooters'
    
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(20), unique=True, nullable=False, index=True)
    model = db.Column(db.String(50), nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    
    # Location information
    latitude = db.Column(db.Numeric(10, 8), nullable=False)
    longitude = db.Column(db.Numeric(11, 8), nullable=False)
    address = db.Column(db.String(255))
    last_location_update = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Status management
    status = db.Column(db.Enum('available', 'in_use', 'maintenance', 'offline', 
                              name='scooter_status'), 
                      default='available', nullable=False, index=True)
    battery_level = db.Column(db.Integer, default=100, nullable=False)  # 0-100%
    
    # Technical specifications
    max_speed = db.Column(db.Integer)  # km/h
    range_km = db.Column(db.Integer)   # km on full battery
    
    # QR code for rental
    qr_code = db.Column(db.String(255), unique=True, nullable=False)
    
    # Provider relationship
    provider_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                          onupdate=datetime.utcnow, nullable=False)
    last_maintenance = db.Column(db.DateTime)
    
    # Relationships
    rentals = db.relationship('Rental', backref='scooter', lazy='dynamic',
                              cascade='all, delete-orphan')
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_scooter_status_location', 'status', 'latitude', 'longitude'),
        db.Index('idx_scooter_provider_status', 'provider_id', 'status'),
        db.Index('idx_scooter_battery', 'battery_level'),
        db.CheckConstraint('battery_level >= 0 AND battery_level <= 100', 
                          name='check_battery_level'),
    )
    
    def __init__(self, identifier, model, brand, latitude, longitude, provider_id):
        self.identifier = identifier.upper()
        self.model = model.title()
        self.brand = brand.title()
        self.latitude = latitude
        self.longitude = longitude
        self.provider_id = provider_id
        self.qr_code = self.generate_qr_code()
    
    def generate_qr_code(self):
        """Generate unique QR code for scooter"""
        import uuid
        return f"SCOOT-{uuid.uuid4().hex[:8].upper()}-{self.identifier}"
    
    def update_location(self, latitude, longitude, address=None):
        """Update scooter location"""
        self.latitude = latitude
        self.longitude = longitude
        if address:
            self.address = address
        self.last_location_update = datetime.utcnow()
        db.session.commit()
    
    def set_status(self, status):
        """Update scooter status with validation"""
        valid_statuses = ['available', 'in_use', 'maintenance', 'offline']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}")
        
        self.status = status
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def is_available(self):
        """Check if scooter is available for rental"""
        return self.status == 'available' and self.battery_level > 10
    
    def needs_maintenance(self):
        """Check if scooter needs maintenance"""
        return (self.battery_level < 20 or 
                (self.last_maintenance and 
                 (datetime.utcnow() - self.last_maintenance).days > 30))
    
    def get_current_rental(self):
        """Get currently active rental"""
        return self.rentals.filter_by(status='active').first()
    
    def get_rental_history(self, limit=10):
        """Get rental history"""
        return self.rentals.order_by(db.desc('created_at')).limit(limit).all()
    
    def get_total_revenue(self):
        """Calculate total revenue from this scooter"""
        from sqlalchemy import func
        from app.models.payment import Payment
        
        result = db.session.query(func.sum(Payment.amount))\
                          .join(Rental, Payment.rental_id == Rental.id)\
                          .filter(Rental.scooter_id == self.id)\
                          .scalar()
        return float(result) if result else 0.0
    
    def get_utilization_rate(self, days=30):
        """Calculate utilization rate for last N days"""
        from datetime import timedelta
        from sqlalchemy import func
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Calculate total minutes used in the period
        result = db.session.query(func.sum(Rental.duration_minutes))\
                          .filter(Rental.scooter_id == self.id)\
                          .filter(Rental.start_time >= start_date)\
                          .filter(Rental.status == 'completed')\
                          .scalar()
        
        total_minutes_used = int(result) if result else 0
        total_possible_minutes = days * 24 * 60  # Total minutes in the period
        
        return (total_minutes_used / total_possible_minutes) * 100 if total_possible_minutes > 0 else 0
    
    def distance_from(self, latitude, longitude):
        """Calculate distance from given coordinates (in kilometers)"""
        from math import radians, cos, sin, asin, sqrt
        
        lat1, lon1 = float(self.latitude), float(self.longitude)
        lat2, lon2 = float(latitude), float(longitude)
        
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        return c * r
    
    def to_dict(self, include_sensitive=False):
        """Convert scooter to dictionary"""
        data = {
            'id': self.id,
            'identifier': self.identifier,
            'model': self.model,
            'brand': self.brand,
            'latitude': float(self.latitude),
            'longitude': float(self.longitude),
            'address': self.address,
            'status': self.status,
            'battery_level': self.battery_level,
            'is_available': self.is_available(),
            'created_at': self.created_at.isoformat(),
            'last_location_update': self.last_location_update.isoformat()
        }
        
        if include_sensitive:
            data.update({
                'qr_code': self.qr_code,
                'max_speed': self.max_speed,
                'range_km': self.range_km,
                'provider_id': self.provider_id,
                'provider_name': self.provider.get_full_name(),
                'total_revenue': self.get_total_revenue(),
                'utilization_rate': self.get_utilization_rate(),
                'rental_count': self.rentals.count(),
                'needs_maintenance': self.needs_maintenance(),
                'last_maintenance': self.last_maintenance.isoformat() if self.last_maintenance else None
            })
        
        return data
    
    def __repr__(self):
        return f'<Scooter {self.identifier}>'
