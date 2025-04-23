from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from collections import Counter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mood_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class MoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    mood = db.Column(db.String(20), nullable=False)
    reasons = db.Column(db.String(500), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'mood': self.mood,
            'reasons': self.reasons,
            'timestamp': self.timestamp.isoformat()
        }

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recap')
@app.route('/recap/<user_id>')
def recap(user_id=None):
    return render_template('recap.html', user_id=user_id)

@app.route('/check_today_entry/<user_id>')
def check_today_entry(user_id):
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    existing_entry = MoodEntry.query.filter(
        MoodEntry.user_id == user_id,
        MoodEntry.timestamp >= today_start,
        MoodEntry.timestamp <= today_end
    ).first()
    
    if existing_entry:
        return jsonify({
            'has_entry': True,
            'entry': existing_entry.to_dict()
        })
    else:
        return jsonify({
            'has_entry': False
        })

@app.route('/submit_mood', methods=['POST'])
def submit_mood():
    data = request.get_json()
    user_id = data.get('user_id')
    mood = data.get('mood')
    reasons = data.get('reasons', '')  # Get reasons, default to empty string if not provided
    
    if not user_id or not mood:
        return jsonify({'error': 'Missing user_id or mood'}), 400
    
    # Check if user has already submitted a mood entry today
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    existing_entry = MoodEntry.query.filter(
        MoodEntry.user_id == user_id,
        MoodEntry.timestamp >= today_start,
        MoodEntry.timestamp <= today_end
    ).first()
    
    if existing_entry:
        return jsonify({
            'error': "You've already tracked today's mood!"
        }), 409
    
    # If no entry exists for today, create a new one
    entry = MoodEntry(user_id=user_id, mood=mood, reasons=reasons)
    db.session.add(entry)
    db.session.commit()
    
    return jsonify({'message': 'Mood recorded successfully', 'entry': entry.to_dict()})

@app.route('/get_moods/<user_id>')
def get_moods(user_id):
    entries = MoodEntry.query.filter_by(user_id=user_id).all()
    return jsonify([entry.to_dict() for entry in entries])

@app.route('/get_weekly_analysis/<user_id>')
def get_weekly_analysis(user_id):
    # Get the date range for the current week
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # Convert to datetime for database query
    start_datetime = datetime.combine(start_of_week, datetime.min.time())
    end_datetime = datetime.combine(end_of_week, datetime.max.time())
    
    # Get all mood entries for the user in the current week
    entries = MoodEntry.query.filter(
        MoodEntry.user_id == user_id,
        MoodEntry.timestamp >= start_datetime,
        MoodEntry.timestamp <= end_datetime
    ).all()
    
    if not entries:
        return jsonify({
            'error': 'No mood entries found for this week',
            'has_data': False
        })
    
    # Convert entries to dictionaries
    entries_dict = [entry.to_dict() for entry in entries]
    
    # Analyze the data
    analysis = analyze_weekly_mood(entries_dict)
    
    return jsonify({
        'has_data': True,
        'entries': entries_dict,
        'analysis': analysis
    })

def analyze_weekly_mood(entries):
    # Group entries by day of week
    entries_by_day = {}
    for entry in entries:
        entry_date = datetime.fromisoformat(entry['timestamp']).date()
        day_name = entry_date.strftime('%A')
        
        if day_name not in entries_by_day:
            entries_by_day[day_name] = []
        
        entries_by_day[day_name].append(entry)
    
    # Find most common mood
    mood_counts = Counter(entry['mood'] for entry in entries)
    most_common_mood = mood_counts.most_common(1)[0][0] if mood_counts else None
    
    # Find reasons for the most common mood
    most_common_reasons = []
    if most_common_mood:
        # Get all entries with the most common mood
        common_mood_entries = [entry for entry in entries if entry['mood'] == most_common_mood]
        
        # Extract all reasons from these entries
        all_reasons = []
        for entry in common_mood_entries:
            if entry['reasons']:
                reasons = [reason.strip() for reason in entry['reasons'].split(',')]
                all_reasons.extend(reasons)
        
        # Count reason frequencies
        reason_counts = Counter(all_reasons)
        most_common_reasons = [reason for reason, _ in reason_counts.most_common(3)]
    
    # Find mood patterns by day
    mood_patterns = {}
    day_reasons = {}
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        if day in entries_by_day:
            day_entries = entries_by_day[day]
            mood_patterns[day] = [entry['mood'] for entry in day_entries]
            
            # Get reasons for this day
            day_all_reasons = []
            for entry in day_entries:
                if entry['reasons']:
                    reasons = [reason.strip() for reason in entry['reasons'].split(',')]
                    day_all_reasons.extend(reasons)
            
            # Count reason frequencies for this day
            day_reason_counts = Counter(day_all_reasons)
            day_reasons[day] = [reason for reason, _ in day_reason_counts.most_common(3)]
    
    return {
        'most_common_mood': most_common_mood,
        'most_common_reasons': most_common_reasons,
        'mood_patterns': mood_patterns,
        'day_reasons': day_reasons,
        'mood_counts': dict(mood_counts)
    }

@app.route('/get_monthly_analysis/<user_id>')
def get_monthly_analysis(user_id):
    # Get the date range for the current month
    today = date.today()
    start_of_month = today.replace(day=1)
    end_of_month = (start_of_month + relativedelta(months=1)) - timedelta(days=1)
    
    # Convert to datetime for database query
    start_datetime = datetime.combine(start_of_month, datetime.min.time())
    end_datetime = datetime.combine(end_of_month, datetime.max.time())
    
    # Get all mood entries for the user in the current month
    entries = MoodEntry.query.filter(
        MoodEntry.user_id == user_id,
        MoodEntry.timestamp >= start_datetime,
        MoodEntry.timestamp <= end_datetime
    ).all()
    
    if not entries:
        return jsonify({
            'error': 'No mood entries found for this month',
            'has_data': False
        })
    
    # Convert entries to dictionaries
    entries_dict = [entry.to_dict() for entry in entries]
    
    # Analyze the data
    analysis = analyze_monthly_mood(entries_dict)
    
    return jsonify({
        'has_data': True,
        'entries': entries_dict,
        'analysis': analysis
    })

def analyze_monthly_mood(entries):
    # Group entries by day of week
    entries_by_day = {}
    for entry in entries:
        entry_date = datetime.fromisoformat(entry['timestamp']).date()
        day_name = entry_date.strftime('%A')
        
        if day_name not in entries_by_day:
            entries_by_day[day_name] = []
        
        entries_by_day[day_name].append(entry)
    
    # Find most common mood
    mood_counts = Counter(entry['mood'] for entry in entries)
    most_common_mood = mood_counts.most_common(1)[0][0] if mood_counts else None
    
    # Find reasons for the most common mood
    most_common_reasons = []
    if most_common_mood:
        # Get all entries with the most common mood
        common_mood_entries = [entry for entry in entries if entry['mood'] == most_common_mood]
        
        # Extract all reasons from these entries
        all_reasons = []
        for entry in common_mood_entries:
            if entry['reasons']:
                reasons = [reason.strip() for reason in entry['reasons'].split(',')]
                all_reasons.extend(reasons)
        
        # Count reason frequencies
        reason_counts = Counter(all_reasons)
        most_common_reasons = [reason for reason, _ in reason_counts.most_common(3)]
    
    # Find mood patterns by day
    mood_patterns = {}
    day_reasons = {}
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        if day in entries_by_day:
            day_entries = entries_by_day[day]
            mood_patterns[day] = [entry['mood'] for entry in day_entries]
            
            # Get reasons for this day
            day_all_reasons = []
            for entry in day_entries:
                if entry['reasons']:
                    reasons = [reason.strip() for reason in entry['reasons'].split(',')]
                    day_all_reasons.extend(reasons)
            
            # Count reason frequencies for this day
            day_reason_counts = Counter(day_all_reasons)
            day_reasons[day] = [reason for reason, _ in day_reason_counts.most_common(3)]
    
    return {
        'most_common_mood': most_common_mood,
        'most_common_reasons': most_common_reasons,
        'mood_patterns': mood_patterns,
        'day_reasons': day_reasons,
        'mood_counts': dict(mood_counts)
    }

@app.route('/monthly_recap')
@app.route('/monthly_recap/<user_id>')
def monthly_recap(user_id=None):
    return render_template('monthly_recap.html', user_id=user_id)

if __name__ == '__main__':
    app.run(debug=True) 
