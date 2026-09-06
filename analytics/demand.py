import pandas as pd


def demand_growth_pct(series: pd.DataFrame, recent_days: int = 28, prior_days: int = 28) -> float | None:
    """% change in average daily demand: last `recent_days` vs the `prior_days` before that."""
    s = series.sort_values("date")
    if len(s) < recent_days + prior_days:
        return None
    recent = s["demand"].tail(recent_days).mean()
    prior = s["demand"].tail(recent_days + prior_days).head(prior_days).mean()
    if prior <= 0:
        return None
    return round((recent - prior) / prior * 100, 2)


def volatility(series: pd.DataFrame, window: int = 28) -> float:
    s = series.sort_values("date")
    tail = s["demand"].tail(window)
    if tail.mean() <= 0:
        return 0.0
    return round(float(tail.std() / tail.mean() * 100), 2)  # coefficient of variation %


def category_demand(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("category", as_index=False)["quantity"].sum().rename(columns={"quantity": "total_demand"})


def top_growth_products(df: pd.DataFrame, recent_days: int = 28, top_n: int = 10) -> pd.DataFrame:
    results = []
    max_date = df["date"].max()
    recent_cut = max_date - pd.Timedelta(days=recent_days)
    prior_cut = recent_cut - pd.Timedelta(days=recent_days)
    for pid, g in df.groupby("product_id"):
        recent = g[g["date"] > recent_cut]["quantity"].sum()
        prior = g[(g["date"] > prior_cut) & (g["date"] <= recent_cut)]["quantity"].sum()
        if prior > 0:
            pct = (recent - prior) / prior * 100
            name = g["product_name"].iloc[0]
            results.append({"product_id": pid, "product_name": name, "growth_pct": round(pct, 1),
                             "recent_demand": int(recent), "prior_demand": int(prior)})
    out = pd.DataFrame(results).sort_values("growth_pct", ascending=False)
    return out.head(top_n)
