import streamlit as st
import folium
from folium.plugins import LocateControl
from streamlit_folium import st_folium
import requests

# ── Config ──────────────────────────────────────────────────────────────────
API_BASE = "http://localhost:8000"
CHENNAI_CENTER = [13.0827, 80.2707]

HAZARD_CONFIG = {
    "manhole": {"icon": "circle-exclamation", "color": "red", "label": "Open Manhole", "hex": "#ff3b4a", "glow": "rgba(255,59,74,0.35)"},
    "flooding": {"icon": "water", "color": "blue", "label": "Flooding", "hex": "#00b4d8", "glow": "rgba(0,180,216,0.35)"},
    "no_light": {"icon": "lightbulb", "color": "darkpurple", "label": "No Streetlight", "hex": "#b14aed", "glow": "rgba(177,74,237,0.35)"},
    "broken_footpath": {"icon": "road", "color": "orange", "label": "Broken Footpath", "hex": "#ff9f1c", "glow": "rgba(255,159,28,0.35)"},
    "unsafe_area": {"icon": "triangle-exclamation", "color": "darkred", "label": "Unsafe Area", "hex": "#d62828", "glow": "rgba(214,40,40,0.35)"},
    "no_wheelchair_access": {"icon": "wheelchair-move", "color": "gray", "label": "No Wheelchair Access", "hex": "#8d99ae", "glow": "rgba(141,153,174,0.35)"},
}

st.set_page_config(
    page_title="SafeWalk",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Cinematic Styling ───────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@300;400;500&display=swap');

    :root {
        --void: #05080f;
        --surface: #0a0f1c;
        --surface-2: #111827;
        --surface-3: #1a2236;
        --border: rgba(255,255,255,0.06);
        --border-glow: rgba(255,159,28,0.15);
        --text: #e2e8f0;
        --text-dim: #64748b;
        --text-ghost: #334155;
        --neon-amber: #ff9f1c;
        --neon-red: #ff3b4a;
        --neon-green: #00f5a0;
        --neon-cyan: #00b4d8;
        --neon-purple: #b14aed;
    }

    /* ── Page ── */
    .stApp {
        background: var(--void);
        background-image:
            radial-gradient(ellipse 80% 60% at 50% -20%, rgba(255,159,28,0.06) 0%, transparent 70%),
            radial-gradient(ellipse 60% 40% at 80% 100%, rgba(0,180,216,0.04) 0%, transparent 60%);
        font-family: 'Syne', sans-serif;
    }

    .stApp::before {
        content: '';
        position: fixed;
        inset: 0;
        background: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.015'/%3E%3C/svg%3E");
        pointer-events: none;
        z-index: 0;
    }

    /* ── Hide Streamlit chrome ── */
    header[data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stDecoration"] { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    .block-container {
        padding: 0.8rem 1.2rem !important;
        max-width: 100% !important;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0f1c 0%, #080c16 100%) !important;
        border-right: 1px solid var(--border) !important;
    }
    section[data-testid="stSidebar"] * {
        font-family: 'Syne', sans-serif !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        padding-top: 1.5rem;
    }

    /* ── Animations ── */
    @keyframes fadeSlideIn {
        from { opacity: 0; transform: translateY(12px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 0 15px rgba(255,159,28,0.15), inset 0 1px 0 rgba(255,255,255,0.03); }
        50% { box-shadow: 0 0 25px rgba(255,159,28,0.25), inset 0 1px 0 rgba(255,255,255,0.06); }
    }
    @keyframes scanline {
        0% { transform: translateY(-100%); }
        100% { transform: translateY(100vh); }
    }
    @keyframes borderGlow {
        0%, 100% { border-color: rgba(255,159,28,0.1); }
        50% { border-color: rgba(255,159,28,0.3); }
    }
    @keyframes breathe {
        0%, 100% { opacity: 0.6; }
        50% { opacity: 1; }
    }

    /* ── Header ── */
    .sw-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.6rem 0 0.8rem;
        margin-bottom: 0.6rem;
        border-bottom: 1px solid var(--border);
        animation: fadeSlideIn 0.6s ease-out;
        position: relative;
    }
    .sw-header::after {
        content: '';
        position: absolute;
        bottom: -1px;
        left: 0;
        width: 120px;
        height: 1px;
        background: linear-gradient(90deg, var(--neon-amber), transparent);
    }
    .sw-brand {
        display: flex;
        align-items: baseline;
        gap: 3px;
    }
    .sw-brand-safe {
        font-family: 'Syne', sans-serif;
        font-weight: 800;
        font-size: 1.9rem;
        background: linear-gradient(135deg, #ff9f1c, #ffcb47);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
        line-height: 1;
    }
    .sw-brand-walk {
        font-family: 'Syne', sans-serif;
        font-weight: 400;
        font-size: 1.9rem;
        color: var(--text);
        letter-spacing: -1px;
        line-height: 1;
    }
    .sw-tagline {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.62rem;
        font-weight: 400;
        color: var(--text-dim);
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-top: 3px;
    }
    .sw-status-dot {
        display: inline-block;
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: var(--neon-green);
        box-shadow: 0 0 8px var(--neon-green);
        margin-right: 6px;
        animation: breathe 2s ease-in-out infinite;
    }
    .sw-status {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.65rem;
        color: var(--text-dim);
        letter-spacing: 1px;
    }

    /* ── Score Cards ── */
    .metrics-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 8px;
        margin-bottom: 0.7rem;
        animation: fadeSlideIn 0.8s ease-out 0.1s both;
    }
    .metric-card {
        background: linear-gradient(145deg, var(--surface-2), var(--surface));
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 14px 16px;
        text-align: center;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        border-color: var(--border-glow);
        transform: translateY(-1px);
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
    }
    .metric-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.58rem;
        font-weight: 400;
        color: var(--text-ghost);
        text-transform: uppercase;
        letter-spacing: 2.5px;
        margin-bottom: 6px;
    }
    .metric-value {
        font-family: 'Syne', sans-serif;
        font-weight: 700;
        font-size: 1.5rem;
        line-height: 1.1;
    }
    .metric-value.green { color: var(--neon-green); text-shadow: 0 0 20px rgba(0,245,160,0.3); }
    .metric-value.amber { color: var(--neon-amber); text-shadow: 0 0 20px rgba(255,159,28,0.3); }
    .metric-value.red { color: var(--neon-red); text-shadow: 0 0 20px rgba(255,59,74,0.3); }
    .metric-value.cyan { color: var(--neon-cyan); text-shadow: 0 0 20px rgba(0,180,216,0.3); }
    .metric-sub {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.6rem;
        color: var(--text-dim);
        margin-top: 4px;
        letter-spacing: 0.5px;
    }

    /* ── Map container ── */
    .map-wrap {
        position: relative;
        border-radius: 12px;
        overflow: hidden;
        animation: fadeSlideIn 1s ease-out 0.2s both;
    }
    .map-wrap::before {
        content: '';
        position: absolute;
        inset: 0;
        border-radius: 12px;
        border: 1px solid var(--border);
        pointer-events: none;
        z-index: 10;
        animation: borderGlow 4s ease-in-out infinite;
    }
    .map-wrap::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 40px;
        background: linear-gradient(180deg, rgba(5,8,15,0.5), transparent);
        pointer-events: none;
        z-index: 10;
        border-radius: 12px 12px 0 0;
    }
    iframe {
        border-radius: 12px !important;
        border: none !important;
    }

    /* ── Legend ── */
    .legend-strip {
        display: flex;
        gap: 6px;
        margin-top: 8px;
        flex-wrap: wrap;
        animation: fadeSlideIn 1.1s ease-out 0.3s both;
    }
    .legend-chip {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        background: var(--surface-2);
        border: 1px solid var(--border);
        border-radius: 20px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.65rem;
        color: var(--text-dim);
        letter-spacing: 0.5px;
        transition: all 0.2s ease;
    }
    .legend-chip:hover {
        background: var(--surface-3);
        color: var(--text);
    }
    .legend-pip {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        flex-shrink: 0;
    }

    /* ── Sidebar sections ── */
    .sb-section-title {
        font-family: 'Syne', sans-serif;
        font-weight: 700;
        font-size: 0.95rem;
        color: var(--text);
        letter-spacing: -0.2px;
        padding-bottom: 8px;
        margin-bottom: 12px;
        border-bottom: 1px solid var(--border);
        position: relative;
    }
    .sb-section-title::after {
        content: '';
        position: absolute;
        bottom: -1px;
        left: 0;
        width: 40px;
        height: 1px;
        background: var(--neon-amber);
    }
    .sb-section-title .accent {
        color: var(--neon-amber);
    }

    .sb-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.6rem;
        color: var(--text-ghost);
        text-transform: uppercase;
        letter-spacing: 2.5px;
        margin: 16px 0 6px;
    }

    .sb-coord-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        background: rgba(0,245,160,0.06);
        border: 1px solid rgba(0,245,160,0.15);
        border-radius: 8px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
        color: var(--neon-green);
        margin-bottom: 12px;
    }

    .sb-waiting {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        background: rgba(255,159,28,0.06);
        border: 1px solid rgba(255,159,28,0.12);
        border-radius: 8px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.68rem;
        color: var(--neon-amber);
        animation: breathe 3s ease-in-out infinite;
    }

    /* ── Hazard cards in sidebar ── */
    .hazard-card {
        background: var(--surface-2);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 8px;
        transition: all 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    .hazard-card:hover {
        border-color: rgba(255,255,255,0.1);
        background: var(--surface-3);
    }
    .hazard-card-type {
        font-family: 'Syne', sans-serif;
        font-weight: 600;
        font-size: 0.82rem;
        color: var(--text);
        margin-bottom: 3px;
    }
    .hazard-card-desc {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.65rem;
        color: var(--text-dim);
        line-height: 1.4;
        margin-bottom: 6px;
    }
    .hazard-card-meta {
        display: flex;
        align-items: center;
        gap: 8px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.6rem;
        color: var(--text-ghost);
    }
    .hazard-confirm-count {
        color: var(--neon-green);
    }

    /* ── Streamlit widget overrides ── */
    .stSelectbox label, .stTextArea label, .stNumberInput label,
    .stFileUploader label, .stTextInput label, .stSlider label {
        font-family: 'IBM Plex Mono', monospace !important;
        font-weight: 400 !important;
        color: var(--text-dim) !important;
        font-size: 0.7rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
    }

    .stButton > button {
        font-family: 'Syne', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: 0.3px;
        border-radius: 8px !important;
        transition: all 0.25s ease !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #ff9f1c, #e68a00) !important;
        border: none !important;
        color: #0a0f1c !important;
        font-weight: 700 !important;
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 0 25px rgba(255,159,28,0.4) !important;
        transform: translateY(-1px) !important;
    }

    div[data-testid="stMetric"] {
        background: var(--surface-2);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 14px;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: var(--void); }
    ::-webkit-scrollbar-thumb { background: var(--surface-3); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--text-ghost); }

    /* ── FOSS badge ── */
    .foss-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        background: rgba(177,74,237,0.08);
        border: 1px solid rgba(177,74,237,0.2);
        border-radius: 6px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.58rem;
        color: var(--neon-purple);
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── API helpers ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def fetch_hazards():
    try:
        resp = requests.get(f"{API_BASE}/hazards", timeout=5)
        resp.raise_for_status()
        return resp.json().get("hazards", [])
    except Exception:
        return []


def report_hazard(hazard_type, description, lat, lon, reported_by, image_file=None):
    form_data = {
        "type": hazard_type,
        "description": description,
        "latitude": str(lat),
        "longitude": str(lon),
        "reported_by": reported_by,
    }
    files = {}
    if image_file is not None:
        files["image"] = (image_file.name, image_file.getvalue(), image_file.type)
    try:
        resp = requests.post(f"{API_BASE}/hazards", data=form_data, files=files or None, timeout=10)
        resp.raise_for_status()
        return True, resp.json().get("message", "Hazard reported!")
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to backend. Is the server running?"
    except Exception as e:
        return False, f"Error: {e}"


def confirm_hazard(hazard_id):
    try:
        resp = requests.post(f"{API_BASE}/hazards/{hazard_id}/confirm", timeout=5)
        resp.raise_for_status()
        return True, resp.json()
    except Exception as e:
        return False, str(e)


def fetch_safety_score(lat, lon, radius=0.01):
    try:
        resp = requests.get(
            f"{API_BASE}/safety-score",
            params={"latitude": lat, "longitude": lon, "radius": radius},
            timeout=5,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


# ── Data ────────────────────────────────────────────────────────────────────
hazards = fetch_hazards()
safety = fetch_safety_score(CHENNAI_CENTER[0], CHENNAI_CENTER[1])

score_val = safety["safety_score"] if safety else "—"
score_label = safety["safety_label"] if safety else "Offline"
hazard_count = len(hazards)
confirmed = sum(1 for h in hazards if h.get("confirmed_count", 0) > 0)
backend_live = safety is not None

if isinstance(score_val, (int, float)):
    score_class = "green" if score_val >= 80 else ("amber" if score_val >= 60 else "red")
else:
    score_class = "amber"

# ── Header ──────────────────────────────────────────────────────────────────
status_dot_color = "var(--neon-green)" if backend_live else "var(--neon-red)"
status_text = "LIVE" if backend_live else "OFFLINE"

st.markdown(
    f"""
    <div class="sw-header">
        <div>
            <div class="sw-brand">
                <span class="sw-brand-safe">Safe</span><span class="sw-brand-walk">Walk</span>
            </div>
            <div class="sw-tagline">Pedestrian Safety Intelligence &middot; Chennai</div>
        </div>
        <div style="display:flex;align-items:center;gap:16px;">
            <span class="foss-badge">FOSS Hack 2026</span>
            <span class="sw-status">
                <span class="sw-status-dot" style="background:{status_dot_color};box-shadow:0 0 8px {status_dot_color};"></span>
                {status_text}
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Metrics ─────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="metrics-row">
        <div class="metric-card">
            <div class="metric-label">Safety Index</div>
            <div class="metric-value {score_class}">{score_val}</div>
            <div class="metric-sub">/ 100</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Threat Level</div>
            <div class="metric-value amber" style="font-size:0.9rem;">{score_label}</div>
            <div class="metric-sub">current status</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Active Hazards</div>
            <div class="metric-value red">{hazard_count}</div>
            <div class="metric-sub">reported</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Verified</div>
            <div class="metric-value cyan">{confirmed}</div>
            <div class="metric-sub">community confirmed</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Folium Map ──────────────────────────────────────────────────────────────
m = folium.Map(
    location=CHENNAI_CENTER,
    zoom_start=12,
    tiles="CartoDB dark_matter",
    control_scale=True,
)
LocateControl(auto_start=False, strings={"title": "Find me"}).add_to(m)

for h in hazards:
    lat = h.get("latitude")
    lon = h.get("longitude")
    if lat is None or lon is None:
        continue

    h_type = h.get("type", "unknown")
    cfg = HAZARD_CONFIG.get(h_type, {"icon": "circle-info", "color": "gray", "label": h_type, "hex": "#888", "glow": "rgba(136,136,136,0.3)"})
    conf_count = h.get("confirmed_count", 0)

    photo_html = ""
    if h.get("photo_url"):
        photo_html = f'<img src="{h["photo_url"]}" style="width:100%;max-height:100px;object-fit:cover;border-radius:6px;margin-top:8px;border:1px solid #1a1a2e;">'

    popup_html = f"""
    <div style="font-family:system-ui,-apple-system,sans-serif;min-width:210px;max-width:260px;padding:2px;">
        <div style="font-weight:700;font-size:13px;color:{cfg['hex']};margin-bottom:5px;letter-spacing:-0.2px;">
            {cfg['label']}
        </div>
        <div style="font-size:11.5px;color:#374151;margin-bottom:8px;line-height:1.45;">
            {h.get('description', 'No description')}
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;padding-top:6px;border-top:1px solid #e5e7eb;">
            <span style="font-size:10.5px;color:#6b7280;">by <b>{h.get('reported_by', 'anon')}</b></span>
            <span style="font-size:10.5px;color:#059669;font-weight:600;">{conf_count} verified</span>
        </div>
        {photo_html}
    </div>
    """

    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_html, max_width=280),
        tooltip=f"{cfg['label']} — click for details",
        icon=folium.Icon(icon=cfg["icon"], prefix="fa", color=cfg["color"]),
    ).add_to(m)

st.markdown('<div class="map-wrap">', unsafe_allow_html=True)
map_data = st_folium(m, height=520, use_container_width=True, returned_objects=["last_clicked"])
st.markdown('</div>', unsafe_allow_html=True)

if map_data and map_data.get("last_clicked"):
    st.session_state["clicked_lat"] = map_data["last_clicked"]["lat"]
    st.session_state["clicked_lng"] = map_data["last_clicked"]["lng"]

# ── Legend ──────────────────────────────────────────────────────────────────
legend_chips = "".join(
    f'<div class="legend-chip"><div class="legend-pip" style="background:{c["hex"]};box-shadow:0 0 6px {c["glow"]};"></div>{c["label"]}</div>'
    for c in HAZARD_CONFIG.values()
)
st.markdown(f'<div class="legend-strip">{legend_chips}</div>', unsafe_allow_html=True)

# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center;padding:8px 0 16px;">
            <div class="sw-brand" style="justify-content:center;">
                <span class="sw-brand-safe" style="font-size:1.4rem;">Safe</span><span class="sw-brand-walk" style="font-size:1.4rem;">Walk</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Report section ──
    st.markdown('<div class="sb-section-title"><span class="accent">//</span> Report Hazard</div>', unsafe_allow_html=True)

    clicked_lat = st.session_state.get("clicked_lat", None)
    clicked_lng = st.session_state.get("clicked_lng", None)

    if clicked_lat and clicked_lng:
        st.markdown(
            f'<div class="sb-coord-badge">&#9673; {clicked_lat:.5f}, {clicked_lng:.5f}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="sb-waiting">&#9678; Click map to set location</div>',
            unsafe_allow_html=True,
        )

    with st.form("report_form", clear_on_submit=True):
        hazard_type = st.selectbox(
            "TYPE",
            options=list(HAZARD_CONFIG.keys()),
            format_func=lambda x: HAZARD_CONFIG[x]["label"],
        )
        description = st.text_area("DESCRIPTION", placeholder="What did you observe?", max_chars=500, height=80)
        reported_by = "Shruthika"
        image = st.file_uploader("EVIDENCE", type=["jpg", "jpeg", "png"])

        col1, col2 = st.columns(2)
        with col1:
            lat_input = st.number_input(
                "LAT", value=clicked_lat if clicked_lat else CHENNAI_CENTER[0],
                format="%.6f", step=0.0001,
            )
        with col2:
            lng_input = st.number_input(
                "LNG", value=clicked_lng if clicked_lng else CHENNAI_CENTER[1],
                format="%.6f", step=0.0001,
            )

        submitted = st.form_submit_button("SUBMIT REPORT", use_container_width=True, type="primary")
        if submitted:
            if not description.strip():
                st.error("Description required.")
            else:
                success, msg = report_hazard(
                    hazard_type, description.strip(), lat_input, lng_input,
                    reported_by, image,
                )
                if success:
                    st.success(msg)
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(msg)

    # ── Confirm section ──
    st.markdown('<div class="sb-section-title" style="margin-top:24px;"><span class="accent">//</span> Verify Reports</div>', unsafe_allow_html=True)

    if hazards:
        for h in hazards[:8]:
            h_type = h.get("type", "unknown")
            cfg = HAZARD_CONFIG.get(h_type, {"label": h_type, "hex": "#888"})
            desc_short = (h.get("description", "")[:45] + "...") if len(h.get("description", "")) > 45 else h.get("description", "")
            conf = h.get("confirmed_count", 0)

            st.markdown(
                f"""
                <div class="hazard-card">
                    <div class="hazard-card-type" style="color:{cfg['hex']};">{cfg['label']}</div>
                    <div class="hazard-card-desc">{desc_short}</div>
                    <div class="hazard-card-meta">
                        <span class="hazard-confirm-count">{conf} verified</span>
                        <span>&middot;</span>
                        <span>{h.get('reported_by', 'anon')}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Verify", key=f"confirm_{h['id']}", use_container_width=True):
                ok, result = confirm_hazard(h["id"])
                if ok:
                    st.success(f"Verified! ({result.get('confirmed_count', conf + 1)})")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(result)
    else:
        st.markdown(
            '<div class="sb-waiting" style="margin-top:8px;">No reports yet</div>',
            unsafe_allow_html=True,
        )

    # ── Safety score section ──
    st.markdown('<div class="sb-section-title" style="margin-top:24px;"><span class="accent">//</span> Safety Scan</div>', unsafe_allow_html=True)

    with st.form("score_form"):
        sc_lat = st.number_input("LAT", value=CHENNAI_CENTER[0], format="%.6f", key="sc_lat")
        sc_lon = st.number_input("LNG", value=CHENNAI_CENTER[1], format="%.6f", key="sc_lon")
        sc_radius = st.slider("SCAN RADIUS (KM)", min_value=0.5, max_value=5.0, value=1.0, step=0.5)

        if st.form_submit_button("SCAN AREA", use_container_width=True):
            result = fetch_safety_score(sc_lat, sc_lon, radius=sc_radius / 100)
            if result:
                st.metric("Safety Score", f"{result['safety_score']} / 100")
                st.info(result["safety_label"])
                st.caption(f"{result['nearby_hazards_count']} hazards in range")
            else:
                st.error("Backend offline")

    # ── Footer ──
    st.markdown(
        """
        <div style="text-align:center;margin-top:32px;padding-top:16px;border-top:1px solid rgba(255,255,255,0.04);">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.55rem;color:#334155;letter-spacing:2px;text-transform:uppercase;">
                Random Forest Rangers
            </div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.5rem;color:#1e293b;margin-top:4px;letter-spacing:1px;">
                FOSS Hack 2026 &middot; MIT License
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
