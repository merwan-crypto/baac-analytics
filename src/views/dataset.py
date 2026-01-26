# Vue `dataset` (View dans MVC)

# Cette view est responsable uniquement de l'affichage. Elle appelle le controller
# pour obtenir des données prêtes à être affichées et ne comporte pas de logique
# métier lourde.

import streamlit as st
from src.controllers.dataset_controller import DatasetController

def load_view():
    """Vue de description du jeu de données
    
    Charge et affiche la page de présentation du Dataset en respectant MVC.

    La vue :
    - appelle le controller pour récupérer les données,
    - affiche des textes et des actions (boutons),
    - présente des visualisations préparées par le controller.
    """

    st.set_page_config(page_title="Jeu de données", layout="wide")

    st.title("Jeu de données du projet")

    # Instancier / utiliser le controller pour obtenir le dataset
    controller = DatasetController()
    df = controller.get_dataset() # Appel au controller (c'est lui qui gère la logique métier)

    st.subheader("Aperçu des données")
    st.markdown(
        """
        Ce projet utilise un jeu de données des matchs disputés par Roger Federer de 1998 à 2003.
        
        Il est public et disponible gratuitement sur https://github.com/ipython-books/cookbook-2nd-data/blob/master/federer.csv?raw=true.
        """
    )

    # Afficher un aperçu des données via le controller
    st.dataframe(df.head(10))

    # Afficher un résumé statistique préparé par le controller
    st.subheader("Statistiques descriptives")
    summary = controller.get_summary(df)
    st.dataframe(summary)

    # Visualisation fournie par le controller
    st.subheader("Visualisation : événements par année")
    fig = controller.plot_counts_by_year(df)
    st.pyplot(fig)