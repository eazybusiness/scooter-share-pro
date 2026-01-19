"""
Rental management routes
"""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.web import bp
from app.services.rental_service import RentalService
from app.services.scooter_service import ScooterService

rental_service = RentalService()
scooter_service = ScooterService()

@bp.route('/rentals')
@login_required
def rentals_list():
    """List rentals - providers see their scooter rentals, customers see their own rentals"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    if current_user.is_admin():
        rentals = rental_service.get_all_rentals(limit=per_page, offset=(page-1)*per_page)
        return render_template('rentals/list.html', rentals=rentals, page=page)
    elif current_user.is_provider():
        # Providers see rentals of their scooters
        rentals = rental_service.get_provider_rentals(current_user.id, limit=per_page)
        return render_template('rentals/provider_list.html', rentals=rentals, page=page)
    else:
        # Customers see their own rentals
        rentals = rental_service.get_user_rentals(current_user.id, limit=per_page)
        return render_template('rentals/list.html', rentals=rentals, page=page)

@bp.route('/rentals/<int:rental_id>')
@login_required
def rental_detail(rental_id):
    """Rental detail page"""
    rental = rental_service.get_rental_by_id(rental_id)
    
    if not rental:
        flash('Rental not found.', 'danger')
        return redirect(url_for('web.rentals_list'))
    
    if not rental_service.validate_rental_access(rental, current_user):
        flash('You are not authorized to view this rental.', 'danger')
        return redirect(url_for('web.rentals_list'))
    
    return render_template('rentals/detail.html', rental=rental)

@bp.route('/rentals/start/<int:scooter_id>', methods=['GET', 'POST'])
@login_required
def start_rental(scooter_id):
    """Start a rental"""
    scooter = scooter_service.get_scooter_by_id(scooter_id)
    
    if not scooter:
        flash('Scooter not found.', 'danger')
        return redirect(url_for('web.available_scooters'))
    
    if request.method == 'POST':
        latitude = float(request.form.get('latitude', scooter.latitude))
        longitude = float(request.form.get('longitude', scooter.longitude))
        
        rental, error = rental_service.start_rental(
            user_id=current_user.id,
            scooter_id=scooter_id,
            start_latitude=latitude,
            start_longitude=longitude
        )
        
        if error:
            flash(error, 'danger')
            return redirect(url_for('web.scooter_detail', scooter_id=scooter_id))
        
        flash('Rental started successfully!', 'success')
        return redirect(url_for('web.rental_detail', rental_id=rental.id))
    
    return render_template('rentals/start.html', scooter=scooter)

@bp.route('/rentals/<int:rental_id>/end', methods=['POST'])
@login_required
def end_rental(rental_id):
    """End a rental"""
    rental = rental_service.get_rental_by_id(rental_id)
    
    if not rental:
        flash('Rental not found.', 'danger')
        return redirect(url_for('web.rentals_list'))
    
    if not rental_service.can_end_rental(rental, current_user):
        flash('You are not authorized to end this rental.', 'danger')
        return redirect(url_for('web.rental_detail', rental_id=rental_id))
    
    latitude = request.form.get('latitude', type=float)
    longitude = request.form.get('longitude', type=float)
    
    rental, error = rental_service.end_rental(rental_id, latitude, longitude)
    
    if error:
        flash(error, 'danger')
    else:
        flash('Rental ended successfully!', 'success')
    
    return redirect(url_for('web.rental_detail', rental_id=rental_id))

@bp.route('/rentals/<int:rental_id>/cancel', methods=['POST'])
@login_required
def cancel_rental(rental_id):
    """Cancel a rental"""
    rental = rental_service.get_rental_by_id(rental_id)
    
    if not rental:
        flash('Rental not found.', 'danger')
        return redirect(url_for('web.rentals_list'))
    
    if not current_user.is_admin() and rental.user_id != current_user.id:
        flash('You are not authorized to cancel this rental.', 'danger')
        return redirect(url_for('web.rental_detail', rental_id=rental_id))
    
    reason = request.form.get('reason')
    
    rental, error = rental_service.cancel_rental(rental_id, reason)
    
    if error:
        flash(error, 'danger')
    else:
        flash('Rental cancelled.', 'info')
    
    return redirect(url_for('web.rental_detail', rental_id=rental_id))

@bp.route('/rentals/<int:rental_id>/rate', methods=['POST'])
@login_required
def rate_rental(rental_id):
    """Rate a rental"""
    rental = rental_service.get_rental_by_id(rental_id)
    
    if not rental:
        flash('Rental not found.', 'danger')
        return redirect(url_for('web.rentals_list'))
    
    if rental.user_id != current_user.id:
        flash('You are not authorized to rate this rental.', 'danger')
        return redirect(url_for('web.rental_detail', rental_id=rental_id))
    
    rating = int(request.form.get('rating'))
    feedback = request.form.get('feedback')
    
    success, error = rental_service.add_rating(rental_id, rating, feedback)
    
    if error:
        flash(error, 'danger')
    else:
        flash('Thank you for your rating!', 'success')
    
    return redirect(url_for('web.rental_detail', rental_id=rental_id))
