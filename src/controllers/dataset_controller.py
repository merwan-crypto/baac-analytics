# Dataset controller (MVC) — Responsable de la logique métier et de l'accès aux données pour la vue dataset.py.

# Rôle du controller :
# - récupérer les données via le model (ici, simplifié en interne),
# - préparer/transformer les données pour la vue,
# - exposer des fonctions simples que la vue peut appeler sans connaître
#   les détails d'implémentation.

import pandas as pd
import matplotlib.pyplot as plt


class DatasetController:
    """Controller minimal pour la page `dataset`.

    Méthodes utiles pour la view :
    - get_dataset() -> pd.DataFrame
    - get_summary(df) -> pd.DataFrame
    - plot_counts_by_year(df) -> matplotlib.figure.Figure
    """

    @staticmethod
    def get_dataset() -> pd.DataFrame:
        """Retourne un DataFrame d'exemple.

        Ici on télécharge un CSV public (dataset d'exemple).
        """
        url = (
            "https://github.com/ipython-books/"
            "cookbook-2nd-data/blob/master/"
            "federer.csv?raw=true"
        )
        df = pd.read_csv(url, parse_dates=["start date"], dayfirst=True)
        # Exemple de nettoyage minimal : s'assurer que la colonne date est bien en datetime
        df["start date"] = pd.to_datetime(df["start date"], errors="coerce")
        return df

    @staticmethod
    def get_summary(df: pd.DataFrame) -> pd.DataFrame:
        """Retourne des statistiques descriptives utiles pour la view."""
        # Nb : retournons la description transposée pour affichage plus lisible
        summary = df.describe(include="all", datetime_is_numeric=True).transpose()
        # Convertir tous les Timestamp en ISO8601 puis tout en str pour éviter les types mixtes
        summary = summary.applymap(lambda x: x.isoformat() if isinstance(x, pd.Timestamp) else x)
        summary = summary.astype(str)
        return summary

    @staticmethod
    def plot_counts_by_year(df: pd.DataFrame) -> plt.Figure:
        """Crée une figure matplotlib montrant le nombre d'événements par année.

        La view peut alors afficher la figure via `st.pyplot(fig)`.
        """
        fig, ax = plt.subplots(figsize=(8, 3.5))
        if "start date" in df.columns:
            years = df["start date"].dt.year.dropna().astype(int)
            counts = years.value_counts().sort_index()
            counts.plot(kind="bar", ax=ax, color="#2b8cbe")
            ax.set_title("Nombre d'événements / matches par année")
            ax.set_xlabel("Année")
            ax.set_ylabel("Nombre")
            plt.tight_layout()
        else:
            ax.text(0.5, 0.5, "Pas de colonne 'start date' disponible", ha="center")
        return fig
