"""
Script to populate the database with test users, friendships, friend requests,
and structured mood data for testing the application.
Run this before using other test scripts like add_mood_data.py.
"""
# Import necessary components: app factory, models, security tools, datetime, and randomization utilities.
from app import create_app
from app.models import db, User, Mood, Friendship, FriendRequest
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

# Initialize the Flask application.
app = create_app()

# Start application context for database operations.
def add_test_data():
    with app.app_context():
        # Define four test users with preset usernames and passwords.
        test_user1 = User(username='test1')
        test_user1.set_password('password123')
        
        test_user2 = User(username='test2')
        test_user2.set_password('password123')

        test_user3 = User(username='test3')
        test_user3.set_password('password123')

        test_user4 = User(username='test4')
        test_user4.set_password('password123')
        
        # Add and save all users to the database.
        db.session.add_all([test_user1, test_user2, test_user3, test_user4])
        db.session.commit()
        
        # Create a bidirectional friendship between test_user1 and test_user2.
        friendship1 = Friendship(user_id=test_user1.username, friend_id=test_user2.username)
        friendship2 = Friendship(user_id=test_user2.username, friend_id=test_user1.username)
        db.session.add_all([friendship1, friendship2])

        # Add two pending friend requests to test_user1 from users 3 and 4.
        friend_request1 = FriendRequest(sender_id=test_user3.username, receiver_id=test_user1.username, status='pending')
        friend_request2 = FriendRequest(sender_id=test_user4.username, receiver_id=test_user1.username, status='pending')
        db.session.add_all([friend_request1, friend_request2])
        
        # Generate moods for the last 30 days with focused patterns
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Predefined mood type based on the day of the week.
        mood_patterns = {
            'Monday': 'tired',
            'Tuesday': 'happy',
            'Wednesday': 'sad',
            'Thursday': 'happy',
            'Friday': 'happy',
            'Saturday': 'happy',
            'Sunday': 'tired'
        }
        
        # Define activity patterns for different moods
        activity_patterns = {
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
            'tired': [
                "Rested",
                "Did errands",
                "School/work/study/productivity",
                "Watched a film or television show",
                "Read"
            ]
        }
        
        # Loop over the last 30 days to generate mood data.
        current_date = start_date
        while current_date <= end_date:
            # Get the day name (e.g. Monday) and corresponding mood.
            day_name = current_date.strftime('%A')
            if day_name in mood_patterns:
                # Get the mood for this day
                mood_type = mood_patterns[day_name]
                
                # Assign a random time during the day for the mood.
                mood_time = current_date + timedelta(
                    hours=random.randint(8, 22),
                    minutes=random.randint(0, 59)
                )
                
                mood_activities = activity_patterns[mood_type]

                # Randomly select 1 to 3 appropriate reasons for the mood.
                num_reasons = random.randint(1, 3)
                selected_reasons = random.sample(mood_activities, min(num_reasons, len(mood_activities)))
                
                # Create and stage the mood entry for test_user1.
                mood = Mood(
                    mood=mood_type,
                    reasons=str(selected_reasons).replace("'", '"'),
                    timestamp=mood_time,
                    user_id=test_user1.username
                )
                db.session.add(mood)
            
            current_date += timedelta(days=1)
        
        # Add predefined mood entries for test_user2 for basic testing.
        mood1 = Mood(
            mood='happy',
            reasons='["Went outside", "Had good food or drinks", "Socialised"]',
            timestamp=datetime.now(),
            user_id=test_user2.username
        )
        
        mood2 = Mood(
            mood='tired',
            reasons='["Rested", "Did errands"]',
            timestamp=datetime.now(),
            user_id=test_user2.username
        )
        
        # Save all data to the database and confirm success.
        db.session.add_all([mood1, mood2])
        db.session.commit()
        
        print("Test data added successfully!")

# Run the function if the script is executed directly.
if __name__ == '__main__':
    add_test_data() 
