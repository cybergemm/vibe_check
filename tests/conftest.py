"""
conftest.py

Pytest fixtures to set up the Flask app, test client, CLI runner, and a test user for use in tests.
"""
import pytest
from app import create_app, db
from app.models import User

@pytest.fixture
def app():
    # Create a Flask app instance configured for testing
    app = create_app('config.TestingConfig')
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for tests (simplifies form testing)
    app.config['TESTING'] = True  # Enable testing mode to propagate errors
    with app.app_context():
        db.create_all() # Create all database tables
        yield app # Provide the app instance to tests
        db.session.remove() # Clean up the session
        db.drop_all() # Drop all tables to reset state after tests

@pytest.fixture
def client(app):
    # Provide a test client for making HTTP requests to the app
    return app.test_client()

@pytest.fixture
def runner(app):
    # Provide a test CLI runner for invoking Flask CLI commands in tests
    return app.test_cli_runner()

@pytest.fixture
def test_user(app):
    # Create and add a test user to the database for use in tests
    user = User(username='testuser')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    return user 
