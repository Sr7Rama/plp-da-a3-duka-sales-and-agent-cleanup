import numpy as np
import pandas as pd

def generate_data():
    rng = np.random.default_rng(44)
    n = 600

    # Generate agent registry
    agents = pd.DataFrame({
        "agent_id": [f"AG{i:03d}" for i in range(1, 21)],
        "county": rng.choice(["Nairobi", "Kiambu", "Nakuru", "Mombasa", "Kisumu"], 20),
        "onboarded": pd.date_range("2024-01-01", periods=20, freq="MS").strftime("%Y-%m-%d"),
    })

    # Generate transaction database
    txns = pd.DataFrame({
        "txn_id": [f"TX{i:05d}" for i in range(1, n + 1)],
        "agent_id": rng.choice(agents["agent_id"], n),
        "txn_type": rng.choice(["Deposit", "withdrawal", "DEPOSIT ", "Withdrawal", "deposit"], n),
        "amount": rng.lognormal(7.5, 0.8, n).round(0).astype(str),
        "txn_date": (pd.to_datetime("2026-03-01") + pd.to_timedelta(rng.integers(0, 60, n), unit="D")).strftime("%Y-%m-%d"),
    })

    # Inject specific defects for auditing demonstration
    idx = rng.choice(n, 30, replace=False)
    txns.loc[idx[:15], "amount"] = np.nan
    txns.loc[idx[15:20], "amount"] = "N/A"
    txns.loc[idx[20:25], "amount"] = "250000"
    txns.loc[idx[25:], "txn_date"] = txns.loc[idx[25:], "txn_date"].str.replace("-", "/")

    # Inject duplicates
    txns = pd.concat([txns, txns.sample(12, random_state=1)], ignore_index=True)

    # Inject unknown agent IDs
    txns.loc[rng.choice(len(txns), 8, replace=False), "agent_id"] = "AG099"

    agents.to_csv("agents.csv", index=False)
    txns.to_csv("agent_transactions.csv", index=False)

    # 2. Generate Duka Electronics Dataset (Seed 2026)
# Re-seeding numpy generator for Duka Sales dataset generation
duka_rng = np.random.default_rng(2026)
d_n = 1000

duka_sales = pd.DataFrame({
    "order_id": [f"DK{i:05d}" for i in range(1, d_n + 1)],
    "order_date": (pd.to_datetime("2026-01-01") + pd.to_timedelta(duka_rng.integers(0, 181, d_n), unit="D")).strftime("%Y-%m-%d"),
    "branch": duka_rng.choice(["Nairobi", "Mombasa", "Kisumu", "Nakuru"], d_n, p=[0.4, 0.25, 0.2, 0.15]),
    "product_name": duka_rng.choice(["Smart TV", "Smartphone", "Laptop", "Soundbar", "Wireless Headphones"], d_n, p=[0.15, 0.3, 0.2, 0.15, 0.2]),
    "quantity": duka_rng.choice([1, 2, 3], d_n, p=[0.7, 0.2, 0.1]),
    "unit_price_kes": duka_rng.choice([35000, 15000, 55000, 8000, 3500], d_n, p=[0.15, 0.3, 0.2, 0.15, 0.2]),
    "channel": duka_rng.choice(["In-Store", "Online"], d_n, p=[0.55, 0.45])
})
duka_sales.to_csv("duka_sales.csv", index=False)
print("Generated datasets: duka_sales.csv, agents.csv, agent_transactions.csv successfully!")

generate_data()