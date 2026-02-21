from google_auth import handle_google_auth, google_login_button

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sqlite3
import hashlib
from collections import Counter
from datetime import datetime
import urllib.request
import xml.etree.ElementTree as ET
import time
import json
import os

st.set_page_config(
    page_title="CampusEdge – Market Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

import streamlit.components.v1 as components
_PLUM_JS = """
<script>
(function forcePlum() {
  const styles = `
    .stApp, .main, [data-testid="stAppViewContainer"] { background-color: #171523 !important; }
    [data-testid="stSidebar"], section[data-testid="stSidebar"] > div { background-color: #1e1a2e !important; border-right: 1px solid #3d2f5a !important; }
    .block-container { background-color: #171523 !important; }
    [data-testid="stHeader"] { background-color: #171523 !important; }
    h1,h2,h3,h4,h5,h6 { color: #e8d5f5 !important; }
    p, label, .stCaption { color: #9d87b8 !important; }
    .stTextInput input { background-color: #232131 !important; color: #e8d5f5 !important; border-color: #3d2f5a !important; }
    .stTextArea textarea { background-color: #232131 !important; color: #e8d5f5 !important; border-color: #3d2f5a !important; }
    .stNumberInput input { background-color: #232131 !important; color: #e8d5f5 !important; }
    [data-baseweb="select"] > div { background-color: #232131 !important; border-color: #3d2f5a !important; color: #e8d5f5 !important; }
    [data-baseweb="popover"] { background-color: #232131 !important; }
    [role="listbox"] li { background-color: #232131 !important; color: #e8d5f5 !important; }
    [role="listbox"] li:hover { background-color: #2a2040 !important; }
    [data-baseweb="tab-list"] { background-color: #1e1a2e !important; }
    [data-baseweb="tab"] { color: #9d87b8 !important; }
    [aria-selected="true"][data-baseweb="tab"] { color: #e91e8c !important; border-bottom: 2px solid #e91e8c !important; }
    button[kind="primary"], [data-testid="baseButton-primary"] { background-color: #e91e8c !important; border-color: #e91e8c !important; color: #fff !important; }
    button[kind="secondary"], [data-testid="baseButton-secondary"] { background-color: #232131 !important; border-color: #3d2f5a !important; color: #c9a8f0 !important; }
    [data-testid="stDataFrame"] th { background-color: #2a2040 !important; color: #c9a8f0 !important; }
    [data-testid="stDataFrame"] td { background-color: #232131 !important; color: #e8d5f5 !important; }
    details, .streamlit-expanderHeader { background-color: #232131 !important; color: #c9a8f0 !important; border-color: #3d2f5a !important; }
    .streamlit-expanderContent { background-color: #1e1a2e !important; }
    hr { border-color: #3d2f5a !important; }
    [data-testid="stSlider"] [role="slider"] { background-color: #e91e8c !important; }
  `;
  const el = document.createElement('style');
  el.id = 'plum-override';
  el.textContent = styles;
  document.head.appendChild(el);
  new MutationObserver(() => {
    if (!document.getElementById('plum-override')) document.head.appendChild(el);
  }).observe(document.body, { childList: true, subtree: true });
})();
</script>
"""
components.html(_PLUM_JS, height=0, scrolling=False)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
  --plum-bg:       #171523;
  --plum-card:     #232131;
  --plum-elevated: #2a2040;
  --plum-border:   #3d2f5a;
  --plum-accent:   #c482d5;
  --plum-lavender: #b388f4;
  --plum-pink:     #e91e8c;
  --plum-soft:     #f48fb1;
  --plum-text:     #e8d5f5;
  --plum-muted:    #9d87b8;
  --plum-dim:      #7a6e8a;
}

html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif !important; }
.stApp { background-color: #171523 !important; }
.main  { background-color: #171523 !important; }
section[data-testid="stSidebar"] { background-color: #1e1a2e !important; border-right: 1px solid #3d2f5a !important; }
.block-container { padding: 2rem 3rem; background-color: #171523 !important; }
div[data-testid="stForm"] { background-color: #232131 !important; border: 1px solid #3d2f5a !important; }
div.stButton > button[kind="primary"] { background-color: #c482d5 !important; border-color: #c482d5 !important; color: #fff !important; }
div.stButton > button[kind="primary"]:hover { background-color: #b36ec0 !important; }
div.stButton > button[kind="secondary"] { background-color: #232131 !important; border-color: #3d2f5a !important; color: #c9a8f0 !important; }
div.stButton > button[kind="secondary"]:hover { border-color: #c482d5 !important; }
.stSelectbox label, .stSlider label, .stNumberInput label, .stTextInput label, .stTextArea label, .stMultiselect label { color: #9d87b8 !important; }
div[data-baseweb="select"] { background-color: #232131 !important; border-color: #3d2f5a !important; }
div[data-baseweb="input"] input { background-color: #232131 !important; color: #e8d5f5 !important; border-color: #3d2f5a !important; }
div[data-baseweb="textarea"] textarea { background-color: #232131 !important; color: #e8d5f5 !important; border-color: #3d2f5a !important; }
.stTabs [data-baseweb="tab-list"] { background-color: #1e1a2e !important; border-radius: 8px; }
.stTabs [data-baseweb="tab"] { color: #9d87b8 !important; }
.stTabs [aria-selected="true"] { color: #c482d5 !important; background-color: #2a2040 !important; }
.stDataFrame { background-color: #232131 !important; }
.stExpander { background-color: #232131 !important; border: 1px solid #3d2f5a !important; }
.stExpander summary { color: #c9a8f0 !important; }
div[data-testid="stMetricValue"] { color: #b388f4 !important; }
.stAlert { background-color: #2a2040 !important; }
.hero-title { font-size: 3.2rem; font-weight: 700; background: linear-gradient(135deg, #b388f4, #c482d5); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.1; margin-bottom: 0.3rem; }
.hero-sub { font-size: 1.1rem; color: #9d87b8; margin-bottom: 2rem; }
.skill-chip-have { display: inline-block; background: #231a35; color: #e91e8c; border: 1px solid #3d2f5a; border-radius: 20px; padding: 4px 14px; font-size: 0.85rem; margin: 4px; font-family: 'JetBrains Mono', monospace; }
.skill-chip-missing { display: inline-block; background: #1f1228; color: #f06292; border: 1px solid #3d1a45; border-radius: 20px; padding: 4px 14px; font-size: 0.85rem; margin: 4px; font-family: 'JetBrains Mono', monospace; }
.action-card { background: linear-gradient(135deg, #1e1a2e, #2a2040); border: 1px solid #3d2f5a; border-radius: 12px; padding: 1.2rem 1.5rem; margin-bottom: 0.8rem; }
.action-title { font-weight: 700; color: #c9a8f0; font-size: 1rem; }
.action-meta { color: #7a6e8a; font-size: 0.82rem; margin-top: 0.2rem; }
.action-link { color: #b388f4; font-size: 0.85rem; }
.metric-box { background: #232131; border: 1px solid #2d2545; border-radius: 12px; padding: 1.2rem; text-align: center; }
.metric-val { font-size: 2.2rem; font-weight: 700; color: #b388f4; }
.metric-label { color: #9d87b8; font-size: 0.82rem; margin-top: 0.2rem; }
.section-header { font-size: 1.4rem; font-weight: 700; color: #e8d5f5; margin-bottom: 1rem; border-left: 4px solid #c482d5; padding-left: 0.8rem; margin-top: 1.5rem; }
.profile-badge { display: inline-block; background: #2a2040; color: #c9a8f0; border: 1px solid #3d2f5a; border-radius: 8px; padding: 6px 14px; font-size: 0.85rem; margin: 4px; }
.bonus-card { background: #1e1a2e; border: 1px solid #3d2f5a; border-radius: 12px; padding: 1rem 1.4rem; margin-bottom: 0.6rem; }
.warning-card { background: #231530; border: 1px solid #4a1a5a; border-radius: 12px; padding: 1rem 1.4rem; margin-bottom: 0.6rem; }
.peer-card { background: #1e1a2e; border: 1px solid #3d2f5a; border-radius: 10px; padding: 0.8rem 1.2rem; margin-bottom: 0.5rem; color: #9d87b8; font-size: 0.88rem; }
.intel-box { background: linear-gradient(135deg, #1e1a2e, #2a2040); border: 1px solid #c482d5; border-radius: 14px; padding: 1.2rem 1.6rem; margin-bottom: 1rem; }
.prob-box { background: linear-gradient(135deg, #1e1a2e, #231a35); border: 1px solid #3d2f5a; border-radius: 14px; padding: 1.2rem 1.6rem; margin-bottom: 1rem; }
.compare-card { background: #232131; border: 1px solid #2d2545; border-radius: 12px; padding: 1rem 1.2rem; margin-bottom: 0.5rem; }
.drive-card { background: #232131; border: 1px solid #3d2f5a; border-radius: 14px; padding: 1.3rem 1.6rem; margin-bottom: 1rem; }
.drive-card:hover { border-color: #c482d5; }
.ann-card { border-radius: 12px; padding: 1rem 1.4rem; margin-bottom: 0.7rem; }
.ann-high   { background: #1f1228; border-left: 4px solid #ef4444; }
.ann-normal { background: #232131; border-left: 4px solid #c482d5; }
.ann-low    { background: #1a1525; border-left: 4px solid #c482d5; }
.ann-title  { font-weight: 700; color: #e8d5f5; font-size: 0.95rem; }
.ann-body   { color: #7a6e8a; font-size: 0.85rem; margin-top: 0.3rem; }
.ann-time   { color: #4a3a60; font-size: 0.75rem; margin-top: 0.4rem; }
.login-wrap { max-width: 440px; margin: 3rem auto; background: #232131; border: 1px solid #3d2f5a; border-radius: 20px; padding: 2.5rem; }
.login-title { font-size: 2rem; font-weight: 700; background: linear-gradient(135deg, #b388f4, #c482d5); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 0.3rem; }
.login-sub { text-align: center; color: #7a6e8a; font-size: 0.88rem; margin-bottom: 1.8rem; }
.demo-creds { background: #171523; border: 1px solid #2d2545; border-radius: 10px; padding: 0.8rem 1rem; margin-top: 1.2rem; font-size: 0.8rem; color: #7a6e8a; font-family: 'JetBrains Mono', monospace; }
.chip { display: inline-block; border-radius: 20px; padding: 3px 12px; font-size: 0.78rem; margin: 3px; font-family: 'JetBrains Mono', monospace; }
.chip-green  { background: #231a35; color: #e91e8c; border: 1px solid #3d2f5a; }
.chip-red    { background: #1f1228; color: #f06292; border: 1px solid #3d1a45; }
.chip-blue   { background: #231a35; color: #c9a8f0; border: 1px solid #1d4ed8; }
.chip-gray   { background: #1e1a2e; color: #9d87b8; border: 1px solid #2d2545; }
.chip-amber  { background: #231a35; color: #f48fb1; border: 1px solid #4a1a5a; }
.prog-wrap { background: #1e1a2e; border-radius: 20px; height: 6px; margin-top: 6px; }
.prog-fill { border-radius: 20px; height: 6px; }
.apply-btn {
    display: inline-block;
    background: linear-gradient(135deg, #e91e8c, #c482d5);
    color: #fff !important;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 0.88rem;
    padding: 8px 20px;
    border-radius: 8px;
    text-decoration: none !important;
    border: none;
    cursor: pointer;
    transition: opacity 0.2s;
    letter-spacing: 0.02em;
}
.apply-btn:hover { opacity: 0.85; }
.apply-btn-applied {
    display: inline-block;
    background: #1e1a2e;
    color: #e91e8c !important;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 0.88rem;
    padding: 8px 20px;
    border-radius: 8px;
    text-decoration: none !important;
    border: 1px solid #e91e8c;
    cursor: default;
}
.apply-btn-disabled {
    display: inline-block;
    background: #1a1525;
    color: #7a6e8a !important;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 0.88rem;
    padding: 8px 20px;
    border-radius: 8px;
    text-decoration: none !important;
    border: 1px solid #3d2f5a;
    cursor: not-allowed;
}
/* Floating chatbot */
.floating-chat-btn {
    position: fixed;
    bottom: 24px;
    right: 24px;
    z-index: 9998;
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: linear-gradient(135deg, #e91e8c, #c482d5);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    cursor: pointer;
    box-shadow: 0 4px 20px rgba(233,30,140,0.4);
}
.floating-chat-popup {
    position: fixed;
    bottom: 90px;
    right: 24px;
    width: 360px;
    max-height: 520px;
    background: #1e1a2e;
    border: 1px solid #3d2f5a;
    border-radius: 16px;
    z-index: 9997;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
}
.floating-chat-header {
    padding: 0.8rem 1.2rem;
    background: linear-gradient(135deg, #2a2040, #3d2f5a);
    font-weight: 700;
    color: #e8d5f5;
    font-size: 0.9rem;
    border-bottom: 1px solid #3d2f5a;
}
.floating-chat-body {
    flex: 1;
    overflow-y: auto;
    padding: 0.8rem 1rem;
}
.fchat-msg-user {
    background: #2a1a45;
    border-radius: 12px 12px 4px 12px;
    padding: 0.5rem 0.8rem;
    margin: 0.4rem 0 0.4rem 2rem;
    color: #e8d5f5;
    font-size: 0.85rem;
}
.fchat-msg-ai {
    background: #232131;
    border-radius: 12px 12px 12px 4px;
    padding: 0.5rem 0.8rem;
    margin: 0.4rem 2rem 0.4rem 0;
    color: #e8d5f5;
    font-size: 0.85rem;
}
#MainMenu { visibility: hidden; } footer { visibility: hidden; } header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DATABASE LAYER
# ══════════════════════════════════════════════════════════════════════════════
DB_PATH = "CampusEdge.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL, password TEXT NOT NULL,
        role TEXT NOT NULL, name TEXT,
        created_at TEXT DEFAULT (datetime('now')))""")
    c.execute("""CREATE TABLE IF NOT EXISTS student_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL, name TEXT, branch TEXT, year TEXT,
        target_role TEXT, skills TEXT, cgpa REAL, internships INTEGER DEFAULT 0,
        projects INTEGER DEFAULT 0, certifications INTEGER DEFAULT 0,
        backlogs INTEGER DEFAULT 0, linkedin TEXT DEFAULT '', github TEXT DEFAULT '',
        readiness_score INTEGER DEFAULT 0,
        updated_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(user_id) REFERENCES users(id))""")
    c.execute("""CREATE TABLE IF NOT EXISTS score_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER, score INTEGER, target_role TEXT,
        recorded_at TEXT DEFAULT (datetime('now')))""")
    c.execute("""CREATE TABLE IF NOT EXISTS placement_drives (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT, role TEXT, package TEXT, description TEXT,
        eligibility_cgpa REAL DEFAULT 6.0, eligible_branches TEXT,
        required_skills TEXT, drive_date TEXT, apply_link TEXT,
        posted_by INTEGER, posted_at TEXT DEFAULT (datetime('now')),
        is_active INTEGER DEFAULT 1)""")
    c.execute("""CREATE TABLE IF NOT EXISTS drive_applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        drive_id INTEGER, user_id INTEGER, status TEXT DEFAULT 'Applied',
        applied_at TEXT DEFAULT (datetime('now')))""")
    c.execute("""CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT, content TEXT, priority TEXT DEFAULT 'normal',
        posted_by INTEGER, posted_at TEXT DEFAULT (datetime('now')))""")
    c.execute("""CREATE TABLE IF NOT EXISTS tpo_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        designation TEXT DEFAULT '',
        department TEXT DEFAULT '',
        college TEXT DEFAULT '',
        email TEXT DEFAULT '',
        phone TEXT DEFAULT '',
        updated_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(user_id) REFERENCES users(id))""")

    for uname, pw, role, name in [
        ("tpo_admin", "tpo123", "tpo", "Dr. Placement Officer"),
        ("student_demo", "student123", "student", "Demo Student"),
    ]:
        c.execute("INSERT OR IGNORE INTO users (username,password,role,name) VALUES (?,?,?,?)",
                  (uname, hash_pw(pw), role, name))

    for d in [
        ("Google","Software Engineer","25 LPA","SWE role. Rounds: OA → 3 Tech → HR.",7.5,"Computer Science,Information Technology","Python,DSA,System Design","2025-03-15","https://careers.google.com",1),
        ("TCS","Data Analyst","6.5 LPA","TCS Digital hiring for data roles.",6.0,"Computer Science,Information Technology,Electronics","Python,SQL,Excel","2025-03-20","https://www.tcs.com/careers",1),
        ("HUL","Marketing Analyst","8 LPA","HUL management trainee program.",7.0,"MBA,BBA,Computer Science","Excel,Communication,Google Analytics","2025-04-01","https://www.hul.co.in/careers/",1),
        ("Swiggy","UI/UX Designer","10 LPA","Design team expansion. Portfolio mandatory.",6.5,"Computer Science,Information Technology,Other","Figma,Prototyping,User Research","2025-04-10","https://careers.swiggy.com",1),
    ]:
        d_exists = c.execute("SELECT id FROM placement_drives WHERE company=? AND role=?", (d[0], d[1])).fetchone()
        if not d_exists:
            c.execute("INSERT INTO placement_drives (company,role,package,description,eligibility_cgpa,eligible_branches,required_skills,drive_date,apply_link,posted_by) VALUES (?,?,?,?,?,?,?,?,?,?)", d)

    c.execute("""DELETE FROM placement_drives WHERE id NOT IN (
        SELECT MAX(id) FROM placement_drives GROUP BY company, role)""")
    c.execute("""DELETE FROM announcements WHERE id NOT IN (
        SELECT MAX(id) FROM announcements GROUP BY title)""")

    for ann in [
        ("Pre-Placement Talk: Google","Google PPT on Feb 25th at 10 AM in Main Auditorium. Attendance mandatory for all final year CS/IT students.","high",1),
        ("Resume Submission Deadline","All students must upload updated resumes by March 1st. Format: PDF only, max 1 page.","normal",1),
        ("Mock Interview Drive","Department organizing mock interviews on Feb 28th. Register with your TPO coordinator.","normal",1),
    ]:
        exists = c.execute("SELECT id FROM announcements WHERE title=?", (ann[0],)).fetchone()
        if not exists:
            c.execute("INSERT INTO announcements (title,content,priority,posted_by) VALUES (?,?,?,?)", ann)

    conn.commit()
    conn.close()

def db_login(username, password):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE username=? AND password=?",
                       (username, hash_pw(password))).fetchone()
    conn.close()
    return dict(row) if row else None

def db_register(username, password, role, name):
    try:
        conn = get_conn()
        conn.execute("INSERT INTO users (username,password,role,name) VALUES (?,?,?,?)",
                     (username, hash_pw(password), role, name))
        conn.commit()
        conn.close()
        return True, "Account created!"
    except sqlite3.IntegrityError:
        return False, "Username already exists."

def db_save_profile(user_id, data, score):
    conn = get_conn()
    exists = conn.execute("SELECT id FROM student_profiles WHERE user_id=?", (user_id,)).fetchone()
    skills_str = ",".join(data["skills"])
    now = datetime.now().isoformat()
    if exists:
        conn.execute("""UPDATE student_profiles SET name=?,branch=?,year=?,target_role=?,skills=?,
            cgpa=?,internships=?,projects=?,certifications=?,backlogs=?,
            linkedin=?,github=?,readiness_score=?,updated_at=? WHERE user_id=?""",
            (data["name"],data["branch"],data["year"],data["target_role"],skills_str,
             data["cgpa"],data["internships"],data["projects"],data["certifications"],
             data["backlogs"],data.get("linkedin",""),data.get("github",""),score,now,user_id))
    else:
        conn.execute("""INSERT INTO student_profiles
            (user_id,name,branch,year,target_role,skills,cgpa,internships,projects,
             certifications,backlogs,linkedin,github,readiness_score,updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (user_id,data["name"],data["branch"],data["year"],data["target_role"],skills_str,
             data["cgpa"],data["internships"],data["projects"],data["certifications"],
             data["backlogs"],data.get("linkedin",""),data.get("github",""),score,now))
    conn.execute("INSERT INTO score_history (user_id,score,target_role) VALUES (?,?,?)",
                 (user_id, score, data["target_role"]))
    conn.commit()
    conn.close()

def db_get_profile(user_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM student_profiles WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    if row:
        d = dict(row)
        d["skills"] = d["skills"].split(",") if d["skills"] else []
        return d
    return None

def db_get_score_history(user_id):
    conn = get_conn()
    rows = conn.execute("SELECT score,target_role,recorded_at FROM score_history WHERE user_id=? ORDER BY recorded_at ASC", (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def db_get_all_students():
    conn = get_conn()
    rows = conn.execute("""SELECT u.id,u.username,u.name as user_name,sp.*
        FROM users u LEFT JOIN student_profiles sp ON u.id=sp.user_id
        WHERE u.role='student' ORDER BY sp.readiness_score DESC""").fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["skills"]         = d["skills"].split(",") if d.get("skills") else []
        d["name"]           = d.get("name") or d.get("user_name") or "—"
        d["branch"]         = d.get("branch") or None
        d["year"]           = d.get("year") or None
        d["target_role"]    = d.get("target_role") or None
        d["cgpa"]           = d.get("cgpa") or None
        d["internships"]    = d.get("internships") or 0
        d["projects"]       = d.get("projects") or 0
        d["certifications"] = d.get("certifications") or 0
        d["backlogs"]       = d.get("backlogs") or 0
        d["linkedin"]       = d.get("linkedin") or ""
        d["github"]         = d.get("github") or ""
        d["readiness_score"]= d.get("readiness_score") or 0
        result.append(d)
    return result

def db_get_drives(active_only=True):
    conn = get_conn()
    q = "SELECT * FROM placement_drives" + (" WHERE is_active=1" if active_only else "") + " ORDER BY posted_at DESC"
    rows = conn.execute(q).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["company"]          = d.get("company") or "—"
        d["role"]             = d.get("role") or "—"
        d["package"]          = d.get("package") or "TBD"
        d["drive_date"]       = d.get("drive_date") or "TBD"
        d["apply_link"]       = d.get("apply_link") or ""
        d["is_active"]        = d.get("is_active") if d.get("is_active") is not None else 1
        d["required_skills"]  = d.get("required_skills") or ""
        d["eligible_branches"]= d.get("eligible_branches") or ""
        d["description"]      = d.get("description") or ""
        d["eligibility_cgpa"] = d.get("eligibility_cgpa") or 0.0
        result.append(d)
    return result

def db_post_drive(data, posted_by):
    conn = get_conn()
    conn.execute("""INSERT INTO placement_drives
        (company,role,package,description,eligibility_cgpa,eligible_branches,
         required_skills,drive_date,apply_link,posted_by) VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (data["company"],data["role"],data["package"],data["description"],
         data["eligibility_cgpa"],",".join(data["eligible_branches"]),
         ",".join(data["required_skills"]),data["drive_date"],data["apply_link"],posted_by))
    conn.commit()
    conn.close()

def db_toggle_drive(drive_id, active):
    conn = get_conn()
    conn.execute("UPDATE placement_drives SET is_active=? WHERE id=?", (1 if active else 0, drive_id))
    conn.commit()
    conn.close()

def db_apply_drive(drive_id, user_id):
    conn = get_conn()
    exists = conn.execute("SELECT id FROM drive_applications WHERE drive_id=? AND user_id=?", (drive_id, user_id)).fetchone()
    if not exists:
        conn.execute("INSERT INTO drive_applications (drive_id,user_id) VALUES (?,?)", (drive_id, user_id))
        conn.commit()
    conn.close()

def db_get_my_apps(user_id):
    conn = get_conn()
    rows = conn.execute("""SELECT da.*,pd.company,pd.role,pd.package,pd.drive_date
        FROM drive_applications da JOIN placement_drives pd ON da.drive_id=pd.id
        WHERE da.user_id=?""", (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def db_get_drive_applicants(drive_id):
    conn = get_conn()
    rows = conn.execute("""SELECT da.*,u.name,u.username,sp.cgpa,sp.branch,sp.readiness_score,sp.skills
        FROM drive_applications da JOIN users u ON da.user_id=u.id
        LEFT JOIN student_profiles sp ON da.user_id=sp.user_id WHERE da.drive_id=?""", (drive_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def db_update_app_status(app_id, status):
    conn = get_conn()
    conn.execute("UPDATE drive_applications SET status=? WHERE id=?", (status, app_id))
    conn.commit()
    conn.close()

def db_get_announcements():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM announcements ORDER BY posted_at DESC LIMIT 20").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def db_post_announcement(title, content, priority, posted_by):
    conn = get_conn()
    conn.execute("INSERT INTO announcements (title,content,priority,posted_by) VALUES (?,?,?,?)",
                 (title, content, priority, posted_by))
    conn.commit()
    conn.close()

def db_delete_announcement(ann_id):
    conn = get_conn()
    conn.execute("DELETE FROM announcements WHERE id=?", (ann_id,))
    conn.commit()
    conn.close()

def db_get_recent_activity(limit=10):
    conn = get_conn()
    rows = conn.execute("""
        SELECT da.applied_at, da.status, u.name as student_name,
               pd.company, pd.role
        FROM drive_applications da
        JOIN users u ON da.user_id = u.id
        JOIN placement_drives pd ON da.drive_id = pd.id
        ORDER BY da.applied_at DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def db_get_monthly_trends():
    conn = get_conn()
    rows = conn.execute("""
        SELECT strftime('%Y-%m', applied_at) as month, COUNT(*) as applications,
               SUM(CASE WHEN status='Selected' THEN 1 ELSE 0 END) as selected
        FROM drive_applications
        GROUP BY month ORDER BY month ASC LIMIT 12
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def db_get_tpo_profile(user_id):
    try:
        conn = get_conn()
        row = conn.execute("SELECT * FROM tpo_profiles WHERE user_id=?", (user_id,)).fetchone()
        conn.close()
        return dict(row) if row else None
    except Exception:
        return None

def db_save_tpo_profile(user_id, data):
    conn = get_conn()
    conn.execute("""CREATE TABLE IF NOT EXISTS tpo_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        designation TEXT DEFAULT '',
        department TEXT DEFAULT '',
        college TEXT DEFAULT '',
        email TEXT DEFAULT '',
        phone TEXT DEFAULT '',
        updated_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(user_id) REFERENCES users(id))""")
    conn.commit()
    exists = conn.execute("SELECT id FROM tpo_profiles WHERE user_id=?", (user_id,)).fetchone()
    now = datetime.now().isoformat()
    if exists:
        conn.execute("""UPDATE tpo_profiles SET designation=?,department=?,college=?,
            email=?,phone=?,updated_at=? WHERE user_id=?""",
            (data["designation"],data["department"],data["college"],
             data["email"],data["phone"],now,user_id))
    else:
        conn.execute("""INSERT INTO tpo_profiles
            (user_id,designation,department,college,email,phone,updated_at)
            VALUES (?,?,?,?,?,?,?)""",
            (user_id,data["designation"],data["department"],data["college"],
             data["email"],data["phone"],now))
    conn.execute("UPDATE users SET name=? WHERE id=?", (data["name"], user_id))
    conn.commit()
    conn.close()

def db_change_password(user_id, old_pw, new_pw):
    conn = get_conn()
    row = conn.execute("SELECT id FROM users WHERE id=? AND password=?",
                       (user_id, hash_pw(old_pw))).fetchone()
    if not row:
        conn.close()
        return False, "Current password is incorrect."
    conn.execute("UPDATE users SET password=? WHERE id=?", (hash_pw(new_pw), user_id))
    conn.commit()
    conn.close()
    return True, "Password changed successfully!"

def render_error(e, page="this page"):
    import traceback
    tb = traceback.format_exc()
    st.markdown(f'''<div style="background:#2a1a1a;border:1px solid #f06292;border-radius:12px;
        padding:1.5rem;margin:1rem 0">
        <div style="color:#f06292;font-size:1.1rem;font-weight:700">⚠️ Something went wrong on {page}</div>
        <div style="color:#e8d5f5;margin-top:0.5rem;font-size:0.85rem">{str(e)}</div>
    </div>''', unsafe_allow_html=True)
    with st.expander("🔍 Error details (for debugging)"):
        st.code(tb)

# ══════════════════════════════════════════════════════════════════════════════
# MARKET DATA & STATIC DATASET
# ══════════════════════════════════════════════════════════════════════════════
MARKET_DATA = {
    "Data Analyst": {
        "required_skills": ["Python","SQL","Excel","PowerBI","Statistics","Tableau","Data Cleaning"],
        "avg_package": "6.5 LPA", "min_cgpa": 6.5,
        "top_companies": ["TCS","Infosys","Flipkart","Amazon","Deloitte"],
        "placement_rate": 78,
        "skill_weights": {"Python":92,"SQL":88,"PowerBI":80,"Excel":75,"Statistics":70,"Tableau":65,"Data Cleaning":60},
        "resources": {
            "PowerBI": ("Microsoft Learn – PowerBI","https://learn.microsoft.com/en-us/power-bi/"),
            "Tableau": ("Tableau Free Training","https://www.tableau.com/learn/training"),
            "Statistics": ("Khan Academy Statistics","https://www.khanacademy.org/math/statistics-probability"),
            "Data Cleaning": ("Kaggle – Data Cleaning Course","https://www.kaggle.com/learn/data-cleaning"),
            "Python": ("Python for Everybody – Coursera","https://www.coursera.org/specializations/python"),
            "SQL": ("Mode SQL Tutorial","https://mode.com/sql-tutorial/"),
        }
    },
    "Software Engineer": {
        "required_skills": ["Python","DSA","Java","Git","SQL","System Design","OS Concepts"],
        "avg_package": "9.2 LPA", "min_cgpa": 7.0,
        "top_companies": ["Google","Microsoft","Wipro","HCL","Zoho"],
        "placement_rate": 85,
        "skill_weights": {"DSA":95,"Python":88,"Java":82,"Git":75,"SQL":68,"System Design":65,"OS Concepts":60},
        "resources": {
            "DSA": ("Striver's DSA Sheet","https://takeuforward.org/strivers-a2z-dsa-course/"),
            "System Design": ("System Design Primer – GitHub","https://github.com/donnemartin/system-design-primer"),
            "OS Concepts": ("GATE Overflow OS Notes","https://gateoverflow.in/"),
            "Git": ("Learn Git Branching","https://learngitbranching.js.org/"),
            "Java": ("Java MOOC.fi","https://java-programming.mooc.fi/"),
            "SQL": ("SQLZoo","https://sqlzoo.net/"),
        }
    },
    "Marketing Analyst": {
        "required_skills": ["Excel","Google Analytics","SEO","PowerBI","Communication","SQL","Python"],
        "avg_package": "5.0 LPA", "min_cgpa": 6.0,
        "top_companies": ["HUL","P&G","Swiggy","Myntra","Zomato"],
        "placement_rate": 65,
        "skill_weights": {"Excel":90,"Google Analytics":85,"Communication":80,"SEO":72,"PowerBI":65,"SQL":58,"Python":50},
        "resources": {
            "Google Analytics": ("GA4 Skillshop (Free)","https://skillshop.google.com/"),
            "SEO": ("Moz Beginner's Guide to SEO","https://moz.com/beginners-guide-to-seo"),
            "Python": ("Python for Everybody – Coursera","https://www.coursera.org/specializations/python"),
            "SQL": ("Mode SQL Tutorial","https://mode.com/sql-tutorial/"),
        }
    },
    "UI/UX Designer": {
        "required_skills": ["Figma","User Research","Wireframing","Prototyping","CSS","Adobe XD","Usability Testing"],
        "avg_package": "5.8 LPA", "min_cgpa": 6.0,
        "top_companies": ["Swiggy","Razorpay","Dunzo","Freshworks","Zoho"],
        "placement_rate": 60,
        "skill_weights": {"Figma":95,"Prototyping":85,"User Research":78,"Wireframing":75,"Adobe XD":60,"CSS":55,"Usability Testing":52},
        "resources": {
            "Figma": ("Figma for Beginners – YouTube","https://www.youtube.com/c/Figma"),
            "User Research": ("Nielsen Norman Group Articles","https://www.nngroup.com/articles/"),
            "Usability Testing": ("UX Mastery","https://uxmastery.com/"),
            "Adobe XD": ("Adobe XD Tutorials","https://helpx.adobe.com/xd/tutorials.html"),
        }
    },
}

ALL_SKILLS   = sorted(set(s for rd in MARKET_DATA.values() for s in rd["required_skills"]))
ALL_BRANCHES = ["Computer Science","Information Technology","Electronics","Mechanical","Civil","MBA","BBA","Other"]

@st.cache_data
def load_dataset():
    data = [
        (1,'Aarav','Data Analyst','Python, Excel',7.8,1,7),
        (2,'Riya','Data Analyst','SQL, Excel',8.2,2,8),
        (3,'Krishna','Web Developer','HTML, CSS, JS',7.5,1,6),
        (4,'Ananya','Data Analyst','Python, SQL',8.5,2,9),
        (5,'Rohit','Software Engineer','Java, DSA',7.9,1,7),
        (6,'Sneha','Data Analyst','Excel, PowerBI',8.0,1,8),
        (7,'Arjun','Web Developer','HTML, CSS',7.2,0,6),
        (8,'Pooja','Data Analyst','Python, Excel, SQL',8.7,2,9),
        (9,'Karan','Software Engineer','Java, DBMS',7.6,1,7),
        (10,'Meena','Data Analyst','Excel',7.3,0,6),
        (11,'Rahul','Data Analyst','Python, PowerBI',8.1,1,8),
        (12,'Aisha','Web Developer','HTML, CSS, JS, React',8.4,2,9),
        (13,'Vikram','Software Engineer','C++, DSA',7.7,1,7),
        (14,'Neha','Data Analyst','SQL, Excel',8.3,2,8),
        (15,'Dev','Data Analyst','Python',7.4,0,6),
        (16,'Tanvi','Web Developer','HTML, CSS, JS',8.2,1,8),
        (17,'Aman','Software Engineer','Java, DSA, DBMS',8.0,2,8),
        (18,'Kavya','Data Analyst','Excel, PowerBI',7.9,1,7),
        (19,'Yash','Web Developer','HTML, CSS',7.1,0,6),
        (20,'Isha','Data Analyst','Python, SQL, Excel',8.6,2,9),
        (21,'Raj','Data Analyst','SQL',7.2,0,6),
        (22,'Simran','Web Developer','HTML, CSS, JS',8.3,2,8),
        (23,'Aditya','Software Engineer','Java, DSA',7.8,1,7),
        (24,'Nisha','Data Analyst','Python, Excel',8.4,2,9),
        (25,'Kunal','Data Analyst','Excel, PowerBI',7.5,1,7),
        (26,'Alok','Web Developer','HTML, CSS',7.0,0,6),
        (27,'Payal','Data Analyst','SQL, Python',8.5,2,9),
        (28,'Deepak','Software Engineer','C++, DBMS',7.6,1,7),
        (29,'Shruti','Data Analyst','Excel',7.3,0,6),
        (30,'Manish','Web Developer','HTML, CSS, JS',8.1,1,8),
        (31,'Priya','Data Analyst','Python, SQL, PowerBI',8.7,2,9),
        (32,'Sachin','Software Engineer','Java, DSA',7.9,1,7),
        (33,'Divya','Data Analyst','Excel, SQL',8.2,2,8),
        (34,'Nikhil','Web Developer','HTML, CSS',7.4,0,6),
        (35,'Ritika','Data Analyst','Python',7.6,1,7),
        (36,'Harsh','Software Engineer','C++, DSA',7.8,1,7),
        (37,'Swati','Data Analyst','Excel, PowerBI',8.3,2,8),
        (38,'Ramesh','Web Developer','HTML, CSS, JS',7.5,1,7),
        (39,'Kriti','Data Analyst','SQL, Excel',8.1,2,8),
        (40,'Suresh','Software Engineer','Java',7.2,0,6),
        (41,'Ankit','Data Analyst','Python, SQL',8.4,2,9),
        (42,'Pallavi','Web Developer','HTML, CSS, JS, React',8.5,2,9),
        (43,'Varun','Software Engineer','Java, DBMS',7.7,1,7),
        (44,'Geeta','Data Analyst','Excel',7.3,0,6),
        (45,'Ravi','Data Analyst','Python, Excel',8.2,2,8),
        (46,'Neeraj','Web Developer','HTML, CSS',7.1,0,6),
        (47,'Shreya','Data Analyst','SQL, PowerBI',8.6,2,9),
        (48,'Ashok','Software Engineer','C++, DSA',7.8,1,7),
        (49,'Komal','Data Analyst','Excel, SQL',8.0,1,8),
        (50,'Ayush','Web Developer','HTML, CSS, JS',7.6,1,7),
    ]
    df = pd.DataFrame(data, columns=['ID','Name','Role','Skills','CGPA','Internships','Communication'])
    df['Skills_List'] = df['Skills'].apply(lambda x: [s.strip() for s in x.split(',')])
    return df

STUDENT_DF = load_dataset()

# ══════════════════════════════════════════════════════════════════════════════
# ANALYTICS / SCORING FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def analyze(profile, role_data):
    required     = set(role_data["required_skills"])
    have         = required & set(profile["skills"])
    missing      = required - set(profile["skills"])
    skill_score  = int((len(have) / len(required)) * 70)
    cgpa         = profile.get("cgpa", 0)
    min_cgpa     = role_data.get("min_cgpa", 6.5)
    cgpa_score   = 10 if cgpa >= min_cgpa + 1 else 7 if cgpa >= min_cgpa else 4 if cgpa >= min_cgpa - 0.5 else 0
    intern_score = 10 if profile.get("internships", 0) >= 2 else 6 if profile.get("internships", 0) == 1 else 0
    proj_score   = 5  if profile.get("projects", 0) >= 3    else 3 if profile.get("projects", 0) >= 1    else 0
    cert_score   = 5  if profile.get("certifications", 0) >= 3 else 3 if profile.get("certifications", 0) >= 1 else 0
    penalty      = min(profile.get("backlogs", 0) * 5, 15)
    total        = max(0, min(100, skill_score + cgpa_score + intern_score + proj_score + cert_score - penalty))
    return have, missing, total, {
        "Skills": skill_score, "CGPA": cgpa_score, "Internships": intern_score,
        "Projects": proj_score, "Certifications": cert_score, "Backlog Penalty": -penalty
    }

def get_peer_stats(role, user_cgpa):
    peers = STUDENT_DF[STUDENT_DF['Role'] == role]
    if peers.empty:
        return None
    all_skills = []
    for s in peers['Skills_List']:
        all_skills.extend(s)
    top_skills = [s for s, _ in Counter(all_skills).most_common(5)]
    total      = len(peers)
    above      = len(peers[peers['CGPA'] > user_cgpa])
    return {
        "avg_cgpa":    round(peers['CGPA'].mean(), 2),
        "avg_interns": round(peers['Internships'].mean(), 1),
        "top_skills":  top_skills,
        "total_peers": total,
        "percentile":  round(((total - above) / total) * 100),
    }

def placement_probability(score, missing, role_data):
    curr        = min(95, int(score * 0.9 + 5))
    top_missing = sorted(missing, key=lambda s: role_data["skill_weights"].get(s, 0), reverse=True)
    after1      = min(95, curr + 15) if top_missing else curr
    after2      = min(95, curr + 28) if len(top_missing) >= 2 else after1
    after_full  = min(95, curr + 45) if missing else curr
    return curr, after1, after2, after_full, top_missing

def generate_study_plan(top_missing, role_data, internships, projects, certifications):
    plan      = {"30": [], "60": [], "90": []}
    resources = role_data.get("resources", {})
    if top_missing:
        s1 = top_missing[0]
        r1 = resources.get(s1)
        l1 = f" → [{r1[0]}]({r1[1]})" if r1 else " → Search YouTube/Coursera"
        plan["30"].append(f"📚 Learn **{s1}** (Market demand: {role_data['skill_weights'].get(s1, 50)}%){l1}")
        plan["30"].append(f"🛠️ Build 1 small project using **{s1}**")
    if len(top_missing) >= 2:
        s2 = top_missing[1]
        r2 = resources.get(s2)
        l2 = f" → [{r2[0]}]({r2[1]})" if r2 else " → Search YouTube/Coursera"
        plan["60"].append(f"📚 Learn **{s2}** (Market demand: {role_data['skill_weights'].get(s2, 50)}%){l2}")
        plan["60"].append(f"🛠️ Combine **{top_missing[0]}** + **{s2}** into 1 complete project")
    else:
        plan["60"].append("🛠️ Improve existing projects — add docs and deploy online")
    if projects == 0:
        plan["60"].append("💡 Complete at least 2 projects for your portfolio")
    if certifications == 0:
        plan["90"].append(f"📜 Get certified in **{top_missing[0] if top_missing else role_data['required_skills'][0]}** (Coursera/NPTEL – Free!)")
    if internships == 0:
        plan["90"].append("💼 Apply for internships on LinkedIn, Internshala, Naukri")
    plan["90"].append("🎯 Start applying to companies — you will be ready!")
    plan["90"].append(f"🏢 Target: {', '.join(role_data['top_companies'][:3])}")
    return plan

def get_batch_analytics():
    total = len(STUDENT_DF)
    return {
        "total":       total,
        "role_counts": STUDENT_DF['Role'].value_counts().to_dict(),
        "avg_cgpa":    round(STUDENT_DF['CGPA'].mean(), 2),
        "avg_interns": round(STUDENT_DF['Internships'].mean(), 1),
        "high_cgpa":   len(STUDENT_DF[STUDENT_DF['CGPA'] >= 8.0]),
        "low_cgpa":    len(STUDENT_DF[STUDENT_DF['CGPA'] < 7.0]),
        "with_intern": len(STUDENT_DF[STUDENT_DF['Internships'] >= 1]),
        "no_intern":   len(STUDENT_DF[STUDENT_DF['Internships'] == 0]),
    }

def compare_with_all(profile, score):
    role         = profile["target_role"]
    peers        = STUDENT_DF[STUDENT_DF['Role'] == role].copy()
    total        = len(peers)
    better       = len(peers[peers['CGPA'] > profile['cgpa']])
    rank         = better + 1
    pct          = round(((total - better) / total) * 100)
    peers_sorted = peers.sort_values('CGPA', ascending=False).reset_index(drop=True)
    peers_sorted['Rank'] = peers_sorted.index + 1
    user_row = {
        'Rank': rank, 'Name': f"⭐ {profile['name']} (You)", 'CGPA': profile['cgpa'],
        'Internships': profile['internships'], 'Skills': ", ".join(profile['skills']), 'Role': role
    }
    result_df = pd.concat([
        pd.DataFrame([user_row]),
        peers_sorted[['Rank','Name','CGPA','Internships','Skills','Role']]
    ]).sort_values('CGPA', ascending=False).reset_index(drop=True)
    result_df['Rank'] = result_df.index + 1
    return result_df, rank, total, pct

def get_readiness_tier(score):
    if score >= 75: return "🟢 Placement Ready", "#e91e8c"
    if score >= 50: return "🟡 Almost There", "#f48fb1"
    if score >= 25: return "🟠 Needs Work", "#ce93d8"
    return "🔴 Early Stage", "#f06292"

def score_color(score):
    if score >= 75: return "#e91e8c"
    if score >= 50: return "#f48fb1"
    if score >= 25: return "#ce93d8"
    return "#f06292"

# ══════════════════════════════════════════════════════════════════════════════
# CHART HELPERS
# ══════════════════════════════════════════════════════════════════════════════
BG = "rgba(0,0,0,0)"

def render_gauge(score):
    color = "#e91e8c" if score >= 70 else "#f48fb1" if score >= 40 else "#f06292"
    fig   = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        number={"suffix": "%", "font": {"size": 36, "color": color}},
        gauge={
            "axis": {"range": [0, 100]}, "bar": {"color": color, "thickness": 0.3},
            "bgcolor": "#232131", "bordercolor": "#3d2f5a",
            "steps": [{"range": [0,40], "color":"#1f1228"}, {"range":[40,70],"color":"#2a1a35"}, {"range":[70,100],"color":"#2a1540"}],
            "threshold": {"line": {"color": color, "width": 4}, "thickness": 0.75, "value": score}
        }
    ))
    fig.update_layout(height=220, margin=dict(t=20,b=10,l=20,r=20), paper_bgcolor=BG, font_color="#e8d5f5")
    return fig

def render_breakdown(breakdown):
    values = list(breakdown.values())
    fig    = go.Figure(go.Bar(
        x=values, y=list(breakdown.keys()), orientation='h',
        marker_color=["#f06292" if v < 0 else "#e91e8c" if v >= 7 else "#f48fb1" for v in values],
        text=[f"{'+' if v >= 0 else ''}{v} pts" for v in values],
        textposition="outside", textfont=dict(color="#e8d5f5", size=11)
    ))
    fig.update_layout(height=280, margin=dict(t=10,b=10,l=10,r=80),
        paper_bgcolor=BG, plot_bgcolor=BG,
        xaxis=dict(showgrid=False, color="#3d2f5a", range=[-20, 80]),
        yaxis=dict(color="#e8d5f5", tickfont=dict(family="JetBrains Mono", size=11)), showlegend=False)
    return fig

def render_skill_demand(role_data, have):
    weights = role_data["skill_weights"]
    fig = go.Figure(go.Bar(
        x=list(weights.values()), y=list(weights.keys()), orientation='h',
        marker_color=["#e91e8c" if s in have else "#f06292" for s in weights.keys()],
        text=[f"{v}% of placed students" for v in weights.values()],
        textposition="outside", textfont=dict(color="#9d87b8", size=10)
    ))
    fig.update_layout(height=260, margin=dict(t=10,b=10,l=10,r=160),
        paper_bgcolor=BG, plot_bgcolor=BG,
        xaxis=dict(showgrid=False, color="#3d2f5a", range=[0, 130]),
        yaxis=dict(color="#e8d5f5", tickfont=dict(family="JetBrains Mono")), showlegend=False)
    return fig

def render_score_history(history):
    dates  = [h["recorded_at"][:10] for h in history]
    scores = [h["score"] for h in history]
    fig    = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=scores, mode='lines+markers',
        line=dict(color="#c482d5", width=2), marker=dict(color="#b388f4", size=8),
        fill='tozeroy', fillcolor='rgba(196,130,213,0.1)'))
    fig.update_layout(height=200, margin=dict(t=10,b=30,l=40,r=20),
        paper_bgcolor=BG, plot_bgcolor=BG,
        xaxis=dict(showgrid=False, color="#7a6e8a", tickfont=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor="#2d2545", color="#7a6e8a", range=[0, 100]), showlegend=False)
    return fig

def render_tpo_charts(students):
    profiled = [s for s in students if s.get("readiness_score") is not None]
    if not profiled:
        return None, None, None
    buckets = {"75+ Ready": 0, "50–74 Almost": 0, "25–49 Needs Work": 0, "<25 Early": 0}
    branch_scores, role_counts = {}, {}
    for s in profiled:
        sc = s.get("readiness_score", 0) or 0
        if sc >= 75:   buckets["75+ Ready"] += 1
        elif sc >= 50: buckets["50–74 Almost"] += 1
        elif sc >= 25: buckets["25–49 Needs Work"] += 1
        else:          buckets["<25 Early"] += 1
        b = s.get("branch", "?") or "?"
        branch_scores.setdefault(b, []).append(sc)
        r = s.get("target_role", "?") or "?"
        role_counts[r] = role_counts.get(r, 0) + 1
    fig_pie = go.Figure(go.Pie(
        labels=list(buckets.keys()), values=list(buckets.values()),
        marker_colors=["#e91e8c","#f48fb1","#ce93d8","#f06292"], hole=0.5,
        textfont=dict(size=11, color="#e8d5f5")))
    fig_pie.update_layout(height=280, paper_bgcolor=BG, margin=dict(t=10,b=10,l=10,r=10),
        legend=dict(font=dict(color="#9d87b8", size=10)))
    branch_avg = {b: int(sum(v)/len(v)) for b, v in branch_scores.items()}
    fig_branch = go.Figure(go.Bar(
        x=list(branch_avg.values()), y=list(branch_avg.keys()), orientation='h',
        marker_color=["#e91e8c" if v >= 70 else "#f48fb1" if v >= 40 else "#f06292" for v in branch_avg.values()],
        text=[f"{v}%" for v in branch_avg.values()],
        textposition="outside", textfont=dict(color="#9d87b8", size=11)))
    fig_branch.update_layout(height=max(200, len(branch_avg)*45), margin=dict(t=10,b=10,l=10,r=60),
        paper_bgcolor=BG, plot_bgcolor=BG,
        xaxis=dict(showgrid=False, range=[0, 120]), yaxis=dict(color="#e8d5f5"), showlegend=False)
    fig_role = go.Figure(go.Bar(
        x=list(role_counts.values()), y=list(role_counts.keys()), orientation='h',
        marker_color="#c482d5", text=list(role_counts.values()),
        textposition="outside", textfont=dict(color="#9d87b8", size=11)))
    fig_role.update_layout(height=max(200, len(role_counts)*50), margin=dict(t=10,b=10,l=10,r=60),
        paper_bgcolor=BG, plot_bgcolor=BG,
        xaxis=dict(showgrid=False), yaxis=dict(color="#e8d5f5"), showlegend=False)
    return fig_pie, fig_branch, fig_role

def get_common_missing(students):
    counter = Counter()
    for s in students:
        role = s.get("target_role")
        if not role or role not in MARKET_DATA:
            continue
        user_skills = set(s.get("skills", []))
        for req in MARKET_DATA[role]["required_skills"]:
            if req not in user_skills:
                counter[req] += 1
    return counter.most_common(10)

# ══════════════════════════════════════════════════════════════════════════════
# REAL-TIME TECH NEWS
# ══════════════════════════════════════════════════════════════════════════════
TECH_RSS_FEEDS = [
    ("TechCrunch",      "https://techcrunch.com/feed/",                "🔵"),
    ("The Verge",       "https://www.theverge.com/rss/index.xml",      "🟣"),
    ("Hacker News",     "https://hnrss.org/frontpage",                 "🟠"),
    ("MIT Tech Review", "https://www.technologyreview.com/feed/",      "🔴"),
    ("Wired",           "https://www.wired.com/feed/rss",              "🟡"),
    ("VentureBeat",     "https://venturebeat.com/feed/",               "🟢"),
]

RELEVANT_KEYWORDS = [
    "ai","artificial intelligence","machine learning","data","python","software",
    "startup","tech","hiring","jobs","career","coding","developer","engineer",
    "cloud","cybersecurity","blockchain","automation","openai","google","microsoft",
    "amazon","meta","layoff","funding","skills","programming","analytics"
]

@st.cache_data(ttl=3600)
def fetch_tech_news(max_per_feed=3):
    import re as _re
    all_articles = []
    headers = {"User-Agent": "Mozilla/5.0 (compatible; CampusEdge/1.0)"}
    for source_name, rss_url, emoji in TECH_RSS_FEEDS:
        try:
            req = urllib.request.Request(rss_url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as resp:
                raw = resp.read()
            root  = ET.fromstring(raw)
            ns    = {"atom": "http://www.w3.org/2005/Atom"}
            items = root.findall(".//item")
            if not items:
                items = root.findall(".//atom:entry", ns)
            count = 0
            for item in items:
                if count >= max_per_feed:
                    break
                title_el = item.find("title")
                title    = title_el.text if title_el is not None else ""
                if not title:
                    continue
                if not any(kw in title.lower() for kw in RELEVANT_KEYWORDS):
                    continue
                link_el = item.find("link")
                if link_el is None:
                    link_el = item.find("{http://www.w3.org/2005/Atom}link")
                link = ""
                if link_el is not None:
                    link = link_el.text or link_el.get("href", "")
                desc_el  = item.find("description") or item.find("{http://www.w3.org/2005/Atom}summary")
                desc     = ""
                if desc_el is not None and desc_el.text:
                    desc = _re.sub(r"<[^>]+>", "", desc_el.text or "")
                    desc = desc[:180].strip() + "..." if len(desc) > 180 else desc.strip()
                pub_el   = item.find("pubDate") or item.find("{http://www.w3.org/2005/Atom}updated")
                pub_date = ""
                if pub_el is not None and pub_el.text:
                    try:
                        from email.utils import parsedate_to_datetime
                        dt       = parsedate_to_datetime(pub_el.text)
                        pub_date = dt.strftime("%d %b %Y, %I:%M %p")
                    except Exception:
                        pub_date = pub_el.text[:16] if pub_el.text else ""
                all_articles.append({
                    "source": source_name, "emoji": emoji,
                    "title": title.strip(), "link": link.strip(),
                    "desc": desc, "date": pub_date,
                })
                count += 1
        except Exception:
            continue
    return all_articles[:20]

def render_news_card(article):
    link_html = (f'<a href="{article["link"]}" target="_blank" '
                 f'style="color:#e91e8c;font-size:0.82rem;text-decoration:none">🔗 Read Full Article →</a>'
                 if article["link"] else "")
    return f'''<div style="background:#232131;border:1px solid #3d2f5a;border-radius:12px;
                padding:1rem 1.4rem;margin-bottom:0.8rem;border-left:3px solid #e91e8c;">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.4rem">
            <span style="background:#1e1a2e;color:#c9a8f0;font-size:0.72rem;padding:2px 10px;border-radius:20px;border:1px solid #3d2f5a">
                {article["emoji"]} {article["source"]}
            </span>
            <span style="color:#4a3a60;font-size:0.72rem">{article["date"]}</span>
        </div>
        <div style="font-weight:700;color:#e8d5f5;font-size:0.95rem;margin-bottom:0.4rem;line-height:1.4">{article["title"]}</div>
        <div style="color:#7a6e8a;font-size:0.82rem;margin-bottom:0.6rem;line-height:1.5">{article["desc"]}</div>
        {link_html}
    </div>'''

# ══════════════════════════════════════════════════════════════════════════════
# UI HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def metric_box(val, label, color="#b388f4"):
    return (f'<div class="metric-box"><div class="metric-val" style="color:{color}">{val}</div>'
            f'<div class="metric-label">{label}</div></div>')

def ann_html(a):
    cls  = f"ann-{a.get('priority', 'normal')}"
    time = a["posted_at"][:16] if a.get("posted_at") else ""
    return (f'<div class="ann-card {cls}"><div class="ann-title">{a["title"]}</div>'
            f'<div class="ann-body">{a.get("content","")}</div>'
            f'<div class="ann-time">🕐 {time}</div></div>')

def prog_bar(pct, color="#c482d5"):
    return (f'<div class="prog-wrap"><div class="prog-fill" '
            f'style="width:{min(pct,100)}%;background:{color}"></div></div>')

def chip(text, kind="gray"):
    return f'<span class="chip chip-{kind}">{text}</span>'

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INIT
# ══════════════════════════════════════════════════════════════════════════════
init_db()

for k, v in [
    ("page", "login"), ("profile", {}), ("user", None),
    ("student_page", "dashboard"), ("tpo_page", "overview"),
    ("show_reg", False), ("chat_history", []),
    ("fchat_open", False), ("fchat_messages", []),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Persist login across reloads ─────────────────────────────────────────────
SESSION_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".campusedge_session")

def save_session(user_id):
    try:
        with open(SESSION_FILE, "w") as f:
            f.write(str(user_id))
    except Exception:
        pass

def load_session():
    try:
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, "r") as f:
                uid = int(f.read().strip())
            conn = get_conn()
            row  = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
            conn.close()
            return dict(row) if row else None
    except Exception:
        pass
    return None

def clear_session():
    try:
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
    except Exception:
        pass

# Restore session on reload
if st.session_state.user is None:
    restored = load_session()
    if restored:
        st.session_state.user = restored

user = st.session_state.user

# ══════════════════════════════════════════════════════════════════════════════
# LOGIN / REGISTER PAGE
# ══════════════════════════════════════════════════════════════════════════════
if handle_google_auth():
    st.rerun()

if not user:
    st.markdown('''
    <div style="max-width:440px;margin:3rem auto 1.5rem auto;background:linear-gradient(135deg,#2a2040,#1e1a2e);border:1px solid #3d2f5a;border-radius:20px;padding:2rem 2.5rem;text-align:center;">
      <div style="font-size:2.4rem;font-weight:800;background:linear-gradient(135deg,#b388f4,#c482d5);-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:-0.5px;">🎯 CampusEdge</div>
      <div style="color:#9d87b8;font-size:0.9rem;margin-top:0.4rem;">College Placement Intelligence Platform</div>
    </div>
    ''', unsafe_allow_html=True)


    if not st.session_state.show_reg:
        st.subheader("Sign In")
        uname = st.text_input("Username")
        pwd   = st.text_input("Password", type="password")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔐 Login", use_container_width=True, type="primary"):
                u = db_login(uname, pwd)
                if u:
                    st.session_state.user = u
                    st.session_state.student_page = "dashboard"
                    save_session(u["id"])
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
        with c2:
            if st.button("📝 Register", use_container_width=True):
                st.session_state.show_reg = True
                st.rerun()
        st.markdown("""<div class="demo-creds">
            <strong>Demo accounts:</strong><br>
            👨‍💼 TPO &nbsp;&nbsp;: <code>tpo_admin</code> / <code>tpo123</code><br>
            🎓 Student: <code>student_demo</code> / <code>student123</code>
        </div>""", unsafe_allow_html=True)
        st.markdown('<div style="margin:1.2rem 0;text-align:center;color:#4a3a60">─── or ───</div>', unsafe_allow_html=True)
        google_login_button("🔵 Continue with Google", role_hint="student")
    else:
        st.subheader("Create Account")
        name  = st.text_input("Full Name")
        uname = st.text_input("Username")
        pwd   = st.text_input("Password", type="password")
        role  = st.selectbox("Account Type", ["student","tpo"],
                             format_func=lambda x: "🎓 Student" if x == "student" else "👨‍💼 TPO / Placement Officer")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Create Account", use_container_width=True, type="primary"):
                if not all([name, uname, pwd]):
                    st.warning("All fields required.")
                elif len(pwd) < 6:
                    st.warning("Password must be at least 6 characters.")
                else:
                    ok, msg = db_register(uname, pwd, role, name)
                    if ok:
                        st.success(msg + " Please login.")
                        st.session_state.show_reg = False
                        st.rerun()
                    else:
                        st.error(msg)
        with c2:
            if st.button("← Back to Login", use_container_width=True):
                st.session_state.show_reg = False
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    display_name = user.get("name", user["username"]) or user["username"]
    username     = user["username"]
    role_label   = "Training & Placement Officer" if user["role"] == "tpo" else "Student"
    initials_url = f"https://ui-avatars.com/api/?name={display_name.replace(' ', '+')}&background=c482d5&color=fff&size=128&bold=true&rounded=true"
    st.markdown(f'''
    <div style="text-align:center;padding:1.2rem 0 0.8rem">
        <img src="{initials_url}" width="80" height="80"
             style="border-radius:50%;border:3px solid #c482d5;
                    box-shadow:0 0 18px rgba(196,130,213,0.4);margin-bottom:0.7rem"/>
        <div style="font-size:1rem;font-weight:700;color:#e8d5f5;margin-bottom:0.2rem">{display_name}</div>
        <div style="font-size:0.78rem;color:#7a6e8a;margin-bottom:0.3rem">@{username}</div>
        <div style="display:inline-block;background:#2a2040;color:#c9a8f0;font-size:0.68rem;
                    padding:2px 10px;border-radius:20px;border:1px solid #3d2f5a;
                    letter-spacing:0.08em;text-transform:uppercase">{role_label}</div>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown("---")

    if user["role"] == "student":
        pages = {
            "dashboard":     "📊  Dashboard",
            "profile":       "✏️  Edit Profile",
            "drives":        "🏢  Placement Drives",
            "applications":  "📋  My Applications",
            "peers":         "🏆  Peer Leaderboard",
            "announcements": "📢  Announcements",
            "chatbot":       "🤖  AI Career Assistant",
        }
        for k, label in pages.items():
            active = st.session_state.student_page == k
            if st.button(label, key=f"snav_{k}", use_container_width=True,
                         type="primary" if active else "secondary"):
                st.session_state.student_page = k
                st.rerun()
    else:
        pages = {
            "overview":     "📊  Overview",
            "students":     "👥  All Students",
            "drives":       "🏢  Manage Drives",
            "announcements":"📢  Announcements",
            "skill_gaps":   "🔍  Skill Gap Report",
            "exports":      "📥  Export Data",
            "tpo_profile":  "👤  My Profile",
        }
        for k, label in pages.items():
            active = st.session_state.tpo_page == k
            if st.button(label, key=f"tnav_{k}", use_container_width=True,
                         type="primary" if active else "secondary"):
                st.session_state.tpo_page = k
                st.rerun()

    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
        st.session_state.user      = None
        st.session_state.show_reg  = False
        st.session_state.fchat_open     = False
        st.session_state.fchat_messages = []
        st.session_state.chat_history   = []
        clear_session()
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# MAIN PAGE ROUTING
# ══════════════════════════════════════════════════════════════════════════════
try:
    # ── STUDENT: DASHBOARD ────────────────────────────────────────────────────
    if user["role"] == "student" and st.session_state.student_page == "dashboard":
        profile_db = db_get_profile(user["id"])
        st.markdown('<div class="hero-title">📊 My Dashboard</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="hero-sub">Welcome back, <strong>{user.get("name","")}</strong></div>', unsafe_allow_html=True)

        if not profile_db:
            st.info("👋 You haven't set up your profile yet. Go to **Edit Profile** to get your readiness score!")
            if st.button("→ Set Up Profile Now", type="primary"):
                st.session_state.student_page = "profile"
                st.rerun()
            st.stop()

        p         = profile_db
        role_data = MARKET_DATA[p["target_role"]]
        have, missing, score, breakdown = analyze(p, role_data)
        peer_stats  = get_peer_stats(p["target_role"], p["cgpa"])
        top_missing = sorted(missing, key=lambda s: role_data["skill_weights"].get(s, 0), reverse=True)
        curr_prob, after1, after2, after_full, _ = placement_probability(score, missing, role_data)
        study_plan  = generate_study_plan(top_missing, role_data, p["internships"], p["projects"], p["certifications"])
        batch       = get_batch_analytics()
        compare_df, user_rank, total_peers, user_pct = compare_with_all(p, score)

        if score >= 70:
            st.balloons()

        badges = [
            f"🎓 CGPA: {p['cgpa']}", f"💼 Internships: {p['internships']}",
            f"🛠️ Projects: {p['projects']}", f"📜 Certifications: {p['certifications']}",
            f"⚠️ Backlogs: {p['backlogs']}",
        ]
        if p.get("linkedin"): badges.append("🔗 LinkedIn")
        if p.get("github"):   badges.append("🐙 GitHub")
        st.markdown(" ".join([f'<span class="profile-badge">{b}</span>' for b in badges]), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        if top_missing:
            top_skill  = top_missing[0]
            top_demand = role_data["skill_weights"][top_skill]
            st.markdown(f'''<div class="intel-box">
                <div style="color:#c9a8f0;font-size:0.85rem;font-weight:600;margin-bottom:0.5rem">🧠 MARKET INTELLIGENCE INSIGHT</div>
                <div style="color:#e8d5f5;font-size:1.05rem">You are targeting <strong>{p["target_role"]}</strong> roles.
                <strong>{top_demand}%</strong> of placed students had <strong>{top_skill}</strong> — but you do not.</div>
                <div style="color:#7a6e8a;font-size:0.85rem;margin-top:0.5rem">⚡ Recommended Action: Learn <strong>{top_skill}</strong> immediately.</div>
            </div>''', unsafe_allow_html=True)
        else:
            st.markdown(f'''<div class="intel-box">
                <div style="color:#c9a8f0;font-size:0.85rem;font-weight:600;margin-bottom:0.5rem">🧠 MARKET INTELLIGENCE INSIGHT</div>
                <div style="color:#e91e8c;font-size:1.05rem">✅ You have all required skills for <strong>{p["target_role"]}</strong>! Focus on projects and interview prep.</div>
            </div>''', unsafe_allow_html=True)

        for col, (val, label) in zip(st.columns(5), [
            (f"{score}%", "Overall Readiness"),
            (f"{len(have)}/{len(role_data['required_skills'])}", "Skills Matched"),
            (role_data["avg_package"], "Avg Package"),
            (f"{role_data['placement_rate']}%", "Placement Rate"),
            (f"{role_data['min_cgpa']}+", "Min CGPA Required"),
        ]):
            col.markdown(metric_box(val, label), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        cg, cb = st.columns([1, 1.5])
        with cg:
            st.markdown('<div class="section-header">Readiness Gauge</div>', unsafe_allow_html=True)
            st.plotly_chart(render_gauge(score), use_container_width=True)
            tier, tc = get_readiness_tier(score)
            st.markdown(f"<center style='color:{tc}'>{tier}</center>", unsafe_allow_html=True)
        with cb:
            st.markdown('<div class="section-header">Score Breakdown</div>', unsafe_allow_html=True)
            st.plotly_chart(render_breakdown(breakdown), use_container_width=True)

        history = db_get_score_history(user["id"])
        if len(history) > 1:
            st.markdown('<div class="section-header">📅 Progress Over Time</div>', unsafe_allow_html=True)
            st.plotly_chart(render_score_history(history), use_container_width=True)
            delta = history[-1]["score"] - history[0]["score"]
            if delta > 0:
                st.success(f"🚀 You've improved by **{delta} points** since your first assessment!")

        st.markdown('<div class="section-header">🏆 Placement Probability Score</div>', unsafe_allow_html=True)
        for col, (val, label, col_c) in zip(st.columns(4), [
            (f"{curr_prob}%", "Current Probability", "#f06292"),
            (f"{after1}%",    f"After Learning {top_missing[0] if top_missing else 'Top Skill'}", "#f48fb1"),
            (f"{after2}%",    "After 2 More Skills", "#f48fb1"),
            (f"{after_full}%","After All Skills Learned", "#e91e8c"),
        ]):
            col.markdown(metric_box(val, label, col_c), unsafe_allow_html=True)

        fig_prob = go.Figure(go.Bar(
            x=["Current", f"+ {top_missing[0] if top_missing else 'Skill'}", "+ 2 Skills", "All Skills"],
            y=[curr_prob, after1, after2, after_full],
            marker_color=["#f06292","#f48fb1","#f48fb1","#e91e8c"],
            text=[f"{v}%" for v in [curr_prob, after1, after2, after_full]],
            textposition="outside", textfont=dict(color="#e8d5f5", size=12)
        ))
        fig_prob.update_layout(height=260, margin=dict(t=20,b=10,l=10,r=10),
            paper_bgcolor=BG, plot_bgcolor=BG,
            xaxis=dict(showgrid=False, color="#e8d5f5"),
            yaxis=dict(showgrid=False, color="#e8d5f5", range=[0, 110]), showlegend=False)
        st.plotly_chart(fig_prob, use_container_width=True)

        st.markdown('<div class="section-header">📅 Your 30-60-90 Day Study Plan</div>', unsafe_allow_html=True)
        d1, d2, d3 = st.columns(3)
        with d1:
            st.markdown('<div style="background:#1e1a2e;border:1px solid #3d2f5a;border-radius:12px;padding:1rem 1.2rem">', unsafe_allow_html=True)
            st.markdown("**📅 NEXT 30 DAYS**")
            for item in study_plan["30"]: st.markdown(item)
            st.markdown('</div>', unsafe_allow_html=True)
        with d2:
            st.markdown('<div style="background:#231a35;border:1px solid #4a2060;border-radius:12px;padding:1rem 1.2rem">', unsafe_allow_html=True)
            st.markdown("**📅 NEXT 60 DAYS**")
            for item in study_plan["60"]: st.markdown(item)
            st.markdown('</div>', unsafe_allow_html=True)
        with d3:
            st.markdown('<div style="background:#1e1a2e;border:1px solid #3d2f5a;border-radius:12px;padding:1rem 1.2rem">', unsafe_allow_html=True)
            st.markdown("**📅 NEXT 90 DAYS**")
            for item in study_plan["90"]: st.markdown(item)
            st.markdown('</div>', unsafe_allow_html=True)

        if peer_stats:
            st.markdown('<div class="section-header">👥 Peer Benchmarking (Real Student Data)</div>', unsafe_allow_html=True)
            for col, (val, label) in zip(st.columns(4), [
                (peer_stats["total_peers"],         "Peers in Dataset"),
                (peer_stats["avg_cgpa"],            "Avg Peer CGPA"),
                (peer_stats["avg_interns"],         "Avg Internships"),
                (f"{peer_stats['percentile']}%",    "Your CGPA Percentile"),
            ]):
                col.markdown(metric_box(val, label), unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            peers_df = STUDENT_DF[STUDENT_DF['Role'] == p["target_role"]]
            fig_peer = go.Figure()
            fig_peer.add_trace(go.Bar(x=peers_df['Name'], y=peers_df['CGPA'], marker_color="#c482d5", opacity=0.7))
            fig_peer.add_hline(y=p["cgpa"], line_color="#b388f4", line_width=2,
                               annotation_text=f"  You ({p['cgpa']})", annotation_font_color="#b388f4")
            fig_peer.update_layout(title=dict(text="Your CGPA vs All Peers", font=dict(color="#e8d5f5")),
                height=280, margin=dict(t=40,b=10,l=10,r=10),
                paper_bgcolor=BG, plot_bgcolor=BG,
                xaxis=dict(showgrid=False, color="#3d2f5a", tickfont=dict(size=9)),
                yaxis=dict(color="#e8d5f5", range=[6, 10]), showlegend=False)
            st.plotly_chart(fig_peer, use_container_width=True)
            cgpa_dir = "above" if p["cgpa"] >= peer_stats["avg_cgpa"] else "below"
            st.markdown(f'<div class="peer-card">🔥 <strong>Top skills among your peers:</strong> {", ".join(peer_stats["top_skills"])}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="peer-card">📊 Your CGPA <strong>{p["cgpa"]}</strong> is <strong>{cgpa_dir}</strong> the peer avg of <strong>{peer_stats["avg_cgpa"]}</strong>. Ranked <strong>#{user_rank}</strong> of <strong>{total_peers}</strong> — <strong>{user_pct}th percentile.</strong></div>', unsafe_allow_html=True)

        st.markdown(f'<div class="section-header">🆚 Your Ranking Among All {p["target_role"]} Students</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="peer-card">⭐ Ranked <strong>#{user_rank}</strong> out of <strong>{total_peers}</strong> students — <strong>{user_pct}th percentile</strong></div>', unsafe_allow_html=True)
        st.dataframe(compare_df[['Rank','Name','CGPA','Internships','Skills']], use_container_width=True, hide_index=True)

        st.markdown('<div class="section-header">📈 Skill Demand in Market</div>', unsafe_allow_html=True)
        st.plotly_chart(render_skill_demand(role_data, have), use_container_width=True)

        ch, cm = st.columns(2)
        with ch:
            st.markdown('<div class="section-header">✅ Skills You Have</div>', unsafe_allow_html=True)
            st.markdown(" ".join([f'<span class="skill-chip-have">✓ {s}</span>' for s in sorted(have)]) or "<span style='color:#9d87b8'>None matched yet</span>", unsafe_allow_html=True)
        with cm:
            st.markdown("<div class='section-header'>⚠️ Skills You're Missing</div>", unsafe_allow_html=True)
            st.markdown(" ".join([f'<span class="skill-chip-missing">✗ {s}</span>' for s in sorted(missing)]) or "<span style='color:#e91e8c'>All skills matched! 🎉</span>", unsafe_allow_html=True)

        st.markdown('<div class="section-header">💡 Profile Insights</div>', unsafe_allow_html=True)
        for condition, good, bad in [
            (p["cgpa"] >= role_data["min_cgpa"],
             f'🎓 <strong>CGPA {p["cgpa"]}</strong> meets the minimum {role_data["min_cgpa"]} requirement!',
             f'🎓 <strong>CGPA {p["cgpa"]}</strong> is below {role_data["min_cgpa"]}. Focus on academics.'),
            (p["internships"] >= 1,
             f'💼 <strong>{p["internships"]} Internship(s)</strong> — Great boost!',
             '💼 <strong>No internships</strong> — Get at least 1 before placements.'),
            (p["projects"] >= 1,
             f'🛠️ <strong>{p["projects"]} Project(s)</strong> — Put them on GitHub!',
             '🛠️ <strong>No projects</strong> — Build at least 2 relevant projects.'),
            (p["certifications"] >= 1,
             f'📜 <strong>{p["certifications"]} Certification(s)</strong> — Validates your skills!',
             '📜 <strong>No certifications</strong> — Get 1–2 free ones from Coursera or NPTEL.'),
        ]:
            cls = "bonus-card" if condition else "warning-card"
            st.markdown(f'<div class="{cls}">{good if condition else bad}</div>', unsafe_allow_html=True)
        if p["backlogs"] > 0:
            st.markdown(f'<div class="warning-card">⚠️ <strong>{p["backlogs"]} Backlog(s)</strong> — Many companies have a no-backlog policy. Clear them ASAP.</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-header">🚀 Personalized Action Plan</div>', unsafe_allow_html=True)
        if not missing:
            st.success("🎉 You have all required skills! Focus on projects, certifications, and interview prep.")
        else:
            for i, skill in enumerate(top_missing):
                demand   = role_data["skill_weights"].get(skill, 50)
                res      = role_data.get("resources", {}).get(skill)
                res_html = (f'<div class="action-link">📚 <a href="{res[1]}" target="_blank" style="color:#b388f4">{res[0]}</a></div>'
                            if res else '<div class="action-link" style="color:#7a6e8a">Search on YouTube or Coursera</div>')
                priority = "🔴 Learn this first" if demand >= 75 else "🟡 After high-priority skills" if demand >= 55 else "🟢 When time permits"
                st.markdown(f'''<div class="action-card">
                    <div class="action-title">#{i+1} Learn {skill}</div>
                    <div class="action-meta">📊 <strong>{demand}%</strong> of placed <strong>{p["target_role"]}</strong>s had <strong>{skill}</strong> — but you don't.</div>
                    <div class="action-meta">🎯 {priority}</div>
                    {res_html}
                </div>''', unsafe_allow_html=True)

        st.markdown(f'<div class="section-header">🏢 Top Companies Hiring {p["target_role"]}</div>', unsafe_allow_html=True)
        for col, company in zip(st.columns(len(role_data["top_companies"])), role_data["top_companies"]):
            col.markdown(f'<div style="background:#232131;border:1px solid #3d2f5a;border-radius:10px;padding:0.8rem;text-align:center;color:#e8d5f5;font-weight:600">🏢<br>{company}</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-header">📊 Batch Analytics — Cohort View</div>', unsafe_allow_html=True)
        st.caption("Overview of all 50 students in the reference dataset")
        for col, (val, label) in zip(st.columns(4), [
            (batch["total"],       "Total Students"),
            (batch["avg_cgpa"],    "Average CGPA"),
            (batch["avg_interns"], "Avg Internships"),
            (batch["with_intern"], "Students with Internship"),
        ]):
            col.markdown(metric_box(val, label), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        with b1:
            fig_role_pie = go.Figure(go.Pie(
                labels=list(batch["role_counts"].keys()),
                values=list(batch["role_counts"].values()),
                hole=0.4, marker_colors=["#c482d5","#b388f4","#e91e8c","#f06292"]))
            fig_role_pie.update_layout(title=dict(text="Students by Role", font=dict(color="#e8d5f5")),
                height=280, paper_bgcolor=BG, font_color="#e8d5f5")
            st.plotly_chart(fig_role_pie, use_container_width=True)
        with b2:
            fig_cgpa = go.Figure(go.Bar(
                x=["CGPA 8.0+","CGPA 7.0–7.9","CGPA < 7.0"],
                y=[batch["high_cgpa"], batch["total"] - batch["high_cgpa"] - batch["low_cgpa"], batch["low_cgpa"]],
                marker_color=["#e91e8c","#f48fb1","#f06292"],
                text=[batch["high_cgpa"], batch["total"] - batch["high_cgpa"] - batch["low_cgpa"], batch["low_cgpa"]],
                textposition="outside", textfont=dict(color="#e8d5f5")
            ))
            fig_cgpa.update_layout(title=dict(text="CGPA Distribution", font=dict(color="#e8d5f5")),
                height=280, paper_bgcolor=BG, plot_bgcolor=BG,
                xaxis=dict(color="#e8d5f5"), yaxis=dict(color="#e8d5f5", showgrid=False))
            st.plotly_chart(fig_cgpa, use_container_width=True)
        st.markdown(f'''
        <div class="peer-card">📌 <strong>{batch["with_intern"]}</strong> of {batch["total"]} students have internship experience ({round(batch["with_intern"]/batch["total"]*100)}%).</div>
        <div class="peer-card">⚠️ <strong>{batch["no_intern"]}</strong> students have zero internships — high placement risk.</div>
        <div class="peer-card">🏆 <strong>{batch["high_cgpa"]}</strong> students have CGPA 8.0+ — strong academic performers.</div>
        ''', unsafe_allow_html=True)

        st.markdown('<div class="section-header">🏫 Your Placement Summary</div>', unsafe_allow_html=True)
        tc1, tc2 = st.columns(2)
        with tc1:
            st.info(f"""
**Student:** {p['name']}
**Target Role:** {p['target_role']}
**Branch:** {p['branch']} | **Year:** {p['year']}
**Readiness Score:** {score}%
**CGPA:** {p['cgpa']} | **Internships:** {p['internships']}
**Rank:** #{user_rank} out of {total_peers} peers
            """)
        with tc2:
            missing_str = ", ".join(sorted(missing)) if missing else "None — Student is ready!"
            focus       = top_missing[0] if top_missing else "Interview Preparation"
            st.warning(f"""
**Skill Gaps:** {missing_str}

**#1 Recommended Focus:** {focus}

**Placement Probability:** {curr_prob}% → can reach {after_full}%

**Status:** {"🟢 Ready for Placement" if score >= 70 else "🟡 Needs Preparation" if score >= 40 else "🔴 Significant Gaps"}
            """)

    # ── STUDENT: EDIT PROFILE ─────────────────────────────────────────────────
    elif user["role"] == "student" and st.session_state.student_page == "profile":
        st.markdown('<div class="hero-title">✏️ Edit Profile</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-sub">Keep your profile updated to get accurate readiness scores</div>', unsafe_allow_html=True)

        saved = db_get_profile(user["id"])
        col1, col2 = st.columns([1.3, 1])
        with col1:
            st.markdown('<div class="section-header">👤 Personal Info</div>', unsafe_allow_html=True)
            name   = st.text_input("Full Name", value=saved["name"] if saved else user.get("name", ""))
            branch = st.selectbox("Branch", ALL_BRANCHES,
                                  index=ALL_BRANCHES.index(saved["branch"]) if saved and saved.get("branch") in ALL_BRANCHES else 0)
            year   = st.selectbox("Year", ["1st Year","2nd Year","3rd Year","Final Year"],
                                  index=["1st Year","2nd Year","3rd Year","Final Year"].index(saved["year"])
                                  if saved and saved.get("year") in ["1st Year","2nd Year","3rd Year","Final Year"] else 0)
            target = st.selectbox("🎯 Target Role", list(MARKET_DATA.keys()),
                                  index=list(MARKET_DATA.keys()).index(saved["target_role"])
                                  if saved and saved.get("target_role") in MARKET_DATA else 0)
            st.markdown('<div class="section-header">🔗 Links</div>', unsafe_allow_html=True)
            linkedin = st.text_input("LinkedIn URL", value=saved.get("linkedin","") if saved else "", placeholder="https://linkedin.com/in/yourname")
            github   = st.text_input("GitHub URL",   value=saved.get("github","")   if saved else "", placeholder="https://github.com/yourname")
            st.markdown('<div class="section-header">📊 Academic Info</div>', unsafe_allow_html=True)
            cgpa = st.slider("CGPA", 0.0, 10.0, float(saved["cgpa"]) if saved else 7.0, 0.1)
            ca, cb = st.columns(2)
            with ca:
                internships    = st.number_input("Internships Done", 0, 10, int(saved["internships"])    if saved else 0)
                projects       = st.number_input("Projects",         0, 20, int(saved["projects"])       if saved else 0)
            with cb:
                certifications = st.number_input("Certifications",   0, 20, int(saved["certifications"]) if saved else 0)
                backlogs       = st.number_input("Active Backlogs",  0, 10, int(saved["backlogs"])       if saved else 0)
            if backlogs > 0:
                st.warning(f"⚠️ {backlogs} backlog(s) → -{min(backlogs*5,15)} pts penalty.")
            if internships >= 1:
                st.success("✅ Internship gives you bonus points!")
        with col2:
            st.markdown('<div class="section-header">🛠️ Your Skills</div>', unsafe_allow_html=True)
            st.caption("Tick all skills you currently know")
            saved_skills    = set(saved["skills"]) if saved else set()
            selected_skills = []
            skill_cols      = st.columns(2)
            for i, skill in enumerate(ALL_SKILLS):
                if skill_cols[i % 2].checkbox(skill, value=skill in saved_skills, key=f"sk_{skill}"):
                    selected_skills.append(skill)
        st.markdown("---")
        if st.button("💾 Save Profile & Analyze", type="primary"):
            if not name:
                st.warning("Please enter your name.")
            elif not selected_skills:
                st.warning("Please select at least one skill.")
            else:
                pd_data = dict(name=name, branch=branch, year=year, target_role=target,
                               skills=selected_skills, cgpa=cgpa, internships=internships,
                               projects=projects, certifications=certifications,
                               backlogs=backlogs, linkedin=linkedin, github=github)
                _, _, save_score, _ = analyze(pd_data, MARKET_DATA[target])
                db_save_profile(user["id"], pd_data, save_score)
                st.success(f"✅ Profile saved! Your readiness score: **{save_score}%**")
                st.session_state.student_page = "dashboard"
                st.rerun()

    # ── STUDENT: PLACEMENT DRIVES ─────────────────────────────────────────────
    elif user["role"] == "student" and st.session_state.student_page == "drives":
        st.markdown('<div class="hero-title">🏢 Placement Drives</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-sub">Active opportunities posted by your placement office</div>', unsafe_allow_html=True)
        profile_db = db_get_profile(user["id"])
        drives     = db_get_drives(active_only=True)
        my_apps    = {a["drive_id"] for a in db_get_my_apps(user["id"])}

        if not drives:
            st.info("No active drives right now. Check back later!")
            st.stop()

        for drive in drives:
            req_skills  = drive.get("required_skills","").split(",") if drive.get("required_skills") else []
            user_skills = set(profile_db["skills"]) if profile_db else set()
            skill_match = len(set(req_skills) & user_skills)
            skill_total = len(req_skills)
            match_pct   = int(skill_match / skill_total * 100) if skill_total else 0
            cgpa_ok     = (not profile_db) or (profile_db["cgpa"] >= drive.get("eligibility_cgpa", 0))
            applied     = drive["id"] in my_apps
            apply_link  = drive.get("apply_link","").strip()

            if applied:
                action_html = (f'<span class="apply-btn-applied">✅ Applied</span>&nbsp;&nbsp;'
                               + (f'<a href="{apply_link}" target="_blank" class="apply-btn" '
                                  f'style="background:linear-gradient(135deg,#3d2f5a,#2a2040);border:1px solid #c482d5;">🔗 Visit Site →</a>'
                                  if apply_link else ""))
            elif not cgpa_ok:
                action_html = '<span class="apply-btn-disabled">🚫 CGPA Too Low</span>'
            elif apply_link:
                action_html = f'<a href="{apply_link}" target="_blank" class="apply-btn">🚀 Apply Now →</a>'
            else:
                action_html = '<span class="apply-btn-disabled">🔗 No link available</span>'

            st.markdown(f'''<div class="drive-card">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.8rem">
                    <div>
                        <div style="font-size:1.15rem;font-weight:700;color:#e8d5f5">🏢 {drive["company"]}</div>
                        <div style="color:#b388f4;font-size:0.9rem;margin-top:0.2rem">{drive["role"]}</div>
                    </div>
                    <div style="text-align:right">
                        <div style="font-family:JetBrains Mono,monospace;color:#e91e8c;font-size:1rem;font-weight:700">💰 {drive.get("package","TBD")}</div>
                        <div style="color:#7a6e8a;font-size:0.78rem;margin-top:0.2rem">📅 {drive.get("drive_date","TBD")}</div>
                    </div>
                </div>
                <p style="color:#7a6e8a;font-size:0.85rem;margin:0 0 0.7rem">{drive.get("description","")}</p>
                <div style="margin-bottom:0.6rem">
                    {chip(f"Min CGPA: {drive.get('eligibility_cgpa','6.0')}", "blue")}
                    {" ".join([chip(s, "gray") for s in req_skills[:5]])}
                </div>
                <div style="color:#7a6e8a;font-size:0.8rem;margin-bottom:1rem">
                    Skill match: {skill_match}/{skill_total} &nbsp;{prog_bar(match_pct)}
                </div>
                <div style="display:flex;align-items:center;gap:1rem">{action_html}</div>
            </div>''', unsafe_allow_html=True)

            if not applied and cgpa_ok:
                track_key = f"track_clicked_{drive['id']}"
                if track_key not in st.session_state:
                    st.session_state[track_key] = False
                col_btn, _ = st.columns([2, 5])
                with col_btn:
                    if st.button("📌 Track my application", key=f"track_{drive['id']}", type="secondary"):
                        st.session_state[track_key] = True
                if st.session_state[track_key]:
                    col_yes, col_no, _ = st.columns([1, 1, 4])
                    with col_yes:
                        if st.button("✅ Yes, I applied", key=f"yes_{drive['id']}", type="primary"):
                            db_apply_drive(drive["id"], user["id"])
                            st.success(f"✅ {drive['company']} application tracked!")
                            st.session_state[track_key] = False
                            st.rerun()
                    with col_no:
                        if st.button("❌ Not yet", key=f"no_{drive['id']}"):
                            st.session_state[track_key] = False
                            st.rerun()
                    st.warning(f"⚠️ Have you actually applied on the {drive['company']} official website? Click **Apply Now** first, then come back to track it.")

    # ── STUDENT: MY APPLICATIONS ──────────────────────────────────────────────
    elif user["role"] == "student" and st.session_state.student_page == "applications":
        st.markdown('<div class="hero-title">📋 My Applications</div>', unsafe_allow_html=True)
        apps = db_get_my_apps(user["id"])
        if not apps:
            st.info("You haven't applied to any drives yet.")
            if st.button("→ Browse Drives"):
                st.session_state.student_page = "drives"
                st.rerun()
            st.stop()
        status_color = {"Applied":"blue","Shortlisted":"green","Rejected":"red","Selected":"green"}
        for app in apps:
            s = app.get("status","Applied")
            st.markdown(f'''<div class="action-card">
                <div style="display:flex;justify-content:space-between">
                    <div>
                        <div class="action-title">🏢 {app["company"]} — {app["role"]}</div>
                        <div class="action-meta">💰 {app.get("package","TBD")} · 📅 {app.get("drive_date","TBD")} · Applied: {app["applied_at"][:10]}</div>
                    </div>
                    <div>{chip(s, status_color.get(s,"gray"))}</div>
                </div>
            </div>''', unsafe_allow_html=True)

    # ── STUDENT: PEER LEADERBOARD ─────────────────────────────────────────────
    elif user["role"] == "student" and st.session_state.student_page == "peers":
        st.markdown('<div class="hero-title">🏆 Peer Leaderboard</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-sub">See how you rank among your college peers</div>', unsafe_allow_html=True)
        students = [s for s in db_get_all_students() if s.get("readiness_score") is not None]
        if not students:
            st.info("No peer data yet. Peers need to save their profiles first.")
            st.stop()
        profile_db = db_get_profile(user["id"])
        my_rank    = next((i+1 for i, s in enumerate(students) if s["user_id"] == user["id"]), None)
        if my_rank:
            pct = int((1 - (my_rank-1) / max(len(students), 1)) * 100)
            st.markdown(f'''<div style="background:linear-gradient(135deg,#1e1a2e,#2a2040);border:1px solid #3d2f5a;border-radius:14px;padding:1.5rem;text-align:center;margin-bottom:1rem">
                <div style="font-size:2.5rem;font-weight:700;color:#c9a8f0">#{my_rank}</div>
                <div style="color:#9d87b8">Your Rank out of {len(students)} students</div>
                <div style="color:#b388f4;margin-top:0.3rem">Better than {pct}% of your peers</div>
            </div>''', unsafe_allow_html=True)
        filter_role = st.selectbox("Filter by Target Role", ["All Roles"] + list(MARKET_DATA.keys()))
        filtered    = students if filter_role == "All Roles" else [s for s in students if s.get("target_role") == filter_role]
        for i, s in enumerate(filtered[:20]):
            is_me  = s["user_id"] == user["id"]
            sc     = s.get("readiness_score", 0) or 0
            you    = chip("YOU","blue") if is_me else ""
            border = "#c482d5" if is_me else score_color(sc)
            st.markdown(f'''<div style="background:#1e1a2e;border:1px solid {border};border-radius:10px;padding:0.8rem 1.2rem;margin-bottom:0.5rem;display:flex;align-items:center;gap:1rem">
                <div style="font-family:JetBrains Mono,monospace;color:#c482d5;font-size:1.3rem;font-weight:700;min-width:50px">#{i+1}</div>
                <div style="flex:1">
                    <div style="font-weight:600;color:#e8d5f5">{s.get("name") or s.get("user_name","Anonymous")} {you}</div>
                    <div style="color:#7a6e8a;font-size:0.8rem">{s.get("branch","—")} · {s.get("target_role","—")}</div>
                    {prog_bar(sc, score_color(sc))}
                </div>
                <div style="font-family:JetBrains Mono,monospace;font-size:1.2rem;font-weight:600;color:{score_color(sc)}">{sc}%</div>
            </div>''', unsafe_allow_html=True)

    # ── STUDENT: ANNOUNCEMENTS ────────────────────────────────────────────────
    elif user["role"] == "student" and st.session_state.student_page == "announcements":
        st.markdown('<div class="hero-title">📢 Announcements & Tech News</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-sub">College notices + real-time technology news updated every hour</div>', unsafe_allow_html=True)

        tab_ann, tab_news = st.tabs(["🏫 College Announcements","🌐 Live Tech News"])
        with tab_ann:
            anns = db_get_announcements()
            if not anns:
                st.info("No announcements from your placement office yet.")
            for a in anns:
                st.markdown(ann_html(a), unsafe_allow_html=True)

        with tab_news:
            st.markdown(f'''<div style="background:#1e1a2e;border:1px solid #3d2f5a;border-radius:12px;
                padding:0.8rem 1.2rem;margin-bottom:1rem;display:flex;justify-content:space-between;align-items:center">
                <div style="color:#c9a8f0;font-size:0.85rem;font-weight:600">
                    🌐 Live feed from TechCrunch · The Verge · Hacker News · MIT Tech Review · Wired · VentureBeat
                </div>
                <div style="color:#7a6e8a;font-size:0.75rem">🔄 Auto-refreshes every hour · {datetime.now().strftime("%d %b %Y, %I:%M %p")}</div>
            </div>''', unsafe_allow_html=True)

            fcol1, fcol2, fcol3, fcol4 = st.columns(4)
            with fcol1: filter_ai  = st.checkbox("🤖 AI / ML",          value=True)
            with fcol2: filter_job = st.checkbox("💼 Jobs / Hiring",     value=True)
            with fcol3: filter_dev = st.checkbox("💻 Dev / Coding",      value=True)
            with fcol4: filter_biz = st.checkbox("🚀 Startups / Funding",value=True)

            active_kws = []
            if filter_ai:  active_kws += ["ai","artificial intelligence","machine learning","openai","gpt","llm","deep learning","neural","gemini","claude"]
            if filter_job: active_kws += ["hiring","jobs","layoff","career","workforce","employment","recruit","salary"]
            if filter_dev: active_kws += ["python","software","developer","engineer","coding","programming","cloud","github","api","kubernetes","docker"]
            if filter_biz: active_kws += ["startup","funding","billion","unicorn","acquisition","ipo","venture","investment"]

            with st.spinner("📡 Fetching latest tech news..."):
                news = fetch_tech_news(max_per_feed=5)

            if not news:
                st.markdown('''<div style="background:#232131;border:1px solid #3d2f5a;border-radius:12px;padding:2rem;text-align:center">
                    <div style="font-size:2rem">📡</div>
                    <div style="color:#e8d5f5;font-weight:600;margin-top:0.5rem">Could not fetch live news</div>
                    <div style="color:#7a6e8a;font-size:0.85rem;margin-top:0.3rem">Check your internet connection.</div>
                </div>''', unsafe_allow_html=True)
            else:
                filtered_news = [a for a in news if any(kw in a["title"].lower() or kw in a["desc"].lower() for kw in active_kws)] if active_kws else news
                if not filtered_news:
                    st.info("No articles match your selected filters. Try enabling more categories above.")
                else:
                    nc1, nc2 = st.columns(2)
                    for i, article in enumerate(filtered_news):
                        with (nc1 if i % 2 == 0 else nc2):
                            st.markdown(render_news_card(article), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄 Refresh News Now", type="primary"):
                st.cache_data.clear()
                st.rerun()

    # ── STUDENT: AI CAREER ASSISTANT ─────────────────────────────────────────
    elif user["role"] == "student" and st.session_state.student_page == "chatbot":
        profile_db = db_get_profile(user["id"])
        st.markdown('<div class="hero-title">🤖 AI Career Assistant</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-sub">Your personal placement coach — ask anything about jobs, skills, resumes & interviews</div>', unsafe_allow_html=True)

        if profile_db:
            skills_str  = ", ".join(profile_db.get("skills") or [])
            profile_ctx = f"""The student's profile:
- Name: {profile_db.get('name','')}
- Branch: {profile_db.get('branch','')} | Year: {profile_db.get('year','')}
- Target Role: {profile_db.get('target_role','')}
- CGPA: {profile_db.get('cgpa','')} | Internships: {profile_db.get('internships',0)} | Projects: {profile_db.get('projects',0)}
- Certifications: {profile_db.get('certifications',0)} | Backlogs: {profile_db.get('backlogs',0)}
- Skills: {skills_str}
- Readiness Score: {profile_db.get('readiness_score',0)}%
Use this profile to give personalised, specific advice."""
        else:
            profile_ctx = "The student hasn't filled their profile yet. Encourage them to do so for personalised advice, but still help them with general queries."

        SYSTEM_PROMPT = f"""You are CareerEdge AI, a friendly, expert AI career assistant embedded inside CampusEdge — a college placement intelligence platform used by Indian engineering and management students.

Your job is to help students with:
- Resume writing, formatting, and tips
- Interview preparation (technical + HR rounds)
- Skill gap analysis and learning roadmaps
- Career guidance and role selection
- Internship and job search strategies
- LinkedIn profile optimisation
- Salary negotiation advice
- Company-specific placement preparation (TCS, Google, Infosys, Wipro, Swiggy, Amazon, etc.)
- Certification recommendations
- Soft skills and communication tips

{profile_ctx}

Tone: Friendly, encouraging, practical, and concise. Use bullet points when listing steps. Use emojis sparingly to keep it warm. Never give vague answers — always be specific and actionable.
Keep responses under 300 words unless the user asks for something detailed."""

        suggestions = [
            "How do I improve my resume?",
            "What skills should I learn next?",
            "How to prepare for Google interviews?",
            "Write a cold email to a recruiter",
            "How to answer 'Tell me about yourself'?",
            "Best free certifications for placements",
        ]

        st.markdown("""
        <style>
        .chat-user { background:linear-gradient(135deg,#2a1a45,#3d2f5a);border:1px solid #4a2a6a;border-radius:16px 16px 4px 16px;padding:0.75rem 1.1rem;margin:0.4rem 0 0.4rem 3rem;color:#e8d5f5;font-size:0.92rem;line-height:1.55; }
        .chat-ai { background:#1e1a2e;border:1px solid #3d2f5a;border-radius:16px 16px 16px 4px;padding:0.75rem 1.1rem;margin:0.4rem 3rem 0.4rem 0;color:#e8d5f5;font-size:0.92rem;line-height:1.55; }
        .chat-avatar-ai { font-size:1.3rem;margin-bottom:0.2rem;color:#c482d5; }
        .chat-avatar-user { text-align:right;font-size:1.3rem;margin-bottom:0.2rem;color:#b388f4; }
        .chat-wrap { max-height:520px;overflow-y:auto;padding:0.5rem 0.2rem;margin-bottom:1rem; }
        </style>
        """, unsafe_allow_html=True)

        if not st.session_state.chat_history:
            st.markdown("""
            <div style='background:linear-gradient(135deg,#1e1a2e,#2a2040);border:1px solid #3d2f5a;border-radius:14px;padding:1.2rem 1.4rem;margin-bottom:1rem'>
                <div style='color:#c9a8f0;font-weight:600;margin-bottom:0.6rem'>👋 Hi! I'm CareerEdge AI. Try asking:</div>
            </div>
            """, unsafe_allow_html=True)
            sugg_cols = st.columns(3)
            for i, s in enumerate(suggestions):
                if sugg_cols[i % 3].button(s, key=f"sugg_{i}", use_container_width=True, type="secondary"):
                    st.session_state.chat_history.append({"role":"user","content":s})
                    st.rerun()

        if st.session_state.chat_history:
            st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    st.markdown(f'<div class="chat-avatar-user">You 👤</div><div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-avatar-ai">🤖 CareerEdge AI</div><div class="chat-ai">{msg["content"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "user":
            with st.spinner("CareerEdge AI is thinking..."):
                try:
                    messages    = st.session_state.chat_history[-10:]
                    gemini_key  = st.secrets.get("GEMINI_API_KEY", "")
                    gemini_url  = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={gemini_key}"
                    gemini_contents = [
                        {"role":"user",  "parts":[{"text": SYSTEM_PROMPT}]},
                        {"role":"model", "parts":[{"text": "Understood! I am CareerEdge AI, ready to help."}]},
                    ]
                    for m in messages:
                        role = "user" if m["role"] == "user" else "model"
                        gemini_contents.append({"role": role, "parts": [{"text": m["content"]}]})
                    payload = json.dumps({
                        "contents": gemini_contents,
                        "generationConfig": {"maxOutputTokens": 1024, "temperature": 0.7}
                    }).encode("utf-8")
                    req = urllib.request.Request(gemini_url, data=payload,
                                                 headers={"Content-Type":"application/json"}, method="POST")
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        result = json.loads(resp.read().decode("utf-8"))
                    ai_reply = result["candidates"][0]["content"]["parts"][0]["text"]
                    st.session_state.chat_history.append({"role":"assistant","content":ai_reply})
                    st.rerun()
                except urllib.error.HTTPError as e:
                    try:
                        err_body = e.read().decode("utf-8")
                        err_data = json.loads(err_body) if err_body.strip().startswith("{") else {}
                        err_msg  = err_data.get("error",{}).get("message", err_body[:200] if err_body else "Unknown error")
                    except Exception:
                        err_msg = f"HTTP {e.code} error"
                    if e.code in (401, 403):
                        st.error("🔑 API key missing or invalid. Check your GEMINI_API_KEY in secrets.toml")
                    elif e.code == 429:
                        time.sleep(3)
                        st.warning("⏳ Rate limit hit — retrying in a moment, please resend your message.")
                    else:
                        st.error(f"API error ({e.code}): {err_msg}")
                except urllib.error.URLError as e:
                    st.error(f"Connection error: {str(e.reason)}. Check your internet connection.")
                except Exception as ex:
                    st.error(f"Something went wrong: {str(ex)}")

        st.markdown("---")
        inp_col, btn_col = st.columns([5, 1])
        with inp_col:
            user_input = st.text_input("Message", placeholder="Ask about resumes, interviews, skills, companies...",
                                       label_visibility="collapsed", key="chat_input")
        with btn_col:
            send = st.button("Send ➤", type="primary", use_container_width=True)
        if send and user_input.strip():
            st.session_state.chat_history.append({"role":"user","content":user_input.strip()})
            st.rerun()
        if st.session_state.chat_history:
            if st.button("🗑️ Clear conversation", type="secondary"):
                st.session_state.chat_history = []
                st.rerun()
        with st.expander("⚙️ Setup — How to connect the AI"):
            st.markdown("""
1. Go to aistudio.google.com and sign in with Google
2. Click **Get API Key** and create a new key (completely free)
3. Open `.streamlit/secrets.toml` and add:
```
GEMINI_API_KEY = "your-key-here"
```
4. Save and restart Streamlit!
            """)

    # ── TPO: OVERVIEW ─────────────────────────────────────────────────────────
    elif user["role"] == "tpo" and st.session_state.tpo_page == "overview":
        st.markdown('<div class="hero-title">📊 TPO Overview</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="hero-sub">Welcome, <strong>{user.get("name","")}</strong> · {datetime.now().strftime("%d %b %Y")}</div>', unsafe_allow_html=True)

        students = db_get_all_students()
        drives   = db_get_drives(active_only=False)
        profiled = [s for s in students if s.get("readiness_score") is not None]
        avg_sc   = int(sum(s.get("readiness_score",0) or 0 for s in profiled) / max(len(profiled), 1))
        ready    = sum(1 for s in profiled if (s.get("readiness_score") or 0) >= 75)
        active_d = sum(1 for d in drives if d.get("is_active"))

        for col, (v, l) in zip(st.columns(5), [
            (len(students), "Total Students"), (len(profiled), "Profiles Submitted"),
            (f"{avg_sc}%",  "Avg Readiness"),  (ready,          "Placement Ready"),
            (active_d,      "Active Drives"),
        ]):
            col.markdown(metric_box(v, l), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        today    = datetime.now().date()
        upcoming = []
        for d in drives:
            if not d.get("is_active"):
                continue
            try:
                drive_date = datetime.strptime(d["drive_date"], "%Y-%m-%d").date()
                days_left  = (drive_date - today).days
                upcoming.append((days_left, d))
            except Exception:
                pass
        upcoming.sort(key=lambda x: x[0])

        if upcoming:
            st.markdown('<div class="section-header">⏳ Upcoming Drives Countdown</div>', unsafe_allow_html=True)
            cols = st.columns(min(len(upcoming), 4))
            for i, (days, d) in enumerate(upcoming[:4]):
                if days < 0:   label, color = "🔴 Overdue",    "#f06292"
                elif days == 0:label, color = "🔴 Today!",     "#e91e8c"
                elif days <= 3:label, color = f"🟠 {days}d left","#f48fb1"
                elif days <= 7:label, color = f"🟡 {days}d left","#c482d5"
                else:          label, color = f"🟢 {days}d left","#b388f4"
                cols[i].markdown(f'''<div style="background:#232131;border:1px solid #3d2f5a;
                    border-radius:12px;padding:1rem;text-align:center;border-top:3px solid {color}">
                    <div style="font-size:1.8rem;font-weight:700;color:{color}">{abs(days) if days >= 0 else "!"}</div>
                    <div style="color:#7a6e8a;font-size:0.7rem">days left</div>
                    <div style="color:#e8d5f5;font-weight:600;font-size:0.85rem;margin-top:0.4rem">{d["company"]}</div>
                    <div style="color:#b388f4;font-size:0.75rem">{d["role"]}</div>
                    <div style="color:#7a6e8a;font-size:0.72rem;margin-top:0.3rem">{label}</div>
                </div>''', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

        fig_pie, fig_branch, fig_role_chart = render_tpo_charts(students)
        if fig_pie:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="section-header">🎯 Readiness Distribution</div>', unsafe_allow_html=True)
                st.plotly_chart(fig_pie, use_container_width=True)
            with c2:
                st.markdown('<div class="section-header">📊 Avg Score by Branch</div>', unsafe_allow_html=True)
                st.plotly_chart(fig_branch, use_container_width=True)
            st.markdown('<div class="section-header">🎯 Role Preferences</div>', unsafe_allow_html=True)
            st.plotly_chart(fig_role_chart, use_container_width=True)

        trends = db_get_monthly_trends()
        if trends:
            st.markdown('<div class="section-header">📈 Month-wise Application Trend</div>', unsafe_allow_html=True)
            months, apps_count, selected_count = [t["month"] for t in trends], [t["applications"] for t in trends], [t["selected"] for t in trends]
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Bar(x=months, y=apps_count, name="Applications", marker_color="#c482d5", opacity=0.8))
            fig_trend.add_trace(go.Scatter(x=months, y=selected_count, name="Selected",
                mode="lines+markers", line=dict(color="#e91e8c", width=3), marker=dict(size=8, color="#e91e8c")))
            fig_trend.update_layout(height=300, paper_bgcolor=BG, plot_bgcolor=BG,
                margin=dict(t=20,b=30,l=40,r=20), legend=dict(font=dict(color="#9d87b8")),
                xaxis=dict(color="#9d87b8", showgrid=False),
                yaxis=dict(color="#9d87b8", showgrid=True, gridcolor="#2d2545"))
            st.plotly_chart(fig_trend, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="section-header">🕐 Recent Activity</div>', unsafe_allow_html=True)
            activity = db_get_recent_activity(limit=8)
            if not activity:
                st.markdown('<div class="peer-card">No activity yet.</div>', unsafe_allow_html=True)
            for act in activity:
                status   = act.get("status","Applied")
                s_color  = "#e91e8c" if status == "Selected" else "#c482d5" if status == "Shortlisted" else "#7a6e8a"
                s_icon   = "🏆" if status == "Selected" else "⭐" if status == "Shortlisted" else "📝"
                time_str = act.get("applied_at","")[:16]
                st.markdown(f'''<div class="peer-card" style="margin-bottom:0.4rem">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                        <div>
                            <span style="color:#e8d5f5;font-weight:600">{act.get("student_name","—")}</span>
                            <span style="color:#7a6e8a;font-size:0.8rem"> → {act.get("company","—")} ({act.get("role","—")})</span>
                        </div>
                        <span style="color:{s_color};font-size:0.8rem">{s_icon} {status}</span>
                    </div>
                    <div style="color:#4a3a60;font-size:0.72rem;margin-top:0.2rem">🕐 {time_str}</div>
                </div>''', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="section-header">🏆 Top 5 Students</div>', unsafe_allow_html=True)
            for s in profiled[:5]:
                sc = s.get("readiness_score", 0) or 0
                st.markdown(f'<div class="bonus-card"><div style="display:flex;justify-content:space-between"><div><strong style="color:#e8d5f5">{s.get("name") or s.get("user_name","—")}</strong><div style="color:#7a6e8a;font-size:0.8rem">{s.get("branch","—")} · {s.get("target_role","—")}</div></div><div style="font-family:JetBrains Mono,monospace;color:#e91e8c;font-size:1.2rem;font-weight:700">{sc}%</div></div></div>', unsafe_allow_html=True)
            st.markdown('<div class="section-header">⚠️ Need Attention</div>', unsafe_allow_html=True)
            for s in sorted(profiled, key=lambda x: x.get("readiness_score",0) or 0)[:3]:
                sc = s.get("readiness_score", 0) or 0
                st.markdown(f'<div class="warning-card"><div style="display:flex;justify-content:space-between"><div><strong style="color:#e8d5f5">{s.get("name") or s.get("user_name","—")}</strong><div style="color:#7a6e8a;font-size:0.8rem">{s.get("branch","—")} · {s.get("target_role","—")}</div></div><div style="font-family:JetBrains Mono,monospace;color:#f06292;font-size:1.2rem;font-weight:700">{sc}%</div></div></div>', unsafe_allow_html=True)

    # ── TPO: ALL STUDENTS ─────────────────────────────────────────────────────
    elif user["role"] == "tpo" and st.session_state.tpo_page == "students":
        st.markdown('<div class="hero-title">👥 All Students</div>', unsafe_allow_html=True)
        students = db_get_all_students()
        cf1, cf2, cf3 = st.columns(3)
        with cf1: fb = st.selectbox("Branch",      ["All"] + ALL_BRANCHES)
        with cf2: fr = st.selectbox("Target Role", ["All"] + list(MARKET_DATA.keys()))
        with cf3: fs = st.selectbox("Score Range", ["All","75+ (Ready)","50-74","25-49","<25"])
        filtered = students
        if fb != "All": filtered = [s for s in filtered if s.get("branch") == fb]
        if fr != "All": filtered = [s for s in filtered if s.get("target_role") == fr]
        sm = {"75+ (Ready)":(75,101),"50-74":(50,75),"25-49":(25,50),"<25":(0,25)}
        if fs in sm:
            lo, hi = sm[fs]
            filtered = [s for s in filtered if lo <= (s.get("readiness_score") or 0) < hi]
        st.markdown(f"<p style='color:#7a6e8a'>Showing <strong style='color:#e8d5f5'>{len(filtered)}</strong> students</p>", unsafe_allow_html=True)
        if filtered:
            rows = []
            for s in filtered:
                sc       = s.get("readiness_score") or 0
                tier, _  = get_readiness_tier(sc)
                rows.append({
                    "Name":        s.get("name") or s.get("user_name","—"),
                    "Branch":      s.get("branch") or "—",
                    "Year":        s.get("year") or "—",
                    "Target Role": s.get("target_role") or "—",
                    "CGPA":        s.get("cgpa") or "—",
                    "Score":       f"{sc}%",
                    "Status":      tier,
                    "Internships": s.get("internships") or 0,
                    "Backlogs":    s.get("backlogs") or 0,
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            st.markdown('<div class="section-header">🔍 Student Detail View</div>', unsafe_allow_html=True)
            student_names = [s.get("name") or s.get("user_name","—") for s in filtered]
            sel_name = st.selectbox("Select a student", student_names, key="student_detail_select")
            sel = next((s for s in filtered if (s.get("name") or s.get("user_name","—")) == sel_name), None)
            if sel:
                sc   = sel.get("readiness_score") or 0
                role = sel.get("target_role")
                have_s, missing_s = set(), set()
                if role and role in MARKET_DATA:
                    have_s, missing_s, _, _ = analyze(sel, MARKET_DATA[role])
                s1, s2, s3 = st.columns(3)
                with s1:
                    linkedin_html = (f"<a href='{sel['linkedin']}' target='_blank' style='color:#b388f4;font-size:0.82rem'>🔗 LinkedIn</a>"
                                     if sel.get("linkedin") else "")
                    github_html   = (f"&nbsp;&nbsp;<a href='{sel['github']}' target='_blank' style='color:#b388f4;font-size:0.82rem'>🐙 GitHub</a>"
                                     if sel.get("github") else "")
                    st.markdown(f'''<div class="action-card">
                        <div class="action-title">{sel.get("name") or "—"}</div>
                        <div class="action-meta">{sel.get("branch") or "—"} · {sel.get("year") or "—"}</div>
                        <div class="action-meta">CGPA: {sel.get("cgpa") or "—"} · Backlogs: {sel.get("backlogs") or 0}</div>
                        <div class="action-meta">Internships: {sel.get("internships") or 0} · Projects: {sel.get("projects") or 0}</div>
                        <div style="margin-top:0.5rem">{linkedin_html}{github_html}</div>
                    </div>''', unsafe_allow_html=True)
                with s2:
                    have_chips    = " ".join([chip("✓ "+sk, "green") for sk in sorted(have_s)])
                    missing_chips = " ".join([chip("✗ "+sk, "red")   for sk in sorted(missing_s)])
                    st.markdown(f'''<div class="action-card">
                        <div class="action-title">Skills</div>
                        <div style="margin-top:0.5rem">{have_chips or '<span style="color:#7a6e8a">No skills matched</span>'}</div>
                        <div style="margin-top:0.5rem">{missing_chips or '<span style="color:#e91e8c">All skills present!</span>'}</div>
                    </div>''', unsafe_allow_html=True)
                with s3:
                    tier_label = get_readiness_tier(sc)[0]
                    st.markdown(f'''<div style="background:#232131;border:1px solid #2d2545;border-radius:12px;padding:1.2rem;text-align:center">
                        <div style="font-size:2.5rem;font-weight:700;color:{score_color(sc)}">{sc}%</div>
                        <div style="color:#7a6e8a">Readiness Score</div>
                        <div style="color:{score_color(sc)};margin-top:0.3rem">{tier_label}</div>
                    </div>''', unsafe_allow_html=True)

    # ── TPO: MANAGE DRIVES ────────────────────────────────────────────────────
    elif user["role"] == "tpo" and st.session_state.tpo_page == "drives":
        st.markdown('<div class="hero-title">🏢 Manage Drives</div>', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["📋 All Drives","➕ Post New Drive"])
        with tab1:
            for drive in db_get_drives(active_only=False):
                applicants = db_get_drive_applicants(drive["id"])
                active     = bool(drive.get("is_active"))
                st.markdown(f'''<div class="drive-card">
                    <div style="font-size:1.1rem;font-weight:700;color:#e8d5f5">{drive["company"]} — {drive["role"]}</div>
                    <div style="color:#b388f4;font-size:0.85rem">{drive.get("package","TBD")} · {drive.get("drive_date","TBD")}</div>
                    <div style="margin-top:0.4rem">{chip("Active","green") if active else chip("Closed","red")} · {len(applicants)} applicant(s)</div>
                </div>''', unsafe_allow_html=True)
                with st.expander(f"👥 View {len(applicants)} Applicants — {drive['company']}"):
                    if not applicants:
                        st.info("No applicants yet.")
                    else:
                        for a in applicants:
                            sc      = a.get("readiness_score") or 0
                            curr_s  = a.get("status","Applied")
                            ac1, ac2, ac3 = st.columns([2,1,1])
                            with ac1:
                                st.markdown(f"**{a.get('name','—')}** ({a.get('username','')}) · CGPA: {a.get('cgpa','—')} · Score: {sc}%")
                            with ac2:
                                new_s = st.selectbox("Status", ["Applied","Shortlisted","Selected","Rejected"],
                                                     index=["Applied","Shortlisted","Selected","Rejected"].index(curr_s),
                                                     key=f"as_{a['id']}")
                            with ac3:
                                if st.button("Update", key=f"upd_{a['id']}"):
                                    db_update_app_status(a["id"], new_s)
                                    st.rerun()
                dc1, _ = st.columns([1,4])
                with dc1:
                    if st.button("⛔ Close" if active else "✅ Reopen", key=f"tog_{drive['id']}"):
                        db_toggle_drive(drive["id"], not active)
                        st.rerun()
        with tab2:
            st.markdown('<div class="section-header">Post a New Drive</div>', unsafe_allow_html=True)
            company     = st.text_input("Company Name *")
            drole       = st.text_input("Job Role *")
            package     = st.text_input("Package (e.g. 10 LPA)")
            description = st.text_area("Job Description", height=100)
            drive_date  = st.date_input("Drive Date")
            apply_link  = st.text_input("Application Link")
            min_cgpa    = st.slider("Minimum CGPA", 0.0, 10.0, 6.0, 0.1)
            branches    = st.multiselect("Eligible Branches", ALL_BRANCHES, default=["Computer Science","Information Technology"])
            req_skills  = st.multiselect("Required Skills", ALL_SKILLS)
            if st.button("📤 Post Drive", type="primary"):
                if not company or not drole:
                    st.warning("Company and Role are required.")
                else:
                    db_post_drive({
                        "company": company, "role": drole, "package": package,
                        "description": description, "eligibility_cgpa": min_cgpa,
                        "eligible_branches": branches, "required_skills": req_skills,
                        "drive_date": str(drive_date), "apply_link": apply_link
                    }, user["id"])
                    st.success(f"✅ Drive for {company} posted!")
                    st.rerun()

    # ── TPO: ANNOUNCEMENTS ────────────────────────────────────────────────────
    elif user["role"] == "tpo" and st.session_state.tpo_page == "announcements":
        st.markdown('<div class="hero-title">📢 Announcements & Tech News</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-sub">Manage college notices · post to students · monitor live tech trends</div>', unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["📢 Current Announcements","➕ Post New","🌐 Live Tech Trends"])
        with tab1:
            anns = db_get_announcements()
            if not anns:
                st.info("No announcements posted yet. Use the 'Post New' tab to add one.")
            for a in anns:
                st.markdown(ann_html(a), unsafe_allow_html=True)
                if st.button("🗑️ Delete", key=f"del_{a['id']}"):
                    db_delete_announcement(a["id"])
                    st.rerun()
        with tab2:
            st.markdown('<div class="section-header">Post a New Announcement</div>', unsafe_allow_html=True)
            title    = st.text_input("Title *", placeholder="e.g. Google Pre-Placement Talk – Feb 25th")
            content  = st.text_area("Content", height=120, placeholder="Add full details here...")
            priority = st.selectbox("Priority", ["normal","high","low"],
                                    format_func=lambda x: {"normal":"📢 Normal","high":"🔴 High Priority","low":"🟢 Low Priority"}[x])
            st.caption("💡 High priority announcements appear with a red border for students.")
            if st.button("📤 Post Announcement", type="primary"):
                if not title:
                    st.warning("Title is required.")
                else:
                    db_post_announcement(title, content, priority, user["id"])
                    st.success(f"✅ Announcement posted: **{title}**")
                    st.rerun()
        with tab3:
            st.markdown(f'''<div style="background:#1e1a2e;border:1px solid #3d2f5a;border-radius:12px;
                padding:0.8rem 1.2rem;margin-bottom:1rem;display:flex;justify-content:space-between;align-items:center">
                <div style="color:#c9a8f0;font-size:0.85rem;font-weight:600">
                    🌐 Live industry trends from TechCrunch · The Verge · Hacker News · Wired · VentureBeat
                </div>
                <div style="color:#7a6e8a;font-size:0.75rem">🔄 Updates every hour · {datetime.now().strftime("%d %b %Y, %I:%M %p")}</div>
            </div>''', unsafe_allow_html=True)
            with st.spinner("📡 Fetching latest tech news..."):
                news = fetch_tech_news(max_per_feed=4)
            if not news:
                st.warning("Could not fetch live news. Check internet connection.")
            else:
                nc1, nc2 = st.columns(2)
                for i, article in enumerate(news):
                    col = nc1 if i % 2 == 0 else nc2
                    with col:
                        st.markdown(render_news_card(article), unsafe_allow_html=True)
                        if st.button("📌 Post to Students", key=f"post_news_{i}"):
                            db_post_announcement(
                                title=f"📰 {article['title'][:100]}",
                                content=f"{article['desc']} | Source: {article['source']} | {article['link']}",
                                priority="normal", posted_by=user["id"]
                            )
                            st.success("✅ Article posted to student announcements!")
                            st.rerun()
            if st.button("🔄 Refresh News", type="primary"):
                st.cache_data.clear()
                st.rerun()

    # ── TPO: SKILL GAP REPORT ─────────────────────────────────────────────────
    elif user["role"] == "tpo" and st.session_state.tpo_page == "skill_gaps":
        st.markdown('<div class="hero-title">🔍 Skill Gap Report</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-sub">College-wide skill gap analysis to guide training programs</div>', unsafe_allow_html=True)
        students = db_get_all_students()
        profiled = [s for s in students if s.get("target_role")]
        if not profiled:
            st.info("No student profiles yet.")
            st.stop()
        missing_skills = get_common_missing(profiled)
        st.markdown('<div class="section-header">🔴 Most Common Missing Skills (College-Wide)</div>', unsafe_allow_html=True)
        if missing_skills:
            max_c = missing_skills[0][1]
            for skill, count in missing_skills:
                pct = int(count / max(len(profiled), 1) * 100)
                st.markdown(f'''<div class="warning-card">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                        <div><span style="font-family:JetBrains Mono,monospace;color:#f06292;font-size:1rem">{skill}</span>
                        <span style="color:#7a6e8a;font-size:0.8rem;margin-left:0.8rem">{count} students missing · {pct}% of profiled</span></div>
                        <div style="font-family:JetBrains Mono,monospace;color:#f06292">{count}</div>
                    </div>
                    {prog_bar(int(count / max(max_c,1) * 100),"#f06292")}
                </div>''', unsafe_allow_html=True)
        st.markdown('<div class="section-header">📊 Skill Gaps by Target Role</div>', unsafe_allow_html=True)
        for role_name, role_data in MARKET_DATA.items():
            role_students = [s for s in profiled if s.get("target_role") == role_name]
            if not role_students:
                continue
            role_missing = {}
            for s in role_students:
                for req in role_data["required_skills"]:
                    if req not in set(s.get("skills",[])):
                        role_missing[req] = role_missing.get(req, 0) + 1
            with st.expander(f"🎯 {role_name} ({len(role_students)} students)"):
                if role_missing:
                    st.dataframe(pd.DataFrame([{
                        "Skill": sk, "Missing": cnt,
                        "% of Role": f"{int(cnt/len(role_students)*100)}%",
                        "Market Demand": f"{role_data['skill_weights'].get(sk,50)}%"
                    } for sk, cnt in sorted(role_missing.items(), key=lambda x: -x[1])]),
                    use_container_width=True, hide_index=True)
                else:
                    st.success("All students have all required skills!")

    # ── TPO: EXPORT DATA ──────────────────────────────────────────────────────
    elif user["role"] == "tpo" and st.session_state.tpo_page == "exports":
        st.markdown('<div class="hero-title">📥 Export Data</div>', unsafe_allow_html=True)
        students = db_get_all_students()
        if students:
            rows = []
            for s in students:
                tier, _ = get_readiness_tier(s.get("readiness_score",0) or 0)
                rows.append({
                    "Name":            s.get("name") or s.get("user_name","—"),
                    "Username":        s.get("username","—"),
                    "Branch":          s.get("branch","—"),
                    "Year":            s.get("year","—"),
                    "Target Role":     s.get("target_role","—"),
                    "CGPA":            s.get("cgpa","—"),
                    "Readiness Score": s.get("readiness_score",0),
                    "Status":          tier,
                    "Internships":     s.get("internships",0),
                    "Projects":        s.get("projects",0),
                    "Certifications":  s.get("certifications",0),
                    "Backlogs":        s.get("backlogs",0),
                    "Skills":          ", ".join(s.get("skills",[]) or []),
                    "LinkedIn":        s.get("linkedin",""),
                    "GitHub":          s.get("github",""),
                    "Last Updated":    s.get("updated_at",""),
                })
            df = pd.DataFrame(rows)
            st.markdown('<div class="section-header">📊 Student Data Preview</div>', unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button("📥 Download as CSV", df.to_csv(index=False).encode("utf-8"),
                               "CampusEdge_students.csv", "text/csv", type="primary")
        else:
            st.info("No student data available to export.")

    # ── TPO: MY PROFILE ───────────────────────────────────────────────────────
    elif user["role"] == "tpo" and st.session_state.tpo_page == "tpo_profile":
        st.markdown('<div class="hero-title">👤 My Profile</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-sub">Manage your TPO account details and credentials</div>', unsafe_allow_html=True)

        saved = db_get_tpo_profile(user["id"])
        display_name = user.get("name", user["username"]) or user["username"]
        initials_url = f"https://ui-avatars.com/api/?name={display_name.replace(' ', '+')}&background=e91e8c&color=fff&size=128&bold=true&rounded=true"
        st.markdown(f'''
        <div style="display:flex;align-items:center;gap:1.5rem;background:#232131;border:1px solid #3d2f5a;border-radius:16px;padding:1.5rem 2rem;margin-bottom:1.5rem">
            <img src="{initials_url}" width="90" height="90"
                 style="border-radius:50%;border:3px solid #e91e8c;box-shadow:0 0 20px rgba(233,30,140,0.35)"/>
            <div>
                <div style="font-size:1.4rem;font-weight:700;color:#e8d5f5">{display_name}</div>
                <div style="color:#7a6e8a;font-size:0.85rem;margin-top:0.2rem">@{user["username"]}</div>
                <div style="display:inline-block;background:#2a2040;color:#e91e8c;font-size:0.72rem;padding:3px 12px;border-radius:20px;border:1px solid #e91e8c;margin-top:0.5rem;text-transform:uppercase;letter-spacing:0.08em">Training & Placement Officer</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["✏️ Edit Profile","🔑 Change Password"])
        with tab1:
            st.markdown('<div class="section-header">👤 Personal Details</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                tpo_name = st.text_input("Full Name *", value=user.get("name",""))
                desig    = st.text_input("Designation", value=saved.get("designation","") if saved else "", placeholder="e.g. Training & Placement Officer")
                dept     = st.text_input("Department",  value=saved.get("department","") if saved else "", placeholder="e.g. Department of Training & Placement")
            with col2:
                college = st.text_input("College / Institution", value=saved.get("college","") if saved else "", placeholder="e.g. ABC Engineering College")
                email   = st.text_input("Official Email",        value=saved.get("email","")   if saved else "", placeholder="tpo@college.edu.in")
                phone   = st.text_input("Phone Number",          value=saved.get("phone","")   if saved else "", placeholder="+91 98765 43210")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("💾 Save Profile", type="primary"):
                if not tpo_name.strip():
                    st.warning("Name is required.")
                else:
                    db_save_tpo_profile(user["id"], {
                        "name": tpo_name, "designation": desig,
                        "department": dept, "college": college,
                        "email": email, "phone": phone
                    })
                    st.session_state.user["name"] = tpo_name
                    st.success("✅ Profile saved successfully!")
                    st.rerun()

            st.markdown('<div class="section-header">👁️ Profile Preview</div>', unsafe_allow_html=True)
            col_a, col_b = st.columns(2)
            details = [
                ("🏷️ Designation",  saved.get("designation","—") if saved else "—"),
                ("🏛️ Department",   saved.get("department","—")  if saved else "—"),
                ("🎓 College",      saved.get("college","—")     if saved else "—"),
                ("📧 Email",        saved.get("email","—")       if saved else "—"),
                ("📞 Phone",        saved.get("phone","—")       if saved else "—"),
                ("🕐 Last Updated", saved.get("updated_at","—")[:16] if saved and saved.get("updated_at") else "—"),
            ]
            for i, (label, val) in enumerate(details):
                (col_a if i % 2 == 0 else col_b).markdown(f'''<div class="action-card" style="margin-bottom:0.5rem">
                    <div style="color:#7a6e8a;font-size:0.78rem">{label}</div>
                    <div style="color:#e8d5f5;font-weight:600;margin-top:0.2rem">{val}</div>
                </div>''', unsafe_allow_html=True)

        with tab2:
            st.markdown('<div class="section-header">🔑 Change Password</div>', unsafe_allow_html=True)
            st.markdown('<div class="peer-card">🔒 For security, enter your current password before setting a new one.</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            curr_pw = st.text_input("Current Password",      type="password", key="curr_pw")
            new_pw  = st.text_input("New Password",          type="password", key="new_pw", help="Minimum 6 characters")
            conf_pw = st.text_input("Confirm New Password",  type="password", key="conf_pw")
            if st.button("🔑 Update Password", type="primary"):
                if not all([curr_pw, new_pw, conf_pw]):
                    st.warning("Please fill in all password fields.")
                elif len(new_pw) < 6:
                    st.warning("New password must be at least 6 characters.")
                elif new_pw != conf_pw:
                    st.error("New passwords do not match.")
                else:
                    ok, msg = db_change_password(user["id"], curr_pw, new_pw)
                    if ok:
                        st.success(f"✅ {msg} Please log in again.")
                        st.session_state.user = None
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

except Exception as _page_err:
    render_error(_page_err, "the current page")

# ══════════════════════════════════════════════════════════════════════════════
# FLOATING AI CHATBOT (Gemini-powered, visible after login)
# ══════════════════════════════════════════════════════════════════════════════
FLOAT_SYSTEM_PROMPT = (
    "You are CareerEdge AI, a helpful placement assistant for Indian engineering students. "
    "Keep answers concise (under 150 words). Be friendly, practical and specific."
)

# Toggle button
col_float, _ = st.columns([1, 20])
with col_float:
    if st.button("💬", key="float_toggle", help="Open AI Assistant"):
        st.session_state.fchat_open = not st.session_state.fchat_open

if st.session_state.fchat_open:
    st.markdown("---")
    with st.container():
        st.markdown("### 🤖 Quick AI Assistant")
        st.caption("Powered by Google Gemini · Free to use")

        # Display history
        for msg in st.session_state.fchat_messages:
            if msg["role"] == "user":
                st.markdown(f'<div class="fchat-msg-user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="fchat-msg-ai">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

        # Process pending AI response
        if st.session_state.fchat_messages and st.session_state.fchat_messages[-1]["role"] == "user":
            with st.spinner("Thinking..."):
                try:
                    gemini_key = st.secrets.get("GEMINI_API_KEY", "")
                    gemini_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={gemini_key}"
                    contents   = [
                        {"role":"user",  "parts":[{"text": FLOAT_SYSTEM_PROMPT}]},
                        {"role":"model", "parts":[{"text": "Got it, I'll keep answers short and helpful."}]},
                    ]
                    for m in st.session_state.fchat_messages[-6:]:
                        role = "user" if m["role"] == "user" else "model"
                        contents.append({"role": role, "parts":[{"text": m["content"]}]})
                    payload = json.dumps({
                        "contents": contents,
                        "generationConfig": {"maxOutputTokens": 512, "temperature": 0.7}
                    }).encode("utf-8")
                    req = urllib.request.Request(gemini_url, data=payload,
                                                 headers={"Content-Type":"application/json"}, method="POST")
                    with urllib.request.urlopen(req, timeout=20) as resp:
                        result = json.loads(resp.read().decode("utf-8"))
                    reply = result["candidates"][0]["content"]["parts"][0]["text"]
                    st.session_state.fchat_messages.append({"role":"assistant","content":reply})
                    st.rerun()
                except Exception as fe:
                    st.error(f"AI error: {str(fe)[:120]}")

        # Input
        fc_col1, fc_col2 = st.columns([5, 1])
        with fc_col1:
            fc_input = st.text_input("Quick question", label_visibility="collapsed",
                                     placeholder="Ask anything...", key="fchat_input")
        with fc_col2:
            if st.button("Send", key="fchat_send", type="primary"):
                if fc_input.strip():
                    st.session_state.fchat_messages.append({"role":"user","content":fc_input.strip()})
                    st.rerun()

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🗑️ Clear", key="fchat_clear", type="secondary"):
                st.session_state.fchat_messages = []
                st.rerun()
        with c2:
            if st.button("✖ Close", key="fchat_close", type="secondary"):
                st.session_state.fchat_open = False
                st.rerun()