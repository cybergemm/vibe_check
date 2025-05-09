from app import create_app
from app.models import db, User, Mood, Friendship, FriendRequest
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

app = create_app()

def add_test_data():
    with app.app_context():
        # Create test users
        test_user1 = User(username='test1')
        test_user1.set_password('password123')
        
        test_user2 = User(username='test2')
        test_user2.set_password('password123')

        test_user3 = User(username='test3')
        test_user3.set_password('password123')

        test_user4 = User(username='test4')
        test_user4.set_password('password123')
        
        # Add users to database
        db.session.add_all([test_user1, test_user2, test_user3, test_user4])
        db.session.commit()
        
        # Create friendship between users
        friendship1 = Friendship(user_id=test_user1.id, friend_id=test_user2.id)
        friendship2 = Friendship(user_id=test_user2.id, friend_id=test_user1.id)
        db.session.add_all([friendship1, friendship2])

        # Create friend request from test_user3 to test_user1
        friend_request1 = FriendRequest(sender_id=test_user3.id, receiver_id=test_user1.id, status='pending')
        friend_request2 = FriendRequest(sender_id=test_user4.id, receiver_id=test_user1.id, status='pending')
        db.session.add_all([friend_request1, friend_request2])
        
        # Define possible moods and their associated reasons
        mood_data = {
            'happy': [
                "Went outside",
                "Had good food or drinks",
                "Socialised",
                "Listened to music",
                "Watched a film or television show",
                "Took care of their health",
                "Played video games"
            ],
            'sad': [
                "Rested",
                "Had bad food or drinks",
                "School/work/study/productivity",
                "Did errands"
            ],
            'angry': [
                "School/work/study/productivity",
                "Did errands",
                "Had bad food or drinks",
                "Travelled"
            ],
            'tired': [
                "Rested",
                "Did errands",
                "School/work/study/productivity",
                "Watched a film or television show",
                "Read"
            ],
            'scared': [
                "Rested",
                "Read",
                "Did art",
                "Listened to music"
            ]
        }

        # Define mood patterns for days of the week (for test_user1)
        mood_patterns = {
            'Monday': 'tired',    # Tired on Mondays
            'Tuesday': 'happy',   # Happy on Tuesdays
            'Wednesday': 'sad',   # Sad on Wednesdays
            'Thursday': 'angry',  # Angry on Thursdays
            'Friday': 'happy',    # Happy on Fridays
            'Saturday': 'happy',  # Happy on Saturdays
            'Sunday': 'tired'     # Tired on Sundays
        }

        # Generate moods for the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        current_date = start_date
        while current_date <= end_date:
            # For test_user1, use the day-based pattern
            day_name = current_date.strftime('%A')
            if day_name in mood_patterns:
                mood_type = mood_patterns[day_name]
                mood_time = current_date + timedelta(
                    hours=random.randint(8, 22),
                    minutes=random.randint(0, 59)
                )
                num_reasons = random.randint(1, 3)
                reasons = random.sample(mood_data[mood_type], min(num_reasons, len(mood_data[mood_type])))
                
                mood = Mood(
                    mood=mood_type,
                    reasons=str(reasons).replace("'", '"'),
                    timestamp=mood_time,
                    user_id=test_user1.id
                )
                db.session.add(mood)

            # For test_user2, use random moods (2-4 per day)
            num_moods = random.randint(2, 4)
            for _ in range(num_moods):
                mood_time = current_date + timedelta(
                    hours=random.randint(8, 22),
                    minutes=random.randint(0, 59)
                )
                mood_type = random.choice(list(mood_data.keys()))
                num_reasons = random.randint(1, 3)
                reasons = random.sample(mood_data[mood_type], min(num_reasons, len(mood_data[mood_type])))
                
                mood = Mood(
                    mood=mood_type,
                    reasons=str(reasons).replace("'", '"'),
                    timestamp=mood_time,
                    user_id=test_user2.id
                )
                db.session.add(mood)
            
            current_date += timedelta(days=1)

        db.session.commit()
        print("Test data added successfully!")

if __name__ == '__main__':
    add_test_data() 
