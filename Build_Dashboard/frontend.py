"""
Streamlit Frontend - Professional Dashboard UI
"""
import os
import warnings
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import requests
from typing import Dict, List
import json

# Configure Streamlit
st.set_page_config(
    page_title="Enterprise Data Analytics Dashboard",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Force dark text on all Plotly charts via a shared template
_tmpl = go.layout.Template()
_tmpl.layout.font = {"color": "#1a202c", "family": "Inter, Segoe UI, Tahoma, sans-serif"}
_tmpl.layout.paper_bgcolor = "rgba(0,0,0,0)"
_tmpl.layout.plot_bgcolor = "rgba(0,0,0,0)"
_tmpl.layout.legend = {
    "bgcolor": "rgba(255,255,255,0.92)",
    "bordercolor": "#e2e8f0",
    "borderwidth": 1,
    "font": {"color": "#1a202c", "size": 12},
}
pio.templates["enterprise"] = _tmpl
pio.templates.default = "plotly+enterprise"

# Apply enterprise-grade professional styling
st.markdown("""
    <style>
    /* Enterprise color palette and typography */
    :root {
        --primary-color: #1a365d;
        --secondary-color: #2d3748;
        --accent-color: #3182ce;
        --success-color: #38a169;
        --warning-color: #d69e2e;
        --danger-color: #e53e3e;
        --background-primary: #ffffff;
        --background-secondary: #f7fafc;
        --background-tertiary: #edf2f7;
        --text-primary: #1a202c;
        --text-secondary: #4a5568;
        --border-color: #e2e8f0;
        --shadow-light: 0 1px 3px rgba(0, 0, 0, 0.1);
        --shadow-medium: 0 4px 6px rgba(0, 0, 0, 0.1);
        --shadow-heavy: 0 10px 15px rgba(0, 0, 0, 0.1);
        --border-radius: 8px;
        --border-radius-large: 12px;
    }

    /* Global styling */
    .main {
        background-color: var(--background-primary);
        color: var(--text-primary);
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
    }

    /* Reduce Streamlit default top padding */
    .block-container {
        padding-top: 0.75rem !important;
        padding-bottom: 1rem !important;
    }

    /* Hide all Streamlit exception / traceback blocks */
    div[data-testid="stException"],
    div.stException,
    div[data-testid="stException"] * { display: none !important; }

    /* Compact section headings */
    h2 { font-size: 1.1rem !important; font-weight: 600 !important;
         color: var(--primary-color) !important; margin: 0.6rem 0 0.4rem 0 !important; }
    h3 { font-size: 0.95rem !important; font-weight: 600 !important;
         color: var(--secondary-color) !important; margin: 0.4rem 0 0.3rem 0 !important; }

    /* Header styling - compact */
    .enterprise-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3730a3 100%);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: var(--border-radius);
        margin-bottom: 0.75rem;
        box-shadow: var(--shadow-medium);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .enterprise-header h1 {
        color: white !important;
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
        letter-spacing: 0.3px;
    }

    .enterprise-header p {
        color: rgba(255, 255, 255, 0.82) !important;
        font-size: 0.75rem !important;
        font-weight: 400 !important;
        margin: 0 !important;
    }

    .enterprise-header .status-badge {
        background: rgba(255, 255, 255, 0.15);
        color: white;
        padding: 0.25rem 0.7rem;
        border-radius: 12px;
        font-size: 0.72rem;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.25);
        white-space: nowrap;
    }

    /* Sidebar styling - Enterprise */
    .css-1d391kg, .css-12oz5g7 {  /* Sidebar container */
        background: linear-gradient(180deg, var(--background-primary) 0%, var(--background-secondary) 100%) !important;
        border-right: 2px solid var(--border-color) !important;
        box-shadow: var(--shadow-medium) !important;
    }

    .sidebar-header {
        background: var(--primary-color);
        color: white;
        padding: 0.7rem 1rem;
        margin: -1rem -1rem 1rem -1rem;
        border-radius: 0 0 var(--border-radius) var(--border-radius);
        text-align: center;
    }

    .sidebar-header h3 {
        color: white !important;
        margin: 0 !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
    }

    .sidebar-section {
        background: white;
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: 0.75rem;
        margin-bottom: 0.75rem;
        box-shadow: var(--shadow-light);
        transition: box-shadow 0.2s ease;
    }

    .sidebar-section:hover {
        box-shadow: var(--shadow-medium);
        transform: translateY(-1px);
    }

    .sidebar-section h4 {
        color: var(--primary-color) !important;
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
        border-bottom: 1px solid var(--border-color);
        padding-bottom: 0.25rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Filter styling - Professional */
    .filter-container {
        background: var(--background-secondary);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: var(--shadow-light);
    }

    .filter-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }

    .filter-header h3 {
        color: var(--primary-color) !important;
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        margin: 0 !important;
    }

    .active-filters {
        background: white;
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: 1rem;
        margin-bottom: 1rem;
    }

    .filter-tag {
        display: inline-block;
        background: var(--accent-color);
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 0.2rem 0.3rem 0.2rem 0;
        border: 1px solid rgba(49, 130, 206, 0.3);
    }

    .filter-tag .remove-btn {
        margin-left: 0.5rem;
        cursor: pointer;
        opacity: 0.8;
    }

    .filter-tag .remove-btn:hover {
        opacity: 1;
    }

    /* Metric cards - Enterprise style */
    .metric-card {
        background: white;
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: 0.75rem 1rem;
        margin: 0.25rem 0;
        box-shadow: var(--shadow-light);
        transition: box-shadow 0.2s ease;
        position: relative;
        overflow: hidden;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: var(--accent-color);
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-medium);
    }

    .metric-card.success::before { background: var(--success-color); }
    .metric-card.warning::before { background: var(--warning-color); }
    .metric-card.danger::before { background: var(--danger-color); }

    .metric-value {
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        color: var(--primary-color) !important;
        margin-bottom: 0.2rem !important;
        line-height: 1.2 !important;
    }

    .metric-label {
        color: var(--text-secondary) !important;
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }

    /* Data table styling */
    .dataframe {
        border-radius: var(--border-radius) !important;
        border: 1px solid var(--border-color) !important;
        box-shadow: var(--shadow-light) !important;
        font-family: inherit !important;
    }

    .dataframe th {
        background: var(--background-secondary) !important;
        color: var(--primary-color) !important;
        font-weight: 600 !important;
        padding: 1rem !important;
        border-bottom: 2px solid var(--accent-color) !important;
    }

    .dataframe td {
        padding: 0.8rem 1rem !important;
        border-bottom: 1px solid var(--border-color) !important;
    }

    /* Tab styling - Professional */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: var(--background-secondary);
        padding: 0.5rem;
        border-radius: var(--border-radius) var(--border-radius) 0 0;
        border-bottom: 1px solid var(--border-color);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: var(--border-radius) var(--border-radius) 0 0 !important;
        border: 1px solid var(--border-color) !important;
        background-color: white !important;
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--accent-color) !important;
        color: white !important;
        box-shadow: var(--shadow-medium) !important;
    }

    /* Button styling - Enterprise */
    .stButton>button {
        background: linear-gradient(135deg, var(--accent-color) 0%, #2c5282 100%);
        color: white !important;
        border: none !important;
        border-radius: var(--border-radius) !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
        box-shadow: var(--shadow-light) !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-medium) !important;
    }

    .stButton>button:active {
        transform: translateY(0);
    }

    /* Selectbox styling */
    .stSelectbox div[data-baseweb="select"] {
        border-radius: var(--border-radius) !important;
        border: 2px solid var(--border-color) !important;
        transition: all 0.3s ease !important;
    }

    .stSelectbox div[data-baseweb="select"]:hover {
        border-color: var(--accent-color) !important;
        box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1) !important;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background: var(--background-secondary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--border-radius) !important;
        font-weight: 600 !important;
        color: var(--primary-color) !important;
        transition: all 0.3s ease !important;
    }

    .streamlit-expanderHeader:hover {
        background: var(--background-primary) !important;
        box-shadow: var(--shadow-light) !important;
    }

    /* Info/Success/Warning messages */
    .stAlert {
        border-radius: var(--border-radius) !important;
        border: none !important;
        box-shadow: var(--shadow-light) !important;
    }

    .stAlert > div:first-child {
        font-weight: 600 !important;
    }

    /* Progress bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--accent-color) 0%, var(--success-color) 100%) !important;
        border-radius: 10px !important;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--background-secondary);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-secondary);
    }

    /* Loading animation */
    .stSpinner > div > div {
        border-color: var(--accent-color) transparent transparent transparent !important;
    }

    /* ── Ensure dark, readable text throughout the app ───────────────────── */

    /* Base app surface */
    .stApp, .main, .block-container {
        color: var(--text-primary) !important;
        background-color: var(--background-primary) !important;
    }

    /* st.metric() – value, label, delta */
    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] > div,
    [data-testid="stMetricValue"] * {
        color: var(--primary-color) !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] > div,
    [data-testid="stMetricLabel"] * {
        color: var(--text-secondary) !important;
        font-size: 0.78rem !important;
        font-weight: 500 !important;
    }
    [data-testid="stMetricDelta"] * { color: var(--success-color) !important; }

    /* Widget labels (selectbox, multiselect, slider, checkbox, text input) */
    .stSelectbox label, .stMultiSelect label,
    .stSlider label, .stCheckbox label,
    .stTextInput label, .stNumberInput label,
    .stRadio label, .stDateInput label {
        color: var(--text-primary) !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
    }

    /* Dropdown selected value text */
    [data-baseweb="select"] [data-baseweb="tag"] span,
    [data-baseweb="select"] span {
        color: var(--text-primary) !important;
    }

    /* Multiselect pill text */
    [data-baseweb="tag"] span { color: var(--text-primary) !important; }

    /* Markdown rendered text – paragraphs and list items only.
       Headings are intentionally excluded: the global h2/h3 rules handle
       them, and including h1-h5 here overrides white text inside
       dark-background header sections (enterprise-header, sidebar-header). */
    .stMarkdown p, .stMarkdown li {
        color: var(--text-primary) !important;
    }

    /* Dataframe / table text */
    [data-testid="stDataFrame"] * { color: var(--text-primary) !important; }

    /* Expander header text */
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary span {
        color: var(--primary-color) !important;
        font-weight: 600 !important;
    }

    /* Info / warning / success alert text – keep their native icon colours
       but force body text to be dark */
    [data-testid="stAlertContainer"] p,
    [data-testid="stAlertContainer"] div {
        color: var(--text-primary) !important;
    }

    /* Sidebar widget labels */
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span:not(.filter-tag *),
    [data-testid="stSidebar"] small {
        color: var(--text-primary) !important;
    }

    /* ── Extended font-colour coverage ──────────────────────────────────── */

    /* Sidebar header must stay white-on-dark despite the global h3 !important */
    .sidebar-header, .sidebar-header h3, .sidebar-header * {
        color: white !important;
    }

    /* Input / textarea values */
    .stTextInput input, .stNumberInput input, textarea {
        color: var(--text-primary) !important;
        background-color: white !important;
    }

    /* Dropdown open-menu list items */
    [data-baseweb="menu"] [role="option"],
    [data-baseweb="menu"] [role="option"] * {
        color: var(--text-primary) !important;
    }
    /* Keep accent highlight legible when an option is focused/selected */
    [data-baseweb="menu"] [aria-selected="true"],
    [data-baseweb="menu"] [aria-selected="true"] * {
        color: white !important;
        background-color: var(--accent-color) !important;
    }

    /* st.metric() – extra selectors for newer Streamlit builds */
    .stMetric [data-testid="stMetricValue"],
    .stMetric [data-testid="stMetricLabel"],
    .stMetric label,
    .stMetric div,
    .stMetric p {
        color: var(--text-primary) !important;
    }

    /* General widget label catch-all (covers renamed Streamlit classes) */
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] * {
        color: var(--text-primary) !important;
    }

    /* Checkbox and radio button label text */
    [data-testid="stCheckbox"] span,
    [data-testid="stRadio"] span,
    [data-baseweb="checkbox"] label,
    [data-baseweb="radio"] label {
        color: var(--text-primary) !important;
    }

    /* Tab panel content */
    [role="tabpanel"] {
        color: var(--text-primary) !important;
    }

    /* Plotly SVG text (axis labels, tick labels, legend, titles) */
    .js-plotly-plot text {
        fill: #1a202c !important;
    }

    /* Caption / helper text */
    .stCaption p, [data-testid="stCaptionContainer"] {
        color: var(--text-secondary) !important;
    }

    /* Code inline */
    code {
        color: var(--primary-color) !important;
        background-color: var(--background-tertiary) !important;
    }

    /* ── Hide Streamlit branding ─────────────────────────────────────────── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Responsive design */
    @media (max-width: 768px) {
        .enterprise-header {
            padding: 1.5rem 1rem;
        }

        .enterprise-header h1 {
            font-size: 2rem !important;
        }

        .metric-card {
            margin: 0.25rem 0;
        }
    }

    /* ═══════════════════════════════════════════════════════════════
       DARK-BACKGROUND OVERRIDES
       WHY last: CSS resolves same-specificity !important ties by
       source order — the later rule wins. By placing these rules at
       the very end of the stylesheet they always beat any earlier
       catch-all that accidentally darkens text inside a dark container.
       WHY explicit element tags (not *): the universal selector has
       specificity 0-1-0 for ".cls *", which loses to class+element
       rules like ".stMarkdown p" at 0-1-1. Listing each element
       type explicitly gives 0-1-1 (ties broken by source order, i.e.
       these rules win) or 0-1-2 for the child-combinator form (always
       wins by specificity regardless of order).
    ════════════════════════════════════════════════════════════════ */

    /* Enterprise header — dark blue gradient background */
    .enterprise-header { color: white !important; }
    .enterprise-header h1, .enterprise-header h2, .enterprise-header h3,
    .enterprise-header h4, .enterprise-header h5,
    .enterprise-header span, .enterprise-header small,
    .enterprise-header strong, .enterprise-header em, .enterprise-header a {
        color: white !important;
    }
    /* Subtitle <p>: child-combinator path gives specificity 0-1-2,
       which beats .stMarkdown p (0-1-1) even if stMarkdown comes later */
    .enterprise-header p,
    .enterprise-header div p { color: rgba(255, 255, 255, 0.88) !important; }
    /* Status badge pill */
    .enterprise-header .status-badge,
    .enterprise-header .status-badge span,
    .enterprise-header .status-badge div { color: white !important; }

    /* Sidebar control-panel header — dark navy background */
    .sidebar-header { color: white !important; }
    .sidebar-header h1, .sidebar-header h2, .sidebar-header h3,
    .sidebar-header h4, .sidebar-header p,
    .sidebar-header span, .sidebar-header small,
    .sidebar-header strong, .sidebar-header em {
        color: white !important;
    }

    /* Filter tags — accent blue background */
    .filter-tag, .filter-tag span, .filter-tag .remove-btn {
        color: white !important;
    }

    /* Active tab button — accent blue background */
    .stTabs [aria-selected="true"],
    .stTabs [aria-selected="true"] * { color: white !important; }

    /* Primary action buttons — blue gradient background */
    .stButton > button,
    .stButton > button * { color: white !important; }

    </style>
""", unsafe_allow_html=True)

# API Base URL
# On Render the backend URL is injected via the API_BASE_URL env var.
# Falls back to localhost for local development.
_raw_url = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
API_BASE_URL = f"https://{_raw_url}" if not _raw_url.startswith("http") else _raw_url


@st.cache_resource
def init_session():
    """Initialize session state"""
    if 'filters' not in st.session_state:
        st.session_state.filters = []
    if 'selected_file' not in st.session_state:
        st.session_state.selected_file = None
    if 'current_data' not in st.session_state:
        st.session_state.current_data = None
    if 'active_filters' not in st.session_state:
        st.session_state.active_filters = []


def _ok(response) -> bool:
    """Return True only for 2xx responses."""
    return response.status_code < 300


def get_available_files() -> List[str]:
    """Fetch available files from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/files")
        if not _ok(response):
            return []
        return response.json().get("files", [])
    except Exception:
        return []


def get_default_file() -> str:
    """Return the combined-dataset sentinel so all files are analysed together."""
    return "_combined"


def get_file_summary(filename: str) -> Dict:
    """Get file summary statistics"""
    try:
        response = requests.get(f"{API_BASE_URL}/file/{filename}/summary")
        if not _ok(response):
            st.error(f"Backend error fetching summary: {response.json().get('detail', response.status_code)}")
            return {}
        data = response.json()
        if "shape" not in data:
            return {}
        return data
    except Exception as e:
        st.error(f"Failed to fetch summary: {str(e)}")
        return {}


def get_file_data(filename: str) -> pd.DataFrame:
    """Fetch file data from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/file/{filename}")
        if not _ok(response):
            st.error(f"Backend error fetching data: {response.json().get('detail', response.status_code)}")
            return pd.DataFrame()
        data = response.json()
        return pd.DataFrame(data.get("data", []))
    except Exception as e:
        st.error(f"Failed to fetch data: {str(e)}")
        return pd.DataFrame()


def get_unique_values(filename: str, column: str, limit: int = 100) -> List:
    """Get unique values for a column"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/file/{filename}/unique-values",
            params={"column": column, "limit": limit}
        )
        if not _ok(response):
            return []
        return response.json().get("unique_values", [])
    except Exception:
        return []


def slice_data(filename: str, filters: List[Dict]) -> pd.DataFrame:
    """Apply filters and return sliced data"""
    try:
        payload = {"file": filename, "filters": filters, "limit": 10000}
        response = requests.post(f"{API_BASE_URL}/slice", json=payload)
        if not _ok(response):
            st.error(f"Backend error slicing data: {response.json().get('detail', response.status_code)}")
            return pd.DataFrame()
        data = response.json()
        return pd.DataFrame(data.get("data", []))
    except Exception as e:
        st.error(f"Failed to slice data: {str(e)}")
        return pd.DataFrame()


def render_enterprise_header():
    """Render compact dashboard header bar"""
    st.markdown(f"""
    <div class="enterprise-header">
        <div>
            <h1>🏢 Enterprise Data Analytics</h1>
            <p>Advanced analytics · Intelligent filtering · Comprehensive visualisation</p>
        </div>
        <div class="status-badge">🟢 LIVE &nbsp;·&nbsp; {pd.Timestamp.now().strftime('%H:%M')}</div>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar_controls(filename: str):
    """Render professional sidebar with filters, data combinations and tab controls"""
    with st.sidebar:
        # Sidebar header
        st.markdown("""
        <div class="sidebar-header">
            <h3 style="color:white">🎛️ Control Panel</h3>
        </div>
        """, unsafe_allow_html=True)

        # ── Filters ──────────────────────────────────────────────────────────
        st.markdown("""
        <div class="sidebar-section">
            <h4>🔍 Filters</h4>
        </div>
        """, unsafe_allow_html=True)

        if 'active_filters' not in st.session_state:
            st.session_state.active_filters = []

        # Fetch columns for the active file
        columns = []
        if filename:
            try:
                resp = requests.get(f"{API_BASE_URL}/file/{filename}")
                columns = resp.json().get("columns", [])
            except Exception:
                st.warning("Could not load columns for filtering.")

        # Active filter tags + remove buttons
        if st.session_state.active_filters:
            op_labels = {"eq": "=", "contains": "contains", "gt": ">",
                         "lt": "<", "gte": "≥", "lte": "≤", "in": "in"}
            for i, f in enumerate(st.session_state.active_filters):
                val_str = f"[{len(f['value'])} items]" if isinstance(f['value'], list) else str(f['value'])
                label = f"{f['column']} {op_labels.get(f['operator'], f['operator'])} {val_str}"
                c1, c2 = st.columns([4, 1])
                c1.markdown(f"<small>{label}</small>", unsafe_allow_html=True)
                if c2.button("✕", key=f"rm_filter_{i}"):
                    st.session_state.active_filters.pop(i)
                    st.rerun()
            if st.button("🗑️ Clear All", key="clear_all_filters", use_container_width=True):
                st.session_state.active_filters = []
                st.rerun()

        # Add filter form
        with st.expander("➕ Add Filter", expanded=not bool(st.session_state.active_filters)):
            if columns:
                filter_col = st.selectbox("Column", columns, key="filter_col")

                op_map = {"Equals": "eq", "Contains": "contains",
                          "Greater Than": "gt", "Less Than": "lt",
                          "≥": "gte", "≤": "lte", "IN List": "in"}
                operator_label = st.selectbox("Operator", list(op_map.keys()), key="filter_op_label")
                operator = op_map[operator_label]

                if operator == "contains":
                    filter_val = st.text_input("Value", key="filter_text", placeholder="Enter text")
                elif operator == "in":
                    unique_vals = get_unique_values(filename, filter_col, limit=100)
                    filter_val = st.multiselect("Values", unique_vals, key="filter_multi")
                else:
                    unique_vals = get_unique_values(filename, filter_col, limit=50)
                    filter_val = st.selectbox("Value", unique_vals, key="filter_val")

                if st.button("Add Filter", key="add_filter", use_container_width=True):
                    if filter_col and filter_val is not None and filter_val != [] and filter_val != "":
                        duplicate = any(
                            f['column'] == filter_col and f['operator'] == operator
                            for f in st.session_state.active_filters
                        )
                        if duplicate:
                            st.warning("A filter for this column/operator already exists. Remove it first.")
                        else:
                            st.session_state.active_filters.append(
                                {"column": filter_col, "operator": operator, "value": filter_val}
                            )
                            st.rerun()
            else:
                st.info("Load a data file to enable filtering.")

        st.divider()

        # Data Combinations Section
        st.markdown("""
        <div class="sidebar-section">
            <h4>📊 Data Combinations</h4>
        </div>
        """, unsafe_allow_html=True)

        # Initialize session state for sidebar controls
        if 'selected_data_views' not in st.session_state:
            st.session_state.selected_data_views = ['overview', 'detailed']

        if 'enabled_tabs' not in st.session_state:
            st.session_state.enabled_tabs = {
                'distributions': True,
                'categories': True,
                'relationships': True,
                'trends': True
            }

        # Data View Selection
        st.markdown("**Data Views**")
        data_views = st.multiselect(
            "Select data combinations:",
            ['overview', 'detailed', 'summary', 'raw'],
            default=st.session_state.selected_data_views,
            key="data_views",
            help="Choose which data views to display"
        )
        st.session_state.selected_data_views = data_views

        # Quick Actions
        st.markdown("**Quick Actions**")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Overview", use_container_width=True):
                st.session_state.selected_data_views = ['overview']
                st.rerun()
        with col2:
            if st.button("📈 Detailed", use_container_width=True):
                st.session_state.selected_data_views = ['detailed']
                st.rerun()

        st.divider()

        # Chart Types Section
        st.markdown("""
        <div class="sidebar-section">
            <h4>📊 Chart Types</h4>
        </div>
        """, unsafe_allow_html=True)

        all_chart_types = [
            "📈 Trend Chart",
            "📊 Summary Chart",
            "🥧 Category Chart",
            "🔗 Relationships",
            "📉 Distributions",
            "🔀 Comparison",
        ]

        if 'selected_chart_types' not in st.session_state:
            st.session_state.selected_chart_types = all_chart_types

        selected_chart_types = st.multiselect(
            "Select charts to display:",
            all_chart_types,
            default=st.session_state.selected_chart_types,
            key="chart_types_picker",
        )
        st.session_state.selected_chart_types = selected_chart_types

        st.divider()

        # Advanced Options
        with st.expander("⚙️ Advanced Options"):
            st.markdown("**Chart Settings**")
            chart_height = st.slider("Chart Height", 300, 800, 400, key="chart_height")

            st.markdown("**Data Display**")
            max_rows = st.slider("Max Table Rows", 10, 1000, 100, key="max_rows")

            show_stats = st.checkbox("Show Statistics", value=True, key="show_stats")

        # System Status
        st.divider()
        st.markdown("""
        <div class="sidebar-section">
            <h4>🔧 System Status</h4>
        </div>
        """, unsafe_allow_html=True)

        # Live backend connectivity check
        try:
            _r = requests.get(f"{API_BASE_URL}/health", timeout=5)
            _connected = _r.status_code == 200
        except Exception:
            _connected = False

        st.markdown(f"**Backend URL:** `{API_BASE_URL}`")
        st.markdown(f"**API Status:** {'🟢 Connected' if _connected else '🔴 Unreachable'}")


def render_filters_enterprise(filename: str) -> List[Dict]:
    """Render enterprise-grade filter UI"""
    if not filename:
        return []

    try:
        response = requests.get(f"{API_BASE_URL}/file/{filename}")
        file_data = response.json()
        columns = file_data["columns"]
    except:
        st.error("Could not load file columns")
        return []

    # Initialize session state for filters if not exists
    if 'active_filters' not in st.session_state:
        st.session_state.active_filters = []

    # Enterprise filter container
    st.markdown("""
    <div class="filter-container">
        <div class="filter-header">
            <h3>🔍 Advanced Filtering Engine</h3>
            <span style="color: var(--text-secondary); font-size: 0.9rem;">
                {len(st.session_state.active_filters)} active filter(s)
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Active filters display
    if st.session_state.active_filters:
        st.markdown("**Active Filters:**")
        filter_html = '<div class="active-filters">'
        for i, filter_item in enumerate(st.session_state.active_filters):
            op_labels = {
                "eq": "=",
                "contains": "contains",
                "gt": ">",
                "lt": "<",
                "gte": "≥",
                "lte": "≤",
                "in": "in"
            }
            tag = f"{filter_item['column']} {op_labels.get(filter_item['operator'], filter_item['operator'])} "
            if isinstance(filter_item['value'], list):
                tag += f"[{len(filter_item['value'])} items]"
            else:
                tag += str(filter_item['value'])

            filter_html += f'<span class="filter-tag">{tag}<span class="remove-btn" onclick="removeFilter({i})">×</span></span>'

        filter_html += '</div>'
        st.markdown(filter_html, unsafe_allow_html=True)

        # Remove buttons (hidden but functional)
        cols = st.columns(min(len(st.session_state.active_filters), 6))
        for i, filter_item in enumerate(st.session_state.active_filters):
            col_idx = i % len(cols)
            with cols[col_idx]:
                if st.button("❌", key=f"remove_filter_{i}", help=f"Remove filter: {filter_item['column']}", use_container_width=True):
                    st.session_state.active_filters.pop(i)
                    st.rerun()

        if st.button("🗑️ Clear All Filters", key="clear_all_filters"):
            st.session_state.active_filters = []
            st.rerun()

    # Add new filter form (compact horizontal layout)
    with st.expander("➕ Add New Filter", expanded=False):
        col1, col2, col3, col4 = st.columns([2, 1.5, 2, 1])

        with col1:
            filter_col = st.selectbox(
                "Column",
                columns,
                key="filter_col",
                label_visibility="collapsed",
                placeholder="Select column"
            )

        with col2:
            operators = ["eq", "contains", "gt", "lt", "gte", "lte", "in"]
            op_labels = {
                "eq": "Equals",
                "contains": "Contains",
                "gt": "Greater Than",
                "lt": "Less Than",
                "gte": "≥",
                "lte": "≤",
                "in": "IN List"
            }
            operator = st.selectbox(
                "Operator",
                operators,
                format_func=lambda x: op_labels.get(x, x),
                key="filter_op",
                label_visibility="collapsed",
                placeholder="Operator"
            )

        with col3:
            if operator in ["eq", "gt", "lt", "gte", "lte"]:
                unique_vals = get_unique_values(filename, filter_col, limit=50)
                filter_val = st.selectbox(
                    "Value",
                    unique_vals,
                    key="filter_val",
                    label_visibility="collapsed",
                    placeholder="Select value"
                )
            elif operator == "contains":
                filter_val = st.text_input("Text to search", key="filter_text", label_visibility="collapsed", placeholder="Enter text")
            else:  # "in"
                unique_vals = get_unique_values(filename, filter_col, limit=100)
                filter_val = st.multiselect(
                    "Select values",
                    unique_vals,
                    key="filter_multi",
                    label_visibility="collapsed",
                    placeholder="Select multiple values"
                )

        with col4:
            if st.button("➕ Add Filter", key="add_filter", use_container_width=True):
                if filter_col and filter_val:
                    # Check if filter already exists
                    existing_filter = next(
                        (f for f in st.session_state.active_filters
                         if f['column'] == filter_col and f['operator'] == operator),
                        None
                    )
                    if existing_filter:
                        st.warning(f"Filter for {filter_col} with {operator} already exists. Remove it first to replace.")
                    else:
                        st.session_state.active_filters.append({
                            "column": filter_col,
                            "operator": operator,
                            "value": filter_val
                        })
                        st.success(f"Added filter: {filter_col} {op_labels.get(operator, operator)} {filter_val}")
                        st.rerun()

    return st.session_state.active_filters


def render_data_summary(filename: str):
    """Render enterprise data summary statistics"""
    st.markdown("## 📈 Data Overview & Metrics")

    summary = get_file_summary(filename)

    if not summary:
        st.warning("⚠️ Could not load data summary. Make sure the backend is running and has been restarted after the latest changes.")
        return

    if True:
        # Enterprise metric cards
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{summary["shape"]["rows"]:,}</div>
                <div class="metric-label">Total Records</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{summary["shape"]["columns"]}</div>
                <div class="metric-label">Data Columns</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            null_count = sum(col["null_count"] for col in summary["columns"])
            total_cells = summary["shape"]["rows"] * summary["shape"]["columns"]
            null_percentage = (null_count / total_cells * 100) if total_cells > 0 else 0
            card_class = "danger" if null_percentage > 10 else "warning" if null_percentage > 5 else "success"
            st.markdown(f"""
            <div class="metric-card {card_class}">
                <div class="metric-value">{null_count:,}</div>
                <div class="metric-label">Missing Values</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            numeric_cols = sum(1 for col in summary["columns"] if "numeric" in col["dtype"])
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{numeric_cols}</div>
                <div class="metric-label">Numeric Fields</div>
            </div>
            """, unsafe_allow_html=True)

        # Detailed column information in an enterprise-style expander
        with st.expander("📊 Detailed Column Analysis", expanded=False):
            st.markdown("### Column Metadata & Statistics")

            col_df = pd.DataFrame([
                {
                    "Column Name": col["name"],
                    "Data Type": col["dtype"],
                    "Unique Values": col["unique_count"],
                    "Missing Values": col["null_count"],
                    "Completeness %": f"{((summary['shape']['rows'] - col['null_count']) / summary['shape']['rows'] * 100):.1f}%" if summary['shape']['rows'] > 0 else "N/A"
                }
                for col in summary["columns"]
            ])
            st.dataframe(col_df, use_container_width=True)

            # Data quality indicators
            st.markdown("### Data Quality Indicators")
            quality_cols = st.columns(3)

            with quality_cols[0]:
                complete_cols = sum(1 for col in summary["columns"] if col["null_count"] == 0)
                st.metric("Complete Columns", f"{complete_cols}/{summary['shape']['columns']}")

            with quality_cols[1]:
                rows = summary["shape"]["rows"]
                num_cols = len(summary["columns"])
                avg_uniqueness = (sum(col["unique_count"] / rows for col in summary["columns"]) / num_cols) if rows > 0 and num_cols > 0 else 0
                st.metric("Avg. Uniqueness", f"{avg_uniqueness:.1%}")

            with quality_cols[2]:
                text_cols = sum(1 for col in summary["columns"] if "object" in col["dtype"])
                st.metric("Text Columns", text_cols)


def render_data_table(df: pd.DataFrame):
    """Render enterprise data table"""
    st.markdown("## 📋 Data Explorer")

    # Get max rows from session state
    max_rows = getattr(st.session_state, 'max_rows', 100)

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        rows_to_show = st.slider(
            "Rows to display",
            10,
            min(max_rows, len(df)),
            min(50, len(df)),
            key="table_rows"
        )

    with col2:
        st.markdown(f"""
        <div style="padding-top: 1.5rem; text-align: center;">
            <span style="color: var(--text-secondary); font-size: 0.9rem;">
                📊 Showing <strong>{min(rows_to_show, len(df)):,}</strong> of <strong>{len(df):,}</strong> total records
            </span>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        if st.button("📥 Export Data", use_container_width=True):
            csv = df.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv,
                f"data_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv",
                use_container_width=True
            )

    # Enhanced dataframe display
    st.dataframe(
        df.head(rows_to_show),
        use_container_width=True,
        column_config={
            col: st.column_config.NumberColumn(col, format="%.2f")
            for col in df.select_dtypes(include=[np.number]).columns
        } if 'np' in globals() else None
    )

    # Data summary
    if len(df) > max_rows:
        st.info(f"💡 Showing first {rows_to_show} rows. Adjust the slider to see more data or modify the max rows setting in the sidebar.")


def render_visualizations(df: pd.DataFrame):
    """Render comprehensive data visualizations with professional styling"""
    st.markdown("## 📊 Advanced Data Visualizations")

    if len(df) == 0:
        st.info("📭 No data available to visualize")
        return

    # Get chart height from session state
    chart_height = getattr(st.session_state, 'chart_height', 400)

    # Better column detection
    numeric_cols = []
    categorical_cols = []
    datetime_cols = []

    _time_keywords = {'year', 'month', 'date', 'period', 'quarter', 'week', 'day'}
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            datetime_cols.append(col)
        elif pd.api.types.is_numeric_dtype(df[col]):
            numeric_cols.append(col)
        else:
            unique_ratio = df[col].nunique() / len(df) if len(df) > 0 else 0
            if unique_ratio <= 0.1 and df[col].nunique() <= 20:
                categorical_cols.append(col)

    # Time axis candidates: proper datetimes + year-like ints + time-named columns
    year_like_cols = [
        c for c in numeric_cols
        if any(kw in c.lower() for kw in _time_keywords)
        or (df[c].dropna().between(1900, 2100).all() and df[c].nunique() <= 100)
    ]
    time_named_cols = [
        c for c in df.columns
        if c not in datetime_cols and c not in year_like_cols
        and any(kw in c.lower() for kw in _time_keywords)
    ]
    time_axis_cols = datetime_cols + year_like_cols + time_named_cols

    # Show what we found
    with st.expander("📋 Column Analysis", expanded=False):
        st.write(f"**Numeric columns:** {', '.join(numeric_cols) if numeric_cols else 'None'}")
        st.write(f"**Categorical columns:** {', '.join(categorical_cols) if categorical_cols else 'None'}")
        st.write(f"**DateTime columns:** {', '.join(datetime_cols) if datetime_cols else 'None'}")

    if not numeric_cols and not categorical_cols:
        st.warning("⚠️ No suitable columns found for visualization. Try different data or check column types.")
        return

    # Map sidebar chart-type labels to internal tab keys
    chart_type_map = {
        "📈 Trend Chart":    ("📈 Trend Chart",    "trends"),
        "📊 Summary Chart":  ("📊 Summary Chart",  "categories"),
        "🥧 Category Chart": ("🥧 Category Chart", "categories"),
        "🔗 Relationships":  ("🔗 Relationships",  "relationships"),
        "📉 Distributions":  ("📉 Distributions",  "distributions"),
        "🔀 Comparison":     ("🔀 Comparison",     "comparison"),
    }

    selected = getattr(st.session_state, 'selected_chart_types', list(chart_type_map.keys()))
    seen_keys = set()
    tab_configs = []
    for label in selected:
        if label in chart_type_map:
            tab_label, tab_key = chart_type_map[label]
            if tab_key not in seen_keys:
                tab_configs.append((tab_label, tab_key))
                seen_keys.add(tab_key)

    if not tab_configs:
        st.warning("No visualization tabs are enabled. Please enable at least one tab in the sidebar.")
        return

    # Create tabs dynamically
    tabs = st.tabs([config[0] for config in tab_configs])

    # ── Distributions Tab ────────────────────────────────────────────────────
    if 'distributions' in seen_keys:
        tab_idx = next(i for i, c in enumerate(tab_configs) if c[1] == 'distributions')
        with tabs[tab_idx]:
            st.markdown("### Distribution Analysis")
            if numeric_cols:
                # Controls row
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    dist_cols = st.multiselect(
                        "Columns to plot",
                        numeric_cols,
                        default=[numeric_cols[0]],
                        key="dist_cols",
                    )
                with c2:
                    dist_type = st.selectbox(
                        "Chart type",
                        ["Histogram", "Box Plot", "Violin Plot"],
                        key="dist_type",
                    )
                with c3:
                    dist_color = st.selectbox(
                        "Color by",
                        ["None"] + categorical_cols,
                        key="dist_color",
                    )
                with c4:
                    dist_bins = st.slider("Bins (histogram)", 5, 100, 30, key="dist_bins")

                if dist_cols:
                    if dist_type == "Histogram":
                        if len(dist_cols) == 1:
                            kwargs = dict(x=dist_cols[0], nbins=dist_bins,
                                          marginal="box",
                                          title=f"Distribution of {dist_cols[0]}")
                            if dist_color != "None":
                                kwargs["color"] = dist_color
                            fig = px.histogram(df, **kwargs)
                        else:
                            # Overlay multiple columns
                            fig = go.Figure()
                            for col in dist_cols:
                                fig.add_trace(go.Histogram(x=df[col], name=col,
                                                           nbinsx=dist_bins, opacity=0.7))
                            fig.update_layout(barmode="overlay",
                                              title="Distribution Comparison")
                    elif dist_type == "Box Plot":
                        plot_df = df[dist_cols].melt(var_name="Column", value_name="Value")
                        kwargs = dict(x="Column", y="Value",
                                      title="Box Plot Comparison")
                        if dist_color != "None" and len(dist_cols) == 1:
                            kwargs = dict(x=dist_color, y=dist_cols[0],
                                          title=f"{dist_cols[0]} by {dist_color}")
                            fig = px.box(df, **kwargs)
                        else:
                            fig = px.box(plot_df, **kwargs)
                    else:  # Violin
                        plot_df = df[dist_cols].melt(var_name="Column", value_name="Value")
                        kwargs = dict(x="Column", y="Value",
                                      box=True, points="outliers",
                                      title="Violin Plot Comparison")
                        if dist_color != "None" and len(dist_cols) == 1:
                            kwargs = dict(x=dist_color, y=dist_cols[0],
                                          box=True, points="outliers",
                                          title=f"{dist_cols[0]} by {dist_color}")
                            fig = px.violin(df, **kwargs)
                        else:
                            fig = px.violin(plot_df, **kwargs)

                    fig.update_layout(height=chart_height,
                                      plot_bgcolor='rgba(0,0,0,0)',
                                      paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True, theme=None)

                    if getattr(st.session_state, 'show_stats', True) and len(dist_cols) == 1:
                        col = dist_cols[0]
                        s1, s2, s3, s4 = st.columns(4)
                        s1.metric("Mean", f"{df[col].mean():.2f}")
                        s2.metric("Median", f"{df[col].median():.2f}")
                        s3.metric("Std Dev", f"{df[col].std():.2f}")
                        s4.metric("Count", len(df[col].dropna()))
            else:
                st.info("No numeric columns available for distribution analysis")

    # ── Categories Tab ───────────────────────────────────────────────────────
    if 'categories' in seen_keys:
        tab_idx = next(i for i, c in enumerate(tab_configs) if c[1] == 'categories')
        with tabs[tab_idx]:
            st.markdown("### Summary / Category Analysis")
            if categorical_cols:
                # Controls row
                c1, c2, c3, c4, c5 = st.columns(5)
                with c1:
                    selected_cat = st.selectbox(
                        "Category column",
                        categorical_cols,
                        key="cat_col",
                    )
                with c2:
                    value_options = ["Count"] + numeric_cols
                    cat_value = st.selectbox(
                        "Value (metric)",
                        value_options,
                        key="cat_value",
                    )
                with c3:
                    agg_options = ["Sum", "Mean", "Median", "Max", "Min"]
                    cat_agg = st.selectbox(
                        "Aggregation",
                        agg_options,
                        key="cat_agg",
                        disabled=(cat_value == "Count"),
                    )
                with c4:
                    cat_type = st.selectbox(
                        "Chart type",
                        ["Bar Chart", "Pie Chart", "Treemap"],
                        key="cat_type",
                    )
                with c5:
                    max_categories = st.slider("Max categories", 5, 50, 20, key="max_cat")

                if selected_cat:
                    if cat_value == "Count":
                        agg_series = df[selected_cat].value_counts().head(max_categories)
                        y_label = "Count"
                    else:
                        agg_fn = {"Sum": "sum", "Mean": "mean", "Median": "median",
                                  "Max": "max", "Min": "min"}[cat_agg]
                        agg_series = (df.groupby(selected_cat)[cat_value]
                                      .agg(agg_fn)
                                      .sort_values(ascending=False)
                                      .head(max_categories))
                        y_label = f"{cat_agg} of {cat_value}"

                    if cat_type == "Bar Chart":
                        fig = px.bar(
                            x=agg_series.index, y=agg_series.values,
                            title=f"{y_label} by {selected_cat}",
                            labels={"x": selected_cat, "y": y_label},
                        )
                    elif cat_type == "Pie Chart":
                        fig = px.pie(
                            values=agg_series.values, names=agg_series.index,
                            title=f"{y_label} by {selected_cat}",
                        )
                    else:
                        fig = px.treemap(
                            names=agg_series.index, values=agg_series.values,
                            title=f"{y_label} by {selected_cat}",
                        )

                    fig.update_layout(height=chart_height,
                                      plot_bgcolor='rgba(0,0,0,0)',
                                      paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True, theme=None)

                    summary_df = agg_series.reset_index()
                    summary_df.columns = [selected_cat, y_label]
                    st.dataframe(summary_df, use_container_width=True)
            else:
                st.info("No suitable categorical columns available for analysis")

    # ── Relationships Tab ────────────────────────────────────────────────────
    if 'relationships' in seen_keys:
        tab_idx = next(i for i, c in enumerate(tab_configs) if c[1] == 'relationships')
        with tabs[tab_idx]:
            st.markdown("### Relationship Analysis")
            if len(numeric_cols) >= 2:
                # Controls row
                c1, c2, c3, c4, c5 = st.columns(5)
                with c1:
                    x_col = st.selectbox("X-Axis", numeric_cols, key="scatter_x")
                with c2:
                    y_col = st.selectbox("Y-Axis", numeric_cols,
                                         index=1 if len(numeric_cols) > 1 else 0,
                                         key="scatter_y")
                with c3:
                    color_by = st.selectbox("Color by",
                                            ["None"] + categorical_cols,
                                            key="scatter_color")
                with c4:
                    size_by = st.selectbox("Size by",
                                           ["None"] + numeric_cols,
                                           key="scatter_size")
                with c5:
                    trendline = st.selectbox("Trendline",
                                             ["None", "OLS (linear)", "Lowess (smooth)"],
                                             key="scatter_trend")

                if x_col and y_col:
                    trendline_map = {"OLS (linear)": "ols", "Lowess (smooth)": "lowess"}
                    scatter_kwargs = dict(
                        x=x_col, y=y_col,
                        title=f"{x_col} vs {y_col}",
                        hover_data=categorical_cols[:3] if categorical_cols else None,
                    )
                    if color_by != "None":
                        scatter_kwargs["color"] = color_by
                    if size_by != "None":
                        scatter_kwargs["size"] = size_by
                    if trendline != "None":
                        scatter_kwargs["trendline"] = trendline_map[trendline]

                    try:
                        fig = px.scatter(df, **scatter_kwargs)
                    except Exception as _ols_err:
                        err_msg = str(_ols_err)
                        if trendline != "None":
                            st.warning(
                                f"⚠️ **{trendline} trendline could not be fitted** — "
                                f"retrying without trendline.\n\n"
                                f"Reason: {err_msg}\n\n"
                                f"Common causes: a 'Color by' group has fewer than 2 points, "
                                f"or the column contains too many missing values."
                            )
                            scatter_kwargs.pop("trendline", None)
                            fig = px.scatter(df, **scatter_kwargs)
                        else:
                            st.info(f"Could not render scatter plot: {err_msg}")
                            fig = None

                    if fig is not None:
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore", RuntimeWarning)
                            correlation = df[x_col].corr(df[y_col])
                        if pd.notna(correlation):
                            fig.add_annotation(
                                x=0.02, y=0.98,
                                text=f"r = {correlation:.3f}",
                                showarrow=False, xref="paper", yref="paper",
                                bgcolor="rgba(255,255,255,0.9)",
                                font=dict(color="#1a202c"),
                            )

                        fig.update_layout(height=chart_height,
                                          plot_bgcolor='rgba(0,0,0,0)',
                                          paper_bgcolor='rgba(0,0,0,0)')
                        st.plotly_chart(fig, use_container_width=True, theme=None)

                    if len(numeric_cols) > 2:
                        corr_cols = st.multiselect(
                            "Columns for correlation matrix",
                            numeric_cols,
                            default=numeric_cols,
                            key="corr_cols",
                        )
                        if len(corr_cols) >= 2:
                            st.markdown("**Correlation Matrix:**")
                            fig_corr = px.imshow(
                                df[corr_cols].corr(),
                                text_auto=True, aspect="auto",
                                color_continuous_scale="RdBu_r",
                                title="Correlation Matrix",
                            )
                            fig_corr.update_layout(height=int(chart_height * 0.7))
                            st.plotly_chart(fig_corr, use_container_width=True, theme=None)
            else:
                st.info("Need at least 2 numeric columns for relationship analysis")

    # ── Trends Tab ───────────────────────────────────────────────────────────
    if 'trends' in seen_keys:
        tab_idx = next(i for i, c in enumerate(tab_configs) if c[1] == 'trends')
        with tabs[tab_idx]:
            st.markdown("### Trend Analysis")
            if not numeric_cols:
                st.info("No numeric columns available for trend analysis.")
            elif not time_axis_cols:
                st.info("No time/period columns found. Add a Year, Month, or Date column to enable trend charts.")
            else:
                # Build the full list of time options, including a synthetic Year+Month combo
                _year_col = next((c for c in df.columns if c.lower().strip() == 'year'), None)
                _month_col = next((c for c in df.columns if c.lower().strip() == 'month'), None)
                synthetic_opts = ["Year + Month (combined)"] if _year_col and _month_col else []
                all_time_opts = time_axis_cols + synthetic_opts

                # ── Row 1: time / value / aggregation / resample ────────────
                r1c1, r1c2, r1c3, r1c4 = st.columns(4)
                with r1c1:
                    time_col = st.selectbox("Time axis", all_time_opts, key="time_col")
                with r1c2:
                    value_cols = st.multiselect(
                        "Value column(s)",
                        numeric_cols,
                        default=[numeric_cols[0]],
                        key="trend_values",
                    )
                with r1c3:
                    trend_agg = st.selectbox(
                        "Aggregation",
                        ["Mean", "Sum", "Median", "Min", "Max"],
                        key="trend_agg",
                    )
                with r1c4:
                    is_datetime_col = time_col in datetime_cols
                    resample = st.selectbox(
                        "Resample (datetime only)",
                        ["None", "Daily", "Weekly", "Monthly"],
                        key="trend_resample",
                        disabled=not is_datetime_col,
                    )

                # ── Row 2: multi-field group-by + divide-by ──────────────────
                all_dim_cols = [c for c in df.columns if c not in numeric_cols and c not in time_axis_cols]
                r2c1, r2c2 = st.columns([3, 1])
                with r2c1:
                    group_dims = st.multiselect(
                        "Group by (combine fields into one series label — e.g. Brand + Model + Trim)",
                        all_dim_cols,
                        default=[],
                        key="trend_group_dims",
                    )
                with r2c2:
                    divide_by = st.selectbox(
                        "Divide by (facet)",
                        ["None"] + [c for c in all_dim_cols if c not in group_dims],
                        key="trend_divide",
                    )

                if time_col and value_cols:
                    df_plot = df.copy()
                    agg_fn = {"Mean": "mean", "Sum": "sum", "Median": "median",
                              "Min": "min", "Max": "max"}[trend_agg]

                    # ── Prepare time axis ────────────────────────────────────
                    if time_col == "Year + Month (combined)":
                        df_plot["_time"] = (
                            df_plot[_year_col].astype(str).str.strip()
                            + " - "
                            + df_plot[_month_col].astype(str).str.strip()
                        )
                        actual_time = "_time"
                        is_datetime_col = False
                    elif time_col in datetime_cols:
                        df_plot[time_col] = pd.to_datetime(df_plot[time_col], errors="coerce")
                        df_plot = df_plot.dropna(subset=[time_col])
                        actual_time = time_col
                    else:
                        df_plot = df_plot.dropna(subset=[time_col])
                        actual_time = time_col
                        is_datetime_col = False

                    try:
                        # ── Build combo label from multiple group dims ───────
                        if group_dims:
                            df_plot["_combo"] = df_plot[group_dims].astype(str).apply(
                                lambda r: " · ".join(v.strip() for v in r), axis=1
                            )
                            color_col = "_combo"
                        else:
                            color_col = None

                        # ── Value cols: if any equal the time axis, replace
                        #    with record-count so groupby doesn't self-aggregate
                        safe_value_cols = []
                        for vc in value_cols:
                            if vc == actual_time:
                                df_plot["_count"] = 1
                                safe_value_cols.append("_count")
                            else:
                                safe_value_cols.append(vc)

                        # ── Aggregate ────────────────────────────────────────
                        grp_keys = [actual_time]
                        if color_col:
                            grp_keys.append(color_col)
                        if divide_by != "None":
                            grp_keys.append(divide_by)

                        resample_map = {"Daily": "D", "Weekly": "W", "Monthly": "ME"}
                        if is_datetime_col and resample != "None" and resample in resample_map:
                            df_plot = (
                                df_plot.set_index(actual_time)
                                .groupby(
                                    ([color_col] if color_col else []) +
                                    ([divide_by] if divide_by != "None" else [])
                                )[safe_value_cols]
                                .resample(resample_map[resample])
                                .agg(agg_fn)
                                .reset_index()
                            )
                        else:
                            df_plot = (
                                df_plot.groupby(grp_keys, sort=False)[safe_value_cols]
                                .agg(agg_fn)
                                .reset_index()
                            )
                            if pd.api.types.is_numeric_dtype(df_plot[actual_time]):
                                df_plot = df_plot.sort_values(actual_time)

                        # ── Plot ─────────────────────────────────────────────
                        facet_col_arg = divide_by if divide_by != "None" else None
                        plot_title = (
                            f"{trend_agg} of {', '.join(safe_value_cols)} by {time_col}"
                            + (f"  ·  {' + '.join(group_dims)}" if group_dims else "")
                            + (f"  ·  by {divide_by}" if divide_by != "None" else "")
                        )

                        if len(safe_value_cols) > 1:
                            keep = [actual_time] + safe_value_cols
                            if color_col:
                                keep.append(color_col)
                            if facet_col_arg:
                                keep.append(facet_col_arg)
                            keep = [c for c in keep if c in df_plot.columns]
                            melt_df = df_plot[keep].melt(
                                id_vars=[c for c in keep if c not in safe_value_cols],
                                var_name="Metric", value_name="Value",
                            )
                            fig = px.line(melt_df, x=actual_time, y="Value",
                                          color="Metric", facet_col=facet_col_arg,
                                          markers=True, title=plot_title)
                        else:
                            fig = px.line(df_plot, x=actual_time, y=safe_value_cols[0],
                                          color=color_col, facet_col=facet_col_arg,
                                          markers=True, title=plot_title)

                        fig.update_layout(
                            height=chart_height if not facet_col_arg else chart_height + 200,
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            xaxis_title=time_col,
                            legend_title=" · ".join(group_dims) if group_dims else None,
                        )
                        st.plotly_chart(fig, use_container_width=True, theme=None)

                        if getattr(st.session_state, 'show_stats', True) and len(safe_value_cols) == 1:
                            raw_col = value_cols[0] if value_cols[0] in df.columns else None
                            if raw_col:
                                s1, s2, s3 = st.columns(3)
                                s1.metric("Average", f"{df[raw_col].mean():.2f}")
                                s2.metric("Min", f"{df[raw_col].min():.2f}")
                                s3.metric("Max", f"{df[raw_col].max():.2f}")

                    except Exception as _trend_err:
                        st.info(f"Select valid time and value columns to render the trend chart. ({_trend_err})")

    # ── Comparison Tab ───────────────────────────────────────────────────────
    if 'comparison' in seen_keys:
        tab_idx = next(i for i, c in enumerate(tab_configs) if c[1] == 'comparison')
        with tabs[tab_idx]:
            st.markdown("### Combination Comparison")
            all_cols = df.columns.tolist()
            str_cols = [c for c in all_cols if df[c].dtype == object or str(df[c].dtype) == 'category']

            # ── Row 1: controls ──────────────────────────────────────────────
            r1c1, r1c2, r1c3, r1c4, r1c5 = st.columns([2, 1, 1, 1, 1])
            with r1c1:
                dim_cols = st.multiselect(
                    "Combination dimensions (e.g. Brand + Model + Trim)",
                    all_cols,
                    default=[c for c in ["Brand ", "Brand", "Model", "Trim Collected"] if c in all_cols][:3],
                    key="cmp_dims",
                    help="These columns are joined to form each combination label",
                )
            with r1c2:
                metric_col = st.selectbox(
                    "Metric",
                    numeric_cols,
                    index=numeric_cols.index("MSRP") if "MSRP" in numeric_cols else 0,
                    key="cmp_metric",
                )
            with r1c3:
                agg_fn_label = st.selectbox(
                    "Aggregation",
                    ["Mean", "Median", "Min", "Max", "Sum"],
                    key="cmp_agg",
                )
            with r1c4:
                split_col = st.selectbox(
                    "Compare across",
                    ["(none)"] + str_cols,
                    index=(["(none)"] + str_cols).index("Market") if "Market" in str_cols else 0,
                    key="cmp_split",
                )
            with r1c5:
                cmp_chart = st.selectbox(
                    "Chart type",
                    ["Grouped Bar", "Line", "Heatmap"],
                    key="cmp_chart",
                )

            if not dim_cols:
                st.info("Select at least one dimension column above to build combinations.")
            else:
                # Build combination label column
                df_work = df.copy()
                df_work["_combo"] = df_work[dim_cols].astype(str).apply(
                    lambda row: " · ".join(v.strip() for v in row), axis=1
                )

                all_combos = sorted(df_work["_combo"].dropna().unique().tolist())

                # ── Row 2: pick which combos to compare ──────────────────────
                default_combos = all_combos[:min(5, len(all_combos))]
                chosen_combos = st.multiselect(
                    f"Select combinations to compare ({len(all_combos)} available)",
                    all_combos,
                    default=default_combos,
                    key="cmp_chosen",
                )

                if not chosen_combos:
                    st.info("Select at least one combination above.")
                else:
                    df_filtered = df_work[df_work["_combo"].isin(chosen_combos)]
                    agg_map = {"Mean": "mean", "Median": "median",
                               "Min": "min", "Max": "max", "Sum": "sum"}
                    agg = agg_map[agg_fn_label]

                    if split_col == "(none)":
                        # Simple bar across combinations
                        agg_df = (df_filtered.groupby("_combo")[metric_col]
                                  .agg(agg).reset_index()
                                  .rename(columns={"_combo": "Combination", metric_col: agg_fn_label}))
                        agg_df = agg_df.sort_values(agg_fn_label, ascending=False)

                        if cmp_chart == "Grouped Bar":
                            fig = px.bar(agg_df, x="Combination", y=agg_fn_label,
                                         title=f"{agg_fn_label} {metric_col} by Combination",
                                         text_auto=".2f")
                        else:
                            fig = px.line(agg_df, x="Combination", y=agg_fn_label,
                                          title=f"{agg_fn_label} {metric_col} by Combination",
                                          markers=True)
                    else:
                        agg_df = (df_filtered.groupby(["_combo", split_col])[metric_col]
                                  .agg(agg).reset_index()
                                  .rename(columns={"_combo": "Combination", metric_col: agg_fn_label}))

                        if cmp_chart == "Heatmap":
                            pivot = agg_df.pivot(index="Combination", columns=split_col, values=agg_fn_label)
                            fig = px.imshow(
                                pivot, text_auto=".0f", aspect="auto",
                                color_continuous_scale="Blues",
                                title=f"{agg_fn_label} {metric_col}: Combination vs {split_col}",
                            )
                        elif cmp_chart == "Line":
                            fig = px.line(agg_df, x=split_col, y=agg_fn_label,
                                          color="Combination", markers=True,
                                          title=f"{agg_fn_label} {metric_col} by {split_col}")
                        else:  # Grouped Bar
                            fig = px.bar(agg_df, x=split_col, y=agg_fn_label,
                                         color="Combination", barmode="group",
                                         title=f"{agg_fn_label} {metric_col} by {split_col}",
                                         text_auto=".0f")

                    fig.update_layout(height=chart_height,
                                      plot_bgcolor='rgba(0,0,0,0)',
                                      paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True, theme=None)

                    # Summary table
                    with st.expander("📋 Data table", expanded=False):
                        st.dataframe(agg_df, use_container_width=True)


def main():
    """Enterprise dashboard main logic"""
    init_session()

    # Render enterprise header
    render_enterprise_header()

    # Resolve the data file from the backend
    selected_file = get_default_file()

    # Render sidebar controls (filters + chart type picker live here)
    render_sidebar_controls(selected_file)

    if not selected_file:
        st.error("❌ No Excel files found in the data folder. Please add your data file to the 'data' folder.")
        st.info("💡 Place your Excel (.xlsx or .xls) files in the 'data' folder to get started.")
        return

    # Show data source info
    st.markdown(f"""
    <div style="background: var(--background-secondary); padding: 1rem; border-radius: var(--border-radius); margin-bottom: 1rem; border-left: 4px solid var(--accent-color);">
        <strong>📊 Data Source:</strong> {selected_file} | <strong>Status:</strong> Connected | <strong>Last Updated:</strong> {pd.Timestamp.now().strftime('%H:%M:%S')}
    </div>
    """, unsafe_allow_html=True)

    # Render enterprise data summary
    render_data_summary(selected_file)

    st.divider()

    # Load and display data based on selected data views
    data_views = getattr(st.session_state, 'selected_data_views', ['overview'])

    if 'raw' in data_views or 'detailed' in data_views:
        filters = st.session_state.get('active_filters', [])
        if filters:
            df = slice_data(selected_file, filters)
            st.info(f"✅ Applied {len(filters)} filter(s). Showing {len(df):,} rows")
        else:
            df = get_file_data(selected_file)

        if len(df) > 0:
            if 'raw' in data_views:
                render_data_table(df)
                st.divider()

            render_visualizations(df)
        else:
            st.warning("⚠️ No data available with the current filters. Try adjusting your filter criteria.")
    elif 'overview' in data_views:
        # Show only summary and visualizations for overview
        df = get_file_data(selected_file)
        if len(df) > 0:
            render_visualizations(df)
        else:
            st.warning("⚠️ No data available for overview.")
    else:
        st.info("📋 Select a data view from the sidebar to begin analysis.")


if __name__ == "__main__":
    main()
