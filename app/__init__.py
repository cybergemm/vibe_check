"""
Initializes the Flask application, configures extensions such as SQLAlchemy and Flask-Login, 
sets up CSRF protection if available, registers blueprints for routing, and prepares the 
instance folder and user loading mechanism for the Vibe Check web app.
"""
# Import necessary libraries and modules for Flask app setup, database, login handling, configuration, and file operations.
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import os

# Attempt to import CSRF protection; disable it with a warning if not available.
try:
    from flask_wtf import CSRFProtect
    csrf_available = True
except ImportError:
    csrf_available = False
    print("WARNING: flask_wtf is not installed. CSRF protection is disabled.")

# Initialize database and login manager; set the default login route.
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

#Create and configure the Flask app using the specified configuration class.
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Apply CSRF protection to the app if available.
    if csrf_available:
        csrf = CSRFProtect(app)  # moved here to use app context directly

    # Initialize database and login manager with the app instance. 
    db.init_app(app)
    login_manager.init_app(app)

    # Import and register authentication and main route blueprints. 
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # Ensure that the instance folder exists to store the database and configuration files.
    os.makedirs(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance'), exist_ok=True)

    # Import database models to ensure they are recognized by SQLAlchemy.
    from app.models import User, Mood, Friendship

    # Define a user loader callback for Flask-Login to retrieve a user by ID.
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(str(id))

    return app # Return the fully configured Flask app instance.
