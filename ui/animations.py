"""Subtle count-up animation for KPI numbers, implemented as a small inline
HTML/JS snippet. Falls back silently to a static number if JS doesn't run
(e.g. the value is still shown immediately by the initial render)."""
import streamlit as st
import uuid


def count_up(value: float, label: str, prefix: str = "", suffix: str = "", decimals: int = 0,
              duration_ms: int = 700):
    el_id = f"fn-cu-{uuid.uuid4().hex[:8]}"
    st.markdown(f"""
    <div class="fn-card">
        <div class="fn-kpi-label">{label}</div>
        <div class="fn-kpi-value" id="{el_id}">{prefix}0{suffix}</div>
    </div>
    <script>
    (function() {{
        const target = {value};
        const el = document.getElementById("{el_id}");
        if (!el) return;
        const duration = {duration_ms};
        const start = performance.now();
        function tick(now) {{
            const progress = Math.min((now - start) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            const current = target * eased;
            el.textContent = "{prefix}" + current.toFixed({decimals}) + "{suffix}";
            if (progress < 1) requestAnimationFrame(tick);
        }}
        requestAnimationFrame(tick);
    }})();
    </script>
    """, unsafe_allow_html=True)
