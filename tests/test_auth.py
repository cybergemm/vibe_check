from app.models import User

def test_login_success(client, test_user):
    response = client.post('/login', data={'username': 'testuser', 'password': 'password123'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Welcome' in response.data

def test_login_failure(client):
    response = client.post('/login', data={'username': 'wronguser', 'password': 'wrongpass'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data

def test_signup_success(client):
    response = client.post('/signup', data={'username': 'newuser', 'password': 'newpass'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Registration successful' in response.data

def test_signup_failure(client, test_user):
    response = client.post('/signup', data={'username': 'testuser', 'password': 'newpass'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Username already taken' in response.data 
