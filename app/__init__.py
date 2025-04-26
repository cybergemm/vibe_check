from flask import Flask
from .models import db
from .routes import main

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vibecheck.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'dev'
    db.init_app(app)
    app.register_blueprint(main)

    return app