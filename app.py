import streamlit as st
import subprocess
import os
import json
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

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
.stApp {
    background: #0d1117;
}
section[data-testid="stSidebar"] {
    background: #0d1117;
    border-right: 1px solid #1e2530;
}
section[data-testid="stSidebar"] > div {
    padding-top: 1.5rem;
}

/* ── Hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 4rem; max-width: 1100px; }

/* ── Sidebar brand ── */
.brand {
    display: flex; align-items: center; gap: 10px;
    padding: 0 1rem 1.5rem;
    border-bottom: 1px solid #1e2530;
    margin-bottom: 1.5rem;
}
.brand-icon {
    width: 36px; height: 36px; border-radius: 10px;
    background: linear-gradient(135deg, #00c9a7, #00a3d9);
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
}
.brand-text { font-size: 15px; font-weight: 600; color: #e6edf3; letter-spacing: -0.02em; }
.brand-sub  { font-size: 11px; color: #6e7681; letter-spacing: 0.04em; text-transform: uppercase; }

/* ── Nav items ── */
.nav-item {
    display: flex; align-items: center; gap: 10px;
    padding: 9px 14px; border-radius: 8px; margin-bottom: 3px;
    cursor: pointer; transition: background 0.15s;
    color: #8b949e; font-size: 14px; font-weight: 500;
    text-decoration: none;
}
.nav-item:hover { background: #161b22; color: #e6edf3; }
.nav-item.active { background: #161b22; color: #00c9a7; }
.nav-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #00c9a7; margin-left: auto;
}

/* ── Page header ── */
.page-header {
    margin-bottom: 2rem;
    padding-bottom: 1.25rem;
    border-bottom: 1px solid #1e2530;
}
.page-title {
    font-size: 26px; font-weight: 600; color: #e6edf3;
    letter-spacing: -0.03em; margin-bottom: 4px;
}
.page-subtitle { font-size: 14px; color: #6e7681; }

/* ── Cards ── */
.card {
    background: #161b22;
    border: 1px solid #1e2530;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}
.card-title {
    font-size: 11px; font-weight: 600; letter-spacing: 0.08em;
    text-transform: uppercase; color: #6e7681; margin-bottom: 14px;
}

/* ── Stat cards ── */
.stat-row {
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;
    margin-bottom: 1.5rem;
}
.stat-card {
    background: #161b22; border: 1px solid #1e2530;
    border-radius: 12px; padding: 1.1rem 1.25rem;
}
.stat-num { font-size: 28px; font-weight: 600; color: #e6edf3; letter-spacing: -0.04em; }
.stat-label { font-size: 12px; color: #6e7681; margin-top: 2px; }
.stat-accent { color: #00c9a7; }
.stat-warn   { color: #f0883e; }
.stat-danger { color: #f85149; }

/* ── Workflow steps ── */
.workflow {
    display: flex; gap: 0; margin-bottom: 1.5rem;
    background: #161b22; border: 1px solid #1e2530;
    border-radius: 12px; overflow: hidden;
}
.wf-step {
    flex: 1; padding: 1rem 0.75rem; text-align: center;
    border-right: 1px solid #1e2530; position: relative;
}
.wf-step:last-child { border-right: none; }
.wf-num {
    width: 28px; height: 28px; border-radius: 50%;
    background: #1e2530; color: #6e7681;
    font-size: 12px; font-weight: 600;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 8px;
}
.wf-num.done { background: rgba(0,201,167,0.15); color: #00c9a7; }
.wf-num.curr { background: rgba(0,163,217,0.15); color: #00a3d9; box-shadow: 0 0 0 4px rgba(0,163,217,0.08); }
.wf-label { font-size: 11px; color: #8b949e; font-weight: 500; }
.wf-label.curr { color: #e6edf3; }

/* ── Student chips ── */
.student-list {
    display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 1rem;
}
.student-chip {
    display: flex; align-items: center; gap: 8px;
    background: #0d1117; border: 1px solid #1e2530;
    border-radius: 8px; padding: 6px 12px;
    font-size: 13px; color: #e6edf3;
}
.chip-avatar {
    width: 22px; height: 22px; border-radius: 50%;
    background: linear-gradient(135deg, #00c9a7, #00a3d9);
    font-size: 10px; font-weight: 600; color: #0d1117;
    display: flex; align-items: center; justify-content: center;
}
.chip-dot { width: 6px; height: 6px; border-radius: 50%; background: #00c9a7; }

/* ── Upload area ── */
.upload-hint {
    background: rgba(0,201,167,0.04);
    border: 1.5px dashed rgba(0,201,167,0.25);
    border-radius: 10px;
    padding: 1.25rem;
    text-align: center;
    color: #6e7681; font-size: 13px;
    margin-bottom: 0.5rem;
}
.upload-hint strong { color: #00c9a7; }

/* ── Attendance table ── */
.att-table {
    width: 100%; border-collapse: collapse;
    font-size: 13px;
}
.att-table th {
    text-align: left; padding: 8px 12px;
    color: #6e7681; font-size: 11px;
    font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase;
    border-bottom: 1px solid #1e2530;
}
.att-table td {
    padding: 10px 12px; border-bottom: 1px solid #1e2530;
    color: #e6edf3;
}
.att-table tr:last-child td { border-bottom: none; }
.badge {
    display: inline-block; padding: 3px 10px;
    border-radius: 20px; font-size: 11px; font-weight: 600;
}
.badge-present { background: rgba(0,201,167,0.12); color: #00c9a7; }
.badge-absent  { background: rgba(248,81,73,0.12);  color: #f85149; }
.badge-late    { background: rgba(240,136,62,0.12); color: #f0883e; }

/* ── Buttons override ── */
.stButton > button {
    background: linear-gradient(135deg, #00c9a7, #00a3d9) !important;
    color: #0d1117 !important; font-weight: 600 !important;
    border: none !important; border-radius: 8px !important;
    padding: 0.5rem 1.5rem !important; font-size: 14px !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: opacity 0.15s !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

/* Secondary button pattern */
.stButton.secondary > button {
    background: #1e2530 !important; color: #e6edf3 !important;
}

/* ── Inputs ── */
.stTextInput input, .stSelectbox select {
    background: #0d1117 !important;
    border: 1px solid #1e2530 !important;
    border-radius: 8px !important; color: #e6edf3 !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput label, .stSelectbox label, .stFileUploader label {
    color: #8b949e !important; font-size: 13px !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Code block ── */
.stCodeBlock code {
    font-family: 'DM Mono', monospace !important;
    font-size: 12px !important;
    background: #0d1117 !important;
    color: #00c9a7 !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: #00c9a7 !important; }

/* ── Success / Error / Warning ── */
.stSuccess { background: rgba(0,201,167,0.08) !important; border-color: rgba(0,201,167,0.3) !important; color: #00c9a7 !important; }
.stError   { background: rgba(248,81,73,0.08)  !important; border-color: rgba(248,81,73,0.3)  !important; }
.stWarning { background: rgba(240,136,62,0.08) !important; border-color: rgba(240,136,62,0.3) !important; }

/* ── Progress bar ── */
.stProgress > div > div > div { background: linear-gradient(90deg, #00c9a7, #00a3d9) !important; }

/* ── Divider ── */
hr { border-color: #1e2530 !important; }

/* ── Sidebar radio override ── */
.stRadio > label { color: #8b949e !important; font-size: 13px !important; }
.stRadio > div   { gap: 4px !important; }
.stRadio [data-testid="stMarkdownContainer"] p { font-size: 14px !important; }
</style>
""", unsafe_allow_html=True)


# ─── HELPERS ───────────────────────────────────────────────────────────────────
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


def parse_attendance_output(raw: str, enrolled: list):
    """
    Parses attendance.py stdout lines of the form:
        [08:42:31] PRESENT: Roseena
    Returns a row per enrolled student — present if found in output, absent otherwise.
    """
    import re
    present_names = {}   # name -> timestamp

    for line in raw.splitlines():
        line = line.strip()
        # Match:  [HH:MM:SS] PRESENT: Name
        m = re.match(r'\[(\d{2}:\d{2}:\d{2})\]\s+PRESENT:\s+(.+)', line, re.IGNORECASE)
        if m:
            timestamp, name = m.group(1), m.group(2).strip()
            present_names[name.lower()] = {"name": name, "time": timestamp}

    rows = []
    # Show all enrolled students — mark absent if not detected
    for student in enrolled:
        key = student.lower()
        if key in present_names:
            rows.append({
                "name":   present_names[key]["name"],
                "status": "Present",
                "time":   present_names[key]["time"],
            })
        else:
            rows.append({
                "name":   student,
                "status": "Absent",
                "time":   "—",
            })

    # Also include any detected name not in enrolled list (edge case)
    for key, val in present_names.items():
        if not any(r["name"].lower() == key for r in rows):
            rows.append({"name": val["name"], "status": "Present", "time": val["time"]})

    return rows


def sidebar():
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
    trained  = model_is_trained()

    choice = st.radio(
        "",
        ["🏠  Home", "👤  Enroll Student", "🧠  Train Model", "✅  Take Attendance"],
        label_visibility="collapsed"
    )

    st.markdown("<hr style='margin:1.5rem 0;'>", unsafe_allow_html=True)

    # Mini status panel
    st.markdown(f"""
    <div style="padding:0 0.5rem;">
        <div style="font-size:11px;color:#6e7681;font-weight:600;letter-spacing:0.08em;
                    text-transform:uppercase;margin-bottom:10px;">System Status</div>
        <div style="display:flex;justify-content:space-between;font-size:12px;
                    color:#8b949e;margin-bottom:6px;">
            <span>Students enrolled</span>
            <span style="color:{'#00c9a7' if enrolled else '#f85149'};font-weight:600;">
                {len(enrolled)}
            </span>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:12px;color:#8b949e;">
            <span>Model trained</span>
            <span style="color:{'#00c9a7' if trained else '#f85149'};font-weight:600;">
                {'Yes' if trained else 'No'}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    return choice.split("  ", 1)[-1].strip()


# ─── WORKFLOW INDICATOR ─────────────────────────────────────────────────────────
def workflow_bar(active: int):
    steps = ["Enroll", "Train", "Upload Video", "Attendance"]
    enrolled = len(get_enrolled_students()) > 0
    trained  = model_is_trained()
    done_map = [enrolled, trained, False, False]

    html = '<div class="workflow">'
    for i, (s, done) in enumerate(zip(steps, done_map)):
        num_cls = "done" if done else ("curr" if i+1 == active else "")
        lbl_cls = "curr" if i+1 == active else ""
        icon = "✓" if done else str(i+1)
        html += f"""
        <div class="wf-step">
            <div class="wf-num {num_cls}">{icon}</div>
            <div class="wf-label {lbl_cls}">{s}</div>
        </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


# ─── PAGES ─────────────────────────────────────────────────────────────────────
def page_home():
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Welcome to SmartAttend</div>
        <div class="page-subtitle">AI-powered face recognition attendance · YOLOv8 + FAISS</div>
    </div>
    """, unsafe_allow_html=True)

    enrolled = get_enrolled_students()
    trained  = model_is_trained()

    # Stat cards
    att_rate = "—"
    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-card">
            <div class="stat-num stat-accent">{len(enrolled)}</div>
            <div class="stat-label">Students Enrolled</div>
        </div>
        <div class="stat-card">
            <div class="stat-num {'stat-accent' if trained else 'stat-danger'}">
                {'Ready' if trained else 'Needed'}
            </div>
            <div class="stat-label">Model Status</div>
        </div>
        <div class="stat-card">
            <div class="stat-num stat-accent">YOLOv8x</div>
            <div class="stat-label">Detection Engine</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Workflow
    st.markdown('<div class="card-title">Your Progress</div>', unsafe_allow_html=True)
    workflow_bar(1 if not enrolled else (2 if not trained else 3))

    # Enrolled students
    if enrolled:
        chips = ""
        for s in enrolled:
            init = student_initials(s)
            chips += f"""
            <div class="student-chip">
                <div class="chip-avatar">{init}</div>
                {s}
                <div class="chip-dot"></div>
            </div>"""
        st.markdown(f"""
        <div class="card">
            <div class="card-title">Enrolled Students</div>
            <div class="student-list">{chips}</div>
        </div>
        """, unsafe_allow_html=True)

    # Steps guide
    st.markdown("""
    <div class="card">
        <div class="card-title">How It Works</div>
        <table style="width:100%;border-collapse:collapse;font-size:13px;">
            <tr>
                <td style="padding:10px 12px;color:#6e7681;border-bottom:1px solid #1e2530;width:28px;">01</td>
                <td style="padding:10px 12px;color:#e6edf3;font-weight:500;border-bottom:1px solid #1e2530;">Enroll Students</td>
                <td style="padding:10px 12px;color:#8b949e;border-bottom:1px solid #1e2530;">Upload a short video (5–15s) per student to extract face embeddings</td>
            </tr>
            <tr>
                <td style="padding:10px 12px;color:#6e7681;border-bottom:1px solid #1e2530;">02</td>
                <td style="padding:10px 12px;color:#e6edf3;font-weight:500;border-bottom:1px solid #1e2530;">Train the Model</td>
                <td style="padding:10px 12px;color:#8b949e;border-bottom:1px solid #1e2530;">Build FAISS index from enrolled embeddings — takes under a minute</td>
            </tr>
            <tr>
                <td style="padding:10px 12px;color:#6e7681;border-bottom:1px solid #1e2530;">03</td>
                <td style="padding:10px 12px;color:#e6edf3;font-weight:500;border-bottom:1px solid #1e2530;">Upload Class Video</td>
                <td style="padding:10px 12px;color:#8b949e;border-bottom:1px solid #1e2530;">Any classroom recording — mp4, avi, or mov</td>
            </tr>
            <tr>
                <td style="padding:10px 12px;color:#6e7681;">04</td>
                <td style="padding:10px 12px;color:#e6edf3;font-weight:500;">Take Attendance</td>
                <td style="padding:10px 12px;color:#8b949e;">YOLOv8 detects faces, FAISS matches identities, results exported</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)


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
        chips = "".join(f"""
        <div class="student-chip">
            <div class="chip-avatar">{student_initials(s)}</div>
            {s} <div class="chip-dot"></div>
        </div>""" for s in enrolled)
        st.markdown(f"""
        <div class="card">
            <div class="card-title">Already Enrolled ({len(enrolled)})</div>
            <div class="student-list">{chips}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="card-title" style="margin-bottom:8px;">Add New Student</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="medium")
    with col1:
        student_name = st.text_input("Full Name", placeholder="e.g. Roseena")
    with col2:
        st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:12px;color:#6e7681;margin-top:20px;">
            💡 Use the same name every time — it becomes the folder name
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="upload-hint">
        <strong>Upload a short video · 5–15 seconds</strong><br>
        Face clearly visible · Good lighting · Multiple angles preferred<br>
        Formats: .mp4 · .avi · .mov
    </div>
    """, unsafe_allow_html=True)

    uploaded_video = st.file_uploader(
        "Choose video file",
        type=["mp4", "avi", "mov"],
        label_visibility="collapsed"
    )

    if uploaded_video:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;padding:10px 14px;
                    background:#0d1117;border:1px solid #1e2530;border-radius:8px;
                    margin-bottom:1rem;font-size:13px;color:#8b949e;">
            <span style="color:#00c9a7;">▶</span>
            <span style="color:#e6edf3;font-weight:500;">{uploaded_video.name}</span>
            <span style="margin-left:auto;">{uploaded_video.size // 1024} KB</span>
        </div>
        """, unsafe_allow_html=True)

    if st.button("Enroll Student →"):
        if student_name and uploaded_video:
            os.makedirs("student_videos", exist_ok=True)
            video_path = os.path.join("student_videos", f"{student_name}.mp4")
            with open(video_path, "wb") as f:
                f.write(uploaded_video.read())
            st.success(f"✓ Video saved for **{student_name}**")

            with st.spinner(f"Running enrollment.py for {student_name}…"):
                result = subprocess.run(
                    ["python", "enrollment.py"],
                    capture_output=True, text=True
                )

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


def page_train():
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Train Face Model</div>
        <div class="page-subtitle">Build the FAISS index from all enrolled student embeddings</div>
    </div>
    """, unsafe_allow_html=True)

    workflow_bar(2)

    enrolled = get_enrolled_students()
    trained  = model_is_trained()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-num {'stat-accent' if enrolled else 'stat-danger'}">{len(enrolled)}</div>
            <div class="stat-label">Students ready to train</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        idx_size = ""
        if Path("faces.index").exists():
            idx_size = f"{Path('faces.index').stat().st_size // 1024} KB"
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-num {'stat-accent' if trained else 'stat-danger'}">
                {'Built' if trained else 'None'}
            </div>
            <div class="stat-label">FAISS index {idx_size}</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        mtime = ""
        if Path("faces.index").exists():
            ts = Path("faces.index").stat().st_mtime
            mtime = datetime.fromtimestamp(ts).strftime("%b %d, %H:%M")
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-num" style="font-size:16px;padding-top:4px;">
                {mtime if mtime else '—'}
            </div>
            <div class="stat-label">Last trained</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    if not enrolled:
        st.markdown("""
        <div style="padding:1.25rem;background:rgba(248,81,73,0.08);border:1px solid rgba(248,81,73,0.2);
                    border-radius:10px;color:#f85149;font-size:14px;">
            ⚠ No students enrolled yet. Go to <b>Enroll Student</b> first.
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown("""
    <div class="card">
        <div class="card-title">What this does</div>
        <div style="font-size:13px;color:#8b949e;line-height:1.7;">
            training.py reads all face embeddings extracted during enrollment, 
            builds a FAISS L2 index, and saves <code style="color:#00c9a7;">faces.index</code> 
            and <code style="color:#00c9a7;">labels.pkl</code> to disk. 
            Run this any time you add new students.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Start Training →"):
        progress = st.progress(0, text="Initialising…")
        with st.spinner("Building FAISS index…"):
            result = subprocess.run(
                ["python", "training.py"],
                capture_output=True, text=True
            )
        progress.progress(100, text="Done")
        time.sleep(0.4)
        progress.empty()

        if result.returncode == 0:
            st.success("✓ Model trained successfully! You can now take attendance.")
        else:
            st.error("Training failed — see output below")

        if result.stdout:
            with st.expander("Script output", expanded=False):
                st.code(result.stdout, language="bash")
        if result.stderr:
            with st.expander("Errors", expanded=True):
                st.code(result.stderr, language="bash")


def page_attendance():
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Take Attendance</div>
        <div class="page-subtitle">Upload a classroom recording and let AI mark attendance</div>
    </div>
    """, unsafe_allow_html=True)

    workflow_bar(4)

    if not model_is_trained():
        st.markdown("""
        <div style="padding:1.25rem;background:rgba(248,81,73,0.08);border:1px solid rgba(248,81,73,0.2);
                    border-radius:10px;color:#f85149;font-size:14px;margin-bottom:1rem;">
            ⚠ Model not trained yet. Go to <b>Train Model</b> first.
        </div>
        """, unsafe_allow_html=True)

    enrolled = get_enrolled_students()
    if enrolled:
        chips = "".join(f"""
        <div class="student-chip">
            <div class="chip-avatar">{student_initials(s)}</div>
            {s}
        </div>""" for s in enrolled)
        st.markdown(f"""
        <div class="card">
            <div class="card-title">Checking against {len(enrolled)} enrolled students</div>
            <div class="student-list">{chips}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="upload-hint">
        <strong>Upload Classroom Video</strong><br>
        Any lecture or session recording · longer videos take more time to process<br>
        Formats: .mp4 · .avi · .mov
    </div>
    """, unsafe_allow_html=True)

    attendance_video = st.file_uploader(
        "Classroom video",
        type=["mp4", "avi", "mov"],
        label_visibility="collapsed"
    )

    if attendance_video:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;padding:10px 14px;
                    background:#0d1117;border:1px solid #1e2530;border-radius:8px;
                    margin:0.75rem 0;font-size:13px;color:#8b949e;">
            <span style="color:#00c9a7;">▶</span>
            <span style="color:#e6edf3;font-weight:500;">{attendance_video.name}</span>
            <span style="margin-left:auto;">{attendance_video.size // 1024} KB</span>
        </div>
        """, unsafe_allow_html=True)

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

                # Parse results — cross-reference with enrolled list for absent students
                rows = parse_attendance_output(stdout, enrolled)

                if rows:
                    present = sum(1 for r in rows if r["status"] == "Present")
                    absent  = sum(1 for r in rows if r["status"] == "Absent")
                    total   = len(rows)
                    rate    = f"{present / total * 100:.0f}%" if total else "—"

                    st.markdown(f"""
                    <div class="stat-row" style="margin-top:1.5rem;">
                        <div class="stat-card">
                            <div class="stat-num stat-accent">{present}</div>
                            <div class="stat-label">Present</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-num stat-danger">{absent}</div>
                            <div class="stat-label">Absent</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-num">{rate}</div>
                            <div class="stat-label">Attendance Rate</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    badge_map = {
                        "Present": "badge-present",
                        "Absent":  "badge-absent",
                    }
                    rows_html = ""
                    for r in rows:
                        bc = badge_map.get(r["status"], "badge-absent")
                        init = student_initials(r["name"])
                        rows_html += f"""
                        <tr>
                            <td>
                                <div style="display:flex;align-items:center;gap:10px;">
                                    <div class="chip-avatar">{init}</div>
                                    {r['name']}
                                </div>
                            </td>
                            <td><span class="badge {bc}">{r['status']}</span></td>
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
                else:
                    # Raw output fallback
                    with st.expander("Raw attendance output", expanded=True):
                        st.code(stdout, language="bash")
            else:
                st.error("Attendance script failed")
                with st.expander("Errors", expanded=True):
                    st.code(stderr, language="bash")
        else:
            st.warning("Please upload a classroom video first.")


# ─── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    with st.sidebar:
        page = sidebar()

    if   page == "Home":            page_home()
    elif page == "Enroll Student":  page_enroll()
    elif page == "Train Model":     page_train()
    elif page == "Take Attendance": page_attendance()


if __name__ == "__main__":
    main()
