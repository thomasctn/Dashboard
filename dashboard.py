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
with tab3:
    st.header("📺 Dashboard YouTube — Vidéos populaires")

    YT_FILE = "youtube_data.csv"

    if not os.path.exists(YT_FILE):
        st.info("Pas de données. Lance collect_data_youtube.py au moins une fois pour créer youtube_data.csv")
        st.stop()

    df_yt = pd.read_csv(YT_FILE)
    df_yt["time"] = pd.to_datetime(df_yt["time"], errors="coerce")
    df_yt = df_yt.dropna(subset=["time"]).sort_values("time")

    # Nettoyage des colonnes numériques
    for col in ["views", "likes", "comments"]:
        if col in df_yt.columns:
            df_yt[col] = pd.to_numeric(df_yt[col], errors="coerce").fillna(0).astype(int)

    # Création d'une colonne pour identifier la vidéo facilement
    df_yt["video_label"] = df_yt["title"] + " — " + df_yt["channel_title"]

    # Trier par nombre de vues maximum
    latest_views = df_yt.groupby("video_label")["views"].max()
    videos_sorted = latest_views.sort_values(ascending=False).index.tolist()

    selected_videos = st.multiselect(
        "Choisir les vidéos",
        videos_sorted,
        default=videos_sorted[:5]  # préselection des 5 plus vues
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
                        (df_yt["video_label"].isin(selected_videos))]

    # Metrics
    st.subheader("📈 Indicateurs par vidéo")
    cols = st.columns(len(selected_videos) if selected_videos else 1)
    for i, vid in enumerate(selected_videos):
        sub = filtered_yt[filtered_yt["video_label"] == vid].sort_values("time")
        if sub.empty:
            cols[i].write(vid)
            cols[i].metric("Vues", "—", delta="—")
            cols[i].metric("Likes", "—", delta="—")
            cols[i].metric("Commentaires", "—", delta="—")
            continue

        current = sub.iloc[-1]
        first = sub.iloc[0]

        # Vues
        delta_views = ((current["views"] - first["views"]) / first["views"] * 100) if first["views"] != 0 else 0
        cols[i].metric(label="Vues", value=f"{current['views']:,}", delta=f"{delta_views:.2f}%")

        # Likes
        delta_likes = ((current["likes"] - first["likes"]) / first["likes"] * 100) if first["likes"] != 0 else 0
        cols[i].metric(label="Likes", value=f"{current['likes']:,}", delta=f"{delta_likes:.2f}%")

        # Commentaires
        delta_comments = ((current["comments"] - first["comments"]) / first["comments"] * 100) if first["comments"] != 0 else 0
        cols[i].metric(label="Commentaires", value=f"{current['comments']:,}", delta=f"{delta_comments:.2f}%")

    # Graphiques interactifs
    st.subheader("Graphiques des vues")
    if filtered_yt.empty:
        st.info("Pas de données pour cette sélection/période.")
    else:
        fig = px.line(
            filtered_yt,
            x="time",
            y="views",
            color="video_label",
            labels={"time": "Temps", "views": "Vues", "video_label": "Vidéo"},
            title="Évolution des vues"
        )
        fig.update_layout(legend_title_text="Vidéo")
        st.plotly_chart(fig, use_container_width=True)

    # Sparklines miniatures
    st.subheader("Mini-sparklines")
    for vid in selected_videos:
        sub = filtered_yt[filtered_yt["video_label"] == vid].sort_values("time")
        if not sub.empty:
            spark = px.line(sub, x="time", y="views", height=100)
            st.write(vid)
            st.plotly_chart(spark, use_container_width=True)

    # Tableau des données
    with st.expander("Voir les données brutes"):
        st.dataframe(filtered_yt)
