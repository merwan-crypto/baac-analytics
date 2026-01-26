# Structure du projet

Ce fichier décrit la structure du dépôt et le rôle des principaux fichiers et dossiers. Il s'agit d'une vue d'ensemble destinée à vous faire découvrir le projet.

### Racine du projet

- `README.md` : Documentation principale du dépôt : elle vous indique comment lancer l'application.
- `requirements.txt` : Liste des librairies Python requises pour lancer l'application.
- `run.sh`, `setup.sh` : Scripts d'aide à l'exécution / à l'installation.
- `main.py` : Point d'entrée de l'application Streamlit (lance l'interface web) : c'est depuis ce code qu'on accède à tous les autres grâce à des routes.
- `utils` : Fonctions utilitaires partagées et petites abstractions réutilisées dans l'application.
- `PATHS.py` : Constantes de chemins/paramètres globaux (utilisé par le projet) : c'est dans ce fichier que l'on contrôle ce qui s'affiche sur la barre de navigation de l'application par exemple.
- `.gitignore` : Noms des fichiers / dossiers qui ne seront pas suivis par Git (et donc, non synchronisés sur Github).

### Dossier `data/`

Contient la base de données des utilisateurs de l'application `users.db`. Il vous faudra ajouter vos jeux de données sous la forme d'une base de données ou de fichiers CSV.

**P.S :** Ne commitez pas de données sensibles.

### Dossier `src/`

Contient l'essentiel du code source de l'application.

- `router.py` : Logique de routage interne (navigation entre vues dans l'app Streamlit).
- `controllers/` : Contrôleurs (logique métier/coordination). Exemples : `auth.py`, `signup.py`, `dataset_controller.py`.
- `models/` : Accès aux données et gestion de la persistance (ex. `database.py`, `session.py`).
- `views/` : Vues Streamlit (UI). Exemples : `home.py`, `analysis.py`, `conclusion.py`, `dataset.py`, `login.py`.
- `assets/` : Ressources statiques (fichiers CSS, images).

### Dossier `notebooks/`

Contient les Notebooks d'exploration et démonstration. Utiles pour bien commencer et pour la reproductibilité.

### Dossiers `tests/`

Emplacement recommandé pour les tests unitaires. Nommer les fichiers `test_*.py` pour être compatibles avec `pytest` et `unittest`.