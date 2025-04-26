from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import User, Mood, Friendship, db
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
        Mood.user_id == current_user.id,
        Mood.timestamp >= today_start,
        Mood.timestamp <= today_end
    ).first()
    
    # Get friends with their today's mood
    friends = []
    for friend in current_user.friends:
        friend_mood = Mood.query.filter(
            Mood.user_id == friend.id,
            Mood.timestamp >= today_start,
            Mood.timestamp <= today_end
        ).first()
        friends.append({
            'id': friend.id,
            'name': friend.name,
            'today_mood': friend_mood
        })
    
    return render_template('home.html',
                         today_mood=today_mood,
                         friends=friends,
                         reasons=Mood.get_all_reasons())

@bp.route('/search_users')
@login_required
def search_users():
    query = request.args.get('q', '')
    if query:
        users = User.query.filter(
            (User.username.ilike(f'%{query}%')) |
            (User.full_name.ilike(f'%{query}%'))
        ).filter(User.id != current_user.id).all()
    else:
        users = []
    
    friend_ids = {f.friend_id for f in Friendship.query.filter_by(user_id=current_user.id).all()}
    
    return render_template('main/search_users.html', users=users, friend_ids=friend_ids)

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

@bp.route('/remove_friend/<int:friend_id>', methods=['POST'])
@login_required
def remove_friend(friend_id):
    Friendship.query.filter_by(
        user_id=current_user.id,
        friend_id=friend_id
    ).delete()
    Friendship.query.filter_by(
        user_id=friend_id,
        friend_id=current_user.id
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
        Mood.user_id == current_user.id,
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
        user_id=current_user.id
    )
    entry.set_reasons(reasons)
    db.session.add(entry)
    db.session.commit()
    
    return jsonify({'message': 'Mood recorded successfully', 'entry': entry.to_dict()})

@bp.route('/get_moods')
@login_required
def get_moods():
    entries = Mood.query.filter_by(user_id=current_user.id).all()
    return jsonify([entry.to_dict() for entry in entries])

@bp.route('/get_friend_moods/<int:friend_id>')
@login_required
def get_friend_moods(friend_id):
    friendship = Friendship.query.filter_by(
        user_id=current_user.id,
        friend_id=friend_id
    ).first()
    
    if not friendship:
        return jsonify({'error': 'Not friends with this user'}), 403
    
    entries = Mood.query.filter_by(user_id=friend_id).all()
    return jsonify([entry.to_dict() for entry in entries])

@bp.route('/calendar/<int:user_id>')
@login_required
def calendar_view(user_id):
    # Get the user
    user = User.query.get_or_404(user_id)
    
    # Check if the user is a friend
    if user_id != current_user.id:
        friendship = Friendship.query.filter_by(
            user_id=current_user.id,
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

@bp.route('/analysis/<int:user_id>')
@login_required
def analysis(user_id):
    # Get the user
    user = User.query.get_or_404(user_id)
    
    # Check if the user is a friend or the current user
    if user_id != current_user.id:
        friendship = Friendship.query.filter_by(
            user_id=current_user.id,
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
    
    # Analyze weekly data
    weekly_analysis = analyze_weekly_moods(week_moods)
    
    # Analyze monthly data
    monthly_analysis = analyze_monthly_moods(month_moods)
    
    return render_template('analysis.html',
                         user=user,
                         weekly_analysis=weekly_analysis,
                         monthly_analysis=monthly_analysis)

def analyze_weekly_moods(moods):
    """Analyze weekly mood data to find most frequent mood and reasons."""
    if not moods:
        return {
            'most_frequent_mood': None,
            'most_frequent_reasons': []
        }
    
    # Count mood frequencies
    mood_counts = {}
    for mood in moods:
        if mood.mood in mood_counts:
            mood_counts[mood.mood] += 1
        else:
            mood_counts[mood.mood] = 1
    
    # Find most frequent mood
    most_frequent_mood = max(mood_counts.items(), key=lambda x: x[1])[0]
    
    # Count reason frequencies
    reason_counts = {}
    for mood in moods:
        for reason in mood.get_reasons():
            if reason in reason_counts:
                reason_counts[reason] += 1
            else:
                reason_counts[reason] = 1
    
    # Find top 3 most frequent reasons
    most_frequent_reasons = sorted(reason_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    most_frequent_reasons = [reason for reason, count in most_frequent_reasons]
    
    return {
        'most_frequent_mood': most_frequent_mood,
        'most_frequent_reasons': most_frequent_reasons
    }

def analyze_monthly_moods(moods):
    """Analyze monthly mood data to find days for each mood and most frequent reasons."""
    if not moods:
        return {
            'mood_days': {},
            'most_frequent_reasons': []
        }
    
    # Group moods by type
    mood_days = {}
    for mood in moods:
        mood_type = mood.mood
        day = mood.timestamp.strftime('%Y-%m-%d')
        
        if mood_type not in mood_days:
            mood_days[mood_type] = []
        
        if day not in mood_days[mood_type]:
            mood_days[mood_type].append(day)
    
    # Count reason frequencies
    reason_counts = {}
    for mood in moods:
        for reason in mood.get_reasons():
            if reason in reason_counts:
                reason_counts[reason] += 1
            else:
                reason_counts[reason] = 1
    
    # Find top 3 most frequent reasons
    most_frequent_reasons = sorted(reason_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    most_frequent_reasons = [reason for reason, count in most_frequent_reasons]
    
    return {
        'mood_days': mood_days,
        'most_frequent_reasons': most_frequent_reasons
    } 
