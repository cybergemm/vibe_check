from app import create_app
from app.models import db, User, Mood, Friendship
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
        
        # Add users to database
        db.session.add_all([test_user1, test_user2])
        db.session.commit()
        
        # Create friendship between users
        friendship = Friendship(user_id=test_user1.id, friend_id=test_user2.id)
        db.session.add(friendship)
        
        # Create comprehensive mood data for test_user1
        mood_types = ['happy', 'sad', 'angry', 'tired', 'scared']
        reasons = [
            "Went outside", "Took care of their health", "Played video games",
            "School/work/study/productivity", "Had good food or drinks",
            "Had bad food or drinks", "Travelled", "Socialised",
            "Listened to music", "Watched a film or television show",
            "Read", "Did art", "Rested", "Did errands"
        ]
        
        # Generate moods for the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        current_date = start_date
        while current_date <= end_date:
            # Add 3-5 moods per day
            num_moods = random.randint(3, 5)
            for _ in range(num_moods):
                # Random time during the day
                mood_time = current_date + timedelta(
                    hours=random.randint(8, 22),
                    minutes=random.randint(0, 59)
                )
                
                # Random mood and reasons
                mood_type = random.choice(mood_types)
                num_reasons = random.randint(1, 3)
                selected_reasons = random.sample(reasons, num_reasons)
                
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
