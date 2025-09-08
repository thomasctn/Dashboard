import requests
import pandas as pd
import datetime
import os

# ==============================
# 🔹 Partie Crypto
# ==============================
COINS = ["bitcoin", "ethereum", "cardano", "solana", "polkadot", "ripple", "litecoin", "dogecoin"]
CRYPTO_FILE = "crypto_data.csv"
CRYPTO_API = "https://api.coingecko.com/api/v3/coins/markets"

def fetch_crypto():
    params = {
        "vs_currency": "eur",
        "ids": ",".join(COINS),
        "order": "market_cap_desc",
        "per_page": len(COINS),
        "page": 1,
        "sparkline": False,
        "price_change_percentage": "24h,7d"
    }
    r = requests.get(CRYPTO_API, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

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
    return pd.DataFrame(rows)

def save_crypto(df_new):
    if os.path.exists(CRYPTO_FILE):
        df_old = pd.read_csv(CRYPTO_FILE)
        df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df = df_new
    df.to_csv(CRYPTO_FILE, index=False)
    print(f"✅ Crypto sauvegardé dans {CRYPTO_FILE}")

# ==============================
# 🔹 Partie Steam
# ==============================
STEAM_FILE = "steam_data.csv"
STEAM_API = "https://api.steampowered.com/ISteamChartsService/GetMostPlayedGames/v1/"

def fetch_steam():
    r = requests.get(STEAM_API, timeout=10)
    r.raise_for_status()
    data = r.json()["response"]["ranks"]
    print(data)  # 👈 voir la structure exacte

    now = datetime.datetime.utcnow().isoformat()
    rows = []
    for g in data:
        rows.append({
            "time": now,
            "appid": g.get("appid"),
            "rank": g.get("rank"),
            "last_week_rank": g.get("last_week_rank"),
            "players": g.get("peak_in_game")  # anciennement 'concurrent_in_game'
        })
    return pd.DataFrame(rows)

def save_steam(df_new):
    if os.path.exists(STEAM_FILE):
        df_old = pd.read_csv(STEAM_FILE)
        df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df = df_new
    df.to_csv(STEAM_FILE, index=False)
    print(f"✅ Steam sauvegardé dans {STEAM_FILE}")

# ==============================
# 🔹 Main
# ==============================
def main():
    try:
        df_crypto = fetch_crypto()
        save_crypto(df_crypto)
    except Exception as e:
        print(f"❌ Erreur Crypto: {e}")

    try:
        df_steam = fetch_steam()
        save_steam(df_steam)
    except Exception as e:
        print(f"❌ Erreur Steam: {e}")

if __name__ == "__main__":
    main()
