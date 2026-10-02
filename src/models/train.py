import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, roc_auc_score, average_precision_score
import xgboost as xgb
import joblib
from pathlib import Path

def main():
    df = pd.read_csv("data/featured_transactions.csv")
    
    target_col = "is_fraud" if "is_fraud" in df.columns else "fraud"
    y = df[target_col]
    
    drop_cols = [target_col, "transaction_id", "user_id", "timestamp"]
    if "merchant" in df.columns:
        drop_cols.append("merchant")
    
    X = df.drop(columns=[c for c in drop_cols if c in df.columns])
    X = pd.get_dummies(X, drop_first=True)
    
    time_col = "transaction_timestamp" if "transaction_timestamp" in df.columns else "timestamp"
    chronological_order = df[time_col].pipe(pd.to_datetime).sort_values(kind="stable").index
    split_at = int(len(chronological_order) * 0.8)
    train_idx, test_idx = chronological_order[:split_at], chronological_order[split_at:]
    X_train, X_test = X.loc[train_idx], X.loc[test_idx]
    y_train, y_test = y.loc[train_idx], y.loc[test_idx]
    
    fraud_count = y_train.sum()
    scale_pos_weight = (len(y_train) - fraud_count) / fraud_count if fraud_count > 0 else 1
    
    print(f"Training samples: {len(X_train)}")
    print(f"Fraud ratio: {y_train.mean():.4f}")
    print(f"Features: {X.shape[1]}")
    
    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        eval_metric="aucpr",
        random_state=42,
        n_jobs=4,
    )
    
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    
    print("\n--- Classification Report ---")
    print(classification_report(y_test, y_pred, digits=4))
    
    roc = roc_auc_score(y_test, y_proba)
    pr = average_precision_score(y_test, y_proba)
    print(f"ROC AUC: {roc:.4f}")
    print(f"PR AUC:  {pr:.4f}")
    
    Path("model").mkdir(exist_ok=True)
    joblib.dump(model, "model/fraud_model.pkl")
    pd.Series(X.columns).to_csv("model/feature_names.csv", index=False)
    print("\nModel saved to model/fraud_model.pkl")

if __name__ == "__main__":
    main()