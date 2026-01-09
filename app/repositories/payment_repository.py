"""
Payment repository for data access operations
"""

from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from app import db
from app.models.payment import Payment

class PaymentRepository:
    """Repository for Payment model data access"""
    
    @staticmethod
    def create(user_id: int, rental_id: int, amount: float, 
               payment_method: str) -> Payment:
        """Create a new payment"""
        payment = Payment(
            user_id=user_id,
            rental_id=rental_id,
            amount=amount,
            payment_method=payment_method
        )
        
        db.session.add(payment)
        db.session.commit()
        return payment
    
    @staticmethod
    def get_by_id(payment_id: int) -> Optional[Payment]:
        """Get payment by ID"""
        return Payment.query.get(payment_id)
    
    @staticmethod
    def get_by_transaction_id(transaction_id: str) -> Optional[Payment]:
        """Get payment by transaction ID"""
        return Payment.query.filter_by(transaction_id=transaction_id).first()
    
    @staticmethod
    def get_all(limit: int = 100, offset: int = 0) -> List[Payment]:
        """Get all payments with pagination"""
        return Payment.query.order_by(Payment.created_at.desc()).limit(limit).offset(offset).all()
    
    @staticmethod
    def get_by_user(user_id: int, limit: int = 100) -> List[Payment]:
        """Get payments by user"""
        return Payment.query.filter_by(user_id=user_id)\
                            .order_by(Payment.created_at.desc())\
                            .limit(limit).all()
    
    @staticmethod
    def get_by_rental(rental_id: int) -> List[Payment]:
        """Get payments for a rental"""
        return Payment.query.filter_by(rental_id=rental_id)\
                            .order_by(Payment.created_at.desc()).all()
    
    @staticmethod
    def get_by_status(status: str, limit: int = 100) -> List[Payment]:
        """Get payments by status"""
        return Payment.query.filter_by(status=status)\
                            .order_by(Payment.created_at.desc())\
                            .limit(limit).all()
    
    @staticmethod
    def get_pending_payments(limit: int = 100) -> List[Payment]:
        """Get pending payments"""
        return Payment.query.filter_by(status='pending')\
                            .order_by(Payment.created_at.asc())\
                            .limit(limit).all()
    
    @staticmethod
    def get_completed_payments(limit: int = 100) -> List[Payment]:
        """Get completed payments"""
        return Payment.query.filter_by(status='completed')\
                            .order_by(Payment.processed_at.desc())\
                            .limit(limit).all()
    
    @staticmethod
    def get_failed_payments(limit: int = 100) -> List[Payment]:
        """Get failed payments"""
        return Payment.query.filter_by(status='failed')\
                            .order_by(Payment.created_at.desc())\
                            .limit(limit).all()
    
    @staticmethod
    def get_payments_in_timerange(start_date: datetime, end_date: datetime,
                                   limit: int = 1000) -> List[Payment]:
        """Get payments within a time range"""
        return Payment.query.filter(
            and_(
                Payment.created_at >= start_date,
                Payment.created_at <= end_date
            )
        ).order_by(Payment.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_recent_payments(days: int = 7, limit: int = 100) -> List[Payment]:
        """Get recent payments"""
        start_date = datetime.utcnow() - timedelta(days=days)
        return Payment.query.filter(Payment.created_at >= start_date)\
                            .order_by(Payment.created_at.desc())\
                            .limit(limit).all()
    
    @staticmethod
    def update(payment: Payment, **kwargs) -> Payment:
        """Update payment attributes"""
        for key, value in kwargs.items():
            if hasattr(payment, key):
                setattr(payment, key, value)
        
        db.session.commit()
        return payment
    
    @staticmethod
    def delete(payment: Payment) -> bool:
        """Delete payment"""
        db.session.delete(payment)
        db.session.commit()
        return True
    
    @staticmethod
    def count_by_status(status: str) -> int:
        """Count payments by status"""
        return Payment.query.filter_by(status=status).count()
    
    @staticmethod
    def count_by_user(user_id: int) -> int:
        """Count payments by user"""
        return Payment.query.filter_by(user_id=user_id).count()
    
    @staticmethod
    def get_total_revenue(start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None) -> float:
        """Calculate total revenue from completed payments"""
        from sqlalchemy import func
        
        query = db.session.query(func.sum(Payment.amount))\
                         .filter_by(status='completed')
        
        if start_date:
            query = query.filter(Payment.processed_at >= start_date)
        if end_date:
            query = query.filter(Payment.processed_at <= end_date)
        
        result = query.scalar()
        return float(result) if result else 0.0
    
    @staticmethod
    def get_revenue_by_method(payment_method: str, 
                             start_date: Optional[datetime] = None) -> float:
        """Calculate revenue by payment method"""
        from sqlalchemy import func
        
        query = db.session.query(func.sum(Payment.amount))\
                         .filter_by(status='completed', payment_method=payment_method)
        
        if start_date:
            query = query.filter(Payment.processed_at >= start_date)
        
        result = query.scalar()
        return float(result) if result else 0.0
    
    @staticmethod
    def get_user_total_spent(user_id: int) -> float:
        """Get total amount spent by user"""
        from sqlalchemy import func
        
        result = db.session.query(func.sum(Payment.amount))\
                          .filter_by(user_id=user_id, status='completed')\
                          .scalar()
        
        return float(result) if result else 0.0
    
    @staticmethod
    def get_refundable_payments(user_id: Optional[int] = None) -> List[Payment]:
        """Get payments that can be refunded"""
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        query = Payment.query.filter(
            and_(
                Payment.status == 'completed',
                Payment.created_at >= thirty_days_ago,
                Payment.refund_amount < Payment.amount
            )
        )
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        return query.order_by(Payment.created_at.desc()).all()
    
    @staticmethod
    def get_payment_statistics(start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> dict:
        """Get payment statistics"""
        from sqlalchemy import func
        
        query = Payment.query
        
        if start_date:
            query = query.filter(Payment.created_at >= start_date)
        if end_date:
            query = query.filter(Payment.created_at <= end_date)
        
        total_payments = query.count()
        completed = query.filter_by(status='completed').count()
        pending = query.filter_by(status='pending').count()
        failed = query.filter_by(status='failed').count()
        
        total_revenue = PaymentRepository.get_total_revenue(start_date, end_date)
        
        return {
            'total_payments': total_payments,
            'completed': completed,
            'pending': pending,
            'failed': failed,
            'total_revenue': total_revenue,
            'success_rate': (completed / total_payments * 100) if total_payments > 0 else 0
        }
