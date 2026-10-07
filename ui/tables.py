"""Table formatting, interactive data editors, and DataFrame column configuration helpers."""
from typing import Any
import pandas as pd
import streamlit as st


def build_table_column_config(
    df: pd.DataFrame,
    editable_columns: list[str] | None = None,
    custom_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Generates optimized Streamlit column configurations with vivid, high-contrast
    styling for promotions, monetary figures, and date series.
    """
    col_cfg: dict[str, Any] = dict(custom_config or {})
    edit_set = set(editable_columns or [])

    # Promotion Column: Vivid, High-Contrast & Interactive
    if "promotion" in df.columns and "promotion" not in col_cfg:
        col_cfg["promotion"] = st.column_config.CheckboxColumn(
            label="Promotion",
            help="Active marketing promotion or price discount campaign (Interactive toggle)",
            default=False,
            disabled=False if (not editable_columns or "promotion" in edit_set) else True,
        )

    # Standard Semantic Columns
    if "date" in df.columns and "date" not in col_cfg:
        col_cfg["date"] = st.column_config.DateColumn("Date", format="YYYY-MM-DD")

    if "price" in df.columns and "price" not in col_cfg:
        col_cfg["price"] = st.column_config.NumberColumn("Price", format="$%.2f")

    if "revenue" in df.columns and "revenue" not in col_cfg:
        col_cfg["revenue"] = st.column_config.NumberColumn("Revenue", format="$%.2f")

    if "quantity" in df.columns and "quantity" not in col_cfg:
        col_cfg["quantity"] = st.column_config.NumberColumn("Quantity", format="%d")

    if "inventory" in df.columns and "inventory" not in col_cfg:
        col_cfg["inventory"] = st.column_config.NumberColumn("Inventory", format="%d")

    if "lead_time" in df.columns and "lead_time" not in col_cfg:
        col_cfg["lead_time"] = st.column_config.NumberColumn("Lead Time (d)", format="%d")

    return col_cfg


def style_dataframe(
    df: pd.DataFrame,
    height: int | None = None,
    interactive: bool | None = None,
    editable_columns: list[str] | None = None,
    column_config: dict[str, Any] | None = None,
    key: str | None = None,
) -> pd.DataFrame | None:
    """Renders a styled, responsive DataFrame or interactive DataEditor.

    If interactive is True, or editable_columns is specified, or if 'promotion'
    is present in the columns (unless interactive is explicitly False), renders
    via st.data_editor so that the promotion column is vibrant, colorful, and
    clickable, while locking all other columns to protect operational integrity.
    """
    if df is None or df.empty:
        st.caption("No tabular records to display.")
        return df

    # Determine whether interactive mode should be engaged
    should_be_interactive = (
        interactive is True
        or editable_columns is not None
        or (interactive is not False and "promotion" in df.columns)
    )

    # Build optimized column configurations
    active_editable = editable_columns or (["promotion"] if "promotion" in df.columns else [])
    cfg = build_table_column_config(df, active_editable, column_config)

    kwargs: dict[str, Any] = {"hide_index": True, "column_config": cfg}
    if height is not None:
        kwargs["height"] = height

    if should_be_interactive:
        disabled_cols = [c for c in df.columns if c not in active_editable]
        if key is not None:
            kwargs["key"] = key
        try:
            return st.data_editor(
                df,
                disabled=disabled_cols,
                width="stretch",
                num_rows="fixed",
                **kwargs,
            )
        except (TypeError, AttributeError):
            try:
                return st.data_editor(
                    df,
                    disabled=disabled_cols,
                    use_container_width=True,
                    num_rows="fixed",
                    **kwargs,
                )
            except Exception:
                pass  # Fall back to standard st.dataframe below

    # Standard read-only presentation
    try:
        st.dataframe(df, width="stretch", **kwargs)
    except TypeError:
        st.dataframe(df, use_container_width=True, **kwargs)
    return df
