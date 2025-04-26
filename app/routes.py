from flask import Blueprint, render_template, session, jsonify, redirect, request, flash
from .models import db, User, Mood

main = Blueprint('main', __name__)
@main.route('/')
def intro():
    return render_template('intro.html')

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

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        print(username)
        password = request.form.get('password')
        print(password)

        user = User.query.filter_by(username=username).first()
        print("3")

        if user and user.password == password:
            session['user_id'] = user.id
            print("4")
            session['username'] = user.username
            print("5")
            flash('Logged in successfully!', 'success')
            print("6")
            return redirect("home")
        else:
            flash('Invalid username or password.', 'danger')
            print("7")

    return render_template('login.html')

@main.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect("intro.html")