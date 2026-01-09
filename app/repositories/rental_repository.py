"""
Rental repository for data access operations
"""

from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from app import db
from app.models.rental import Rental

class RentalRepository:
    """Repository for Rental model data access"""
    
    @staticmethod
    def create(user_id: int, scooter_id: int, start_latitude: float, 
               start_longitude: float) -> Rental:
        """Create a new rental"""
        rental = Rental(
            user_id=user_id,
            scooter_id=scooter_id,
            start_latitude=start_latitude,
            start_longitude=start_longitude
        )
        
        db.session.add(rental)
        db.session.commit()
        return rental
    
    @staticmethod
    def get_by_id(rental_id: int) -> Optional[Rental]:
        """Get rental by ID"""
        return Rental.query.get(rental_id)
    
    @staticmethod
    def get_by_code(rental_code: str) -> Optional[Rental]:
        """Get rental by rental code"""
        return Rental.query.filter_by(rental_code=rental_code).first()
    
    @staticmethod
    def get_all(limit: int = 100, offset: int = 0) -> List[Rental]:
        """Get all rentals with pagination"""
        return Rental.query.order_by(Rental.created_at.desc()).limit(limit).offset(offset).all()
    
    @staticmethod
    def get_by_user(user_id: int, limit: int = 100) -> List[Rental]:
        """Get rentals by user"""
        return Rental.query.filter_by(user_id=user_id)\
                           .order_by(Rental.created_at.desc())\
                           .limit(limit).all()
    
    @staticmethod
    def get_by_scooter(scooter_id: int, limit: int = 100) -> List[Rental]:
        """Get rentals by scooter"""
        return Rental.query.filter_by(scooter_id=scooter_id)\
                           .order_by(Rental.created_at.desc())\
                           .limit(limit).all()
    
    @staticmethod
    def get_by_status(status: str, limit: int = 100) -> List[Rental]:
        """Get rentals by status"""
        return Rental.query.filter_by(status=status)\
                           .order_by(Rental.created_at.desc())\
                           .limit(limit).all()
    
    @staticmethod
    def get_active_rentals(limit: int = 100) -> List[Rental]:
        """Get all active rentals"""
        return Rental.query.filter_by(status='active')\
                           .order_by(Rental.start_time.desc())\
                           .limit(limit).all()
    
    @staticmethod
    def get_active_by_user(user_id: int) -> Optional[Rental]:
        """Get active rental for a user"""
        return Rental.query.filter_by(user_id=user_id, status='active').first()
    
    @staticmethod
    def get_active_by_scooter(scooter_id: int) -> Optional[Rental]:
        """Get active rental for a scooter"""
        return Rental.query.filter_by(scooter_id=scooter_id, status='active').first()
    
    @staticmethod
    def get_completed_rentals(limit: int = 100) -> List[Rental]:
        """Get completed rentals"""
        return Rental.query.filter_by(status='completed')\
                           .order_by(Rental.end_time.desc())\
                           .limit(limit).all()
    
    @staticmethod
    def get_overdue_rentals() -> List[Rental]:
        """Get overdue rentals"""
        return Rental.query.filter_by(status='overdue').all()
    
    @staticmethod
    def get_rentals_in_timerange(start_date: datetime, end_date: datetime, 
                                  limit: int = 1000) -> List[Rental]:
        """Get rentals within a time range"""
        return Rental.query.filter(
            and_(
                Rental.start_time >= start_date,
                Rental.start_time <= end_date
            )
        ).order_by(Rental.start_time.desc()).limit(limit).all()
    
    @staticmethod
    def get_recent_rentals(days: int = 7, limit: int = 100) -> List[Rental]:
        """Get recent rentals"""
        start_date = datetime.utcnow() - timedelta(days=days)
        return Rental.query.filter(Rental.created_at >= start_date)\
                           .order_by(Rental.created_at.desc())\
                           .limit(limit).all()
    
    @staticmethod
    def update(rental: Rental, **kwargs) -> Rental:
        """Update rental attributes"""
        for key, value in kwargs.items():
            if hasattr(rental, key):
                setattr(rental, key, value)
        
        db.session.commit()
        return rental
    
    @staticmethod
    def delete(rental: Rental) -> bool:
        """Delete rental"""
        db.session.delete(rental)
        db.session.commit()
        return True
    
    @staticmethod
    def count_by_status(status: str) -> int:
        """Count rentals by status"""
        return Rental.query.filter_by(status=status).count()
    
    @staticmethod
    def count_by_user(user_id: int) -> int:
        """Count rentals by user"""
        return Rental.query.filter_by(user_id=user_id).count()
    
    @staticmethod
    def get_total_revenue(start_date: Optional[datetime] = None, 
                         end_date: Optional[datetime] = None) -> float:
        """Calculate total revenue from rentals"""
        from sqlalchemy import func
        
        query = db.session.query(func.sum(Rental.total_cost))
        
        if start_date:
            query = query.filter(Rental.start_time >= start_date)
        if end_date:
            query = query.filter(Rental.start_time <= end_date)
        
        result = query.scalar()
        return float(result) if result else 0.0
    
    @staticmethod
    def get_average_duration() -> float:
        """Calculate average rental duration in minutes"""
        from sqlalchemy import func
        
        result = db.session.query(func.avg(Rental.duration_minutes))\
                          .filter(Rental.status == 'completed')\
                          .scalar()
        
        return float(result) if result else 0.0
    
    @staticmethod
    def get_user_statistics(user_id: int) -> dict:
        """Get rental statistics for a user"""
        from sqlalchemy import func
        
        total_rentals = RentalRepository.count_by_user(user_id)
        
        total_spent = db.session.query(func.sum(Rental.total_cost))\
                               .filter_by(user_id=user_id)\
                               .scalar()
        
        avg_duration = db.session.query(func.avg(Rental.duration_minutes))\
                                 .filter_by(user_id=user_id, status='completed')\
                                 .scalar()
        
        return {
            'total_rentals': total_rentals,
            'total_spent': float(total_spent) if total_spent else 0.0,
            'average_duration': float(avg_duration) if avg_duration else 0.0
        }
