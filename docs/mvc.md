# Architecture MVC — rappel pédagogique

MVC (Model — View — Controller) est une architecture logicielle qui aide à séparer les responsabilités :

- Model : Gère les données, le schéma et l'accès à la persistance (bases de données, fichiers (CSV entre autres)). Dans ce projet, les modèles sont dans `src/models/`.
- View : Interface utilisateur ; elle présente les données et capte les interactions Dans ce projet, les vues Streamlit sont dans `src/views/`.
- Controller : orchestre la logique métier, transforme les données fournies par le Model et les prépare pour la View. On les retrouvera dans `src/controllers`.

Pourquoi utiliser MVC ?

- Testabilité : la logique métier est isolée et plus facile à tester.
- Maintenabilité : modifications d'une couche sans impacter directement les autres.
- Clarté pour ceux qui relient votre code : chaque rôle est clairement identifié.

Mapping vers ce projet (exemples)

- Model : `src/models/database.py`, `src/models/session.py` servent à la gestion des accès à la base de données et à l'exécution de requêtes SQL par exemple.
- Controller : `src/controllers/*` — p.ex. `dataset_controller.py` fournit des fonctions `get_dataset()`, `get_summary()` et `plot_counts_by_year()` que la view `src/views/dataset.py` appelle.
- View : `src/views/*` — `home.py`, `analysis.py`, `conclusion.py` fournissent l'interface Streamlit : ce que les utilisateurs vont voir. Les views doivent être légères et s'appuyer sur les controllers.

Remarque : Dans ce dépôt, certaines vues et controllers (p.ex. la view `dataset` et le controller `dataset_controller`) sont fournis comme exemples pédagogiques :

- Ils démontrent comment on peut structurer les appels entre view et controller.
- Ce ne sont pas nécessairement des implémentations complètes pour production (par exemple le controller peut télécharger un CSV public pour l'exemple).

Conseils :

- Faites en sorte que la view reste sans logique métier : elle appelle le controller qui récupère et manipule la donnée, puis se contente d'afficher les résultats.
- Grandes tables : Préférer des samples ou des résumés dans la view, ou paginer l'affichage plutôt qu'afficher un long dataset.

Conclusion

L'architecture MVC est une bonne pratique pédagogique et technique. Dans ce dépôt, utilisez les controllers fournis comme point de départ et essayez d'extraire progressivement la logique métier et l'accès aux données dans des modules testables.