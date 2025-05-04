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
        friendship = Friendship(user_id=test_user1.id, friend_id=test_user2.id)
        db.session.add(friendship)

        # Create friend request from test_user3 to test_user1
        friend_request1 = FriendRequest(sender_id=test_user3.id, receiver_id=test_user1.id, status='pending')
        friend_request2 = FriendRequest(sender_id=test_user4.id, receiver_id=test_user1.id, status='pending')
        db.session.add_all([friend_request1, friend_request2])
        
        # Create comprehensive mood data for test_user1
        reasons = [
            "Went outside", "Took care of their health", "Played video games",
            "School/work/study/productivity", "Had good food or drinks",
            "Had bad food or drinks", "Travelled", "Socialised",
            "Listened to music", "Watched a film or television show",
            "Read", "Did art", "Rested", "Did errands"
        ]
        
        # Generate moods for the last 30 days with focused patterns
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Define mood patterns for days of the week
        mood_patterns = {
            'Monday': 'tired',    # Tired on Mondays
            'Tuesday': 'happy',   # Happy on Tuesdays
            'Wednesday': 'sad',   # Sad on Wednesdays
            'Thursday': 'angry',  # Angry on Thursdays
            'Friday': 'happy',    # Happy on Fridays
            'Saturday': 'happy',  # Happy on Saturdays
            'Sunday': 'tired'     # Tired on Sundays
        }
        
        # Define activity patterns
        activity_patterns = {
            'happy': ["Went outside", "Had good food or drinks", "Socialised", "Listened to music"],
            'sad': ["Rested", "Had bad food or drinks", "School/work/study/productivity"],
            'angry': ["School/work/study/productivity", "Did errands", "Had bad food or drinks"],
            'tired': ["Rested", "Did errands", "School/work/study/productivity"],
            'scared': ["Rested", "Read", "Did art"]
        }
        
        current_date = start_date
        while current_date <= end_date:
            day_name = current_date.strftime('%A')
            if day_name in mood_patterns:
                # Get the mood for this day
                mood_type = mood_patterns[day_name]
                
                # Random time during the day
                mood_time = current_date + timedelta(
                    hours=random.randint(8, 22),
                    minutes=random.randint(0, 59)
                )
                
                # Get activities for this mood type
                mood_activities = activity_patterns[mood_type]
                num_reasons = random.randint(1, 3)
                selected_reasons = random.sample(mood_activities, min(num_reasons, len(mood_activities)))
                
                mood = Mood(
                    mood=mood_type,
                    reasons=str(selected_reasons).replace("'", '"'),
                    timestamp=mood_time,
                    user_id=test_user1.id
                )
                db.session.add(mood)
            
            current_date += timedelta(days=1)
        
        # Create some initial mood entries for test_user2
        mood1 = Mood(
            mood='happy',
            reasons='["Went outside", "Had good food or drinks", "Socialised"]',
            timestamp=datetime.now(),
            user_id=test_user2.id
        )
        
        mood2 = Mood(
            mood='tired',
            reasons='["Rested", "Did errands"]',
            timestamp=datetime.now(),
            user_id=test_user2.id
        )
        
        db.session.add_all([mood1, mood2])
        db.session.commit()
        
        print("Test data added successfully!")

if __name__ == '__main__':
    add_test_data() 
