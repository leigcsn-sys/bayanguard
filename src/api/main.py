import uuid
import pandas as pd
from fastapi import FastAPI
from src.api.schemas import TransactionRequest, PredictionResponse
from src.features.engineering import engineer_features
import joblib
from pathlib import Path

app = FastAPI(title="BayanGuard API")

model_path = Path(__file__).parent.parent.parent / "model" / "fraud_model.pkl"
model = joblib.load(model_path)
feature_names = model.get_booster().feature_names

def heuristic_risk(amount, hour, category, merchant):
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

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict", response_model=PredictionResponse)
def predict(tx: TransactionRequest):
    df = pd.DataFrame([tx.model_dump()])
    df = engineer_features(df)
    
    drop_cols = ["transaction_id", "user_id", "timestamp", "merchant"]
    X = df.drop(columns=[c for c in drop_cols if c in df.columns])
    X = pd.get_dummies(X, drop_first=True)
    
    for col in feature_names:
        if col not in X.columns:
            X[col] = 0
    X = X[feature_names]
    
    model_proba = model.predict_proba(X)[0][1]
    cust_count = float(df["cust_tx_count"].iloc[0])
    
    if cust_count <= 2:
        h = heuristic_risk(tx.amount, df["hour"].iloc[0], tx.category, tx.merchant)
        final_proba = 0.7 * h + 0.3 * model_proba
    else:
        final_proba = model_proba
    
    pred = final_proba > 0.5
    
    return PredictionResponse(
        transaction_id=tx.transaction_id or str(uuid.uuid4()),
        fraud_probability=round(float(final_proba), 4),
        is_fraud=bool(pred),
        risk_level="HIGH" if final_proba > 0.7 else "MEDIUM" if final_proba > 0.3 else "LOW",
        model_raw_score=round(float(model_proba), 4),
        user_history_count=int(cust_count)
    )