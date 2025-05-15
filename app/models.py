"""
Defines the database models for the Vibe Check web application, including User accounts,
friendship relationships, mood entries, and friend requests, with methods for authentication,
mood serialization, and filtering.
"""
# Import necessary modules for password hashing, login support, and database access.
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db
import json

# Represents a many-to-many relationship table for user friendships.
class Friendship(db.Model):
    __tablename__ = 'friendships'
    user_id = db.Column(db.String(30), db.ForeignKey('user.username'), primary_key=True)
    friend_id = db.Column(db.String(30), db.ForeignKey('user.username'), primary_key=True)

# Main User model including login support, password handling, privacy, and friend connections.    
class User(UserMixin, db.Model):
    username = db.Column(db.String(30), primary_key=True)
    password = db.Column(db.String(100))
    privacy_setting = db.Column(db.String(20), default='friends')  # Can be 'public', 'friends', or 'private'
    moods = db.relationship('Mood', backref='user', lazy=True)
    friends = db.relationship(
        'User',
        secondary='friendships',
        primaryjoin=username==Friendship.user_id,
        secondaryjoin=username==Friendship.friend_id,
        backref='friend_of'
    )

    # Returns the username as the unique user identifier for Flask-Login.
    def get_id(self):
        return self.username
    
    # Methods for securely setting and checking hashed passwords.
    def set_password(self, password):
        self.password = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password, password)

# Represents a friend request between two users with status and timestamp.    
class FriendRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.String(30), db.ForeignKey('user.username'), nullable=False)
    receiver_id = db.Column(db.String(30), db.ForeignKey('user.username'), nullable=False)
    status = db.Column(db.String(20), default='pending')  
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])

# Stores an individual mood entry with reasons, timestamp, and related user.
class Mood(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mood = db.Column(db.String(50), nullable=False)
    reasons = db.Column(db.String(500), nullable=True)  # JSON string of selected reasons
    timestamp = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.String(30), db.ForeignKey('user.username'), nullable=False)

    # Static method returning all possible mood reasons as a list.
    @staticmethod
    def get_all_reasons():
        return [
            "Went outside",
            "Took care of their health",
            "Played video games",
            "School/work/study/productivity",
            "Had good food or drinks",
            "Had bad food or drinks",
            "Travelled",
            "Socialised",
            "Listened to music",
            "Watched a film or television show",
            "Read",
            "Did art",
            "Rested",
            "Did errands"
        ]
    
    # Methods to encode and decode reasons stored as JSON.
    def set_reasons(self, reasons_list):
        self.reasons = json.dumps(reasons_list)
    def get_reasons(self):
        return json.loads(self.reasons) if self.reasons else []
    
    # Converts a mood object into a dictionary for JSON serialization.
    def to_dict(self):
        return {
            'id': self.id,
            'mood': self.mood,
            'reasons': self.get_reasons(),
            'timestamp': self.timestamp.isoformat(),
            'user_id': self.user_id
        }
    
    # Static method to fetch all moods for a user within a specified date range, grouped by day.
    @staticmethod
    def get_moods_for_date_range(user_id, start_date, end_date):
        """Get all moods for a user within a date range."""
        moods = Mood.query.filter(
            Mood.user_id == user_id,
            Mood.timestamp >= start_date,
            Mood.timestamp <= end_date
        ).order_by(Mood.timestamp).all()
        
        # Organize moods by date
        mood_dict = {}
        for mood in moods:
            date_str = mood.timestamp.strftime('%Y-%m-%d')
            mood_dict[date_str] = mood
            
        return mood_dict
