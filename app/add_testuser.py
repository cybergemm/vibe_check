"""
add_testuser.py

This script creates or updates a test user account in the database with a predefined username and password.
It is useful for quickly setting up a test user for development or testing purposes.
"""
from app import create_app  # Import the Flask app factory
from app.models import db, User # Import the database and User model

app = create_app() # Create an instance of the Flask app

with app.app_context(): # Push the application context for database operations
    # Check if a user with username 'testuser' already exists
    user = User.query.filter_by(username='testuser').first()
    
    # If not found, create a new user with username 'testuser'
    if not user:
        user = User(username='testuser')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        print("Added testuser with password 'password123'.")
    
     # If user exists, update the password to 'password123'
    else:
        user.set_password('password123')
        db.session.commit()
        print("Updated testuser password to 'password123'.") 
