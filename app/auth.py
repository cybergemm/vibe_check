from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, login_user, current_user, logout_user
from werkzeug.urls import url_parse
from app import db
from app.forms import LoginForm  # Import the LoginForm class
from app.forms import SignupForm  # Import SignupForm
from app.models import User

bp = Blueprint('auth', __name__)

from app.forms import LoginForm  # Make sure LoginForm is imported

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()  # Create a form instance
    if form.validate_on_submit():  # This replaces checking 'POST' manually
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    
    return render_template('login.html', form=form)  # Pass form to template

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = SignupForm()  # Create the form instance
    if form.validate_on_submit():  # Use Flask-WTF's validation
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken.')
            return redirect(url_for('auth.signup'))
        
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('auth.login'))
    
    return render_template('signup.html', form=form)  # Pass form to template

@login_required
@bp.route('/logout')
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('auth.login'))
