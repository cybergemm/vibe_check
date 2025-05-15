"""
Configuration file for the Flask application.
Defines environment variables, database settings, and other core configuration options.
"""
import os
# Get the absolute path of the directory containing this file
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Secret key for session management, CSRF protection, etc.
    # Falls back to 'dev' if SECRET_KEY is not set in the environment.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'

    # Database URI: uses environment variable DATABASE_URL if set,
    # otherwise defaults to a local SQLite database in the instance folder.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'app.db')
    
    # Disable tracking of object modifications to save resources.
    SQLALCHEMY_TRACK_MODIFICATIONS = False 
