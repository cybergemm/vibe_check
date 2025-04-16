from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

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

if __name__ == '__main__':
    app.run(debug=True) 
