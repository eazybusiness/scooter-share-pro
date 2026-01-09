"""
Scooter repository for data access operations
"""

from typing import List, Optional
from sqlalchemy import and_, or_
from app import db
from app.models.scooter import Scooter

class ScooterRepository:
    """Repository for Scooter model data access"""
    
    @staticmethod
    def create(identifier: str, model: str, brand: str, latitude: float, 
               longitude: float, provider_id: int, **kwargs) -> Scooter:
        """Create a new scooter"""
        scooter = Scooter(
            identifier=identifier,
            model=model,
            brand=brand,
            latitude=latitude,
            longitude=longitude,
            provider_id=provider_id
        )
        
        if 'address' in kwargs:
            scooter.address = kwargs['address']
        if 'battery_level' in kwargs:
            scooter.battery_level = kwargs['battery_level']
        if 'max_speed' in kwargs:
            scooter.max_speed = kwargs['max_speed']
        if 'range_km' in kwargs:
            scooter.range_km = kwargs['range_km']
        
        db.session.add(scooter)
        db.session.commit()
        return scooter
    
    @staticmethod
    def get_by_id(scooter_id: int) -> Optional[Scooter]:
        """Get scooter by ID"""
        return Scooter.query.get(scooter_id)
    
    @staticmethod
    def get_by_identifier(identifier: str) -> Optional[Scooter]:
        """Get scooter by identifier"""
        return Scooter.query.filter_by(identifier=identifier.upper()).first()
    
    @staticmethod
    def get_by_qr_code(qr_code: str) -> Optional[Scooter]:
        """Get scooter by QR code"""
        return Scooter.query.filter_by(qr_code=qr_code).first()
    
    @staticmethod
    def get_all(limit: int = 100, offset: int = 0) -> List[Scooter]:
        """Get all scooters with pagination"""
        return Scooter.query.limit(limit).offset(offset).all()
    
    @staticmethod
    def get_by_status(status: str, limit: int = 100) -> List[Scooter]:
        """Get scooters by status"""
        return Scooter.query.filter_by(status=status).limit(limit).all()
    
    @staticmethod
    def get_available(limit: int = 100) -> List[Scooter]:
        """Get available scooters"""
        return Scooter.query.filter(
            and_(
                Scooter.status == 'available',
                Scooter.battery_level > 10
            )
        ).limit(limit).all()
    
    @staticmethod
    def get_by_provider(provider_id: int, limit: int = 100) -> List[Scooter]:
        """Get scooters by provider"""
        return Scooter.query.filter_by(provider_id=provider_id).limit(limit).all()
    
    @staticmethod
    def get_nearby(latitude: float, longitude: float, radius_km: float = 5.0, 
                   limit: int = 50) -> List[Scooter]:
        """Get scooters near a location (simplified - uses bounding box)"""
        lat_delta = radius_km / 111.0
        lon_delta = radius_km / (111.0 * abs(latitude))
        
        return Scooter.query.filter(
            and_(
                Scooter.latitude.between(latitude - lat_delta, latitude + lat_delta),
                Scooter.longitude.between(longitude - lon_delta, longitude + lon_delta),
                Scooter.status == 'available'
            )
        ).limit(limit).all()
    
    @staticmethod
    def get_low_battery(threshold: int = 20, limit: int = 100) -> List[Scooter]:
        """Get scooters with low battery"""
        return Scooter.query.filter(
            Scooter.battery_level <= threshold
        ).limit(limit).all()
    
    @staticmethod
    def get_needing_maintenance(limit: int = 100) -> List[Scooter]:
        """Get scooters needing maintenance"""
        from datetime import datetime, timedelta
        
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        return Scooter.query.filter(
            or_(
                Scooter.battery_level < 20,
                and_(
                    Scooter.last_maintenance.isnot(None),
                    Scooter.last_maintenance < thirty_days_ago
                )
            )
        ).limit(limit).all()
    
    @staticmethod
    def update(scooter: Scooter, **kwargs) -> Scooter:
        """Update scooter attributes"""
        for key, value in kwargs.items():
            if hasattr(scooter, key):
                setattr(scooter, key, value)
        
        db.session.commit()
        return scooter
    
    @staticmethod
    def delete(scooter: Scooter) -> bool:
        """Delete scooter"""
        db.session.delete(scooter)
        db.session.commit()
        return True
    
    @staticmethod
    def search(query: str, limit: int = 50) -> List[Scooter]:
        """Search scooters by identifier, model, or brand"""
        search_pattern = f"%{query}%"
        return Scooter.query.filter(
            or_(
                Scooter.identifier.ilike(search_pattern),
                Scooter.model.ilike(search_pattern),
                Scooter.brand.ilike(search_pattern)
            )
        ).limit(limit).all()
    
    @staticmethod
    def count_by_status(status: str) -> int:
        """Count scooters by status"""
        return Scooter.query.filter_by(status=status).count()
    
    @staticmethod
    def count_by_provider(provider_id: int) -> int:
        """Count scooters by provider"""
        return Scooter.query.filter_by(provider_id=provider_id).count()
    
    @staticmethod
    def exists(identifier: str) -> bool:
        """Check if scooter exists by identifier"""
        return Scooter.query.filter_by(identifier=identifier.upper()).count() > 0
    
    @staticmethod
    def bulk_update_status(scooter_ids: List[int], status: str) -> int:
        """Bulk update scooter status"""
        count = Scooter.query.filter(Scooter.id.in_(scooter_ids)).update(
            {'status': status},
            synchronize_session=False
        )
        db.session.commit()
        return count
