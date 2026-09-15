import streamlit as st
import requests
import json

st.set_page_config(page_title="BayanGuard", page_icon="🛡️", layout="centered")

st.title("🛡️ BayanGuard")
st.subheader("Real-Time Fraud Detection Dashboard")
st.markdown("---")

# Input form
col1, col2 = st.columns(2)

with col1:
    transaction_id = st.text_input("Transaction ID", value="TXN_DEMO_001")
    user_id = st.text_input("User ID", value="USR_DEMO_001")
    timestamp = st.text_input("Timestamp", value="2024-06-15 02:30:00")
    
with col2:
    amount = st.number_input("Amount (PHP)", min_value=0.0, value=8500.0, step=100.0)
    merchant = st.selectbox("Merchant", [
        "LBC Remittance", "Western Union", "Palawan Pawnshop",
        "Lazada", "Shopee", "Zalora PH",
        "Jollibee", "McDonald's", "KFC",
        "Puregold", "SM Supermarket",
        "Shell", "Petron", "Caltex",
        "Mercury Drug", "Watsons",
        "Netflix PH", "Grab"
    ])
    category = st.selectbox("Category", [
        "remittance", "ecommerce", "food", "grocery", 
        "fuel", "pharmacy", "entertainment", "transport", "bills", "retail"
    ])

st.markdown("---")

if st.button("🔍 Check for Fraud", type="primary", use_container_width=True):
    with st.spinner("Analyzing transaction..."):
        payload = {
            "transaction_id": transaction_id,
            "user_id": user_id,
            "timestamp": timestamp,
            "amount": amount,
            "merchant": merchant,
            "category": category
        }
        
        try:
            response = requests.post(
                "http://127.0.0.1:8000/predict",
                json=payload,
                timeout=10
            )
            result = response.json()
            
            prob = result["fraud_probability"]
            
            # Risk display
            if prob > 0.7:
                st.error(f"### 🚨 HIGH RISK: {prob:.1%}")
                st.progress(prob, text="Fraud Probability")
            elif prob > 0.3:
                st.warning(f"### ⚠️ MEDIUM RISK: {prob:.1%}")
                st.progress(prob, text="Fraud Probability")
            else:
                st.success(f"### ✅ LOW RISK: {prob:.1%}")
                st.progress(prob, text="Fraud Probability")
            
            # Details
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Fraud Probability", f"{prob:.2%}")
            with col_b:
                st.metric("Model Raw Score", f"{result['model_raw_score']:.2%}")
            with col_c:
                st.metric("User History", result['user_history_count'])
            
            st.json(result)
            
        except Exception as e:
            st.error(f"Error connecting to API: {e}")
            st.info("Make sure the API is running: `python run_api.py`")

st.markdown("---")
st.caption("BayanGuard - AI-Powered Fraud Detection for the Philippines")