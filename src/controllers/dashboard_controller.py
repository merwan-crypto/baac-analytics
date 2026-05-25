import duckdb
import pandas as pd
import streamlit as st
from src.config.constants import MOIS_ORDRE, GRAV_LABELS, DUCKDB_PATH

DB_PATH = DUCKDB_PATH


# ---------------------------------------------------------------------------
# Connexion unique partagée (cache Streamlit)
# ---------------------------------------------------------------------------
@st.cache_resource
def get_con():
    from src.config.db_loader import ensure_db
    ensure_db()  # garantit que le fichier existe avant de connecter
    return duckdb.connect(DB_PATH, read_only=True)


# ---------------------------------------------------------------------------
# Helpers requêtes
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def fetch_df(sql: str, params=None) -> pd.DataFrame:
    return get_con().execute(sql, params or []).df()


@st.cache_data(show_spinner=False)
def fetch_list(sql: str) -> list:
    return [r[0] for r in get_con().execute(sql).fetchall()]


# ---------------------------------------------------------------------------
# Chargement des dimensions (filtres sidebar)
# ---------------------------------------------------------------------------
def get_dimensions() -> dict:
    annees = fetch_list("SELECT an FROM dim_annees")
    deps = fetch_list("SELECT dep FROM dim_deps WHERE dep != '20'")
    lum_vals = fetch_list("SELECT lum FROM dim_lum")
    atm_vals = fetch_list("SELECT atm FROM dim_atm")
    col_vals = fetch_list("SELECT col FROM dim_col")
    catr_vals = fetch_list("SELECT catr FROM dim_catr")
    surf_vals = fetch_list("SELECT surf FROM dim_surf")
    vma_vals = fetch_list("SELECT vma FROM dim_vma")

    mois_brut = fetch_list("""
        SELECT DISTINCT mois
        FROM caracteristiques
        WHERE mois IS NOT NULL
    """)
    mois_vals = [m for m in MOIS_ORDRE if m in mois_brut]

    return {
        "annees": annees,
        "deps": deps,
        "lum_vals": lum_vals,
        "atm_vals": atm_vals,
        "col_vals": col_vals,
        "catr_vals": catr_vals,
        "surf_vals": surf_vals,
        "vma_vals": vma_vals,
        "mois_vals": mois_vals,
    }


# ---------------------------------------------------------------------------
# Construction des clauses WHERE
# ---------------------------------------------------------------------------
def build_where(an, dep, mois, lum, atm, colf, catr, surf, vma):
    clauses = []
    params = []

    if an:
        placeholders = ",".join(["?"] * len(an))
        clauses.append(f"an IN ({placeholders})")
        params.extend([int(a) for a in an])

    if dep:
        placeholders = ",".join(["?"] * len(dep))
        clauses.append(f"dep IN ({placeholders})")
        params.extend(dep)

    if mois:
        placeholders = ",".join(["?"] * len(mois))
        clauses.append(f"mois IN ({placeholders})")
        params.extend(mois)

    if lum:
        placeholders = ",".join(["?"] * len(lum))
        clauses.append(f"lum IN ({placeholders})")
        params.extend(lum)

    if atm:
        placeholders = ",".join(["?"] * len(atm))
        clauses.append(f"atm IN ({placeholders})")
        params.extend(atm)

    if colf:
        placeholders = ",".join(["?"] * len(colf))
        clauses.append(f"col IN ({placeholders})")
        params.extend(colf)

    if catr:
        placeholders = ",".join(["?"] * len(catr))
        clauses.append(f"catr IN ({placeholders})")
        params.extend(catr)

    if surf:
        placeholders = ",".join(["?"] * len(surf))
        clauses.append(f"surf IN ({placeholders})")
        params.extend(surf)

    if vma:
        placeholders = ",".join(["?"] * len(vma))
        clauses.append(f"vma IN ({placeholders})")
        params.extend(vma)

    where_sql = "WHERE " + " AND ".join(clauses) if clauses else ""
    return where_sql, params


def build_where_usagers(an, dep, mois):
    clauses = []
    params = []

    if an:
        placeholders = ",".join(["?"] * len(an))
        clauses.append(f"an IN ({placeholders})")
        params.extend([int(a) for a in an])

    if dep:
        placeholders = ",".join(["?"] * len(dep))
        clauses.append(f"dep IN ({placeholders})")
        params.extend(dep)

    if mois:
        placeholders = ",".join(["?"] * len(mois))
        clauses.append(f"mois IN ({placeholders})")
        params.extend(mois)

    where_sql = "WHERE " + " AND ".join(clauses) if clauses else ""
    return where_sql, params


# ---------------------------------------------------------------------------
# Requêtes métier
# ---------------------------------------------------------------------------
def get_kpi(where_sql: str, params: list) -> dict:
    df = fetch_df(f"""
        SELECT
            COUNT(*) AS accidents,
            COALESCE(SUM(nb_vehicules), 0) AS vehicules,
            COALESCE(SUM(nb_usagers), 0) AS usagers
        FROM accident_full
        {where_sql}
    """, params)

    return {
        "accidents": int(df.loc[0, "accidents"]),
        "vehicules": int(df.loc[0, "vehicules"]),
        "usagers": int(df.loc[0, "usagers"]),
    }


def get_accidents_par_mois(where_sql: str, params: list) -> pd.DataFrame:
    df = fetch_df(f"""
        SELECT mois, COUNT(*) AS nb
        FROM accident_full
        {where_sql}
        GROUP BY mois
    """, params)

    if not df.empty:
        df["mois"] = pd.Categorical(df["mois"], categories=MOIS_ORDRE, ordered=True)
        df = df.sort_values("mois")

    return df


def get_accidents_par_heure(where_sql: str, params: list) -> pd.DataFrame:
    df = fetch_df(f"""
        WITH base AS (
            SELECT
                CASE
                    WHEN hrmn IS NULL THEN NULL
                    WHEN regexp_matches(cast(hrmn as varchar), '^[0-9]{{1,2}}:[0-9]{{2}}$')
                        THEN try_cast(split_part(cast(hrmn as varchar), ':', 1) AS INTEGER)
                    WHEN regexp_matches(regexp_replace(cast(hrmn as varchar), '[^0-9]', '', 'g'), '^[0-9]{{3,6}}$')
                        THEN try_cast(substr(lpad(regexp_replace(cast(hrmn as varchar), '[^0-9]', '', 'g'), 4, '0'), 1, 2) AS INTEGER)
                    ELSE NULL
                END AS heure
            FROM accident_full
            {where_sql}
        )
        SELECT heure, COUNT(*) AS nb
        FROM base
        WHERE heure BETWEEN 0 AND 23
        GROUP BY heure
        ORDER BY heure
    """, params)

    if not df.empty:
        all_hours = pd.DataFrame({"heure": list(range(24))})
        df["heure"] = df["heure"].astype(int)
        df = all_hours.merge(df, on="heure", how="left").fillna({"nb": 0})
        df["heure_label"] = df["heure"].astype(str).str.zfill(2) + "h"

    return df


def get_gravite(where_sql_u: str, params_u: list, an, dep, mois) -> pd.DataFrame:
    df = fetch_df(f"""
        SELECT
            CASE
                WHEN grav_int = 1 THEN 'Indemne'
                WHEN grav_int = 2 THEN 'Tué'
                WHEN grav_int = 3 THEN 'Blessé hospitalisé'
                WHEN grav_int = 4 THEN 'Blessé léger'
                ELSE 'Inconnu'
            END AS grav_label,
            COUNT(*) AS nb
        FROM v_usagers_detail_clean
        {where_sql_u}
        GROUP BY grav_int
        ORDER BY grav_int
    """, params_u)

    if not df.empty:
        ordre = ["Tué", "Blessé hospitalisé", "Blessé léger", "Indemne", "Inconnu"]
        df["grav_label"] = pd.Categorical(df["grav_label"], categories=ordre, ordered=True)
        df = df.sort_values("grav_label")

    return df


def get_accident_by_num(num_acc: str) -> dict:
    return {
        "accident": fetch_df(
            """
            SELECT Num_Acc, an, mois, jour, hrmn, dep, agg, catr, circ, plan, prof,
                   surf, vma, nbv, situ, lum, atm, int, col, nb_vehicules, nb_usagers
            FROM accident_full
            WHERE Num_Acc = ?
            """,
            [num_acc],
        ),
        "vehicules": fetch_df(
            "SELECT * FROM vehicules WHERE Num_Acc = ?",
            [num_acc],
        ),
        "usagers": fetch_df(
            "SELECT * FROM v_usagers_detail_clean WHERE Num_Acc = ?",
            [num_acc],
        ),
    }


def get_page_accidents(where_sql: str, params: list, page: int, page_size: int = 500):
    total = int(fetch_df(
        f"SELECT COUNT(*) AS n FROM accident_full {where_sql}",
        params
    ).loc[0, "n"])

    offset = (page - 1) * page_size

    df = fetch_df(f"""
        SELECT Num_Acc, an, mois, jour, hrmn, dep, agg, catr, circ, plan, prof,
               surf, vma, nbv, situ, lum, atm, int, col, nb_vehicules, nb_usagers
        FROM accident_full
        {where_sql}
        ORDER BY an DESC, mois_int DESC NULLS LAST, jour DESC
        LIMIT {page_size} OFFSET {offset}
    """, params)

    return df, total


def get_collisions(where_sql: str, params: list) -> pd.DataFrame:
    base_where = where_sql.strip()

    if base_where:
        sql = f"""
            SELECT col, COUNT(*) AS nb
            FROM accident_full
            {base_where} AND col IS NOT NULL
            GROUP BY col
            ORDER BY nb DESC
        """
    else:
        sql = """
            SELECT col, COUNT(*) AS nb
            FROM accident_full
            WHERE col IS NOT NULL
            GROUP BY col
            ORDER BY nb DESC
        """

    return fetch_df(sql, params)


def export_csv(where_sql: str, params: list) -> bytes:
    df = fetch_df(f"""
        SELECT Num_Acc, an, mois, jour, hrmn, dep, agg, catr, circ, plan, prof,
               surf, vma, nbv, situ, lum, atm, int, col, nb_vehicules, nb_usagers
        FROM accident_full
        {where_sql}
    """, params)

    return df.to_csv(index=False).encode("utf-8")
