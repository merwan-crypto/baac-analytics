import streamlit as st

def load_view():
    """Vue d'analyse — endroit recommandé pour vos graphiques et visualisations.

    Recommandations :
    - Sur cette page, vous pouvez déposer vos graphiques (exploratoires, diagnostics, modèles de Machine Learning).
    - Ces conseils sont facultatifs : adaptez‑les selon votre projet et vos préférences pédagogiques.
    - Utilisez des légendes et interprétations courtes pour chaque graphique afin que le lecteur comprenne ce qu'il voit.
    """

    st.set_page_config(page_title="Analyse", layout="wide")

    st.title("Analyse — visualisations et exploration")

    st.markdown(
        """
        Sur cette page, vous devriez regrouper les graphiques les plus pertinents qui illustrent vos découvertes.

        Vous pouvez inclure par exemple :
        - Histogrammes et densités pour étudier la distribution d'une variable.
        - Boxplots pour repérer des valeurs extrêmes.
        - Heatmaps / matrices de corrélation pour explorer les relations entre variables.
        - Pairplots ou scatterplots pour visualiser des relations bivariées.
        - Graphiques temporels si vos données ont une composante date/heure.
        - Résultats de modèles de Machine Learning (courbes d'apprentissage, matrices de confusion, etc.).
        - Inférences via des boutons pour générer des prédictions à la volée...

        Conseils (facultatifs mais recommandés) :
        - Ajoutez un titre et une courte interprétation sous chaque graphique (2‑3 lignes).
        - Sauvegardez les figures et fournissez le code qui les génère pour la reproductibilité.
        - Si vous utilisez des notebooks, commentez les étapes de transformation qui précèdent chaque figure.
        """
    )

    st.subheader("Checklist pour vos visualisations")
    st.markdown(
        """
        - [ ] Choisir le(s) graphique(s) adaptés aux variables.
        - [ ] Vérifier la présence de valeurs manquantes et les traiter.
        - [ ] Annoter les graphiques (titre, légende, unités).
        - [ ] Rédiger 2‑3 phrases d'interprétation par graphique.
        - [ ] Garder le code reproductible (fonctions / scripts séparés).
        """
    )

    st.subheader("Note aux étudiants")
    st.info(
        "Ces suggestions sont des bonnes pratiques : vous n'êtes pas obligé·e·s de toutes les suivre, mais elles facilitent la lecture et l'évaluation de votre travail."
    )