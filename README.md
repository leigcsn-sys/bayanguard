<p align="center">
  <img src="https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/svgs/solid/shield-halved.svg" width="80" height="80" alt="BayanGuard Logo">
</p>

<h1 align="center">BayanGuard</h1>

<p align="center">
  <b>Real-Time Fraud Detection for Philippine Fintech</b><br>
  AI-powered transaction risk scoring with cold-start handling
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white" alt="Python 3.11">
  <img src="https://img.shields.io/badge/XGBoost-ML-%23EB5424?logo=xgboost&logoColor=white" alt="XGBoost">
  <img src="https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/scikit--learn-1.4-%23F7931E?logo=scikit-learn&logoColor=white" alt="scikit-learn">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
</p>

---

## What is BayanGuard?

BayanGuard is an end-to-end machine learning system that detects fraudulent financial transactions in real-time. Built specifically for the Philippine market, it handles:

- 100,000 synthetic transactions with realistic fraud patterns
- Cold-start users (new customers with no history)
- Real-time API scoring via FastAPI
- Interactive monitoring dashboard via Streamlit

## Architecture

```
Data Generator → Feature Engineering → XGBoost Model → FastAPI → Streamlit Dashboard
      |                |                     |
   100K rows      18 features         ROC AUC: 0.996
   1.5% fraud     No leakage          PR AUC: 0.66
```

## Model Performance

| Metric        | Score  | Status |
|---------------|--------|--------|
| ROC AUC       | 0.996  | Excellent |
| PR AUC        | 0.662  | Strong |
| Fraud Recall  | 97.3%  | Excellent |
| Cold-start    | Blended| Production-ready |

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate Data

```bash
python data/generate_synthetic.py
```

### 3. Engineer Features

```bash
python run_features.py
```

### 4. Train Model

```bash
python run_training.py
```

### 5. Start API Server

```bash
python run_api.py
```

### 6. Launch Dashboard (new terminal)

```bash
streamlit run dashboard/app.py
```

## API Example

**Endpoint:** `POST /predict`

**Request:**

```json
{
  "transaction_id": "TXN_001",
  "user_id": "USR_001",
  "timestamp": "2024-06-15 02:30:00",
  "amount": 8500.00,
  "merchant": "LBC Remittance",
  "category": "remittance"
}
```

**Response:**

```json
{
  "transaction_id": "TXN_001",
  "fraud_probability": 0.6652,
  "is_fraud": true,
  "risk_level": "MEDIUM",
  "model_raw_score": 0.0008,
  "user_history_count": 1
}
```

## Key Features

- **No Data Leakage:** Merchant fraud rates are computed properly without target contamination
- **Cold-Start Handling:** Heuristic rule blending for users with no transaction history
- **Real-Time Scoring:** Sub-100ms API response time
- **Interactive Dashboard:** Visual risk assessment with probability bars

## Tech Stack

| Layer        | Technology |
|--------------|------------|
| Language     | Python 3.11 |
| ML Model     | XGBoost |
| Preprocessing| pandas, NumPy, scikit-learn |
| API          | FastAPI, Uvicorn |
| Dashboard    | Streamlit |
| Data         | Synthetic (100K transactions) |

## Project Structure

```
bayanguard/
├── data/
│   ├── generate_synthetic.py
│   ├── transactions.csv
│   └── featured_transactions.csv
├── src/
│   ├── features/
│   │   └── engineering.py
│   ├── models/
│   │   └── train.py
│   └── api/
│       └── predict.py
├── dashboard/
│   └── app.py
├── model/
│   ├── fraud_model.pkl
│   └── feature_names.csv
├── run_features.py
├── run_training.py
├── run_api.py
├── requirements.txt
└── README.md
```

## Why This Matters

In the Philippines, digital payments and remittances are growing rapidly. Fraud detection systems must handle:

- High-value remittances at odd hours
- First-time users with no history
- Real-time decisions (approve/block)

BayanGuard demonstrates all three capabilities.

## License

MIT License. Built for portfolio and educational purposes.
