"""
Script to check rental ratings in the database
Run this on the production server to debug rating issues
"""

import os
import sys
from sqlalchemy import text

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db

def check_ratings():
    """Check ratings in the database"""
    app = create_app(os.getenv('FLASK_CONFIG', 'production'))
    
    with app.app_context():
        # Check all rentals with feedback
        print("=== Rentals with Feedback ===")
        result = db.session.execute(text("""
            SELECT id, rental_code, rating, feedback, status, created_at
            FROM rentals
            WHERE feedback IS NOT NULL
            ORDER BY created_at DESC
            LIMIT 10
        """))
        
        for row in result:
            print(f"ID: {row.id}, Code: {row.rental_code}")
            print(f"  Rating: {row.rating}")
            print(f"  Feedback: {row.feedback[:100] if row.feedback else None}...")
            print(f"  Status: {row.status}")
            print()
        
        # Check specific rental IDs if they exist
        print("\n=== Checking specific rentals (13, 14) ===")
        result = db.session.execute(text("""
            SELECT id, rental_code, rating, feedback, status, user_id, scooter_id
            FROM rentals
            WHERE id IN (13, 14)
        """))
        
        for row in result:
            print(f"ID: {row.id}, Code: {row.rental_code}")
            print(f"  Rating: {row.rating} (type: {type(row.rating)})")
            print(f"  Feedback: {row.feedback}")
            print(f"  Status: {row.status}")
            print()
        
        # Check database schema for rating column
        print("\n=== Rating Column Schema ===")
        result = db.session.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'rentals' AND column_name = 'rating'
        """))
        
        for row in result:
            print(f"Column: {row.column_name}")
            print(f"  Type: {row.data_type}")
            print(f"  Nullable: {row.is_nullable}")
            print(f"  Default: {row.column_default}")
        
        # Count rentals with ratings
        print("\n=== Rating Statistics ===")
        result = db.session.execute(text("""
            SELECT 
                COUNT(*) as total_rentals,
                COUNT(rating) as rentals_with_rating,
                COUNT(feedback) as rentals_with_feedback,
                COUNT(CASE WHEN rating IS NOT NULL AND feedback IS NOT NULL THEN 1 END) as with_both
            FROM rentals
        """))
        
        for row in result:
            print(f"Total rentals: {row.total_rentals}")
            print(f"With rating: {row.rentals_with_rating}")
            print(f"With feedback: {row.rentals_with_feedback}")
            print(f"With both: {row.with_both}")

if __name__ == "__main__":
    check_ratings()
