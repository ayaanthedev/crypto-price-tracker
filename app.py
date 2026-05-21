import json
import tkinter as tk
import urllib.request
from datetime import datetime

# ---------- FUNCTION ----------


def fetch_crypto_data():
    url = "https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH&tsyms=USD,JPY,EUR,PKR"
    with urllib.request.urlopen(url, timeout=6) as resp:
        prices = json.load(resp)

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


def track_crypto():
    try:
        response = fetch_crypto_data()

        btc = response.get("BTC", {})
        eth = response.get("ETH", {})

        time = datetime.now().strftime("%H:%M:%S")

        btc_usd_label.config(text=format_price("USD", btc.get("USD")))
        btc_jpy_label.config(text=format_price("JPY", btc.get("JPY")))
        btc_eur_label.config(text=format_price("EUR", btc.get("EUR")))
        btc_pkr_label.config(text=format_price("PKR", btc.get("PKR")))

        eth_usd_label.config(text=format_price("USD", eth.get("USD")))
        eth_jpy_label.config(text=format_price("JPY", eth.get("JPY")))
        eth_eur_label.config(text=format_price("EUR", eth.get("EUR")))
        eth_pkr_label.config(text=format_price("PKR", eth.get("PKR")))

        status_label.config(text=f"Last Updated • {time}", fg="#8b949e")

    except Exception:
        status_label.config(text="⚠ Failed to fetch data", fg="red")

    root.after(10000, track_crypto)


# ---------- WINDOW ----------
root = tk.Tk()
root.title("Crypto Tracker (BTC + ETH)")
root.geometry("1100x560")
root.config(bg="#0d1117")
root.resizable(False, False)

# ---------- FONTS ----------
title_font = ("Consolas", 26, "bold")
label_font = ("Consolas", 14)
price_font = ("Consolas", 22, "bold")
status_font = ("Consolas", 10)

# ---------- TITLE ----------
title = tk.Label(
    root,
    text="CRYPTO PRICE TRACKER",
    font=title_font,
    bg="#0d1117",
    fg="#f2a900"
)
title.pack(pady=20)

#    SIDE-BY-SIDE CONTAINER
cards_container = tk.Frame(root, bg="#0d1117")
cards_container.pack(padx=30, pady=8, fill="both", expand=True)

cards_container.grid_columnconfigure(0, weight=1)
cards_container.grid_columnconfigure(1, weight=1)
cards_container.grid_rowconfigure(0, weight=1)

btc_card = tk.Frame(cards_container, bg="#161b22", bd=0)
btc_card.grid(row=0, column=0, padx=10, sticky="nsew")

eth_card = tk.Frame(cards_container, bg="#161b22", bd=0)
eth_card.grid(row=0, column=1, padx=10, sticky="nsew")


def price_row(parent, text, color):
    frame = tk.Frame(parent, bg="#161b22")
    frame.pack(pady=8)

    label = tk.Label(frame, text=text, font=label_font,
                     bg="#161b22", fg="#8b949e")
    label.pack()

    price = tk.Label(frame, text="---", font=price_font,
                     bg="#161b22", fg=color)
    price.pack()

    return price


btc_title = tk.Label(
    btc_card,
    text="₿ BITCOIN (BTC)",
    font=label_font,
    bg="#161b22",
    fg="#f2a900"
)
btc_title.pack(pady=(14, 4))

btc_usd_label = price_row(btc_card, "USD", "#00ff99")
btc_jpy_label = price_row(btc_card, "JPY", "#58a6ff")
btc_eur_label = price_row(btc_card, "EUR", "#ff7b72")
btc_pkr_label = price_row(btc_card, "PKR", "#d2a8ff")

eth_title = tk.Label(
    eth_card,
    text="Ξ ETHEREUM (ETH)",
    font=label_font,
    bg="#161b22",
    fg="#79c0ff"
)
eth_title.pack(pady=(14, 4))

eth_usd_label = price_row(eth_card, "USD", "#00ff99")
eth_jpy_label = price_row(eth_card, "JPY", "#58a6ff")
eth_eur_label = price_row(eth_card, "EUR", "#ff7b72")
eth_pkr_label = price_row(eth_card, "PKR", "#d2a8ff")

#    STATUS
status_label = tk.Label(
    root,
    text="Loading...",
    font=status_font,
    bg="#0d1117",
    fg="#8b949e"
)
status_label.pack(pady=15)


track_crypto()
root.mainloop()
