from app import create_app
from app.models import db, User, Mood, Friendship
from datetime import datetime

app = create_app()

with app.app_context():
    user1 = User(username="alice123")
    user2 = User(username="bob123")
    user3 = User(username="charlie123")
    db.session.add_all([user1, user2, user3])
    db.session.commit()

    mood1 = Mood(mood="Happy", timestamp=datetime.now(), user_id=user1.id)
    mood2 = Mood(mood="Sleepy", timestamp=datetime.now(), user_id=user1.id)
    db.session.add_all([mood1, mood2])
    db.session.commit()

    db.session.add_all([
        Friendship(user_id=user1.id, friend_id=user2.id), # Alice is friends with Bob
        Friendship(user_id=user2.id, friend_id=user1.id), # Bob is friends with Alice
        Friendship(user_id=user2.id, friend_id=user3.id), # Bob is friends with Charlie
        Friendship(user_id=user3.id, friend_id=user2.id), # Charlie is friends with Bob, but not Alice
    ])
    db.session.commit()

    print("Sample data seeded!")