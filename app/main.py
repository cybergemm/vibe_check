from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
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
        Mood.username == current_user.username,
        Mood.timestamp >= today_start,
        Mood.timestamp <= today_end
    ).first()
    
    # Get friends with their today's mood
    friends = []
    for friend in current_user.friends:
        friend_mood = Mood.query.filter(
            Mood.username == friend.username,
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
                         reasons=Mood.get_all_reasons())

@bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@bp.route('/api/user_settings', methods=['GET', 'POST'])
@login_required
def user_settings():
    if request.method == 'GET':
        return jsonify({'privacy_setting': current_user.privacy_setting})
    else:
        data = request.get_json()
        setting = data.get('privacy_setting')
        if setting not in ['friends', 'nobody']:
            return jsonify({'error': 'Invalid setting'}), 400

        current_user.privacy_setting = setting
        db.session.commit()
        return jsonify({'message': 'Settings updated successfully'})

@bp.route('/api/friend_requests/<username>', methods=['GET'])
@login_required
def get_friend_requests(username):
    requests = FriendRequest.query.filter_by(receiver_username=username, status='pending').all()
    result = [
        {
            'request_id': fr.id,
            'sender_username': fr.sender_username,
        }
        for fr in requests
    ]
    return jsonify(result)

@bp.route('/api/friend_request/accept/<int:request_id>', methods=['POST'])
@login_required
def accept_friend_request(request_id):
    fr = FriendRequest.query.get(request_id)
    if not fr or fr.status != 'pending':
        return jsonify({'message': 'Invalid request'}), 404

    fr.status = 'accepted'

    db.session.execute("""
        INSERT INTO friendships (username, friend_username) VALUES (:u1, :u2), (:u2, :u1)
    """, {'u1': fr.sender_username, 'u2': fr.receiver_username})

    db.session.commit()
    return jsonify({'message': 'Friend request accepted'})

@bp.route('/api/friend_request/decline/<int:request_id>', methods=['POST'])
@login_required
def decline_friend_request(request_id):
    fr = FriendRequest.query.get(request_id)
    if not fr or fr.status != 'pending':
        return jsonify({'message': 'Invalid request'}), 404

    fr.status = 'declined'
    db.session.commit()
    return jsonify({'message': 'Friend request declined'})

@bp.route('/api/search_users')
@login_required
def search_users():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])

    # Get current user's existing friends and pending requests
    friend_usernames = db.session.query(Friendship.friend_username).filter_by(username=current_user.username)
    sent_requests = db.session.query(FriendRequest.receiver_username).filter_by(sender_username=current_user.username, status='pending')
    excluded_usernames = friend_usernames.union(sent_requests)

    users = User.query.filter(
        User.username.ilike(f"%{query}%"),
        User.username != current_user.username,
        ~User.username.in_(excluded_usernames)
    ).all()

    return jsonify([{'username': user.username} for user in users])

@bp.route('/api/send_friend_request/<receiver_username>', methods=['POST'])
@login_required
def send_friend_request(receiver_username):
    if receiver_username == current_user.username:
        return jsonify({'error': 'You cannot send a request to yourself'}), 400

    existing = FriendRequest.query.filter_by(sender_username=current_user.username, receiver_username=receiver_username, status='pending').first()
    if existing:
        return jsonify({'error': 'Request already sent'}), 400

    # Optional: Check if already friends
    already_friends = Friendship.query.filter_by(username=current_user.username, friend_username=receiver_username).first()
    if already_friends:
        return jsonify({'error': 'Already friends'}), 400

    new_request = FriendRequest(sender_username=current_user.username, receiver_username=receiver_username, status='pending')
    db.session.add(new_request)
    db.session.commit()
    return jsonify({'message': 'Friend request sent'})

@bp.route('/remove_friend/<friend_username>', methods=['POST'])
@login_required
def remove_friend(friend_username):
    Friendship.query.filter_by(
        username=current_user.username,
        friend_username=friend_username
    ).delete()
    Friendship.query.filter_by(
        username=friend_username,
        friend_username=current_user.username
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
        Mood.username == current_user.username,
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
        username=current_user.username
    )
    entry.set_reasons(reasons)
    db.session.add(entry)
    db.session.commit()
    
    return jsonify({'message': 'Mood recorded successfully', 'entry': entry.to_dict()})

@bp.route('/get_moods')
@login_required
def get_moods():
    entries = Mood.query.filter_by(username=current_user.username).all()
    return jsonify([entry.to_dict() for entry in entries])

@bp.route('/get_friend_moods/<friend_username>')
@login_required
def get_friend_moods(friend_username):
    friendship = Friendship.query.filter_by(
        username=current_user.username,
        friend_username=friend_username
    ).first()
    
    if not friendship:
        return jsonify({'error': 'Not friends with this user'}), 403
    
    entries = Mood.query.filter_by(username=friend_username).all()
    return jsonify([entry.to_dict() for entry in entries])

@bp.route('/calendar/<username>')
@login_required
def calendar_view(username):
    # Get the user
    user = User.query.get_or_404(username)

    if user.privacy_setting == 'nobody' and user != current_user:
        flash("This user's mood analysis is private.")
        return redirect(url_for('main.home'))
    
    # Check if the user is a friend
    if username != current_user.username:
        friendship = Friendship.query.filter_by(
            username=current_user.username,
            friend_username=username
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
    week_moods = Mood.get_moods_for_date_range(username, week_start, week_end)
    month_moods = Mood.get_moods_for_date_range(username, month_start, month_end)
    
    return render_template('calendar.html',
                         user=user,
                         week_dates=week_dates,
                         month_dates=month_dates,
                         week_moods=week_moods,
                         month_moods=month_moods)

@bp.route('/analysis/<username>')
@login_required
def analysis(username):
    # Get the user
    user = User.query.get_or_404(username)
    
    # Check if the user is a friend or the current user
    if username != current_user.username:
        friendship = Friendship.query.filter_by(
            username=current_user.username,
            friend_username=username
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
        Mood.username == username,
        Mood.timestamp >= week_start,
        Mood.timestamp <= week_end
    ).all()
    
    # Get moods for the month
    month_moods = Mood.query.filter(
        Mood.username == username,
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
    
    # Prepare data for monthly days chart (total moods per day)
    monthly_days_data = {
        'Monday': 0,
        'Tuesday': 0,
        'Wednesday': 0,
        'Thursday': 0,
        'Friday': 0,
        'Saturday': 0,
        'Sunday': 0
    }
    for mood in month_moods:
        day_name = mood.timestamp.strftime('%A')
        monthly_days_data[day_name] += 1

    # Prepare data for grouped bar chart: moods per day of week
    all_moods = set([m.mood for m in month_moods])
    moods_per_day = {mood: {day: 0 for day in monthly_days_data.keys()} for mood in all_moods}
    for mood in month_moods:
        day_name = mood.timestamp.strftime('%A')
        moods_per_day[mood.mood][day_name] += 1
    
    # Ensure all dictionaries have at least one entry to prevent chart errors
    if not weekly_mood_data:
        weekly_mood_data = {'No Data': 1}
    if not weekly_activities:
        weekly_activities = {'No Activities': 1}
    if not monthly_mood_data:
        monthly_mood_data = {'No Data': 1}
    if not monthly_activities:
        monthly_activities = {'No Activities': 1}
    
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
