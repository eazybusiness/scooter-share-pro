"""
Payment model for Scooter Share Pro
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import db

class Payment(db.Model):
    """Payment model for rental transactions"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Payment relationships
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rental_id = db.Column(db.Integer, db.ForeignKey('rentals.id'), nullable=False)
    
    # Payment details
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='EUR', nullable=False)
    payment_method = db.Column(db.Enum('credit_card', 'paypal', 'bank_transfer', 'cash', 
                                      name='payment_methods'), 
                              nullable=False)
    
    # Payment status
    status = db.Column(db.Enum('pending', 'processing', 'completed', 'failed', 'refunded', 
                              name='payment_status'), 
                      default='pending', nullable=False, index=True)
    
    # Payment gateway information
    gateway_transaction_id = db.Column(db.String(100))
    gateway_response = db.Column(db.JSON)
    
    # Refund information
    refund_amount = db.Column(db.Numeric(10, 2), default=0.00)
    refund_reason = db.Column(db.Text)
    refund_date = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                          onupdate=datetime.utcnow, nullable=False)
    processed_at = db.Column(db.DateTime)
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_payment_user_status', 'user_id', 'status'),
        db.Index('idx_payment_rental', 'rental_id'),
        db.Index('idx_payment_created', 'created_at'),
        db.CheckConstraint('amount >= 0', name='check_amount_positive'),
        db.CheckConstraint('refund_amount >= 0', name='check_refund_positive'),
    )
    
    def __init__(self, user_id, rental_id, amount, payment_method):
        self.user_id = user_id
        self.rental_id = rental_id
        self.amount = amount
        self.payment_method = payment_method
        self.transaction_id = self.generate_transaction_id()
    
    def generate_transaction_id(self):
        """Generate unique transaction ID"""
        import uuid
        return f"PAY-{uuid.uuid4().hex[:12].upper()}"
    
    def process_payment(self, gateway_transaction_id=None, gateway_response=None):
        """Mark payment as processing"""
        self.status = 'processing'
        self.gateway_transaction_id = gateway_transaction_id
        self.gateway_response = gateway_response
        self.processed_at = datetime.utcnow()
        db.session.commit()
    
    def complete_payment(self, gateway_transaction_id=None, gateway_response=None):
        """Mark payment as completed"""
        self.status = 'completed'
        if gateway_transaction_id:
            self.gateway_transaction_id = gateway_transaction_id
        if gateway_response:
            self.gateway_response = gateway_response
        self.processed_at = datetime.utcnow()
        db.session.commit()
    
    def fail_payment(self, gateway_response=None):
        """Mark payment as failed"""
        self.status = 'failed'
        self.gateway_response = gateway_response
        self.processed_at = datetime.utcnow()
        db.session.commit()
    
    def refund_payment(self, refund_amount=None, reason=None):
        """Process refund"""
        if self.status != 'completed':
            raise ValueError("Only completed payments can be refunded")
        
        if refund_amount is None:
            refund_amount = self.amount
        
        if refund_amount > self.amount:
            raise ValueError("Refund amount cannot exceed payment amount")
        
        self.refund_amount = refund_amount
        self.refund_reason = reason
        self.refund_date = datetime.utcnow()
        
        if refund_amount >= self.amount:
            self.status = 'refunded'
        
        db.session.commit()
    
    def is_refundable(self):
        """Check if payment can be refunded"""
        return (self.status == 'completed' and 
                self.refund_amount < self.amount and
                (datetime.utcnow() - self.created_at).days <= 30)  # 30-day refund window
    
    def get_refundable_amount(self):
        """Get amount that can be refunded"""
        if not self.is_refundable():
            return 0.0
        return float(self.amount - self.refund_amount)
    
    def to_dict(self, include_sensitive=False):
        """Convert payment to dictionary"""
        data = {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'user_id': self.user_id,
            'rental_id': self.rental_id,
            'amount': float(self.amount),
            'currency': self.currency,
            'payment_method': self.payment_method,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }
        
        if include_sensitive:
            data.update({
                'gateway_transaction_id': self.gateway_transaction_id,
                'gateway_response': self.gateway_response,
                'refund_amount': float(self.refund_amount),
                'refund_reason': self.refund_reason,
                'refund_date': self.refund_date.isoformat() if self.refund_date else None,
                'user_name': self.user.get_full_name(),
                'rental_code': self.rental.rental_code,
                'is_refundable': self.is_refundable(),
                'refundable_amount': self.get_refundable_amount()
            })
        
        return data
    
    def __repr__(self):
        return f'<Payment {self.transaction_id}>'
