"""CareConnect database layer (SQLite): schema, auth helpers, sample data."""
import hashlib, hmac, os, re, secrets, sqlite3
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "careconnect.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, phone TEXT, salt TEXT, pw TEXT, created TEXT);
CREATE TABLE IF NOT EXISTS doctors(id INTEGER PRIMARY KEY, name TEXT, speciality TEXT, hospital TEXT, days TEXT, slots TEXT, fee INTEGER, exp INTEGER);
CREATE TABLE IF NOT EXISTS appointments(id INTEGER PRIMARY KEY, user_id INT, doctor_id INT, date TEXT, time TEXT, reason TEXT, status TEXT DEFAULT 'Booked');
CREATE TABLE IF NOT EXISTS medicines(id INTEGER PRIMARY KEY, user_id INT, name TEXT, dosage TEXT, frequency TEXT, times TEXT, active INT DEFAULT 1);
CREATE TABLE IF NOT EXISTS med_log(id INTEGER PRIMARY KEY, med_id INT, date TEXT, time TEXT);
CREATE TABLE IF NOT EXISTS groups(id INTEGER PRIMARY KEY, name TEXT UNIQUE, about TEXT, created_by INT);
CREATE TABLE IF NOT EXISTS group_members(group_id INT, user_id INT, PRIMARY KEY(group_id, user_id));
CREATE TABLE IF NOT EXISTS posts(id INTEGER PRIMARY KEY, user_id INT, group_id INT, kind TEXT, title TEXT, body TEXT, created TEXT);
CREATE TABLE IF NOT EXISTS likes(post_id INT, user_id INT, PRIMARY KEY(post_id, user_id));
CREATE TABLE IF NOT EXISTS comments(id INTEGER PRIMARY KEY, post_id INT, user_id INT, body TEXT, created TEXT);
CREATE TABLE IF NOT EXISTS contacts(id INTEGER PRIMARY KEY, user_id INT, name TEXT, phone TEXT, relation TEXT);
"""


def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def run(sql, args=()):
    """Execute a write statement and return the new row id."""
    c = _conn()
    try:
        cur = c.execute(sql, args)
        c.commit()
        return cur.lastrowid
    finally:
        c.close()


def get(sql, args=()):
    """Return all rows as a list of dicts."""
    c = _conn()
    try:
        return [dict(r) for r in c.execute(sql, args).fetchall()]
    finally:
        c.close()


def one(sql, args=()):
    rows = get(sql, args)
    return rows[0] if rows else None


def now(hours_ago=0):
    return (datetime.now() - timedelta(hours=hours_ago)).isoformat(timespec="seconds")


# ---------- authentication ----------
def hash_pw(pw, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), 120_000).hex()
    return salt, digest


def register(name, email, phone, pw):
    name, email, phone = name.strip(), email.strip().lower(), phone.strip()
    if len(name) < 2:
        return None, "Please enter your full name."
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return None, "Please enter a valid email address."
    if not re.fullmatch(r"\+?\d{10,13}", phone):
        return None, "Phone number must have 10 to 13 digits."
    if len(pw) < 6:
        return None, "Password must be at least 6 characters."
    if one("SELECT id FROM users WHERE email=?", (email,)):
        return None, "An account with this email already exists. Please log in."
    salt, digest = hash_pw(pw)
    uid = run("INSERT INTO users(name,email,phone,salt,pw,created) VALUES(?,?,?,?,?,?)",
              (name, email, phone, salt, digest, now()))
    run("INSERT OR IGNORE INTO group_members VALUES(1, ?)", (uid,))
    return one("SELECT * FROM users WHERE id=?", (uid,)), "Welcome to CareConnect!"


def login(email, pw):
    u = one("SELECT * FROM users WHERE email=?", (email.strip().lower(),))
    if not u or u["salt"] == "-":
        return None
    _, digest = hash_pw(pw, u["salt"])
    return u if hmac.compare_digest(digest, u["pw"]) else None


# ---------- setup and sample data ----------
def init():
    c = _conn()
    c.executescript(SCHEMA)
    c.commit()
    c.close()
    if one("SELECT id FROM users LIMIT 1"):
        return
    # community members (cannot log in) plus a demo account
    for n in ["Aarti", "Rohan", "Meera", "Kabir", "Isha"]:
        run("INSERT INTO users(name,email,phone,salt,pw,created) VALUES(?,?,?,?,?,?)",
            (n, n.lower() + "@seed.local", "9000000000", "-", "-", now()))
    salt, digest = hash_pw("demo1234")
    demo = run("INSERT INTO users(name,email,phone,salt,pw,created) VALUES(?,?,?,?,?,?)",
               ("Demo Student", "demo@careconnect.com", "9876543210", salt, digest, now()))

    slots = "09:00,10:00,11:00,12:00,14:00,15:00,16:00,17:00"
    docs = [
        ("Dr. Anita Sharma", "General Physician", "City Care Hospital", "0,1,2,3,4,5", 400, 12),
        ("Dr. Rahul Mehta", "Neurologist", "Apex Neuro Centre", "0,2,4", 900, 15),
        ("Dr. Priya Nair", "Psychologist", "MindWell Clinic", "1,3,5", 700, 9),
        ("Dr. Sanjay Gupta", "Diabetologist", "Sunrise Hospital", "0,1,2,3,4", 600, 18),
        ("Dr. Kavita Rao", "Gynaecologist", "Lotus Women’s Care", "0,1,3,4,5", 800, 14),
        ("Dr. Imran Khan", "Orthopaedic", "Bone & Joint Institute", "1,2,4,5", 750, 11),
        ("Dr. Sneha Patil", "Dermatologist", "Glow Skin Clinic", "0,2,3,5", 500, 8),
        ("Dr. Arjun Verma", "Paediatrician", "Little Steps Hospital", "0,1,2,3,4,5", 500, 10),
    ]
    for d in docs:
        run("INSERT INTO doctors(name,speciality,hospital,days,slots,fee,exp) VALUES(?,?,?,?,?,?,?)",
            (d[0], d[1], d[2], d[3], slots, d[4], d[5]))

    groups = [
        ("General Community", "Open space for everyone to share and support each other."),
        ("Migraine Support", "Triggers, coping tips and recovery stories for migraines and headaches."),
        ("Mental Wellness", "Stress, anxiety and exam pressure: you are not alone."),
        ("Diabetes Care", "Living well with diabetes: food, monitoring and motivation."),
        ("Fitness & Recovery", "Injuries, physiotherapy and getting back to activity."),
    ]
    for g in groups:
        run("INSERT INTO groups(name,about,created_by) VALUES(?,?,1)", g)
    for gid in range(1, 6):
        for uid in range(1, 7):
            run("INSERT OR IGNORE INTO group_members VALUES(?,?)", (gid, uid))
    run("INSERT OR IGNORE INTO group_members VALUES(1, ?)", (demo,))

    posts = [
        (1, 2, "Experience", "Frequent migraines: what helped me",
         "My migraines started during exams. A dark room, water and a regular sleep time helped. Writing a trigger diary showed that skipping breakfast was my trigger.", 50),
        (3, 3, "Question", "Anyone else getting anxious before presentations?",
         "My heart races and I avoid college events. How do you handle it? Any breathing exercises that really work?", 30),
        (4, 4, "Advice", "Newly diagnosed? Start with a diabetes educator",
         "A diabetes educator taught me carb counting step by step. Meeting others who check their sugar daily made everything feel normal.", 20),
        (2, 5, "Experience", "Back to football after a knee injury",
         "Physio felt slow, but the boring exercises every day brought me back to the pitch. Please be patient with your body.", 12),
        (3, 1, "Support", "Sleep and screen time",
         "I stopped using my phone in bed and my headaches got less frequent. Small changes add up.", 5),
    ]
    for uid, gid, kind, title, body, h in posts:
        run("INSERT INTO posts(user_id,group_id,kind,title,body,created) VALUES(?,?,?,?,?,?)",
            (uid, gid, kind, title, body, now(h)))
    for pid, uid in [(1, 3), (1, 4), (1, demo), (2, 1), (2, 5), (3, 2), (4, 1)]:
        run("INSERT OR IGNORE INTO likes VALUES(?,?)", (pid, uid))
    run("INSERT INTO comments(post_id,user_id,body,created) VALUES(1,3,'Same here! A diary made it easy to explain things to my doctor.',?)", (now(40),))
    run("INSERT INTO comments(post_id,user_id,body,created) VALUES(2,5,'Slow breathing and practising with two friends helped me a lot.',?)", (now(20),))

    # demo account data
    tomorrow = (datetime.now() + timedelta(days=1)).date().isoformat()
    run("INSERT INTO appointments(user_id,doctor_id,date,time,reason) VALUES(?,?,?,?,?)",
        (demo, 1, tomorrow, "10:00", "General check-up"))
    run("INSERT INTO medicines(user_id,name,dosage,frequency,times) VALUES(?,?,?,?,?)",
        (demo, "Vitamin D3", "1 tablet (60,000 IU)", "Once daily", "09:00"))
    run("INSERT INTO medicines(user_id,name,dosage,frequency,times) VALUES(?,?,?,?,?)",
        (demo, "Paracetamol", "500 mg", "Twice daily", "08:00,20:00"))
    run("INSERT INTO contacts(user_id,name,phone,relation) VALUES(?,?,?,?)",
        (demo, "Mom", "9812345678", "Family"))
