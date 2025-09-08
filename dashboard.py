import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Dashboard Multi-domaines", layout="wide")
st.title("📊 Dashboard Global")

# ───────────────────────────────────────────────
# Onglets
tab1, tab2, tab3 = st.tabs(["💰 Crypto", "🎮 Steam","Youtube"])

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

    # Trie les cryptos par prix décroissant
    latest_prices = df.groupby("name")["price"].last()  # dernier prix connu
    cryptos_sorted = latest_prices.sort_values(ascending=False).index.tolist()

    selected = st.multiselect(
        "Cryptos à afficher",
        cryptos_sorted,          # liste triée par prix décroissant
        default=cryptos_sorted[:3]  # préselection des 3 plus chères
    )

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

    # Trie les jeux par nombre maximum de joueurs
    latest_players = df_steam.groupby("name")["players"].max()
    apps_sorted = latest_players.sort_values(ascending=False).index.tolist()

    selected_apps = st.multiselect(
        "Choisir les jeux",
        apps_sorted,           # liste triée par joueurs max décroissant
        default=apps_sorted[:5]  # préselection des 5 plus joués
    )

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

# ───────────────────────────────────────────────
# Onglet YouTube
tab3 = st.tab("📺 YouTube")  # Ajouter un troisième onglet
with tab3:
    st.header("📺 Dashboard YouTube — Chaînes populaires")

    YT_FILE = "youtube_data.csv"

    if not os.path.exists(YT_FILE):
        st.info("Pas de données. Lance collect_data_youtube.py au moins une fois pour créer youtube_data.csv")
        st.stop()

    df_yt = pd.read_csv(YT_FILE)
    df_yt["time"] = pd.to_datetime(df_yt["time"], errors="coerce")
    df_yt = df_yt.dropna(subset=["time"]).sort_values("time")

    # Trier par nombre d'abonnés décroissant
    latest_subs = df_yt.groupby("name")["subscribers"].last()
    channels_sorted = latest_subs.sort_values(ascending=False).index.tolist()

    selected_channels = st.multiselect(
        "Choisir les chaînes",
        channels_sorted,
        default=channels_sorted[:5]  # préselection des 5 plus populaires
    )

    # Filtre période
    min_time = df_yt["time"].min().to_pydatetime()
    max_time = df_yt["time"].max().to_pydatetime()
    default_start = max_time - timedelta(days=7)

    start_time, end_time = st.slider(
        "Choisir la période YouTube",
        min_value=min_time,
        max_value=max_time,
        value=(default_start, max_time),
        format="YYYY-MM-DD"
    )

    filtered_yt = df_yt[(df_yt["time"] >= start_time) &
                        (df_yt["time"] <= end_time) &
                        (df_yt["name"].isin(selected_channels))]

    # Metrics
    st.subheader("📈 Indicateurs par chaîne")
    cols = st.columns(len(selected_channels) if selected_channels else 1)
    for i, channel in enumerate(selected_channels):
        sub = filtered_yt[filtered_yt["name"] == channel].sort_values("time")
        if sub.empty:
            cols[i].write(channel)
            cols[i].metric("Abonnés", "—", delta="—")
            cols[i].metric("Vues", "—", delta="—")
            cols[i].metric("Vidéos", "—", delta="—")
            continue

        current = sub.iloc[-1]
        first = sub.iloc[0]

        # Abonnés
        delta_sub = ((current["subscribers"] - first["subscribers"]) / first["subscribers"] * 100) if first["subscribers"] != 0 else 0
        cols[i].metric(label=f"{channel} — Abonnés", value=f"{current['subscribers']:,}", delta=f"{delta_sub:.2f}%")

        # Vues
        delta_views = ((current["views"] - first["views"]) / first["views"] * 100) if first["views"] != 0 else 0
        cols[i].metric(label="Vues", value=f"{current['views']:,}", delta=f"{delta_views:.2f}%")

        # Vidéos
        delta_videos = ((current["videos"] - first["videos"]) / first["videos"] * 100) if first["videos"] != 0 else 0
        cols[i].metric(label="Vidéos", value=f"{current['videos']:,}", delta=f"{delta_videos:.2f}%")

    # Graphiques interactifs
    st.subheader("Graphiques des abonnés")
    if filtered_yt.empty:
        st.info("Pas de données pour cette sélection/période.")
    else:
        fig = px.line(
            filtered_yt,
            x="time",
            y="subscribers",
            color="name",
            labels={"time": "Temps", "subscribers": "Abonnés", "name": "Chaîne"},
            title="Évolution du nombre d'abonnés"
        )
        fig.update_layout(legend_title_text="Chaîne")
        st.plotly_chart(fig, use_container_width=True)

    # Sparklines miniatures
    st.subheader("Mini-sparklines")
    for channel in selected_channels:
        sub = filtered_yt[filtered_yt["name"] == channel].sort_values("time")
        if not sub.empty:
            spark = px.line(sub, x="time", y="subscribers", height=100)
            st.write(channel)
            st.plotly_chart(spark, use_container_width=True)

    # Tableau des données
    with st.expander("Voir les données brutes"):
        st.dataframe(filtered_yt)
