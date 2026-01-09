#!/usr/bin/env python3
"""
Scooter Share Pro - Main application entry point
Enterprise E-Scooter Rental Platform
"""

import os
from app import create_app, db
from app.models import User, Scooter, Rental, Payment

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_context():
    """Make database models available in Flask shell"""
    return dict(db=db, User=User, Scooter=Scooter, Rental=Rental, Payment=Payment)

@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print('Database initialized.')

@app.cli.command()
def create_admin():
    """Create an admin user"""
    from app.services.auth_service import AuthService
    
    email = input('Enter admin email: ')
    password = input('Enter admin password: ')
    
    auth_service = AuthService()
    admin = auth_service.create_user(
        email=email,
        password=password,
        first_name='Admin',
        last_name='User',
        role='admin'
    )
    
    if admin:
        print(f'Admin user {email} created successfully.')
    else:
        print('Failed to create admin user.')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
