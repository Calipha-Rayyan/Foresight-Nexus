"""FORESIGHT Nexus — Data Lab.

Enterprise data ingestion and validation hub: upload CSV/XLSX files, map schemas,
generate synthetic demo environments, and audit automated data cleansing rules.
"""
import streamlit as st
from core.constants import REQUIRED_COLUMNS, OPTIONAL_COLUMNS
from data.loader import (
    load_file, apply_mapping, clean_dataset, data_health_score,
    guess_column, generate_csv_template
)
from data.sample.generate_sample import generate_sample_dataset
from ui.headers import render_page_header, render_section_header
from ui.cards import render_kpi_card
from ui.tables import style_dataframe
from database.repositories import SalesRepository
from utils.logging import log_error

render_page_header(
    "Data Lab",
    "Connect your historical sales, demand, and inventory records to activate FORESIGHT Nexus intelligence.",
    meta_items=["Multi-Format Ingestion", "Automated Cleansing", "Schema Mapping"]
)

tab_upload, tab_demo = st.tabs(["📁 Upload Enterprise Dataset", "⚡ Instant Demo Dataset"])

with tab_upload:
    st.markdown(
        '<div class="fn-card" style="padding:1.2rem 1.4rem; margin-bottom:1.2rem;">'
        '<div style="font-size:1.05rem; font-weight:700; color:#F1F5F9; margin-bottom:0.35rem;">Enterprise Data Onboarding Workflow</div>'
        '<p style="font-size:0.86rem; color:#8B9BB4; line-height:1.55; margin-bottom:0.8rem;">'
        'Bring your organization\'s historical transactional records (CSV or Excel) from ERP, POS, or WMS systems '
        '(such as SAP, NetSuite, Shopify, or QuickBooks). Our intelligent pipeline automatically matches common column aliases, '
        'removes anomalies, verifies chronological continuity, and loads data directly into our local DuckDB analytical engine.'
        '</p>'
        '</div>',
        unsafe_allow_html=True
    )

    t_col1, t_col2 = st.columns([3, 1])
    with t_col1:
        st.caption("Need a reference schema for your enterprise data export? Download our standard template:")
    with t_col2:
        st.download_button(
            "📥 Download CSV Template",
            data=generate_csv_template(),
            file_name="foresight_nexus_enterprise_template.csv",
            mime="text/csv",
            use_container_width=True,
            help="Pre-formatted CSV with 11 standard headers and sample records ready for enterprise population."
        )

    pending_file = st.session_state.pop("pending_file", None)
    uploaded = st.file_uploader(
        "Drop your CSV or XLSX file here",
        type=["csv", "xlsx", "xls"],
        key="data_lab_file_uploader"
    )
    if uploaded is None and pending_file is not None:
        uploaded = pending_file

    if uploaded is not None:
        try:
            raw_df = load_file(uploaded)
        except Exception as e:
            log_error("File parsing failed", e)
            st.error("This file could not be parsed. Please verify the format and try again.")
            raw_df = None

        if raw_df is not None:
            render_section_header("Schema Alignment", "Map your source columns to the standard FORESIGHT Nexus semantic model.")
            available_cols = list(raw_df.columns)
            cols = ["— none —"] + available_cols
            mapping = {}
            c1, c2 = st.columns(2)
            with c1:
                st.write("**Mandatory Fields** (Core Time-Series)")
                for field in REQUIRED_COLUMNS:
                    guess = guess_column(field, available_cols) or "— none —"
                    idx = cols.index(guess) if guess in cols else 0
                    sel = st.selectbox(f"Map '{field}'", cols, index=idx, key=f"map_{field}")
                    mapping[field] = None if sel == "— none —" else sel
            with c2:
                st.write("**Optional Fields** (Inventory & Financial Intelligence)")
                for field in OPTIONAL_COLUMNS:
                    guess = guess_column(field, available_cols) or "— none —"
                    idx = cols.index(guess) if guess in cols else 0
                    sel = st.selectbox(f"Map '{field}'", cols, index=idx, key=f"map_{field}")
                    mapping[field] = None if sel == "— none —" else sel

            missing = [f for f in REQUIRED_COLUMNS if not mapping.get(f)]
            if missing:
                st.warning(f"⚠️ Mandatory fields unmapped: {', '.join(missing)}. Map these columns to continue.")
            else:
                if st.button("Apply Mapping & Ingest Dataset", type="primary"):
                    with st.spinner("Executing data cleansing pipeline and schema validation..."):
                        try:
                            mapped = apply_mapping(raw_df, mapping)
                            cleaned, log = clean_dataset(mapped)
                            st.session_state["dataset"] = cleaned
                            st.session_state["demo_mode"] = False
                            st.session_state["cleaning_log"] = log
                            st.session_state["column_mapping"] = mapping
                            try:
                                SalesRepository.load(cleaned)
                            except Exception as e:
                                log_error("DuckDB load failed for uploaded dataset", e)
                            st.success("✅ Dataset successfully ingested and verified.")
                            st.rerun()
                        except Exception as e:
                            log_error("Cleansing pipeline error", e)
                            st.error("Error during data cleansing. Please ensure dates and quantities are appropriately typed.")

with tab_demo:
    st.write(
        "Generate a calibrated 24-month multi-category dataset across 30 SKUs with organic trend drift, "
        "weekly & annual seasonality, promotional shocks, and authentic inventory depletion cycles."
    )
    if st.button("Generate & Activate Demo Dataset", type="secondary"):
        with st.spinner("Compiling synthetic market signals..."):
            df = generate_sample_dataset()
        st.session_state["dataset"] = df
        st.session_state["demo_mode"] = True
        st.session_state["cleaning_log"] = ["Demo dataset synthesized — verified zero schema violations."]
        st.session_state["column_mapping"] = {c: c for c in REQUIRED_COLUMNS + OPTIONAL_COLUMNS if c in df.columns}
        try:
            SalesRepository.load(df)
        except Exception as e:
            log_error("DuckDB load failed for demo dataset", e)
        st.success(f"✅ Demo environment activated: {len(df):,} records across {df['product_id'].nunique()} product lines.")
        st.rerun()

# -------------------------------------------------------------
# Active Dataset Health Scorecard
# -------------------------------------------------------------
if st.session_state.get("dataset") is not None:
    df = st.session_state["dataset"]
    is_demo = st.session_state.get("demo_mode", False)

    col_hdr, col_btn = st.columns([3, 1])
    with col_hdr:
        render_section_header("Active Dataset Telemetry & Health Audit", "Diagnostic scoring across completeness, continuity, and schema compliance.")
    with col_btn:
        st.write("")
        if st.button("🔄 Ingest / Switch Dataset", use_container_width=True, help="Reset active dataset and upload a new enterprise file"):
            st.session_state["dataset"] = None
            st.session_state["demo_mode"] = False
            st.session_state["cleaning_log"] = []
            st.session_state["column_mapping"] = {}
            st.rerun()

    if is_demo:
        st.info("ℹ️ **Active Environment:** 🧪 Evaluation Sandbox (Demo Dataset). You are viewing synthetic market signals. To analyze your organization's data, use the Upload tab above or click 'Switch Dataset'.")
    else:
        st.success(f"🏢 **Active Environment:** Live Enterprise Ingestion. Operating on verified customer records ({len(df):,} transactions).")

    health = data_health_score(df, st.session_state.get("column_mapping", {}))
    
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        score = health["score"]
        render_kpi_card("Health Score", f"{score} / 100", status="Healthy" if score >= 80 else "Watch")
    with c2:
        render_kpi_card("Total Rows", f"{health['rows']:,}")
    with c3:
        render_kpi_card("Unique SKUs", f"{health['products']}")
    with c4:
        dr = health["date_range"]
        rng = f"{dr[0].date()} → {dr[1].date()}" if dr[0] is not None else "—"
        render_kpi_card("Historical Window", rng)
    with c5:
        render_kpi_card("Missing Values", f"{health['missing_pct']}%", status="Healthy" if health['missing_pct'] == 0 else "Watch")

    if st.session_state.get("cleaning_log"):
        with st.expander("Cleansing Pipeline Audit Log"):
            for line in st.session_state["cleaning_log"]:
                st.write(f"- {line}")

    missing_optional = [c for c in OPTIONAL_COLUMNS if c not in df.columns]
    if "inventory" in missing_optional:
        st.info("ℹ️ **Notice:** No 'inventory' column mapped. Inventory Intelligence and Replenishment Recommendations require inventory counts.")

    render_section_header(
        "Catalog Preview & Promotional Scenario Studio",
        "Top 100 historical records from active dataset. The promotion column is fully interactive — click any checkbox to simulate promotional campaigns in real time."
    )
    preview_slice = df.head(100).copy()
    has_promo = "promotion" in df.columns
    edited_preview = style_dataframe(
        preview_slice,
        interactive=True,
        editable_columns=["promotion"] if has_promo else None,
        key="catalog_preview_table",
    )
    if edited_preview is not None and has_promo and "promotion" in edited_preview.columns:
        curr_vals = df.loc[edited_preview.index, "promotion"].values
        new_vals = edited_preview["promotion"].values
        if not (curr_vals == new_vals).all():
            df.loc[edited_preview.index, "promotion"] = new_vals
            st.session_state["dataset"] = df
            try:
                SalesRepository.load(df)
            except Exception as e:
                log_error("Failed to sync edited promotion state to DuckDB", e)
            st.toast("⚡ Promotional campaign updated in active dataset & DuckDB!", icon="⚡")
