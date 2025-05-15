"""
test_auth.py

Tests for authentication-related routes including login and signup, 
covering both success and failure cases.
"""
from app.models import User

def test_login_success(client, test_user):
    # Attempt login with correct credentials for existing test_user
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'password123',
        'remember': False
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Welcome' in response.data # Check if welcome message is shown on success

def test_login_failure(client):
    # Attempt login with invalid credentials (wrong username and password)
    response = client.post('/login', data={
        'username': 'wronguser',
        'password': 'wrongpass',
        'remember': False
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data # Expect error message

def test_signup_success(client):
    # Attempt signup with a new username and matching passwords
    response = client.post('/signup', data={
        'username': 'newuser',
        'password': 'newpass',
        'confirm_password': 'newpass',
        'remember': False
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Registration successful' in response.data # Expect success message

def test_signup_failure(client, test_user):
    # Attempt signup with an existing username to test duplicate prevention
    response = client.post('/signup', data={
        'username': 'testuser',
        'password': 'newpass',
        'confirm_password': 'newpass',
        'remember': False
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Username already taken' in response.data # Expect error message
