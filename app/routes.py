from flask import Blueprint, render_template, session, jsonify
from .models import db, User, Mood

main = Blueprint('main', __name__)

@main.route('/home')
def home():
    user_id = 1 # For testing, we are hardcoding the user_id to 1. In a real app, this would come from session or auth.
    user = User.query.get(user_id)

    return render_template('home.html', user=user)

@main.route('/api/user_moods')
def get_user_moods():
    user_id = 1 # For testing, we are hardcoding the user_id to 1. In a real app, this would come from session or auth.
    moods = Mood.query.filter_by(user_id=user_id).order_by(Mood.timestamp.desc()).limit(5).all()
    return jsonify([{'mood': m.mood, 'timestamp': m.timestamp.isoformat()} for m in moods])

@main.route('/api/friends')
def get_friends():
    user_id = 1 # For testing, we are hardcoding the user_id to 1. In a real app, this would come from session or auth.
    user = User.query.get(user_id)
    return jsonify([friend.username for friend in user.friends])