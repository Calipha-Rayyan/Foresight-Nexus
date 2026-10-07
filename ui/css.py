"""FORESIGHT Nexus — Unified Design System & SaaS Stylesheet.

Obsidian / Near-Black Palette:
- Background: #080B11
- Primary Surface: #111622
- Elevated Surface: #161D2B
- Border: #1F293D
- Text Primary: #F1F5F9
- Text Muted: #8B9BB4
- Accent Cyan: #28B8FF
- Accent Violet: #8A63FF
- Status: Healthy #10B981, Watch #F59E0B, At Risk #F97316, Critical #EF4444
"""

APP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
  --fn-bg: #080B11;
  --fn-surface: #111622;
  --fn-surface-elevated: #161D2B;
  --fn-border: #1F293D;
  --fn-border-subtle: #182233;
  
  --fn-text: #F1F5F9;
  --fn-text-muted: #8B9BB4;
  --fn-text-dim: #64748B;
  
  --fn-accent-cyan: #28B8FF;
  --fn-accent-blue: #1E5EFF;
  --fn-accent-violet: #8A63FF;
  
  --fn-healthy: #10B981;
  --fn-watch: #F59E0B;
  --fn-risk: #F97316;
  --fn-critical: #EF4444;
}

/* Global resets & typography */
html, body, [class*="css"] {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif;
  color: var(--fn-text);
  -webkit-font-smoothing: antialiased;
}

.stApp {
  background-color: var(--fn-bg) !important;
  overflow-x: hidden !important;
}

/* Main Container spacing */
.block-container {
  padding-top: 1.5rem !important;
  padding-bottom: 3rem !important;
  max-width: 1360px !important;
  animation: fnPageFadeIn 280ms ease-out both;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
  background-color: #0B101B !important;
  border-right: 1px solid var(--fn-border) !important;
}

section[data-testid="stSidebar"] .block-container {
  padding-top: 0.8rem !important;
  padding-left: 0.85rem !important;
  padding-right: 0.85rem !important;
}

/* Streamlit Native st.logo Positioning & Sizing */
[data-testid="stLogo"] {
  padding: 0.5rem 0.25rem 0.25rem 0.25rem !important;
  margin-bottom: 0.25rem !important;
  height: auto !important;
}

[data-testid="stLogo"] img {
  max-height: 44px !important;
  width: auto !important;
  object-fit: contain !important;
}

/* Sidebar Navigation Items Elevation */
section[data-testid="stSidebar"] ul[data-testid="stSidebarNavItems"] li a {
  border-radius: 8px !important;
  margin: 2px 0 !important;
  padding: 0.45rem 0.75rem !important;
  transition: all 160ms ease !important;
}

section[data-testid="stSidebar"] ul[data-testid="stSidebarNavItems"] li a:hover {
  background: rgba(40, 184, 255, 0.08) !important;
  color: var(--fn-accent-cyan) !important;
}

section[data-testid="stSidebar"] ul[data-testid="stSidebarNavItems"] li a[aria-current="page"] {
  background: linear-gradient(90deg, rgba(30, 94, 255, 0.18) 0%, rgba(40, 184, 255, 0.06) 100%) !important;
  border-left: 3px solid var(--fn-accent-cyan) !important;
  font-weight: 700 !important;
}

/* Sidebar Brand Lockup (Fallback) */
.fn-brand-sidebar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.25rem 0 0.75rem 0;
  border-bottom: 1px solid var(--fn-border-subtle);
  margin-bottom: 0.75rem;
}

.fn-brand-sidebar-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  flex-shrink: 0;
}

.fn-brand-sidebar-name {
  font-size: 1rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  line-height: 1.2;
}

.fn-brand-white {
  color: #FFFFFF;
}

.fn-brand-accent {
  background: linear-gradient(135deg, var(--fn-accent-cyan), var(--fn-accent-violet));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.fn-brand-sidebar-tagline {
  font-size: 0.72rem;
  color: var(--fn-text-muted);
  font-weight: 400;
}

/* Sidebar Telemetry Widget */
.fn-sidebar-telemetry {
  background: var(--fn-surface);
  border: 1px solid var(--fn-border-subtle);
  border-radius: 8px;
  padding: 0.65rem 0.8rem;
  margin-top: 1rem;
  font-size: 0.76rem;
}

.fn-telemetry-header {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-weight: 700;
  color: var(--fn-text);
  margin-bottom: 0.4rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: 0.7rem;
}

.fn-telemetry-meta {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  color: var(--fn-text-muted);
}

.fn-telemetry-meta b {
  color: var(--fn-text);
}

.fn-sidebar-footer {
  margin-top: 1.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--fn-border-subtle);
  font-size: 0.7rem;
  color: var(--fn-text-dim);
}

.fn-footer-brand {
  font-weight: 600;
  color: var(--fn-text-muted);
}

/* Page Header Hierarchy */
.fn-page-header {
  margin-bottom: 1.5rem;
}

.fn-page-header-top {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.fn-page-header-title {
  font-size: 1.75rem !important;
  font-weight: 800 !important;
  letter-spacing: -0.02em !important;
  color: var(--fn-text) !important;
  margin: 0 !important;
}

.fn-page-header-sub {
  font-size: 0.92rem;
  color: var(--fn-text-muted);
  margin-top: 0.35rem;
  margin-bottom: 0;
  max-width: 960px;
  line-height: 1.45;
  text-wrap: balance;
  text-wrap: pretty;
}

.fn-page-header-meta {
  display: flex;
  gap: 1.25rem;
  margin-top: 0.6rem;
  font-size: 0.78rem;
  color: var(--fn-text-dim);
}

.fn-meta-item {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
}

/* Section Header */
.fn-section-wrap {
  margin-top: 1.8rem;
  margin-bottom: 0.85rem;
}

.fn-section-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--fn-text);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.fn-section-sub {
  font-size: 0.82rem;
  color: var(--fn-text-muted);
  margin: 0.2rem 0 0 0;
  max-width: 960px;
  line-height: 1.4;
  text-wrap: balance;
  text-wrap: pretty;
}

/* Hero Section (Command Center) */
.fn-hero {
  background: linear-gradient(135deg, #111622 0%, #151D2D 60%, #101624 100%);
  border: 1px solid var(--fn-border);
  border-radius: 14px;
  padding: 1.5rem 1.75rem;
  margin-bottom: 1.25rem;
  position: relative;
  overflow: hidden;
}

.fn-hero::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 320px;
  height: 100%;
  background: radial-gradient(circle at 100% 0%, rgba(40, 184, 255, 0.08) 0%, transparent 70%);
  pointer-events: none;
}

.fn-hero-brand-line {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  font-size: 1.5rem;
  font-weight: 800;
  letter-spacing: -0.01em;
}

.fn-hero-brand-mark {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  flex-shrink: 0;
  vertical-align: middle;
}

.fn-hero-title-main { color: #FFFFFF; }
.fn-hero-title-accent {
  background: linear-gradient(135deg, var(--fn-accent-cyan), var(--fn-accent-violet));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.fn-hero-pill {
  margin-left: 0.5rem;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 600;
  background: rgba(16, 185, 129, 0.12);
  color: var(--fn-healthy);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.fn-hero-tagline {
  font-size: 0.95rem;
  color: var(--fn-accent-cyan);
  font-weight: 600;
  margin: 0.25rem 0 0.5rem 0;
}

.fn-hero-desc {
  font-size: 0.88rem;
  color: var(--fn-text-muted);
  max-width: 1080px;
  margin: 0;
  line-height: 1.5;
  text-wrap: balance;
  text-wrap: pretty;
}

.fn-hero-meta {
  display: flex;
  gap: 1.5rem;
  margin-top: 1rem;
  padding-top: 0.8rem;
  border-top: 1px solid var(--fn-border-subtle);
  font-size: 0.78rem;
  color: var(--fn-text-dim);
}

.fn-hero-meta b { color: var(--fn-text); }

/* SVG Data Nexus Container (High-Fi Ambient Container) */
.fn-nexus-container {
  width: 100%;
  display: flex;
  justify-content: center;
  margin: 0.25rem 0 1.25rem 0;
  background: radial-gradient(ellipse at 50% 50%, rgba(30, 94, 255, 0.08) 0%, rgba(8, 11, 17, 0) 70%);
  border-radius: 12px;
  border: 1px solid rgba(31, 41, 61, 0.6);
  padding: 0.6rem 0.4rem;
  overflow: hidden;
}

.fn-nexus-svg {
  width: 100%;
  max-width: 880px;
  height: auto;
}

/* Modebar Suppression */
.modebar-container, .js-plotly-plot .plotly .modebar {
  display: none !important;
}

/* Card Geometry */
.fn-card {
  background: var(--fn-surface);
  border: 1px solid var(--fn-border);
  border-radius: 12px;
  padding: 1.1rem 1.25rem;
  transition: border-color 180ms ease, transform 180ms ease;
  height: 100%;
}

.fn-card:hover {
  border-color: var(--fn-accent-cyan);
  transform: translateY(-1px);
}

/* KPI Cards */
.fn-kpi-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.fn-kpi-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.5rem;
  margin-bottom: 0.35rem;
  flex-wrap: wrap;
}

.fn-kpi-label {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--fn-text-muted);
  line-height: 1.3;
  flex: 1 1 auto;
  min-width: 0;
}

.fn-kpi-status {
  flex-shrink: 0;
  display: inline-flex;
}

.fn-kpi-value {
  font-size: 1.85rem;
  font-weight: 800;
  color: var(--fn-text);
  letter-spacing: -0.02em;
  line-height: 1.15;
  margin: 0.15rem 0 0.4rem 0;
}

.fn-kpi-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  font-size: 0.76rem;
}

.fn-kpi-delta-up {
  color: var(--fn-healthy);
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 0.2rem;
}

.fn-kpi-delta-down {
  color: var(--fn-critical);
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 0.2rem;
}

.fn-kpi-context {
  color: var(--fn-text-dim);
}

/* Status Pills */
.fn-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  font-size: 0.68rem;
  font-weight: 700;
  line-height: 1.25;
  white-space: nowrap;
  border: 1px solid transparent;
}

.fn-pill-dot { font-size: 0.65rem; }

.fn-pill-healthy {
  background: rgba(16, 185, 129, 0.12);
  color: var(--fn-healthy);
  border-color: rgba(16, 185, 129, 0.28);
}

.fn-pill-watch {
  background: rgba(245, 158, 11, 0.12);
  color: var(--fn-watch);
  border-color: rgba(245, 158, 11, 0.28);
}

.fn-pill-risk {
  background: rgba(249, 115, 22, 0.12);
  color: var(--fn-risk);
  border-color: rgba(249, 115, 22, 0.28);
}

.fn-pill-critical {
  background: rgba(239, 68, 68, 0.14);
  color: var(--fn-critical);
  border-color: rgba(239, 68, 68, 0.32);
}

.fn-pill-muted {
  background: rgba(139, 155, 180, 0.12);
  color: var(--fn-text-muted);
  border-color: var(--fn-border);
}

.fn-dot-healthy { color: var(--fn-healthy); }
.fn-dot-watch { color: var(--fn-watch); }
.fn-dot-risk { color: var(--fn-risk); }
.fn-dot-critical { color: var(--fn-critical); }

/* Alert Cards */
.fn-alert {
  background: var(--fn-surface);
  border-radius: 10px;
  border: 1px solid var(--fn-border);
  border-left-width: 4px;
  padding: 0.9rem 1.1rem;
  margin-bottom: 0.75rem;
  animation: fnSlideIn 240ms ease both;
}

.fn-alert-critical { border-left-color: var(--fn-critical); }
.fn-alert-high, .fn-alert-at_risk { border-left-color: var(--fn-risk); }
.fn-alert-medium, .fn-alert-watch { border-left-color: var(--fn-watch); }
.fn-alert-low, .fn-alert-healthy { border-left-color: var(--fn-healthy); }

.fn-alert-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.4rem;
}

.fn-alert-header {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.fn-alert-title {
  font-size: 0.92rem;
  font-weight: 700;
  color: var(--fn-text);
}

.fn-alert-category {
  font-size: 0.72rem;
  color: var(--fn-text-dim);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.fn-alert-body {
  font-size: 0.82rem;
  color: var(--fn-text-muted);
  line-height: 1.4;
}

.fn-alert-impact {
  font-size: 0.78rem;
  color: var(--fn-text-dim);
  margin-top: 0.3rem;
}

.fn-alert-action {
  font-size: 0.82rem;
  color: var(--fn-accent-cyan);
  margin-top: 0.45rem;
  font-weight: 600;
}

.fn-alert-action-label {
  color: var(--fn-text-muted);
  font-weight: 400;
}

/* Recommendation Cards */
.fn-recommendation-card {
  padding: 1.15rem 1.35rem;
  margin-bottom: 0.75rem;
}

.fn-rec-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.85rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.fn-rec-title-group {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.fn-rec-product-name {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--fn-text);
  margin: 0;
}

.fn-rec-order-badge {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  background: rgba(40, 184, 255, 0.08);
  border: 1px solid rgba(40, 184, 255, 0.3);
  border-radius: 8px;
  padding: 0.35rem 0.85rem;
}

.fn-rec-order-label {
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: var(--fn-accent-cyan);
}

.fn-rec-order-val {
  font-size: 1.25rem;
  font-weight: 800;
  color: #FFFFFF;
}

.fn-rec-metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
  background: var(--fn-surface-elevated);
  border-radius: 8px;
  padding: 0.65rem 0.85rem;
  margin-bottom: 0.75rem;
}

.fn-rec-metric {
  display: flex;
  flex-direction: column;
}

.fn-rec-metric span {
  font-size: 0.7rem;
  color: var(--fn-text-muted);
}

.fn-rec-metric b {
  font-size: 0.95rem;
  color: var(--fn-text);
  margin-top: 0.1rem;
}

.fn-rec-why {
  font-size: 0.82rem;
  color: var(--fn-text-muted);
  line-height: 1.4;
}

.fn-rec-why-label {
  color: var(--fn-accent-cyan);
  font-weight: 600;
}

/* Forecast Summary Card */
.fn-forecast-summary-card {
  margin-bottom: 1.25rem;
  background: linear-gradient(135deg, var(--fn-surface) 0%, var(--fn-surface-elevated) 100%);
}

.fn-fc-summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.fn-fc-item {
  display: flex;
  flex-direction: column;
}

.fn-fc-label {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--fn-text-muted);
  font-weight: 700;
}

.fn-fc-val {
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--fn-text);
  margin-top: 0.2rem;
}

.fn-fc-summary-reason {
  margin-top: 0.85rem;
  padding-top: 0.65rem;
  border-top: 1px solid var(--fn-border-subtle);
  font-size: 0.82rem;
  color: var(--fn-text-muted);
}

/* Executive Insights */
.fn-insight-card {
  margin-bottom: 1.25rem;
}

.fn-insight-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.65rem;
}

.fn-insight-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--fn-text);
  margin: 0;
}

.fn-insight-list {
  margin: 0;
  padding-left: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.fn-insight-item {
  font-size: 0.84rem;
  color: var(--fn-text-muted);
  line-height: 1.45;
}

.fn-insight-item b {
  color: var(--fn-text);
}

/* Empty State */
.fn-empty {
  text-align: center;
  padding: 3rem 1.5rem;
  background: var(--fn-surface);
  border: 1px dashed var(--fn-border);
  border-radius: 12px;
  margin: 1.5rem 0;
}

.fn-empty-icon {
  font-size: 2.2rem;
  margin-bottom: 0.5rem;
}

.fn-empty-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--fn-text);
  margin-bottom: 0.4rem;
}

.fn-empty-body {
  font-size: 0.88rem;
  color: var(--fn-text-muted);
  max-width: 860px;
  margin: 0 auto;
  line-height: 1.5;
  text-wrap: balance;
  text-wrap: pretty;
  text-align: center;
}

/* Streamlit Widget Overrides */
/* Buttons */
.stButton > button, .stDownloadButton > button {
  background-color: var(--fn-surface-elevated) !important;
  color: var(--fn-text) !important;
  border: 1px solid var(--fn-border) !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  padding: 0.45rem 1.1rem !important;
  font-size: 0.85rem !important;
  transition: all 180ms ease !important;
}

.stButton > button:hover, .stDownloadButton > button:hover {
  border-color: var(--fn-accent-cyan) !important;
  color: var(--fn-accent-cyan) !important;
  transform: translateY(-1px) !important;
}

.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, var(--fn-accent-blue) 0%, var(--fn-accent-cyan) 100%) !important;
  color: #080B11 !important;
  font-weight: 700 !important;
  border: none !important;
}

.stButton > button[kind="primary"]:hover {
  filter: brightness(1.1) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 12px rgba(40, 184, 255, 0.25) !important;
}

/* Form Inputs & Selects */
div[data-baseweb="select"] > div,
.stTextInput > div > div,
.stNumberInput > div > div {
  background-color: var(--fn-surface) !important;
  border-color: var(--fn-border) !important;
  border-radius: 8px !important;
  color: var(--fn-text) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  gap: 6px !important;
  border-bottom: 1px solid var(--fn-border) !important;
}

.stTabs [data-baseweb="tab"] {
  color: var(--fn-text-muted) !important;
  font-weight: 600 !important;
  font-size: 0.88rem !important;
  padding: 0.6rem 1.1rem !important;
}

.stTabs [aria-selected="true"] {
  color: var(--fn-accent-cyan) !important;
  border-bottom-color: var(--fn-accent-cyan) !important;
}

/* Expanders */
.streamlit-expanderHeader, div[data-testid="stExpander"] {
  background-color: var(--fn-surface) !important;
  border: 1px solid var(--fn-border) !important;
  border-radius: 10px !important;
}

/* File Uploader */
section[data-testid="stFileUploaderDropzone"] {
  background-color: var(--fn-surface) !important;
  border: 1px dashed var(--fn-border) !important;
  border-radius: 10px !important;
  padding: 1.5rem !important;
}

/* DataFrames & Interactive Data Editors */
div[data-testid="stDataFrame"], div[data-testid="stDataEditor"] {
  border: 1px solid var(--fn-border) !important;
  border-radius: 10px !important;
  overflow: hidden !important;
  background-color: var(--fn-surface) !important;
  transition: border-color 160ms ease, box-shadow 160ms ease !important;
}

div[data-testid="stDataEditor"]:focus-within {
  border-color: var(--fn-accent-cyan) !important;
  box-shadow: 0 0 0 1px rgba(40, 184, 255, 0.25) !important;
}

/* Sliders */
div[data-testid="stSlider"] > div > div > div[role="slider"] {
  background: var(--fn-accent-cyan) !important;
}

/* Streamlit native metric elements */
div[data-testid="stMetric"] {
  background: var(--fn-surface) !important;
  border: 1px solid var(--fn-border) !important;
  border-radius: 10px !important;
  padding: 0.8rem 1rem !important;
}

/* Keyframe Animations */
@keyframes fnPageFadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fnSlideIn {
  from { opacity: 0; transform: translateX(-6px); }
  to { opacity: 1; transform: translateX(0); }
}

@keyframes fnPulseLive {
  0% { transform: scale(0.92); opacity: 0.7; }
  50% { transform: scale(1.18); opacity: 1; }
  100% { transform: scale(0.92); opacity: 0.7; }
}

.fn-pulse-live {
  display: inline-block;
  animation: fnPulseLive 2s infinite ease-in-out;
}

/* Responsive Breakpoints */
@media (max-width: 1024px) {
  .fn-hero { padding: 1.25rem 1.4rem; }
  .fn-hero-brand-line { font-size: 1.35rem; }
  .fn-hero-meta { flex-wrap: wrap; gap: 0.75rem 1.25rem; }
  .fn-fc-summary-grid { grid-template-columns: repeat(2, 1fr); }
  .fn-rec-metrics-grid { grid-template-columns: repeat(2, 1fr); }
  .fn-kpi-value { font-size: 1.35rem; }
  .fn-kpi-card { padding: 0.85rem 1rem; }

  [data-testid="stHorizontalBlock"] {
    flex-wrap: wrap !important;
    gap: 0.75rem !important;
  }
  [data-testid="stHorizontalBlock"] > div[data-testid="column"] {
    min-width: 180px !important;
    flex: 1 1 calc(50% - 0.75rem) !important;
  }
}

@media (max-width: 640px) {
  .block-container {
    padding-left: 0.75rem !important;
    padding-right: 0.75rem !important;
  }
  .fn-hero {
    padding: 1.1rem 1rem;
    margin-bottom: 0.85rem;
  }
  .fn-hero-brand-line {
    font-size: 1.2rem;
    flex-wrap: wrap;
  }
  .fn-hero-tagline { font-size: 0.88rem; }
  .fn-hero-desc { font-size: 0.8rem; }
  .fn-hero-meta {
    flex-direction: column;
    gap: 0.35rem;
    font-size: 0.74rem;
  }
  .fn-kpi-value { font-size: 1.35rem; }
  .fn-kpi-card { padding: 0.85rem 1rem; }
  .fn-rec-metrics-grid { grid-template-columns: 1fr; }
  .fn-fc-summary-grid { grid-template-columns: 1fr; }
  .fn-nexus-container { margin: 0 0 0.75rem 0; }

  [data-testid="stHorizontalBlock"] > div[data-testid="column"] {
    min-width: 100% !important;
    flex: 1 1 100% !important;
  }

  /* Prevent horizontal scroll */
  div[data-testid="stPlotlyChart"] {
    max-height: 320px;
    width: 100% !important;
  }
}
</style>
"""
