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


def heuristic_risk(amount, hour, day_of_week, category, merchant, cust_count):
    """
    Improved cold-start heuristic with category-specific thresholds,
    weekend/night multipliers, and merchant-category mismatch detection.
    """
    score = 0.03  # Base risk slightly lower

    # === Amount risk (category-aware thresholds) ===
    cat_amount_thresholds = {
        "remittance": 4000,
        "ecommerce": 3000,
        "fuel": 2500,
        "bills": 3500,
        "food": 800,
        "grocery": 2000,
        "pharmacy": 1500,
        "retail": 2500,
        "entertainment": 1000,
        "transport": 500,
    }
    threshold = cat_amount_thresholds.get(category, 2000)

    if amount > threshold * 3:
        score += 0.30
    elif amount > threshold * 2:
        score += 0.18
    elif amount > threshold * 1.5:
        score += 0.08
    elif amount > threshold:
        score += 0.03

    # === Time-based risk ===
    if hour <= 4:
        score += 0.28
    elif hour >= 23:
        score += 0.14
    elif 0 <= hour <= 5:
        score += 0.10

    # Weekend + night combo is extra suspicious
    if day_of_week >= 5 and hour <= 5:
        score += 0.12

    # === Category risk ===
    cat_risk = {
        "remittance": 0.12,
        "ecommerce": 0.06,
        "fuel": 0.04,
        "bills": 0.03,
        "food": 0.01,
        "grocery": 0.01,
        "pharmacy": 0.01,
        "retail": 0.01,
        "entertainment": 0.02,
        "transport": 0.01,
    }
    score += cat_risk.get(category, 0.02)

    # === Merchant risk ===
    high_risk_merchants = {
        "LBC Remittance": 0.10,
        "Western Union": 0.10,
        "Palawan Pawnshop": 0.10,
        "Shopee": 0.04,
        "Lazada": 0.04,
        "Zalora PH": 0.03,
    }
    score += high_risk_merchants.get(merchant, 0.0)

    # === Merchant-Category mismatch detection ===
    # e.g., "Jollibee" with category "remittance" is suspicious
    merchant_category_map = {
        "Jollibee": "food", "McDonald's": "food", "KFC": "food", "Chowking": "food",
        "Puregold": "grocery", "SM Supermarket": "grocery", "Robinsons Supermarket": "grocery",
        "Shell": "fuel", "Petron": "fuel", "Caltex": "fuel", "Seaoil": "fuel",
        "Lazada": "ecommerce", "Shopee": "ecommerce", "Zalora PH": "ecommerce",
        "LBC Remittance": "remittance", "Western Union": "remittance", "Palawan Pawnshop": "remittance",
        "Netflix PH": "entertainment", "Spotify PH": "entertainment",
        "Grab": "transport", "Angkas": "transport",
        "Meralco": "bills", "Maynilad": "bills", "PLDT": "bills", "Globe": "bills",
        "Mercury Drug": "pharmacy", "Watsons": "pharmacy",
        "Bench": "retail", "Uniqlo": "retail", "H&M": "retail",
    }
    expected_category = merchant_category_map.get(merchant)
    if expected_category and category != expected_category:
        score += 0.25  # Strong signal of fraud

    # === New user penalty ===
    # Brand new users (0-1 transactions) are inherently riskier
    if cust_count == 0:
        score += 0.08
    elif cust_count == 1:
        score += 0.04

    return min(score, 0.95)


def compute_blend_ratio(cust_count):
    """
    Dynamic blending: more history = more model, less heuristic.
    0 tx  -> 90% heuristic, 10% model
    1 tx  -> 80% heuristic, 20% model
    2 tx  -> 70% heuristic, 30% model (your original)
    3-5   -> 50% heuristic, 50% model
    6-10  -> 30% heuristic, 70% model
    11+   -> 10% heuristic, 90% model
    """
    if cust_count == 0:
        return 0.90
    elif cust_count == 1:
        return 0.80
    elif cust_count == 2:
        return 0.70
    elif cust_count <= 5:
        return 0.50
    elif cust_count <= 10:
        return 0.30
    else:
        return 0.10


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
    cust_count = int(df["cust_tx_count"].iloc[0])
    day_of_week = int(df["day_of_week"].iloc[0])

    # Cold-start blend with dynamic ratio
    blend_ratio = compute_blend_ratio(cust_count)
    h = heuristic_risk(
        tx.amount, df["hour"].iloc[0], day_of_week,
        tx.category, tx.merchant, cust_count
    )
    final_proba = blend_ratio * h + (1 - blend_ratio) * model_proba

    pred = final_proba > 0.5

    return PredictionResponse(
        transaction_id=tx.transaction_id or str(uuid.uuid4()),
        fraud_probability=round(float(final_proba), 4),
        is_fraud=bool(pred),
        risk_level="HIGH" if final_proba > 0.7 else "MEDIUM" if final_proba > 0.3 else "LOW",
        model_raw_score=round(float(model_proba), 4),
        user_history_count=cust_count
    )