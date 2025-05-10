from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, Mood, Friendship, FriendRequest, db
from datetime import datetime, timedelta

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    return redirect(url_for('main.home'))

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

# @bp.route('/search_users')
# @login_required
# def search_users():
#     query = request.args.get('q', '')
#     if query:
#         users = User.query.filter(
#             (User.username.ilike(f'%{query}%')) |
#             (User.full_name.ilike(f'%{query}%'))
#         ).filter(User.id != current_user.id).all()
#     else:
# <<<<<<< settings-page-privacy-settings-and-change-password
#         data = request.get_json()
#         setting = data.get('privacy_setting')
#         if setting not in ['friends', 'nobody']:
#             return jsonify({'error': 'Invalid setting'}), 400

#         current_user.privacy_setting = setting
#         db.session.commit()
#         return jsonify({'message': 'Settings updated successfully'})
    
@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current = request.form.get('current_password')
        new = request.form.get('new_password')
        confirm = request.form.get('confirm_new_password')

        if not check_password_hash(current_user.password, current):
            flash('Current password is incorrect.', 'danger')
        elif new != confirm:
            flash('New passwords do not match.', 'warning')
        else:
            current_user.password = generate_password_hash(new)
            db.session.commit()
            flash('Your password has been updated.', 'success')
            return redirect(url_for('main.home'))

    return render_template('changepassword.html')

@bp.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
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

# @bp.route('/search_users')
# @login_required
# def search_users():
#     query = request.args.get('q', '')
#     if query:
#         users = User.query.filter(
#             (User.username.ilike(f'%{query}%')) |
#             (User.full_name.ilike(f'%{query}%'))
#         ).filter(User.id != current_user.id).all()
#     else:
#         users = []
    
#     friend_ids = {f.friend_id for f in Friendship.query.filter_by(user_id=current_user.id).all()}
    
#     return render_template('main/search_users.html', users=users, friend_ids=friend_ids)
# =======
#         users = []
    
#     friend_ids = {f.friend_id for f in Friendship.query.filter_by(user_id=current_user.id).all()}
    
#     return render_template('main/search_users.html', users=users, friend_ids=friend_ids)
# >>>>>>> main

# send friend request
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

# get friend requests for logged-in user
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

# accept friend request
@bp.route('/api/friend_request/accept/<int:request_id>', methods=['POST'])
@login_required
def accept_friend_request(request_id):
    fr = FriendRequest.query.get(request_id)
    if not fr or fr.status != 'pending':
        return jsonify({'message': 'Invalid request'}), 404

    fr.status = 'accepted'

    # Create friendship using usernames
    friendship1 = Friendship(user_id=fr.sender_id, friend_id=fr.receiver_id)
    friendship2 = Friendship(user_id=fr.receiver_id, friend_id=fr.sender_id)
    db.session.add_all([friendship1, friendship2])
    db.session.commit()
    
    return jsonify({'message': 'Friend request accepted'})

# decline friend request
@bp.route('/api/friend_request/decline/<int:request_id>', methods=['POST'])
@login_required
def decline_friend_request(request_id):
    fr = FriendRequest.query.get(request_id)
    if not fr or fr.status != 'pending':
        return jsonify({'message': 'Invalid request'}), 404

    fr.status = 'declined'
    db.session.commit()
    return jsonify({'message': 'Friend request declined'})

@bp.route('/add_friend/<int:friend_id>', methods=['POST'])
@login_required
def add_friend(friend_id):
    if friend_id == current_user.id:
        flash("You can't add yourself as a friend!")
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
        flash("Friend added successfully!")
    else:
        flash("You are already friends with this user!")
    
    return redirect(url_for('main.search_users'))

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
    flash("Friend removed successfully!")
    return redirect(url_for('main.home'))

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

@bp.route('/get_moods')
@login_required
def get_moods():
    entries = Mood.query.filter_by(user_id=current_user.username).all()
    return jsonify([entry.to_dict() for entry in entries])

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

@bp.route('/calendar/<user_id>')
@login_required
def calendar_view(user_id):
    # Get the user
    user = User.query.get_or_404(user_id)
    
    # Check privacy settings
    if user_id != current_user.username:
        if user.privacy_setting == 'private':
            flash("This user's data is private")
            return redirect(url_for('main.home'))
        elif user.privacy_setting == 'friends':
            friendship = Friendship.query.filter_by(
                user_id=current_user.username,
                friend_id=user_id
            ).first()
            if not friendship:
                flash("You can only view calendars of your friends")
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

@bp.route('/analysis/<user_id>')
@login_required
def analysis(user_id):
    # Get the user
    user = User.query.get_or_404(user_id)
    
    # Check privacy settings
    if user_id != current_user.username:
        if user.privacy_setting == 'private':
            flash("This user's data is private")
            return redirect(url_for('main.home'))
        elif user.privacy_setting == 'friends':
            friendship = Friendship.query.filter_by(
                user_id=current_user.username,
                friend_id=user_id
            ).first()
            if not friendship:
                flash("You can only view analysis of your friends")
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
        'Monday': {'happy': 0, 'sad': 0, 'excited': 0, 'calm': 0, 'anxious': 0},
        'Tuesday': {'happy': 0, 'sad': 0, 'excited': 0, 'calm': 0, 'anxious': 0},
        'Wednesday': {'happy': 0, 'sad': 0, 'excited': 0, 'calm': 0, 'anxious': 0},
        'Thursday': {'happy': 0, 'sad': 0, 'excited': 0, 'calm': 0, 'anxious': 0},
        'Friday': {'happy': 0, 'sad': 0, 'excited': 0, 'calm': 0, 'anxious': 0},
        'Saturday': {'happy': 0, 'sad': 0, 'excited': 0, 'calm': 0, 'anxious': 0},
        'Sunday': {'happy': 0, 'sad': 0, 'excited': 0, 'calm': 0, 'anxious': 0}
    }
    
    # Calculate average moods per day
    moods_per_day = {}
    for mood in month_moods:
        day = mood.timestamp.strftime('%Y-%m-%d')
        if day not in moods_per_day:
            moods_per_day[day] = []
        moods_per_day[day].append(mood.mood)
    
    return render_template('analysis.html',
                         user=user,
                         weekly_mood_data=weekly_mood_data,
                         weekly_activities=weekly_activities,
                         monthly_mood_data=monthly_mood_data,
                         monthly_activities=monthly_activities,
                         monthly_days_data=monthly_days_data,
                         moods_per_day=moods_per_day)

def analyze_weekly_moods(moods):
    """Analyze weekly mood data to find most frequent mood and activities occurring more than 3 times."""
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

def analyze_monthly_moods(moods):
    """Analyze monthly mood data to find days for each mood and frequent activities."""
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

@bp.route('/update_privacy', methods=['POST'])
@login_required
def update_privacy():
    privacy_setting = request.form.get('privacy_setting')
    if privacy_setting not in ['public', 'friends', 'private']:
        flash('Invalid privacy setting')
        return redirect(url_for('main.change_password'))
    
    current_user.privacy_setting = privacy_setting
    db.session.commit()
    flash('Privacy settings updated successfully')
    return redirect(url_for('main.change_password')) 
