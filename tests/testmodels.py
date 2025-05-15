"""
testmodels.py

Unit tests for the User and Mood models, verifying user creation, password hashing,
and mood entry creation tied to a user.
"""
from app.models import User, Mood
from app import db

def test_user_creation(app):
    # Test that a new user can be created and committed to the database
    user = User(username='newuser')
    user.set_password('newpassword')
    db.session.add(user)
    db.session.commit()
    assert User.query.filter_by(username='newuser').first() is not None

def test_password_hashing(app):
    # Test password hashing: correct password validates, wrong password fails
    user = User(username='hashuser')
    user.set_password('hashpassword')
    assert user.check_password('hashpassword') is True
    assert user.check_password('wrongpassword') is False

def test_mood_creation(app, test_user):
    # Test mood creation linked to a user
    mood = Mood(mood='Happy', reasons='["Went outside"]', timestamp='2023-01-01T00:00:00', user_id=test_user.username)
    db.session.add(mood)
    db.session.commit()
    assert Mood.query.filter_by(user_id=test_user.username).first() is not None 
