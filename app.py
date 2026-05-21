import streamlit as st
import urllib.request
import json
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Crypto Price Tracker", page_icon="🪙", layout="wide")

# Custom Dark styling
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    div[data-testid="metric-container"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 8px;
    }
    </style>
""", unsafe_html=True)

# ---------- DATA FETCHING ----------
def fetch_crypto_data():
    url = "https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH&tsyms=USD,JPY,EUR,PKR"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception:
        return {}

# Fetch prices
live_data = fetch_crypto_data()

# Fallbacks if API is rate-limited
fallback_btc = {"USD": 67250, "JPY": 10520000, "EUR": 62100, "PKR": 18700000}
fallback_eth = {"USD": 3520, "JPY": 550000, "EUR": 3250, "PKR": 980000}

btc = live_data.get("BTC", fallback_btc)
eth = live_data.get("ETH", fallback_eth)

# ---------- UI DESIGN ----------
st.title("🪙 CRYPTO PRICE TRACKER")
notice = "🟢 Live Prices Operational" if live_data else "⚠️ Using Backup Data"
st.caption(f"{notice} • Last Checked: {datetime.now().strftime('%H:%M:%S')}")

st.markdown("---")

# Layout Columns
col1, col2 = st.columns(2)

with col1:
    st.header("⚡ BITCOIN (BTC)")
    st.metric(label="USD Price", value=f"${btc.get('USD'):,}")
    st.metric(label="JPY Price", value=f"¥{btc.get('JPY'):,}")
    st.metric(label="EUR Price", value=f"€{btc.get('EUR'):,}")
    st.metric(label="PKR Price", value=f"Rs {btc.get('PKR'):,}")

with col2:
    st.header("🔷 ETHEREUM (ETH)")
    st.metric(label="USD Price", value=f"${eth.get('USD'):,}")
    st.metric(label="JPY Price", value=f"¥{eth.get('JPY'):,}")
    st.metric(label="EUR Price", value=f"€{eth.get('EUR'):,}")
    st.metric(label="PKR Price", value=f"Rs {eth.get('PKR'):,}")

st.markdown("---")
st.caption("IM JUST HOSTING IT IM NOT TAKING ANY OF THE CREDITS FOR THE SOURCE CODE.")

# Auto-refresh button for the user
if st.button("🔄 Refresh Prices"):
    st.rerun()