from app import create_app, db
from app.models import User, Mood, Friendship
import os

def create_database():
    # Create instance directory if it doesn't exist
    os.makedirs('instance', exist_ok=True)
    
    # Delete existing database file
    if os.path.exists('instance/mood_tracker.db'):
        os.remove('instance/mood_tracker.db')
    
    # Create new database
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Database created successfully!")

if __name__ == '__main__':
    create_database()
