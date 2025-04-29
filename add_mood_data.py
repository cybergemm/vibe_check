from app import create_app
from app.models import db, User, Mood
from datetime import datetime, timedelta
import random

app = create_app()

def add_mood_data():
    with app.app_context():
        # Get our test users
        user1 = User.query.filter_by(email='test1@example.com').first()
        user2 = User.query.filter_by(email='test2@example.com').first()
        
        if not user1 or not user2:
            print("Test users not found. Please run add_test_data.py first.")
            return

        # Define possible moods and their associated reasons
        mood_data = {
            'Happy': [
                "Went outside",
                "Had good food or drinks",
                "Socialised",
                "Listened to music",
                "Watched a film or television show"
            ],
            'Calm': [
                "Rested",
                "Read",
                "Did art",
                "Listened to music"
            ],
            'Energetic': [
                "Went outside",
                "Took care of their health",
                "Played video games",
                "School/work/study/productivity"
            ],
            'Tired': [
                "Rested",
                "Did errands",
                "School/work/study/productivity"
            ],
            'Stressed': [
                "School/work/study/productivity",
                "Did errands",
                "Had bad food or drinks"
            ]
        }

        # Generate moods for the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        current_date = start_date
        while current_date <= end_date:
            # Add 1-3 moods per day for each user
            for user in [user1, user2]:
                num_moods = random.randint(1, 3)
                for _ in range(num_moods):
                    # Random time during the day
                    mood_time = current_date + timedelta(
                        hours=random.randint(8, 22),
                        minutes=random.randint(0, 59)
                    )
                    
                    # Random mood and reasons
                    mood_type = random.choice(list(mood_data.keys()))
                    num_reasons = random.randint(1, 3)
                    reasons = random.sample(mood_data[mood_type], min(num_reasons, len(mood_data[mood_type])))
                    
                    mood = Mood(
                        mood=mood_type,
                        reasons=str(reasons).replace("'", '"'),  # Convert to JSON string format
                        timestamp=mood_time,
                        user_id=user.id
                    )
                    db.session.add(mood)
            
            current_date += timedelta(days=1)

        db.session.commit()
        print("Added comprehensive mood data for analysis!")

if __name__ == '__main__':
    add_mood_data() 
