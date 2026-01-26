import streamlit as st


def load_view():
    """Vue de conclusion

    Cette page est dédiée à la synthèse de vos résultats dans le but de préparer la
    remise finale (notebook, code, rapport). Elle reste une aide ; adaptez le
    contenu selon le projet.
    """

    st.set_page_config(page_title="Conclusion", layout="wide")

    st.title("Conclusion — Synthèse et recommandations")

    st.markdown(
        """
        ## Résumé rapide

        Rappelez brièvement :

        - l'objectif principal de votre projet (question à laquelle vous répondez),
        - les jeux de données utilisés,
        - les étapes majeures (prétraitement, analyses, modèles testés),
        - les résultats principaux (métriques, observations clés).

        Exemple synthétique :
        > Objectif : prédire la variable Y. Jeux de données : `data/xxx.csv`.
        > Méthodologie : nettoyage, features engineering, modèle X (score : 0.82).
        """
    )

    st.subheader("Principales découvertes")
    st.markdown(
        """
        - Indiquez 3 points clés que vous retenez de vos analyses.
        - Mentionnez les relations importantes entre variables (corrélations, effets observés).
        - Précisez les limites de vos conclusions (biais, données manquantes, taille d'échantillon).
        """
    )

    st.subheader("Limites et sources d'incertitude")
    st.markdown(
        """
        - Décrivez brièvement les limitations méthodologiques.
        - Proposez des moyens d'atténuer ces limites (plus de données, validations supplémentaires, méthodes robustes).
        """
    )

    st.subheader("Recommandations et prochaines étapes")
    st.markdown(
        """
        - Recommandation opérationnelle : que conseilleriez‑vous à un utilisateur / décideur ?
        - Prochaines étapes techniques : nouvelles features, tests, déploiement, monitoring.
        """
    )