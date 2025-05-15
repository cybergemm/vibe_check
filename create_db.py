"""
Script to initialize (or reset) the application database.
Deletes any existing database file and recreates a new one with all tables defined in models.
"""
from app import create_app, db
from app.models import User, Mood, Friendship
import os

def create_database():
    # Ensure the instance directory exists to store the SQLite database
    os.makedirs('instance', exist_ok=True)
    
    # Delete the existing database file to start fresh (for development/testing)
    if os.path.exists('instance/app.db'):
        os.remove('instance/app.db')
    
    # Create a new Flask app and database
    app = create_app()
    with app.app_context():
        # Create all tables defined in the app's models
        db.create_all()
        print("Database created successfully!")

# Run the function if this script is executed directly
if __name__ == '__main__':
    create_database()
