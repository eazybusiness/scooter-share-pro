"""
Web authentication routes
"""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.web import bp
from app.services.auth_service import AuthService

auth_service = AuthService()

@bp.route('/')
def index():
    """Homepage"""
    if current_user.is_authenticated:
        return redirect(url_for('web.dashboard'))
    return render_template('index.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('web.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user, error = auth_service.login_user(email, password)
        
        if error:
            flash(error, 'danger')
            return render_template('auth/login.html')
        
        login_user(user)
        flash('Login successful!', 'success')
        
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('web.dashboard'))
    
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('web.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        role = request.form.get('role', 'customer')
        
        user, error = auth_service.register_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            phone=phone
        )
        
        if error:
            flash(error, 'danger')
            return render_template('auth/register.html')
        
        login_user(user)
        flash('Registration successful!', 'success')
        return redirect(url_for('web.dashboard'))
    
    return render_template('auth/register.html')

@bp.route('/logout')
@login_required
def logout():
    """Logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('web.index'))

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page"""
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        
        updated_user, error = auth_service.update_profile(
            current_user,
            first_name=first_name,
            last_name=last_name,
            phone=phone
        )
        
        if error:
            flash(error, 'danger')
        else:
            flash('Profile updated successfully!', 'success')
        
        return redirect(url_for('web.profile'))
    
    return render_template('auth/profile.html', user=current_user)

@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password page"""
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return render_template('auth/change_password.html')
        
        success, error = auth_service.change_password(
            current_user,
            old_password,
            new_password
        )
        
        if error:
            flash(error, 'danger')
        else:
            flash('Password changed successfully!', 'success')
            return redirect(url_for('web.profile'))
    
    return render_template('auth/change_password.html')
