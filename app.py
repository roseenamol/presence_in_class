import streamlit as st
import subprocess
import os
import time
from datetime import datetime
from pathlib import Path

st.set_page_config(
    page_title="SmartAttend · AI Attendance",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── GLOBAL CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #0d1117; }
section[data-testid="stSidebar"] { background: #0d1117; border-right: 1px solid #1e2530; }
section[data-testid="stSidebar"] > div { padding-top: 1.5rem; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 4rem; max-width: 1100px; }

.brand { display: flex; align-items: center; gap: 10px; padding: 0 1rem 1.5rem; border-bottom: 1px solid #1e2530; margin-bottom: 1.5rem; }
.brand-icon { width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg, #00c9a7, #00a3d9); display: flex; align-items: center; justify-content: center; font-size: 18px; }
.brand-text { font-size: 15px; font-weight: 600; color: #e6edf3; letter-spacing: -0.02em; }
.brand-sub  { font-size: 11px; color: #6e7681; letter-spacing: 0.04em; text-transform: uppercase; }

.page-header { margin-bottom: 2rem; padding-bottom: 1.25rem; border-bottom: 1px solid #1e2530; }
.page-title { font-size: 26px; font-weight: 600; color: #e6edf3; letter-spacing: -0.03em; margin-bottom: 4px; }
.page-subtitle { font-size: 14px; color: #6e7681; }

.card { background: #161b22; border: 1px solid #1e2530; border-radius: 12px; padding: 1.25rem 1.5rem; margin-bottom: 1rem; }
.card-title { font-size: 11px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: #6e7681; margin-bottom: 14px; }

.stat-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 1.5rem; }
.stat-card { background: #161b22; border: 1px solid #1e2530; border-radius: 12px; padding: 1.1rem 1.25rem; }
.stat-num { font-size: 28px; font-weight: 600; color: #e6edf3; letter-spacing: -0.04em; }
.stat-label { font-size: 12px; color: #6e7681; margin-top: 2px; }
.stat-accent { color: #00c9a7; }
.stat-warn   { color: #f0883e; }
.stat-danger { color: #f85149; }

.workflow { display: flex; gap: 0; margin-bottom: 1.5rem; background: #161b22; border: 1px solid #1e2530; border-radius: 12px; overflow: hidden; }
.wf-step { flex: 1; padding: 1rem 0.75rem; text-align: center; border-right: 1px solid #1e2530; position: relative; }
.wf-step:last-child { border-right: none; }
.wf-num { width: 28px; height: 28px; border-radius: 50%; background: #1e2530; color: #6e7681; font-size: 12px; font-weight: 600; display: flex; align-items: center; justify-content: center; margin: 0 auto 8px; }
.wf-num.done { background: rgba(0,201,167,0.15); color: #00c9a7; }
.wf-num.curr { background: rgba(0,163,217,0.15); color: #00a3d9; box-shadow: 0 0 0 4px rgba(0,163,217,0.08); }
.wf-label { font-size: 11px; color: #8b949e; font-weight: 500; }
.wf-label.curr { color: #e6edf3; }

.student-list { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 1rem; }
.student-chip { display: flex; align-items: center; gap: 8px; background: #0d1117; border: 1px solid #1e2530; border-radius: 8px; padding: 6px 12px; font-size: 13px; color: #e6edf3; }
.chip-avatar { width: 22px; height: 22px; border-radius: 50%; background: linear-gradient(135deg, #00c9a7, #00a3d9); font-size: 10px; font-weight: 600; color: #0d1117; display: flex; align-items: center; justify-content: center; }
.chip-dot { width: 6px; height: 6px; border-radius: 50%; background: #00c9a7; }

.upload-hint { background: rgba(0,201,167,0.04); border: 1.5px dashed rgba(0,201,167,0.25); border-radius: 10px; padding: 1.25rem; text-align: center; color: #6e7681; font-size: 13px; margin-bottom: 0.5rem; }
.upload-hint strong { color: #00c9a7; }

.att-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.att-table th { text-align: left; padding: 8px 12px; color: #6e7681; font-size: 11px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; border-bottom: 1px solid #1e2530; }
.att-table td { padding: 10px 12px; border-bottom: 1px solid #1e2530; color: #e6edf3; }
.att-table tr:last-child td { border-bottom: none; }
.badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
.badge-present  { background: rgba(0,201,167,0.12);  color: #00c9a7; }
.badge-absent   { background: rgba(248,81,73,0.12);   color: #f85149; }
.badge-late     { background: rgba(240,136,62,0.12);  color: #f0883e; }
.badge-approved { background: rgba(0,201,167,0.12);  color: #00c9a7; }
.badge-rejected { background: rgba(248,81,73,0.12);   color: #f85149; }
.badge-pending  { background: rgba(240,136,62,0.12);  color: #f0883e; }

.req-card { background: #0d1117; border: 1px solid #1e2530; border-radius: 10px; padding: 1rem 1.25rem; margin-bottom: 0.75rem; }
.req-card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem; }
.req-name { font-size: 15px; font-weight: 600; color: #e6edf3; }
.req-meta { font-size: 12px; color: #6e7681; }

.stage-bar { display: flex; align-items: center; gap: 0; margin: 0.75rem 0 0.5rem; }
.stage-node { display: flex; flex-direction: column; align-items: center; flex: 1; }
.stage-circle { width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 600; }
.sc-done    { background: rgba(0,201,167,0.2); color: #00c9a7; border: 1px solid rgba(0,201,167,0.4); }
.sc-curr    { background: rgba(0,163,217,0.2); color: #00a3d9; border: 1px solid rgba(0,163,217,0.5); }
.sc-pending { background: #1e2530; color: #6e7681; border: 1px solid #2d3748; }
.sc-reject  { background: rgba(248,81,73,0.15); color: #f85149; border: 1px solid rgba(248,81,73,0.4); }
.stage-line { flex: 1; height: 1px; background: #1e2530; margin-bottom: 18px; }
.stage-label { font-size: 10px; color: #6e7681; margin-top: 4px; text-align: center; }

.login-wrap { max-width: 420px; margin: 4rem auto 0; }
.login-card { background: #161b22; border: 1px solid #1e2530; border-radius: 16px; padding: 2.5rem 2rem; }
.login-brand { text-align: center; margin-bottom: 2rem; }
.login-icon { font-size: 40px; margin-bottom: 0.5rem; }
.login-title { font-size: 22px; font-weight: 600; color: #e6edf3; letter-spacing: -0.03em; }
.login-sub { font-size: 13px; color: #6e7681; margin-top: 4px; }
.role-pill { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; background: rgba(0,201,167,0.12); color: #00c9a7; margin-top: 6px; }

.stButton > button { background: linear-gradient(135deg, #00c9a7, #00a3d9) !important; color: #0d1117 !important; font-weight: 600 !important; border: none !important; border-radius: 8px !important; padding: 0.5rem 1.5rem !important; font-size: 14px !important; font-family: 'DM Sans', sans-serif !important; transition: opacity 0.15s !important; }
.stButton > button:hover { opacity: 0.88 !important; }
.stTextInput input, .stSelectbox select { background: #0d1117 !important; border: 1px solid #1e2530 !important; border-radius: 8px !important; color: #e6edf3 !important; font-family: 'DM Sans', sans-serif !important; }
.stTextInput label, .stSelectbox label, .stFileUploader label { color: #8b949e !important; font-size: 13px !important; font-family: 'DM Sans', sans-serif !important; }
.stCodeBlock code { font-family: 'DM Mono', monospace !important; font-size: 12px !important; background: #0d1117 !important; color: #00c9a7 !important; }
.stSpinner > div { border-top-color: #00c9a7 !important; }
.stSuccess { background: rgba(0,201,167,0.08) !important; border-color: rgba(0,201,167,0.3) !important; color: #00c9a7 !important; }
.stError   { background: rgba(248,81,73,0.08)  !important; border-color: rgba(248,81,73,0.3)  !important; }
.stWarning { background: rgba(240,136,62,0.08) !important; border-color: rgba(240,136,62,0.3) !important; }
.stProgress > div > div > div { background: linear-gradient(90deg, #00c9a7, #00a3d9) !important; }
hr { border-color: #1e2530 !important; }
.stRadio > label { color: #8b949e !important; font-size: 13px !important; }
.stRadio > div   { gap: 4px !important; }
.stRadio [data-testid="stMarkdownContainer"] p { font-size: 14px !important; }
</style>
""", unsafe_allow_html=True)


# ─── SESSION STATE INIT ────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = ""
if "late_requests" not in st.session_state:
    st.session_state.late_requests = []
if "req_counter" not in st.session_state:
    st.session_state.req_counter = 1


# ─── USER CREDENTIALS ─────────────────────────────────────────────────────────
USERS = {
    "faculty":  {"password": "faculty123", "role": "faculty",  "display": "Faculty / Teacher"},
    "hod":      {"password": "hod123",     "role": "hod",      "display": "Head of Department"},
    "admin":    {"password": "admin123",   "role": "admin",    "display": "Administrator"},
}


# ─── HELPERS ──────────────────────────────────────────────────────────────────
def get_enrolled_students():
    folder = Path("student_videos")
    if not folder.exists():
        return []
    return [f.stem for f in folder.iterdir() if f.suffix in (".mp4", ".avi", ".mov")]


def student_initials(name):
    parts = name.strip().split()
    return (parts[0][0] + (parts[1][0] if len(parts) > 1 else parts[0][-1])).upper()


def model_is_trained():
    return Path("faces.index").exists() and Path("labels.pkl").exists()


def create_late_request(student_name, time_detected, reason=""):
    req_id = f"LR-{st.session_state.req_counter:04d}"
    st.session_state.req_counter += 1
    st.session_state.late_requests.append({
        "id": req_id,
        "student": student_name,
        "time_detected": time_detected,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "reason": reason,
        "stage": "faculty",
        "faculty_action": None, "faculty_reason": "", "faculty_at": "",
        "hod_action":     None, "hod_reason":     "", "hod_at":     "",
        "admin_action":   None, "admin_reason":   "", "admin_at":   "",
    })
    return req_id


def pending_count_for_role(role):
    return sum(1 for r in st.session_state.late_requests if r["stage"] == role)


def stage_icon(req, stage_key):
    action = req.get(f"{stage_key}_action")
    if action == "approved":
        return "sc-done"
    if action == "rejected":
        return "sc-reject"
    if req["stage"] == stage_key:
        return "sc-curr"
    stage_order = ["faculty", "hod", "admin"]
    current_idx = stage_order.index(req["stage"]) if req["stage"] in stage_order else 3
    stage_idx = stage_order.index(stage_key)
    if stage_idx < current_idx:
        return "sc-done"
    return "sc-pending"


def stage_label_text(req, stage_key):
    action = req.get(f"{stage_key}_action")
    if action:
        return action.capitalize()
    if req["stage"] == stage_key:
        return "In review"
    stage_order = ["faculty", "hod", "admin"]
    current_idx = stage_order.index(req["stage"]) if req["stage"] in stage_order else 3
    stage_idx = stage_order.index(stage_key)
    return "Done" if stage_idx < current_idx else "Waiting"


def render_stage_bar(req):
    stages = [("faculty", "Faculty"), ("hod", "HOD"), ("admin", "Admin")]
    parts = []
    for i, (key, label) in enumerate(stages):
        circle_cls = stage_icon(req, key)
        lbl_text = stage_label_text(req, key)
        if "done" in circle_cls:
            icon_text = "✓"
        elif "reject" in circle_cls:
            icon_text = "✗"
        elif "curr" in circle_cls:
            icon_text = "▶"
        else:
            icon_text = "–"
        parts.append(f"""
        <div class="stage-node">
          <div class="stage-circle {circle_cls}">{icon_text}</div>
          <div class="stage-label">{label}<br><span style="color:#4d5561;">{lbl_text}</span></div>
        </div>""")
        if i < len(stages) - 1:
            parts.append('<div class="stage-line"></div>')
    return '<div class="stage-bar">' + "".join(parts) + "</div>"


def parse_attendance_output(raw, enrolled):
    import re
    present_names = {}
    late_names = {}
    for line in raw.splitlines():
        line = line.strip()
        m = re.match(r'\[(\d{2}:\d{2}:\d{2})\]\s+PRESENT:\s+(.+)', line, re.IGNORECASE)
        if m:
            timestamp, name = m.group(1), m.group(2).strip()
            present_names[name.lower()] = {"name": name, "time": timestamp}
            continue
        m = re.match(r'\[(\d{2}:\d{2}:\d{2})\]\s+LATE:\s+(.+)', line, re.IGNORECASE)
        if m:
            timestamp, name = m.group(1), m.group(2).strip()
            late_names[name.lower()] = {"name": name, "time": timestamp}
    rows = []
    for student in enrolled:
        key = student.lower()
        if key in late_names:
            rows.append({"name": late_names[key]["name"], "status": "Late", "time": late_names[key]["time"]})
        elif key in present_names:
            rows.append({"name": present_names[key]["name"], "status": "Present", "time": present_names[key]["time"]})
        else:
            rows.append({"name": student, "status": "Absent", "time": "—"})
    for key, val in {**present_names, **late_names}.items():
        if not any(r["name"].lower() == key for r in rows):
            status = "Late" if key in late_names else "Present"
            rows.append({"name": val["name"], "status": status, "time": val["time"]})
    return rows


# ─── SHARED: APPROVAL PANEL ───────────────────────────────────────────────────
def render_approval_panel(role):
    role_requests = [r for r in st.session_state.late_requests if r["stage"] == role]
    if not role_requests:
        st.markdown(
            f'<div style="padding:1.5rem;text-align:center;color:#6e7681;font-size:13px;'
            f'background:#0d1117;border:1px solid #1e2530;border-radius:10px;">'
            f'No requests pending {role.upper()} review right now.</div>',
            unsafe_allow_html=True
        )
        return

    for req in role_requests:
        st.markdown(f"""
        <div class="req-card">
            <div class="req-card-header">
                <div>
                    <span class="req-name">{req['student']}</span>
                    <span style="font-size:11px;color:#6e7681;margin-left:10px;">{req['id']}</span>
                </div>
                <span class="badge badge-pending">Pending {role.upper()}</span>
            </div>
            <div class="req-meta">
                📅 {req['date']} &nbsp;·&nbsp; 🕐 Detected at {req['time_detected']}
                {f"&nbsp;·&nbsp; 📝 {req['reason']}" if req['reason'] else ""}
            </div>
            {render_stage_bar(req)}
        </div>
        """, unsafe_allow_html=True)

        col_a, col_r, col_reason = st.columns([1, 1, 3])
        with col_a:
            approve_clicked = st.button("✓ Approve", key=f"approve_{req['id']}_{role}")
        with col_r:
            reject_clicked = st.button("✗ Reject", key=f"reject_{req['id']}_{role}")
        with col_reason:
            reviewer_note = st.text_input(
                "Note (optional)",
                key=f"note_{req['id']}_{role}",
                placeholder="Add a comment…",
                label_visibility="collapsed"
            )

        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        if approve_clicked:
            req[f"{role}_action"] = "approved"
            req[f"{role}_reason"] = reviewer_note
            req[f"{role}_at"] = now
            next_stage = {"faculty": "hod", "hod": "admin", "admin": "approved"}
            req["stage"] = next_stage[role]
            st.rerun()

        if reject_clicked:
            req[f"{role}_action"] = "rejected"
            req[f"{role}_reason"] = reviewer_note
            req[f"{role}_at"] = now
            req["stage"] = "rejected"
            st.rerun()

        st.markdown("<hr style='margin:0.25rem 0;'>", unsafe_allow_html=True)


# ─── WORKFLOW BAR ─────────────────────────────────────────────────────────────
def workflow_bar(active):
    steps = ["Enroll", "Train", "Upload Video", "Attendance"]
    enrolled = len(get_enrolled_students()) > 0
    trained = model_is_trained()
    done_map = [enrolled, trained, False, False]
    html = '<div class="workflow">'
    for i, (s, done) in enumerate(zip(steps, done_map)):
        num_cls = "done" if done else ("curr" if i + 1 == active else "")
        lbl_cls = "curr" if i + 1 == active else ""
        icon = "✓" if done else str(i + 1)
        html += f"""
        <div class="wf-step">
            <div class="wf-num {num_cls}">{icon}</div>
            <div class="wf-label {lbl_cls}">{s}</div>
        </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


# ─── LOGIN PAGE ───────────────────────────────────────────────────────────────
def login_page():
    st.markdown("""
    <div class="login-wrap">
        <div class="login-card">
            <div class="login-brand">
                <div class="login-icon">🎓</div>
                <div class="login-title">SmartAttend</div>
                <div class="login-sub">AI-powered Face Recognition Attendance</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

        if st.button("Sign In →"):
            if username in USERS and USERS[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.role = USERS[username]["role"]
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid username or password. Please try again.")

        st.markdown("""
        <div style="margin-top:1.5rem;padding:1rem;background:#0d1117;border:1px solid #1e2530;border-radius:10px;">
            <div style="font-size:11px;color:#6e7681;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:10px;">
                Demo Credentials
            </div>
            <div style="font-size:12px;color:#8b949e;line-height:2;">
                👨‍🏫 Faculty &nbsp;→&nbsp; <code style="color:#00c9a7;">faculty</code> / <code style="color:#00c9a7;">faculty123</code><br>
                🏛 HOD &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;→&nbsp; <code style="color:#00c9a7;">hod</code> / <code style="color:#00c9a7;">hod123</code><br>
                ⚙️ Admin &nbsp;&nbsp;&nbsp;→&nbsp; <code style="color:#00c9a7;">admin</code> / <code style="color:#00c9a7;">admin123</code>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
def sidebar():
    role = st.session_state.role
    username = st.session_state.username

    st.markdown("""
    <div class="brand">
        <div class="brand-icon">🎓</div>
        <div>
            <div class="brand-text">SmartAttend</div>
            <div class="brand-sub">AI · Face Recognition</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    enrolled = get_enrolled_students()
    trained = model_is_trained()
    pending_f = pending_count_for_role("faculty")
    pending_h = pending_count_for_role("hod")
    pending_a = pending_count_for_role("admin")

    # Role-specific menus — NO HTML in radio labels (st.radio does not render HTML)
    if role == "faculty":
        late_label = f"🕐  Late Approval ({pending_f})" if pending_f else "🕐  Late Approval"
        options = [
            "🏠  Home",
            "👤  Enroll Student",
            "🧠  Train Model",
            "✅  Take Attendance",
            late_label,
        ]
    elif role == "hod":
        hod_label = f"🏛  HOD Approvals ({pending_h})" if pending_h else "🏛  HOD Approvals"
        options = [
            "🏠  Home",
            hod_label,
            "📋  All Requests",
        ]
    elif role == "admin":
        admin_label = f"⚙️  Admin Approvals ({pending_a})" if pending_a else "⚙️  Admin Approvals"
        options = [
            "🏠  Home",
            admin_label,
            "📋  All Requests",
        ]
    else:
        options = ["🏠  Home"]

    choice = st.radio("", options, label_visibility="collapsed")

    st.markdown("<hr style='margin:1.5rem 0;'>", unsafe_allow_html=True)

    # System status
    st.markdown(f"""
    <div style="padding:0 0.5rem;">
        <div style="font-size:11px;color:#6e7681;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:10px;">System Status</div>
        <div style="display:flex;justify-content:space-between;font-size:12px;color:#8b949e;margin-bottom:6px;">
            <span>Students enrolled</span>
            <span style="color:{'#00c9a7' if enrolled else '#f85149'};font-weight:600;">{len(enrolled)}</span>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:12px;color:#8b949e;margin-bottom:6px;">
            <span>Model trained</span>
            <span style="color:{'#00c9a7' if trained else '#f85149'};font-weight:600;">{'Yes' if trained else 'No'}</span>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:12px;color:#8b949e;margin-bottom:6px;">
            <span>Pending (Faculty)</span>
            <span style="color:{'#f0883e' if pending_f else '#00c9a7'};font-weight:600;">{pending_f}</span>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:12px;color:#8b949e;margin-bottom:6px;">
            <span>Pending (HOD)</span>
            <span style="color:{'#f0883e' if pending_h else '#00c9a7'};font-weight:600;">{pending_h}</span>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:12px;color:#8b949e;">
            <span>Pending (Admin)</span>
            <span style="color:{'#f0883e' if pending_a else '#00c9a7'};font-weight:600;">{pending_a}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='margin:1.5rem 0;'>", unsafe_allow_html=True)

    # Logged-in user info
    role_labels = {"faculty": "Faculty / Teacher", "hod": "Head of Department", "admin": "Administrator"}
    st.markdown(f"""
    <div style="padding:0 0.5rem;margin-bottom:1rem;">
        <div style="font-size:11px;color:#6e7681;margin-bottom:4px;">Logged in as</div>
        <div style="font-size:14px;font-weight:600;color:#e6edf3;">{username}</div>
        <div style="font-size:11px;color:#00c9a7;margin-top:2px;">{role_labels.get(role, role)}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Logout →"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.username = ""
        st.rerun()

    # Parse page name — strip emoji prefix and trailing count like "(2)"
    import re as _re
    raw = choice.split("  ", 1)[-1].strip()
    raw = _re.sub(r'\s*\(\d+\)\s*$', '', raw).strip()
    return raw


# ─── PAGE: HOME ───────────────────────────────────────────────────────────────
def page_home():
    role = st.session_state.role
    role_labels = {"faculty": "Faculty / Teacher", "hod": "Head of Department", "admin": "Administrator"}

    st.markdown(f"""
    <div class="page-header">
        <div class="page-title">Welcome to SmartAttend</div>
        <div class="page-subtitle">
            AI-powered face recognition attendance · YOLOv8 + FAISS &nbsp;·&nbsp;
            Signed in as <span style="color:#00c9a7;">{role_labels.get(role, role)}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    enrolled = get_enrolled_students()
    trained = model_is_trained()
    pending_total = (
        pending_count_for_role("faculty") +
        pending_count_for_role("hod") +
        pending_count_for_role("admin")
    )

    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-card">
            <div class="stat-num stat-accent">{len(enrolled)}</div>
            <div class="stat-label">Students Enrolled</div>
        </div>
        <div class="stat-card">
            <div class="stat-num {'stat-accent' if trained else 'stat-danger'}">{'Ready' if trained else 'Needed'}</div>
            <div class="stat-label">Model Status</div>
        </div>
        <div class="stat-card">
            <div class="stat-num {'stat-warn' if pending_total else 'stat-accent'}">{pending_total}</div>
            <div class="stat-label">Pending Approvals</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if role == "faculty":
        workflow_bar(1 if not enrolled else (2 if not trained else 3))

    if enrolled:
        chips = "".join(
            f'<div class="student-chip"><div class="chip-avatar">{student_initials(s)}</div>{s}<div class="chip-dot"></div></div>'
            for s in enrolled
        )
        st.markdown(
            f'<div class="card"><div class="card-title">Enrolled Students</div>'
            f'<div class="student-list">{chips}</div></div>',
            unsafe_allow_html=True
        )

    st.markdown("""
    <div class="card">
        <div class="card-title">System Workflow</div>
        <table style="width:100%;border-collapse:collapse;font-size:13px;">
            <tr>
                <td style="padding:10px 12px;color:#6e7681;border-bottom:1px solid #1e2530;width:28px;">01</td>
                <td style="padding:10px 12px;color:#e6edf3;font-weight:500;border-bottom:1px solid #1e2530;">Enroll Students</td>
                <td style="padding:10px 12px;color:#8b949e;border-bottom:1px solid #1e2530;">Faculty uploads a short video per student</td>
            </tr>
            <tr>
                <td style="padding:10px 12px;color:#6e7681;border-bottom:1px solid #1e2530;">02</td>
                <td style="padding:10px 12px;color:#e6edf3;font-weight:500;border-bottom:1px solid #1e2530;">Train the Model</td>
                <td style="padding:10px 12px;color:#8b949e;border-bottom:1px solid #1e2530;">Build FAISS index from enrolled embeddings</td>
            </tr>
            <tr>
                <td style="padding:10px 12px;color:#6e7681;border-bottom:1px solid #1e2530;">03</td>
                <td style="padding:10px 12px;color:#e6edf3;font-weight:500;border-bottom:1px solid #1e2530;">Take Attendance</td>
                <td style="padding:10px 12px;color:#8b949e;border-bottom:1px solid #1e2530;">YOLOv8 detects faces, FAISS matches identities</td>
            </tr>
            <tr>
                <td style="padding:10px 12px;color:#6e7681;border-bottom:1px solid #1e2530;">04</td>
                <td style="padding:10px 12px;color:#e6edf3;font-weight:500;border-bottom:1px solid #1e2530;">Faculty Reviews Late</td>
                <td style="padding:10px 12px;color:#8b949e;border-bottom:1px solid #1e2530;">Faculty approves or rejects late requests first</td>
            </tr>
            <tr>
                <td style="padding:10px 12px;color:#6e7681;border-bottom:1px solid #1e2530;">05</td>
                <td style="padding:10px 12px;color:#e6edf3;font-weight:500;border-bottom:1px solid #1e2530;">HOD Reviews</td>
                <td style="padding:10px 12px;color:#8b949e;border-bottom:1px solid #1e2530;">HOD gives second-level approval</td>
            </tr>
            <tr>
                <td style="padding:10px 12px;color:#6e7681;">06</td>
                <td style="padding:10px 12px;color:#e6edf3;font-weight:500;">Admin Final Approval</td>
                <td style="padding:10px 12px;color:#8b949e;">Admin gives the final sign-off</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)


# ─── PAGE: ENROLL ─────────────────────────────────────────────────────────────
def page_enroll():
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Enroll Student</div>
        <div class="page-subtitle">Upload a face video to extract and store embeddings</div>
    </div>
    """, unsafe_allow_html=True)

    workflow_bar(1)
    enrolled = get_enrolled_students()

    if enrolled:
        chips = "".join(
            f'<div class="student-chip"><div class="chip-avatar">{student_initials(s)}</div>{s}<div class="chip-dot"></div></div>'
            for s in enrolled
        )
        st.markdown(
            f'<div class="card"><div class="card-title">Already Enrolled ({len(enrolled)})</div>'
            f'<div class="student-list">{chips}</div></div>',
            unsafe_allow_html=True
        )

    st.markdown('<div class="card-title" style="margin-bottom:8px;">Add New Student</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1], gap="medium")
    with col1:
        student_name = st.text_input("Full Name", placeholder="e.g. Roseena")
    with col2:
        st.markdown('<div style="font-size:12px;color:#6e7681;margin-top:36px;">💡 Use the same name every time</div>', unsafe_allow_html=True)

    st.markdown('<div class="upload-hint"><strong>Upload a short video · 5–15 seconds</strong><br>Face clearly visible · Good lighting · Formats: .mp4 · .avi · .mov</div>', unsafe_allow_html=True)
    uploaded_video = st.file_uploader("Choose video file", type=["mp4", "avi", "mov"], label_visibility="collapsed")

    if uploaded_video:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:10px;padding:10px 14px;background:#0d1117;'
            f'border:1px solid #1e2530;border-radius:8px;margin-bottom:1rem;font-size:13px;color:#8b949e;">'
            f'<span style="color:#00c9a7;">▶</span>'
            f'<span style="color:#e6edf3;font-weight:500;">{uploaded_video.name}</span>'
            f'<span style="margin-left:auto;">{uploaded_video.size // 1024} KB</span></div>',
            unsafe_allow_html=True
        )

    if st.button("Enroll Student →"):
        if student_name and uploaded_video:
            os.makedirs("student_videos", exist_ok=True)
            video_path = os.path.join("student_videos", f"{student_name}.mp4")
            with open(video_path, "wb") as f:
                f.write(uploaded_video.read())
            st.success(f"✓ Video saved for **{student_name}**")
            with st.spinner(f"Running enrollment.py for {student_name}…"):
                result = subprocess.run(["python", "enrollment.py"], capture_output=True, text=True)
            if result.returncode == 0:
                st.success(f"✓ {student_name} enrolled successfully! Re-train the model to include them.")
            else:
                st.error("Enrollment script failed — check the output below")
            if result.stdout:
                with st.expander("Script output", expanded=False):
                    st.code(result.stdout, language="bash")
            if result.stderr:
                with st.expander("Errors", expanded=True):
                    st.code(result.stderr, language="bash")
        else:
            st.warning("Please enter a student name and upload a video.")


# ─── PAGE: TRAIN ──────────────────────────────────────────────────────────────
def page_train():
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Train Face Model</div>
        <div class="page-subtitle">Build the FAISS index from all enrolled student embeddings</div>
    </div>
    """, unsafe_allow_html=True)

    workflow_bar(2)
    enrolled = get_enrolled_students()
    trained = model_is_trained()

    col1, col2, col3 = st.columns(3)
    with col1:
        color = "stat-accent" if enrolled else "stat-danger"
        st.markdown(
            f'<div class="stat-card"><div class="stat-num {color}">{len(enrolled)}</div>'
            f'<div class="stat-label">Students ready to train</div></div>',
            unsafe_allow_html=True
        )
    with col2:
        idx_size = f"{Path('faces.index').stat().st_size // 1024} KB" if Path("faces.index").exists() else ""
        color2 = "stat-accent" if trained else "stat-danger"
        st.markdown(
            f'<div class="stat-card"><div class="stat-num {color2}">{"Built" if trained else "None"}</div>'
            f'<div class="stat-label">FAISS index {idx_size}</div></div>',
            unsafe_allow_html=True
        )
    with col3:
        mtime = ""
        if Path("faces.index").exists():
            mtime = datetime.fromtimestamp(Path("faces.index").stat().st_mtime).strftime("%b %d, %H:%M")
        st.markdown(
            f'<div class="stat-card"><div class="stat-num" style="font-size:16px;padding-top:4px;">'
            f'{mtime if mtime else "—"}</div><div class="stat-label">Last trained</div></div>',
            unsafe_allow_html=True
        )

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    if not enrolled:
        st.markdown(
            '<div style="padding:1.25rem;background:rgba(248,81,73,0.08);border:1px solid rgba(248,81,73,0.2);'
            'border-radius:10px;color:#f85149;font-size:14px;">⚠ No students enrolled yet. Go to <b>Enroll Student</b> first.</div>',
            unsafe_allow_html=True
        )
        return

    st.markdown(
        '<div class="card"><div class="card-title">What this does</div>'
        '<div style="font-size:13px;color:#8b949e;line-height:1.7;">training.py reads all face embeddings, '
        'builds a FAISS L2 index, and saves <code style="color:#00c9a7;">faces.index</code> and '
        '<code style="color:#00c9a7;">labels.pkl</code> to disk.</div></div>',
        unsafe_allow_html=True
    )

    if st.button("Start Training →"):
        progress = st.progress(0, text="Initialising…")
        with st.spinner("Building FAISS index…"):
            result = subprocess.run(["python", "training.py"], capture_output=True, text=True)
        progress.progress(100, text="Done")
        time.sleep(0.4)
        progress.empty()
        if result.returncode == 0:
            st.success("✓ Model trained successfully!")
        else:
            st.error("Training failed — see output below")
        if result.stdout:
            with st.expander("Script output", expanded=False):
                st.code(result.stdout, language="bash")
        if result.stderr:
            with st.expander("Errors", expanded=True):
                st.code(result.stderr, language="bash")


# ─── PAGE: ATTENDANCE ─────────────────────────────────────────────────────────
def page_attendance():
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Take Attendance</div>
        <div class="page-subtitle">Upload a classroom recording and let AI mark attendance</div>
    </div>
    """, unsafe_allow_html=True)

    workflow_bar(4)

    if not model_is_trained():
        st.markdown(
            '<div style="padding:1.25rem;background:rgba(248,81,73,0.08);border:1px solid rgba(248,81,73,0.2);'
            'border-radius:10px;color:#f85149;font-size:14px;margin-bottom:1rem;">'
            '⚠ Model not trained yet. Go to <b>Train Model</b> first.</div>',
            unsafe_allow_html=True
        )

    enrolled = get_enrolled_students()
    if enrolled:
        chips = "".join(
            f'<div class="student-chip"><div class="chip-avatar">{student_initials(s)}</div>{s}</div>'
            for s in enrolled
        )
        st.markdown(
            f'<div class="card"><div class="card-title">Checking against {len(enrolled)} enrolled students</div>'
            f'<div class="student-list">{chips}</div></div>',
            unsafe_allow_html=True
        )

    st.markdown('<div class="upload-hint"><strong>Upload Classroom Video</strong><br>Any lecture or session recording · Formats: .mp4 · .avi · .mov</div>', unsafe_allow_html=True)
    attendance_video = st.file_uploader("Classroom video", type=["mp4", "avi", "mov"], label_visibility="collapsed")

    if attendance_video:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:10px;padding:10px 14px;background:#0d1117;'
            f'border:1px solid #1e2530;border-radius:8px;margin:0.75rem 0;font-size:13px;color:#8b949e;">'
            f'<span style="color:#00c9a7;">▶</span>'
            f'<span style="color:#e6edf3;font-weight:500;">{attendance_video.name}</span>'
            f'<span style="margin-left:auto;">{attendance_video.size // 1024} KB</span></div>',
            unsafe_allow_html=True
        )

    # Manual late flag
    st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
    with st.expander("➕ Manually flag a student as late", expanded=False):
        st.markdown(
            '<div style="font-size:13px;color:#8b949e;margin-bottom:0.75rem;">'
            "Use this if the video didn't capture a late-arriving student. "
            "Their request will enter the approval workflow immediately.</div>",
            unsafe_allow_html=True
        )
        mc1, mc2, mc3 = st.columns([2, 1, 1])
        with mc1:
            manual_name = st.selectbox(
                "Student",
                options=enrolled if enrolled else ["No students enrolled"],
                key="manual_late_name"
            )
        with mc2:
            manual_time = st.text_input("Arrival time", placeholder="e.g. 09:15:00", key="manual_late_time")
        with mc3:
            manual_reason = st.text_input("Reason (optional)", placeholder="e.g. traffic", key="manual_late_reason")

        if st.button("Flag as Late →", key="manual_late_btn"):
            if manual_name and manual_name != "No students enrolled":
                t = manual_time or datetime.now().strftime("%H:%M:%S")
                rid = create_late_request(manual_name, t, manual_reason)
                st.success(f"✓ Late request {rid} created for **{manual_name}** — see 🕐 Late Approval to process it.")
            else:
                st.warning("Select a student first.")

    if st.button("Start Attendance →"):
        if attendance_video:
            with open("row.mp4", "wb") as f:
                f.write(attendance_video.read())
            st.success("✓ Classroom video saved")

            progress = st.progress(0, text="Starting face detection…")
            status_text = st.empty()
            stages = [
                (20, "Loading FAISS index and labels…"),
                (45, "YOLOv8 detecting faces in frames…"),
                (70, "Extracting face embeddings…"),
                (90, "Matching against enrolled faces…"),
                (100, "Saving attendance results…"),
            ]
            proc = subprocess.Popen(
                ["python", "attendance.py"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            for pct, msg in stages:
                time.sleep(0.4)
                progress.progress(pct, text=msg)
                status_text.markdown(
                    f'<div style="font-size:12px;color:#6e7681;">{msg}</div>',
                    unsafe_allow_html=True
                )
            stdout, stderr = proc.communicate()
            progress.empty()
            status_text.empty()

            if proc.returncode == 0:
                st.success("✓ Attendance completed!")
                rows = parse_attendance_output(stdout, enrolled)

                existing_names = {r["student"].lower() for r in st.session_state.late_requests}
                for row in rows:
                    if row["status"] == "Late" and row["name"].lower() not in existing_names:
                        create_late_request(row["name"], row["time"], "detected late by system")

                if rows:
                    present = sum(1 for r in rows if r["status"] == "Present")
                    late = sum(1 for r in rows if r["status"] == "Late")
                    absent = sum(1 for r in rows if r["status"] == "Absent")
                    total = len(rows)
                    rate = f"{present / total * 100:.0f}%" if total else "—"

                    st.markdown(f"""
                    <div class="stat-row" style="margin-top:1.5rem;grid-template-columns:repeat(4,1fr);">
                        <div class="stat-card"><div class="stat-num stat-accent">{present}</div><div class="stat-label">Present</div></div>
                        <div class="stat-card"><div class="stat-num stat-warn">{late}</div><div class="stat-label">Late</div></div>
                        <div class="stat-card"><div class="stat-num stat-danger">{absent}</div><div class="stat-label">Absent</div></div>
                        <div class="stat-card"><div class="stat-num">{rate}</div><div class="stat-label">Attendance Rate</div></div>
                    </div>
                    """, unsafe_allow_html=True)

                    late_status_map = {r["student"].lower(): r["stage"] for r in st.session_state.late_requests}
                    rows_html = ""
                    for r in rows:
                        init = student_initials(r["name"])
                        if r["status"] == "Present":
                            badge_html = '<span class="badge badge-present">Present</span>'
                        elif r["status"] == "Absent":
                            badge_html = '<span class="badge badge-absent">Absent</span>'
                        else:
                            lstage = late_status_map.get(r["name"].lower(), "faculty")
                            if lstage == "approved":
                                badge_html = '<span class="badge badge-late">Late</span> <span class="badge badge-approved">Approved</span>'
                            elif lstage == "rejected":
                                badge_html = '<span class="badge badge-late">Late</span> <span class="badge badge-rejected">Rejected</span>'
                            else:
                                stage_label = {
                                    "faculty": "Pending Faculty",
                                    "hod": "Pending HOD",
                                    "admin": "Pending Admin"
                                }.get(lstage, lstage)
                                badge_html = (
                                    f'<span class="badge badge-late">Late</span> '
                                    f'<span class="badge badge-pending">{stage_label}</span>'
                                )
                        rows_html += f"""
                        <tr>
                            <td><div style="display:flex;align-items:center;gap:10px;">
                                <div class="chip-avatar">{init}</div>{r['name']}
                            </div></td>
                            <td>{badge_html}</td>
                            <td style="color:#6e7681;font-family:'DM Mono',monospace;">{r['time']}</td>
                        </tr>"""

                    st.markdown(f"""
                    <div class="card" style="margin-top:1rem;">
                        <div class="card-title">Attendance Detail</div>
                        <table class="att-table">
                            <thead><tr><th>Student</th><th>Status</th><th>First Detected</th></tr></thead>
                            <tbody>{rows_html}</tbody>
                        </table>
                    </div>
                    """, unsafe_allow_html=True)

                    if late > 0:
                        st.info(f"ℹ️ {late} student(s) marked late. Go to **🕐 Late Approval** to process their requests.")
                else:
                    with st.expander("Raw attendance output", expanded=True):
                        st.code(stdout, language="bash")
            else:
                st.error("Attendance script failed")
                with st.expander("Errors", expanded=True):
                    st.code(stderr, language="bash")
        else:
            st.warning("Please upload a classroom video first.")


# ─── PAGE: FACULTY LATE APPROVAL ──────────────────────────────────────────────
def page_faculty_approval():
    pending = pending_count_for_role("faculty")
    st.markdown(f"""
    <div class="page-header">
        <div class="page-title">Late Arrival Approvals</div>
        <div class="page-subtitle">Faculty review · First stage of approval workflow · {pending} pending</div>
    </div>
    """, unsafe_allow_html=True)

    requests = st.session_state.late_requests
    total = len(requests)
    approved = sum(1 for r in requests if r["stage"] == "approved")
    rejected = sum(1 for r in requests if r["stage"] == "rejected")

    st.markdown(f"""
    <div class="stat-row" style="grid-template-columns:repeat(4,1fr);">
        <div class="stat-card"><div class="stat-num">{total}</div><div class="stat-label">Total requests</div></div>
        <div class="stat-card"><div class="stat-num stat-warn">{pending}</div><div class="stat-label">Awaiting your review</div></div>
        <div class="stat-card"><div class="stat-num stat-accent">{approved}</div><div class="stat-label">Fully approved</div></div>
        <div class="stat-card"><div class="stat-num stat-danger">{rejected}</div><div class="stat-label">Rejected</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card-title">Requests awaiting Faculty review</div>', unsafe_allow_html=True)
    render_approval_panel("faculty")


# ─── PAGE: HOD APPROVAL ───────────────────────────────────────────────────────
def page_hod_approval():
    pending = pending_count_for_role("hod")
    st.markdown(f"""
    <div class="page-header">
        <div class="page-title">HOD Approvals</div>
        <div class="page-subtitle">Head of Department review · Second stage · {pending} pending</div>
    </div>
    """, unsafe_allow_html=True)

    requests = st.session_state.late_requests
    total = len(requests)
    approved = sum(1 for r in requests if r["stage"] == "approved")
    rejected = sum(1 for r in requests if r["stage"] == "rejected")

    st.markdown(f"""
    <div class="stat-row" style="grid-template-columns:repeat(4,1fr);">
        <div class="stat-card"><div class="stat-num">{total}</div><div class="stat-label">Total requests</div></div>
        <div class="stat-card"><div class="stat-num stat-warn">{pending}</div><div class="stat-label">Awaiting your review</div></div>
        <div class="stat-card"><div class="stat-num stat-accent">{approved}</div><div class="stat-label">Fully approved</div></div>
        <div class="stat-card"><div class="stat-num stat-danger">{rejected}</div><div class="stat-label">Rejected</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="card-title">Requests escalated to HOD (Faculty already approved)</div>',
        unsafe_allow_html=True
    )
    render_approval_panel("hod")


# ─── PAGE: ADMIN APPROVAL ─────────────────────────────────────────────────────
def page_admin_approval():
    pending = pending_count_for_role("admin")
    st.markdown(f"""
    <div class="page-header">
        <div class="page-title">Admin Final Approval</div>
        <div class="page-subtitle">Administrator review · Final stage · {pending} pending</div>
    </div>
    """, unsafe_allow_html=True)

    requests = st.session_state.late_requests
    total = len(requests)
    approved = sum(1 for r in requests if r["stage"] == "approved")
    rejected = sum(1 for r in requests if r["stage"] == "rejected")

    st.markdown(f"""
    <div class="stat-row" style="grid-template-columns:repeat(4,1fr);">
        <div class="stat-card"><div class="stat-num">{total}</div><div class="stat-label">Total requests</div></div>
        <div class="stat-card"><div class="stat-num stat-warn">{pending}</div><div class="stat-label">Awaiting your review</div></div>
        <div class="stat-card"><div class="stat-num stat-accent">{approved}</div><div class="stat-label">Fully approved</div></div>
        <div class="stat-card"><div class="stat-num stat-danger">{rejected}</div><div class="stat-label">Rejected</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="card-title">Requests awaiting Admin final sign-off</div>',
        unsafe_allow_html=True
    )
    render_approval_panel("admin")


# ─── PAGE: ALL REQUESTS (HOD + ADMIN) ─────────────────────────────────────────
def page_all_requests():
    st.markdown("""
    <div class="page-header">
        <div class="page-title">All Late Requests</div>
        <div class="page-subtitle">Full history and audit trail of all late-arrival requests</div>
    </div>
    """, unsafe_allow_html=True)

    requests = st.session_state.late_requests

    if not requests:
        st.markdown(
            '<div style="padding:2rem;text-align:center;color:#6e7681;font-size:14px;background:#161b22;'
            'border:1px solid #1e2530;border-radius:12px;">No late-arrival requests yet.</div>',
            unsafe_allow_html=True
        )
        return

    total = len(requests)
    pending_f = pending_count_for_role("faculty")
    pending_h = pending_count_for_role("hod")
    pending_a = pending_count_for_role("admin")
    approved = sum(1 for r in requests if r["stage"] == "approved")
    rejected = sum(1 for r in requests if r["stage"] == "rejected")

    st.markdown(f"""
    <div class="stat-row" style="grid-template-columns:repeat(5,1fr);">
        <div class="stat-card"><div class="stat-num">{total}</div><div class="stat-label">Total</div></div>
        <div class="stat-card"><div class="stat-num stat-warn">{pending_f}</div><div class="stat-label">At Faculty</div></div>
        <div class="stat-card"><div class="stat-num stat-warn">{pending_h}</div><div class="stat-label">At HOD</div></div>
        <div class="stat-card"><div class="stat-num stat-warn">{pending_a}</div><div class="stat-label">At Admin</div></div>
        <div class="stat-card"><div class="stat-num stat-accent">{approved}</div><div class="stat-label">Approved</div></div>
    </div>
    """, unsafe_allow_html=True)

    status_color = {
        "faculty":  ("#f0883e", "Pending Faculty"),
        "hod":      ("#f0883e", "Pending HOD"),
        "admin":    ("#f0883e", "Pending Admin"),
        "approved": ("#00c9a7", "Approved"),
        "rejected": ("#f85149", "Rejected"),
    }

    rows_html = ""
    for req in reversed(requests):
        init = student_initials(req["student"])
        color, label = status_color.get(req["stage"], ("#8b949e", req["stage"].capitalize()))
        rows_html += f"""
        <tr>
            <td><div style="display:flex;align-items:center;gap:8px;">
                <div class="chip-avatar">{init}</div>{req['student']}
            </div></td>
            <td style="color:#6e7681;font-family:'DM Mono',monospace;font-size:12px;">{req['id']}</td>
            <td style="color:#6e7681;">{req['date']}</td>
            <td style="color:#6e7681;">{req['time_detected']}</td>
            <td><span style="color:{color};font-size:12px;font-weight:600;">{label}</span></td>
        </tr>"""

    st.markdown(f"""
    <div class="card">
        <div class="card-title">Request History</div>
        <table class="att-table">
            <thead><tr><th>Student</th><th>Request ID</th><th>Date</th><th>Arrival</th><th>Status</th></tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)

    # Audit trail
    completed = [r for r in requests if r["stage"] in ("approved", "rejected")]
    if completed:
        st.markdown('<div class="card-title" style="margin-top:1.5rem;">Audit Trail</div>', unsafe_allow_html=True)
        for req in reversed(completed):
            trail_html = (
                f'<div style="font-size:12px;color:#8b949e;margin-bottom:0.5rem;">'
                f'<b style="color:#e6edf3;">{req["student"]}</b> ({req["id"]}) · {req["date"]}</div>'
            )
            for stage in ("faculty", "hod", "admin"):
                action = req.get(f"{stage}_action")
                if action:
                    note = req.get(f"{stage}_reason") or "—"
                    when = req.get(f"{stage}_at") or "—"
                    color = "#00c9a7" if action == "approved" else "#f85149"
                    trail_html += (
                        f'<div style="font-size:12px;color:#6e7681;padding:4px 0 4px 12px;'
                        f'border-left:2px solid {color};margin:4px 0;">'
                        f'<span style="color:{color};font-weight:600;">{stage.upper()} {action}</span>'
                        f' · {when} · Note: {note}</div>'
                    )
            st.markdown(f'<div class="card" style="padding:1rem;">{trail_html}</div>', unsafe_allow_html=True)


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    # Show login if not authenticated
    if not st.session_state.logged_in:
        login_page()
        return

    role = st.session_state.role

    with st.sidebar:
        page = sidebar()

    # ── Faculty routing ──────────────────────────────────────────────────────
    if role == "faculty":
        if page == "Home":
            page_home()
        elif page == "Enroll Student":
            page_enroll()
        elif page == "Train Model":
            page_train()
        elif page == "Take Attendance":
            page_attendance()
        elif "Late Approval" in page:
            page_faculty_approval()

    # ── HOD routing ──────────────────────────────────────────────────────────
    elif role == "hod":
        if page == "Home":
            page_home()
        elif "HOD Approvals" in page:
            page_hod_approval()
        elif "All Requests" in page:
            page_all_requests()

    # ── Admin routing ─────────────────────────────────────────────────────────
    elif role == "admin":
        if page == "Home":
            page_home()
        elif "Admin Approvals" in page:
            page_admin_approval()
        elif "All Requests" in page:
            page_all_requests()


if __name__ == "__main__":
    main()