# Dataset controller (MVC) — Responsable de la logique métier et de l'accès aux données pour la vue dataset.py.

# Rôle du controller :
# - récupérer les données via le model (ici, simplifié en interne),
# - préparer/transformer les données pour la vue,
# - exposer des fonctions simples que la vue peut appeler sans connaître
#   les détails d'implémentation.

import pandas as pd
import streamlit as st

from src.controllers.dashboard_controller import fetch_df


class DatasetController:
    """Controller minimal pour la page `dataset`.

    Méthodes utiles pour la view :
    - get_stats_par_annee() -> pd.DataFrame
    - get_summary(df) -> pd.DataFrame
    """

    @staticmethod
    @st.cache_data(show_spinner=False, ttl=3600)
    def get_stats_par_annee() -> pd.DataFrame:
        """Retourne le nombre d'accidents, de tués et de blessés par année."""
        return fetch_df("""
            SELECT
                a.an,
                COUNT(DISTINCT a.Num_Acc)                              AS nb_accidents,
                SUM(CASE WHEN u.grav_int = 2 THEN 1 ELSE 0 END)       AS nb_tues,
                SUM(CASE WHEN u.grav_int = 3 THEN 1 ELSE 0 END)       AS nb_blesses_hosp,
                SUM(CASE WHEN u.grav_int = 4 THEN 1 ELSE 0 END)       AS nb_blesses_legers
            FROM usagers_clean u
            JOIN accident_full a ON u.Num_Acc = a.Num_Acc
            WHERE a.an IS NOT NULL
            GROUP BY a.an
            ORDER BY a.an
        """)

    @staticmethod
    def get_summary(df: pd.DataFrame) -> pd.DataFrame:
        """Retourne des statistiques descriptives utiles pour la view."""
        summary = df.describe(include="all").transpose()
        summary = summary.astype(str)
        return summary