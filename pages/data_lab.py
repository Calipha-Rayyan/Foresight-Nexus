import streamlit as st
from core.constants import REQUIRED_COLUMNS, OPTIONAL_COLUMNS
from data.loader import load_file, apply_mapping, clean_dataset, data_health_score
from data.sample.generate_sample import generate_sample_dataset
from ui.components import section_title, kpi_card
from database.repositories import SalesRepository
from utils.logging import log_error

st.title("Data Lab")
st.caption("Upload your sales & inventory history, or load the demo dataset to explore FORESIGHT Nexus.")

tab_upload, tab_demo = st.tabs(["Upload Dataset", "Load Demo Dataset"])

with tab_demo:
    st.write("Generates a realistic 24-month synthetic sales & inventory dataset across 30 products "
             "in 5 categories, with trend, seasonality, promotions, and deliberate stockout/overstock patterns.")
    if st.button("Load Demo Dataset", type="primary"):
        with st.spinner("Generating synthetic demand history..."):
            df = generate_sample_dataset()
        st.session_state["dataset"] = df
        st.session_state["demo_mode"] = True
        st.session_state["cleaning_log"] = ["Demo dataset generated — no cleaning required."]
        st.session_state["column_mapping"] = {c: c for c in REQUIRED_COLUMNS + OPTIONAL_COLUMNS if c in df.columns}
        try:
            SalesRepository.load(df)
        except Exception as e:
            log_error("DuckDB load failed for demo dataset", e)
        st.success(f"Demo dataset loaded: {len(df):,} rows, {df['product_id'].nunique()} products.")
        st.rerun()

with tab_upload:
    uploaded = st.file_uploader("Drag and drop a CSV or XLSX file", type=["csv", "xlsx", "xls"])
    if uploaded is not None:
        try:
            raw_df = load_file(uploaded)
        except Exception as e:
            log_error("File load failed", e)
            st.error("This file couldn't be read. Please confirm it's a valid CSV or XLSX file and try again.")
            raw_df = None

        if raw_df is not None:
            st.write("**Column Mapping** — map your file's columns to the fields FORESIGHT Nexus needs.")
            cols = ["— none —"] + list(raw_df.columns)
            mapping = {}
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Required**")
                for field in REQUIRED_COLUMNS:
                    guess = field if field in raw_df.columns else "— none —"
                    sel = st.selectbox(field, cols, index=cols.index(guess) if guess in cols else 0, key=f"map_{field}")
                    mapping[field] = None if sel == "— none —" else sel
            with c2:
                st.markdown("**Optional**")
                for field in OPTIONAL_COLUMNS:
                    guess = field if field in raw_df.columns else "— none —"
                    sel = st.selectbox(field, cols, index=cols.index(guess) if guess in cols else 0, key=f"map_{field}")
                    mapping[field] = None if sel == "— none —" else sel

            missing = [f for f in REQUIRED_COLUMNS if not mapping.get(f)]
            if missing:
                st.warning(f"Missing required field(s): {', '.join(missing)}. These must be mapped before continuing.")
            else:
                if st.button("Apply Mapping & Clean Data", type="primary"):
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
                        st.success("Dataset processed.")
                        st.rerun()
                    except Exception as e:
                        log_error("Data cleaning pipeline failed", e)
                        st.error("Something went wrong while processing this dataset. Please check that the "
                                  "mapped columns contain the expected data types (dates, numeric quantities).")

if st.session_state.get("dataset") is not None:
    df = st.session_state["dataset"]
    section_title("Data Health")
    health = data_health_score(df, st.session_state.get("column_mapping", {}))
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi_card("Health Score", f"{health['score']} / 100")
    with c2: kpi_card("Rows", f"{health['rows']:,}")
    with c3: kpi_card("Products", f"{health['products']}")
    with c4:
        dr = health["date_range"]
        rng = f"{dr[0].date()} → {dr[1].date()}" if dr[0] is not None else "—"
        kpi_card("Date Range", rng)
    with c5: kpi_card("Missing Values", f"{health['missing_pct']}%")

    if st.session_state.get("cleaning_log"):
        with st.expander("What changed during cleaning"):
            for line in st.session_state["cleaning_log"]:
                st.write(f"- {line}")

    missing_optional = [c for c in OPTIONAL_COLUMNS if c not in df.columns]
    if "lead_time" in missing_optional:
        st.info("Supplier lead time unavailable. Reorder recommendations will use the configured default lead time (Settings page).")
    if "price" in missing_optional and "revenue" in missing_optional:
        st.info("Price/revenue fields unavailable — financial intelligence (inventory value, revenue) will not be calculated.")

    section_title("Preview")
    st.dataframe(df.head(200), use_container_width=True)
else:
    st.info("No dataset loaded yet. Load the demo dataset or upload your own file above.")
