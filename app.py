"""CareConnect – Your Health, Your Community, Your Support (Streamlit + SQLite)."""
import html
from datetime import date, datetime, timedelta
from urllib.parse import quote

import streamlit as st

import db
from content import AWARE, CONDITIONS, HOSPITALS, NUMBERS, PREVENT, TIPS

st.set_page_config(page_title="CareConnect", page_icon="🩺", layout="wide")


@st.cache_resource
def boot():
    db.init()
    return True


boot()
e = html.escape
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
PAGES = ["🏠 Dashboard", "📅 Appointments", "💊 Medicines", "👥 Community", "🚨 Emergency", "📚 Health Info", "👤 Profile"]
FREQ = {"Once daily": ["09:00"], "Twice daily": ["08:00", "20:00"],
        "Three times daily": ["08:00", "14:00", "20:00"], "Four times daily": ["06:00", "12:00", "18:00", "22:00"]}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
html, body, .stApp, button, input, textarea {font-family:'Poppins',sans-serif !important;}
.stApp{background:linear-gradient(180deg,#f2fafb 0%,#f4f1fc 100%);}
.block-container{padding-top:1.6rem;max-width:1200px;}
section[data-testid="stSidebar"]{background:linear-gradient(190deg,#0f766e 0%,#14958a 70%,#7c6fd6 140%);}
section[data-testid="stSidebar"] *{color:#fff !important;}
section[data-testid="stSidebar"] div[role="radiogroup"] label{padding:.55rem .8rem;border-radius:12px;width:100%;}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover{background:rgba(255,255,255,.16);}
.card{background:#fff;border:1px solid #e1eff2;border-radius:18px;padding:1rem 1.2rem;margin-bottom:.8rem;box-shadow:0 4px 18px rgba(15,118,110,.08);}
.card h4{margin:0 0 .2rem 0;color:#0f4f4a;font-size:1.02rem;}
.muted{color:#5b7478;font-size:.86rem;}
.hero{background:linear-gradient(120deg,#0f766e 0%,#38b6c9 60%,#a78bfa 120%);color:#fff;border-radius:22px;padding:1.5rem 1.8rem;margin-bottom:1rem;box-shadow:0 8px 24px rgba(15,118,110,.2);}
.hero h1,.hero h2,.hero p{color:#fff;margin:0;}
.hero p{opacity:.92;margin-top:.3rem;}
.pill{display:inline-block;border-radius:999px;padding:2px 11px;font-size:.76rem;background:#e8e3fb;color:#4c3a99;margin-right:6px;}
.pill.t{background:#d5f2ee;color:#0f766e;} .pill.r{background:#fde2e2;color:#b91c1c;} .pill.g{background:#e8eef0;color:#5b7478;}
.stButton>button,.stFormSubmitButton>button{border-radius:12px;border:1px solid #14958a;color:#0f766e;background:#fff;font-weight:600;}
.stButton>button:hover,.stFormSubmitButton>button:hover{background:#e6f6f4;border-color:#0f766e;color:#0f766e;}
.stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primary"],button[data-testid="stBaseButton-primary"],button[data-testid="stBaseButton-primaryFormSubmit"]{background:#0f766e;color:#fff;border:0;}
.sos a{display:block;text-align:center;background:#dc2626;color:#fff !important;border-radius:14px;padding:.8rem;font-weight:700;text-decoration:none;margin:.3rem 0;}
.call{display:inline-block;background:#e6f6f4;color:#0f766e !important;border-radius:10px;padding:3px 12px;font-weight:600;text-decoration:none;}
@media (max-width:700px){.hero{padding:1.1rem;}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ---------------- helpers ----------------
def ago(ts):
    s = (datetime.now() - datetime.fromisoformat(ts)).total_seconds()
    if s < 60: return "just now"
    if s < 3600: return f"{int(s // 60)} min ago"
    if s < 86400: return f"{int(s // 3600)} h ago"
    return f"{int(s // 86400)} d ago"


def go(page):
    st.session_state.nav = page


def pretty(d, t):
    return datetime.strptime(f"{d} {t}", "%Y-%m-%d %H:%M").strftime("%a, %d %b · %I:%M %p")


def card(title, body, pills=""):
    st.markdown(f'<div class="card"><h4>{title}</h4><div class="muted">{body}</div>{pills}</div>', unsafe_allow_html=True)


def upcoming_appts(uid, limit=None):
    t, n = date.today().isoformat(), datetime.now().strftime("%H:%M")
    rows = db.get("SELECT a.*,d.name dname,d.speciality,d.hospital,d.fee FROM appointments a JOIN doctors d ON d.id=a.doctor_id "
                  "WHERE a.user_id=? AND a.status='Booked' AND (a.date>? OR (a.date=? AND a.time>=?)) ORDER BY a.date,a.time",
                  (uid, t, t, n))
    return rows[:limit] if limit else rows


def today_doses(uid):
    t, out = date.today().isoformat(), []
    for m in db.get("SELECT * FROM medicines WHERE user_id=? AND active=1", (uid,)):
        done = {r["time"] for r in db.get("SELECT time FROM med_log WHERE med_id=? AND date=?", (m["id"], t))}
        out += [{**m, "time": tm, "taken": tm in done} for tm in m["times"].split(",")]
    return sorted(out, key=lambda d: d["time"])


def mark_taken(mid, tm):
    db.run("INSERT INTO med_log(med_id,date,time) VALUES(?,?,?)", (mid, date.today().isoformat(), tm))
    st.toast("Marked as taken ✅")


def dose_row(d, key):
    late = (not d["taken"]) and d["time"] < datetime.now().strftime("%H:%M")
    badge = '<span class="pill t">Taken</span>' if d["taken"] else ('<span class="pill r">Overdue</span>' if late else '<span class="pill">Upcoming</span>')
    c1, c2 = st.columns([3, 1])
    c1.markdown(f'<div class="card" style="margin-bottom:.4rem"><h4>💊 {e(d["name"])} · {d["time"]}</h4>'
                f'<div class="muted">{e(d["dosage"])} · {d["frequency"]}</div>{badge}</div>', unsafe_allow_html=True)
    if not d["taken"]:
        c2.button("Mark taken", key=key, on_click=mark_taken, args=(d["id"], d["time"]), use_container_width=True)


def toggle_like(pid, uid):
    if db.one("SELECT 1 FROM likes WHERE post_id=? AND user_id=?", (pid, uid)):
        db.run("DELETE FROM likes WHERE post_id=? AND user_id=?", (pid, uid))
    else:
        db.run("INSERT INTO likes VALUES(?,?)", (pid, uid))


def toggle_group(gid, uid, joined):
    if joined:
        db.run("DELETE FROM group_members WHERE group_id=? AND user_id=?", (gid, uid))
    else:
        db.run("INSERT OR IGNORE INTO group_members VALUES(?,?)", (gid, uid))


def posts_query(uid, where="", args=()):
    return db.get("SELECT p.*,u.name author,g.name gname,(SELECT COUNT(*) FROM likes l WHERE l.post_id=p.id) likes,"
                  "(SELECT COUNT(*) FROM comments c WHERE c.post_id=p.id) ncom,"
                  "EXISTS(SELECT 1 FROM likes l WHERE l.post_id=p.id AND l.user_id=?) liked "
                  "FROM posts p JOIN users u ON u.id=p.user_id LEFT JOIN groups g ON g.id=p.group_id " + where +
                  " ORDER BY p.created DESC", (uid,) + tuple(args))


def post_card(p, uid):
    with st.container(border=True):
        st.markdown(f'**{p["author"]}** · <span class="muted">{ago(p["created"])}</span><br>'
                    f'<span class="pill t">{p["kind"]}</span><span class="pill">{e(p["gname"] or "General")}</span>', unsafe_allow_html=True)
        st.markdown(f'#### {p["title"]}')
        st.markdown(p["body"])
        c1, c2, _ = st.columns([1, 1, 3])
        c1.button(f'{"❤️" if p["liked"] else "🤍"} {p["likes"]}', key=f'lk{p["id"]}', on_click=toggle_like, args=(p["id"], uid))
        with st.expander(f'💬 {p["ncom"]} comments'):
            for c in db.get("SELECT c.*,u.name author FROM comments c JOIN users u ON u.id=c.user_id WHERE post_id=? ORDER BY created", (p["id"],)):
                st.markdown(f'**{c["author"]}** <span class="muted">· {ago(c["created"])}</span>  \n{c["body"]}', unsafe_allow_html=True)
            with st.form(f'cf{p["id"]}', clear_on_submit=True):
                txt = st.text_input("Add a kind comment", key=f'ct{p["id"]}')
                if st.form_submit_button("Comment") and txt.strip():
                    db.run("INSERT INTO comments(post_id,user_id,body,created) VALUES(?,?,?,?)", (p["id"], uid, txt.strip(), db.now()))
                    st.rerun()


# ---------------- authentication ----------------
def auth_page():
    st.markdown('<div class="hero"><h1>🩺 CareConnect</h1><p>Your Health, Your Community, Your Support.<br>'
                'Book doctors, track medicines, get emergency help and talk to people who have been there.</p></div>', unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        t1, t2 = st.tabs(["🔐 Log in", "✨ Create account"])
        with t1:
            with st.form("login"):
                em, pw = st.text_input("Email"), st.text_input("Password", type="password")
                if st.form_submit_button("Log in", type="primary", use_container_width=True):
                    u = db.login(em, pw)
                    if u:
                        st.session_state.user = u
                        st.rerun()
                    st.error("Incorrect email or password.")
            st.info("Demo account: **demo@careconnect.com** / **demo1234**")
        with t2:
            with st.form("reg"):
                n, em, ph = st.text_input("Full name"), st.text_input("Email address"), st.text_input("Phone number")
                p1, p2 = st.text_input("Password (min 6 characters)", type="password"), st.text_input("Confirm password", type="password")
                if st.form_submit_button("Create my account", type="primary", use_container_width=True):
                    if p1 != p2:
                        st.error("Passwords do not match.")
                    else:
                        u, msg = db.register(n, em, ph, p1)
                        if u:
                            st.session_state.user = u
                            st.rerun()
                        st.error(msg)


# ---------------- pages ----------------
def dashboard(u):
    tip = TIPS[date.today().toordinal() % len(TIPS)]
    st.markdown(f'<div class="hero"><h2>Welcome back, {e(u["name"].split()[0])} 👋</h2>'
                f'<p>{date.today():%A, %d %B %Y} · {tip[0]} Tip of the day: {tip[2]}</p></div>', unsafe_allow_html=True)
    cols = st.columns(4)
    for c, (lab, pg) in zip(cols, [("📅 Book a doctor", PAGES[1]), ("💊 Add medicine", PAGES[2]), ("👥 Community", PAGES[3]), ("🚨 Emergency", PAGES[4])]):
        c.button(lab, key="q" + pg, on_click=go, args=(pg,), use_container_width=True)
    doses, appts = today_doses(u["id"]), upcoming_appts(u["id"])
    pend = [d for d in doses if not d["taken"]]
    m = st.columns(4)
    m[0].metric("Upcoming appointments", len(appts))
    m[1].metric("Doses left today", len(pend))
    m[2].metric("Community posts", db.one("SELECT COUNT(*) n FROM posts")["n"])
    m[3].metric("Emergency contacts", db.one("SELECT COUNT(*) n FROM contacts WHERE user_id=?", (u["id"],))["n"])
    l, r = st.columns(2)
    with l:
        st.subheader("📅 Upcoming appointments")
        if not appts:
            st.info("No appointments yet. Book one in a few clicks.")
        for a in appts[:3]:
            card(f'{e(a["dname"])}', f'{a["speciality"]} · {e(a["hospital"])}<br>{pretty(a["date"], a["time"])}')
        st.subheader("🔔 Notifications")
        notes = [f"⚠️ {d['name']} at {d['time']} is overdue." for d in pend if d["time"] < datetime.now().strftime("%H:%M")]
        notes += [f"📅 Appointment with {a['dname']} on {pretty(a['date'], a['time'])}." for a in appts if a["date"] <= (date.today() + timedelta(days=1)).isoformat()]
        notes.append(f"{tip[0]} {tip[1]}: {tip[2]}")
        for n in notes[:4]:
            st.markdown(f'<div class="card" style="padding:.6rem 1rem">{e(n)}</div>', unsafe_allow_html=True)
    with r:
        st.subheader("💊 Medicine reminders")
        if not pend:
            st.success("All done for today. Great job!")
        for d in pend[:4]:
            dose_row(d, f'd{d["id"]}{d["time"]}')
        st.subheader("👥 Community updates")
        for p in posts_query(u["id"])[:3]:
            card(e(p["title"]), f'{p["author"]} · {ago(p["created"])} · ❤️ {p["likes"]} · 💬 {p["ncom"]}', f'<span class="pill">{e(p["gname"] or "General")}</span>')


def appointments(u):
    docs = db.get("SELECT * FROM doctors ORDER BY name")
    t1, t2 = st.tabs(["🩺 Book appointment", "📋 My appointments"])
    def book():
        spec = st.selectbox("Filter by speciality", ["All"] + sorted({d["speciality"] for d in docs}))
        shown = [d for d in docs if spec in ("All", d["speciality"])]
        for i in range(0, len(shown), 2):
            for c, d in zip(st.columns(2), shown[i:i + 2]):
                with c:
                    av = ", ".join(DAYS[int(x)] for x in d["days"].split(","))
                    card(f'{e(d["name"])}', f'{d["speciality"]} · {d["exp"]} yrs · {e(d["hospital"])}<br>Available: {av}',
                         f'<span class="pill t">₹{d["fee"]} fee</span>')
                    c.button("Select doctor", key=f'sd{d["id"]}', on_click=lambda x=d["id"]: st.session_state.update(sel_doc=x), use_container_width=True)
        sel = next((d for d in docs if d["id"] == st.session_state.get("sel_doc")), None)
        st.divider()
        if not sel:
            return st.info("Select a doctor above to choose a date and time.")
        st.subheader(f'Book with {sel["name"]}')
        day = st.date_input("Appointment date", min_value=date.today(), max_value=date.today() + timedelta(days=60))
        if str(day.weekday()) not in sel["days"].split(","):
            return st.warning(f'{sel["name"]} is not available on {day:%A}. Please pick another date.')
        taken = {r["time"] for r in db.get("SELECT time FROM appointments WHERE doctor_id=? AND date=? AND status='Booked'", (sel["id"], day.isoformat()))}
        free = [s for s in sel["slots"].split(",") if s not in taken and not (day == date.today() and s <= datetime.now().strftime("%H:%M"))]
        if not free:
            return st.warning("No free slots on this date. Try another day.")
        tm = st.selectbox("Time slot", free)
        why = st.text_input("Reason for visit (optional)")
        st.caption(f'Consultation fee: ₹{sel["fee"]} (pay at the clinic)')
        if st.button("Confirm booking", type="primary"):
            db.run("INSERT INTO appointments(user_id,doctor_id,date,time,reason) VALUES(?,?,?,?,?)", (u["id"], sel["id"], day.isoformat(), tm, why))
            st.success(f'Booked! {sel["name"]} on {pretty(day.isoformat(), tm)}.')
            st.balloons()

    with t1:
        book()
    with t2:
        rows = db.get("SELECT a.*,d.name dname,d.speciality,d.hospital,d.fee FROM appointments a JOIN doctors d ON d.id=a.doctor_id WHERE a.user_id=? ORDER BY a.date DESC,a.time DESC", (u["id"],))
        if not rows:
            st.info("You have no appointments yet.")
        for a in rows:
            c1, c2 = st.columns([4, 1])
            pill = {"Booked": "t", "Cancelled": "g"}.get(a["status"], "")
            c1.markdown(f'<div class="card"><h4>{e(a["dname"])} · {a["speciality"]}</h4><div class="muted">{pretty(a["date"], a["time"])} · {e(a["hospital"])} · ₹{a["fee"]}'
                        f'{" · " + e(a["reason"]) if a["reason"] else ""}</div><span class="pill {pill}">{a["status"]}</span></div>', unsafe_allow_html=True)
            if a["status"] == "Booked" and c2.button("Cancel", key=f'ca{a["id"]}', use_container_width=True):
                db.run("UPDATE appointments SET status='Cancelled' WHERE id=?", (a["id"],))
                st.rerun()


def medicines(u):
    t1, t2, t3 = st.tabs(["⏰ Today", "➕ Add medicine", "🗂️ All medicines"])
    with t1:
        doses = today_doses(u["id"])
        if not doses:
            st.info("No medicines added yet. Use the Add medicine tab.")
        else:
            st.progress(sum(d["taken"] for d in doses) / len(doses), text=f'{sum(d["taken"] for d in doses)} of {len(doses)} doses taken today')
        for d in doses:
            dose_row(d, f'm{d["id"]}{d["time"]}')
    with t2:
        freq = st.selectbox("How often?", list(FREQ))
        with st.form("addmed", clear_on_submit=True):
            name, dose = st.text_input("Medicine name"), st.text_input("Dosage (e.g. 500 mg, 1 tablet)")
            times = [st.time_input(f"Time {i + 1}", datetime.strptime(t, "%H:%M").time(), key=f"{freq}{i}") for i, t in enumerate(FREQ[freq])]
            if st.form_submit_button("Save reminder", type="primary"):
                if not name.strip() or not dose.strip():
                    st.error("Please enter the medicine name and dosage.")
                else:
                    db.run("INSERT INTO medicines(user_id,name,dosage,frequency,times) VALUES(?,?,?,?,?)",
                           (u["id"], name.strip(), dose.strip(), freq, ",".join(sorted(t.strftime("%H:%M") for t in times))))
                    st.success("Reminder saved.")
    with t3:
        for m in db.get("SELECT * FROM medicines WHERE user_id=? AND active=1", (u["id"],)):
            c1, c2 = st.columns([4, 1])
            c1.markdown(f'<div class="card"><h4>{e(m["name"])}</h4><div class="muted">{e(m["dosage"])} · {m["frequency"]} · {m["times"].replace(",", ", ")}</div></div>', unsafe_allow_html=True)
            if c2.button("Delete", key=f'dm{m["id"]}', use_container_width=True):
                db.run("UPDATE medicines SET active=0 WHERE id=?", (m["id"],))
                st.rerun()


def community(u):
    uid = u["id"]
    t1, t2, t3 = st.tabs(["📰 Feed", "✍️ Share or ask", "🫂 Groups"])
    groups = db.get("SELECT g.*,(SELECT COUNT(*) FROM group_members m WHERE m.group_id=g.id) n,"
                    "EXISTS(SELECT 1 FROM group_members m WHERE m.group_id=g.id AND m.user_id=?) joined FROM groups g ORDER BY g.id", (uid,))
    with t1:
        a, b = st.columns(2)
        gsel = a.selectbox("Group", ["All groups"] + [g["name"] for g in groups])
        q = b.text_input("Search experiences (e.g. migraine, anxiety)")
        where, args = [], []
        if gsel != "All groups":
            where.append("g.name=?"); args.append(gsel)
        if q.strip():
            where.append("(p.title LIKE ? OR p.body LIKE ?)"); args += [f"%{q.strip()}%"] * 2
        posts = posts_query(uid, ("WHERE " + " AND ".join(where)) if where else "", args)
        if not posts:
            st.info("No posts found. Be the first to share your experience.")
        for p in posts:
            post_card(p, uid)
    with t2:
        with st.form("newpost", clear_on_submit=True):
            kind = st.radio("I want to", ["Experience", "Question", "Advice", "Support"], horizontal=True)
            gname = st.selectbox("Post in group", [g["name"] for g in groups if g["joined"]] or ["General Community"])
            title, body = st.text_input("Title"), st.text_area("What would you like to share?", height=150)
            if st.form_submit_button("Post to community", type="primary"):
                if len(title.strip()) < 4 or len(body.strip()) < 15:
                    st.error("Please add a title and at least a few sentences.")
                else:
                    gid = next(g["id"] for g in groups if g["name"] == gname)
                    db.run("INSERT INTO posts(user_id,group_id,kind,title,body,created) VALUES(?,?,?,?,?,?)", (uid, gid, kind, title.strip(), body.strip(), db.now()))
                    st.success("Shared! Others can now like, comment and support you.")
        st.caption("This community shares personal experiences, not medical advice.")
    with t3:
        for g in groups:
            c1, c2 = st.columns([4, 1])
            c1.markdown(f'<div class="card"><h4>{e(g["name"])}</h4><div class="muted">{e(g["about"])}</div>'
                        f'<span class="pill">{g["n"]} members</span>{"<span class=pill>Joined</span>" if g["joined"] else ""}</div>', unsafe_allow_html=True)
            c2.button("Leave" if g["joined"] else "Join", key=f'g{g["id"]}', on_click=toggle_group, args=(g["id"], uid, g["joined"]), use_container_width=True)
        with st.expander("➕ Create a discussion group"):
            with st.form("newgroup", clear_on_submit=True):
                gn, ga = st.text_input("Group name (e.g. Asthma Warriors)"), st.text_input("What is this group about?")
                if st.form_submit_button("Create group", type="primary"):
                    if len(gn.strip()) < 3:
                        st.error("Please give the group a name.")
                    elif db.one("SELECT 1 FROM groups WHERE name=?", (gn.strip(),)):
                        st.error("A group with this name already exists.")
                    else:
                        gid = db.run("INSERT INTO groups(name,about,created_by) VALUES(?,?,?)", (gn.strip(), ga.strip(), uid))
                        db.run("INSERT INTO group_members VALUES(?,?)", (gid, uid))
                        st.rerun()


def emergency(u):
    st.markdown('<style>.stButton>button[kind="primary"],button[data-testid="stBaseButton-primary"]{background:#dc2626;color:#fff;border:0;font-size:1.2rem;padding:.9rem;}</style>', unsafe_allow_html=True)
    st.markdown('<div class="hero" style="background:linear-gradient(120deg,#b91c1c,#ef4444 70%,#a78bfa 130%)"><h2>🚨 Emergency assistance</h2><p>In a life-threatening emergency call 112 immediately.</p></div>', unsafe_allow_html=True)
    contacts = db.get("SELECT * FROM contacts WHERE user_id=?", (u["id"],))
    if st.button("🆘 EMERGENCY SOS", type="primary", use_container_width=True):
        st.session_state.sos = True
    if st.session_state.get("sos"):
        links = '<a href="tel:112">📞 Call 112 (National Emergency)</a><a href="tel:108">🚑 Call 108 (Ambulance)</a>'
        links += "".join(f'<a href="tel:{c["phone"]}">📞 Call {e(c["name"])} ({e(c["relation"])})</a>' for c in contacts)
        st.markdown(f'<div class="sos">{links}</div>', unsafe_allow_html=True)
        st.error("SOS activated. Tap a button to call. Tell them your exact location and what happened. Stay calm and stay on the line.")
        if st.button("Cancel SOS"):
            st.session_state.sos = False
            st.rerun()
    t1, t2, t3 = st.tabs(["☎️ Emergency numbers", "🏥 Nearby hospitals", "👨‍👩‍👧 My emergency contacts"])
    with t1:
        for n, num, d in NUMBERS:
            st.markdown(f'<div class="card"><h4>{n}</h4><div class="muted">{d}</div><a class="call" href="tel:{num}">📞 {num}</a></div>', unsafe_allow_html=True)
    with t2:
        st.caption("Sample hospitals for the demo. In a real version these come from a maps service using your live location.")
        kind = st.selectbox("Type", ["All"] + sorted({h[1] for h in HOSPITALS}))
        for n, k, dist, ph, info in HOSPITALS:
            if kind in ("All", k):
                st.markdown(f'<div class="card"><h4>{n}</h4><div class="muted">{k} · {info} · <b>{dist}</b> away</div>'
                            f'<a class="call" href="tel:{ph}">📞 {ph}</a> <a class="call" href="https://www.google.com/maps/search/{quote(n)}" target="_blank">🗺️ Directions</a></div>', unsafe_allow_html=True)
    with t3:
        with st.form("addc", clear_on_submit=True):
            a, b, c = st.columns(3)
            cn, cp, cr = a.text_input("Name"), b.text_input("Phone"), c.selectbox("Relation", ["Family", "Friend", "Doctor", "Neighbour", "Other"])
            if st.form_submit_button("Save contact", type="primary"):
                if cn.strip() and cp.strip().replace("+", "").isdigit():
                    db.run("INSERT INTO contacts(user_id,name,phone,relation) VALUES(?,?,?,?)", (u["id"], cn.strip(), cp.strip(), cr))
                    st.rerun()
                else:
                    st.error("Enter a name and a valid phone number.")
        for c in contacts:
            c1, c2 = st.columns([4, 1])
            c1.markdown(f'<div class="card"><h4>{e(c["name"])} <span class="pill">{c["relation"]}</span></h4><a class="call" href="tel:{e(c["phone"])}">📞 {e(c["phone"])}</a></div>', unsafe_allow_html=True)
            if c2.button("Remove", key=f'rc{c["id"]}', use_container_width=True):
                db.run("DELETE FROM contacts WHERE id=?", (c["id"],))
                st.rerun()


def health_info(u):
    t1, t2, t3, t4 = st.tabs(["💡 Wellness tips", "🩻 Common conditions", "🛡️ Prevention", "🎗️ Awareness"])
    with t1:
        for i in range(0, len(TIPS), 3):
            for c, t in zip(st.columns(3), TIPS[i:i + 3]):
                with c:
                    card(f"{t[0]} {t[1]}", t[2])
    with t2:
        for name, d in CONDITIONS.items():
            with st.expander(name):
                st.markdown(f'**What it is:** {d[0]}\n\n**Common signs:** {d[1]}\n\n**Self-care:** {d[2]}\n\n**See a doctor if:** {d[3]}')
        st.caption("General information only. It is not a diagnosis or a substitute for professional care.")
    with t3:
        for t, d in PREVENT:
            card(t, d)
    with t4:
        for d, n, w in AWARE:
            card(f"🎗️ {n}", f"{d} · {w}")


def profile(u):
    uid = u["id"]
    st.markdown(f'<div class="hero"><h2>👤 {e(u["name"])}</h2><p>{e(u["email"])} · {e(u["phone"])} · Member since {u["created"][:10]}</p></div>', unsafe_allow_html=True)
    t1, t2, t3, t4 = st.tabs(["✏️ Edit profile", "📅 Appointments", "💊 Medicines", "👥 Community activity"])
    with t1:
        with st.form("prof"):
            n, p = st.text_input("Full name", u["name"]), st.text_input("Phone number", u["phone"])
            old, new = st.text_input("Current password (only to change it)", type="password"), st.text_input("New password", type="password")
            if st.form_submit_button("Save changes", type="primary"):
                if len(n.strip()) < 2 or not p.strip().replace("+", "").isdigit():
                    st.error("Please enter a valid name and phone number.")
                elif new and not (len(new) >= 6 and db.login(u["email"], old)):
                    st.error("Current password is wrong or the new one is shorter than 6 characters.")
                else:
                    db.run("UPDATE users SET name=?,phone=? WHERE id=?", (n.strip(), p.strip(), uid))
                    if new:
                        s, h = db.hash_pw(new)
                        db.run("UPDATE users SET salt=?,pw=? WHERE id=?", (s, h, uid))
                    st.session_state.user = db.one("SELECT * FROM users WHERE id=?", (uid,))
                    st.success("Profile updated.")
                    st.rerun()
    with t2:
        rows = db.get("SELECT a.date,a.time,d.name doctor,d.speciality,a.status FROM appointments a JOIN doctors d ON d.id=a.doctor_id WHERE a.user_id=? ORDER BY a.date DESC", (uid,))
        st.dataframe(rows, use_container_width=True, hide_index=True) if rows else st.info("No appointments yet.")
        st.button("Manage appointments", on_click=go, args=(PAGES[1],))
    with t3:
        rows = db.get("SELECT name,dosage,frequency,times FROM medicines WHERE user_id=? AND active=1", (uid,))
        st.dataframe(rows, use_container_width=True, hide_index=True) if rows else st.info("No medicines yet.")
        st.button("Manage medicines", on_click=go, args=(PAGES[2],))
    with t4:
        a = st.columns(3)
        a[0].metric("Posts", db.one("SELECT COUNT(*) n FROM posts WHERE user_id=?", (uid,))["n"])
        a[1].metric("Comments", db.one("SELECT COUNT(*) n FROM comments WHERE user_id=?", (uid,))["n"])
        a[2].metric("Groups joined", db.one("SELECT COUNT(*) n FROM group_members WHERE user_id=?", (uid,))["n"])
        mine = posts_query(uid, "WHERE p.user_id=?", (uid,))
        for p in mine:
            card(e(p["title"]), f'{ago(p["created"])} · ❤️ {p["likes"]} · 💬 {p["ncom"]}', f'<span class="pill">{e(p["gname"] or "General")}</span>')
        if not mine:
            st.info("You have not posted yet. Share your first experience in the Community.")


# ---------------- router ----------------
if "user" not in st.session_state:
    auth_page()
else:
    u = st.session_state.user
    with st.sidebar:
        st.markdown("## 🩺 CareConnect")
        st.caption("Your Health, Your Community, Your Support")
        st.radio("Menu", PAGES, key="nav", label_visibility="collapsed")
        st.divider()
        st.markdown(f"Signed in as **{e(u['name'])}**")
        if st.button("Log out", use_container_width=True):
            st.session_state.clear()
            st.rerun()
    {PAGES[0]: dashboard, PAGES[1]: appointments, PAGES[2]: medicines, PAGES[3]: community,
     PAGES[4]: emergency, PAGES[5]: health_info, PAGES[6]: profile}[st.session_state.nav](u)
