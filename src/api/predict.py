import pandas as pd
import joblib
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from features.engineering import engineer_features

app = FastAPI(title="BayanGuard Fraud Detection API")

model_path = Path(__file__).parent.parent.parent / "model" / "fraud_model.pkl"
model = joblib.load(model_path)
feature_names = model.get_booster().feature_names

class Transaction(BaseModel):
    transaction_id: str
    user_id: str
    timestamp: str
    amount: float
    merchant: str
    category: str

def heuristic_risk(amount, hour, category, merchant):
    """Rule-based risk score for cold-start users (no history)."""
    score = 0.05
    
    if amount > 4000:
        score += 0.35
    elif amount > 2500:
        score += 0.20
    elif amount > 1500:
        score += 0.08
    
    if hour <= 4:
        score += 0.30
    elif hour >= 23:
        score += 0.15
    
    if category == "remittance":
        score += 0.15
    elif category == "ecommerce":
        score += 0.05
    
    if merchant in ["LBC Remittance", "Western Union", "Palawan Pawnshop"]:
        score += 0.10
    
    return min(score, 0.95)

@app.get("/")
def root():
    return {"message": "BayanGuard API is running"}

@app.post("/predict")
def predict(transaction: Transaction):
    df = pd.DataFrame([transaction.model_dump()])
    df = engineer_features(df)
    
    drop_cols = ["transaction_id", "user_id", "timestamp", "merchant"]
    X = df.drop(columns=[c for c in drop_cols if c in df.columns])
    X = pd.get_dummies(X, drop_first=True)
    
    for col in feature_names:
        if col not in X.columns:
            X[col] = 0
    X = X[feature_names]
    
    model_proba = model.predict_proba(X)[0][1]
    
    # Cold-start blend: if user has few transactions, mix with heuristic
    cust_count = float(df["cust_tx_count"].iloc[0])
    if cust_count <= 2:
        # 70% heuristic, 30% model for brand new users
        h = heuristic_risk(transaction.amount, df["hour"].iloc[0], 
                            transaction.category, transaction.merchant)
        final_proba = 0.7 * h + 0.3 * model_proba
    else:
        final_proba = model_proba
    
    pred = int(final_proba > 0.5)
    
    return {
        "transaction_id": transaction.transaction_id,
        "fraud_probability": round(float(final_proba), 4),
        "is_fraud": bool(pred),
        "risk_level": "HIGH" if final_proba > 0.7 else "MEDIUM" if final_proba > 0.3 else "LOW",
        "model_raw_score": round(float(model_proba), 4),
        "user_history_count": int(cust_count)
    }