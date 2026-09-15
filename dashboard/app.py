import streamlit as st
import requests

st.set_page_config(
    page_title="BayanGuard",
    page_icon="shield",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }
    
    .main-header h1 {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0.3rem;
        letter-spacing: -0.5px;
    }
    
    .main-header p {
        font-size: 0.95rem;
        color: #64748b;
        font-weight: 400;
        margin-top: 0;
    }
    
    .shield-icon {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    
    .result-card {
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
    
    .result-high {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border: 1px solid #fca5a5;
    }
    
    .result-medium {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 1px solid #fbbf24;
    }
    
    .result-low {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border: 1px solid #34d399;
    }
    
    .risk-label {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 0.5rem;
    }
    
    .risk-percentage {
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        line-height: 1;
    }
    
    .risk-high .risk-label { color: #dc2626; }
    .risk-high .risk-percentage { color: #991b1b; }
    .risk-medium .risk-label { color: #d97706; }
    .risk-medium .risk-percentage { color: #92400e; }
    .risk-low .risk-label { color: #059669; }
    .risk-low .risk-percentage { color: #065f46; }
    
    .metric-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .metric-box {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #e2e8f0;
    }
    
    .metric-value {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.7rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.3rem;
    }
    
    .section-title {
        font-size: 0.8rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin: 1.5rem 0 0.8rem 0;
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        padding: 0.75rem;
        font-weight: 600;
        font-size: 1rem;
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: white;
        border: none;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #334155 0%, #475569 100%);
    }
    
    .api-status {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.8rem;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: 500;
    }
    
    .api-online {
        background: #d1fae5;
        color: #065f46;
    }
    
    .api-offline {
        background: #fee2e2;
        color: #991b1b;
    }
    
    .dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
    }
    
    .dot-online { background: #10b981; }
    .dot-offline { background: #ef4444; }
    
    .footer {
        text-align: center;
        padding: 2rem 0 1rem 0;
        color: #94a3b8;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('''
<div class="main-header">
    <div class="shield-icon">&#x1F6E1;</div>
    <h1>BayanGuard</h1>
    <p>Real-Time Fraud Detection for Philippine Fintech</p>
</div>
''', unsafe_allow_html=True)

api_online = False
try:
    r = requests.get("http://127.0.0.1:8000/health", timeout=2)
    if r.status_code == 200:
        api_online = True
except:
    pass

status_class = "api-online" if api_online else "api-offline"
dot_class = "dot-online" if api_online else "dot-offline"
status_text = "API Online" if api_online else "API Offline"

st.markdown(f'''
<div style="text-align: center; margin-bottom: 1.5rem;">
    <span class="api-status {status_class}">
        <span class="dot {dot_class}"></span>
        {status_text}
    </span>
</div>
''', unsafe_allow_html=True)

if not api_online:
    st.warning("Start the API first: python run_api.py")

st.markdown('<div class="section-title">Transaction Details</div>', unsafe_allow_html=True)

with st.form("tx_form", border=False):
    col1, col2 = st.columns(2)
    
    with col1:
        tx_id = st.text_input("Transaction ID", value="TXN_001")
        user_id = st.text_input("User ID", value="USR_001")
        ts = st.text_input("Timestamp", value="2024-06-15 02:30:00")
        amount = st.number_input("Amount (PHP)", min_value=0.0, value=8500.0, step=100.0)
        
    with col2:
        merchant = st.selectbox("Merchant", [
            "LBC Remittance", "Western Union", "Palawan Pawnshop",
            "Shopee", "Lazada", "Zalora PH",
            "Jollibee", "McDonald's", "KFC",
            "Puregold", "SM Supermarket", "Robinsons Supermarket",
            "Shell", "Petron", "Caltex",
            "GCash", "Maya", "PayMaya"
        ])
        
        category = st.selectbox("Category", [
            "remittance", "ecommerce", "food", "grocery", 
            "fuel", "ewallet", "bills", "transport", "entertainment"
        ])
    
    submitted = st.form_submit_button("Analyze Transaction")

if submitted and api_online:
    payload = {
        "transaction_id": tx_id,
        "user_id": user_id,
        "timestamp": ts,
        "amount": amount,
        "merchant": merchant,
        "category": category
    }
    
    try:
        with st.spinner("Analyzing..."):
            r = requests.post("http://127.0.0.1:8000/predict", json=payload, timeout=10).json()
        
        p = r["fraud_probability"]
        
        if p > 0.7:
            result_class = "result-high risk-high"
            risk_text = "High Risk"
            icon = "&#x1F6A8;"
        elif p > 0.3:
            result_class = "result-medium risk-medium"
            risk_text = "Medium Risk"
            icon = "&#x26A0;"
        else:
            result_class = "result-low risk-low"
            risk_text = "Low Risk"
            icon = "&#x2705;"
        
        st.markdown(f'''
        <div class="result-card {result_class}">
            <div class="risk-label">{icon} {risk_text}</div>
            <div class="risk-percentage">{p:.1%}</div>
            <p style="margin-top: 0.5rem; opacity: 0.7; font-size: 0.85rem;">Fraud Probability</p>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown(f'''
        <div class="metric-grid">
            <div class="metric-box">
                <div class="metric-value">{r["is_fraud"]}</div>
                <div class="metric-label">Fraud Flag</div>
            </div>
            <div class="metric-box">
                <div class="metric-value">{r["user_history_count"]}</div>
                <div class="metric-label">User History</div>
            </div>
            <div class="metric-box">
                <div class="metric-value">{r["model_raw_score"]:.1%}</div>
                <div class="metric-label">Model Score</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        with st.expander("View Raw Response"):
            st.json(r)
        
    except Exception as e:
        st.error(f"Prediction failed: {e}")

elif submitted and not api_online:
    st.error("Cannot analyze. API is not running.")
    st.info("Start it with: python run_api.py")

st.markdown('''
<div class="footer">
    BayanGuard &mdash; AI-Powered Fraud Detection for the Philippines<br>
    <span style="font-size: 0.7rem; opacity: 0.7;">Built with Python &middot; XGBoost &middot; FastAPI &middot; Streamlit</span>
</div>
''', unsafe_allow_html=True)
