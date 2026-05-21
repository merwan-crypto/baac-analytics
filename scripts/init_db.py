"""
init_db.py — Pipeline d'ingestion DuckDB pour les données d'accidents routiers
Corrections appliquées :
  ✅ Validation des chemins CSV (sécurité)
  ✅ Transaction + gestion d'erreurs
  ✅ Index sur Num_Acc, an, dep
  ✅ Un seul scan pour les dimensions
  ✅ Table ref_mois (mapping mois → entier)
  ✅ Matérialisation de usagers_clean
  ✅ SELECT * sur les tables sources (compatible avec tout schéma CSV)
  ✅ [PATCH] Filtre age_accident sur usagers_clean :
       - Exclut age_accident >= 100 (valeur sentinel BAAC, an_nais=1924)
       - Exclut age_accident < 0    (erreurs de saisie)
       - Exclut age_accident IS NULL (an_nais non renseigné)
       Impact : -23 767 entrées (1,1 % des conducteurs bruts)
"""

import duckdb
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DB_PATH   = "data/accidents.duckdb"
CSV_CARAC = "data/caract_2005_2024_clean.csv"
CSV_LIEUX = "data/lieux_2005_2024_clean1.csv"
CSV_VEH   = "data/vehicules_2005_2024_clean1.csv"
CSV_USG   = "data/usagers_2005_2024_clean1.csv"

# ---------------------------------------------------------------------------
# 🔴 SÉCURITÉ — Validation des chemins CSV
# ---------------------------------------------------------------------------
def _validate_csv(path_str: str) -> str:
    """Vérifie qu'un chemin CSV est valide, existant et de bonne extension."""
    p = Path(path_str).resolve()
    if p.suffix.lower() != ".csv":
        raise ValueError(f"Extension invalide (attendu .csv) : {p}")
    if not p.exists():
        raise FileNotFoundError(f"Fichier CSV introuvable : {p}")
    return str(p)


def main() -> None:
    # Validation en amont — avant toute connexion DB
    csv_carac = _validate_csv(CSV_CARAC)
    csv_lieux = _validate_csv(CSV_LIEUX)
    csv_veh   = _validate_csv(CSV_VEH)
    csv_usg   = _validate_csv(CSV_USG)

    con = duckdb.connect(DB_PATH)

    # -----------------------------------------------------------------------
    # 🟡 TRANSACTION — rollback complet en cas d'erreur
    # -----------------------------------------------------------------------
    try:
        con.execute("BEGIN TRANSACTION")

        # -------------------------------------------------------------------
        # 1. TABLES SOURCES
        # -------------------------------------------------------------------
        print("1/7 — Création des tables sources...")

        con.execute(f"""
        CREATE OR REPLACE TABLE caracteristiques AS
        SELECT
            * EXCLUDE (dep),
            CASE
                WHEN length(trim(dep)) = 1 THEN '0' || trim(dep)
                ELSE trim(dep)
            END AS dep
        FROM read_csv_auto(
            '{csv_carac}',
            encoding='utf-8',
            types={{
                'Num_Acc' : 'VARCHAR',
                'dep'     : 'VARCHAR',
                'com'     : 'VARCHAR',
                'an'      : 'INTEGER',
                'mois'    : 'VARCHAR',
                'jour'    : 'INTEGER',
                'hrmn'    : 'VARCHAR',
                'lat'     : 'VARCHAR',
                'long'    : 'VARCHAR'
            }}
        );
        """)

        con.execute(f"""
        CREATE OR REPLACE TABLE lieux AS
        -- Déduplique lieux : certains Num_Acc ont plusieurs lignes dans le CSV source
        -- On garde la première ligne par Num_Acc (QUALIFY + ROW_NUMBER)
        SELECT * EXCLUDE (rn)
        FROM (
            SELECT *,
                   ROW_NUMBER() OVER (PARTITION BY Num_Acc ORDER BY Num_Acc) AS rn
            FROM read_csv_auto(
                '{csv_lieux}',
                types={{'Num_Acc': 'VARCHAR'}}
            )
        )
        WHERE rn = 1;
        """)

        con.execute(f"""
        CREATE OR REPLACE TABLE vehicules AS
        SELECT *
        FROM read_csv_auto(
            '{csv_veh}',
            types={{
                'Num_Acc'    : 'VARCHAR',
                'id_vehicule': 'VARCHAR',
                'num_veh'    : 'VARCHAR'
            }}
        );
        """)

        con.execute(f"""
        CREATE OR REPLACE TABLE usagers AS
        SELECT *
        FROM read_csv_auto(
            '{csv_usg}',
            types={{
                'Num_Acc'    : 'VARCHAR',
                'id_usager'  : 'VARCHAR',
                'id_vehicule': 'VARCHAR',
                'num_veh'    : 'VARCHAR',
                'grav'       : 'VARCHAR',
                'an_nais'    : 'VARCHAR'
            }}
        );
        """)

        # -------------------------------------------------------------------
        # 2. 🔵 TABLE DE RÉFÉRENCE mois → entier (plus de CASE inline dupliqué)
        # -------------------------------------------------------------------
        print("2/7 — Création de ref_mois...")

        con.execute("""
        CREATE OR REPLACE TABLE ref_mois (mois_label VARCHAR, mois_int INTEGER);
        INSERT INTO ref_mois VALUES
            ('Janvier',   1), ('Février',  2), ('Fevrier',   2),
            ('Mars',      3), ('Avril',    4), ('Mai',       5),
            ('Juin',      6), ('Juillet',  7), ('Août',      8),
            ('Aout',      8), ('Septembre',9), ('Octobre',  10),
            ('Novembre', 11), ('Décembre',12), ('Decembre', 12);
        """)

        # -------------------------------------------------------------------
        # 3. VUE + TABLE MATÉRIALISÉE accident_full
        # -------------------------------------------------------------------
        print("3/7 — Création de accident_full...")

        con.execute("""
        CREATE OR REPLACE VIEW v_accident_full AS
        WITH
        veh AS (
            -- Compter via num_veh (compatible toutes années, id_vehicule NULL avant 2019)
            SELECT Num_Acc, COUNT(DISTINCT num_veh) AS nb_vehicules
            FROM vehicules
            GROUP BY Num_Acc
        ),
        usg AS (
            -- Compter via num_veh + place (id_usager NULL avant 2019)
            SELECT Num_Acc, COUNT(*) AS nb_usagers
            FROM usagers
            GROUP BY Num_Acc
        )
        SELECT
            c.* EXCLUDE (an),
            -- ✅ 2009 : an est NULL dans le CSV source → on le déduit depuis Num_Acc
            COALESCE(
                c.an,
                TRY_CAST(LEFT(CAST(c.Num_Acc AS VARCHAR), 4) AS INTEGER)
            ) AS an,
            rm.mois_int,
            l.* EXCLUDE (Num_Acc),
            COALESCE(veh.nb_vehicules, 0) AS nb_vehicules,
            COALESCE(usg.nb_usagers,   0) AS nb_usagers
        FROM caracteristiques c
        LEFT JOIN ref_mois rm  ON TRIM(c.mois) = rm.mois_label
        LEFT JOIN lieux     l  ON l.Num_Acc    = c.Num_Acc
        LEFT JOIN veh          ON veh.Num_Acc  = c.Num_Acc
        LEFT JOIN usg          ON usg.Num_Acc  = c.Num_Acc;
        """)

        con.execute("""
        CREATE OR REPLACE TABLE accident_full AS
        SELECT * FROM v_accident_full;
        """)

        # -------------------------------------------------------------------
        # 4. 🔴 INDEX sur les clés de jointure et filtres fréquents
        # -------------------------------------------------------------------
        print("4/7 — Création des index...")

        for table, col in [
            ("caracteristiques", "Num_Acc"),
            ("lieux",            "Num_Acc"),
            ("vehicules",        "Num_Acc"),
            ("usagers",          "Num_Acc"),
            ("accident_full",    "Num_Acc"),
            ("accident_full",    "an"),
            ("accident_full",    "dep"),
        ]:
            idx_name = f"idx_{table}_{col.lower()}"
            con.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({col});")

        # -------------------------------------------------------------------
        # 5. TABLE MATÉRIALISÉE usagers_clean (🔵 remplace la vue recalculée)
        # -------------------------------------------------------------------
        # [PATCH] Filtre age_accident appliqué directement dans la table source :
        #
        #   • age_accident >= 100 → valeur sentinel BAAC (an_nais = 1924 utilisé
        #     pour coder "année de naissance inconnue"). Ces 6 323 entrées ne
        #     représentent pas de vrais conducteurs centenaires.
        #
        #   • age_accident < 0   → erreur de saisie (an_nais > an accident).
        #
        #   • age_accident IS NULL → an_nais non renseigné dans le BAAC.
        #
        #   Les conducteurs de 16-17 ans (50 500 entrées) sont CONSERVÉS :
        #   ils sont légalement valides en France (cyclomoteur AM, conduite
        #   accompagnée AAC, moto légère A1).
        #
        #   Impact total : -23 767 usagers (1,1 % du brut), négligeable.
        # -------------------------------------------------------------------
        print("5/7 — Création de usagers_clean...")

        con.execute("""
        CREATE OR REPLACE TABLE usagers_clean AS
        SELECT
            u.*,
            -- Jointure accident
            a.an,
            a.mois,
            a.mois_int,
            a.dep,
            -- Gravité normalisée
            CASE lower(trim(u.grav))
                WHEN 'indemne'                    THEN 1
                WHEN 'tué'                        THEN 2
                WHEN 'tue'                        THEN 2
                WHEN 'blessé hospitalisé'         THEN 3
                WHEN 'blesse hospitalise'         THEN 3
                WHEN 'blessé hospitalise'         THEN 3
                WHEN 'blessé léger'               THEN 4
                WHEN 'blesse leger'               THEN 4
                WHEN 'blessé leger'               THEN 4
                ELSE NULL
            END AS grav_int,
            -- Âge au moment de l'accident (calculé depuis an_nais et l'année de l'accident)
            CAST(a.an - try_cast(u.an_nais AS INTEGER) AS INTEGER) AS age_accident
        FROM usagers u
        LEFT JOIN accident_full a ON a.Num_Acc = u.Num_Acc
        -- [PATCH] Filtre sur age_accident :
        --   - Exclut les an_nais non castables (non numériques)
        --   - Exclut age >= 100 (sentinel BAAC an_nais=1924)
        --   - Exclut age < 0   (erreur de saisie)
        WHERE try_cast(u.an_nais AS INTEGER) IS NOT NULL
          AND a.an IS NOT NULL
          AND (a.an - try_cast(u.an_nais AS INTEGER)) >= 0
          AND (a.an - try_cast(u.an_nais AS INTEGER)) < 100;
        """)

        # Vue légère pour compatibilité ascendante avec le code Streamlit existant
        con.execute("""
        CREATE OR REPLACE VIEW v_usagers_detail_clean AS
        SELECT * FROM usagers_clean;
        """)

        # -------------------------------------------------------------------
        # 6. 🟡 DIMENSIONS — un seul scan de accident_full
        # -------------------------------------------------------------------
        print("6/7 — Création des tables de dimensions...")

        # Snapshot unique pour toutes les dimensions issues de accident_full
        con.execute("""
        CREATE OR REPLACE TEMP TABLE _dims_snapshot AS
        SELECT DISTINCT an, dep, mois, mois_int, lum, atm, col, catr, surf, vma
        FROM accident_full;
        """)

        dim_queries = {
            "dim_annees": "SELECT DISTINCT an   FROM _dims_snapshot WHERE an   IS NOT NULL ORDER BY an DESC",
            "dim_deps"  : "SELECT DISTINCT dep  FROM _dims_snapshot WHERE dep  IS NOT NULL ORDER BY dep",
            "dim_mois"  : "SELECT DISTINCT mois FROM _dims_snapshot WHERE mois IS NOT NULL ORDER BY mois_int",
            "dim_lum"   : "SELECT DISTINCT lum  FROM _dims_snapshot WHERE lum  IS NOT NULL ORDER BY lum",
            "dim_atm"   : "SELECT DISTINCT atm  FROM _dims_snapshot WHERE atm  IS NOT NULL ORDER BY atm",
            "dim_col"   : "SELECT DISTINCT col  FROM _dims_snapshot WHERE col  IS NOT NULL ORDER BY col",
            "dim_catr"  : "SELECT DISTINCT catr FROM _dims_snapshot WHERE catr IS NOT NULL ORDER BY catr",
            "dim_surf"  : "SELECT DISTINCT surf FROM _dims_snapshot WHERE surf IS NOT NULL ORDER BY surf",
            "dim_vma"   : "SELECT DISTINCT vma  FROM _dims_snapshot WHERE vma  IS NOT NULL ORDER BY vma",
        }

        for table, query in dim_queries.items():
            con.execute(f"CREATE OR REPLACE TABLE {table} AS {query};")

        # dim_grav depuis usagers_clean (déjà matérialisé)
        con.execute("""
        CREATE OR REPLACE TABLE dim_grav AS
        SELECT DISTINCT grav_int AS grav
        FROM usagers_clean
        WHERE grav_int BETWEEN 1 AND 4
        ORDER BY grav;
        """)

        # -------------------------------------------------------------------
        # 7. COMMIT
        # -------------------------------------------------------------------
        con.execute("COMMIT")
        print("7/7 — Transaction commitée ✅")

    except Exception as e:
        con.execute("ROLLBACK")
        con.close()
        raise RuntimeError(f"❌ Échec de l'initialisation — rollback effectué : {e}") from e

    # -----------------------------------------------------------------------
    # DIAGNOSTIC
    # -----------------------------------------------------------------------
    print("\n========== DIAGNOSTIC ==========")
    print("Accidents   :", con.execute("SELECT COUNT(*) AS n FROM accident_full").fetchdf())
    print("Usagers     :", con.execute("SELECT COUNT(*) AS n FROM usagers").fetchdf())
    print("Usagers clean:", con.execute("SELECT COUNT(*) AS n FROM usagers_clean").fetchdf())
    print("Age min/max dans usagers_clean :")
    print(con.execute("""
        SELECT MIN(age_accident) AS age_min, MAX(age_accident) AS age_max
        FROM usagers_clean
        WHERE catu = 'Conducteur'
    """).fetchdf())
    print("Grav clean  :")
    print(con.execute("""
        SELECT grav_int, COUNT(*) AS n
        FROM usagers_clean
        GROUP BY grav_int
        ORDER BY grav_int
    """).fetchdf())
    print("Top grav brut:")
    print(con.execute("""
        SELECT grav, COUNT(*) AS n
        FROM usagers
        GROUP BY grav
        ORDER BY n DESC
        LIMIT 10
    """).fetchdf())
    print("================================\n")

    con.close()
    print(f"✅ Base prête : {DB_PATH}")


if __name__ == "__main__":
    main()
