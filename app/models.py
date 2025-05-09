from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db
import json

class Friendship(db.Model):
    __tablename__ = 'friendships'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(100))
    username = db.Column(db.String(30), nullable=False, unique=True)
    moods = db.relationship('Mood', backref='user', lazy=True)
    friends = db.relationship(
        'User',
        secondary='friendships',
        primaryjoin=id==Friendship.user_id,
        secondaryjoin=id==Friendship.friend_id,
        backref='friend_of'
    )

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Mood(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mood = db.Column(db.String(50), nullable=False)
    reasons = db.Column(db.String(500), nullable=True)  # JSON string of selected reasons
    timestamp = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

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

    def set_reasons(self, reasons_list):
        self.reasons = json.dumps(reasons_list)

    def get_reasons(self):
        return json.loads(self.reasons) if self.reasons else []

    def to_dict(self):
        return {
            'id': self.id,
            'mood': self.mood,
            'reasons': self.get_reasons(),
            'timestamp': self.timestamp.isoformat(),
            'user_id': self.user_id
        }

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
