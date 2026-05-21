import json
import urllib.request
from datetime import datetime
import streamlit as st

# ---------- PAGE SETUP ----------
st.set_page_config(page_title="Crypto Price Tracker", page_icon="🪙", layout="wide")

# Custom Dark styling to match your friend's original colors
st.html(
    """
    <style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    div[data-testid="metric-container"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 8px;
    }
    </style>
    """
)

# ---------- DATA FETCHING (Your Friend's Logic) ----------


def fetch_crypto_data():
    url = "https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH&tsyms=USD,JPY,EUR,PKR"
    try:
        with urllib.request.urlopen(url, timeout=6) as resp:
            prices = json.load(resp)
    except Exception:
        prices = {}

    btc = prices.get("BTC", {})
    eth = prices.get("ETH", {})

    # Fallback 1: direct PKR quotes from CoinGecko.
    pkr_fallback_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=pkr"
    try:
        with urllib.request.urlopen(pkr_fallback_url, timeout=6) as resp:
            fallback = json.load(resp)
        if btc.get("PKR") is None:
            btc["PKR"] = fallback.get("bitcoin", {}).get("pkr")
        if eth.get("PKR") is None:
            eth["PKR"] = fallback.get("ethereum", {}).get("pkr")
    except Exception:
        pass

    # Fallback 2: convert USD to PKR if direct PKR is still missing.
    if btc.get("PKR") is None or eth.get("PKR") is None:
        usd_pkr_url = "https://open.er-api.com/v6/latest/USD"
        try:
            with urllib.request.urlopen(usd_pkr_url, timeout=6) as resp:
                fx = json.load(resp)
            usd_to_pkr = fx.get("rates", {}).get("PKR")
            if usd_to_pkr:
                if btc.get("PKR") is None and btc.get("USD") is not None:
                    btc["PKR"] = round(btc["USD"] * usd_to_pkr, 2)
                if eth.get("PKR") is None and eth.get("USD") is not None:
                    eth["PKR"] = round(eth["USD"] * usd_to_pkr, 2)
        except Exception:
            pass

    prices["BTC"] = btc
    prices["ETH"] = eth
    return prices


def format_price(symbol, value):
    if value is None:
        return "N/A"
    if symbol == "USD":
        return f"${value:,}"
    if symbol == "JPY":
        return f"¥{value:,}"
    if symbol == "EUR":
        return f"€{value:,}"
    if symbol == "PKR":
        return f"Rs {value:,}"
    return f"{value:,}"


# ---------- STREAMLIT INTERFACE ----------

st.title("🪙 CRYPTO PRICE TRACKER")

try:
    response = fetch_crypto_data()
    btc = response.get("BTC", {})
    eth = response.get("ETH", {})
    current_time = datetime.now().strftime("%H:%M:%S")
    st.caption(f"Last Updated • {current_time}")
except Exception:
    st.error("⚠ Failed to fetch data")
    btc, eth = {}, {}

st.markdown("---")

# Layout Side-by-Side Columns
col1, col2 = st.columns(2)

with col1:
    st.header("₿ BITCOIN (BTC)")
    st.metric(label="USD", value=format_price("USD", btc.get("USD")))
    st.metric(label="JPY", value=format_price("JPY", btc.get("JPY")))
    st.metric(label="EUR", value=format_price("EUR", btc.get("EUR")))
    st.metric(label="PKR", value=format_price("PKR", btc.get("PKR")))

with col2:
    st.header("Ξ ETHEREUM (ETH)")
    st.metric(label="USD", value=format_price("USD", eth.get("USD")))
    st.metric(label="JPY", value=format_price("JPY", eth.get("JPY")))
    st.metric(label="EUR", value=format_price("EUR", eth.get("EUR")))
    st.metric(label="PKR", value=format_price("PKR", eth.get("PKR")))

st.markdown("---")

# Quick interactive refresh button for the grading expo team
if st.button("🔄 Click to Refresh Prices"):
    st.rerun()