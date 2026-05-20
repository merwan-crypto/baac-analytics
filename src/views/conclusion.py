import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from src.models.nosql_db import set_last_page
from src.config.constants import GRAV_LABELS
from src.utils.ui_helpers import insight_box, COLOR_DANGER, COLOR_WARN, COLOR_OK
from src.controllers.analysis_controller import (
    load_gravite_global,
    load_sexe_conducteurs,
    load_accidents_par_annee_global,
    get_stats_globales,
)


def load_view():
    email = st.session_state.get("user_email", "guest")
    set_last_page(email, "conclusion")

    st.title("📊 Conclusion générale")
    st.caption("Synthèse des principaux enseignements tirés de l’analyse 2005–2024")

    st.markdown(
        "Cette page résume les tendances majeures observées dans les données "
        "sur les accidents corporels de la route en France."
    )

    df_an = load_accidents_par_annee_global()
    df_grav = load_gravite_global()
    df_sexe = load_sexe_conducteurs()
    stats = get_stats_globales()

    st.divider()

    c1, c2, c3 = st.columns(3)
    c1.metric("Accidents (2005–2024)", f"{stats['total_accidents']:,}")
    c2.metric("Tués", f"{stats['total_tues']:,}")
    c3.metric("Moyenne annuelle", f"{stats['moyenne_annuelle']:,}")

    st.divider()

    st.subheader("📈 Évolution des accidents")
    st.caption("Lecture globale de la tendance sur l’ensemble de la période")

    if not df_an.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_an["an"],
            y=df_an["nb_accidents"],
            mode="lines+markers",
            line=dict(color="#1F4E79", width=3),
            marker=dict(size=6),
            hovertemplate="<b>%{x}</b><br>%{y:,} accidents<extra></extra>",
        ))
        fig.update_layout(
            title="Nombre d'accidents par année",
            xaxis_title="Année",
            yaxis_title="Accidents",
            height=360,
            title_font_size=14,
            margin=dict(t=50, b=40, l=40, r=20),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("⚠️ Gravité des usagers")
    st.caption("Répartition des conséquences humaines observées dans les données")

    if not df_grav.empty:
        df_grav = df_grav.copy()
        df_grav["label"] = df_grav["grav_int"].map(GRAV_LABELS)

        fig = px.bar(
            df_grav,
            x="label",
            y="nb",
            color="label",
            title="Répartition des usagers selon la gravité",
            labels={"label": "Gravité", "nb": "Nombre d'usagers"},
            color_discrete_map={
                "Tué": COLOR_DANGER,
                "Blessé hospitalisé": "#E67E22",
                "Blessé léger": "#F1C40F",
                "Indemne": COLOR_OK,
            }
        )
        fig.update_layout(
            showlegend=False,
            height=360,
            title_font_size=14,
            margin=dict(t=50, b=40, l=40, r=20),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("👤 Profil des conducteurs")
    st.caption("Lecture synthétique d’un des profils les plus présents dans les données")

    if not df_sexe.empty:
        fig = px.pie(
            df_sexe,
            values="nb",
            names="sexe",
            hole=0.4,
            title="Répartition par sexe des conducteurs impliqués",
            color_discrete_sequence=["#3498db", "#e91e8c"],
        )
        fig.update_layout(
            title_font_size=14,
            margin=dict(t=50, b=20, l=20, r=20),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("📋 Points clés retenus")

    if not df_sexe.empty:
        top = df_sexe.iloc[0]
        pct = int(top["nb"] / df_sexe["nb"].sum() * 100)
        insight_box(
            "👤",
            f"Parmi les conducteurs impliqués, les personnes de genre <b>{top['sexe'].lower()}</b> sont majoritaires avec environ <b>{pct}%</b> du total observé.",
        )

    if not df_grav.empty:
        tues = int(df_grav[df_grav["grav_int"] == 2]["nb"].sum())
        total = int(df_grav["nb"].sum())
        pct = round(tues / total * 100, 1)
        insight_box(
            "⚠️",
            f"La part des usagers <b>tués</b> représente <b>{pct}%</b> des cas de gravité renseignés, soit <b>{tues:,}</b> décès sur la période.",
            color=COLOR_DANGER,
        )

    if not df_an.empty:
        an_max = int(df_an.loc[df_an["nb_accidents"].idxmax(), "an"])
        an_min = int(df_an.loc[df_an["nb_accidents"].idxmin(), "an"])
        nb_max = int(df_an["nb_accidents"].max())
        nb_min = int(df_an["nb_accidents"].min())
        baisse = round((nb_max - nb_min) / nb_max * 100)

        insight_box(
            "📉",
            f"Le volume annuel passe d’un maximum de <b>{nb_max:,}</b> accidents en <b>{an_max}</b> "
            f"à un minimum de <b>{nb_min:,}</b> en <b>{an_min}</b>, soit une baisse d’environ <b>{baisse}%</b>.",
            color=COLOR_OK,
        )

    st.divider()

    st.subheader("🧠 Conclusion")

    st.markdown(
        """
L’analyse met en évidence plusieurs tendances structurantes de la sécurité routière en France entre 2005 et 2024.

D’abord, les accidents impliquent massivement certains profils d’usagers, en particulier les conducteurs. Ensuite, même si une grande partie des victimes ressortent indemnes ou légèrement blessées, la part des cas mortels demeure un enjeu central de sécurité publique.

Sur le temps long, les données montrent une baisse globale du nombre d’accidents observés. Cette évolution va dans le sens d’une amélioration progressive de la sécurité routière, même si des contextes plus à risque subsistent selon les territoires, les conditions de circulation ou les moments de l’année.

Ces résultats invitent à poursuivre les efforts de prévention, de sensibilisation et d’aménagement ciblé pour réduire encore la gravité des accidents.
"""
    )

    insight_box(
        "⚠️",
        "Certaines données, notamment sur quelques départements avant 2018, peuvent être incomplètes. "
        "Les résultats doivent donc être interprétés avec cette limite.",
        color=COLOR_WARN,
    )