"""Generates a realistic synthetic sales/inventory dataset for FORESIGHT Nexus demo mode.

Not random noise: each product has a base level, a trend, weekly + yearly
seasonality, occasional promo spikes, and a subset with deliberate decline
or stockout/overstock patterns, so downstream forecasting/risk logic has
something real to compute on.
"""
import numpy as np
import pandas as pd

CATEGORIES = {
    "Electronics": ["Wireless Mouse", "USB-C Hub", "Bluetooth Speaker", "Laptop Stand", "Webcam HD",
                     "Mechanical Keyboard", "Power Bank 10K", "Noise Cancel Earbuds"],
    "Home": ["Ceramic Mug Set", "LED Desk Lamp", "Throw Blanket", "Aroma Diffuser", "Wall Clock",
             "Storage Bin Set", "Cutting Board Set"],
    "Apparel": ["Cotton T-Shirt", "Running Socks 3pk", "Fleece Hoodie", "Rain Jacket", "Baseball Cap"],
    "Office": ["Notebook A5", "Gel Pen Pack", "Desk Organizer", "Whiteboard Small", "Sticky Notes Pack"],
    "Outdoor": ["Water Bottle 1L", "Camping Chair", "Hiking Backpack", "Insect Repellent", "Picnic Mat"],
}

def _rng(seed):
    return np.random.default_rng(seed)

def generate_sample_dataset(months: int = 24, seed: int = 42) -> pd.DataFrame:
    r = _rng(seed)
    end_date = pd.Timestamp.today().normalize()
    start_date = end_date - pd.DateOffset(months=months)
    dates = pd.date_range(start_date, end_date, freq="D")

    rows = []
    product_id = 1000
    for category, products in CATEGORIES.items():
        for name in products:
            product_id += 1
            base = r.uniform(8, 60)
            trend_per_day = r.normal(0.0, 0.015) * base  # slow drift, can be + or -
            weekly_amp = r.uniform(0.05, 0.30)
            yearly_amp = r.uniform(0.05, 0.25)
            noise_sd = base * r.uniform(0.10, 0.25)
            price = round(r.uniform(5, 120), 2)

            # a subset of products get a deliberate strong decline or strong growth
            regime = r.choice(["stable", "growth", "decline", "volatile"], p=[0.4, 0.25, 0.2, 0.15])
            if regime == "growth":
                trend_per_day = abs(trend_per_day) + base * 0.003
            elif regime == "decline":
                trend_per_day = -abs(trend_per_day) - base * 0.002
            elif regime == "volatile":
                noise_sd *= 2.0

            promo_days = set(r.choice(len(dates), size=max(1, len(dates) // 45), replace=False))

            inv = base * r.uniform(20, 70)  # starting inventory
            for i, d in enumerate(dates):
                seasonal = 1 + weekly_amp * np.sin(2 * np.pi * d.dayofweek / 7) \
                           + yearly_amp * np.sin(2 * np.pi * d.dayofyear / 365.25)
                level = base + trend_per_day * i
                demand = max(0, level * seasonal + r.normal(0, noise_sd))
                promo = i in promo_days
                if promo:
                    demand *= r.uniform(1.4, 2.2)
                qty = int(round(demand))

                inv = max(0, inv - qty)
                # periodic restock: every ~14-21 days, replenish toward a target
                if i % int(r.integers(14, 22)) == 0:
                    target = base * r.uniform(25, 45)
                    inv = max(inv, target)

                rows.append({
                    "date": d,
                    "product_id": f"P{product_id}",
                    "product_name": name,
                    "category": category,
                    "quantity": qty,
                    "price": price,
                    "revenue": round(qty * price, 2),
                    "promotion": bool(promo),
                    "inventory": int(round(inv)),
                    "lead_time": int(r.integers(3, 15)),
                })

    df = pd.DataFrame(rows)
    return df

if __name__ == "__main__":
    df = generate_sample_dataset()
    df.to_csv("sample_dataset.csv", index=False)
    print(f"Generated {len(df):,} rows across {df['product_id'].nunique()} products")
