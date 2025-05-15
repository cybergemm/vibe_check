"""
Migration script to add a 'privacy_setting' column to the User table.
This column controls visibility of user mood data, defaulting to 'friends'.
"""
import os
import sys

# Ensure the parent directory is in the path so the app module can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User

def migrate():
    # Create a Flask app context to work with the database
    app = create_app()
    with app.app_context():
        # Perform raw SQL command to add a new column for privacy settings with defaul value 'friends'.
        db.engine.execute('ALTER TABLE user ADD COLUMN privacy_setting VARCHAR(20) DEFAULT "friends"')
        print("Added privacy_setting column to user table")

# Run the migration when this script is executed directly
if __name__ == '__main__':
    migrate() 
