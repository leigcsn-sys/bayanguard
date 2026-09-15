import streamlit as st
import requests

st.set_page_config(page_title="BayanGuard", layout="centered")
st.title("BayanGuard Fraud Detection")

with st.form("tx_form"):
    col1, col2 = st.columns(2)
    with col1:
        tx_id = st.text_input("Transaction ID", "TXN_001")
        user_id = st.text_input("User ID", "USR_001")
        ts = st.text_input("Timestamp", "2024-06-15 02:30:00")
        amount = st.number_input("Amount (PHP)", 0.0, 100000.0, 8500.0)
    with col2:
        merchant = st.selectbox("Merchant", [
            "LBC Remittance", "Western Union", "Palawan Pawnshop",
            "Shopee", "Lazada", "Jollibee", "Puregold"
        ])
        category = st.selectbox("Category", [
            "remittance", "ecommerce", "food", "grocery", "fuel"
        ])
    submitted = st.form_submit_button("Check Fraud")

if submitted:
    payload = {
        "transaction_id": tx_id,
        "user_id": user_id,
        "timestamp": ts,
        "amount": amount,
        "merchant": merchant,
        "category": category
    }
    try:
        r = requests.post("http://127.0.0.1:8000/predict", json=payload, timeout=10).json()
        p = r["fraud_probability"]
        if p > 0.7:
            st.error(f"HIGH RISK: {p:.1%}")
        elif p > 0.3:
            st.warning(f"MEDIUM RISK: {p:.1%}")
        else:
            st.success(f"LOW RISK: {p:.1%}")
        st.json(r)
    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Start the API first: python run_api.py")