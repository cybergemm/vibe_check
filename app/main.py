'''
main.py - Core Flask routes and view functions for the Mood Tracking app.

Handles user authentication, mood submission, mood analysis, friend management 
(friend requests, accept/decline, removal), privacy settings, password changes, 
account deletion, and mood calendar display.

Includes API endpoints for user search and mood data retrieval to support 
frontend interactivity.

All routes require user login to protect privacy and data integrity.
'''
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, Mood, Friendship, FriendRequest, db
from datetime import datetime, timedelta
from flask_wtf import FlaskForm
from app.forms import ChangePasswordForm, PrivacyForm, DeleteAccountForm

bp = Blueprint('main', __name__)

# A default route to the intropage.html
@bp.route('/')
def intro():
    # Redirect to the home page
    return render_template('intropage.html')

# A route into home.html after successful user log in.
@bp.route('/index')
@login_required
def index():
    return redirect(url_for('main.home'))

# displays the logged-in user's daily mood (if submitted), the moods of their friends for today, 
# and a list of predefined mood reasons on the /home page.
@bp.route('/home')
@login_required
def home():
    
    # Get today's date
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    # Check if user has already submitted a mood today
    today_mood = Mood.query.filter(
        Mood.user_id == current_user.username,
        Mood.timestamp >= today_start,
        Mood.timestamp <= today_end
    ).first()
    
    # Get friends with their today's mood
    friends = []
    for friend in current_user.friends:
        friend_mood = Mood.query.filter(
            Mood.user_id == friend.username,
            Mood.timestamp >= today_start,
            Mood.timestamp <= today_end
        ).first()
        friends.append({
            'username': friend.username,
            'today_mood': friend_mood
        })
    
    return render_template('home.html',
                         today_mood=today_mood,
                         friends=friends,
                         reasons=Mood.get_all_reasons(), 
                         user_id=current_user.username)

# This function securely handles user password changes by verifying the current password, 
# confirming the new password, updating it if valid, and displaying success or error messages as appropriate.  
@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    change_form = ChangePasswordForm()
    privacy_form = PrivacyForm()
    delete_form = DeleteAccountForm()
    privacy_form.privacy_setting.data = current_user.privacy_setting
    if change_form.validate_on_submit():
        current = change_form.current_password.data
        new = change_form.new_password.data
        confirm = change_form.confirm_new_password.data

        # if password fields are incorrect (respective issue error messages)
        if not check_password_hash(current_user.password, current):
            flash('Current password is incorrect.', 'danger')
        elif new != confirm:
            flash('New passwords do not match.', 'danger')
        else:
            current_user.password = generate_password_hash(new)
            db.session.commit()
            flash('Your password has been updated.', 'success')
            return redirect(url_for('main.change_password'))

    return render_template(
        'changepassword.html',
        change_form=change_form,
        privacy_form=privacy_form,
        delete_form=delete_form
    )

# This function securely deletes the current user’s account and all associated data if they submit a valid deletion form, 
# ensuring data cleanup and proper user feedback.
@bp.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    form = DeleteAccountForm()
    if form.validate_on_submit():
        # Delete all user's moods
        Mood.query.filter_by(user_id=current_user.username).delete()
        
        # Delete all friendships
        Friendship.query.filter_by(user_id=current_user.username).delete()
        Friendship.query.filter_by(friend_id=current_user.username).delete()
        
        # Delete all friend requests
        FriendRequest.query.filter_by(sender_id=current_user.username).delete()
        FriendRequest.query.filter_by(receiver_id=current_user.username).delete()
        
        # Delete the user
        db.session.delete(current_user)
        db.session.commit()
        
        flash('Your account has been deleted successfully.', 'success')
        return redirect(url_for('auth.login'))
    
    flash('Form submission failed. Please try again.', 'danger')
    return redirect(url_for('main.change_password'))

# This function lets users send friend requests through an API call, ensures no duplicate requests are made, 
# and responds appropriately with a success or error message.
@bp.route('/api/friend_request', methods=['POST'])
@login_required
def send_friend_request():
    data = request.get_json()
    sender_username = data['sender_username']
    receiver_username = data['receiver_username']

    existing_request = FriendRequest.query.filter_by(sender_id=sender_username, receiver_id=receiver_username).first()
    if existing_request:
        return jsonify({'message': 'Request already sent'}), 400

    new_request = FriendRequest(sender_id=sender_username, receiver_id=receiver_username)
    db.session.add(new_request)
    db.session.commit()
    return jsonify({'message': 'Friend request sent'}), 200

# This function returns a list of all pending friend requests for a given user in JSON format, 
# including each request's ID and sender's username.
@bp.route('/api/friend_requests/<user_id>', methods=['GET'])
@login_required
def get_friend_requests(user_id):
    requests = FriendRequest.query.filter_by(receiver_id=user_id, status='pending').all()
    result = [
        {
            'request_id': fr.id,
            'sender_username': fr.sender.username,
        }
        for fr in requests
    ]
    return jsonify(result)

# This function accepts a valid, pending friend request and creates a two-way friendship, 
# while preventing duplicates and ensuring only the correct recipient can accept.
@bp.route('/api/friend_request/accept/<int:request_id>', methods=['POST'])
@login_required
def accept_friend_request(request_id):
    try:
        fr = FriendRequest.query.filter_by(id=request_id).first()
        if not fr:
            return jsonify({'message': 'Friend request not found'}), 404
        
        if fr.status != 'pending':
            return jsonify({'message': 'Friend request is no longer pending'}), 400
        
        # Verify that the current user is the receiver of the request
        if fr.receiver_id != current_user.username:
            return jsonify({'message': 'Unauthorized'}), 403

        # Check if friendship already exists
        existing_friendship = Friendship.query.filter_by(
            user_id=fr.sender_id,
            friend_id=fr.receiver_id
        ).first()
        
        if existing_friendship:
            fr.status = 'accepted'
            db.session.commit()
            return jsonify({'message': 'Already friends'}), 200

        # Update friend request status
        fr.status = 'accepted'

        # Create bidirectional friendship
        friendship1 = Friendship(user_id=fr.sender_id, friend_id=fr.receiver_id)
        friendship2 = Friendship(user_id=fr.receiver_id, friend_id=fr.sender_id)
        
        db.session.add_all([friendship1, friendship2])
        db.session.commit()
        
        return jsonify({'message': 'Friend request accepted'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error accepting friend request: {str(e)}")  # Add logging
        return jsonify({'message': 'Error accepting friend request'}), 500

# This function lets users decline a pending friend request by updating its status, 
# ensuring only valid pending requests are processed.
@bp.route('/api/friend_request/decline/<int:request_id>', methods=['POST'])
@login_required
def decline_friend_request(request_id):
    fr = FriendRequest.query.get(request_id)
    if not fr or fr.status != 'pending':
        return jsonify({'message': 'Invalid request'}), 404

    fr.status = 'declined'
    db.session.commit()
    return jsonify({'message': 'Friend request declined'})

# This function manually adds a two-way friendship between users, 
# with safeguards against self-addition and duplicate friendships.
@bp.route('/add_friend/<int:friend_id>', methods=['POST'])
@login_required
def add_friend(friend_id):
    if friend_id == current_user.id:
        flash("You can't add yourself as a friend!", "danger")
        return redirect(url_for('main.search_users'))
    
    existing = Friendship.query.filter_by(
        user_id=current_user.id,
        friend_id=friend_id
    ).first()
    
    if not existing:
        friendship1 = Friendship(user_id=current_user.id, friend_id=friend_id)
        friendship2 = Friendship(user_id=friend_id, friend_id=current_user.id)
        db.session.add_all([friendship1, friendship2])
        db.session.commit()
        flash("Friend added successfully!", "success")
    else:
        flash("You are already friends with this user!", "warning")
    
    return redirect(url_for('main.search_users'))

# This function cleanly removes the mutual friendship between two users and updates the database accordingly.
@bp.route('/remove_friend/<friend_id>', methods=['POST'])
@login_required
def remove_friend(friend_id):
    Friendship.query.filter_by(
        user_id=current_user.username,
        friend_id=friend_id
    ).delete()
    Friendship.query.filter_by(
        user_id=friend_id,
        friend_id=current_user.username
    ).delete()
    db.session.commit()
    flash("Friend removed successfully!", "success")
    return redirect(url_for('main.home'))

# It ensures users can only submit one mood per day, stores it with optional reasons, and confirms successful submission.
@bp.route('/submit_mood', methods=['POST'])
@login_required
def submit_mood():
    data = request.get_json()
    mood = data.get('mood')
    reasons = data.get('reasons', [])
    
    if not mood:
        return jsonify({'error': 'Missing mood'}), 400
    
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    existing_entry = Mood.query.filter(
        Mood.user_id == current_user.username,
        Mood.timestamp >= today_start,
        Mood.timestamp <= today_end
    ).first()
    
    if existing_entry:
        return jsonify({
            'error': "You've already tracked today's mood!"
        }), 409
    
    entry = Mood(
        mood=mood,
        timestamp=datetime.now(),
        user_id=current_user.username
    )
    entry.set_reasons(reasons)
    db.session.add(entry)
    db.session.commit()
    
    return jsonify({'message': 'Mood recorded successfully', 'entry': entry.to_dict()})

# It provides an API endpoint that retrieves and sends back all of the current user's mood history.
@bp.route('/get_moods')
@login_required
def get_moods():
    entries = Mood.query.filter_by(user_id=current_user.username).all()
    return jsonify([entry.to_dict() for entry in entries])

# It securely provides the mood history of a friend only if the current user has a friendship with that friend.
@bp.route('/get_friend_moods/<friend_id>')
@login_required
def get_friend_moods(friend_id):
    friendship = Friendship.query.filter_by(
        user_id=current_user.username,
        friend_id=friend_id
    ).first()
    
    if not friendship:
        return jsonify({'error': 'Not friends with this user'}), 403
    
    entries = Mood.query.filter_by(user_id=friend_id).all()
    return jsonify([entry.to_dict() for entry in entries])

# It controls access to a user’s calendar page based on privacy: only the user themselves or their friends 
# (if privacy allows) can view the calendar; otherwise, access is blocked with a flash message.
@bp.route('/calendar/<user_id>')
@login_required
def calendar_view(user_id):
    # Get the user
    user = User.query.get_or_404(user_id)
    
    # Check privacy settings
    if user_id != current_user.username:
        if user.privacy_setting == 'private':
            flash("This user's data is private", "warning")
            return redirect(url_for('main.home'))
        elif user.privacy_setting == 'friends':
            friendship = Friendship.query.filter_by(
                user_id=current_user.username,
                friend_id=user_id
            ).first()
            if not friendship:
                flash("You can only view calendars of your friends", "warning")
                return redirect(url_for('main.home'))
    
    # Get the date ranges
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
    month_start = today.replace(day=1)
    if today.month == 12:
        month_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        month_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    
    # Get week and month dates
    week_dates = [week_start + timedelta(days=i) for i in range(7)]
    month_dates = []
    current_date = month_start
    while current_date <= month_end:
        month_dates.append(current_date)
        current_date += timedelta(days=1)
    
    # Get moods for both views
    week_moods = Mood.get_moods_for_date_range(user_id, week_start, week_end)
    month_moods = Mood.get_moods_for_date_range(user_id, month_start, month_end)
    
    return render_template('calendar.html',
                         user=user,
                         week_dates=week_dates,
                         month_dates=month_dates,
                         week_moods=week_moods,
                         month_moods=month_moods)

# It ensures only authorized users (self or friends) can view a user’s mood analysis based on privacy settings, 
# otherwise it denies access and redirects home.
@bp.route('/analysis/<user_id>')
@login_required
def analysis(user_id):
    # Get the user
    user = User.query.get_or_404(user_id)
    
    # Check privacy settings
    if user_id != current_user.username:
        if user.privacy_setting == 'private':
            flash("This user's data is private", "warning")
            return redirect(url_for('main.home'))
        elif user.privacy_setting == 'friends':
            friendship = Friendship.query.filter_by(
                user_id=current_user.username,
                friend_id=user_id
            ).first()
            if not friendship:
                flash("You can only view analysis of your friends", "warning")
                return redirect(url_for('main.home'))
    
    # Get the date ranges
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
    month_start = today.replace(day=1)
    if today.month == 12:
        month_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        month_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    
    # Get moods for the week
    week_moods = Mood.query.filter(
        Mood.user_id == user_id,
        Mood.timestamp >= week_start,
        Mood.timestamp <= week_end
    ).all()
    
    # Get moods for the month
    month_moods = Mood.query.filter(
        Mood.user_id == user_id,
        Mood.timestamp >= month_start,
        Mood.timestamp <= month_end
    ).all()
    
    # Prepare data for weekly mood distribution chart
    weekly_mood_data = {}
    for mood in week_moods:
        if mood.mood in weekly_mood_data:
            weekly_mood_data[mood.mood] += 1
        else:
            weekly_mood_data[mood.mood] = 1
    
    # Prepare data for weekly activities chart
    weekly_activities = {}
    for mood in week_moods:
        for reason in mood.get_reasons():
            if reason in weekly_activities:
                weekly_activities[reason] += 1
            else:
                weekly_activities[reason] = 1
    
    # Prepare data for monthly mood distribution chart
    monthly_mood_data = {}
    for mood in month_moods:
        if mood.mood in monthly_mood_data:
            monthly_mood_data[mood.mood] += 1
        else:
            monthly_mood_data[mood.mood] = 1
    
    # Prepare data for monthly activities chart
    monthly_activities = {}
    for mood in month_moods:
        for reason in mood.get_reasons():
            if reason in monthly_activities:
                monthly_activities[reason] += 1
            else:
                monthly_activities[reason] = 1
    
    # Prepare data for mood distribution by day of week
    monthly_days_data = {
        'Monday': {'happy': 0, 'sad': 0, 'excited': 0, 'calm': 0, 'anxious': 0, 'angry': 0, 'tired': 0, 'scared': 0},
        'Tuesday': {'happy': 0, 'sad': 0, 'excited': 0, 'calm': 0, 'anxious': 0, 'angry': 0, 'tired': 0, 'scared': 0},
        'Wednesday': {'happy': 0, 'sad': 0, 'excited': 0, 'calm': 0, 'anxious': 0, 'angry': 0, 'tired': 0, 'scared': 0},
        'Thursday': {'happy': 0, 'sad': 0, 'excited': 0, 'calm': 0, 'anxious': 0, 'angry': 0, 'tired': 0, 'scared': 0},
        'Friday': {'happy': 0, 'sad': 0, 'excited': 0, 'calm': 0, 'anxious': 0, 'angry': 0, 'tired': 0, 'scared': 0},
        'Saturday': {'happy': 0, 'sad': 0, 'excited': 0, 'calm': 0, 'anxious': 0, 'angry': 0, 'tired': 0, 'scared': 0},
        'Sunday': {'happy': 0, 'sad': 0, 'excited': 0, 'calm': 0, 'anxious': 0, 'angry': 0, 'tired': 0, 'scared': 0}
    }
    
    # Count mood frequencies by day of week
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for mood in month_moods:
        day_of_week = days_of_week[mood.timestamp.weekday()]
        monthly_days_data[day_of_week][mood.mood] += 1
    
    return render_template('analysis.html',
                         user=user,
                         weekly_mood_data=weekly_mood_data,
                         weekly_activities=weekly_activities,
                         monthly_mood_data=monthly_mood_data,
                         monthly_activities=monthly_activities,
                         monthly_days_data=monthly_days_data)

# Analyze weekly mood data to find most frequent mood and activities occurring more than 3 times
def analyze_weekly_moods(moods):
    if not moods:
        return {
            'most_frequent_mood': None,
            'frequent_activities': []
        }
    
    # Count mood frequencies
    mood_counts = {}
    for mood in moods:
        if mood.mood in mood_counts:
            mood_counts[mood.mood] += 1
        else:
            mood_counts[mood.mood] = 1
    
    # Find most frequent mood
    most_frequent_mood = max(mood_counts.items(), key=lambda x: x[1])[0] if mood_counts else None
    
    # Count activity frequencies
    activity_counts = {}
    for mood in moods:
        for reason in mood.get_reasons():
            if reason in activity_counts:
                activity_counts[reason] += 1
            else:
                activity_counts[reason] = 1
    
    # Find activities occurring more than 3 times
    frequent_activities = [activity for activity, count in activity_counts.items() if count > 3]
    
    return {
        'most_frequent_mood': most_frequent_mood,
        'frequent_activities': frequent_activities if frequent_activities else ['none']
    }

# Analyze monthly mood data to find days for each mood and frequent activities.
def analyze_monthly_moods(moods):
    if not moods:
        return {
            'mood_days': {},
            'frequent_activities': []
        }
    
    # Group moods by type and day of week
    mood_days = {}
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    for mood in moods:
        mood_type = mood.mood
        day_of_week = days_of_week[mood.timestamp.weekday()]
        
        if mood_type not in mood_days:
            mood_days[mood_type] = {}
        
        if day_of_week not in mood_days[mood_type]:
            mood_days[mood_type][day_of_week] = 0
        
        mood_days[mood_type][day_of_week] += 1
    
    # Filter to only include days with more than 3 occurrences
    filtered_mood_days = {}
    for mood_type, days in mood_days.items():
        filtered_days = {day: count for day, count in days.items() if count > 3}
        if filtered_days:
            filtered_mood_days[mood_type] = filtered_days
    
    # Count activity frequencies
    activity_counts = {}
    for mood in moods:
        for reason in mood.get_reasons():
            if reason in activity_counts:
                activity_counts[reason] += 1
            else:
                activity_counts[reason] = 1
    
    # Find activities occurring more than 3 times
    frequent_activities = [activity for activity, count in activity_counts.items() if count > 3]
    
    return {
        'mood_days': filtered_mood_days,
        'frequent_activities': frequent_activities if frequent_activities else ['none']
    }

# Handle POST request to update the current user's privacy setting; 
# validates input, updates the setting if valid, commits to database, 
# flashes success or error messages, then redirects to the change password page.
@bp.route('/update_privacy', methods=['POST'])
@login_required
def update_privacy():
    form = PrivacyForm()
    if form.validate_on_submit():
        setting = form.privacy_setting.data
        if setting in ['public', 'friends', 'private']:
            current_user.privacy_setting = setting
            db.session.commit()
            flash('Privacy settings updated successfully', 'success')
        else:
            flash('Invalid privacy setting', 'danger')
    db.session.refresh(current_user)
    return redirect(url_for('main.change_password'))

# API endpoint to search users by username query (case-insensitive); 
# excludes current user, returns list with each user's username, 
# friendship status with current user, pending friend request status, 
# and their mood entry for today if available.
@bp.route('/api/search_users', methods=['GET'])
@login_required
def search_users():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    
    # Get today's date range
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    # Search for users by username
    users = User.query.filter(User.username.ilike(f'%{query}%')).all()
    
    # Get current user's friends and pending requests
    current_friends = {f.username for f in current_user.friends}
    pending_requests = {
        fr.receiver_id for fr in FriendRequest.query.filter_by(sender_id=current_user.username, status='pending').all()
    }
    
    results = []
    for user in users:
        if user.username != current_user.username:  # Don't show current user
            # Get today's mood for the user
            today_mood = Mood.query.filter(
                Mood.user_id == user.username,
                Mood.timestamp >= today_start,
                Mood.timestamp <= today_end
            ).first()
            
            user_data = {
                'username': user.username,
                'is_friend': user.username in current_friends,
                'request_pending': user.username in pending_requests,
                'today_mood': today_mood.to_dict() if today_mood else None
            }
            results.append(user_data)
    
    return jsonify(results) 
