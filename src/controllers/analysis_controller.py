import pandas as pd
import streamlit as st

from src.controllers.dashboard_controller import fetch_df
from src.config.constants import MOIS_ORDRE


@st.cache_data(show_spinner=False, ttl=3600)
def load_grav_by(column_name: str) -> pd.DataFrame:
    allowed_columns = {"lum", "catr", "atm"}
    if column_name not in allowed_columns:
        raise ValueError(f"Colonne non autorisée : {column_name}")

    return fetch_df(f"""
        SELECT a.{column_name} AS modalite, u.grav_int, COUNT(*) AS nb
        FROM usagers_clean u
        JOIN accident_full a ON u.Num_Acc = a.Num_Acc
        WHERE a.{column_name} IS NOT NULL
          AND u.grav_int BETWEEN 1 AND 4
          AND TRIM(a.{column_name}) NOT IN ('', 'Non renseigné', '-1')
        GROUP BY a.{column_name}, u.grav_int
        ORDER BY a.{column_name}, u.grav_int
    """)


@st.cache_data(show_spinner=False, ttl=3600)
def load_carte() -> pd.DataFrame:
    return fetch_df("""
        SELECT
            a.dep,
            COUNT(DISTINCT a.Num_Acc) AS nb_accidents,
            SUM(CASE WHEN u.grav_int = 2 THEN 1 ELSE 0 END) AS nb_tues,
            ROUND(
                SUM(CASE WHEN u.grav_int = 2 THEN 1 ELSE 0 END) * 100.0
                / NULLIF(COUNT(*), 0),
                2
            ) AS taux_mortalite
        FROM usagers_clean u
        JOIN accident_full a ON u.Num_Acc = a.Num_Acc
        WHERE a.dep IS NOT NULL AND u.grav_int IS NOT NULL
        GROUP BY a.dep
        ORDER BY nb_accidents DESC
    """)


@st.cache_data(show_spinner=False, ttl=3600)
def load_mortalite_annee() -> pd.DataFrame:
    return fetch_df("""
        SELECT
            a.an,
            COUNT(DISTINCT a.Num_Acc) AS nb_accidents,
            SUM(CASE WHEN u.grav_int = 2 THEN 1 ELSE 0 END) AS nb_tues,
            ROUND(
                SUM(CASE WHEN u.grav_int = 2 THEN 1 ELSE 0 END) * 100.0
                / NULLIF(COUNT(*), 0),
                3
            ) AS taux_mortalite
        FROM usagers_clean u
        JOIN accident_full a ON u.Num_Acc = a.Num_Acc
        WHERE a.an IS NOT NULL AND u.grav_int IS NOT NULL
        GROUP BY a.an
        ORDER BY a.an
    """)


@st.cache_data(show_spinner=False, ttl=3600)
def load_mortalite_mois() -> pd.DataFrame:
    df = fetch_df("""
        SELECT
            a.mois,
            COUNT(DISTINCT a.Num_Acc) AS nb_accidents,
            SUM(CASE WHEN u.grav_int = 2 THEN 1 ELSE 0 END) AS nb_tues,
            ROUND(
                SUM(CASE WHEN u.grav_int = 2 THEN 1 ELSE 0 END) * 100.0
                / NULLIF(COUNT(*), 0),
                3
            ) AS taux_mortalite
        FROM usagers_clean u
        JOIN accident_full a ON u.Num_Acc = a.Num_Acc
        WHERE a.mois IS NOT NULL AND u.grav_int IS NOT NULL
        GROUP BY a.mois
    """)
    df["mois_ordre"] = df["mois"].apply(lambda m: MOIS_ORDRE.index(m) if m in MOIS_ORDRE else 99)
    return df.sort_values("mois_ordre")


@st.cache_data(show_spinner=False, ttl=3600)
def load_bubble_heure_mois() -> pd.DataFrame:
    return fetch_df("""
        WITH base AS (
            SELECT
                a.mois,
                CASE
                    WHEN regexp_matches(cast(a.hrmn as varchar), '^[0-9]{1,2}:[0-9]{2}$')
                        THEN try_cast(split_part(cast(a.hrmn as varchar), ':', 1) AS INTEGER)
                    WHEN regexp_matches(regexp_replace(cast(a.hrmn as varchar), '[^0-9]', '', 'g'), '^[0-9]{3,6}$')
                        THEN try_cast(substr(lpad(regexp_replace(cast(a.hrmn as varchar), '[^0-9]', '', 'g'), 4, '0'), 1, 2) AS INTEGER)
                    ELSE NULL
                END AS heure,
                u.grav_int
            FROM usagers_clean u
            JOIN accident_full a ON u.Num_Acc = a.Num_Acc
            WHERE a.mois IS NOT NULL AND u.grav_int = 2
        )
        SELECT
            mois,
            heure,
            COUNT(*) AS nb_tues,
            COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () AS pct
        FROM base
        WHERE heure BETWEEN 0 AND 23
          AND mois IS NOT NULL
        GROUP BY mois, heure
        ORDER BY mois, heure
    """)


@st.cache_data(show_spinner=False)
def load_gravite_global() -> pd.DataFrame:
    return fetch_df("""
        SELECT grav_int, COUNT(*) AS nb
        FROM usagers_clean
        WHERE grav_int BETWEEN 1 AND 4
        GROUP BY grav_int
        ORDER BY grav_int
    """)


@st.cache_data(show_spinner=False)
def load_sexe_conducteurs() -> pd.DataFrame:
    return fetch_df("""
        SELECT sexe, COUNT(*) AS nb
        FROM usagers_clean
        WHERE catu = 'Conducteur'
          AND sexe IS NOT NULL
          AND TRIM(sexe) NOT IN ('', 'Non renseigné', '-1')
        GROUP BY sexe
        ORDER BY nb DESC
    """)


@st.cache_data(show_spinner=False)
def load_accidents_par_annee_global() -> pd.DataFrame:
    return fetch_df("""
        SELECT an, COUNT(*) AS nb_accidents
        FROM accident_full
        WHERE an IS NOT NULL
        GROUP BY an
        ORDER BY an
    """)


@st.cache_data(show_spinner=False)
def get_stats_globales() -> dict:
    df_an = load_accidents_par_annee_global()
    df_grav = load_gravite_global()

    total_acc = int(df_an["nb_accidents"].sum()) if not df_an.empty else 0
    total_tues = int(df_grav[df_grav["grav_int"] == 2]["nb"].sum()) if not df_grav.empty else 0

    nb_years = len(df_an) if not df_an.empty else 0
    moyenne_annuelle = int(total_acc / nb_years) if nb_years else 0

    return {
        "total_accidents": total_acc,
        "total_tues": total_tues,
        "moyenne_annuelle": moyenne_annuelle,
    }