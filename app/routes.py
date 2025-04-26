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

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Logged in successfully!', 'success')
            return redirect("home")
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')


@main.route('/home')
def home():
    user_id = session.get('user_id')
    user = User.query.get(user_id)

    return render_template('home.html', user=user)

@main.route('/api/user_moods')
def get_user_moods():
    user_id = session.get('user_id')
    moods = Mood.query.filter_by(user_id=user_id).order_by(Mood.timestamp.desc()).limit(5).all()
    return jsonify([{'mood': m.mood, 'timestamp': m.timestamp.isoformat()} for m in moods])

@main.route('/api/friends')
def get_friends():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    return jsonify([friend.username for friend in user.friends])


@main.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect("intro.html")