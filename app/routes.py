from flask import Blueprint, render_template, session, jsonify, redirect, request, flash
from .models import db, User, Mood

main = Blueprint('main', __name__)

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        full_name = request.form['full_name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        # Create a new user instance
        new_user = User(username=username, full_name=full_name, email=email, phone=phone, password=password)

        # Add to database
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully!')
        return redirect('home.html')  # or redirect to a home page

    return render_template('signup.html')

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