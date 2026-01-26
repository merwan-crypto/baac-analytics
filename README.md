# Projet Streamlit : Template de démarrage

## Auteurs

*Marouan K. : marouan@datarockstars.ai*

*Bilel O. : bilel@datarockstars.ai*

*Matis C. : matis@datarockstars.ai*

## Démarrage

- Naviguez jusqu'à ce dossier :
  ```
  cd projet-fil-rouge-{username_github}
  ```
- Vérifiez que vous voyez bien les fichiers de ce dépôt lorsque vous exécutez `ls`.

### MacOS / Linux

- Dans le terminal, exécutez la commande suivante pour démarrer le projet : 
  ```
  bash setup.sh
  ```
  Vous n'aurez pas à le faire les prochaines fois.

- Exécutez maintenant la commande suivante pour afficher le site crée à l'aide de Streamlit :
  ```
  bash run.sh
  ```

### Windows

Exécutez les commandes suivantes, dans l'ordre :

- Pour installer les librairies utiles et initialiser la base de données : 
    ```
    pip install --update pip
    pip install -r requirements.txt
    python3 setup.py
    ```

- Pour lancer votre application Streamlit :
    ```
    streamlit run main.py
    ```

## Documentation

Une documentation vous permettant de bien démarrer et de comprendre le code est mise à votre disposition dans le répertoire `docs` de ce même projet.