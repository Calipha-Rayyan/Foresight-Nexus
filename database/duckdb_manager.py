"""DuckDB-backed analytical storage. Used to persist the active dataset for
the session and run fast aggregate queries without re-scanning pandas for
every page. SQLite (sqlite_manager.py) is used instead for tiny bits of
application state (e.g. saved settings) where DuckDB would be overkill.
"""
import duckdb
import pandas as pd
import streamlit as st


@st.cache_resource(show_spinner=False)
def get_connection():
    """One in-memory DuckDB connection per Streamlit session/resource cache."""
    return duckdb.connect(database=":memory:")


def load_dataframe(df: pd.DataFrame, table_name: str = "sales") -> None:
    con = get_connection()
    con.register("df_view", df)
    con.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df_view")


def query(sql: str) -> pd.DataFrame:
    con = get_connection()
    return con.execute(sql).df()


def category_totals(table_name: str = "sales") -> pd.DataFrame:
    return query(f"""
        SELECT category, SUM(quantity) AS total_demand, COUNT(DISTINCT product_id) AS products
        FROM {table_name}
        GROUP BY category
        ORDER BY total_demand DESC
    """)


def product_summary(table_name: str = "sales") -> pd.DataFrame:
    return query(f"""
        SELECT product_id, product_name, SUM(quantity) AS total_quantity,
               AVG(quantity) AS avg_daily_quantity, MIN(date) AS first_date, MAX(date) AS last_date
        FROM {table_name}
        GROUP BY product_id, product_name
        ORDER BY total_quantity DESC
    """)
