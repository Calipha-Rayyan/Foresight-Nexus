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


def has_data() -> bool:
    return st.session_state.get("dataset") is not None and len(st.session_state["dataset"]) > 0
