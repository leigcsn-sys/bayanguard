from pydantic import BaseModel
from typing import Optional

class TransactionRequest(BaseModel):
    transaction_id: Optional[str] = None
    user_id: str
    timestamp: str
    amount: float
    merchant: str
    category: str

class PredictionResponse(BaseModel):
    transaction_id: str
    fraud_probability: float
    is_fraud: bool
    risk_level: str
    model_raw_score: float
    user_history_count: int