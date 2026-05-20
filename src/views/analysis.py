import requests
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from src.controllers.dashboard_controller import fetch_df
from src.models.nosql_db import save_page_preferences, get_page_preferences
from src.models.nosql_db import set_last_page
from src.config.constants import GRAV_LABELS, GRAV_ORDRE, MOIS_ORDRE
from src.utils.ui_helpers import insight_box, COLOR_DANGER, COLOR_WARN, COLOR_OK
from src.controllers.analysis_controller import (
    load_grav_by,
    load_carte,
    load_mortalite_annee,
    load_mortalite_mois,
    load_bubble_heure_mois,
    # [PATCH] Remplace les anciennes fonctions locales load_tranches_age_conducteurs
    # et load_gravite_par_tranche_age — elles sont maintenant dans analysis_controller.py
    load_tranches_age_conducteurs,
    load_gravite_par_tranche_age,
    TRANCHES_AGE_ORDRE,
)


GRAV_COLORS = {
    "Tué": COLOR_DANGER,
    "Blessé hospitalisé": COLOR_WARN,
    "Blessé léger": "#F1C40F",
    "Indemne": COLOR_OK,
}


@st.cache_data(show_spinner=False, ttl=3600)
def load_geojson():
    url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson"
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


# [PATCH] Suppression des deux fonctions locales load_tranches_age_conducteurs()
# et load_gravite_par_tranche_age() qui étaient définies ici.
# Elles utilisaient "2024 - CAST(an_nais AS INTEGER)" (age figé à 2024) et
# la tranche "0-17 ans" (inexistante dans les données).
# Elles sont remplacées par les versions corrigées dans analysis_controller.py.


def stacked_pct_bar(df, group_col: str, title: str, max_categories: int = 10):
    df = df.copy()
    df["grav_label"] = df["grav_int"].map(GRAV_LABELS)

    totaux = df.groupby(group_col)["nb"].sum().rename("total")
    df = df.join(totaux, on=group_col)
    df["pct"] = (df["nb"] / df["total"] * 100).round(1)

    top_cats = totaux.nlargest(max_categories).index
    df = df[df[group_col].isin(top_cats)]

    pivot = df.pivot_table(
        index=group_col,
        columns="grav_label",
        values="pct",
        aggfunc="sum",
    ).fillna(0)

    pivot = pivot.reindex(columns=[g for g in GRAV_ORDRE if g in pivot.columns])

    if "Tué" in pivot.columns:
        pivot = pivot.sort_values("Tué", ascending=True)

    fig = go.Figure()
    for grav in pivot.columns:
        fig.add_trace(go.Bar(
            name=grav,
            y=pivot.index,
            x=pivot[grav],
            orientation="h",
            marker_color=GRAV_COLORS.get(grav, "#999999"),
            hovertemplate=f"<b>%{{y}}</b><br>{grav} : %{{x:.1f}}%<extra></extra>",
        ))

    fig.update_layout(
        barmode="stack",
        title=title,
        xaxis=dict(title="% des usagers", range=[0, 100]),
        yaxis=dict(title=""),
        legend=dict(orientation="h", y=-0.2),
        margin=dict(t=50, b=70, l=240, r=20),
        height=420,
        title_font_size=14,
    )
    return fig


def stacked_pct_bar_age(df, group_col: str, title: str):
    """
    Variante de stacked_pct_bar avec ordre canonique des tranches d'âge.
    Garantit que l'axe Y respecte l'ordre TRANCHES_AGE_ORDRE
    même après le tri par taux de tués.
    """
    df = df.copy()
    df["grav_label"] = df["grav_int"].map(GRAV_LABELS)

    totaux = df.groupby(group_col)["nb"].sum().rename("total")
    df = df.join(totaux, on=group_col)
    df["pct"] = (df["nb"] / df["total"] * 100).round(1)

    pivot = df.pivot_table(
        index=group_col,
        columns="grav_label",
        values="pct",
        aggfunc="sum",
    ).fillna(0)

    pivot = pivot.reindex(columns=[g for g in GRAV_ORDRE if g in pivot.columns])

    # Ordre fixe : tranches d'âge croissantes (plus lisible pour le jury)
    ordre_present = [t for t in TRANCHES_AGE_ORDRE if t in pivot.index]
    pivot = pivot.reindex(ordre_present)

    fig = go.Figure()
    for grav in pivot.columns:
        fig.add_trace(go.Bar(
            name=grav,
            y=pivot.index,
            x=pivot[grav],
            orientation="h",
            marker_color=GRAV_COLORS.get(grav, "#999999"),
            hovertemplate=f"<b>%{{y}}</b><br>{grav} : %{{x:.1f}}%<extra></extra>",
        ))

    fig.update_layout(
        barmode="stack",
        title=title,
        xaxis=dict(title="% des usagers", range=[0, 100]),
        yaxis=dict(title="", categoryorder="array", categoryarray=list(reversed(ordre_present))),
        legend=dict(orientation="h", y=-0.2),
        margin=dict(t=50, b=70, l=130, r=20),
        height=420,
        title_font_size=14,
    )
    return fig


def load_view():
    email = st.session_state.get("user_email", "guest")
    set_last_page(email, "analysis")
    prefs = get_page_preferences(email, "analysis")

    st.title("🔬 Analyse — Facteurs de risque & tendances")
    st.caption("Exploration des facteurs associés à la gravité et à la mortalité routière")

    st.markdown(
        "Cette page vise à **mieux comprendre les contextes d'accidents** : "
        "conditions de circulation, disparités territoriales et évolutions dans le temps."
    )

    st.divider()
    st.subheader("⚠️ Facteurs de risque — Gravité selon les conditions")
    st.caption("Chaque barre représente 100% des usagers dans une condition donnée")

    tab_lum, tab_route, tab_meteo = st.tabs(["🌙 Luminosité", "🛣️ Type de route", "🌧️ Météo"])

    with tab_lum:
        df = load_grav_by("lum").rename(columns={"modalite": "lum"})
        if not df.empty:
            st.plotly_chart(
                stacked_pct_bar(df, "lum", "Gravité selon les conditions de luminosité"),
                use_container_width=True,
                config={"displayModeBar": False},
            )
            insight_box(
                "💡",
                "Certaines conditions de luminosité semblent associées à une plus forte proportion de cas graves. "
                "Le graphique aide à comparer les contextes plutôt qu'à mesurer un risque absolu.",
            )
        else:
            st.info("Aucune donnée disponible.")

    with tab_route:
        df = load_grav_by("catr").rename(columns={"modalite": "catr"})
        if not df.empty:
            st.plotly_chart(
                stacked_pct_bar(df, "catr", "Gravité selon le type de voie"),
                use_container_width=True,
                config={"displayModeBar": False},
            )
            insight_box(
                "💡",
                "Les types de voie ne présentent pas le même profil de gravité. "
                "Cette lecture permet de repérer les contextes où les conséquences humaines paraissent les plus lourdes.",
            )
        else:
            st.info("Aucune donnée disponible.")

    with tab_meteo:
        df = load_grav_by("atm").rename(columns={"modalite": "atm"})
        if not df.empty:
            st.plotly_chart(
                stacked_pct_bar(df, "atm", "Gravité selon les conditions atmosphériques"),
                use_container_width=True,
                config={"displayModeBar": False},
            )
            insight_box(
                "💡",
                "Le volume d'accidents et leur gravité ne coïncident pas toujours. "
                "Certaines situations météo semblent produire moins d'accidents, mais potentiellement plus graves.",
            )
        else:
            st.info("Aucune donnée disponible.")

    st.divider()
    st.subheader("🗺️ Carte des accidents par département")
    st.caption("Comparaison géographique selon le volume d'accidents, le nombre de tués ou la mortalité")

    with st.spinner("Chargement de la carte..."):
        df_carte = load_carte()
        geojson = load_geojson()

    metric_options = ["Nombre d'accidents", "Nombre de tués", "Taux de mortalité (%)"]
    metric_default = prefs.get("metric_carte", "Nombre d'accidents")
    if metric_default not in metric_options:
        metric_default = "Nombre d'accidents"

    metric_carte = st.radio(
        "Indicateur :",
        metric_options,
        horizontal=True,
        index=metric_options.index(metric_default),
    )

    updated_prefs = dict(prefs) if prefs else {}
    updated_prefs["metric_carte"] = metric_carte
    save_page_preferences(email, "analysis", updated_prefs)

    col_map = {
        "Nombre d'accidents": "nb_accidents",
        "Nombre de tués": "nb_tues",
        "Taux de mortalité (%)": "taux_mortalite",
    }
    col_sel = col_map[metric_carte]

    label_map = {
        "nb_accidents": "Accidents",
        "nb_tues": "Tués",
        "taux_mortalite": "Taux mort. (%)",
    }

    if geojson and not df_carte.empty:
        df_carte["dep"] = df_carte["dep"].astype(str).str.zfill(2)

        fig = px.choropleth(
            df_carte,
            geojson=geojson,
            locations="dep",
            featureidkey="properties.code",
            color=col_sel,
            color_continuous_scale="Reds" if "tues" in col_sel or "mortalite" in col_sel else "Blues",
            hover_name="dep",
            hover_data={
                "nb_accidents": True,
                "nb_tues": True,
                "taux_mortalite": True,
                col_sel: False,
            },
            labels=label_map,
            title=f"{metric_carte} par département (2005–2024)",
        )

        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(
            margin=dict(t=50, b=0, l=0, r=0),
            height=550,
            title_font_size=14,
            coloraxis_colorbar=dict(title=label_map[col_sel]),
        )

        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("**🔴 Top 5 — Départements les plus touchés**")
            top5 = df_carte.nlargest(5, col_sel)[["dep", "nb_accidents", "nb_tues", "taux_mortalite"]]
            top5.columns = ["Dép.", "Accidents", "Tués", "Taux mort. (%)"]
            st.dataframe(top5, hide_index=True, use_container_width=True)

        with col_b:
            st.markdown("**🟢 Top 5 — Départements les moins touchés**")
            bot5 = df_carte.nsmallest(5, col_sel)[["dep", "nb_accidents", "nb_tues", "taux_mortalite"]]
            bot5.columns = ["Dép.", "Accidents", "Tués", "Taux mort. (%)"]
            st.dataframe(bot5, hide_index=True, use_container_width=True)

        insight_box(
            "💡",
            "La carte met en évidence une concentration des accidents dans les zones les plus denses. "
            "En revanche, certains territoires moins urbanisés affichent parfois un taux de mortalité plus élevé, "
            "ce qui peut refléter des contextes routiers différents.",
        )
    else:
        st.warning(
            "La carte nécessite une connexion internet pour charger les contours des départements.",
            icon="🌐",
        )

        if not df_carte.empty:
            st.dataframe(
                df_carte.rename(columns={
                    "dep": "Dép.",
                    "nb_accidents": "Accidents",
                    "nb_tues": "Tués",
                    "taux_mortalite": "Taux mort. (%)",
                }),
                use_container_width=True,
                height=400,
            )

    st.divider()
    st.subheader("📊 Répartition des conducteurs par tranche d'âge")
    st.caption("Distribution des conducteurs impliqués dans les accidents selon leur âge (2005–2024)")

    # [PATCH] Appel de la fonction corrigée depuis analysis_controller
    df_age = load_tranches_age_conducteurs()

    if not df_age.empty:
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=df_age["tranche_age"],
            y=df_age["nb_conducteurs"],
            text=df_age["pct"].apply(lambda v: f"{v:.1f}%"),
            textposition="outside",
            name="Conducteurs",
            marker_color="#5DADE2",
            hovertemplate="<b>%{x}</b><br>Conducteurs : %{y:,}<br>Part : %{text}<extra></extra>",
        ))

        fig.update_layout(
            title="Nombre de conducteurs impliqués par tranche d'âge",
            xaxis=dict(title="Tranche d'âge"),
            yaxis=dict(title="Nombre de conducteurs"),
            margin=dict(t=50, b=60, l=60, r=20),
            height=420,
            title_font_size=14,
        )

        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        tranche_max = df_age.loc[df_age["nb_conducteurs"].idxmax(), "tranche_age"]
        pct_max = df_age.loc[df_age["nb_conducteurs"].idxmax(), "pct"]

        insight_box(
            "💡",
            f"La tranche d'âge la plus représentée parmi les conducteurs impliqués est <b>{tranche_max}</b> "
            f"({pct_max:.1f}% du total). Ce pic correspond aux actifs qui cumulent le plus grand nombre "
            "de kilomètres parcourus annuellement, ce qui accroît mécaniquement leur exposition au risque.",
        )

        # [PATCH] Note méthodologique obligatoire — à conserver pour la soutenance
        st.caption(
            "⚠️ Note méthodologique : 6 323 entrées avec an_nais = 1924 ont été exclues, "
            "car cette valeur est utilisée comme code sentinel dans le BAAC pour indiquer "
            "une année de naissance inconnue (et non de vrais conducteurs centenaires). "
            "Les conducteurs de 16–17 ans (5 250 entrées) sont conservés : "
            "ils correspondent à des usagers légalement habilités à conduire en France "
            "(cyclomoteur AM, conduite accompagnée AAC, moto légère A1)."
        )
    else:
        st.info("Aucune donnée disponible.")

    st.subheader("🚻 Gravité selon le sexe")
    st.caption("Chaque barre représente 100 % des usagers par sexe")

    df_sexe = fetch_df("""
        WITH base AS (
            SELECT
                CASE
                    WHEN LOWER(TRIM(sexe)) IN ('masculin', 'homme', 'm') THEN 'Homme'
                    WHEN LOWER(TRIM(sexe)) IN ('feminin', 'féminin', 'femme', 'f') THEN 'Femme'
                    ELSE 'Autre / Inconnu'
                END AS modalite,
                grav_int
            FROM usagers_clean
            WHERE grav_int IS NOT NULL
              AND sexe IS NOT NULL
        )
        SELECT
            modalite,
            grav_int,
            COUNT(*) AS nb
        FROM base
        WHERE grav_int IS NOT NULL
        GROUP BY modalite, grav_int
        ORDER BY
            CASE modalite
                WHEN 'Homme' THEN 1
                WHEN 'Femme' THEN 2
                ELSE 3
            END,
            grav_int
    """)

    if not df_sexe.empty:
        df_sexe["grav_int"] = df_sexe["grav_int"].astype(int)

        st.plotly_chart(
            stacked_pct_bar(
                df_sexe,
                "modalite",
                "Gravité des accidents selon le sexe",
                max_categories=10,
            ),
            use_container_width=True,
            config={"displayModeBar": False},
        )

        insight_box(
            "💡",
            "Les différences observées entre hommes et femmes peuvent refléter des comportements de conduite, "
            "des expositions différentes ou des contextes d'usage du véhicule distincts.",
        )
    else:
        st.info("Aucune donnée disponible.")

    st.subheader("🚨 Gravité selon la tranche d'âge")
    st.caption("Chaque barre représente 100 % des usagers d'une tranche d'âge")

    # [PATCH] Appel de la fonction corrigée depuis analysis_controller
    df_age_grav = load_gravite_par_tranche_age()

    if not df_age_grav.empty:
        df_age_grav["grav_int"] = df_age_grav["grav_int"].astype(int)

        st.plotly_chart(
            stacked_pct_bar_age(
                df_age_grav,
                "modalite",
                "Gravité des accidents selon la tranche d'âge",
            ),
            use_container_width=True,
            config={"displayModeBar": False},
        )

        insight_box(
            "💡",
            "Cette lecture compare la structure de gravité au sein de chaque tranche d'âge. "
            "Elle est plus pertinente qu'un simple volume d'accidents pour repérer les profils "
            "potentiellement les plus vulnérables. On observe notamment que les 75 ans et plus "
            "présentent le taux de mortalité le plus élevé, cohérent avec les données ONISR.",
        )
    else:
        st.info("Aucune donnée disponible.")

    st.divider()
    st.subheader("📈 Tendances temporelles — Évolution de la mortalité")
    st.caption("Lecture chronologique des accidents, des décès et de leur intensité relative")

    tab_an, tab_mois, tab_heatmap = st.tabs(["📆 Par année", "📅 Par mois", "🫧 Tués heure × mois"])

    with tab_an:
        df_an = load_mortalite_annee()
        if not df_an.empty:
            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=df_an["an"],
                y=df_an["nb_accidents"],
                name="Accidents",
                marker_color="#AED6F1",
                opacity=0.7,
                yaxis="y1",
                hovertemplate="<b>%{x}</b><br>Accidents : %{y:,}<extra></extra>",
            ))

            fig.add_trace(go.Bar(
                x=df_an["an"],
                y=df_an["nb_tues"],
                name="Tués",
                marker_color=COLOR_DANGER,
                opacity=0.85,
                yaxis="y1",
                hovertemplate="<b>%{x}</b><br>Tués : %{y:,}<extra></extra>",
            ))

            fig.add_trace(go.Scatter(
                x=df_an["an"],
                y=df_an["taux_mortalite"],
                name="Taux mortalité (%)",
                mode="lines+markers",
                line=dict(color="#1F4E79", width=2.5, dash="dot"),
                marker=dict(size=7),
                yaxis="y2",
                hovertemplate="<b>%{x}</b><br>Taux : %{y:.2f}%<extra></extra>",
            ))

            fig.update_layout(
                title="Évolution des accidents, tués et taux de mortalité par année",
                barmode="overlay",
                xaxis=dict(title="Année", dtick=1),
                yaxis=dict(title="Nombre"),
                yaxis2=dict(
                    title="Taux de mortalité (%)",
                    overlaying="y",
                    side="right",
                    showgrid=False,
                ),
                legend=dict(orientation="h", y=-0.2),
                margin=dict(t=50, b=80, l=60, r=60),
                height=450,
                title_font_size=14,
                hovermode="x unified",
            )

            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            tx_max = float(df_an["taux_mortalite"].max())
            tx_min = float(df_an["taux_mortalite"].min())
            an_tmax = int(df_an.loc[df_an["taux_mortalite"].idxmax(), "an"])
            an_tmin = int(df_an.loc[df_an["taux_mortalite"].idxmin(), "an"])
            baisse = round((tx_max - tx_min) / tx_max * 100)

            insight_box(
                "💡",
                f"Le taux de mortalité passe d'un maximum de <b>{tx_max:.2f}%</b> en <b>{an_tmax}</b> "
                f"à un minimum de <b>{tx_min:.2f}%</b> en <b>{an_tmin}</b>, soit une baisse d'environ <b>{baisse}%</b>. "
                "Cette évolution paraît cohérente avec l'amélioration progressive des politiques et équipements de sécurité.",
            )
        else:
            st.info("Aucune donnée disponible.")

    with tab_mois:
        df_mois = load_mortalite_mois()
        if not df_mois.empty:
            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=df_mois["mois"],
                y=df_mois["nb_accidents"],
                name="Accidents",
                marker_color="#AED6F1",
                opacity=0.7,
                yaxis="y1",
                hovertemplate="<b>%{x}</b><br>Accidents : %{y:,}<extra></extra>",
            ))

            fig.add_trace(go.Scatter(
                x=df_mois["mois"],
                y=df_mois["taux_mortalite"],
                name="Taux mortalité (%)",
                mode="lines+markers",
                line=dict(color=COLOR_DANGER, width=2.5),
                marker=dict(size=8),
                yaxis="y2",
                hovertemplate="<b>%{x}</b><br>Taux : %{y:.2f}%<extra></extra>",
            ))

            fig.update_layout(
                title="Saisonnalité : accidents et taux de mortalité par mois",
                xaxis=dict(title="Mois", tickangle=-30),
                yaxis=dict(title="Nombre d'accidents"),
                yaxis2=dict(
                    title="Taux de mortalité (%)",
                    overlaying="y",
                    side="right",
                    showgrid=False,
                ),
                legend=dict(orientation="h", y=-0.25),
                margin=dict(t=50, b=90, l=60, r=60),
                height=430,
                title_font_size=14,
                hovermode="x unified",
            )

            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            top_acc = df_mois.loc[df_mois["nb_accidents"].idxmax(), "mois"]
            top_tx = df_mois.loc[df_mois["taux_mortalite"].idxmax(), "mois"]

            insight_box(
                "💡",
                f"Le mois avec le plus d'accidents est <b>{top_acc}</b>, tandis que le taux de mortalité le plus élevé est observé en <b>{top_tx}</b>. "
                "Cela montre que le volume d'accidents et leur gravité ne se confondent pas toujours.",
            )
        else:
            st.info("Aucune donnée disponible.")

    with tab_heatmap:
        df_bub = load_bubble_heure_mois()
        if not df_bub.empty:
            df_bub["mois_ordre"] = df_bub["mois"].apply(lambda m: MOIS_ORDRE.index(m) if m in MOIS_ORDRE else 99)
            df_bub = df_bub.sort_values(["mois_ordre", "heure"])
            df_bub["heure_label"] = df_bub["heure"].astype(str).str.zfill(2) + "h"

            h_min, h_max = st.select_slider(
                "🕐 Filtrer la plage horaire",
                options=list(range(24)),
                value=(0, 23),
                format_func=lambda h: f"{h:02d}h",
            )

            df_filtered = df_bub[df_bub["heure"].between(h_min, h_max)]

            fig = px.scatter(
                df_filtered,
                x="heure_label",
                y="mois",
                size="nb_tues",
                color="nb_tues",
                color_continuous_scale="Reds",
                size_max=45,
                title="Tués par heure et par mois (2005–2024 cumulés)",
                labels={
                    "heure_label": "Heure de l'accident",
                    "mois": "Mois",
                    "nb_tues": "Nb tués",
                },
                hover_data={
                    "nb_tues": True,
                    "heure_label": True,
                    "mois": True,
                    "pct": ":.2f",
                },
                category_orders={"mois": MOIS_ORDRE},
            )

            fig.update_layout(
                height=520,
                margin=dict(t=50, b=60, l=110, r=20),
                title_font_size=14,
                coloraxis_colorbar=dict(title="Nb tués"),
                yaxis=dict(
                    categoryorder="array",
                    categoryarray=list(reversed(MOIS_ORDRE)),
                ),
                xaxis=dict(tickangle=-45),
            )

            fig.update_traces(
                hovertemplate=(
                    "<b>%{y} — %{x}</b><br>"
                    "Tués : <b>%{marker.size}</b><br>"
                    "<extra></extra>"
                )
            )

            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            top = df_bub.loc[df_bub["nb_tues"].idxmax()]
            top_h = f"{int(top['heure']):02d}h"
            top_m = top["mois"]
            top_nb = int(top["nb_tues"])

            heure_totaux = df_bub.groupby("heure")["nb_tues"].sum()
            top_heure = int(heure_totaux.idxmax())
            top_mois_tot = df_bub.groupby("mois")["nb_tues"].sum().idxmax()

            insight_box(
                "💡",
                f"Le pic observé dans ces données se situe en <b>{top_m}</b> à <b>{top_h}</b>, avec <b>{top_nb:,} tués</b> cumulés sur la période. "
                f"L'heure la plus meurtrière toutes saisons confondues est <b>{top_heure:02d}h</b> et le mois le plus meurtrier est <b>{top_mois_tot}</b>.",
            )
        else:
            st.info("Aucune donnée disponible.")
