"""
Rental service for rental management and operations
"""

from typing import Optional, Tuple, List
from datetime import datetime
from app.repositories.rental_repository import RentalRepository
from app.repositories.scooter_repository import ScooterRepository
from app.repositories.user_repository import UserRepository
from app.models.rental import Rental
from app.models.scooter import Scooter
from app.models.user import User

class RentalService:
    """Service for rental management"""
    
    def __init__(self):
        self.rental_repo = RentalRepository()
        self.scooter_repo = ScooterRepository()
        self.user_repo = UserRepository()
    
    def start_rental(self, user_id: int, scooter_id: int, 
                    start_latitude: float, start_longitude: float) -> Tuple[Optional[Rental], Optional[str]]:
        """
        Start a new rental
        Returns: (Rental, error_message)
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None, 'User not found'
        
        if not user.is_active:
            return None, 'User account is not active'
        
        active_rental = self.rental_repo.get_active_by_user(user_id)
        if active_rental:
            return None, 'User already has an active rental'
        
        scooter = self.scooter_repo.get_by_id(scooter_id)
        if not scooter:
            return None, 'Scooter not found'
        
        if not scooter.is_available():
            return None, 'Scooter is not available'
        
        try:
            rental = self.rental_repo.create(
                user_id=user_id,
                scooter_id=scooter_id,
                start_latitude=start_latitude,
                start_longitude=start_longitude
            )
            
            rental.start_rental()
            
            return rental, None
        except Exception as e:
            return None, str(e)
    
    def end_rental(self, rental_id: int, end_latitude: Optional[float] = None, 
                  end_longitude: Optional[float] = None) -> Tuple[Optional[Rental], Optional[str]]:
        """
        End an active rental
        Returns: (Rental, error_message)
        """
        rental = self.rental_repo.get_by_id(rental_id)
        
        if not rental:
            return None, 'Rental not found'
        
        if rental.status != 'active':
            return None, 'Rental is not active'
        
        try:
            rental.end_rental(end_latitude, end_longitude)
            return rental, None
        except Exception as e:
            return None, str(e)
    
    def cancel_rental(self, rental_id: int, reason: Optional[str] = None) -> Tuple[Optional[Rental], Optional[str]]:
        """
        Cancel an active rental
        Returns: (Rental, error_message)
        """
        rental = self.rental_repo.get_by_id(rental_id)
        
        if not rental:
            return None, 'Rental not found'
        
        if rental.status != 'active':
            return None, 'Only active rentals can be cancelled'
        
        try:
            rental.cancel_rental(reason)
            return rental, None
        except Exception as e:
            return None, str(e)
    
    def get_rental_by_id(self, rental_id: int) -> Optional[Rental]:
        """Get rental by ID"""
        return self.rental_repo.get_by_id(rental_id)
    
    def get_rental_by_code(self, rental_code: str) -> Optional[Rental]:
        """Get rental by code"""
        return self.rental_repo.get_by_code(rental_code)
    
    def get_user_rentals(self, user_id: int, limit: int = 100) -> List[Rental]:
        """Get rentals for a user"""
        return self.rental_repo.get_by_user(user_id, limit)
    
    def get_active_rental_for_user(self, user_id: int) -> Optional[Rental]:
        """Get active rental for a user"""
        return self.rental_repo.get_active_by_user(user_id)
    
    def get_scooter_rentals(self, scooter_id: int, limit: int = 100) -> List[Rental]:
        """Get rentals for a scooter"""
        return self.rental_repo.get_by_scooter(scooter_id, limit)
    
    def get_provider_rentals(self, provider_id: int, limit: int = 100) -> List[Rental]:
        """Get all rentals for a provider's scooters"""
        scooters = self.scooter_repo.get_by_provider(provider_id, limit=1000)
        scooter_ids = [s.id for s in scooters]
        
        all_rentals = []
        for scooter_id in scooter_ids:
            rentals = self.rental_repo.get_by_scooter(scooter_id, limit=limit)
            all_rentals.extend(rentals)
        
        # Sort by created_at descending
        all_rentals.sort(key=lambda r: r.created_at, reverse=True)
        return all_rentals[:limit]
    
    def get_all_rentals(self, limit: int = 100, offset: int = 0) -> List[Rental]:
        """Get all rentals"""
        return self.rental_repo.get_all(limit, offset)
    
    def get_active_rentals(self, limit: int = 100) -> List[Rental]:
        """Get all active rentals"""
        return self.rental_repo.get_active_rentals(limit)
    
    def get_completed_rentals(self, limit: int = 100) -> List[Rental]:
        """Get completed rentals"""
        return self.rental_repo.get_completed_rentals(limit)
    
    def add_rating(self, rental_id: int, rating: int, 
                  feedback: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Add rating to a completed rental
        Returns: (success, error_message)
        """
        rental = self.rental_repo.get_by_id(rental_id)
        
        if not rental:
            return False, 'Rental not found'
        
        try:
            rental.add_rating(rating, feedback)
            return True, None
        except Exception as e:
            return False, str(e)
    
    def check_overdue_rentals(self) -> List[Rental]:
        """Check and update overdue rentals"""
        active_rentals = self.rental_repo.get_active_rentals(limit=1000)
        overdue_rentals = []
        
        for rental in active_rentals:
            if rental.check_overdue_status():
                overdue_rentals.append(rental)
        
        return overdue_rentals
    
    def get_rental_statistics(self, start_date: Optional[datetime] = None, 
                             end_date: Optional[datetime] = None) -> dict:
        """Get rental statistics"""
        if start_date and end_date:
            rentals = self.rental_repo.get_rentals_in_timerange(start_date, end_date)
        else:
            rentals = self.rental_repo.get_all(limit=10000)
        
        total_rentals = len(rentals)
        active = len([r for r in rentals if r.status == 'active'])
        completed = len([r for r in rentals if r.status == 'completed'])
        cancelled = len([r for r in rentals if r.status == 'cancelled'])
        overdue = len([r for r in rentals if r.status == 'overdue'])
        
        total_revenue = self.rental_repo.get_total_revenue(start_date, end_date)
        avg_duration = self.rental_repo.get_average_duration()
        
        return {
            'total_rentals': total_rentals,
            'active': active,
            'completed': completed,
            'cancelled': cancelled,
            'overdue': overdue,
            'total_revenue': total_revenue,
            'average_duration_minutes': avg_duration,
            'completion_rate': (completed / total_rentals * 100) if total_rentals > 0 else 0
        }
    
    def get_user_rental_statistics(self, user_id: int) -> dict:
        """Get rental statistics for a user"""
        return self.rental_repo.get_user_statistics(user_id)
    
    def validate_rental_access(self, rental: Rental, user: User) -> bool:
        """Check if user can access rental details"""
        if user.is_admin():
            return True
        
        if rental.user_id == user.id:
            return True
        
        if user.is_provider() and rental.scooter.provider_id == user.id:
            return True
        
        return False
    
    def can_end_rental(self, rental: Rental, user: User) -> bool:
        """Check if user can end the rental"""
        if rental.status != 'active':
            return False
        
        if user.is_admin():
            return True
        
        return rental.user_id == user.id
