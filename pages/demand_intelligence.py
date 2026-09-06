import streamlit as st
from core.state import has_data
from ui.components import kpi_card, empty_state, section_title
from analytics.demand import demand_growth_pct, volatility, category_demand, top_growth_products
from visualizations.demand_charts import (create_demand_trend_chart, create_weekly_seasonality_chart,
                                           create_monthly_seasonality_chart, create_category_demand_chart)

st.title("Demand Intelligence")

if not has_data():
    empty_state("No dataset loaded", "Upload your sales history or load the demo dataset to see demand analytics.")
    st.stop()

df = st.session_state["dataset"]
daily = df.groupby("date", as_index=False)["quantity"].sum().rename(columns={"quantity": "demand"})
daily = daily.set_index("date").asfreq("D", fill_value=0).reset_index()

total_demand = int(df["quantity"].sum())
growth = demand_growth_pct(daily)
avg_daily = round(daily["demand"].tail(90).mean(), 1)
vol = volatility(daily)

c1, c2, c3, c4 = st.columns(4)
with c1: kpi_card("Total Demand", f"{total_demand:,} units")
with c2: kpi_card("Demand Growth (28d)", f"{growth:+.1f}%" if growth is not None else "N/A", delta_positive=(growth or 0) >= 0)
with c3: kpi_card("Avg Daily Demand", f"{avg_daily}")
with c4: kpi_card("Demand Volatility", f"{vol}%", context="Coefficient of variation, last 28 days")

section_title("Trend")
st.plotly_chart(create_demand_trend_chart(daily), use_container_width=True)

section_title("Seasonality")
c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(create_weekly_seasonality_chart(df), use_container_width=True)
with c2:
    st.plotly_chart(create_monthly_seasonality_chart(df), use_container_width=True)

if "category" in df.columns:
    section_title("Category Comparison")
    cat = category_demand(df)
    st.plotly_chart(create_category_demand_chart(cat), use_container_width=True)

c1, c2 = st.columns(2)
with c1:
    section_title("Strongest Demand Growth")
    growers = top_growth_products(df, top_n=8)
    if len(growers):
        st.dataframe(growers, use_container_width=True, hide_index=True)
    else:
        st.caption("Not enough history yet to compute growth leaders (needs 56+ days).")
with c2:
    section_title("Demand Decline")
    decliners = top_growth_products(df, top_n=200).sort_values("growth_pct").head(8)
    if len(decliners):
        st.dataframe(decliners, use_container_width=True, hide_index=True)
    else:
        st.caption("Not enough history yet to compute decline leaders (needs 56+ days).")
