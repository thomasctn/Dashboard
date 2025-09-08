import streamlit as st
import pandas as pd
import requests
import os
import plotly.express as px

st.set_page_config(page_title="Steam Dashboard", layout="wide")
st.title("🎮 Dashboard Steam — Jeux les plus joués")

CSV_FILE = "steam_data.csv"

if not os.path.exists(CSV_FILE):
    st.info("Pas de données. Lance collect_steam.py au moins une fois.")
    st.stop()

df = pd.read_csv(CSV_FILE)
df["time"] = pd.to_datetime(df["time"])
df = df.sort_values("time")

# Traduction appid -> nom
@st.cache_data
def get_game_name(appid):
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=fr&l=fr"
    r = requests.get(url, timeout=10)
    try:
        data = r.json()[str(appid)]["data"]
        return data["name"]
    except Exception:
        return str(appid)

df["name"] = df["appid"].apply(get_game_name)

# Sidebar filtres
st.sidebar.header("Filtres")
top_n = st.sidebar.slider("Top N jeux", 5, 20, 10)

latest = df[df["time"] == df["time"].max()]
top_games = latest.sort_values("players", ascending=False).head(top_n)

# Metrics
st.subheader("📈 Jeux les plus joués actuellement")
cols = st.columns(len(top_games))
for i, row in enumerate(top_games.itertuples()):
    cols[i].metric(row.name, f"{row.players:,} joueurs", f"Rang {row.rank}")

# Graph
st.subheader("📊 Évolution des joueurs")
fig = px.line(df, x="time", y="players", color="name",
              title="Évolution du nombre de joueurs par jeu")
st.plotly_chart(fig, use_container_width=True)

# Table brute
with st.expander("Voir les données brutes"):
    st.dataframe(df.tail(50))
