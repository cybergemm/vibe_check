from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import os
try:
    from flask_wtf import CSRFProtect
    csrf_available = True
except ImportError:
    csrf_available = False
    print("WARNING: flask_wtf is not installed. CSRF protection is disabled.")

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    if csrf_available:
        csrf = CSRFProtect(app)  # moved here to use app context directly

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # Create instance directory for database
    os.makedirs(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance'), exist_ok=True)

    from app.models import User, Mood, Friendship

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(str(id))

    return app
