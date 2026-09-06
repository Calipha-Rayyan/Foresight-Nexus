# FORESIGHT Nexus — Final Browser QA Checklist

**Status: Browser-rendered responsive QA has not been performed.** The
engineering sandbox used to build this project has network egress restricted
to package registries only (pip/npm/GitHub) — it cannot reach the
Playwright/Chromium browser-download CDN, so no headless browser could be
launched to render and screenshot the app. Everything in this document is a
checklist for a human reviewer (or a CI job with real browser access) to
work through — it has not been executed, and no screenshots exist yet.

Do not treat any item below as complete until someone has actually opened
the app in a real browser (or device/emulator) and looked at it.

---

## How to run this checklist

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL Streamlit prints (typically `http://localhost:8501`).
Load the demo dataset from Data Lab first — most pages show an empty state
until a dataset is loaded.

Use your browser's device toolbar (Chrome/Edge DevTools → Toggle Device
Toolbar, or Firefox Responsive Design Mode) to set each width below, or
resize the window manually for desktop widths.

---

## 1. Viewport Checklist

For **every** viewport width listed, check every item in the "Check at each
width" list against every page (Command Center, Demand Intelligence,
Inventory Intelligence, Forecast Studio, Product Explorer, Alerts & Risks,
Recommendations, Data Lab, Model Performance, Settings).

### Desktop
- [ ] 1920px
- [ ] 1600px
- [ ] 1440px
- [ ] 1280px
- [ ] 1024px

### Tablet
- [ ] 1024px (portrait)
- [ ] 834px
- [ ] 820px
- [ ] 768px

### Mobile
- [ ] 430px
- [ ] 412px
- [ ] 390px

### Check at each width
- [ ] Page width — no forced minimum width wider than the viewport
- [ ] Horizontal overflow — no horizontal scrollbar anywhere on the page
- [ ] Sidebar — opens/collapses correctly, nav items are tappable/clickable, text isn't clipped
- [ ] KPI cards — grid reflows sensibly (4-across on desktop → 2-across tablet → 1-across mobile), no card is cut off or overlapping another
- [ ] Plotly charts — render at a readable size, legends don't overflow the chart area, axis labels aren't overlapping, tooltips appear on hover/tap
- [ ] Tables (`st.dataframe`) — scroll horizontally within their own container rather than forcing the page wider; column headers stay legible
- [ ] Filters/selectboxes (category, product, horizon, model) — fully visible, dropdown opens without being clipped by the viewport edge
- [ ] Buttons — full label visible, comfortably tappable on touch (not < ~40px tall)
- [ ] Empty states ("No dataset loaded", etc.) — text and button are centered and readable, not stretched or squashed
- [ ] Loading states (spinners during forecast/backtest generation) — visible, don't cause a layout jump when they resolve
- [ ] Alert cards (Alerts & Risks) — severity pill, title, body, and action text all readable without truncation or overlap
- [ ] Recommendation cards — order-quantity metric and explanation text both fully visible, card doesn't overflow horizontally
- [ ] 3D data-nexus hero (Command Center) — SVG scales with its container, keeps aspect ratio, never overlaps the hero text above/below it, never causes horizontal scroll, animation doesn't visibly stutter
- [ ] Typography — page title / section title / KPI value / KPI label / body text maintain a clear size hierarchy at every width (nothing becomes illegibly small on mobile, nothing dominates the screen on desktop)
- [ ] Spacing — consistent padding around cards/sections; no elements touching the viewport edge on mobile; no excessive dead whitespace on ultra-wide desktop

---

## 2. Manual User-Journey Checklist

### Demo flow
- [ ] Load Demo Dataset (Data Lab) succeeds and shows a success message
- [ ] Command Center populates with real KPIs, executive summary, and outlook chart
- [ ] Demand Intelligence shows trend/seasonality/category charts with real numbers
- [ ] Product Explorer: selecting a product shows consistent stock/forecast/risk data
- [ ] Forecast Studio: generating a forecast for the same product shows a model, forecast total, and confidence — matches Product Explorer's forecast direction
- [ ] Inventory Intelligence: health matrix and aging buckets populate
- [ ] Recommendations: reorder-eligible products appear with explanations that cite real numbers

### Upload flow
- [ ] Upload a valid CSV in Data Lab
- [ ] Column mapping UI appears and lets you map required/optional fields
- [ ] "Apply Mapping & Clean Data" succeeds, data health score and preview appear
- [ ] Downstream pages (Command Center, Forecast Studio, etc.) reflect the uploaded data, not the demo data

### Error flow
- [ ] Upload a malformed CSV (bad dates, negative quantities, missing required column)
- [ ] No raw Python traceback is ever shown
- [ ] A plain-language error or cleaning-log message explains what happened
- [ ] The affected field/column is identifiable from the message

### Insufficient-history flow
- [ ] Use or construct a dataset where a product has under ~30 days of history
- [ ] In Forecast Studio, confirm ARIMA is not offered/selected for that product (or a graceful fallback message appears if manually selected)
- [ ] A baseline model (Naive/Moving Average/Seasonal Naive) is used instead
- [ ] The on-screen explanation says why (insufficient history), not a generic error

---

## 3. Numerical Consistency Checklist

Pick **one product** and record its values on each page below. All values in
the same row must match (or be a clearly explainable derivative, e.g.
Forecast Studio's chosen forecast horizon differing from Product Explorer's
fixed 30-day forecast).

| Metric | Command Center | Inventory Intelligence | Product Explorer | Alerts & Risks | Recommendations | Forecast Studio |
|---|---|---|---|---|---|---|
| Current Stock | | | | | | — |
| Forecast (specify horizon) | | — | | — | — | |
| Safety Stock | — | — | | — | (in explanation text) | — |
| Reorder Point | — | — | | — | (in explanation text) | — |
| Coverage (days) | | | | | | — |
| Risk Level | | | | | | — |
| Recommended Order Qty | (reorder value estimate) | — | | — | | — |

If any cell disagrees with another for the same product, that's a real bug —
please report it rather than assuming it's expected.

---

## 4. Deployment Checklist

- [ ] Streamlit entry point is `app.py`
- [ ] `requirements.txt` installs cleanly in a fresh virtual environment
- [ ] `.streamlit/config.toml` is present and applies the dark theme
- [ ] No secrets or credentials are committed anywhere in the repo
- [ ] All file paths are relative/portable (no hard-coded Windows paths or drive letters)
- [ ] Demo dataset generates in-app (`data/sample/generate_sample.py`) — no external file/network dependency required to see a populated dashboard
- [ ] `streamlit run app.py` boots without errors from a clean `__pycache__`-free checkout
- [ ] `http://localhost:8501/_stcore/health` returns `ok` while the app is running

---

## 5. Sign-off

- [ ] All viewport checks above completed with real browser rendering
- [ ] All user journeys completed
- [ ] Numerical consistency table filled in with no mismatches
- [ ] Deployment checklist completed
- [ ] Reviewer name/date: _______________________

Until this section is checked off by an actual human (or CI) browser
session, FORESIGHT Nexus should be considered a **release candidate**, not a
verified release.
