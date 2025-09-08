import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Dashboard Multi-domaines", layout="wide")
st.title("📊 Dashboard Global")

# ───────────────────────────────────────────────
# Onglets
tab1, tab2 = st.tabs(["💰 Crypto", "🎮 Steam"])

# ───────────────────────────────────────────────
# Onglet Crypto
with tab1:
    st.header("💰 Dashboard Crypto")

    CSV_FILE = "crypto_data.csv"

    if not os.path.exists(CSV_FILE):
        st.info("Pas de données. Lance collect_data.py au moins une fois pour créer crypto_data.csv")
        st.stop()

    df = pd.read_csv(CSV_FILE)
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time")

    # Filtre des cryptos directement dans l'onglet
    cryptos = sorted(df["name"].unique())
    selected = st.multiselect("Cryptos à afficher", cryptos, default=cryptos[:3])

    # Filtre période
    min_time = df["time"].min().to_pydatetime()
    max_time = df["time"].max().to_pydatetime()
    default_start = max_time - timedelta(days=7)

    start_time, end_time = st.slider(
        "Choisir la période",
        min_value=min_time,
        max_value=max_time,
        value=(default_start, max_time),
        format="YYYY-MM-DD HH:mm"
    )

    filtered = df[(df["time"] >= start_time) & (df["time"] <= end_time) & (df["name"].isin(selected))]

    # Choix des métriques
    metrics_options = ["Prix", "Variation 24h", "Variation 7j", "Market Cap"]
    selected_metrics = st.sidebar.multiselect("Métriques à afficher", metrics_options, default=["Prix"])

    filtered = df[(df["time"] >= start_time) & (df["time"] <= end_time) & (df["name"].isin(selected))]

    # Metrics
    st.subheader("📈 Indicateurs")
    cols = st.columns(len(selected) if selected else 1)
    for i, coin in enumerate(selected):
        sub = filtered[filtered["name"] == coin].sort_values("time")
        if sub.empty:
            cols[i].write(coin.upper())
            for metric in selected_metrics:
                cols[i].metric(metric, "—", delta="—")
            continue

        current = sub.iloc[-1]
        first = sub.iloc[0]

        # Prix
        if "Prix" in selected_metrics:
            delta = ((current["price"] - first["price"]) / first["price"] * 100) if first["price"] != 0 else 0
            cols[i].metric(label=coin.upper()+" Prix", value=f"{current['price']:.2f} €", delta=f"{delta:.2f}%")

        # Variation 24h
        if "Variation 24h" in selected_metrics and "change_24h" in sub.columns:
            cols[i].metric(label="Variation 24h", value=f"{current['change_24h']:.2f} %")

        # Variation 7j
        if "Variation 7j" in selected_metrics and "change_7d" in sub.columns:
            cols[i].metric(label="Variation 7j", value=f"{current['change_7d']:.2f} %")

        # Market Cap
        if "Market Cap" in selected_metrics and "market_cap" in sub.columns:
            cols[i].metric(label="Market Cap", value=f"{current['market_cap']:,} €")

    # Graphiques interactifs
    st.subheader("Graphiques des prix")
    if filtered.empty:
        st.info("Pas de données pour cette sélection/période.")
    else:
        fig = px.line(
            filtered,
            x="time",
            y="price",
            color="name",
            labels={"time": "Temps", "price": "Prix (€)"},
            title="Évolution des prix"
        )
        fig.update_layout(legend_title_text="Crypto")
        st.plotly_chart(fig, use_container_width=True)

    # Sparklines miniatures
    st.subheader("Mini-sparklines")
    for coin in selected:
        sub = filtered[filtered["name"] == coin].sort_values("time")
        if not sub.empty:
            spark = px.line(sub, x="time", y="price", height=100)
            st.write(coin.upper())
            st.plotly_chart(spark, use_container_width=True)

    # Tableau des données
    with st.expander("Voir les données brutes"):
        st.dataframe(filtered)

# ───────────────────────────────────────────────
# Onglet Steam
with tab2:
    st.header("🎮 Dashboard Steam — Jeux vidéo")

    STEAM_FILE = "steam_data.csv"

    if not os.path.exists(STEAM_FILE):
        st.info("Pas de données. Lance collect_data.py au moins une fois pour créer steam_data.csv")
        st.stop()

    df_steam = pd.read_csv(STEAM_FILE)
    # Convertir les dates et supprimer les lignes invalides
    df_steam["time"] = pd.to_datetime(df_steam["time"], errors="coerce")
    df_steam = df_steam.dropna(subset=["time"]).sort_values("time")

    # ─── champ spécifique à Steam ───
    apps = sorted(df_steam["name"].unique())
    selected_apps = st.multiselect("Choisir les jeux", apps, default=apps[:5])

    min_time = df_steam["time"].min().to_pydatetime()
    max_time = df_steam["time"].max().to_pydatetime()
    default_start = max_time - timedelta(days=7)

    start_time, end_time = st.slider(
        "Choisir la période Steam",
        min_value=min_time,
        max_value=max_time,
        value=(default_start, max_time),
        format="YYYY-MM-DD"
    )

    filtered_steam = df_steam[(df_steam["time"] >= start_time) & 
                              (df_steam["time"] <= end_time) & 
                              (df_steam["name"].isin(selected_apps))]

    filtered_steam = df_steam[(df_steam["time"] >= start_time) &
                              (df_steam["time"] <= end_time) &
                              (df_steam["name"].isin(selected_apps))]

    # Metrics
    st.subheader("📈 Indicateurs par jeu")
    cols = st.columns(len(selected_apps) if selected_apps else 1)
    for i, app in enumerate(selected_apps):
        sub = filtered_steam[filtered_steam["name"] == app].sort_values("time")
        if sub.empty:
            cols[i].write(app)
            cols[i].metric("Joueurs max", "—", delta="—")
            continue

        current = sub.iloc[-1]
        first = sub.iloc[0]

        # Joueurs max
        delta = ((current["players"] - first["players"]) / first["players"] * 100) if first["players"] != 0 else 0
        cols[i].metric(label=f"{app} — Joueurs max", value=f"{current['players']:,}", delta=f"{delta:.2f}%")

    # Graphiques interactifs
    st.subheader("Graphiques des joueurs")
    if filtered_steam.empty:
        st.info("Pas de données pour cette sélection/période.")
    else:
        fig = px.line(
            filtered_steam,
            x="time",
            y="players",
            color="name",  # afficher le nom du jeu
            labels={"time": "Temps", "players": "Joueurs simultanés", "name": "Jeu"},
            title="Évolution des joueurs"
        )
        fig.update_layout(legend_title_text="Jeu")
        st.plotly_chart(fig, use_container_width=True)

    # Sparklines miniatures
    st.subheader("Mini-sparklines")
    for app in selected_apps:
        sub = filtered_steam[filtered_steam["name"] == app].sort_values("time")
        if not sub.empty:
            spark = px.line(sub, x="time", y="players", height=100)
            st.write(app)
            st.plotly_chart(spark, use_container_width=True)

    # Tableau des données
    with st.expander("Voir les données brutes"):
        st.dataframe(filtered_steam)
