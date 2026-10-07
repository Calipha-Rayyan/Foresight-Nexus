import os
import streamlit as st
from core.config import DEFAULT_SETTINGS


def init_state():
    defaults = {
        "dataset": None,          # raw cleaned DataFrame
        "column_mapping": {},
        "cleaning_log": [],
        "settings": DEFAULT_SETTINGS,
        "selected_product": None,
        "forecast_cache": {},
        "demo_mode": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # Optional automated demo dataset initialization for QA and head-to-head testing
    if os.environ.get("FORESIGHT_AUTOLOAD_DEMO") == "1" and st.session_state.get("dataset") is None:
        from data.sample.generate_sample import generate_sample_dataset
        from core.constants import REQUIRED_COLUMNS, OPTIONAL_COLUMNS
        from database.repositories import SalesRepository
        df = generate_sample_dataset()
        st.session_state["dataset"] = df
        st.session_state["demo_mode"] = True
        st.session_state["cleaning_log"] = ["Demo dataset initialized."]
        st.session_state["column_mapping"] = {c: c for c in REQUIRED_COLUMNS + OPTIONAL_COLUMNS if c in df.columns}
        try:
            SalesRepository.load(df)
        except Exception:
            pass


def has_data() -> bool:
    return st.session_state.get("dataset") is not None and len(st.session_state["dataset"]) > 0
