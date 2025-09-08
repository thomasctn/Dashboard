# collect_crypto.py
import requests
import pandas as pd
import datetime
import os

COINS = ["bitcoin", "ethereum", "cardano"]  # ajoute d’autres cryptos si tu veux
CSV_FILE = "crypto_data.csv"

API_URL = "https://api.coingecko.com/api/v3/simple/price"

def fetch_prices(coins):
    params = {
        "ids": ",".join(coins),
        "vs_currencies": "eur"
    }
    r = requests.get(API_URL, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

def main():
    data = fetch_prices(COINS)
    now = datetime.datetime.utcnow().isoformat()
    
    # transformer en DataFrame
    rows = []
    for coin, values in data.items():
        rows.append({"time": now, "name": coin, "price": values.get("eur")})
    df_new = pd.DataFrame(rows)

    # si le CSV existe déjà, on concatène
    if os.path.exists(CSV_FILE):
        df_old = pd.read_csv(CSV_FILE)
        df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df = df_new

    df.to_csv(CSV_FILE, index=False)
    print(f"✅ Données sauvegardées dans {CSV_FILE}")

if __name__ == "__main__":
    main()
