"""
Script to populate the database with random mood entries over the past 30 days
for test users. Requires that test users already exist in the database.
"""
# Imports Flask app, models, datetime tools, and random utilities for mood generation.
from app import create_app
from app.models import db, User, Mood
from datetime import datetime, timedelta
import random

# Initialize the Flask application context.
app = create_app()

# Start the application context to interact with the database.
def add_mood_data():
    with app.app_context():
        # Retrieve predefined test users from the database.
        user1 = User.query.filter_by(username='test1').first()
        user2 = User.query.filter_by(username='test2').first()
        
        # Ensure the required test users exist before proceeding.
        if not user1 or not user2:
            print("Test users not found. Please run add_test_data.py first.")
            return

        # Dictionary mapping possible mood types to potential reasons.
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

        # Define the date range for mood generation. Generate moods for the last 30 days.
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        # Loop through each day in the 30-day range.
        current_date = start_date
        while current_date <= end_date:
            # Randomly decide how many moods to generate (2-4) per user per day.
            for user in [user1, user2]:
                num_moods = random.randint(2, 4)
                
                # Assign a random timestamp during the day for each mood.
                for _ in range(num_moods):
                    # Random time during the day
                    mood_time = current_date + timedelta(
                        hours=random.randint(8, 22),
                        minutes=random.randint(0, 59)
                    )
                    
                    # Choose a random mood type and 1–3 associated reasons.
                    mood_type = random.choice(list(mood_data.keys()))
                    num_reasons = random.randint(1, 3)
                    reasons = random.sample(mood_data[mood_type], min(num_reasons, len(mood_data[mood_type])))
                    
                    # Create and stage a Mood entry for insertion.
                    mood = Mood(
                        mood=mood_type,
                        reasons=str(reasons).replace("'", '"'),  # Convert to JSON string format
                        timestamp=mood_time,
                        user_id=user.username
                    )
                    db.session.add(mood)
            
            # Move to the next day in the date range.
            current_date += timedelta(days=1)

        # Commit all staged mood entries to the database.
        db.session.commit()
        print("Added comprehensive mood data for analysis!")

# Run the script directly if executed as the main module.
if __name__ == '__main__':
    add_mood_data() 
