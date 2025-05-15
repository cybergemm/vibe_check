from app import create_app
from app.models import db, User

app = create_app()

with app.app_context():
    user = User.query.filter_by(username='testuser').first()
    if not user:
        user = User(username='testuser')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        print("Added testuser with password 'password123'.")
    else:
        user.set_password('password123')
        db.session.commit()
        print("Updated testuser password to 'password123'.") 
