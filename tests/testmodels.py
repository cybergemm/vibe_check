from app.models import User, Mood
from app import db

def test_user_creation(app):
    user = User(username='newuser')
    user.set_password('newpassword')
    db.session.add(user)
    db.session.commit()
    assert User.query.filter_by(username='newuser').first() is not None

def test_password_hashing(app):
    user = User(username='hashuser')
    user.set_password('hashpassword')
    assert user.check_password('hashpassword') is True
    assert user.check_password('wrongpassword') is False

def test_mood_creation(app, test_user):
    mood = Mood(mood='Happy', reasons='["Went outside"]', timestamp='2023-01-01T00:00:00', user_id=test_user.username)
    db.session.add(mood)
    db.session.commit()
    assert Mood.query.filter_by(user_id=test_user.username).first() is not None 
