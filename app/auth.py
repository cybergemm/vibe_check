"""
Handles user authentication for the Vibe Check web app, including login, signup, and logout 
routes using Flask-Login, WTForms for form validation, and database integration for user management.
"""
# Import necessary modules, forms, and models for user authentication functionality.
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, login_user, current_user, logout_user
from werkzeug.urls import url_parse
from app import db
from app.forms import LoginForm  # Import the LoginForm class
from app.forms import SignupForm  # Import SignupForm
from app.models import User

# Create a blueprint named 'auth' for authentication-related routes.
bp = Blueprint('auth', __name__)

from app.forms import LoginForm  # Make sure LoginForm is imported

# Route to handle user login; displays form and processes login submission.
@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect already-logged-in users to the home page.
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Instantiate and validate the login form.
    form = LoginForm()  # Create a form instance
    if form.validate_on_submit():  # This replaces checking 'POST' manually
        # Extract login credentials and remember-me option from the form.
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        
        # Check credentials; if invalid, flash error and reload login page.
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('Invalid username or password', "danger")
            return redirect(url_for('auth.login'))
        
        # Log the user in and redirect to the intended or default page.
        login_user(user, remember=remember)
        flash('Welcome', 'success')
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    
    # Render the login page with the form.
    return render_template('login.html', form=form)  # Pass form to template

# Route to handle user registration; displays form and processes new user creation.
@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    # Redirect logged-in users from signup page to main index.
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Instantiate and validate the signup form.
    form = SignupForm()  # Create the form instance
    if form.validate_on_submit():  # Use Flask-WTF's validation
        # Extract new user data from the form.
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        
        # Check if username is taken; if so, flash warning and reload signup.
        if User.query.filter_by(username=username).first():
            flash('Username already taken', "warning")
            return render_template('signup.html', form=form)
        
        # Create new user, hash password, and add them to the database.
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Confirm success and redirect user to login page.
        flash('Registration successful', "success")
        return redirect(url_for('auth.login'))
    
    # Render the signup page with the form.
    return render_template('signup.html', form=form)  # Pass form to template

# Route to log out an authenticated user.
@login_required
@bp.route('/logout')
def logout():
    # End user session, flash confirmation, and redirect to login.
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for('auth.login'))
