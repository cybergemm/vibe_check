import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Mood, Friendship
from datetime import datetime, timedelta
import random

def create_test_data():
    app = create_app()
    with app.app_context():
        # Create test users if they don't exist
        test_users = [
            {
                'email': 'test1@example.com',
                'name': 'Test User 1',
                'phone': '1234567890',
                'username': 'testuser1'
            },
            {
                'email': 'test2@example.com',
                'name': 'Test User 2',
                'phone': '2345678901',
                'username': 'testuser2'
            }
        ]
        
        users = []
        for user_data in test_users:
            user = User.query.filter_by(email=user_data['email']).first()
            if not user:
                user = User(
                    email=user_data['email'],
                    name=user_data['name'],
                    phone=user_data['phone'],
                    username=user_data['username']
                )
                user.set_password('password123')
                db.session.add(user)
            users.append(user)
        
        # Create friendship between users
        # Create bidirectional friendship
        friendship1 = Friendship.query.filter_by(
            user_id=users[0].id,
            friend_id=users[1].id
        ).first()
        friendship2 = Friendship.query.filter_by(
            user_id=users[1].id,
            friend_id=users[0].id
        ).first()
        
        if not friendship1:
            friendship1 = Friendship(user_id=users[0].id, friend_id=users[1].id)
            db.session.add(friendship1)
            print(f"Created friendship: {users[0].email} -> {users[1].email}")
        if not friendship2:
            friendship2 = Friendship(user_id=users[1].id, friend_id=users[0].id)
            db.session.add(friendship2)
            print(f"Created friendship: {users[1].email} -> {users[0].email}")
        
        # Verify friendships after creation
        db.session.commit()
        print("\nVerifying friendships:")
        for user in users:
            print(f"\nFriends of {user.email}:")
            for friend in user.friends:
                print(f"- {friend.email}")
        
        # Create mood data for the last 30 days
        moods = ['happy', 'sad', 'excited', 'calm', 'anxious']
        all_reasons = Mood.get_all_reasons()
        
        for user in users:
            # Create moods for the last 30 days
            for days_ago in range(30):
                date = datetime.now() - timedelta(days=days_ago)
                # 70% chance of having a mood for each day
                if random.random() < 0.7:
                    mood = Mood(
                        mood=random.choice(moods),
                        timestamp=date,
                        user_id=user.id
                    )
                    # Randomly select 1-3 reasons
                    selected_reasons = random.sample(all_reasons, random.randint(1, 3))
                    mood.set_reasons(selected_reasons)
                    db.session.add(mood)
        
        db.session.commit()
        print("Test data created successfully!")

if __name__ == '__main__':
    create_test_data() 
