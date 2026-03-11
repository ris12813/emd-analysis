import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import hashlib
from functools import lru_cache

st.set_page_config(
    page_title="SubsIQ — Subscription Analytics",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
  --navy:    #03112b;
  --blue1:   #0a3d8f;
  --blue2:   #1057c8;
  --blue3:   #2979ff;
  --cyan:    #00b4d8;
  --light1:  #e8f0fe;
  --light2:  #c7d8fc;
  --white:   #ffffff;
  --green:   #00c896;
  --red:     #ff4d6d;
  --amber:   #ffb300;
  --gray1:   #f4f7ff;
  --gray2:   #dce6fb;
  --text1:   #03112b;
  --text2:   #3a5282;
  --text3:   #7b93c4;
}

* { font-family: 'Outfit', sans-serif; }
.mono { font-family: 'JetBrains Mono', monospace; }

.stApp {
  background: linear-gradient(135deg, #f0f5ff 0%, #e8f0fe 50%, #f4f9ff 100%);
  min-height: 100vh;
}

section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, var(--navy) 0%, #071e47 60%, #061630 100%) !important;
  border-right: 1px solid rgba(41,121,255,0.2);
}
section[data-testid="stSidebar"] * { color: #c8d8f8 !important; }
section[data-testid="stSidebar"] .stRadio > label { display: none; }
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] { gap: 4px; }
section[data-testid="stSidebar"] .stRadio label {
  display: flex !important;
  align-items: center;
  padding: 10px 16px !important;
  border-radius: 10px !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  color: #8aaee0 !important;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}
section[data-testid="stSidebar"] .stRadio label:hover {
  background: rgba(41,121,255,0.15) !important;
  color: #c8d8f8 !important;
  border-color: rgba(41,121,255,0.3);
}
section[data-testid="stSidebar"] .stRadio input:checked + div {
  background: linear-gradient(135deg, rgba(41,121,255,0.3), rgba(0,180,216,0.15)) !important;
  border-color: rgba(41,121,255,0.5) !important;
}

.page-header {
  background: linear-gradient(135deg, var(--blue1) 0%, var(--blue2) 60%, var(--blue3) 100%);
  border-radius: 18px;
  padding: 28px 32px;
  margin-bottom: 24px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(10,61,143,0.25);
}
.page-header::before {
  content: '';
  position: absolute; top: -50%; right: -10%;
  width: 300px; height: 300px;
  background: radial-gradient(circle, rgba(0,180,216,0.2) 0%, transparent 70%);
  border-radius: 50%;
}
.page-header h1 {
  color: white !important;
  font-size: 26px !important;
  font-weight: 800 !important;
  margin: 0 !important;
  letter-spacing: -0.5px;
}
.page-header p {
  color: rgba(255,255,255,0.7) !important;
  font-size: 13px !important;
  margin: 6px 0 0 !important;
}

.kpi-card {
  background: white;
  border: 1px solid var(--light2);
  border-radius: 16px;
  padding: 20px 22px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 16px rgba(10,61,143,0.07);
  transition: transform 0.2s, box-shadow 0.2s;
}
.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(10,61,143,0.13);
}
.kpi-card::after {
  content: '';
  position: absolute; bottom: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--blue2), var(--cyan));
}
.kpi-label {
  font-size: 11px; font-weight: 700;
  color: #0a3d8f !important;
  text-transform: uppercase; letter-spacing: 1px;
  margin-bottom: 8px;
}
.kpi-value {
  font-size: 30px; font-weight: 800;
  color: var(--text1); line-height: 1;
  font-family: 'Outfit', sans-serif;
  letter-spacing: -1px;
}
.kpi-delta {
  font-size: 12px; color: var(--text2);
  margin-top: 6px;
}
.kpi-card.green::after { background: linear-gradient(90deg, #00c896, #00e5b0); }
.kpi-card.red::after   { background: linear-gradient(90deg, #ff4d6d, #ff8fa3); }
.kpi-card.amber::after { background: linear-gradient(90deg, #ffb300, #ffd54f); }
.kpi-card.cyan::after  { background: linear-gradient(90deg, #00b4d8, #48cae4); }

.sec-title {
  font-size: 16px; font-weight: 700;
  color: #03112b !important;
  padding-bottom: 10px;
  border-bottom: 2px solid #1057c8;
  margin: 20px 0 16px;
  letter-spacing: -0.2px;
}

.filter-bar {
  background: white;
  border: 1px solid var(--light2);
  border-radius: 14px;
  padding: 16px 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(10,61,143,0.05);
}
.filter-bar label, .filter-bar .stSelectbox label, .filter-bar .stMultiSelect label {
  color: #03112b !important;
  font-weight: 600 !important;
  font-size: 13px !important;
}
label[data-testid="stWidgetLabel"] {
  color: #03112b !important;
  font-weight: 600 !important;
}
.stSelectbox label, .stMultiSelect label, .stDateInput label {
  color: #03112b !important;
}

.stTabs [data-baseweb="tab-list"] {
  background: var(--light1);
  border-radius: 12px;
  padding: 4px;
  gap: 3px;
}
.stTabs [data-baseweb="tab"] {
  border-radius: 9px;
  font-weight: 600;
  font-size: 13px;
  color: var(--blue1);
  padding: 8px 16px;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, var(--blue2), var(--blue3)) !important;
  color: white !important;
  box-shadow: 0 3px 10px rgba(41,121,255,0.35);
}
.stTabs [data-baseweb="tab-panel"] {
  background: rgba(255,255,255,0.5) !important;
  padding: 20px;
  border-radius: 0 0 12px 12px;
}

div[data-testid="metric-container"] {
  background: white !important;
  border: 1px solid var(--light2) !important;
  border-radius: 14px !important;
  padding: 16px !important;
  box-shadow: 0 2px 12px rgba(10,61,143,0.06) !important;
}
div[data-testid="metric-container"],
div[data-testid="metric-container"] *,
div[data-testid="metric-container"] label,
div[data-testid="metric-container"] p,
div[data-testid="metric-container"] span,
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] *,
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] * {
  color: #03112b !important;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] { 
  font-size: 26px !important; 
  font-weight: 800 !important; 
}
div[data-testid="metric-container"] [data-testid="stMetricLabel"] * { 
  color: #0a3d8f !important; 
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] * { 
  color: #03112b !important; 
}
div[data-baseweb="select"] > div {
  background: white !important;
  border: 1.5px solid var(--light2) !important;
  border-radius: 10px !important;
  font-size: 13px !important;
}
div[data-baseweb="select"] span,
div[data-baseweb="select"] div {
  color: #03112b !important;
}
div[data-baseweb="select"] input {
  color: #03112b !important;
}
div[data-baseweb="tag"] {
  background: var(--blue2) !important;
  border-radius: 6px !important;
}
div[data-baseweb="tag"] span {
  color: white !important;
}

.stDataFrame { border-radius: 12px !important; overflow: hidden !important; }
.stDataFrame thead tr th {
  background: var(--navy) !important;
  color: white !important;
  font-weight: 700 !important;
}
.stDataFrame td, 
.stDataFrame tr,
[data-testid="stDataFrame"] td,
[data-testid="stDataFrame"] div {
  color: #03112b !important;
  background: white !important;
}

div[data-baseweb="popover"] {
  background: white !important;
}

div[role="option"] {
  color: #03112b !important;
  background: white !important;
}

div[role="option"]:hover {
  background: #e8f0fe !important;
  color: #0a3d8f !important;
}
div[data-testid="stExpander"] {
    background: #ffffff !important;
    border: 1.5px solid #1057c8 !important;
    border-radius: 10px !important;
}
div[data-testid="stExpander"] summary {
    color: #1057c8 !important;
    font-weight: 600 !important;
}

div[role="option"][aria-selected="true"] {
  background: #1057c8 !important;
  color: white !important;
  font-weight: 600 !important;
}

ul[role="listbox"] li {
  color: #03112b !important;
  background: white !important;
}

ul[role="listbox"] li:hover {
  background: #e8f0fe !important;
}

ul[role="listbox"] li[aria-selected="true"] {
  background: #1057c8 !important;
  color: white !important;
}

.stAlert {
  border-radius: 12px !important; 
  background: #e8f0fe !important;
  border-left: 4px solid #1057c8 !important;
}
.stAlert p {
  color: #03112b !important;
  font-size: 14px !important;
}
.stAlert svg {
  display: none !important;
}
[data-testid="stFileUploader"] {
  background: white;
  border: 2px dashed var(--light2) !important;
  border-radius: 14px !important;
}

.stSlider [data-baseweb="slider"] { padding: 4px 0 !important; }

div[data-testid="stHorizontalBlock"] { gap: 12px !important; }

.js-plotly-plot .plotly .xtick text,
.js-plotly-plot .plotly .ytick text,
.js-plotly-plot .plotly .legendtext {
  fill: #03112b !important;
}
div[data-baseweb="menu"] {
  background-color: white !important;
}

div[data-baseweb="menu"] li {
  background-color: white !important;
  color: #03112b !important;
}

div[data-baseweb="menu"] li:hover {
  background-color: #e8f0fe !important;
  color: #0a3d8f !important;
}

div[data-baseweb="menu"] li[aria-selected="true"] {
  background-color: #1057c8 !important;
  color: white !important;
}

[role="listbox"] {
  background: white !important;
}

[role="option"] {
  background-color: white !important;
  color: #03112b !important;
  padding: 8px 12px !important;
}

[role="option"]:hover,
[role="option"][data-highlighted="true"] {
  background-color: #e8f0fe !important;
  color: #0a3d8f !important;
}

[role="option"][aria-selected="true"] {
  background-color: #1057c8 !important;
  color: white !important;
  font-weight: 600 !important;
}

div[data-baseweb="popover"] > div {
  background: white !important;
}

div[data-baseweb="select"] [data-baseweb="input"] {
  color: #03112b !important;
}

div[data-baseweb="select"] [role="combobox"] {
  color: #03112b !important;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.9; }
  50% { transform: scale(1.1); opacity: 1; }
}

.renewal-box {
    background: #e8f0fe;
    border-left: 3px solid #1057c8;
    padding: 8px 12px;
    margin: 6px 0;
    border-radius: 6px;
    font-size: 13px;
    color: #03112b;
}

.renewal-heading {
    font-weight: 600;
    color: #0a3d8f;
    margin: 12px 0 8px;
    font-size: 14px;
}

.renewal-title {
    color: #03112b !important;
    font-weight: 800 !important;
    font-size: 18px !important;
    margin: 18px 0 12px 0 !important;
}

[title] {
    pointer-events: none !important;
}
[data-baseweb="tooltip"], [role="tooltip"] {
    display: none !important;
}

.stTabs [data-baseweb="tab-panel"] h1,
.stTabs [data-baseweb="tab-panel"] h2,
.stTabs [data-baseweb="tab-panel"] h3,
.stTabs [data-baseweb="tab-panel"] h4 {
    color: #03112b !important;
    font-weight: 800 !important;
}

[data-testid="stDataFrame"] > div {
    background: white !important;
}
[data-testid="stDataFrame"] iframe {
    color-scheme: light !important;
    min-height: 350px !important;
}
[data-testid="stDataFrame"] {
    background: white !important;
    color-scheme: light !important;
    display: block !important;
    visibility: visible !important;
    height: auto !important;
    overflow: visible !important;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════

CANCEL_SET = {'cancelled','forced cancelled','failed','not active','not found (order)'}
PLANS = ['VIP PLATINUM','VIP STARTER','VIP INFINITY']
PLAN_COLORS = {'VIP PLATINUM':'#1057c8','VIP STARTER':'#00b4d8','VIP INFINITY':'#7c3aed'}
PROMO_DAYS = set(pd.to_datetime([
    '2025-11-10','2025-11-11','2025-11-12','2025-11-13','2025-11-14',
    '2025-11-15','2025-11-16','2025-11-17','2025-11-30',
    '2025-12-01','2025-12-02','2025-12-03','2025-12-24','2025-12-25',
    '2026-01-04','2026-01-06','2026-01-07','2026-01-08','2026-01-31'
]).date)

# ══════════════════════════════════════════════════════════════
# OPTIMIZED CACHING FUNCTIONS
# ══════════════════════════════════════════════════════════════

@st.cache_data(ttl=7200, persist="disk", show_spinner=False, max_entries=100)
def load(f):
    """✅ OPTIMIZED: 2hr cache, disk persist, 100 entries"""
    df = pd.read_csv(f, low_memory=False)
    df['Created At'] = pd.to_datetime(df['Created At'], dayfirst=False, errors='coerce')
    df['End Date']   = pd.to_datetime(df['End Date'],   dayfirst=False, errors='coerce')
    df['Start Date'] = pd.to_datetime(df['Start Date'], dayfirst=False, errors='coerce')
    df['ym']         = df['Created At'].dt.to_period('M').astype(str)
    df['date']       = df['Created At'].dt.date
    df['end_ym']     = df['End Date'].dt.to_period('M').astype(str)
    df['mandate']    = df['Mandate status'].str.lower().str.strip()
    
    df['pm'] = df['Payment Method'].str.lower().str.strip().fillna('null')
    df['Payment Method Clean'] = df['pm'].replace({
        'cc': 'CC', 'dc': 'DC', 'upi': 'UPI',
        'si_cc': 'SI_CC', 'si_upi': 'SI_UPI',
        'si_undefined': 'SI_UNDEFINED', 'null': 'NULL'
    })
    
    df['mandate_clean'] = df['Mandate status'].str.lower().str.strip()
    df['active']        = df['mandate_clean'] == 'active'
    df['cancelled']     = df['mandate_clean'].isin(CANCEL_SET)
    df['is_si']         = df['pm'].isin(['si_cc', 'si_upi'])
    df['is_promo']      = df['date'].isin(PROMO_DAYS)
    df['Grand Total Amount'] = pd.to_numeric(
        df['Grand Total Amount'].astype(str).str.replace(',', '').str.strip(), 
        errors='coerce'
    ).fillna(0)
    return df

@st.cache_data(ttl=3600, show_spinner=False)
def build_cycle_map(df_hash):
    """✅ OPTIMIZED: Build cycle map once, reuse everywhere"""
    df = st.session_state['df']
    order_parent_dict = dict(zip(df['Order Id'], df['Parent Order Id']))
    
    cycle_map = {}
    for order_id in df['Order Id']:
        cycle = 0
        parent = order_parent_dict.get(order_id)
        
        while pd.notna(parent) and parent in order_parent_dict:
            cycle += 1
            parent = order_parent_dict.get(parent)
        
        cycle_map[order_id] = cycle
    
    return cycle_map

@st.cache_data(ttl=3600, show_spinner=False)
def get_month_renewals(df_hash, ym, plans_tuple):
    """✅ OPTIMIZED: Cache month renewals"""
    df = st.session_state['df']
    month_start = pd.Timestamp(f"{ym}-01")
    month_end = month_start + pd.offsets.MonthEnd(0) + pd.Timedelta(hours=23, minutes=59, seconds=59)

    month_renewals = df[
        (df['Parent Order Id'].notna()) &
        (df['Parent Order Id'].isin(df['Order Id'])) & 
        (df['Created At'] >= month_start) &
        (df['Created At'] <= month_end) &
        (df['Payment Status'].str.strip().str.lower() == "success") &
        (df['Subscription Name'].isin(plans_tuple))
    ].copy()
    
    parent_pm = df[["Order Id", "pm"]].rename(columns={
        "Order Id": "Parent Order Id", "pm": "prev_pm"
    })
    month_renewals = month_renewals.merge(parent_pm, on="Parent Order Id", how="left")
    month_renewals["prev_pm"] = month_renewals["prev_pm"].fillna("si_undefined")
    
    return month_renewals

def ctheme(fig, title="", h=380):
    """✅ FIXED: Single definition"""
    fig.update_layout(
        title=dict(text=title, font=dict(family='Outfit',size=14,color='#03112b'), x=0),
        paper_bgcolor='white', plot_bgcolor='white', height=h,
        font=dict(family='Outfit', color='#3a5282', size=12),
        margin=dict(l=12,r=12,t=44,b=12),
        legend=dict(font=dict(size=11), bgcolor='rgba(0,0,0,0)',
                    bordercolor='#dce6fb', borderwidth=1),
        xaxis=dict(gridcolor='#f0f5ff', linecolor='#dce6fb', showline=True),
        yaxis=dict(gridcolor='#f0f5ff', linecolor='#dce6fb', showline=True),
        hoverlabel=dict(bgcolor='#03112b', font_color='white',
                        font_family='Outfit', font_size=12, bordercolor='#1057c8'),
    )
    return fig

def kpi(label, val, delta="", cls=""):
    return f"""<div class='kpi-card {cls}'>
  <div class='kpi-label'>{label}</div>
  <div class='kpi-value'>{val}</div>
  {"<div class='kpi-delta'>" + delta + "</div>" if delta else ""}
</div>"""

def show_table(d, max_rows=500):
    import re
    html_table = d.head(max_rows).to_html(index=False, border=0, escape=True)
    html_table = re.sub(r'\s*title="[^"]*"', '', html_table)
    
    st.markdown(
        '<div style="overflow-x:auto;border-radius:12px;border:1px solid #dce6fb;">' +
        html_table.replace(
            '<table','<table style="width:100%;border-collapse:collapse;font-family:Outfit,sans-serif;font-size:13px;"'
        ).replace(
            '<th>','<th style="background:#03112b;color:white;padding:10px 12px;text-align:left;font-weight:700;">'
        ).replace(
            '<td>','<td style="padding:9px 12px;color:#03112b;background:white;">'
        ) + '</div>',
        unsafe_allow_html=True
    )

# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════

date_range_text = "Upload CSV to view data"
with st.sidebar:
    st.markdown("""
    <div style='padding:24px 16px 16px; text-align:center;'>
      <div style='font-size:28px; letter-spacing:-1px; font-weight:800;
                  background:linear-gradient(135deg,#2979ff,#00b4d8);
                  -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>
        ◈ SubsIQ
      </div>
      <div style='font-size:11px; color:#4a6fa5; margin-top:4px; font-weight:500;
                  letter-spacing:1.5px; text-transform:uppercase;'>Analytics Platform</div>
    </div>
    <hr style='border:none; border-top:1px solid rgba(41,121,255,0.2); margin:4px 0 16px;'>
    """, unsafe_allow_html=True)

    page = st.radio("Navigate", [
        "🏠  Home Overview",
        "📅  Monthly Analysis",
        "⚖️  Month Comparison",
        "📦  Plan Deep Dive",
        "💳  Payment Methods",
        "🔮  Predictions",
        "🔍  Data Explorer",
    ], label_visibility="collapsed")

    st.markdown("""
    <hr style='border:none; border-top:1px solid rgba(41,121,255,0.15); margin:16px 0 12px;'>
    <div style='padding:0 4px;'>
    """, unsafe_allow_html=True)
    uploaded = st.file_uploader("📂 Upload CSV", type="csv", label_visibility="visible")
    st.markdown(f"""
    <div style='font-size:10px; color:#3a5282; margin-top:8px; text-align:center;'>
      {date_range_text}
    </div></div>
    """, unsafe_allow_html=True)

import streamlit.components.v1 as components

if uploaded is None:
    st.markdown("""
    <div style='display:flex; flex-direction:column; align-items:center;
                justify-content:center; min-height:70vh; text-align:center;'>
      <div style='font-size:80px; margin-bottom:20px;
                  background:linear-gradient(135deg, #2979ff 0%, #00b4d8 100%);
                  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                  animation: pulse 2s ease-in-out infinite;'>◈</div>
      <h1 style='font-size:36px; font-weight:800; 
                 background:linear-gradient(135deg, #1057c8 0%, #2979ff 60%, #00b4d8 100%);
                 -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                 letter-spacing:-1px; margin:0 0 12px;'>SubsIQ Analytics</h1>
      <p style='color:#7b93c4; font-size:16px; max-width:400px; line-height:1.6;'>
        Upload your <strong>subscription_order_history.csv</strong> from the sidebar to start exploring your data
      </p>
      <div style='margin-top:32px; display:flex; gap:16px; flex-wrap:wrap; justify-content:center;'>
        <div style='background:white; border:1px solid #dce6fb; border-radius:12px;
                    padding:16px 24px; font-size:13px; color:#3a5282;'>📅 Monthly Analysis</div>
        <div style='background:white; border:1px solid #dce6fb; border-radius:12px;
                    padding:16px 24px; font-size:13px; color:#3a5282;'>⚖️ Month Comparison</div>
        <div style='background:white; border:1px solid #dce6fb; border-radius:12px;
                    padding:16px 24px; font-size:13px; color:#3a5282;'>🔮 Predictions</div>
        <div style='background:white; border:1px solid #dce6fb; border-radius:12px;
                    padding:16px 24px; font-size:13px; color:#3a5282;'>🔄 Renewal Tracker</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════
# DATA LOADING & PROCESSING
# ══════════════════════════════════════════════════════════════

df = load(uploaded)
df = df.sort_values(['User Id', 'Created At'])

# ✅ Create data hash for caching
df_hash = hashlib.md5(pd.util.hash_pandas_object(df).values).hexdigest()[:16]

# Store in session state
st.session_state['df'] = df

# Generate full year months (Jan–Dec 2026) even if data missing
all_yms = sorted(df['ym'].dropna().unique())

future_months = pd.period_range("2026-01", "2026-12", freq="M").astype(str)

all_yms = sorted(set(all_yms).union(set(future_months)))

MONTH_ORDER = all_yms
MONTH_LABELS = {ym: pd.Period(ym, 'M').strftime('%B %Y') for ym in all_yms}
MONTH_SHORT = {ym: pd.Period(ym, 'M').strftime('%b') for ym in all_yms}


# User metrics
user_active_map = df.groupby('User Id')['active'].any()
total_unique_users = len(user_active_map)
active_users_count = int(user_active_map.sum())
inactive_users_count = int((~user_active_map).sum())

def is_reacquired(group):
    statuses = group['mandate_clean'].tolist()
    had_cancel = False
    for s in statuses:
        if s in CANCEL_SET:
            had_cancel = True
        if had_cancel and s == 'active':
            return True
    return False

df_sorted = df.sort_values(['User Id', 'Created At'])
reacquired_users = int(df_sorted.groupby('User Id').apply(is_reacquired, include_groups=False).sum())

date_range_text = f"Data: {df['Created At'].min().strftime('%d %b %Y')} – {df['Created At'].max().strftime('%d %b %Y')}"

# ══════════════════════════════════════════════════════════════
# HOME PAGE
# ══════════════════════════════════════════════════════════════

if "Home" in page:
    st.markdown("""<div class='page-header'>
      <h1>📊 Subscription Overview</h1>
      <p>All-time metrics</p>
    </div>""", unsafe_allow_html=True)
    
    total = len(df); active = int(df['active'].sum()); cancel = int(df['cancelled'].sum())
    si = int(df['is_si'].sum()); rev = int(df['Grand Total Amount'].sum())
    
    st.markdown("<div class='sec-title'>👤 User Metrics</div>", unsafe_allow_html=True)
    u1,u2,u3 = st.columns(3)
    u1.markdown(kpi("Total Unique Users", f"{total_unique_users:,}", "All users"), unsafe_allow_html=True)
    u2.markdown(kpi("Active Users", f"{active_users_count:,}", f"{active_users_count/total_unique_users*100:.1f}% active","green"), unsafe_allow_html=True)
    u3.markdown(kpi("Inactive Users", f"{inactive_users_count:,}", f"{inactive_users_count/total_unique_users*100:.1f}% inactive","red"), unsafe_allow_html=True)
    
    st.markdown("<div class='sec-title'>📦 Subscription Metrics</div>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(kpi("Total Subscriptions", f"{total:,}", "All records"), unsafe_allow_html=True)
    c2.markdown(kpi("Active Subs", f"{active:,}", f"{active/total*100:.1f}% active","green"), unsafe_allow_html=True)
    c3.markdown(kpi("Cancelled Subs", f"{cancel:,}", f"{cancel/total*100:.1f}% churned","red"), unsafe_allow_html=True)
    c4.markdown(kpi("SI Auto-Renewals", f"{si:,}", "Auto-debit confirmed","amber"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c_rev, _ = st.columns([1,3])
    c_rev.markdown(kpi("Total Revenue", f"₹{rev/100000:.1f}L", "Grand total","cyan"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='sec-title'>📊 Plan Performance & Renewals Overview</div>", unsafe_allow_html=True)

    colA, colB = st.columns(2)

    with colA:
        plan_rows = []
        for plan in PLANS:
            pdf = df[df["Subscription Name"] == plan]
            if len(pdf) == 0: continue
            plan_rows.append({
                "Plan": plan.replace("VIP ", ""),
                "Total": len(pdf),
                "Active": int(pdf["active"].sum()),
                "Cancelled": int(pdf["cancelled"].sum())
            })

        plan_df_exec = pd.DataFrame(plan_rows)

        fig_left = go.Figure()
        fig_left.add_trace(go.Bar(
            name="Total",
            x=plan_df_exec["Plan"],
            y=plan_df_exec["Total"],
            marker_color="#1f4ed8",
            text=plan_df_exec["Total"],
            textposition="outside",
            textfont=dict(color="#1f2937", size=12)
        ))
        fig_left.add_trace(go.Bar(
            name="Active",
            x=plan_df_exec["Plan"],
            y=plan_df_exec["Active"],
            marker_color="#10b981",
            text=plan_df_exec["Active"],
            textposition="inside",
            textfont=dict(color="white", size=11)
        ))
        fig_left.add_trace(go.Bar(
            name="Cancelled",
            x=plan_df_exec["Plan"],
            y=plan_df_exec["Cancelled"],
            marker_color="#f43f5e",
            text=plan_df_exec["Cancelled"],
            textposition="inside",
            textfont=dict(color="white", size=11)
        ))
        
        fig_left.update_layout(
            barmode="group",
            height=400,
            paper_bgcolor="white",
            plot_bgcolor="white",
            uniformtext_minsize=10,
            uniformtext_mode="hide",
            title=dict(
                text="Plan Distribution — Total vs Active vs Cancelled",
                x=0.02,
                xanchor="left",
                font=dict(family="Outfit", size=16, color="#1f2937")
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_left.update_traces(cliponaxis=False)
        st.plotly_chart(fig_left, use_container_width=True, key="home_plan_chart")

    with colB:
        renewal_df_exec = df[
            (df["Parent Order Id"].notna()) &
            (df["Payment Status"].str.strip().str.lower() == "success") &
            (~df["pm"].str.lower().isin(["si_undefined"]))
        ].copy()

        renewal_rows = []
        for plan in PLANS:
            rpdf = renewal_df_exec[renewal_df_exec["Subscription Name"] == plan]
            renewal_rows.append({
                "Plan": plan.replace("VIP ", ""),
                "Renewals": len(rpdf)
            })

        renewal_df_plot = pd.DataFrame(renewal_rows)

        fig_right = go.Figure()
        fig_right.add_trace(go.Bar(
            x=renewal_df_plot["Plan"],
            y=renewal_df_plot["Renewals"],
            marker_color="#2563eb",
            text=renewal_df_plot["Renewals"],
            textposition="outside",
            textfont=dict(color="#1f2937", size=12)
        ))

        fig_right.update_layout(
            height=400,
            paper_bgcolor="white",
            plot_bgcolor="white",
            title=dict(
                text="Successful Renewals by Plan (Excl. SI_UNDEFINED)",
                x=0.02,
                xanchor="left",
                font=dict(family="Outfit", size=16, color="#1f2937")
            )
        )
        st.plotly_chart(fig_right, use_container_width=True, key="renewals_chart")

    col1, col2 = st.columns([3,2])

    with col1:
        st.markdown("<div class='sec-title'>Monthly Volume — All Plans</div>", unsafe_allow_html=True)
        rows = []
        for ym in MONTH_ORDER:
            mdf = df[df['ym']==ym]
            for p in PLANS:
                pdf = mdf[mdf['Subscription Name']==p]
                if len(pdf)==0: continue
                rows.append({'Month': MONTH_SHORT[ym], 'Plan': p, 'Count': len(pdf)})
        mdf2 = pd.DataFrame(rows)
        fig = go.Figure()
        for p in PLANS:
            pd3 = mdf2[mdf2['Plan']==p]
            fig.add_trace(go.Bar(name=p.replace('VIP ',''), x=pd3['Month'], y=pd3['Count'],
                marker_color=PLAN_COLORS[p], opacity=0.88,
                text=pd3['Count'], textposition='inside',
                textfont=dict(color='white', size=11, family='Outfit'),
            ))
        fig = ctheme(fig, "Monthly Subscriptions by Plan", h=360)
        fig.update_layout(barmode='group', bargap=0.22, bargroupgap=0.05)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='sec-title'>Overall Status Split</div>", unsafe_allow_html=True)
        fig2 = go.Figure(go.Pie(
            labels=['Active','Cancelled'], values=[active, cancel],
            hole=0.6, marker_colors=['#00c896','#ff4d6d'],
            textfont_size=13, textfont_family='Outfit',
        ))
        fig2.update_layout(
            paper_bgcolor='white', height=360,
            title=dict(text="All-time Status",font=dict(family='Outfit',size=14,color='#03112b')),
            margin=dict(l=12,r=12,t=44,b=12),
            legend=dict(font=dict(size=12),bgcolor='rgba(0,0,0,0)'),
            annotations=[dict(text=f"<b>{active/total*100:.0f}%</b><br>Active",
                              x=0.5,y=0.5,showarrow=False,
                              font=dict(size=16,family='Outfit',color='#03112b'))]
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='sec-title'>Daily Orders Timeline — Organic vs Promo</div>", unsafe_allow_html=True)
    daily = df.groupby('date').size().reset_index(name='n')
    daily['date'] = pd.to_datetime(daily['date'])
    daily['promo'] = daily['date'].dt.date.isin(PROMO_DAYS)
    org = daily[~daily['promo']]; prm = daily[daily['promo']]

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=org['date'], y=org['n'], mode='lines+markers', name='Organic Day',
        line=dict(color='#1057c8', width=2.5),
        marker=dict(size=5, color='#1057c8'),
        hovertemplate='<b>%{x|%d %b}</b><br>Orders: %{y}<extra></extra>',
    ))
    fig3.add_trace(go.Scatter(
        x=prm['date'], y=prm['n'], mode='markers', name='Promo Day',
        marker=dict(size=14, color='#ffb300', symbol='diamond',
                    line=dict(color='white',width=2)),
        hovertemplate='<b>%{x|%d %b}</b> 🎯<br>Promo orders: %{y}<extra></extra>',
    ))
    for x0,x1,label,c in [
        ('2025-12-23','2025-12-26','Christmas 🎄',"#930A2E"),
        ('2026-01-06','2026-01-09','New Year 🎆',"#71b906"),
    ]:
        fig3.add_vrect(x0=x0,x1=x1,fillcolor=c,opacity=0.4,line_width=0,
                       annotation_text=label,annotation_position="top left",
                       annotation_font_size=11,annotation_font_color='#3a5282')
    fig3 = ctheme(fig3, "Daily Orders — Full Period", h=320)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<div class='sec-title'>Payment Method Summary</div>", unsafe_allow_html=True)
    pm_rows = []
    for pm in ['cc', 'dc', 'upi', 'si_cc', 'si_upi', 'si_undefined', 'null']:
        if pm == 'null':
            pdf = df[df['pm'].isin(['null', '', 'nan']) | df['pm'].isna()]
            pm_label = 'NULL'
        else:
            pdf = df[df['pm'] == pm]
            pm_label = pm.upper()
        
        if len(pdf) == 0: continue
            
        pm_rows.append({
            'Payment Method': pm_label,
            'Total': len(pdf),
            'Active': int(pdf['active'].sum()),
            'Cancelled': int(pdf['cancelled'].sum()),
            'Active %': f"{pdf['active'].sum()/len(pdf)*100:.1f}%",
            'Cancel %': f"{pdf['cancelled'].sum()/len(pdf)*100:.1f}%",
            'Revenue': f"₹{int(pdf['Grand Total Amount'].sum()):,}",
        })
    pm_df = pd.DataFrame(pm_rows)
    show_table(pm_df)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        fig_pm = go.Figure()
        fig_pm.add_trace(go.Bar(
            name='Total', x=pm_df['Payment Method'], y=pm_df['Total'],
            marker_color='#1057c8', opacity=0.7,
            text=pm_df['Total'], textposition='outside', textfont=dict(size=11)
        ))
        fig_pm.add_trace(go.Bar(
            name='Active', x=pm_df['Payment Method'], y=pm_df['Active'],
            marker_color='#00c896', opacity=0.85,
            text=pm_df['Active'], textposition='inside', textfont=dict(color='white',size=11)
        ))
        fig_pm.add_trace(go.Bar(
            name='Cancelled', x=pm_df['Payment Method'], y=pm_df['Cancelled'],
            marker_color='#ff4d6d', opacity=0.85,
            text=pm_df['Cancelled'], textposition='inside', textfont=dict(color='white',size=11)
        ))
        fig_pm = ctheme(fig_pm, "Payment Method — Total vs Active vs Cancelled", h=380)
        fig_pm.update_layout(barmode='group', bargap=0.2)
        st.plotly_chart(fig_pm, use_container_width=True)
        
    with col2:
        fig_pm2 = go.Figure()
        fig_pm2.add_trace(go.Bar(
            name='Active', x=pm_df['Payment Method'], y=pm_df['Active'],
            marker_color='#00c896', opacity=0.88,
            text=pm_df['Active'], textposition='inside', textfont=dict(color='white',size=11)
        ))
        fig_pm2.add_trace(go.Bar(
            name='Cancelled', x=pm_df['Payment Method'], y=pm_df['Cancelled'],
            marker_color='#ff4d6d', opacity=0.88,
            text=pm_df['Cancelled'], textposition='inside', textfont=dict(color='white',size=11)
        ))
        fig_pm2 = ctheme(fig_pm2, "Payment Method — Active vs Cancelled Split", h=380)
        fig_pm2.update_layout(barmode='stack')
        st.plotly_chart(fig_pm2, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# MONTHLY ANALYSIS PAGE
# ══════════════════════════════════════════════════════════════

elif "Monthly Analysis" in page:
    st.markdown("""<div class='page-header'>
      <h1>📅 Monthly Analysis</h1>
      <p>Deep dive into any month — filter by plan, payment, date range</p>
    </div>""", unsafe_allow_html=True)

    fc1,fc2 = st.columns([2,2])
    with fc1:
        sel_m = st.selectbox("Select Month", ["-- Please Select Month --"] + list(MONTH_LABELS.values()), key='ma_month')
        if sel_m == "-- Please Select Month --":
            st.info("👆 Please select a month to view analysis.")
            st.stop()
    with fc2:
        sel_p = st.multiselect("Plan Filter", PLANS, default=PLANS, key='ma_plan')

    rev_map = {v:k for k,v in MONTH_LABELS.items()}
    ym = rev_map.get(sel_m,'2025-11')
    fdf = df[(df['ym']==ym) & (df['Subscription Name'].isin(sel_p))]

    if len(fdf)==0:
        st.warning("No data for selected filters."); st.stop()

    total = len(fdf); act = int(fdf['active'].sum()); can = int(fdf['cancelled'].sum())
    days = fdf['date'].nunique()
    drr_total = round(total/days,1) if days else 0
    org_fdf = fdf[~fdf['is_promo']]
    drr_org = round(len(org_fdf)/max(org_fdf['date'].nunique(),1),1)
    
    # ✅ OPTIMIZED: Use cached renewal calculation
    month_renewals = get_month_renewals(df_hash, ym, tuple(sel_p))
    si_cnt = int(month_renewals['pm'].isin(['si_cc','si_upi']).sum())

    k1,k2,k3,k4,k5,k6 = st.columns(6)
    k1.markdown(kpi("Total Subs", f"{total:,}"), unsafe_allow_html=True)
    k2.markdown(kpi("Active", f"{act:,}", f"{act/total*100:.1f}%","green"), unsafe_allow_html=True)
    k3.markdown(kpi("Cancelled", f"{can:,}", f"{can/total*100:.1f}%","red"), unsafe_allow_html=True)
    k4.markdown(kpi("Total DRR", f"{drr_total}", "orders/day"), unsafe_allow_html=True)
    k5.markdown(kpi("Organic DRR", f"{drr_org}", "excl. promo days","cyan"), unsafe_allow_html=True)
    k6.markdown(kpi("SI Renewals", f"{si_cnt}", "auto-debit","amber"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    tab1,tab2,tab3 = st.tabs(["📊 Charts","📋 Plan × Payment Table","📈 Daily Trend"])

    with tab1:
        c1,c2 = st.columns(2)
        with c1:
            rows = []
            for p in sel_p:
                pdf = fdf[fdf['Subscription Name']==p]
                if len(pdf)==0: continue
                rows += [{'Plan':p,'Status':'Active','Count':int(pdf['active'].sum())},
                         {'Plan':p,'Status':'Cancelled','Count':int(pdf['cancelled'].sum())}]
            fig = go.Figure()
            for status, color in [('Active','#00c896'),('Cancelled','#ff4d6d')]:
                d = [r['Count'] for r in rows if r['Status']==status]
                l = [r['Plan'].replace('VIP ','') for r in rows if r['Status']==status]
                fig.add_trace(go.Bar(name=status, x=l, y=d,
                                     marker_color=color, opacity=0.88,
                                     text=d, textposition='inside',
                                     textfont=dict(color='white',size=11)))
            fig = ctheme(fig, f"Active vs Cancelled — {MONTH_SHORT[ym]}")
            fig.update_layout(barmode='stack')
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            plan_counts = [(p.replace('VIP ',''), len(fdf[fdf['Subscription Name']==p])) for p in sel_p if len(fdf[fdf['Subscription Name']==p])>0]
            if plan_counts:
                fig2 = go.Figure(go.Pie(
                    labels=[x[0] for x in plan_counts],
                    values=[x[1] for x in plan_counts],
                    hole=0.55,
                    marker_colors=[PLAN_COLORS[f'VIP {x[0]}'] if f'VIP {x[0]}' in PLAN_COLORS else '#aaa' for x in plan_counts],
                    textfont_size=13, textfont_family='Outfit',
                ))
                fig2.update_layout(
                    paper_bgcolor='white', height=380,
                    title=dict(text="Plan Split",font=dict(family='Outfit',size=14,color='#03112b')),
                    margin=dict(l=12,r=12,t=44,b=12),
                    legend=dict(font=dict(size=12),bgcolor='rgba(0,0,0,0)'),
                    annotations=[dict(text=f"<b>{total:,}</b><br>Total",
                                      x=0.5,y=0.5,showarrow=False,
                                      font=dict(size=15,family='Outfit',color='#03112b'))]
                )
                st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        rows3 = []
        for p in sel_p:
            pdf = fdf[fdf['Subscription Name'] == p]
            if len(pdf) == 0: continue
            
            for pm in ['cc', 'dc', 'upi', 'si_cc', 'si_upi', 'si_undefined', 'null']:
                if pm == 'null':
                    pmd = pdf[pdf['pm'].isin(['null', '', 'nan']) | pdf['pm'].isna()]
                else:
                    pmd = pdf[pdf['pm'] == pm]
                    
                if len(pmd) == 0: continue
                
                rows3.append({
                    'Plan': p, 
                    'Payment': pm.upper(),
                    'Total': len(pmd),
                    'Active': int(pmd['active'].sum()),
                    'Cancelled': int(pmd['cancelled'].sum()),
                    'Active%': f"{pmd['active'].sum()/len(pmd)*100:.0f}%",
                    'Revenue': f"₹{int(pmd['Grand Total Amount'].sum()):,}",
                })
        if rows3:
            show_table(pd.DataFrame(rows3))

    with tab3:
        daily_f = fdf.groupby('date').size().reset_index(name='n')
        daily_f['date'] = pd.to_datetime(daily_f['date'])
        daily_f['promo'] = daily_f['date'].dt.date.isin(PROMO_DAYS)
        fig_d = go.Figure()
        od = daily_f[~daily_f['promo']]; pd2 = daily_f[daily_f['promo']]
        fig_d.add_trace(go.Scatter(x=od['date'],y=od['n'],mode='lines+markers',name='Organic',
                                   line=dict(color='#1057c8',width=2.5),marker=dict(size=7),
                                   hovertemplate='<b>%{x|%d %b}</b><br>%{y} orders<extra></extra>'))
        if len(pd2):
            fig_d.add_trace(go.Scatter(x=pd2['date'],y=pd2['n'],mode='markers',name='Promo',
                                       marker=dict(size=14,color='#ffb300',symbol='diamond',
                                                   line=dict(color='white',width=2)),
                                       hovertemplate='<b>%{x|%d %b}</b> 🎯<br>%{y} orders<extra></extra>'))
        fig_d = ctheme(fig_d, "Daily Orders Trend", h=360)
        st.plotly_chart(fig_d, use_container_width=True)
        st.info(f"📊 **Organic DRR:** {drr_org}/day  |  **Promo days:** {fdf['is_promo'].sum()} orders in promo days  |  **Total DRR:** {drr_total}/day")

    # ══════════════════════════════════════════════════════════════
    # RENEWAL ANALYSIS (OPTIMIZED)
    # ══════════════════════════════════════════════════════════════
    
    with st.expander("🔄 Renewal Analysis", expanded=False):
        st.markdown("<div class='sec-title'>Renewal Tracking</div>", unsafe_allow_html=True)
        
        renewal_data = []
        for _, order in month_renewals.iterrows():
            renewal_data.append({
                'User Id'     : order['User Id'],
                'Subscription': order['Subscription Name'],
                'Prev Order Id': order['Parent Order Id'],
                'Prev Payment': order['prev_pm'].upper(),
                'New Order Id': order['Order Id'],
                'New Start'   : order['Start Date'].strftime('%Y-%m-%d') if pd.notna(order['Start Date']) else '',
                'New End'     : order['End Date'].strftime('%Y-%m-%d')   if pd.notna(order['End Date'])   else '',
                'New Payment' : order['pm'].upper(),
            })
        
        if renewal_data:
            renewal_df = pd.DataFrame(renewal_data)
            total_renewals = len(renewal_df)
            si_renewals = renewal_df['New Payment'].isin(['SI_CC', 'SI_UPI']).sum()
            manual_renewals = total_renewals - si_renewals
            
            r1, r2 = st.columns(2)
            r1.markdown(kpi("Total Renewals", f"{total_renewals:,}"), unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            rt1, rt2, rt3 = st.tabs(["📊 By Subscription", "💳 By Payment", "📋 Full Details"])
            
            with rt1:
                sub_renewal = renewal_df.groupby('Subscription').size().reset_index(name='Total')
                fig_sub = go.Figure()
                fig_sub.add_trace(go.Bar(
                    name='Renewals',
                    x=sub_renewal['Subscription'],
                    y=sub_renewal['Total'],
                    marker_color='#ffb300',
                    opacity=0.9,
                    text=sub_renewal['Total'],
                    textposition='inside',
                    textfont=dict(color='white', size=12)
                ))
                fig_sub = ctheme(fig_sub, "Renewals by Subscription Type")
                st.plotly_chart(fig_sub, use_container_width=True)
            
            with rt2:
                st.markdown("<div class='renewal-title'>🔹 Overall Renewal Payment Method</div>", unsafe_allow_html=True)
                overall_conversion = (
                    renewal_df
                    .groupby(['Prev Payment', 'New Payment'])
                    .size()
                    .reset_index(name='Count')
                )
                show_table(overall_conversion)

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("<div class='renewal-heading'>Overall – Previous Payment Methods:</div>", unsafe_allow_html=True)
                    prev_pm = renewal_df['Prev Payment'].value_counts()
                    for pm, count in prev_pm.items():
                        st.markdown(f"<div class='renewal-box'>{pm}: {count}</div>", unsafe_allow_html=True)

                with c2:
                    st.markdown("<div class='renewal-heading'>Overall – Current Payment Methods:</div>", unsafe_allow_html=True)
                    new_pm = renewal_df['New Payment'].value_counts()
                    for pm, count in new_pm.items():
                        st.markdown(f"<div class='renewal-box'>{pm}: {count}</div>", unsafe_allow_html=True)

                st.markdown("---")
                
                #  OPTIMIZED: Use cached cycle map
                st.markdown("<div class='renewal-heading'>🔄 Renewal Cycle Breakdown</div>", unsafe_allow_html=True)
                
                cycle_map = build_cycle_map(df_hash)
                
                #  VECTORIZED: Apply cycle map to all orders at once
                renewal_df['Cycle'] = renewal_df['New Order Id'].map(cycle_map).fillna(0).astype(int)
                
                all_cycle_data = []
                for plan in sorted(renewal_df['Subscription'].unique()):
                    plan_renewals = renewal_df[renewal_df['Subscription'] == plan]
                    
                    for cycle_num in sorted(plan_renewals['Cycle'].unique()):
                        cycle_data = plan_renewals[plan_renewals['Cycle'] == cycle_num]
                        all_cycle_data.append({
                            'Plan': plan.replace('VIP ', ''),
                            'Cycle': f"Cycle {cycle_num}",
                            'Count': len(cycle_data)
                        })
                
                if all_cycle_data:
                    cycle_df = pd.DataFrame(all_cycle_data)
                    
                    fig_cycle = go.Figure()
                    for plan in cycle_df['Plan'].unique():
                        plan_data = cycle_df[cycle_df['Plan'] == plan]
                        fig_cycle.add_trace(go.Bar(
                            name=plan,
                            x=plan_data['Cycle'],
                            y=plan_data['Count'],
                            text=plan_data['Count'],
                            textposition='outside',
                            textfont=dict(size=11),
                            marker_color='#ffb300' if 'STARTER' in plan else '#1057c8',
                            opacity=0.85
                        ))
                    
                    fig_cycle = ctheme(fig_cycle, f"Renewal Cycles - {MONTH_LABELS[ym]}", h=350)
                    fig_cycle.update_layout(barmode='group', xaxis_title="", yaxis_title="Number of Renewals")
                    st.plotly_chart(fig_cycle, use_container_width=True)
                    
                    st.markdown("---")
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("<div class='renewal-heading'>📊 Subscription Renewal Journey</div>", unsafe_allow_html=True)

                    #  OPTIMIZED: Build journey map once
                    @st.cache_data(ttl=3600, show_spinner=False)
                    def build_journey_data(df_hash, renewal_order_ids):
                        order_parent_map = dict(zip(df['Order Id'], df['Parent Order Id']))
                        order_date_map = dict(zip(df['Order Id'], df['Created At']))
                        
                        journeys = []
                        for order_id in renewal_order_ids:
                            if pd.isna(order_id):
                                continue
                            
                            months = []
                            current = order_id
                            
                            while pd.notna(current) and current in order_parent_map:
                                dt = order_date_map.get(current)
                                if pd.notna(dt):
                                    months.append(dt.strftime("%b"))
                                current = order_parent_map.get(current)
                            
                            months = list(reversed(months))
                            
                            if len(months) > 1:
                                journey = " → ".join(months)
                                cycle = len(months) - 1
                                journeys.append({'order_id': order_id, 'cycle': cycle, 'journey': journey})
                        
                        return pd.DataFrame(journeys)
                    
                    journey_base = build_journey_data(df_hash, tuple(renewal_df['New Order Id'].dropna().unique()))
                    
                    if len(journey_base) > 0:
                        # Merge with renewal_df to get Plan
                        journey_df = renewal_df[['New Order Id', 'Subscription']].merge(
                            journey_base, 
                            left_on='New Order Id', 
                            right_on='order_id',
                            how='inner'
                        )
                        journey_df['Plan'] = journey_df['Subscription'].str.replace('VIP ', '')
                        
                        journey_summary = (
                            journey_df
                            .groupby(['Plan', 'cycle', 'journey'])
                            .size()
                            .reset_index(name='Subscriptions')
                        )
                        
                        plan_order = {"PLATINUM":0, "STARTER":1}
                        journey_summary['PlanOrder'] = journey_summary['Plan'].map(plan_order)
                        journey_summary = journey_summary.sort_values(
                            ['PlanOrder', 'cycle', 'Subscriptions'],
                            ascending=[True, True, False]
                        ).drop(columns=['PlanOrder'])
                        journey_summary.rename(columns={'cycle': 'Cycle', 'journey': 'Journey'}, inplace=True)
                        
                        show_table(journey_summary)
                        
                        for plan in sorted(renewal_df['Subscription'].unique()):
                            plan_cycles = cycle_df[cycle_df['Plan'] == plan.replace('VIP ', '')]
                            if not plan_cycles.empty:
                                cycle_summary = " | ".join([
                                    f"<b>{row['Cycle']}</b>: {row['Count']}" 
                                    for _, row in plan_cycles.iterrows()
                                ])
                                st.markdown(
                                    f"<div class='renewal-box'><b>{plan}</b>: {cycle_summary}</div>",
                                    unsafe_allow_html=True
                                )
                    else:
                        st.info("No renewal journeys found")

                st.markdown("---")

                for plan in sorted(renewal_df['Subscription'].unique()):
                    st.markdown(f"<div class='renewal-title'>🔹 {plan} – Renewal Payment Method</div>", unsafe_allow_html=True)
                    plan_df = renewal_df[
                        (renewal_df['Subscription'] == plan) &
                        (renewal_df['Cycle'].notna())
                    ]

                    plan_conversion = (
                        plan_df
                        .groupby(['Prev Payment', 'New Payment'])
                        .size()
                        .reset_index(name='Count')
                    )
                    show_table(plan_conversion)

                    pc1, pc2 = st.columns(2)
                    with pc1:
                        st.markdown(f"<div class='renewal-heading'>{plan} – Previous Payment Methods:</div>", unsafe_allow_html=True)
                        prev_pm_plan = plan_df['Prev Payment'].value_counts()
                        for pm, count in prev_pm_plan.items():
                            st.markdown(f"<div class='renewal-box'>{pm}: {count}</div>", unsafe_allow_html=True)

                    with pc2:
                        st.markdown(f"<div class='renewal-heading'>{plan} – Current Payment Methods:</div>", unsafe_allow_html=True)
                        new_pm_plan = plan_df['New Payment'].value_counts()
                        for pm, count in new_pm_plan.items():
                            st.markdown(f"<div class='renewal-box'>{pm}: {count}</div>", unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)

                st.info(f"📊 Total Renewals: {len(renewal_df)}")
            
            with rt3:
                show_table(renewal_df[['User Id','Subscription','Prev Order Id','Prev Payment','New Order Id','New Start','New End','New Payment']])
                csv = renewal_df.to_csv(index=False).encode('utf-8')
                st.download_button("⬇️ Download Renewal Data", csv, f"renewals_{ym}.csv", "text/csv")
        else:
            st.info("No renewals found for the selected month and plan filters.")

# ══════════════════════════════════════════════════════════════
# MONTH COMPARISON PAGE
# ══════════════════════════════════════════════════════════════

elif "Comparison" in page:
    st.markdown("""<div class='page-header'>
      <h1>⚖️ Month Comparison</h1>
      <p>Compare any months side by side — sales, active, cancelled, DRR, plan mix</p>
    </div>""", unsafe_allow_html=True)

    fc1,fc2,fc3 = st.columns([2,2,1])
    with fc1:
        months_sel = st.multiselect("Select Months to Compare", list(MONTH_LABELS.values()), default=[], key='comp_months')
    with fc2:
        plans_sel = st.multiselect("Plans", PLANS, default=PLANS, key='comp_plans')
    with fc3:
        metric_type = st.selectbox("Compare By", ["Total","Active","Cancelled","DRR","Revenue"], key='comp_metric')

    rev_map = {v:k for k,v in MONTH_LABELS.items()}
    sel_yms = [rev_map[m] for m in months_sel if m in rev_map]

    if len(sel_yms) < 2:
        st.warning("Please select at least 2 months to compare."); st.stop()

    #  OPTIMIZED: Cache comparison data
    @st.cache_data(ttl=3600, show_spinner=False)
    def get_comparison_data(df_hash, sel_yms_tuple, plans_tuple):
        comp = []
        for ym in sel_yms_tuple:
            mdf = df[(df['ym']==ym)&(df['Subscription Name'].isin(plans_tuple))]
            days = mdf['date'].nunique()
            org = mdf[~mdf['is_promo']]
            
            ym_start = pd.Timestamp(f"{ym}-01")
            ym_end = ym_start + pd.offsets.MonthEnd(0) + pd.Timedelta(hours=23, minutes=59, seconds=59)
            si_ym = df[
                (df['Parent Order Id'].notna()) &
                (df['Parent Order Id'].isin(df['Order Id'])) &
                (df['Created At'] >= ym_start) &
                (df['Created At'] <= ym_end) &
                (df['Payment Status'].str.strip().str.lower() == 'success') &
                (df['Subscription Name'].isin(plans_tuple))
            ]
            
            comp.append({
                'ym': ym,
                'Month': MONTH_LABELS[ym],
                'Short': MONTH_SHORT[ym],
                'Total': len(mdf),
                'Active': int(mdf['active'].sum()),
                'Cancelled': int(mdf['cancelled'].sum()),
                'DRR': round(len(mdf)/days,1) if days else 0,
                'Organic DRR': round(len(org)/max(org['date'].nunique(),1),1),
                'Revenue': int(mdf['Grand Total Amount'].sum()),
                'SI': int(len(si_ym)),
                'Active%': round(mdf['active'].sum()/max(len(mdf),1)*100,1),
                'Cancel%': round(mdf['cancelled'].sum()/max(len(mdf),1)*100,1),
            })
        return pd.DataFrame(comp)
    
    cdf = get_comparison_data(df_hash, tuple(sel_yms), tuple(plans_sel))

    st.markdown("<div class='sec-title'>At a Glance</div>", unsafe_allow_html=True)
    cols = st.columns(len(sel_yms))
    for i,(_, row) in enumerate(cdf.iterrows()):
        with cols[i]:
            prev = cdf.iloc[i-1] if i > 0 else None
            delta_str = ""
            if prev is not None:
                delta = row['Total'] - prev['Total']
                delta_str = f"{'▲' if delta>=0 else '▼'} {abs(delta):,} vs {prev['Short']}"
            cls = "green" if i==0 else ("cyan" if i==1 else ("amber" if i==2 else ""))
            st.markdown(kpi(row['Month'], f"{row['Total']:,}", delta_str, cls), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    t1,t2,t3,t4,t5 = st.tabs(["📊 Side by Side","📈 Trend Lines","🥧 Status Mix","💳 Payment Split","📋 Full Table"])

    with t1:
        c1,c2 = st.columns(2)
        with c1:
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Total', x=cdf['Short'], y=cdf['Total'],
                                 marker_color='#1057c8', opacity=0.85,
                                 text=cdf['Total'], textposition='outside', textfont=dict(size=12)))
            fig.add_trace(go.Bar(name='Active', x=cdf['Short'], y=cdf['Active'],
                                 marker_color='#00c896', opacity=0.88,
                                 text=cdf['Active'], textposition='outside', textfont=dict(size=12)))
            fig.add_trace(go.Bar(name='Cancelled', x=cdf['Short'], y=cdf['Cancelled'],
                                 marker_color='#ff4d6d', opacity=0.88,
                                 text=cdf['Cancelled'], textposition='outside', textfont=dict(size=12)))
            fig = ctheme(fig, "Total vs Active vs Cancelled — Month Comparison", h=400)
            fig.update_layout(barmode='group', bargap=0.25)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                name='Active %', x=cdf['Short'], y=cdf['Active%'],
                marker_color='#00c896', opacity=0.88,
                text=[f"{v}%" for v in cdf['Active%']], textposition='inside',
                textfont=dict(color='white',size=12)))
            fig2.add_trace(go.Bar(
                name='Cancel %', x=cdf['Short'], y=cdf['Cancel%'],
                marker_color='#ff4d6d', opacity=0.88,
                text=[f"{v}%" for v in cdf['Cancel%']], textposition='inside',
                textfont=dict(color='white',size=12)))
            fig2 = ctheme(fig2, "Active % vs Cancel % Comparison", h=400)
            fig2.update_layout(barmode='stack', yaxis=dict(ticksuffix='%'))
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("<div class='sec-title'>Plan-wise Breakdown by Month</div>", unsafe_allow_html=True)
        plan_comp = []
        for ym in sel_yms:
            mdf = df[(df['ym']==ym)&(df['Subscription Name'].isin(plans_sel))]
            for p in plans_sel:
                pdf = mdf[mdf['Subscription Name']==p]
                if len(pdf)==0: continue
                plan_comp.append({'Month':MONTH_SHORT[ym],'Plan':p.replace('VIP ',''),
                                  'Count':len(pdf),'Active':int(pdf['active'].sum()),
                                  'Cancelled':int(pdf['cancelled'].sum())})
        pc_df = pd.DataFrame(plan_comp)
        if len(pc_df):
            fig3 = go.Figure()
            for p in plans_sel:
                pshort = p.replace('VIP ','')
                pdata = pc_df[pc_df['Plan']==pshort]
                fig3.add_trace(go.Bar(
                    name=pshort, x=pdata['Month'], y=pdata['Count'],
                    marker_color=PLAN_COLORS[p], opacity=0.88,
                    text=pdata['Count'], textposition='outside', textfont=dict(size=11),
                ))
            fig3 = ctheme(fig3, "Plan Volume by Month", h=360)
            fig3.update_layout(barmode='group')
            st.plotly_chart(fig3, use_container_width=True)

    with t2:
        c1,c2 = st.columns(2)
        with c1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=cdf['Short'], y=cdf['Total'], mode='lines+markers',
                                     name='Total', line=dict(color='#1057c8',width=3),
                                     marker=dict(size=10,color='#1057c8',line=dict(color='white',width=2))))
            fig.add_trace(go.Scatter(x=cdf['Short'], y=cdf['Active'], mode='lines+markers',
                                     name='Active', line=dict(color='#00c896',width=3),
                                     marker=dict(size=10,color='#00c896',line=dict(color='white',width=2))))
            fig.add_trace(go.Scatter(x=cdf['Short'], y=cdf['Cancelled'], mode='lines+markers',
                                     name='Cancelled', line=dict(color='#ff4d6d',width=3),
                                     marker=dict(size=10,color='#ff4d6d',line=dict(color='white',width=2))))
            fig = ctheme(fig, "Volume Trend Across Months", h=380)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(name='Total DRR', x=cdf['Short'], y=cdf['DRR'],
                                  marker_color='#1057c8', opacity=0.7))
            fig2.add_trace(go.Bar(name='Organic DRR', x=cdf['Short'], y=cdf['Organic DRR'],
                                  marker_color='#00b4d8', opacity=0.9,
                                  text=cdf['Organic DRR'], textposition='outside', textfont=dict(size=12)))
            fig2 = ctheme(fig2, "DRR Comparison — Total vs Organic", h=380)
            fig2.update_layout(barmode='group')
            st.plotly_chart(fig2, use_container_width=True)

    with t3:
        pie_cols = st.columns(len(sel_yms))
        for i,(_, row) in enumerate(cdf.iterrows()):
            with pie_cols[i]:
                fig = go.Figure(go.Pie(
                    labels=['Active','Cancelled'], values=[row['Active'],row['Cancelled']],
                    hole=0.6, marker_colors=['#00c896','#ff4d6d'], textfont_size=12,
                ))
                fig.update_layout(
                    paper_bgcolor='white', height=280,
                    title=dict(text=row['Month'],font=dict(family='Outfit',size=13,color='#03112b')),
                    margin=dict(l=8,r=8,t=36,b=8),
                    legend=dict(font=dict(size=11),bgcolor='rgba(0,0,0,0)'),
                    annotations=[dict(text=f"<b>{row['Active%']}%</b><br>Active",
                                      x=0.5,y=0.5,showarrow=False,
                                      font=dict(size=14,family='Outfit',color='#03112b'))]
                )
                st.plotly_chart(fig, use_container_width=True)

    with t4:
        pm_comp = []
        for ym in sel_yms:
            mdf = df[(df['ym']==ym)&(df['Subscription Name'].isin(plans_sel))]
            for pm in ['cc','dc','upi','si_cc']:
                cnt = int((mdf['pm']==pm).sum())
                if cnt==0: continue
                pm_comp.append({'Month':MONTH_SHORT[ym],'Payment':pm.upper(),'Count':cnt})
        if pm_comp:
            pm_df = pd.DataFrame(pm_comp)
            fig = px.bar(pm_df, x='Month', y='Count', color='Payment', barmode='group',
                         color_discrete_map={'CC':'#1057c8','DC':'#00b4d8','UPI':'#7c3aed','SI_CC':'#ffb300'},
                         text='Count')
            fig = ctheme(fig, "Payment Method by Month")
            fig.update_traces(textposition='outside',textfont_size=11)
            st.plotly_chart(fig, use_container_width=True)

    with t5:
        display_cols = ['Month','Total','Active','Cancelled','Active%','Cancel%',
                        'DRR','Organic DRR','Revenue','SI']
        show_table(cdf[display_cols])
        csv_out = cdf.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download Comparison CSV", csv_out, "month_comparison.csv", "text/csv")

# ══════════════════════════════════════════════════════════════
# PLAN DEEP DIVE PAGE
# ══════════════════════════════════════════════════════════════

elif "Plan" in page:
    st.markdown("""<div class='page-header'>
      <h1>📦 Plan Deep Dive</h1>
      <p>Cancellation funnel, payment breakdown, cohort survival per plan</p>
    </div>""", unsafe_allow_html=True)

    p1,p2 = st.columns([1,2])
    with p1: sel_plan = st.selectbox("Select Plan", PLANS)
    with p2:sel_mo_pl = st.multiselect("Month", list(MONTH_LABELS.values()), default=[], key='pl_month')
    rev_map = {v:k for k,v in MONTH_LABELS.items()}
    yms = [rev_map[m] for m in sel_mo_pl if m in rev_map]
    pdf = df[(df['Subscription Name']==sel_plan)&(df['ym'].isin(yms))]
    if len(pdf)==0: st.warning("No data."); st.stop()

    k1,k2,k3,k4 = st.columns(4)
    k1.markdown(kpi("Total", f"{len(pdf):,}"), unsafe_allow_html=True)
    k2.markdown(kpi("Active", f"{pdf['active'].sum():,}", f"{pdf['active'].sum()/len(pdf)*100:.1f}%","green"), unsafe_allow_html=True)
    k3.markdown(kpi("Cancelled", f"{pdf['cancelled'].sum():,}", f"{pdf['cancelled'].sum()/len(pdf)*100:.1f}%","red"), unsafe_allow_html=True)
    k4.markdown(kpi("SI Renewals", f"{pdf['is_si'].sum():,}", "auto-debit","amber"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    t1,t2,t3 = st.tabs(["📊 Monthly Trend","🔽 Cancellation Funnel","💳 Payment Split"])

    with t1:
        monthly_pl = []
        for ym in yms:
            mdf = pdf[pdf['ym']==ym]
            monthly_pl.append({'Month':MONTH_SHORT[ym],'Total':len(mdf),
                                'Active':int(mdf['active'].sum()),'Cancelled':int(mdf['cancelled'].sum()),
                                'Active%':round(mdf['active'].sum()/max(len(mdf),1)*100,1)})
        pl_df = pd.DataFrame(monthly_pl)
        c1,c2 = st.columns(2)
        with c1:
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Active',x=pl_df['Month'],y=pl_df['Active'],
                                 marker_color='#00c896',opacity=0.88,text=pl_df['Active'],textposition='inside',textfont=dict(color='white',size=11)))
            fig.add_trace(go.Bar(name='Cancelled',x=pl_df['Month'],y=pl_df['Cancelled'],
                                 marker_color='#ff4d6d',opacity=0.88,text=pl_df['Cancelled'],textposition='inside',textfont=dict(color='white',size=11)))
            fig = ctheme(fig, f"{sel_plan} — Monthly Active vs Cancelled")
            fig.update_layout(barmode='stack')
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=pl_df['Month'],y=pl_df['Active%'],mode='lines+markers',
                                      name='Active %',line=dict(color='#00c896',width=3),
                                      marker=dict(size=12,color='#00c896',line=dict(color='white',width=2)),
                                      fill='tozeroy',fillcolor='rgba(0,200,150,0.1)'))
            fig2 = ctheme(fig2, "Active Rate Trend")
            fig2.update_layout(yaxis=dict(ticksuffix='%',range=[0,100]))
            st.plotly_chart(fig2, use_container_width=True)

    with t2:
        can = pdf[pdf['cancelled']]
        has_par = can['Parent Order Id'].notna() & (can['Parent Order Id'].astype(str).str.strip().isin(['','nan'])==False)
        after1 = int((~has_par).sum()); after2 = int(has_par.sum())
        still_active = int(pdf['active'].sum())
        fig_f = go.Figure(go.Funnel(
            y=['Subscribed','Cancelled After 1st','Cancelled After 2nd+','Still Active'],
            x=[len(pdf), after1, after2, still_active],
            marker_color=['#1057c8','#ff4d6d','#ffb300','#00c896'],
            textinfo='value+percent initial',
            textfont=dict(size=13,family='Outfit'),
        ))
        fig_f.update_layout(paper_bgcolor='white',plot_bgcolor='white',height=360,
                            title=dict(text="Cancellation Funnel",font=dict(family='Outfit',size=14,color='#03112b')),
                            margin=dict(l=12,r=12,t=44,b=12))
        st.plotly_chart(fig_f, use_container_width=True)

    with t3:
        pm_rows = []
        for pm in ['cc', 'dc', 'upi', 'si_cc', 'si_upi', 'si_undefined']:
            pmd = pdf[pdf['pm'] == pm]
            if len(pmd) == 0: continue
            
            pm_rows.append({
                'Payment': pm.upper(),
                'Total': len(pmd),
                'Active': int(pmd['active'].sum()),
                'Cancelled': int(pmd['cancelled'].sum()),
                'Active%': f"{pmd['active'].sum()/len(pmd)*100:.1f}%"
            })
        pm_df = pd.DataFrame(pm_rows)
        c1,c2 = st.columns(2)
        with c1:
            fig = px.bar(pm_df,x='Payment',y=['Active','Cancelled'],barmode='stack',
                         color_discrete_map={'Active':'#00c896','Cancelled':'#ff4d6d'})
            fig = ctheme(fig,"Active vs Cancelled by Payment Method",h=320)
            st.plotly_chart(fig,use_container_width=True)
        with c2:
            show_table(pm_df)

# ══════════════════════════════════════════════════════════════
# PAYMENT METHODS PAGE
# ══════════════════════════════════════════════════════════════

elif "Payment" in page:
    st.markdown("""<div class='page-header'>
      <h1>💳 Payment Method Analysis</h1>
      <p>CC vs DC vs UPI vs SI — trends, active rates, plan mix</p>
    </div>""", unsafe_allow_html=True)

    f1, f2 = st.columns(2)
    with f1:
        sel_pay = st.multiselect("Payment Methods", ['All', 'CC', 'DC', 'UPI', 'SI_CC', 'SI_UPI', 'SI_UNDEFINED', 'NULL'],
                                 default=[], key='pm_pay_sel')
    with f2:
        sel_mo_pm = st.multiselect("Month", ['All'] + list(MONTH_LABELS.values()), default=[], key='pm_mo')

    if 'All' in sel_pay and len(sel_pay) > 1: sel_pay = ['All']
    if 'All' in sel_mo_pm and len(sel_mo_pm) > 1: sel_mo_pm = ['All']

    if 'All' in sel_mo_pm:
        yms_pm = MONTH_ORDER
    else:
        rev_map = {v:k for k,v in MONTH_LABELS.items()}
        yms_pm = [rev_map[m] for m in sel_mo_pm if m in rev_map]

    if 'All' in sel_pay:
        fdf_pm = df[df['ym'].isin(yms_pm)]
    else:
        pay_lower = [p.lower() for p in sel_pay]
        fdf_pm = df[(df['pm'].isin(pay_lower)) & (df['ym'].isin(yms_pm))]

    if len(sel_pay) == 0 or len(sel_mo_pm) == 0:
        st.warning("Please select at least one Payment Method and one Month.")
        st.stop()

    k1,k2,k3,k4,k5 = st.columns(5)

    for i,(pm,col,cls) in enumerate([
        ('cc','#1057c8',''),
        ('dc','#00b4d8','cyan'),
        ('upi','#7c3aed',''),
        ('si_cc','#ffb300','amber'),
        ('si_upi','#10b981','green')
    ]):
        
        pmd = fdf_pm[fdf_pm['pm']==pm]
        
        [k1,k2,k3,k4,k5][i].markdown(
            kpi(pm.upper(), f"{len(pmd):,}", f"Active: {pmd['active'].sum()}/{len(pmd)}", cls),
            unsafe_allow_html=True
        )

    c1,c2 = st.columns(2)
    with c1:
        mp = fdf_pm.groupby(['ym','pm']).size().reset_index(name='n')
        mp['Month'] = mp['ym'].map(MONTH_SHORT)
        mp['PM'] = mp['pm'].str.upper()
        fig = px.line(mp,x='Month',y='n',color='PM',markers=True,
                      color_discrete_map={'CC':'#1057c8','DC':'#00b4d8','UPI':'#7c3aed','SI_CC':'#ffb300'},
                      labels={'n':'Orders'})
        fig = ctheme(fig,"Payment Method Trend")
        fig.update_traces(line_width=2.5,marker_size=10)
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        pm_tot = fdf_pm.groupby('pm').size().reset_index(name='n')
        pm_tot['PM'] = pm_tot['pm'].str.upper()
        fig2 = go.Figure(go.Pie(labels=pm_tot['PM'],values=pm_tot['n'],hole=0.55,
                                marker_colors=['#1057c8','#00b4d8','#7c3aed','#ffb300'],
                                textfont_size=13))
        fig2.update_layout(paper_bgcolor='white',height=380,
                           title=dict(text="Payment Share",font=dict(family='Outfit',size=14,color='#03112b')),
                           margin=dict(l=12,r=12,t=44,b=12),
                           legend=dict(font=dict(size=12),bgcolor='rgba(0,0,0,0)'))
        st.plotly_chart(fig2,use_container_width=True)

# ══════════════════════════════════════════════════════════════
# PREDICTIONS PAGE
# ══════════════════════════════════════════════════════════════

elif "Prediction" in page:
    st.markdown("""<div class='page-header'>
      <h1>🔮 Prediction Dashboard</h1>
      <p>Adjust sliders — predictions update live instantly</p>
    </div>""", unsafe_allow_html=True)

    with st.expander("⚙️ Adjust Assumptions (sliders update prediction instantly)", expanded=True):
        sc1,sc2,sc3 = st.columns(3)
        with sc1:
            plat_rr = st.slider("PLATINUM Renewal Rate %",20,55,35,1)
            star_rr = st.slider("STARTER Renewal Rate %",25,65,45,1)
        with sc2:
            drr_feb = st.slider("Feb Organic DRR",15.0,30.0,22.2,0.1)
            drr_mar = st.slider("Mar Organic DRR",15.0,30.0,21.0,0.1)
            drr_apr = st.slider("Apr Organic DRR",15.0,30.0,20.0,0.1)
        with sc3:
            push_feb = st.slider("Feb End Push",50,500,150,10)
            push_mar = st.slider("Mar End Push",50,500,200,10)
            push_apr = st.slider("Apr End Push",50,500,180,10)

    pools = {'Feb':{'PLAT':619,'STAR':316},'Mar':{'PLAT':1801,'STAR':225},'Apr':{'PLAT':2467,'STAR':387}}
    params = {'Feb':{'drr':drr_feb,'days':28,'push':push_feb},
              'Mar':{'drr':drr_mar,'days':31,'push':push_mar},
              'Apr':{'drr':drr_apr,'days':30,'push':push_apr}}

    def predict(m):
        p=params[m]; pool=pools[m]
        new=int(p['drr']*p['days'])+p['push']
        pr=int(pool['PLAT']*plat_rr/100); sr=int(pool['STAR']*star_rr/100)
        renew=pr+sr; total=new+renew
        active=int(new*0.72)+int(renew*0.88); cancel=total-active
        return {'new':new,'renew':renew,'total':total,'active':active,'cancel':cancel,
                'drr':round(total/p['days'],1),'act%':round(active/total*100,1),
                'plat_r':pr,'star_r':sr,'plat_nr':pool['PLAT']-pr,'star_nr':pool['STAR']-sr}

    R={m:predict(m) for m in ['Feb','Mar','Apr']}

    for m,icon in [('Feb','📅'),('Mar','🔥'),('Apr','🏆')]:
        r=R[m]
        st.markdown(f"<div class='sec-title'>{icon} {m} 2026 Prediction</div>",unsafe_allow_html=True)
        k1,k2,k3,k4,k5,k6=st.columns(6)
        k1.markdown(kpi("TOTAL SUBS",f"{r['total']:,}",f"DRR: {r['drr']}/day"),unsafe_allow_html=True)
        k2.markdown(kpi("New Subs",f"{r['new']:,}","organic+push"),unsafe_allow_html=True)
        k3.markdown(kpi("Renewals",f"{r['renew']:,}","from pool","amber"),unsafe_allow_html=True)
        k4.markdown(kpi("Active",f"{r['active']:,}",f"{r['act%']}%","green"),unsafe_allow_html=True)
        k5.markdown(kpi("Cancelled",f"{r['cancel']:,}",f"{100-r['act%']}%","red"),unsafe_allow_html=True)
        k6.markdown(kpi("Not Renewing",f"{r['plat_nr']+r['star_nr']:,}","churn from pool"),unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)

    months_l=['Feb 2026','Mar 2026','Apr 2026']
    c1,c2=st.columns(2)
    with c1:
        fig=go.Figure()
        fig.add_trace(go.Bar(name='New Subs',x=months_l,y=[R[m]['new'] for m in ['Feb','Mar','Apr']],
                             marker_color='#1057c8',opacity=0.88,text=[R[m]['new'] for m in ['Feb','Mar','Apr']],textposition='inside',textfont=dict(color='white',size=12)))
        fig.add_trace(go.Bar(name='Renewals',x=months_l,y=[R[m]['renew'] for m in ['Feb','Mar','Apr']],
                             marker_color='#ffb300',opacity=0.88,text=[R[m]['renew'] for m in ['Feb','Mar','Apr']],textposition='inside',textfont=dict(color='white',size=12)))
        fig=ctheme(fig,"New vs Renewals Prediction",h=360)
        fig.update_layout(barmode='stack')
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        fig2=go.Figure()
        fig2.add_trace(go.Scatter(x=months_l,y=[R[m]['total'] for m in ['Feb','Mar','Apr']],
                                  mode='lines+markers',name='Total',
                                  line=dict(color='#1057c8',width=3),
                                  marker=dict(size=12,color='#1057c8',line=dict(color='white',width=2)),
                                  fill='tozeroy',fillcolor='rgba(16,87,200,0.08)'))
        fig2.add_trace(go.Scatter(x=months_l,y=[R[m]['active'] for m in ['Feb','Mar','Apr']],
                                  mode='lines+markers',name='Active',
                                  line=dict(color='#00c896',width=3),
                                  marker=dict(size=12,color='#00c896',line=dict(color='white',width=2))))
        fig2=ctheme(fig2,"Total & Active Prediction Trend",h=360)
        st.plotly_chart(fig2,use_container_width=True)

    st.markdown("<div class='sec-title'>Full Prediction Table</div>",unsafe_allow_html=True)
    pred_rows=[]
    for m in ['Feb','Mar','Apr']:
        r=R[m]; p=params[m]
        pred_rows.append({'Month':f"{m} 2026",'Organic DRR':p['drr'],'Base (DRR×Days)':int(p['drr']*p['days']),
                          'End Push':p['push'],'Total New':r['new'],
                          'PLAT Pool':pools[m]['PLAT'],'PLAT Renew':r['plat_r'],
                          'STAR Pool':pools[m]['STAR'],'STAR Renew':r['star_r'],
                          'Total Renew':r['renew'],'TOTAL':r['total'],
                          'Active':r['active'],'Cancelled':r['cancel'],'Active%':f"{r['act%']}%",'DRR':r['drr']})
    show_table(pd.DataFrame(pred_rows))
    st.warning("⚠️ **Promo Note:** If campaign runs → add 1,000–3,000 orders. Historical: Christmas=3,030 | New Year=2,964 in 2 days.")

# ══════════════════════════════════════════════════════════════
# DATA EXPLORER PAGE
# ══════════════════════════════════════════════════════════════

elif "Explorer" in page:
    st.markdown("""<div class='page-header'>
      <h1>🔍 Data Explorer</h1>
      <p>Custom filters, quick queries, download data</p>
    </div>""", unsafe_allow_html=True)

    t1,t2,t3=st.tabs(["🎛️ Filter Builder","📊 Quick Queries","⬇️ Download"])

    with t1:
        st.markdown("""<style>
        input[type="text"], textarea {
            background: white !important;
            color: #03112b !important;
        }
        [data-testid="stTextInput"] input {
            background: white !important;
            color: #03112b !important;
            border: 1.5px solid #dce6fb !important;
        }
        [data-testid="stDataFrame"] iframe {
            background: white !important;
        }
        .stDataFrame, [data-testid="stDataFrame"],
        [data-testid="stDataFrame"] * {
            color: #03112b !important;
            background: white !important;
        }
        </style>""", unsafe_allow_html=True)
        f1,f2,f3,f4=st.columns(4)
        with f1: sel_m_ex=st.multiselect("Month",list(MONTH_LABELS.values()),default=list(MONTH_LABELS.values()),key='ex_m')
        with f2: sel_p_ex=st.multiselect("Plan",PLANS,default=PLANS,key='ex_p')
        with f3: sel_pm_ex=st.multiselect("Payment",['CC','DC','UPI','SI_CC','SI_UPI','SI_UNDEFINED','NULL'],default=['CC','DC','UPI','SI_CC','SI_UPI','SI_UNDEFINED','NULL'],key='ex_pm')
        with f4:
            st_opts=['All','Active Only','Cancelled Only']
            sel_st=st.selectbox("Status",st_opts,key='ex_st')
        coupon_in=st.text_input("Coupon Code (optional, partial match)",key='ex_cpn')

        rev_map={v:k for k,v in MONTH_LABELS.items()}
        yms_ex=[rev_map[m] for m in sel_m_ex if m in rev_map]
        pm_lower = [p.lower() for p in sel_pm_ex]
        fdf_ex=df[(df['ym'].isin(yms_ex))&(df['Subscription Name'].isin(sel_p_ex))&(df['pm'].isin(pm_lower))]
        if sel_st=='Active Only': fdf_ex=fdf_ex[fdf_ex['active']]
        elif sel_st=='Cancelled Only': fdf_ex=fdf_ex[fdf_ex['cancelled']]
        if coupon_in: fdf_ex=fdf_ex[fdf_ex['Coupon code'].astype(str).str.upper().str.contains(coupon_in.upper(),na=False)]
        
        s1,s2,s3,s4=st.columns(4)
        s1.metric("Records Found",f"{len(fdf_ex):,}")
        s2.metric("Active",f"{fdf_ex['active'].sum():,}")
        s3.metric("Cancelled",f"{fdf_ex['cancelled'].sum():,}")
        s4.metric("Revenue",f"₹{int(fdf_ex['Grand Total Amount'].sum()):,}")

        show=['Order Id','User Id','Created At','Subscription Name','Payment Method','Mandate status',
            'Grand Total Amount','Coupon code','Start Date','End Date']
        show_table(fdf_ex[show])
        
    with t2:
        q=st.selectbox("Select Query",[
            "Total sales by month","Active users by plan",
            "Cancel rate by payment method","Top 10 coupons",
            "Daily orders trend","Revenue by month","SI growth"])
        if q=="Total sales by month":
            r=df.groupby('ym').size().reset_index(name='Total')
            r['Month']=r['ym'].map(MONTH_LABELS)
            fig=px.bar(r,x='Month',y='Total',color='Total',color_continuous_scale='Blues',text='Total')
            fig=ctheme(fig,"Total Sales by Month"); st.plotly_chart(fig,use_container_width=True)
        elif q=="Active users by plan":
            r=df.groupby('Subscription Name')['active'].agg(['sum','count']).reset_index()
            r.columns=['Plan','Active','Total']; r['Active%']=(r['Active']/r['Total']*100).round(1)
            fig=px.bar(r,x='Plan',y='Active',color='Plan',color_discrete_map=PLAN_COLORS,text='Active')
            fig=ctheme(fig,"Active Users by Plan"); st.plotly_chart(fig,use_container_width=True)
        elif q=="Cancel rate by payment method":
            r=df.groupby('pm').agg(Total=('Order Id','count'),Cancelled=('cancelled','sum')).reset_index()
            r['Cancel%']=(r['Cancelled']/r['Total']*100).round(1); r['PM']=r['pm'].str.upper()
            fig=px.bar(r,x='PM',y='Cancel%',color='Cancel%',color_continuous_scale='Reds',text='Cancel%',labels={'PM':'Payment'})
            fig=ctheme(fig,"Cancel Rate by Payment"); st.plotly_chart(fig,use_container_width=True)
        elif q=="Top 10 coupons":
            r=df[df['Coupon code'].notna()].groupby('Coupon code').size().reset_index(name='Uses').sort_values('Uses',ascending=False).head(10)
            fig=px.bar(r,x='Coupon code',y='Uses',color='Uses',color_continuous_scale='Blues',text='Uses')
            fig=ctheme(fig,"Top 10 Coupons"); st.plotly_chart(fig,use_container_width=True)
        elif q=="Daily orders trend":
            r=df.groupby('date').size().reset_index(name='n'); r['date']=pd.to_datetime(r['date'])
            fig=px.line(r,x='date',y='n',labels={'date':'Date','n':'Orders'})
            fig=ctheme(fig,"Daily Orders"); st.plotly_chart(fig,use_container_width=True)
        elif q=="Revenue by month":
            r=df.groupby('ym')['Grand Total Amount'].sum().reset_index(); r['Month']=r['ym'].map(MONTH_LABELS)
            fig=px.bar(r,x='Month',y='Grand Total Amount',color='Grand Total Amount',color_continuous_scale='Blues',text='Grand Total Amount')
            fig=ctheme(fig,"Revenue by Month"); st.plotly_chart(fig,use_container_width=True)
        elif q=="SI growth":
            r=df[df['is_si']].groupby('ym').size().reset_index(name='SI'); r['Month']=r['ym'].map(MONTH_LABELS)
            fig=px.bar(r,x='Month',y='SI',color='SI',color_continuous_scale='Oranges',text='SI')
            fig=ctheme(fig,"SI Renewals Growth"); st.plotly_chart(fig,use_container_width=True)

    with t3:
        dl_m=st.multiselect("Month",list(MONTH_LABELS.values()),default=list(MONTH_LABELS.values()),key='dl_m')
        dl_p=st.multiselect("Plan",PLANS,default=PLANS,key='dl_p')
        rev_map2={v:k for k,v in MONTH_LABELS.items()}
        dl_yms=[rev_map2[m] for m in dl_m if m in rev_map2]
        dl_df=df[(df['ym'].isin(dl_yms))&(df['Subscription Name'].isin(dl_p))]
        st.info(f"**{len(dl_df):,} records** ready to download")
        st.download_button("⬇️ Download CSV",dl_df.to_csv(index=False).encode('utf-8'),"subscriptions_filtered.csv","text/csv")
                
