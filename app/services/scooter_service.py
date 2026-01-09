"""
Scooter service for scooter management and operations
"""

from typing import Optional, Tuple, List
from app.repositories.scooter_repository import ScooterRepository
from app.repositories.user_repository import UserRepository
from app.models.scooter import Scooter
from app.models.user import User

class ScooterService:
    """Service for scooter management"""
    
    def __init__(self):
        self.scooter_repo = ScooterRepository()
        self.user_repo = UserRepository()
    
    def create_scooter(self, identifier: str, model: str, brand: str, 
                      latitude: float, longitude: float, provider_id: int, 
                      **kwargs) -> Tuple[Optional[Scooter], Optional[str]]:
        """
        Create a new scooter
        Returns: (Scooter, error_message)
        """
        provider = self.user_repo.get_by_id(provider_id)
        
        if not provider:
            return None, 'Provider not found'
        
        if not provider.can_manage_scooters():
            return None, 'User is not authorized to manage scooters'
        
        if self.scooter_repo.exists(identifier):
            return None, 'Scooter with this identifier already exists'
        
        try:
            scooter = self.scooter_repo.create(
                identifier=identifier,
                model=model,
                brand=brand,
                latitude=latitude,
                longitude=longitude,
                provider_id=provider_id,
                **kwargs
            )
            return scooter, None
        except Exception as e:
            return None, str(e)
    
    def get_scooter_by_id(self, scooter_id: int) -> Optional[Scooter]:
        """Get scooter by ID"""
        return self.scooter_repo.get_by_id(scooter_id)
    
    def get_scooter_by_identifier(self, identifier: str) -> Optional[Scooter]:
        """Get scooter by identifier"""
        return self.scooter_repo.get_by_identifier(identifier)
    
    def get_scooter_by_qr_code(self, qr_code: str) -> Optional[Scooter]:
        """Get scooter by QR code"""
        return self.scooter_repo.get_by_qr_code(qr_code)
    
    def get_all_scooters(self, limit: int = 100, offset: int = 0) -> List[Scooter]:
        """Get all scooters"""
        return self.scooter_repo.get_all(limit, offset)
    
    def get_available_scooters(self, limit: int = 100) -> List[Scooter]:
        """Get available scooters"""
        return self.scooter_repo.get_available(limit)
    
    def get_scooters_by_provider(self, provider_id: int, limit: int = 100) -> List[Scooter]:
        """Get scooters by provider"""
        return self.scooter_repo.get_by_provider(provider_id, limit)
    
    def get_nearby_scooters(self, latitude: float, longitude: float, 
                           radius_km: float = 5.0, limit: int = 50) -> List[Scooter]:
        """Get scooters near a location"""
        scooters = self.scooter_repo.get_nearby(latitude, longitude, radius_km, limit)
        
        for scooter in scooters:
            scooter.distance = scooter.distance_from(latitude, longitude)
        
        return sorted(scooters, key=lambda s: s.distance)
    
    def update_scooter(self, scooter: Scooter, user: User, 
                      **kwargs) -> Tuple[Optional[Scooter], Optional[str]]:
        """
        Update scooter details
        Returns: (Scooter, error_message)
        """
        if not user.is_admin() and scooter.provider_id != user.id:
            return None, 'Not authorized to update this scooter'
        
        allowed_fields = ['model', 'brand', 'address', 'battery_level', 
                         'max_speed', 'range_km']
        
        update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not update_data:
            return None, 'No valid fields to update'
        
        try:
            updated_scooter = self.scooter_repo.update(scooter, **update_data)
            return updated_scooter, None
        except Exception as e:
            return None, str(e)
    
    def update_location(self, scooter: Scooter, latitude: float, longitude: float, 
                       address: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Update scooter location
        Returns: (success, error_message)
        """
        try:
            scooter.update_location(latitude, longitude, address)
            return True, None
        except Exception as e:
            return False, str(e)
    
    def update_battery_level(self, scooter: Scooter, 
                            battery_level: int) -> Tuple[bool, Optional[str]]:
        """
        Update scooter battery level
        Returns: (success, error_message)
        """
        if not (0 <= battery_level <= 100):
            return False, 'Battery level must be between 0 and 100'
        
        try:
            self.scooter_repo.update(scooter, battery_level=battery_level)
            
            if battery_level < 20 and scooter.status == 'available':
                scooter.set_status('maintenance')
            
            return True, None
        except Exception as e:
            return False, str(e)
    
    def set_status(self, scooter: Scooter, status: str, 
                  user: User) -> Tuple[bool, Optional[str]]:
        """
        Set scooter status
        Returns: (success, error_message)
        """
        if not user.is_admin() and scooter.provider_id != user.id:
            return False, 'Not authorized to change scooter status'
        
        if scooter.get_current_rental() and status == 'available':
            return False, 'Cannot set scooter to available while it has an active rental'
        
        try:
            scooter.set_status(status)
            return True, None
        except Exception as e:
            return False, str(e)
    
    def set_maintenance(self, scooter: Scooter, user: User) -> Tuple[bool, Optional[str]]:
        """
        Set scooter to maintenance mode
        Returns: (success, error_message)
        """
        if scooter.get_current_rental():
            return False, 'Cannot set scooter to maintenance while it has an active rental'
        
        return self.set_status(scooter, 'maintenance', user)
    
    def complete_maintenance(self, scooter: Scooter, user: User) -> Tuple[bool, Optional[str]]:
        """
        Complete maintenance and set scooter to available
        Returns: (success, error_message)
        """
        from datetime import datetime
        
        if scooter.status != 'maintenance':
            return False, 'Scooter is not in maintenance mode'
        
        try:
            self.scooter_repo.update(scooter, last_maintenance=datetime.utcnow())
            scooter.set_status('available')
            return True, None
        except Exception as e:
            return False, str(e)
    
    def delete_scooter(self, scooter: Scooter, user: User) -> Tuple[bool, Optional[str]]:
        """
        Delete a scooter
        Returns: (success, error_message)
        """
        if not user.is_admin() and scooter.provider_id != user.id:
            return False, 'Not authorized to delete this scooter'
        
        if scooter.get_current_rental():
            return False, 'Cannot delete scooter with active rental'
        
        try:
            self.scooter_repo.delete(scooter)
            return True, None
        except Exception as e:
            return False, str(e)
    
    def search_scooters(self, query: str, limit: int = 50) -> List[Scooter]:
        """Search scooters"""
        return self.scooter_repo.search(query, limit)
    
    def get_scooters_needing_maintenance(self, limit: int = 100) -> List[Scooter]:
        """Get scooters that need maintenance"""
        return self.scooter_repo.get_needing_maintenance(limit)
    
    def get_low_battery_scooters(self, threshold: int = 20, limit: int = 100) -> List[Scooter]:
        """Get scooters with low battery"""
        return self.scooter_repo.get_low_battery(threshold, limit)
    
    def get_scooter_statistics(self, scooter: Scooter) -> dict:
        """Get statistics for a scooter"""
        return {
            'total_revenue': scooter.get_total_revenue(),
            'utilization_rate': scooter.get_utilization_rate(),
            'total_rentals': scooter.rentals.count(),
            'needs_maintenance': scooter.needs_maintenance(),
            'is_available': scooter.is_available()
        }
    
    def get_provider_statistics(self, provider_id: int) -> dict:
        """Get statistics for a provider's scooters"""
        scooters = self.get_scooters_by_provider(provider_id, limit=1000)
        
        total_scooters = len(scooters)
        available = len([s for s in scooters if s.status == 'available'])
        in_use = len([s for s in scooters if s.status == 'in_use'])
        maintenance = len([s for s in scooters if s.status == 'maintenance'])
        
        total_revenue = sum(s.get_total_revenue() for s in scooters)
        avg_utilization = sum(s.get_utilization_rate() for s in scooters) / total_scooters if total_scooters > 0 else 0
        
        return {
            'total_scooters': total_scooters,
            'available': available,
            'in_use': in_use,
            'maintenance': maintenance,
            'total_revenue': total_revenue,
            'average_utilization': avg_utilization
        }
