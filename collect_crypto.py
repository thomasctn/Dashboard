# collect_crypto.py
import requests
import pandas as pd
import datetime
import os

# Liste de cryptos à récupérer
COINS = ["bitcoin", "ethereum", "cardano", "solana", "polkadot", "ripple", "litecoin", "dogecoin"]
CSV_FILE = "crypto_data.csv"

API_URL = "https://api.coingecko.com/api/v3/coins/markets"

def fetch_prices(coins):
    params = {
        "vs_currency": "eur",
        "ids": ",".join(coins),
        "order": "market_cap_desc",
        "per_page": len(coins),
        "page": 1,
        "sparkline": False,
        "price_change_percentage": "24h,7d"
    }
    r = requests.get(API_URL, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

def main():
    data = fetch_prices(COINS)
    now = datetime.datetime.utcnow().isoformat()

    rows = []
    for coin in data:
        rows.append({
            "time": now,
            "name": coin["id"],
            "price": coin.get("current_price"),
            "change_24h": coin.get("price_change_percentage_24h"),
            "change_7d": coin.get("price_change_percentage_7d_in_currency"),
            "market_cap": coin.get("market_cap")
        })

    df_new = pd.DataFrame(rows)

    # si le CSV existe déjà, concaténer
    if os.path.exists(CSV_FILE):
        df_old = pd.read_csv(CSV_FILE)
        df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df = df_new

    df.to_csv(CSV_FILE, index=False)
    print(f"✅ Données sauvegardées dans {CSV_FILE}")

if __name__ == "__main__":
    main()
