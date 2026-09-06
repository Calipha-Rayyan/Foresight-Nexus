"""Thin wrappers documenting FORESIGHT Nexus's caching policy:
- st.cache_data for deterministic data transforms (per-product series, backtests, forecasts)
- st.cache_resource for shared, expensive-to-create resources (DuckDB connection, trained models)
Actual @st.cache_data / @st.cache_resource decorators live directly on the
functions in forecasting/, utils/pipeline.py, and database/ — this module
exists as the documented single source of truth for the policy and for any
future cross-cutting cache-invalidation helpers.
"""
import streamlit as st


def clear_all_caches():
    st.cache_data.clear()
    st.cache_resource.clear()
