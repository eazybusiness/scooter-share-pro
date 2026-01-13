"""
Scooter management routes
"""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.web import bp
from app.services.scooter_service import ScooterService
from app.utils.qr_generator import generate_qr_code_image

scooter_service = ScooterService()

@bp.route('/scooters')
@login_required
def scooters_list():
    """List all scooters"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    if current_user.is_provider():
        scooters = scooter_service.get_scooters_by_provider(current_user.id, limit=per_page)
    else:
        scooters = scooter_service.get_all_scooters(limit=per_page, offset=offset)
    
    return render_template('scooters/list.html', scooters=scooters, page=page)

@bp.route('/scooters/available')
@login_required
def available_scooters():
    """List available scooters"""
    scooters = scooter_service.get_available_scooters(limit=50)
    return render_template('scooters/available.html', scooters=scooters)

@bp.route('/scooters/<int:scooter_id>')
@login_required
def scooter_detail(scooter_id):
    """Scooter detail page"""
    scooter = scooter_service.get_scooter_by_id(scooter_id)
    
    if not scooter:
        flash('Scooter not found.', 'danger')
        return redirect(url_for('web.scooters_list'))
    
    stats = scooter_service.get_scooter_statistics(scooter)
    
    # Generate QR code image
    qr_code_image = generate_qr_code_image(scooter.qr_code)
    
    return render_template('scooters/detail.html', scooter=scooter, stats=stats, qr_code_image=qr_code_image)

@bp.route('/scooters/create', methods=['GET', 'POST'])
@login_required
def create_scooter():
    """Create new scooter"""
    if not current_user.can_manage_scooters():
        flash('You are not authorized to create scooters.', 'danger')
        return redirect(url_for('web.dashboard'))
    
    if request.method == 'POST':
        license_plate = request.form.get('license_plate')
        model = request.form.get('model')
        latitude = float(request.form.get('latitude'))
        longitude = float(request.form.get('longitude'))
        battery_level = int(request.form.get('battery_level', 100))
        qr_code = request.form.get('qr_code')
        notes = request.form.get('notes')
        status = request.form.get('status', 'available')
        
        scooter, error = scooter_service.create_scooter(
            identifier=license_plate,
            model=model,
            brand=model,
            latitude=latitude,
            longitude=longitude,
            provider_id=current_user.id,
            battery_level=battery_level,
            qr_code=qr_code,
            notes=notes,
            status=status
        )
        
        if error:
            flash(error, 'danger')
            return render_template('scooters/create.html')
        
        flash('Scooter created successfully!', 'success')
        return redirect(url_for('web.scooter_detail', scooter_id=scooter.id))
    
    return render_template('scooters/create.html')

@bp.route('/scooters/<int:scooter_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_scooter(scooter_id):
    """Edit scooter"""
    scooter = scooter_service.get_scooter_by_id(scooter_id)
    
    if not scooter:
        flash('Scooter not found.', 'danger')
        return redirect(url_for('web.scooters_list'))
    
    if not current_user.is_admin() and scooter.provider_id != current_user.id:
        flash('You are not authorized to edit this scooter.', 'danger')
        return redirect(url_for('web.scooter_detail', scooter_id=scooter_id))
    
    if request.method == 'POST':
        update_data = {
            'identifier': request.form.get('license_plate'),
            'model': request.form.get('model'),
            'battery_level': int(request.form.get('battery_level')),
            'status': request.form.get('status'),
            'latitude': float(request.form.get('latitude')),
            'longitude': float(request.form.get('longitude')),
            'qr_code': request.form.get('qr_code'),
            'notes': request.form.get('notes')
        }
        
        updated_scooter, error = scooter_service.update_scooter(scooter, current_user, **update_data)
        
        if error:
            flash(error, 'danger')
        else:
            flash('Scooter updated successfully!', 'success')
            return redirect(url_for('web.scooter_detail', scooter_id=scooter_id))
    
    return render_template('scooters/edit.html', scooter=scooter)

@bp.route('/scooters/<int:scooter_id>/delete', methods=['POST'])
@login_required
def delete_scooter(scooter_id):
    """Delete scooter"""
    scooter = scooter_service.get_scooter_by_id(scooter_id)
    
    if not scooter:
        flash('Scooter not found.', 'danger')
        return redirect(url_for('web.scooters_list'))
    
    success, error = scooter_service.delete_scooter(scooter, current_user)
    
    if error:
        flash(error, 'danger')
        return redirect(url_for('web.scooter_detail', scooter_id=scooter_id))
    
    flash('Scooter deleted successfully!', 'success')
    return redirect(url_for('web.scooters_list'))

@bp.route('/scooters/<int:scooter_id>/maintenance', methods=['POST'])
@login_required
def set_maintenance(scooter_id):
    """Set scooter to maintenance"""
    scooter = scooter_service.get_scooter_by_id(scooter_id)
    
    if not scooter:
        flash('Scooter not found.', 'danger')
        return redirect(url_for('web.scooters_list'))
    
    success, error = scooter_service.set_maintenance(scooter, current_user)
    
    if error:
        flash(error, 'danger')
    else:
        flash('Scooter set to maintenance mode.', 'success')
    
    return redirect(url_for('web.scooter_detail', scooter_id=scooter_id))
