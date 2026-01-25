"""
Dashboard routes
"""

from flask import render_template
from flask_login import login_required, current_user
from app.web import bp
from app.services.scooter_service import ScooterService
from app.services.rental_service import RentalService

scooter_service = ScooterService()
rental_service = RentalService()

@bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    if current_user.role == 'admin':
        return admin_dashboard()
    elif current_user.role == 'provider':
        return provider_dashboard()
    else:
        return customer_dashboard()

def admin_dashboard():
    """Admin dashboard"""
    rental_stats = rental_service.get_rental_statistics()
    active_rentals = rental_service.get_active_rentals(limit=10)
    recent_rentals = rental_service.rental_repo.get_recent_rentals(days=7, limit=10)
    
    scooters = scooter_service.get_all_scooters(limit=10)
    available_count = scooter_service.scooter_repo.count_by_status('available')
    in_use_count = scooter_service.scooter_repo.count_by_status('in_use')
    maintenance_count = scooter_service.scooter_repo.count_by_status('maintenance')
    
    return render_template('dashboard/admin.html',
                         rental_stats=rental_stats,
                         active_rentals=active_rentals,
                         recent_rentals=recent_rentals,
                         scooters=scooters,
                         available_count=available_count,
                         in_use_count=in_use_count,
                         maintenance_count=maintenance_count)

def provider_dashboard():
    """Provider dashboard"""
    scooters = scooter_service.get_scooters_by_provider(current_user.id, limit=100)
    
    # Get all rentals for provider's scooters
    all_rentals = rental_service.get_provider_rentals(current_user.id, limit=1000)
    
    # Calculate statistics correctly
    total_scooters = len(scooters)
    available = len([s for s in scooters if s.status == 'available'])
    in_use = len([s for s in scooters if s.status == 'in_use'])
    maintenance = len([s for s in scooters if s.status == 'maintenance'])
    
    # Calculate total revenue from rentals (same method as rentals page)
    total_revenue = sum(rental.total_cost for rental in all_rentals if rental.status == 'completed')
    
    # Calculate utilization rate based on actual rental time
    if all_rentals:
        # Get date range of rentals
        from datetime import datetime
        completed_rentals = [r for r in all_rentals if r.status == 'completed' and r.duration_minutes]
        
        if completed_rentals:
            # Calculate utilization based on actual rental periods
            total_minutes_used = sum(r.duration_minutes for r in completed_rentals)
            
            # Get the time span from first to last rental
            first_rental = min(completed_rentals, key=lambda r: r.created_at)
            last_rental = max(completed_rentals, key=lambda r: r.created_at)
            days_active = (last_rental.created_at - first_rental.created_at).days + 1
            
            # Calculate utilization over the active period
            total_possible_minutes = total_scooters * days_active * 24 * 60
            avg_utilization = (total_minutes_used / total_possible_minutes) * 100 if total_possible_minutes > 0 else 0
        else:
            avg_utilization = 0
    else:
        avg_utilization = 0
    
    stats = {
        'total_scooters': total_scooters,
        'available': available,
        'in_use': in_use,
        'maintenance': maintenance,
        'total_revenue': total_revenue,
        'average_utilization': avg_utilization
    }
    
    recent_rentals = sorted(all_rentals, key=lambda r: r.created_at, reverse=True)[:10]
    
    return render_template('dashboard/provider.html',
                         scooters=scooters,
                         stats=stats,
                         recent_rentals=recent_rentals)

def customer_dashboard():
    """Customer dashboard"""
    active_rental = rental_service.get_active_rental_for_user(current_user.id)
    rental_history = rental_service.get_user_rentals(current_user.id, limit=10)
    user_stats = rental_service.get_user_rental_statistics(current_user.id)
    
    nearby_scooters = []
    
    return render_template('dashboard/customer.html',
                         active_rental=active_rental,
                         rental_history=rental_history,
                         user_stats=user_stats,
                         nearby_scooters=nearby_scooters)
