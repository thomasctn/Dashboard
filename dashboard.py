# dashboard.py
import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import os

st.set_page_config(page_title="Crypto Dashboard", layout="wide")
st.title("📊 Dashboard Crypto — Portfolio")

CSV_FILE = "crypto_data.csv"

if not os.path.exists(CSV_FILE):
    st.info("Pas de données. Lance collect_crypto.py au moins une fois pour créer crypto_data.csv")
    st.stop()

df = pd.read_csv(CSV_FILE)
df["time"] = pd.to_datetime(df["time"])
df = df.sort_values("time")

# Sidebar controls
st.sidebar.header("Filtres")
cryptos = sorted(df["name"].unique().tolist())
selected = st.sidebar.multiselect("Cryptos à afficher", cryptos, default=cryptos[:2])

period = st.sidebar.radio("Période", ["24h", "7j", "30j", "Tout"], index=1)

now = pd.Timestamp.utcnow().tz_localize(None)
if period == "24h":
    start_time = now - pd.Timedelta(days=1)
elif period == "7j":
    start_time = now - pd.Timedelta(days=7)
elif period == "30j":
    start_time = now - pd.Timedelta(days=30)
else:
    start_time = df["time"].min()

filtered = df[(df["time"] >= start_time) & (df["name"].isin(selected))]

# Metrics
st.subheader("📈 Indicateurs")
cols = st.columns(len(selected) if selected else 1)
for i, coin in enumerate(selected):
    sub = filtered[filtered["name"] == coin].sort_values("time")
    if sub.empty:
        cols[i].write(coin.upper())
        cols[i].metric("Prix actuel", "—", delta="—")
        continue
    current = sub.iloc[-1]["price"]
    first = sub.iloc[0]["price"]
    pct = ((current - first) / first * 100) if first != 0 else 0
    delta_str = f"{pct:.2f}%"
    cols[i].metric(label=coin.upper(), value=f"{current:.2f} €", delta=delta_str)

# Graph
st.subheader("Graphique des prix")
if filtered.empty:
    st.info("Pas de données pour cette sélection/période.")
else:
    fig = px.line(filtered, x="time", y="price", color="name",
                  labels={"time":"Temps","price":"Prix (€)"},
                  title="Évolution des prix")
    fig.update_layout(legend_title_text="Crypto")
    st.plotly_chart(fig, use_container_width=True)

# Table raw data
with st.expander("Voir les données brutes"):
    st.write(filtered.tail(50))
