import streamlit as st

from src.models.nosql_db import get_page_preferences, save_page_preferences
from src.models.nosql_db import set_last_page
from src.config.constants import DEPARTEMENT_LABELS
from src.controllers.dashboard_controller import (
    get_dimensions,
    build_where,
    build_where_usagers,
    get_kpi,
    get_accidents_par_mois,
    get_accidents_par_heure,
    get_gravite,
    get_accident_by_num,
    get_page_accidents,
    export_csv,
)


def reset_dataset_filters():
    st.session_state["dataset_an"] = []
    st.session_state["dataset_dep"] = []
    st.session_state["dataset_mois"] = []
    st.session_state["dataset_lum"] = []
    st.session_state["dataset_atm"] = []
    st.session_state["dataset_col"] = []
    st.session_state["dataset_catr"] = []
    st.session_state["dataset_surf"] = []
    st.session_state["dataset_vma"] = []


def load_view():
    # ==============================================================
    # Utilisateur + préférences
    # ==============================================================
    email = st.session_state.get("user_email", "guest")
    set_last_page(email, "dataset")
    prefs = get_page_preferences(email, "dataset") or {}

    st.title("🚗 Accidents de la route — Dashboard")
    st.caption("Vue d’ensemble interactive des accidents, véhicules et usagers")

    # ==============================================================
    # Chargement des dimensions
    # ==============================================================
    dims = get_dimensions()

    dims["deps"] = [
        str(d).zfill(2) if str(d).isdigit() and len(str(d)) < 2 else str(d)
        for d in dims["deps"]
    ]

    # ==============================================================
    # Sidebar — Filtres
    # ==============================================================
    with st.sidebar:
        st.header("Filtres")

        # ----------------------------
        # Années
        # ----------------------------
        annees_vals = [str(a) for a in dims["annees"]]

        if "dataset_an" not in st.session_state:
            saved_an = prefs.get("an", [])
            if isinstance(saved_an, str):
                saved_an = [saved_an] if saved_an else []
            st.session_state["dataset_an"] = [a for a in saved_an if str(a) in annees_vals]

        an = st.multiselect(
            "Année",
            annees_vals,
            key="dataset_an",
            placeholder="Toutes les années",
        )

        # ----------------------------
        # Départements
        # ----------------------------
        deps_vals = [str(d) for d in dims["deps"]]

        if "dataset_dep" not in st.session_state:
            saved_dep = prefs.get("dep", [])
            if isinstance(saved_dep, str):
                saved_dep = [saved_dep] if saved_dep else []
            st.session_state["dataset_dep"] = [d for d in saved_dep if str(d) in deps_vals]

        dep = st.multiselect(
            "Département",
            deps_vals,
            key="dataset_dep",
            placeholder="Tous les départements",
            format_func=lambda code: f"{code} - {DEPARTEMENT_LABELS.get(str(code), 'Inconnu')}",
        )

        # ----------------------------
        # Mois
        # ----------------------------
        if "dataset_mois" not in st.session_state:
            saved_mois = prefs.get("mois", [])
            st.session_state["dataset_mois"] = [m for m in saved_mois if m in dims["mois_vals"]]

        mois = st.multiselect(
            "Mois",
            dims["mois_vals"],
            key="dataset_mois",
            placeholder="Tous les mois",
        )

        st.divider()
        st.subheader("Conditions")
        lum = st.multiselect("Luminosité (lum)", dims["lum_vals"], key="dataset_lum")
        atm = st.multiselect("Atmosphère (atm)", dims["atm_vals"], key="dataset_atm")
        colf = st.multiselect("Collision (col)", dims["col_vals"], key="dataset_col")

        st.divider()
        st.subheader("Route / surface")
        catr = st.multiselect("Catégorie route (catr)", dims["catr_vals"], key="dataset_catr")
        surf = st.multiselect("État surface (surf)", dims["surf_vals"], key="dataset_surf")
        vma = st.multiselect("Vitesse max (vma)", dims["vma_vals"], key="dataset_vma")

        st.divider()
        st.button("Réinitialiser les filtres", on_click=reset_dataset_filters)

        st.caption("Pagination : 100 lignes par page")

    # ==============================================================
    # Sauvegarde des préférences
    # ==============================================================
    save_page_preferences(
        email,
        "dataset",
        {
            "an": an,
            "dep": dep,
            "mois": mois,
        },
    )

    # ==============================================================
    # Construction des filtres SQL
    # ==============================================================
    where_sql, params = build_where(an, dep, mois, lum, atm, colf, catr, surf, vma)
    where_sql_u, params_u = build_where_usagers(an, dep, mois)

    # ==============================================================
    # Tabs
    # ==============================================================
    tab1, tab2, tab3 = st.tabs(
        ["📊 Dashboard", "🔎 Fiche accident (Num_Acc)", "📋 Données"]
    )

    # ==============================================================
    # TAB 1 — Dashboard
    # ==============================================================
    with tab1:
        kpi = get_kpi(where_sql, params)
        c1, c2, c3 = st.columns(3)
        c1.metric("Accidents", kpi["accidents"])
        c2.metric("Véhicules impliqués", kpi["vehicules"])
        c3.metric("Usagers impliqués", kpi["usagers"])

        if kpi["accidents"] == 0:
            filtres_actifs = []

            if an:
                filtres_actifs.append(f"année(s) **{', '.join(map(str, an))}**")
            if dep:
                filtres_actifs.append(f"département(s) **{', '.join(dep)}**")
            if mois:
                filtres_actifs.append(f"mois **{', '.join(mois)}**")

            detail = " + ".join(filtres_actifs) if filtres_actifs else "les filtres sélectionnés"

            st.warning(
                f"⚠️ Aucune donnée pour {detail}. "
                "Les départements 01–09 ne sont disponibles qu'à partir de 2018.",
                icon="⚠️",
            )

        st.divider()

        g1, g2 = st.columns(2)

        with g1:
            st.subheader("📅 Accidents par mois")
            df_mois = get_accidents_par_mois(where_sql, params)

            if df_mois.empty:
                st.info("Aucune donnée.")
            else:
                st.bar_chart(df_mois.set_index("mois")[["nb"]])

        with g2:
            st.subheader("🕒 Accidents par heure")
            df_hour = get_accidents_par_heure(where_sql, params)

            if df_hour.empty:
                st.info("Aucune donnée horaire.")
            else:
                st.line_chart(df_hour.set_index("heure_label")[["nb"]])

        st.divider()

        st.subheader("⚠️ Répartition des victimes par gravité")
        st.caption("Lecture simple des conséquences des accidents sur les usagers")

        df_grav = get_gravite(where_sql_u, params_u, an, dep, mois)

        if df_grav.empty:
            st.info("Aucune donnée de gravité.")
        else:
            st.bar_chart(df_grav.set_index("grav_label")[["nb"]])

            st.dataframe(
                df_grav[["grav_label", "nb"]].rename(
                    columns={
                        "grav_label": "Gravité",
                        "nb": "Nombre de victimes",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )

    # ==============================================================
    # TAB 2 — Fiche accident
    # ==============================================================
    with tab2:
        st.subheader("🔎 Rechercher un accident par Num_Acc")
        st.caption("Affichage détaillé d’un accident, de ses véhicules et de ses usagers")

        num_acc = st.text_input("Num_Acc", placeholder="Ex: 200500000001")

        if num_acc:
            details = get_accident_by_num(num_acc)

            if details["accident"].empty:
                st.error("Aucun accident trouvé avec ce Num_Acc.")
            else:
                df_accident = details["accident"].copy()
                df_vehicules = details["vehicules"].copy()
                df_usagers = details["usagers"].copy()

                colr1, colr2 = st.columns(2)
                colr1.metric("Véhicules", len(df_vehicules) if not df_vehicules.empty else 0)
                colr2.metric("Usagers", len(df_usagers) if not df_usagers.empty else 0)

                st.divider()

                df_accident = df_accident.rename(
                    columns={
                        "Num_Acc": "Numéro accident",
                        "num_acc": "Numéro accident",
                        "jour": "Jour",
                        "mois": "Mois",
                        "an": "Année",
                        "hrmn": "Heure",
                        "lum": "Luminosité",
                        "dep": "Département",
                        "com": "Commune",
                        "agg": "Agglomération",
                        "int": "Intersection",
                        "atm": "Atmosphère",
                        "col": "Type de collision",
                        "adr": "Adresse",
                        "lat": "Latitude",
                        "long": "Longitude",
                        "catr": "Catégorie route",
                        "voie": "Voie",
                        "circ": "Circulation",
                        "nbv": "Nb voies",
                        "prof": "Profil",
                        "plan": "Plan",
                        "surf": "État surface",
                        "infra": "Infrastructure",
                        "situ": "Situation",
                        "vma": "Vitesse max autorisée",
                    }
                )

                ordre_accident = [
                    "Numéro accident",
                    "Jour",
                    "Mois",
                    "Année",
                    "Heure",
                    "Département",
                    "Commune",
                    "Adresse",
                    "Luminosité",
                    "Atmosphère",
                    "Type de collision",
                    "Agglomération",
                    "Intersection",
                    "Catégorie route",
                    "Voie",
                    "Circulation",
                    "Nb voies",
                    "Profil",
                    "Plan",
                    "État surface",
                    "Infrastructure",
                    "Situation",
                    "Vitesse max autorisée",
                    "Latitude",
                    "Longitude",
                ]
                df_accident = df_accident[[c for c in ordre_accident if c in df_accident.columns]]

                st.markdown("### ✅ Accident")
                st.dataframe(df_accident, use_container_width=True, height=220)

                df_vehicules = df_vehicules.rename(
                    columns={
                        "Num_Acc": "Numéro accident",
                        "num_acc": "Numéro accident",
                        "id_vehicule": "ID véhicule",
                        "num_veh": "Num véhicule",
                        "senc": "Sens circulation",
                        "catv": "Catégorie véhicule",
                        "obs": "Obstacle fixe heurté",
                        "obsm": "Obstacle mobile heurté",
                        "choc": "Point de choc initial",
                        "manv": "Manœuvre principale",
                        "motor": "Motorisation",
                    }
                )

                ordre_vehicules = [
                    "ID véhicule",
                    "Num véhicule",
                    "Catégorie véhicule",
                    "Sens circulation",
                    "Obstacle fixe heurté",
                    "Obstacle mobile heurté",
                    "Point de choc initial",
                    "Manœuvre principale",
                    "Motorisation",
                ]
                df_vehicules = df_vehicules[[c for c in ordre_vehicules if c in df_vehicules.columns]]

                st.markdown("### 🚙 Véhicules")
                st.dataframe(df_vehicules, use_container_width=True, height=260)

                df_usagers = df_usagers.drop(
                    columns=["age", "mois_int", "grav_int"],
                    errors="ignore",
                ).rename(
                    columns={
                        "Num_Acc": "Numéro accident",
                        "num_acc": "Numéro accident",
                        "id_vehicule": "ID véhicule",
                        "num_veh": "Num véhicule",
                        "place": "Place",
                        "catu": "Catégorie usager",
                        "grav": "Gravité",
                        "grav_label": "Gravité",
                        "sexe": "Sexe",
                        "an_nais": "Année naissance",
                        "trajet": "Trajet",
                        "secu": "Équipement sécurité",
                        "locp": "Localisation piéton",
                        "actp": "Action piéton",
                        "etatp": "État piéton",
                    }
                )

                ordre_usagers = [
                    "ID véhicule",
                    "Num véhicule",
                    "Catégorie usager",
                    "Place",
                    "Gravité",
                    "Sexe",
                    "Année naissance",
                    "Trajet",
                    "Équipement sécurité",
                    "Localisation piéton",
                    "Action piéton",
                    "État piéton",
                ]
                df_usagers = df_usagers[[c for c in ordre_usagers if c in df_usagers.columns]]

                st.markdown("### 🧍 Usagers")
                st.dataframe(df_usagers, use_container_width=True, height=420)

    # ==============================================================
    # TAB 3 — Données paginées + export
    # ==============================================================
    with tab3:
        st.subheader("📋 Tableau accidents")
        st.caption("Consultation paginée des données filtrées et export CSV")

        page_size = 100
        _, total = get_page_accidents(where_sql, params, page=1, page_size=page_size)
        nb_pages = max(1, (total + page_size - 1) // page_size)

        colp1, colp2, _ = st.columns([1, 1, 3])

        with colp1:
            page = st.number_input(
                "Page",
                min_value=1,
                max_value=nb_pages,
                value=1,
                step=1,
            )

        with colp2:
            st.metric("Pages", nb_pages)

        df_table, total = get_page_accidents(where_sql, params, page=page, page_size=page_size)

        st.caption(f"{total} lignes au total — page {page}/{nb_pages} — {len(df_table)} lignes affichées")
        st.dataframe(df_table, use_container_width=True, height=520)

        st.divider()
        st.subheader("⬇️ Télécharger le résultat filtré")
        st.caption("L’export n’est généré que lorsque tu cliques, pour garder l’app fluide.")

        if st.button("Préparer l’export CSV"):
            with st.spinner("Génération du CSV..."):
                csv_data = export_csv(where_sql, params)
            st.download_button(
                "Télécharger CSV (filtré)",
                data=csv_data,
                file_name="accidents_full_filtre.csv",
                mime="text/csv",
            )