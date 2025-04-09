from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mood_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class MoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    mood = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'mood': self.mood,
            'timestamp': self.timestamp.isoformat()
        }

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_mood', methods=['POST'])
def submit_mood():
    data = request.get_json()
    user_id = data.get('user_id')
    mood = data.get('mood')
    
    if not user_id or not mood:
        return jsonify({'error': 'Missing user_id or mood'}), 400
    
    entry = MoodEntry(user_id=user_id, mood=mood)
    db.session.add(entry)
    db.session.commit()
    
    return jsonify({'message': 'Mood recorded successfully', 'entry': entry.to_dict()})

@app.route('/get_moods/<user_id>')
def get_moods(user_id):
    entries = MoodEntry.query.filter_by(user_id=user_id).all()
    return jsonify([entry.to_dict() for entry in entries])

if __name__ == '__main__':
    app.run(debug=True) 
