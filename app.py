"""
SIH27143 - Oil Spill Detection & Vessel Correlation
Vessel Correlate Platform — Production Frontend (Audit-Fixed)
"""

import hashlib
import json
import os
import uuid
from datetime import datetime, timedelta

import folium
import folium.plugins
import streamlit as st
from folium import Element
from folium.plugins import MiniMap, Fullscreen
from streamlit_folium import st_folium

# ============================================================================
# Constants & Configuration
# ============================================================================
APP_TITLE = "Vessel Correlate"
APP_SUBTITLE = "Oil Spill Detection & Vessel Correlation Platform"
APP_VERSION = "v2.4.1"

DEMO_DATA_DIR = os.path.join(os.path.dirname(__file__), "public", "demo_data")
DEFAULT_TIMESTAMP = "2026-09-05T06:00:00Z"
DEMO_DEMO_END = datetime(2026, 9, 5)
DEMO_DEMO_START = DEMO_DEMO_END - timedelta(days=7)
DEMO_EARLIEST = datetime(2026, 8, 1)
PROXIMITY_MIN_KM = 1.0
PROXIMITY_MAX_KM = 25.0
PROXIMITY_DEFAULT_KM = 5.0

# Theme tokens
THEME = {
    "bg_dark": "#0B0F19",
    "bg_card": "rgba(21, 26, 40, 0.75)",
    "bg_card_hover": "rgba(26, 32, 48, 0.9)",
    "bg_sidebar": "rgba(11, 15, 25, 0.95)",
    "border_subtle": "rgba(255, 255, 255, 0.08)",
    "border_active": "rgba(0, 230, 118, 0.4)",
    "accent_green": "#00E676",
    "accent_orange": "#FFA000",
    "accent_red": "#FF3366",
    "accent_blue": "#00B0FF",
    "accent_yellow": "#FFD600",
    "text_primary": "#E8EAED",
    "text_secondary": "#9AA0A6",
    "text_muted": "#5F6368",
    "shadow_glass": "0 8px 32px rgba(0, 0, 0, 0.6)",
    "shadow_hover": "0 16px 48px rgba(0, 0, 0, 0.7)",
}

# Role definitions
ROLES = {
    "coast_guard": {
        "label": "🛡️ Coast Guard Analyst",
        "description": "Action items, interdiction targets, vessel alerts",
        "color": "#FF3366",
        "clearance": "TS",
    },
    "incident_commander": {
        "label": "⚓ Incident Commander",
        "description": "Unified operational overview, resource deployment",
        "color": "#00B0FF",
        "clearance": "S",
    },
    "auditor": {
        "label": "🌿 Environmental Auditor",
        "description": "Impact metrics, damage assessment, compliance",
        "color": "#00E676",
        "clearance": "C",
    },
}


# ============================================================================
# CSS Design System (built once at import, stored as module constant)
# ============================================================================
def _build_design_system_css() -> str:
    """Build the complete glassmorphic CSS as a single string."""
    return f"""
    <style>
    :root {{
        --bg-dark: {THEME['bg_dark']};
        --bg-card: {THEME['bg_card']};
        --bg-card-hover: {THEME['bg_card_hover']};
        --bg-sidebar: {THEME['bg_sidebar']};
        --border-subtle: {THEME['border_subtle']};
        --border-active: {THEME['border_active']};
        --accent-green: {THEME['accent_green']};
        --accent-orange: {THEME['accent_orange']};
        --accent-red: {THEME['accent_red']};
        --accent-blue: {THEME['accent_blue']};
        --text-primary: {THEME['text_primary']};
        --text-secondary: {THEME['text_secondary']};
        --text-muted: {THEME['text_muted']};
        --shadow-glass: {THEME['shadow_glass']};
        --shadow-hover: {THEME['shadow_hover']};
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --font-stack: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }}

    /* NOTE: No universal margin/padding reset — Streamlit's React widgets need
       their default spacing. We scope resets to explicit element types only. */
    html, body, div, span {{ box-sizing: border-box; }}

    html, body {{
        background: var(--bg-dark) !important;
        color: var(--text-primary) !important;
        font-family: var(--font-stack) !important;
        -webkit-font-smoothing: antialiased;
    }}

    /* Streamlit chrome elimination */
    #MainMenu, footer, header,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stHeader"] {{
        visibility: hidden !important;
        display: none !important;
        height: 0 !important;
    }}

    /* Full-bleed layout */
    .block-container {{
        padding: 0 !important;
        max-width: 100% !important;
        margin: 0 !important;
    }}
    .stApp {{
        background: var(--bg-dark) !important;
        background-image: none !important;
        color: var(--text-primary) !important;
    }}

    /* ================================================================
       AUTHENTICATION PORTAL
       ================================================================ */
    .auth-wrapper {{
        position: fixed;
        inset: 0;
        z-index: 9999;
        background: linear-gradient(135deg, #0B0F19 0%, #1a1f2e 50%, #0B0F19 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        overflow: auto;
    }}
    .auth-wrapper::before {{
        content: '';
        position: absolute;
        top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(ellipse at center, rgba(0, 230, 118, 0.05) 0%, transparent 50%);
        animation: auth-pulse 8s ease-in-out infinite;
        pointer-events: none;
    }}
    @keyframes auth-pulse {{
        0%, 100% {{ opacity: 0.5; transform: scale(1); }}
        50% {{ opacity: 1; transform: scale(1.1); }}
    }}
    .auth-card {{
        background: var(--bg-card) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-lg) !important;
        padding: 3rem !important;
        max-width: 480px;
        width: 100%;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8), 0 0 40px rgba(0, 230, 118, 0.1) !important;
        position: relative;
        z-index: 1;
        display: flex;
        flex-direction: column;
    }}
    .auth-header {{ text-align: center; margin-bottom: 2.5rem; }}
    .auth-logo {{
        font-size: 3.5rem;
        margin-bottom: 1rem;
        display: block;
        filter: drop-shadow(0 0 20px rgba(0, 230, 118, 0.5));
    }}
    .auth-title {{
        color: var(--accent-green) !important;
        font-size: 1.5rem !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        margin-bottom: 0.5rem !important;
    }}
    .auth-subtitle {{
        color: var(--text-secondary) !important;
        font-size: 0.9rem !important;
        font-weight: 400 !important;
    }}
    /* auth-form / auth-input-group / auth-label removed — inputs now use Streamlit native labels */

    /* Auth form inputs — vertical gaps between each field */
    .auth-card [data-testid="stHorizontalBlock"] > div,
    [data-testid="stVerticalBlock"] .stTextInput,
    [data-testid="stVerticalBlock"] .stSelectbox,
    [data-testid="stVerticalBlock"] .stButton {{
        margin-bottom: 1.25rem !important;
    }}

    /* Auth card form labels — uppercase styled */
    .auth-card [data-testid="stTextInput"] label,
    .auth-card [data-testid="stSelectbox"] label {{
        color: var(--text-secondary) !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        margin-bottom: 0.4rem !important;
    }}

    /* Auth card text input inner styling */
    [data-testid="stTextInput"] input[type="text"],
    [data-testid="stTextInput"] input[type="password"] {{
        background: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.95rem !important;
        width: 100% !important;
    }}
    [data-testid="stTextInput"] input[type="text"]:focus,
    [data-testid="stTextInput"] input[type="password"]:focus {{
        border-color: var(--accent-green) !important;
        box-shadow: 0 0 0 2px rgba(0, 230, 118, 0.2) !important;
        outline: none !important;
    }}
    [data-testid="stTextInput"] input::placeholder {{
        color: var(--text-muted) !important;
    }}

    /* ================================================================
       FORM CONTROLS
       ================================================================ */
    .stSelectbox > div > div {{
        background: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
    }}

    .stButton > button {{
        width: 100% !important;
        background: linear-gradient(135deg, #00E676, #00C853) !important;
        color: #000 !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.9rem 2rem !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 20px rgba(0, 230, 118, 0.3) !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 8px 30px rgba(0, 230, 118, 0.5) !important;
    }}
    .stButton > button:active {{
        transform: translateY(0) scale(0.98) !important;
    }}

    /* ================================================================
       SIDEBAR CONTROL DESK
       ================================================================ */
    [data-testid="stSidebar"] {{
        background: var(--bg-sidebar) !important;
        backdrop-filter: blur(12px) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }}
    [data-testid="stSidebar"] .block-container {{
        padding-top: 1.5rem !important;
        padding-left: 1.25rem !important;
        padding-right: 1.25rem !important;
    }}
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {{
        color: var(--accent-green) !important;
        font-size: 0.9rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        border-bottom: 1px solid var(--border-subtle);
        padding-bottom: 0.5rem !important;
        margin-bottom: 1rem !important;
    }}
    [data-testid="stSidebar"] .stSlider label {{
        color: var(--text-secondary) !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
    }}

    /* ================================================================
       KPI METRIC CARDS (FIX U3: use wrapper divs for distinct accents)
       ================================================================ */
    .kpi-card {{
        position: relative !important;
        overflow: hidden !important;
    }}
    .kpi-card::after {{
        content: '';
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 3px !important;
        opacity: 0.85 !important;
    }}
    .kpi-card.kpi-green::after  {{ background: var(--accent-green); }}
    .kpi-card.kpi-blue::after   {{ background: var(--accent-blue); }}
    .kpi-card.kpi-red::after    {{ background: var(--accent-red); }}
    .kpi-card.kpi-orange::after {{ background: var(--accent-orange); }}

    [data-testid="stMetric"] {{
        background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-card-hover) 100%) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-md) !important;
        padding: 1.5rem 1.75rem !important;
        box-shadow: var(--shadow-glass) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
        overflow: hidden !important;
    }}
    [data-testid="stMetric"]:hover {{
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: var(--shadow-hover) !important;
        border-color: var(--border-active) !important;
    }}
    [data-testid="stMetric"] label {{
        color: var(--text-secondary) !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        margin-bottom: 0.5rem !important;
    }}
    [data-testid="stMetric"] [data-testid="stMetricValue"] {{
        color: var(--text-primary) !important;
        font-size: 2.4rem !important;
        font-weight: 800 !important;
        line-height: 1 !important;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3) !important;
    }}
    [data-testid="stMetric"] [data-testid="stMetricDelta"] {{
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        margin-top: 0.5rem !important;
    }}

    /* ================================================================
       MAP VIEWPORT
       ================================================================ */
    .folium-map,
    iframe[title*="folium"],
    iframe[title*="streamlit-folium"] {{
        border-radius: var(--radius-lg) !important;
        box-shadow: var(--shadow-glass) !important;
        border: 1px solid var(--border-subtle) !important;
        margin: 0 !important;
    }}
    div:has(> iframe[title*="folium"]) {{
        border-radius: var(--radius-lg) !important;
        overflow: hidden !important;
    }}

    /* ================================================================
       TYPOGRAPHY (FIX U9: prevent double-uppercase in dashboard header)
       ================================================================ */
    h1, h2, h3 {{
        font-family: var(--font-stack) !important;
        color: var(--text-primary) !important;
        font-weight: 700 !important;
    }}
    h1 {{
        font-size: 1.75rem !important;
        letter-spacing: 0.5px !important;
    }}
    h2 {{
        color: var(--accent-green) !important;
        font-size: 1.15rem !important;
        letter-spacing: 0.3px !important;
    }}
    h3 {{
        color: var(--text-secondary) !important;
        font-size: 0.85rem !important;
    }}
    .dash-title {{
        color: var(--accent-green) !important;
        font-size: 1.4rem !important;
        font-weight: 800 !important;
        text-transform: none !important;
        margin: 0 !important;
    }}

    /* ================================================================
       TABS (FIX U8: dual selector for cross-version compatibility)
       ================================================================ */
    .stTabs [data-testid="stTabBar"],
    .stTabs [data-baseweb="tabList"] {{
        background: var(--bg-card) !important;
        border-radius: var(--radius-md) var(--radius-md) 0 0 !important;
        border: 1px solid var(--border-subtle) !important;
        border-bottom: none !important;
        padding: 0.5rem 0.5rem 0 !important;
    }}
    .stTabs [data-testid="stTab"],
    .stTabs [data-baseweb="tab"] {{
        background: transparent !important;
        color: var(--text-secondary) !important;
        border: none !important;
        border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        padding: 0.6rem 1.25rem !important;
    }}
    .stTabs [data-testid="stTab"]:hover,
    .stTabs [data-baseweb="tab"]:hover {{
        background: rgba(0, 230, 118, 0.1) !important;
        color: var(--accent-green) !important;
    }}
    .stTabs [data-testid="stTab"][aria-selected="true"],
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        background: var(--bg-card) !important;
        color: var(--accent-green) !important;
        border-bottom: 2px solid var(--accent-green) !important;
    }}

    /* ================================================================
       MESSAGES & ALERTS
       ================================================================ */
    .stAlert {{
        border-radius: var(--radius-md) !important;
        backdrop-filter: blur(8px) !important;
    }}
    .stSuccess {{
        background: rgba(0, 230, 118, 0.1) !important;
        border: 1px solid rgba(0, 230, 118, 0.3) !important;
        border-left: 4px solid var(--accent-green) !important;
    }}
    .stError {{
        background: rgba(255, 51, 102, 0.1) !important;
        border: 1px solid rgba(255, 51, 102, 0.3) !important;
        border-left: 4px solid var(--accent-red) !important;
    }}
    .stWarning {{
        background: rgba(255, 160, 0, 0.1) !important;
        border: 1px solid rgba(255, 160, 0, 0.3) !important;
        border-left: 4px solid var(--accent-orange) !important;
    }}
    .stInfo {{
        background: rgba(0, 176, 255, 0.1) !important;
        border: 1px solid rgba(0, 176, 255, 0.3) !important;
        border-left: 4px solid var(--accent-blue) !important;
    }}

    /* ================================================================
       OPERATOR PROFILE
       ================================================================ */
    .operator-card {{
        background: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-md) !important;
        padding: 1rem !important;
        margin-bottom: 1rem !important;
    }}
    .operator-name {{
        color: var(--text-primary) !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
    }}
    .operator-role {{
        color: var(--accent-green) !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }}
    .operator-clearance {{
        color: var(--text-muted) !important;
        font-size: 0.7rem !important;
    }}
    .status-badge {{
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 50px;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .badge-live {{ background: rgba(0, 230, 118, 0.15); color: #00E676; border: 1px solid rgba(0, 230, 118, 0.3); }}
    .badge-red {{ background: rgba(255, 51, 102, 0.15); color: #FF3366; border: 1px solid rgba(255, 51, 102, 0.3); }}
    .badge-blue {{ background: rgba(0, 176, 255, 0.15); color: #00B0FF; border: 1px solid rgba(0, 176, 255, 0.3); }}
    .badge-orange {{ background: rgba(255, 160, 0, 0.15); color: #FFA000; border: 1px solid rgba(255, 160, 0, 0.3); }}

    /* ================================================================
       SLIDERS, EXPANDERS, DIVIDERS
       ================================================================ */
    .stSlider > div > div > div {{ background: var(--border-subtle) !important; }}
    .stSlider [data-testid="stThumbValue"] {{
        color: var(--accent-green) !important;
        font-weight: 700 !important;
    }}
    .streamlit-expander {{
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-md) !important;
    }}
    .streamlit-expander:hover {{ border-color: var(--border-active) !important; }}
    hr {{
        border: none !important;
        border-top: 1px solid var(--border-subtle) !important;
        margin: 1.5rem 0 !important;
    }}

    /* ================================================================
       SCROLLBAR & ANIMATIONS
       ================================================================ */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: rgba(0, 0, 0, 0.2); }}
    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(180deg, var(--accent-green), var(--accent-orange));
        border-radius: 3px;
    }}
    @keyframes slideIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .animate-in {{ animation: slideIn 0.4s ease-out; }}
    @keyframes pulse-glow {{
        0%, 100% {{ box-shadow: 0 0 20px rgba(0, 230, 118, 0.3); }}
        50% {{ box-shadow: 0 0 40px rgba(0, 230, 118, 0.6); }}
    }}
    .pulse-live {{ animation: pulse-glow 3s infinite; }}

    /* ================================================================
       RESPONSIVE (FIX U7: add 480px breakpoint)
       ================================================================ */
    @media (max-width: 1200px) {{
        [data-testid="stMetric"] [data-testid="stMetricValue"] {{ font-size: 1.8rem !important; }}
    }}
    @media (max-width: 768px) {{
        .auth-card {{ padding: 2rem !important; }}
        [data-testid="stMetric"] [data-testid="stMetricValue"] {{ font-size: 1.4rem !important; }}
    }}
    @media (max-width: 480px) {{
        .auth-card {{ padding: 1.5rem !important; max-width: 95vw; }}
        [data-testid="stMetric"] [data-testid="stMetricValue"] {{ font-size: 1.2rem !important; }}
    }}
    </style>
    """


# Module-level constant — built once at import, never recomputed
DESIGN_SYSTEM_CSS = _build_design_system_css()

# CSS is injected once at app startup. Streamlit reruns skip this because the
# module is only imported once per session. We use a session flag to prevent
# duplicate injection on the same rerun.
_CSS_INJECTED_KEY = "_design_css_injected"


def inject_design_system() -> None:
    """Inject the design system CSS (only once per session)."""
    if not st.session_state.get(_CSS_INJECTED_KEY, False):
        st.markdown(DESIGN_SYSTEM_CSS, unsafe_allow_html=True)
        st.session_state[_CSS_INJECTED_KEY] = True


# ============================================================================
# Safe Data Access
# ============================================================================
def safe_get(obj, *keys, default=None):
    """Type-safe nested accessor — never raises KeyError/TypeError/IndexError."""
    try:
        cur = obj
        for k in keys:
            cur = cur[k]
        return cur if cur is not None else default
    except (KeyError, TypeError, IndexError):
        return default


# ============================================================================
# Demo Data Loading
# ============================================================================
@st.cache_data(ttl=300, show_spinner=False)  # FIX P4: shorter TTL for fresh data
def get_demo_data() -> dict:
    """Load demo data from files, falling back to inline mocks."""

    def load_json(filename: str):
        path = os.path.join(DEMO_DATA_DIR, filename)
        try:
            if not os.path.exists(path):
                return None
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not (isinstance(data, dict) and data.get("type") == "FeatureCollection"):
                return None
            if "metadata" not in data:
                data["metadata"] = {"timestamp": DEFAULT_TIMESTAMP}
            return data
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            return None
        except Exception:
            return None

    spills = load_json("spill_polygons.geojson")
    ais = load_json("ais_tracks.geojson")
    sar = load_json("sar_image.geojson")

    fallback_spills = {
        "type": "FeatureCollection",
        "metadata": {"timestamp": DEFAULT_TIMESTAMP},
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "id": "SPILL-001", "name": "Spill Zone Alpha",
                    "area_km2": 14.2, "confidence": 0.94, "severity": "critical",
                    "source_vessel": "MT Prestige", "detected_time": "2026-09-04T18:30:00Z",
                },
                "geometry": {"type": "Polygon", "coordinates": [[
                    [72.80, 18.92], [72.88, 18.90], [72.96, 18.93],
                    [72.98, 18.98], [72.95, 19.05], [72.88, 19.08],
                    [72.82, 19.06], [72.78, 19.00], [72.80, 18.92],
                ]]},
            },
            {
                "type": "Feature",
                "properties": {
                    "id": "SPILL-002", "name": "Spill Zone Bravo",
                    "area_km2": 6.8, "confidence": 0.78, "severity": "moderate",
                    "source_vessel": "Hanjin Container", "detected_time": "2026-09-05T02:15:00Z",
                },
                "geometry": {"type": "Polygon", "coordinates": [[
                    [72.90, 18.96], [72.97, 18.94], [73.04, 18.97],
                    [73.06, 19.03], [73.02, 19.08], [72.94, 19.10],
                    [72.88, 19.06], [72.90, 18.96],
                ]]},
            },
        ],
    }

    fallback_ais = {
        "type": "FeatureCollection",
        "metadata": {"timestamp": DEFAULT_TIMESTAMP},
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "mmsi": "119010123", "name": "MT Prestige", "type": "Tanker",
                    "speed_knots": 3.2, "heading": 180, "flag": "Panama",
                    "alert_level": "RED", "spill_risk": "HIGH - Correlated with SPILL-001",
                },
                "geometry": {"type": "LineString", "coordinates": [
                    [72.78, 18.88], [72.82, 18.92], [72.86, 18.95], [72.90, 18.97],
                ]},
            },
            {
                "type": "Feature",
                "properties": {
                    "mmsi": "241010456", "name": "Hanjin Container", "type": "Container Ship",
                    "speed_knots": 14.8, "heading": 90, "flag": "Singapore",
                    "alert_level": "ORANGE", "spill_risk": "MEDIUM - Secondary source",
                },
                "geometry": {"type": "LineString", "coordinates": [
                    [72.80, 19.02], [72.90, 19.00], [73.00, 18.98], [73.10, 18.96],
                ]},
            },
            {
                "type": "Feature",
                "properties": {
                    "mmsi": "366542180", "name": "ICGS Samar", "type": "Patrol Vessel",
                    "speed_knots": 18.5, "heading": 270, "flag": "India",
                    "alert_level": "BLUE", "spill_risk": "RESPONDER - CG intercept",
                },
                "geometry": {"type": "LineString", "coordinates": [
                    [72.95, 19.05], [72.85, 19.05], [72.75, 19.05], [72.65, 19.05],
                ]},
            },
            {
                "type": "Feature",
                "properties": {
                    "mmsi": "419000678", "name": "Sea Hawk Guardian", "type": "Supply Vessel",
                    "speed_knots": 12.3, "heading": 360, "flag": "India",
                    "alert_level": "GREEN", "spill_risk": "RESPONSE - Boom deployment",
                },
                "geometry": {"type": "LineString", "coordinates": [
                    [72.88, 18.92], [72.88, 18.98], [72.88, 19.04], [72.88, 19.10],
                ]},
            },
            {
                "type": "Feature",
                "properties": {
                    "mmsi": "538000452", "name": "Ever Given", "type": "Container Ship",
                    "speed_knots": 16.2, "heading": 45, "flag": "Panama",
                    "alert_level": "GREY", "spill_risk": "LOW - Clear transit",
                },
                "geometry": {"type": "LineString", "coordinates": [
                    [72.60, 18.70], [72.76, 18.80], [72.92, 18.90], [73.08, 19.00],
                ]},
            },
        ],
    }

    fallback_sar = {
        "type": "FeatureCollection",
        "metadata": {"timestamp": DEFAULT_TIMESTAMP},
        "features": [{
            "type": "Feature",
            "properties": {
                "date": "2026-09-05T04:42:00Z", "sensor": "SAR Sentinel-1 GRD",
                "confidence_pct": 98.7, "notes": "Clear oil detection - wind 2.3 m/s",
            },
            "geometry": {"type": "Polygon", "coordinates": [[
                [72.60, 18.70], [73.20, 18.70], [73.20, 19.20],
                [72.60, 19.20], [72.60, 18.70],
            ]]},
        }],
    }

    return {
        "spills": spills or fallback_spills,
        "ais": ais or fallback_ais,
        "sar": sar or fallback_sar,
    }


# ============================================================================
# Telemetry Computation
# ============================================================================
@st.cache_data(ttl=60, show_spinner=False)
def compute_telemetry(data: dict) -> dict:
    """Compute KPI metrics from demo data."""
    spills = safe_get(data, "spills", "features", default=[]) or []
    vessels = safe_get(data, "ais", "features", default=[]) or []
    sar = safe_get(data, "sar", "features", 0, "properties", default={}) or {}

    total_area = sum(safe_get(s, "properties", "area_km2", default=0) or 0 for s in spills)
    critical = sum(1 for s in spills if safe_get(s, "properties", "severity") == "critical")
    anomalous = sum(1 for v in vessels
                    if safe_get(v, "properties", "alert_level") in ("RED", "ORANGE"))
    correlated = sum(1 for v in vessels
                     if safe_get(v, "properties", "alert_level") == "RED")
    sar_cov = safe_get(sar, "confidence_pct", default=98.0) or 98.0

    return {
        "active_signals": len(vessels),
        "correlated_targets": correlated,
        "anomalous_targets": anomalous,
        "system_health": round(float(sar_cov), 1),
        "total_area_km2": round(total_area, 1),
        "critical_zones": critical,
        "total_spills": len(spills),
    }


# ============================================================================
# Map Builder (FIX C1/P1: cache by content hash, not unhashable dict)
# ============================================================================
def _data_signature(data: dict) -> str:
    """Compute a stable hash for a data dict to use as cache key."""
    try:
        payload = json.dumps({
            "spills": data.get("spills", {}).get("features", []),
            "ais": data.get("ais", {}).get("features", []),
            "sar": data.get("sar", {}).get("features", []),
        }, sort_keys=True, default=str)
        return hashlib.md5(payload.encode("utf-8")).hexdigest()
    except (TypeError, ValueError):
        # Deterministic fallback — content can't be serialized but the
        # structure is stable, so a constant hash is still deterministic
        return "4d3e6f8a1b2c9d0e1f2a3b4c5d6e7f8"


@st.cache_resource(show_spinner=False)
def _build_map_cached(data_sig: str, _data: dict) -> folium.Map:
    """Cached map builder. The string signature is hashable, the data is passed through."""
    m = folium.Map(
        location=[18.96, 72.85],
        zoom_start=11,
        tiles="OpenStreetMap",
        control_scale=True,
    )
    dark_css = "<style>.leaflet-tile-pane { filter: invert(100%) hue-rotate(180deg) brightness(95%) contrast(90%); }</style>"
    m.get_root().header.add_child(Element(dark_css))

    # Severity color map (FIX Q7: distinct color for "low")
    severity_colors = {
        "critical": "#FF3366",
        "moderate": "#FFA000",
        "low": "#FFD600",
    }
    alert_colors = {
        "RED": "#FF3366", "ORANGE": "#FFA000", "BLUE": "#00B0FF",
        "GREEN": "#00E676", "GREY": "#5F6368",
    }

    # SAR Image layer
    folium.GeoJson(
        safe_get(_data, "sar", default={}) or {},
        name="SAR Detection",
        style_function=lambda _: {
            "fillColor": "#FFA000", "color": "#FF8F00",
            "weight": 2, "fillOpacity": 0.12, "dashArray": "6, 4",
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["date", "sensor", "confidence_pct", "notes"],
            aliases=["📅 Date:", "🛰️ Sensor:", "📊 Coverage:", "📝 Notes:"],
        ),
    ).add_to(m)

    # Spill polygons layer
    def spill_style(f):
        sev = safe_get(f, "properties", "severity", default="moderate")
        c = severity_colors.get(sev, "#FFA000")
        return {"fillColor": c, "color": c, "weight": 2, "fillOpacity": 0.35}

    folium.GeoJson(
        safe_get(_data, "spills", default={}) or {},
        name="Oil Spill Zones",
        style_function=spill_style,
        tooltip=folium.GeoJsonTooltip(
            fields=["id", "name", "area_km2", "confidence", "severity", "source_vessel"],
            aliases=["🆔 ID:", "🌊 Zone:", "📐 Area (km²):", "🎯 Confidence:", "⚠️ Severity:", "🚢 Source:"],
        ),
    ).add_to(m)

    # AIS tracks layer
    def ais_style(f):
        lvl = safe_get(f, "properties", "alert_level", default="GREY")
        c = alert_colors.get(lvl, "#5F6368")
        dash = "4, 4" if lvl == "GREEN" else None
        return {"color": c, "weight": 4, "opacity": 0.9, "dashArray": dash}

    folium.GeoJson(
        safe_get(_data, "ais", default={}) or {},
        name="AIS Vessel Tracks",
        style_function=ais_style,
        tooltip=folium.GeoJsonTooltip(
            fields=["name", "mmsi", "type", "speed_knots", "heading", "alert_level", "spill_risk"],
            aliases=["🚢 Vessel:", "🎯 MMSI:", "📦 Type:", "⚡ Speed (kn):", "🧭 Heading:", "🔴 Alert:", "💧 Risk:"],
        ),
    ).add_to(m)

    folium.LayerControl(collapsed=False, position="topright").add_to(m)

    return m


def build_map(data: dict) -> folium.Map:
    """Public map builder. Uses content-hash for cache key (FIX C1/P1)."""
    sig = _data_signature(data)
    return _build_map_cached(sig, data)




# ============================================================================
# Sidebar: Control Desk
# ============================================================================
def render_sidebar() -> None:
    """Render the sidebar control desk."""
    with st.sidebar:
        # Operator Profile Card
        st.markdown("### 👤 Operator Profile")
        st.markdown('<div class="operator-card">', unsafe_allow_html=True)
        st.markdown('<div class="operator-name">CPO Sarah Mitchell</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="operator-role">🛡️ Coast Guard Analyst</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="operator-clearance">Clearance: TS</div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")

        # Time Scrubber
        st.markdown("### 📅 Observation Window")
        try:
            date_range = st.date_input(
                "Date Range:",
                value=(DEMO_DEMO_START.date(), DEMO_DEMO_END.date()),
                min_value=DEMO_EARLIEST.date(),
                max_value=DEMO_DEMO_END.date(),
                key="obs_window",
            )
            if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
                st.caption(f"Window: {date_range[0]} → {date_range[1]}")
            elif hasattr(date_range, "isoformat"):
                st.caption(f"Single date: {date_range.isoformat()}")
        except Exception:
            pass

        st.markdown("---")

        # Proximity Threshold
        st.markdown("### 📡 Proximity Threshold")
        threshold = st.slider(
            "Spatial radius (km):",
            min_value=PROXIMITY_MIN_KM,
            max_value=PROXIMITY_MAX_KM,
            value=PROXIMITY_DEFAULT_KM,
            step=0.5,
            help="Minimum distance from spill zone to flag vessel correlation.",
            key="proximity_slider",
        )
        st.caption(f"Current: {threshold} km")

        st.markdown("---")

        # System Status
        st.markdown("### 🟢 System Status")
        st.markdown(
            '<span class="status-badge badge-live pulse-live">● LIVE</span>'
            ' <span style="color: #9AA0A6; font-size: 0.8rem;">AIS Feed Active</span>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<span class="status-badge badge-blue">● SAR</span>'
            ' <span style="color: #9AA0A6; font-size: 0.8rem;">Sentinel-1 IW Mode</span>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<span class="status-badge badge-orange">● GEO</span>'
            ' <span style="color: #9AA0A6; font-size: 0.8rem;">Processing 2026-09-05</span>',
            unsafe_allow_html=True,
        )


# ============================================================================
# Dashboard: Telemetry KPIs (FIX U3/U4: distinct accent colors via wrapper class)
# ============================================================================
def render_telemetry_bar(telemetry: dict) -> None:
    """Render the 4-column KPI telemetry bar."""
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        st.markdown('<div class="kpi-card kpi-green">', unsafe_allow_html=True)
        st.metric(
            "📡 Active AIS Signals",
            str(telemetry["active_signals"]),
            delta=f"{telemetry['active_signals']} vessels tracked",
            delta_color="normal",
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with kpi2:
        st.markdown('<div class="kpi-card kpi-blue">', unsafe_allow_html=True)
        st.metric(
            "🎯 Correlated Targets",
            str(telemetry["correlated_targets"]),
            delta="High confidence match" if telemetry["correlated_targets"] > 0 else "No matches",
            delta_color="off" if telemetry["correlated_targets"] > 0 else "normal",
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with kpi3:
        st.markdown('<div class="kpi-card kpi-red">', unsafe_allow_html=True)
        st.metric(
            "⚠️ Anomalous Targets",
            str(telemetry["anomalous_targets"]),
            delta=f"{telemetry['critical_zones']} critical zones" if telemetry["critical_zones"] > 0 else "All clear",
            delta_color="inverse" if telemetry["anomalous_targets"] > 0 else "normal",
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with kpi4:
        st.markdown('<div class="kpi-card kpi-orange">', unsafe_allow_html=True)
        st.metric(
            "💚 System Health",
            f"{telemetry['system_health']}%",
            delta="SAR Coverage nominal",
            delta_color="normal",
        )
        st.markdown('</div>', unsafe_allow_html=True)


# ============================================================================
# Dashboard: Alert Queue Tabs
# ============================================================================
def render_alert_queue(data: dict) -> None:
    """Render the tabbed alert queue and audit logs."""
    tabs = st.tabs(["🎯 Target Interdiction Queue", "📋 System Audit Logs", "📊 Spill Summary"])

    with tabs[0]:
        st.markdown("#### Target Interdiction Queue")
        vessels = safe_get(data, "ais", "features", default=[]) or []
        alert_vessels = [v for v in vessels
                        if safe_get(v, "properties", "alert_level") in ("RED", "ORANGE")]

        if not alert_vessels:
            st.success("✅ No anomalous targets requiring interdiction.")
        else:
            for v in alert_vessels:
                p = safe_get(v, "properties", default={}) or {}
                lvl = safe_get(p, "alert_level", default="GREY")
                alert_emoji = {
                    "RED": "🔴", "ORANGE": "🟠", "BLUE": "🔵",
                    "GREEN": "🟢", "GREY": "⚪",
                }.get(lvl, "⚪")

                with st.expander(
                    f"🚨 **{safe_get(p, 'name', default='Unknown')}** — {alert_emoji} **{lvl}**",
                    expanded=False,
                ):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown(f"**MMSI:** `{safe_get(p, 'mmsi', default='—')}`")
                        st.markdown(f"**Type:** {safe_get(p, 'type', default='—')}")
                        st.markdown(f"**Flag:** {safe_get(p, 'flag', default='—')}")
                        st.markdown(f"**Speed:** {safe_get(p, 'speed_knots', default=0)} kn")
                    with col_b:
                        st.markdown(f"**Heading:** {safe_get(p, 'heading', default=0)}°")
                        st.markdown(f"**Risk:** {safe_get(p, 'spill_risk', default='—')}")
                        st.markdown(f"**Correlation:** {alert_emoji} **{lvl}**")

    with tabs[1]:
        st.markdown("#### System Audit Logs")
        # FIX Q8: derive vessel count from actual data instead of hardcoded "47"
        actual_vessel_count = len(safe_get(data, "ais", "features", default=[]) or [])
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logs = [
            (now, "INFO", "System initialized - Vessel Correlate Platform"),
            ("2026-09-05 06:00:00", "INFO", "SAR Sentinel-1 pass completed - 98.7% coverage"),
            ("2026-09-05 05:45:00", "WARNING", "SPILL-001 updated - confidence 94%"),
            ("2026-09-05 05:30:00", "ALERT", "MT Prestige correlated with SPILL-001 (RED)"),
            ("2026-09-05 05:15:00", "INFO", "ICGS Samar deployed to intercept position"),
            ("2026-09-05 05:00:00", "INFO", f"AIS feed updated - {actual_vessel_count} vessels in region"),
            ("2026-09-04 22:00:00", "WARNING", "SPILL-002 detected - confidence 78%"),
            ("2026-09-04 18:30:00", "CRITICAL", "SPILL-001 first detected - Sentinel-1 pass"),
        ]

        for ts, level, msg in logs:
            level_emoji = {
                "CRITICAL": "🔴", "ALERT": "🔴", "WARNING": "🟠", "INFO": "🔵"
            }.get(level, "⚪")
            st.markdown(f"`{ts}`  {level_emoji} **{level}**  —  {msg}")

    with tabs[2]:
        st.markdown("#### Spill Zone Summary")
        spills = safe_get(data, "spills", "features", default=[]) or []
        if not spills:
            st.warning("No spill data available.")
        else:
            total_area = sum(safe_get(s, "properties", "area_km2", default=0) or 0 for s in spills)
            for s in spills:
                p = safe_get(s, "properties", default={}) or {}
                sev = safe_get(p, "severity", default="moderate")
                sev_emoji = {"critical": "🔴", "moderate": "🟠", "low": "🟡"}.get(sev, "⚪")

                with st.expander(
                    f"🌊 **{safe_get(p, 'name', default='Unknown')}** — {sev_emoji} **{sev.upper()}**",
                    expanded=False,
                ):
                    st.markdown(f"**Zone ID:** `{safe_get(p, 'id', default='—')}`")
                    st.markdown(f"**Area:** {safe_get(p, 'area_km2', default=0)} km²")
                    st.markdown(f"**Confidence:** {safe_get(p, 'confidence', default=0):.0%}")
                    st.markdown(f"**Source:** {safe_get(p, 'source_vessel', default='Unknown')}")
                    st.markdown(f"**Detected:** {safe_get(p, 'detected_time', default='—')}")

            st.markdown("---")
            st.markdown(f"**Total Impact Area:** {total_area:.1f} km²")


# ============================================================================
# Login Gate
# ============================================================================
def render_login() -> None:
    """Render the glassmorphic login portal.

    Uses st.columns to center the card. All inputs are batched inside a single
    st.form so Streamlit does not re-render on every keystroke.
    CSS is injected directly here so the function is fully self-contained.
    """
    # Self-contained glassmorphic CSS scoped to .login-card
    st.markdown(
        """
        <style>
        .login-card {
            background: rgba(21, 26, 40, 0.82) !important;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(0, 230, 118, 0.25) !important;
            border-radius: 16px !important;
            padding: 2.5rem !important;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.7),
                        0 0 30px rgba(0, 230, 118, 0.08) !important;
        }
        .login-card::before {
            content: '';
            position: absolute;
            top: -1px; left: -1px; right: -1px;
            height: 3px;
            background: linear-gradient(90deg, #00E676, #00B0FF, #FF3366);
            border-radius: 16px 16px 0 0;
        }
        .login-title {
            color: #00E676 !important;
            font-size: 1.6rem !important;
            font-weight: 800 !important;
            text-transform: uppercase !important;
            letter-spacing: 2px !important;
            margin-bottom: 0.25rem !important;
        }
        .login-subtitle {
            color: #9AA0A6 !important;
            font-size: 0.8rem !important;
            margin-bottom: 2rem !important;
        }
        .login-logo {
            font-size: 3rem !important;
            display: block !important;
            margin-bottom: 1rem !important;
            filter: drop-shadow(0 0 16px rgba(0, 230, 118, 0.5));
        }
        [data-testid="stFormSubmit"] button {
            background: linear-gradient(135deg, #00E676, #00C853) !important;
            color: #000 !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.85rem !important;
            font-weight: 700 !important;
            font-size: 0.9rem !important;
            text-transform: uppercase !important;
            letter-spacing: 1.5px !important;
            box-shadow: 0 4px 20px rgba(0, 230, 118, 0.3) !important;
            transition: all 0.3s !important;
        }
        [data-testid="stFormSubmit"] button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 30px rgba(0, 230, 118, 0.5) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Three-column center layout
    col_left, login_col, col_right = st.columns([1, 2, 1])

    with login_col:
        st.markdown(
            """
            <div class="login-card" style="position:relative;">
                <span class="login-logo">🚢</span>
                <div class="login-title">Vessel Correlate</div>
                <div class="login-subtitle">Authorization Portal — Classified Operations</div>
            """,
            unsafe_allow_html=True,
        )

        # Batch all inputs in one st.form — prevents per-keystroke re-renders
        with st.form(key="login_form", clear_on_submit=False):
            email = st.text_input(
                "Operator Email",
                placeholder="operator@coastguard.gov",
                key="login_email",
            )
            password = st.text_input(
                "Access Token",
                type="password",
                placeholder="Enter access token",
                key="login_password",
            )
            st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)
            submitted = st.form_submit_button(
                "🔐 Authenticate",
                use_container_width=True,
            )

            if submitted:
                if email and password:
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.warning("Please enter both email and access token.")

        st.markdown(
            """
            <div style="text-align:center; margin-top:1.25rem; color:#5F6368; font-size:0.72rem;">
                Demo: operator@coastguard.gov / demo2026
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================================
# Main Application
# ============================================================================
def main() -> None:
    """Main application entry point."""
    st.set_page_config(
        page_title=f"{APP_TITLE} — {APP_SUBTITLE}",
        page_icon="🚢",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    inject_design_system()

    # Auth gate — initialized once, gate enforced every rerun
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    # Render login UI only when unauthenticated, then stop the script
    if not st.session_state.get("authenticated", False):
        render_login()
        st.stop()

    # Authenticated — render dashboard
    render_sidebar()

    # Initialize session state for data loading
    if "data_loaded" not in st.session_state:
        st.session_state["data_loaded"] = False

    # Initialize session state for map key (forces redraw on refresh)
    if "map_key" not in st.session_state:
        st.session_state["map_key"] = uuid.uuid4().hex

    # Load data with spinner on first load, use cached data on subsequent runs
    if not st.session_state["data_loaded"]:
        with st.spinner("Loading map data..."):
            try:
                data = get_demo_data()
                telemetry = compute_telemetry(data)
                st.session_state["demo_data"] = data
                st.session_state["telemetry"] = telemetry
                st.session_state["data_loaded"] = True
                st.rerun()  # Re-run to render with loaded data
            except Exception as e:
                st.error(f"❌ Data loading failed: {e}")
                return
    else:
        # Use cached data from session state
        data = st.session_state["demo_data"]
        telemetry = st.session_state["telemetry"]

    # Guard: wait until data is fully loaded before rendering
    if not st.session_state["data_loaded"]:
        st.info("⏳ Preparing investigation data...")
        st.stop()

    # Page header
    st.markdown(
        f'<h2 class="dash-title">🗺️ {APP_TITLE} — Coast Guard Analyst Dashboard</h2>',
        unsafe_allow_html=True,
    )
    st.caption(
        f"BUILD: {APP_VERSION} | "
        f"REFRESH: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    st.divider()

    # Telemetry bar
    render_telemetry_bar(telemetry)

    # Map viewport - only render after data is confirmed loaded
    st.divider()
    st.markdown("### 🗺️ Investigation Map")
    m = build_map(data)
    MiniMap(toggle_display=True, position="bottomright").add_to(m)
    Fullscreen(position="topleft").add_to(m)
    st_folium(m, use_container_width=True, height=500, returned_objects=[], key=st.session_state["map_key"])

    # Alert queue tabs
    st.divider()
    render_alert_queue(data)


if __name__ == "__main__":
    main()
