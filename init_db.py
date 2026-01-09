"""
Database initialization script for Render.com deployment
Run this after first deployment to create all tables
"""

from app import create_app, db
from app.models import User, Scooter, Rental, Payment

def init_database():
    """Initialize database tables"""
    app = create_app('production')
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Check if admin exists
        admin = User.query.filter_by(email='admin@scootershare.com').first()
        if not admin:
            print("\nCreating default admin user...")
            admin = User(
                email='admin@scootershare.com',
                first_name='Admin',
                last_name='User',
                role='admin',
                is_active=True,
                is_verified=True
            )
            admin.set_password('Admin123!')
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created!")
            print("   Email: admin@scootershare.com")
            print("   Password: Admin123!")
            print("   ⚠️  CHANGE THIS PASSWORD IMMEDIATELY!")
        else:
            print("\n✅ Admin user already exists")
        
        print("\n🎉 Database initialization complete!")

if __name__ == '__main__':
    init_database()
