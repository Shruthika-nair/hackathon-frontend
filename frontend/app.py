import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Chennai Explorer",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Custom styling ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Outfit:wght@300;400;600&display=swap');

    .stApp {
        background: #0a0f1a;
    }

    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 0 !important;
        max-width: 100% !important;
    }

    h1.title-text {
        font-family: 'DM Serif Display', serif;
        color: #f0e6d3;
        font-size: 2.8rem;
        letter-spacing: -0.5px;
        margin-bottom: 0;
        padding-bottom: 0;
    }

    .subtitle-text {
        font-family: 'Outfit', sans-serif;
        font-weight: 300;
        color: #8b9dc3;
        font-size: 1.05rem;
        margin-top: -0.5rem;
        margin-bottom: 1.2rem;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    .coord-badge {
        display: inline-block;
        font-family: 'Outfit', monospace;
        font-weight: 400;
        font-size: 0.8rem;
        color: #c4956a;
        background: rgba(196, 149, 106, 0.1);
        border: 1px solid rgba(196, 149, 106, 0.25);
        border-radius: 20px;
        padding: 4px 14px;
        margin-bottom: 1rem;
        letter-spacing: 1px;
    }

    /* Map container */
    [data-testid="stDecoration"] {
        display: none;
    }

    iframe {
        border-radius: 12px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Header ---
st.markdown('<h1 class="title-text">Chennai</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle-text">Capital of Tamil Nadu</p>', unsafe_allow_html=True
)
st.markdown(
    '<span class="coord-badge">13.0827° N &nbsp;·&nbsp; 80.2707° E</span>',
    unsafe_allow_html=True,
)

# --- Map ---
chennai = pd.DataFrame({"lat": [13.0827], "lon": [80.2707]})
st.map(chennai, latitude="lat", longitude="lon", zoom=11, use_container_width=True)
