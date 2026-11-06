# CareConnect – Your Health, Your Community, Your Support

A Streamlit + SQLite prototype: login/registration, dashboard, doctor appointments,
medicine reminders, community (posts, likes, comments, groups), emergency SOS and
health information.

## Run it
1. Install Python 3.9+ from python.org.
2. In this folder, install the dependency:
       pip install -r requirements.txt
3. Start the app:
       streamlit run app.py
4. Open http://localhost:8501 if it does not open automatically.

The database (`careconnect.db`) is created with sample doctors, groups and posts on first run.
Delete that file to reset everything.

**Demo login:** demo@careconnect.com / demo1234 (or register a new account).

## Files
- `app.py`     pages and interface
- `db.py`      SQLite tables, password hashing (PBKDF2), sample data
- `content.py` health tips, conditions, emergency numbers, sample hospitals
