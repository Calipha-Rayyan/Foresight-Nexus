APP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', -apple-system, sans-serif; }

:root {
  --bg: #0B0E14;
  --surface: #131722;
  --surface2: #171C29;
  --border: #232838;
  --text: #E6E8EF;
  --muted: #8A90A6;
  --accent: #4FD1E8;
  --accent2: #7C6CF0;
  --healthy: #2ecc71;
  --watch: #f1c40f;
  --risk: #e67e22;
  --critical: #e74c3c;
}

.stApp { background: var(--bg); }
section[data-testid="stSidebar"] { background: var(--surface); border-right: 1px solid var(--border); }

.fn-hero {
  padding: 2.2rem 2rem; border-radius: 16px;
  background: linear-gradient(135deg, #131722 0%, #171C2C 60%, #14202B 100%);
  border: 1px solid var(--border);
  margin-bottom: 1.2rem;
}
.fn-hero h1 { font-size: 2.1rem; font-weight: 800; margin: 0; letter-spacing: -0.02em;
  background: linear-gradient(90deg, #E6E8EF, var(--accent));
  -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }
.fn-hero p.tagline { color: var(--accent); font-weight: 500; margin: 0.3rem 0 0.8rem 0; font-size: 1.05rem; }
.fn-hero p.sub { color: var(--muted); max-width: 640px; margin: 0; font-size: 0.92rem; }

.fn-status { display:flex; gap:1.5rem; margin-top:1rem; font-size:0.82rem; color: var(--muted); }
.fn-status .dot { color: var(--healthy); }

.fn-card {
  background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
  padding: 1rem 1.1rem; transition: border-color 180ms ease, transform 180ms ease;
  animation: fnFadeIn 400ms ease both;
}
.fn-card:hover { border-color: var(--accent); transform: translateY(-2px); }
.fn-kpi-label { color: var(--muted); font-size: 0.74rem; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600; }
.fn-kpi-value { font-size: 1.7rem; font-weight: 800; color: var(--text); margin: 0.25rem 0; }
.fn-kpi-delta-up { color: var(--healthy); font-size: 0.82rem; font-weight: 600; }
.fn-kpi-delta-down { color: var(--critical); font-size: 0.82rem; font-weight: 600; }
.fn-kpi-context { color: var(--muted); font-size: 0.76rem; }

.fn-pill { display:inline-flex; align-items:center; gap:0.35rem; padding: 0.2rem 0.6rem; border-radius: 999px;
  font-size: 0.74rem; font-weight: 700; border: 1px solid transparent; }
.fn-pill-healthy { background: rgba(46,204,113,0.12); color: var(--healthy); border-color: rgba(46,204,113,0.3); }
.fn-pill-watch { background: rgba(241,196,15,0.12); color: var(--watch); border-color: rgba(241,196,15,0.3); }
.fn-pill-risk { background: rgba(230,126,34,0.12); color: var(--risk); border-color: rgba(230,126,34,0.3); }
.fn-pill-critical { background: rgba(231,76,60,0.12); color: var(--critical); border-color: rgba(231,76,60,0.3); }

.fn-alert { border-left: 3px solid var(--critical); background: var(--surface); border-radius: 8px;
  padding: 0.8rem 1rem; margin-bottom: 0.6rem; animation: fnSlideIn 300ms ease both; }
.fn-alert.medium { border-left-color: var(--watch); }
.fn-alert.high { border-left-color: var(--risk); }
.fn-alert.low { border-left-color: var(--muted); }
.fn-alert-title { font-weight: 700; font-size: 0.88rem; }
.fn-alert-body { color: var(--muted); font-size: 0.82rem; margin-top: 0.15rem; }
.fn-alert-action { color: var(--accent); font-size: 0.82rem; margin-top: 0.35rem; font-weight: 600; }

.fn-empty { text-align:center; padding: 3rem 1rem; color: var(--muted); border: 1px dashed var(--border);
  border-radius: 12px; }
.fn-empty h3 { color: var(--text); margin-bottom: 0.4rem; }

.fn-section-title { font-size: 1.15rem; font-weight: 700; margin: 1.4rem 0 0.6rem 0; color: var(--text); }
.fn-section-sub { color: var(--muted); font-size: 0.85rem; margin-top: -0.4rem; margin-bottom: 0.8rem; }

@keyframes fnFadeIn { from { opacity: 0; transform: translateY(6px);} to { opacity: 1; transform: translateY(0);} }
@keyframes fnSlideIn { from { opacity: 0; transform: translateX(-6px);} to { opacity: 1; transform: translateX(0);} }

div[data-testid="stMetric"] { background: var(--surface); border:1px solid var(--border); border-radius: 12px; padding: 0.8rem 1rem; }

/* --- Phase 6: soften default Streamlit chrome to match the brand system --- */
.stButton > button, .stDownloadButton > button {
  background: var(--surface2); color: var(--text); border: 1px solid var(--border);
  border-radius: 8px; font-weight: 600; transition: border-color 150ms ease, transform 150ms ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
  border-color: var(--accent); color: var(--accent); transform: translateY(-1px);
}
.stButton > button[kind="primary"] {
  background: linear-gradient(90deg, var(--accent), var(--accent2)); color: #0B0E14; border: none;
}
.stButton > button[kind="primary"]:hover { filter: brightness(1.08); transform: translateY(-1px); }

div[data-baseweb="select"] > div, .stTextInput > div > div, .stNumberInput > div > div {
  background: var(--surface); border-color: var(--border) !important; border-radius: 8px;
}

.stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid var(--border); }
.stTabs [data-baseweb="tab"] { color: var(--muted); font-weight: 600; padding: 0.5rem 1rem; }
.stTabs [aria-selected="true"] { color: var(--accent) !important; border-bottom-color: var(--accent) !important; }

.streamlit-expanderHeader, div[data-testid="stExpander"] {
  background: var(--surface); border: 1px solid var(--border); border-radius: 10px;
}

section[data-testid="stFileUploaderDropzone"] {
  background: var(--surface); border: 1px dashed var(--border); border-radius: 10px;
}

div[data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }

div[data-testid="stContainer"][style*="border"] { border-color: var(--border) !important; border-radius: 12px !important; }

div[data-testid="stSlider"] > div > div > div[role="slider"] { background: var(--accent); }

/* subtle page entrance */
section.main > div.block-container { animation: fnFadeIn 320ms ease both; }

/* --- Responsive: tablet (<=1024px) --- */
@media (max-width: 1024px) {
  .fn-hero { padding: 1.6rem 1.4rem; }
  .fn-hero h1 { font-size: 1.7rem; }
  .fn-status { flex-wrap: wrap; gap: 0.6rem 1.2rem; }
  .fn-kpi-value { font-size: 1.4rem; }
}

/* --- Responsive: mobile (<=640px) — Streamlit already stacks st.columns
   into single-column at narrow widths; these rules tighten spacing/type
   so the stacked layout doesn't feel like an untouched desktop dump --- */
@media (max-width: 640px) {
  .block-container { padding-left: 0.8rem !important; padding-right: 0.8rem !important; }
  .fn-hero { padding: 1.2rem 1rem; margin-bottom: 0.8rem; }
  .fn-hero h1 { font-size: 1.4rem; }
  .fn-hero p.tagline { font-size: 0.92rem; }
  .fn-hero p.sub { font-size: 0.82rem; }
  .fn-status { flex-direction: column; gap: 0.3rem; font-size: 0.74rem; }
  .fn-card { padding: 0.8rem 0.9rem; }
  .fn-kpi-value { font-size: 1.3rem; }
  .fn-section-title { font-size: 1.02rem; margin-top: 1rem; }
  /* Long product names must wrap, never force horizontal scroll */
  .fn-alert-title, .fn-kpi-label { overflow-wrap: anywhere; }
  /* Plotly charts: let the container scale width, cap height so a tall
     desktop chart doesn't dominate a phone screen */
  div[data-testid="stPlotlyChart"] { max-height: 340px; }
}

/* Never allow horizontal scrolling of the page itself; wide tables get
   their own scroll container instead (Streamlit's default stDataFrame
   behavior — reinforced here rather than overridden). */
.stApp { overflow-x: hidden; }
div[data-testid="stDataFrame"] { max-width: 100%; overflow-x: auto; }
</style>
"""
