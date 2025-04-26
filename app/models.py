from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Friendship(db.Model):
    __tablename__ = 'friendships'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    moods = db.relationship('Mood', backref='user', lazy=True)
    friends = db.relationship(
        'User',
        secondary='friendships',
        primaryjoin=id==Friendship.user_id,
        secondaryjoin=id==Friendship.friend_id,
        backref='friend_of'
    )

class Mood(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mood = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

