from app import create_app
from app.models import db, User, Mood, Friendship
from werkzeug.security import generate_password_hash
from datetime import datetime

app = create_app()

def add_test_data():
    with app.app_context():
        # Create test users
        test_user1 = User(username='testuser1')
        test_user1.set_password('password123')
        
        test_user2 = User(username='testuser2')
        test_user2.set_password('password123')
        
        # Add users to database
        db.session.add_all([test_user1, test_user2])
        db.session.commit()
        
        # Create friendship between users
        friendship = Friendship(user_id=test_user1.id, friend_id=test_user2.id)
        db.session.add(friendship)
        
        # Create some mood entries
        mood1 = Mood(
            mood='Happy',
            reasons='["Went outside", "Had good food or drinks"]',
            timestamp=datetime.now(),
            user_id=test_user1.id
        )
        
        mood2 = Mood(
            mood='Sleepy',
            reasons='["Rested"]',
            timestamp=datetime.now(),
            user_id=test_user2.id
        )
        
        db.session.add_all([mood1, mood2])
        db.session.commit()
        
        print("Test data added successfully!")

if __name__ == '__main__':
    add_test_data() 
