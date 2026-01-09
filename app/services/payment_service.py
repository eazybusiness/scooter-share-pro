"""
Payment service for payment processing and management
"""

from typing import Optional, Tuple, List
from datetime import datetime
from app.repositories.payment_repository import PaymentRepository
from app.repositories.rental_repository import RentalRepository
from app.repositories.user_repository import UserRepository
from app.models.payment import Payment
from app.models.rental import Rental
from app.models.user import User

class PaymentService:
    """Service for payment management"""
    
    def __init__(self):
        self.payment_repo = PaymentRepository()
        self.rental_repo = RentalRepository()
        self.user_repo = UserRepository()
    
    def create_payment(self, user_id: int, rental_id: int, amount: float, 
                      payment_method: str) -> Tuple[Optional[Payment], Optional[str]]:
        """
        Create a new payment
        Returns: (Payment, error_message)
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None, 'User not found'
        
        rental = self.rental_repo.get_by_id(rental_id)
        if not rental:
            return None, 'Rental not found'
        
        if rental.user_id != user_id:
            return None, 'Rental does not belong to this user'
        
        if amount <= 0:
            return None, 'Payment amount must be greater than 0'
        
        valid_methods = ['credit_card', 'paypal', 'bank_transfer', 'cash']
        if payment_method not in valid_methods:
            return None, f'Invalid payment method. Must be one of: {", ".join(valid_methods)}'
        
        try:
            payment = self.payment_repo.create(
                user_id=user_id,
                rental_id=rental_id,
                amount=amount,
                payment_method=payment_method
            )
            return payment, None
        except Exception as e:
            return None, str(e)
    
    def process_payment(self, payment_id: int, gateway_transaction_id: Optional[str] = None, 
                       gateway_response: Optional[dict] = None) -> Tuple[bool, Optional[str]]:
        """
        Process a payment
        Returns: (success, error_message)
        """
        payment = self.payment_repo.get_by_id(payment_id)
        
        if not payment:
            return False, 'Payment not found'
        
        if payment.status != 'pending':
            return False, f'Payment is already {payment.status}'
        
        try:
            payment.process_payment(gateway_transaction_id, gateway_response)
            return True, None
        except Exception as e:
            return False, str(e)
    
    def complete_payment(self, payment_id: int, gateway_transaction_id: Optional[str] = None, 
                        gateway_response: Optional[dict] = None) -> Tuple[bool, Optional[str]]:
        """
        Complete a payment
        Returns: (success, error_message)
        """
        payment = self.payment_repo.get_by_id(payment_id)
        
        if not payment:
            return False, 'Payment not found'
        
        if payment.status == 'completed':
            return False, 'Payment is already completed'
        
        try:
            payment.complete_payment(gateway_transaction_id, gateway_response)
            return True, None
        except Exception as e:
            return False, str(e)
    
    def fail_payment(self, payment_id: int, 
                    gateway_response: Optional[dict] = None) -> Tuple[bool, Optional[str]]:
        """
        Mark payment as failed
        Returns: (success, error_message)
        """
        payment = self.payment_repo.get_by_id(payment_id)
        
        if not payment:
            return False, 'Payment not found'
        
        try:
            payment.fail_payment(gateway_response)
            return True, None
        except Exception as e:
            return False, str(e)
    
    def refund_payment(self, payment_id: int, refund_amount: Optional[float] = None, 
                      reason: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Refund a payment
        Returns: (success, error_message)
        """
        payment = self.payment_repo.get_by_id(payment_id)
        
        if not payment:
            return False, 'Payment not found'
        
        if not payment.is_refundable():
            return False, 'Payment is not refundable'
        
        try:
            payment.refund_payment(refund_amount, reason)
            return True, None
        except Exception as e:
            return False, str(e)
    
    def get_payment_by_id(self, payment_id: int) -> Optional[Payment]:
        """Get payment by ID"""
        return self.payment_repo.get_by_id(payment_id)
    
    def get_payment_by_transaction_id(self, transaction_id: str) -> Optional[Payment]:
        """Get payment by transaction ID"""
        return self.payment_repo.get_by_transaction_id(transaction_id)
    
    def get_user_payments(self, user_id: int, limit: int = 100) -> List[Payment]:
        """Get payments for a user"""
        return self.payment_repo.get_by_user(user_id, limit)
    
    def get_rental_payments(self, rental_id: int) -> List[Payment]:
        """Get payments for a rental"""
        return self.payment_repo.get_by_rental(rental_id)
    
    def get_pending_payments(self, limit: int = 100) -> List[Payment]:
        """Get pending payments"""
        return self.payment_repo.get_pending_payments(limit)
    
    def get_completed_payments(self, limit: int = 100) -> List[Payment]:
        """Get completed payments"""
        return self.payment_repo.get_completed_payments(limit)
    
    def get_failed_payments(self, limit: int = 100) -> List[Payment]:
        """Get failed payments"""
        return self.payment_repo.get_failed_payments(limit)
    
    def get_refundable_payments(self, user_id: Optional[int] = None) -> List[Payment]:
        """Get refundable payments"""
        return self.payment_repo.get_refundable_payments(user_id)
    
    def get_payment_statistics(self, start_date: Optional[datetime] = None, 
                              end_date: Optional[datetime] = None) -> dict:
        """Get payment statistics"""
        return self.payment_repo.get_payment_statistics(start_date, end_date)
    
    def get_user_total_spent(self, user_id: int) -> float:
        """Get total amount spent by user"""
        return self.payment_repo.get_user_total_spent(user_id)
    
    def get_revenue_by_method(self, payment_method: str, 
                             start_date: Optional[datetime] = None) -> float:
        """Get revenue by payment method"""
        return self.payment_repo.get_revenue_by_method(payment_method, start_date)
    
    def validate_payment_access(self, payment: Payment, user: User) -> bool:
        """Check if user can access payment details"""
        if user.is_admin():
            return True
        
        if payment.user_id == user.id:
            return True
        
        if user.is_provider() and payment.rental.scooter.provider_id == user.id:
            return True
        
        return False
    
    def process_rental_payment(self, rental_id: int, payment_method: str) -> Tuple[Optional[Payment], Optional[str]]:
        """
        Create and process payment for a rental
        Returns: (Payment, error_message)
        """
        rental = self.rental_repo.get_by_id(rental_id)
        
        if not rental:
            return None, 'Rental not found'
        
        if rental.status not in ['completed', 'cancelled']:
            return None, 'Rental must be completed or cancelled before payment'
        
        existing_payments = self.get_rental_payments(rental_id)
        total_paid = sum(p.amount for p in existing_payments if p.status == 'completed')
        
        if total_paid >= rental.total_cost:
            return None, 'Rental is already fully paid'
        
        remaining_amount = float(rental.total_cost) - total_paid
        
        payment, error = self.create_payment(
            user_id=rental.user_id,
            rental_id=rental_id,
            amount=remaining_amount,
            payment_method=payment_method
        )
        
        if error:
            return None, error
        
        success, error = self.complete_payment(payment.id)
        
        if error:
            return None, error
        
        return payment, None
