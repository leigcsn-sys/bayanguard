import pandas as pd
import numpy as np

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    time_col = "transaction_timestamp" if "transaction_timestamp" in df.columns else "timestamp"
    if time_col in df.columns:
        df[time_col] = pd.to_datetime(df[time_col])
        df["hour"] = df[time_col].dt.hour
        df["day_of_week"] = df[time_col].dt.dayofweek
        df["is_night"] = (df["hour"] <= 5).astype(int)
        df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    amt_col = "transaction_amount" if "transaction_amount" in df.columns else "amount"
    if amt_col in df.columns:
        df["amount_log"] = np.log1p(df[amt_col].clip(lower=0))

    cust_col = "customer_id" if "customer_id" in df.columns else "user_id"
    if cust_col in df.columns:
        df["cust_tx_count"] = df.groupby(cust_col)[amt_col].transform("count")
        df["cust_mean_amt"] = df.groupby(cust_col)[amt_col].transform("mean")
        df["cust_std_amt"] = df.groupby(cust_col)[amt_col].transform("std").fillna(0)
        df["amt_vs_cust_mean"] = df[amt_col] / (df["cust_mean_amt"] + 1e-9)
        df["amt_zscore"] = (df[amt_col] - df["cust_mean_amt"]) / (df["cust_std_amt"] + 1e-9)

    merch_col = "merchant_id" if "merchant_id" in df.columns else "merchant"
    if merch_col in df.columns:
        df["merchant_tx_count"] = df.groupby(merch_col)[amt_col].transform("count")

    return df.fillna(0)