import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User

def migrate():
    app = create_app()
    with app.app_context():
        # Add privacy_setting column with default value 'friends'
        db.engine.execute('ALTER TABLE user ADD COLUMN privacy_setting VARCHAR(20) DEFAULT "friends"')
        print("Added privacy_setting column to user table")

if __name__ == '__main__':
    migrate() 
