import pandas as pd
import numpy as np

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    time_col = "transaction_timestamp" if "transaction_timestamp" in df.columns else "timestamp"
    if time_col in df.columns:
        df[time_col] = pd.to_datetime(df[time_col])
        df = df.sort_values(time_col, kind="stable")
        df["hour"] = df[time_col].dt.hour
        df["day_of_week"] = df[time_col].dt.dayofweek
        df["is_night"] = (df["hour"] <= 5).astype(int)
        df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    amt_col = "transaction_amount" if "transaction_amount" in df.columns else "amount"
    if amt_col in df.columns:
        df["amount_log"] = np.log1p(df[amt_col].clip(lower=0))

    cust_col = "customer_id" if "customer_id" in df.columns else "user_id"
    if cust_col in df.columns:
        customer_amounts = df.groupby(cust_col, sort=False)[amt_col]
        df["cust_tx_count"] = customer_amounts.cumcount()
        df["cust_mean_amt"] = customer_amounts.transform(
            lambda values: values.shift().expanding().mean()
        )
        df["cust_std_amt"] = customer_amounts.transform(
            lambda values: values.shift().expanding().std()
        )
        df["amt_vs_cust_mean"] = df[amt_col] / (df["cust_mean_amt"] + 1e-9)
        df["amt_zscore"] = (df[amt_col] - df["cust_mean_amt"]) / (df["cust_std_amt"] + 1e-9)

    return df.fillna(0)