import pytest
from app import create_app, db
from app.models import User

@pytest.fixture
def app():
    app = create_app('config.TestingConfig')
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF protection for tests
    app.config['TESTING'] = True  # Enable testing mode
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def test_user(app):
    user = User(username='testuser')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    return user 
