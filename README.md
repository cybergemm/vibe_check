## VibeCheck; a Flask-based, web application for tracking users' moods, as well as possibly sharing them with other users.
## By:
- Gemma Lock (23362049).
- Nandana Mathiparambil Vinod (24103138).
- Kamlesh Senthilkumar (24245674) 

## Features:
- User authentication (through its login functionality, as well as its signup functionality).
- Tracking of users' moods (as well as the reasons for those moods).
- Analysis and then visualisation of users' moods (as well as the reasons for those moods).
- Friend system (with friend requests).
- Privacy settings for the sharing of users' moods (as well as the reasons for those moods).
- Responsive design (through Bootstrap).

## Prerequisites:
- Python 3.10, or higher.
- pip (Python package manager).
- Chrome browser (for its Selenium tests).
- Flask-Migrate (for database setup; installed automatically with requirements.txt)

## Installation:
1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database (no migrations needed):
```bash
python3 create_db.py
```

5. Add test data (optional):
```bash
PYTHONPATH=. python3 app/add_testuser.py # On Windows, set PYTHONPATH=. && python app/add_testuser.py
```

## Running:
1. Start the Flask development server:
```bash
export FLASK_APP=app.py  # On Windows: set FLASK_APP=app.py
flask run
```

2. Open your browser and navigate to:
```
http://127.0.0.1:5000
```

### Troubleshooting:
- If you get an error like `OSError: [Errno 48] Address already in use`:
  1. Find the process using port 5000:
     ```bash
     lsof -i :5000  # On macOS/Linux
     netstat -ano | findstr :5000  # On Windows
     ```
  2. Kill the process:
     ```bash
     kill <PID>  # On macOS/Linux
     taskkill /PID <PID> /F  # On Windows
     ```
  3. Try running `flask run` again
- If you see `ModuleNotFoundError: No module named 'app'`, make sure to set `PYTHONPATH=.` when running scripts or tests.
- For Selenium tests, ensure you have ChromeDriver installed and it matches your Chrome version. See: https://sites.google.com/chromium.org/driver/

## API endpoints:
### Authentication:
- `POST /login` (for the user login functionality).
- `POST /signup` (for the user registration functionality).
- `GET /logout` (for the user logout functionality).

### Friend system:
- `GET /api/friend_requests/<username>` (for retrieving users' friend requests).
- `POST /api/friend_requests/<username>` (for sending users' friend requests).
- `PUT /api/friend_requests/<request_id>` (for accepting or rejecting users' friend requests).
- `GET /api/friends/<username>` (for retrieving users' friends lists).

### Mood tracking:
- `GET /api/moods/<username>` (for retrieving users' moods).
- `POST /api/moods` (for adding users' new mood entries).
- `GET /api/moods/stats/<username>` (for geting users' mood statistics).

## Running tests:
1. Install ChromeDriver (required for Selenium tests):
   - On macOS with Homebrew:
     ```bash
     brew install chromedriver
     ```
   - Or download from: https://sites.google.com/chromium.org/driver/

2. Add the test user to the database:
   ```bash
   PYTHONPATH=. python3 app/add_testuser.py
   ```

3. **Start the Flask server** (required for Selenium tests):
   ```bash
   export FLASK_APP=app.py
   flask run
   ```
   (Leave this terminal running.)

4. In a new terminal, run the tests:
   ```bash
   PYTHONPATH=. pytest tests/ # On Windows, $env:PYTHONPATH="."; pytest tests/
   ```

## Project structure:
```
.
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── static/
│   │   ├── css/
│   │   │   ├── base.css
│   │   │   └── intropage.css
│   │   └── images/
│   │       └── Vibe.png
│   └── templates/
│       ├── base.html
│       └── index.html
├── tests/
│   ├── __init__.py
│   └── test_app.py
├── wireframes/
├── migrations/
├── .gitignore
├── README.md
├── add_mood_data.py
├── add_test_data.py
├── app.py
├── config.py
├── create_db.py
├── instructions.txt
└── requirements.txt
```

We acknowledge that we used ChatGPT in the completion of this project.
