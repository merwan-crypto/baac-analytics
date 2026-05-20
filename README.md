# 🚗 Projet Fil Rouge – Analyse des accidents routiers

## 📌 Objectif du projet

Ce projet consiste à développer une application permettant d’explorer et d’analyser les données d’accidents routiers en France.

L’objectif est de proposer une interface interactive permettant :

* d’analyser les tendances
* de visualiser les données
* d’explorer différents indicateurs liés aux accidents

---

## ⚙️ Technologies utilisées

* **Python**
* **Streamlit** (interface web)
* **DuckDB** (base de données analytique)
* **SQLite** (gestion des utilisateurs)
* **TinyDB** (préférences utilisateur)
* **Pandas** (traitement des données)

---

## 🚀 Fonctionnalités principales

* 🔐 Authentification (connexion / inscription)
* 📊 Tableau de bord interactif
* 📈 Analyse des accidents (par période, gravité, etc.)
* 👤 Gestion du profil utilisateur
* 📂 Exploration des datasets

---

## 📁 Structure du projet

```text
projet-fil-rouge-merwan-crypto/
│
├── main.py                # Point d’entrée de l’application
├── requirements.txt       # Dépendances Python
├── README.md              # Présentation du projet
│
├── data/                  # Données et bases
│   ├── accidents.duckdb
│   ├── users.db
│   ├── user_preferences.json
│
├── docs/                  # Documentation technique
│   ├── mvc.md
│   └── structure.md
│
├── scripts/               # Scripts techniques
│   ├── init_db.py         # Création de la base DuckDB
│   └── inject_2009.py     # Correction / enrichissement des données
│
├── src/                   # Code source (architecture MVC)
│   ├── controllers/
│   ├── models/
│   ├── views/
│   ├── utils/
│   ├── config/
│   └── assets/
│
└── tests/                 # Tests (optionnel)
```

---

## 🧠 Architecture

Le projet suit une architecture de type **MVC (Model - View - Controller)** :

* **Models** : gestion des données (DuckDB, SQLite)
* **Views** : interface utilisateur (Streamlit)
* **Controllers** : logique métier et traitement

---

## 💻 Installation

1. Cloner le projet ou extraire l’archive

2. Installer les dépendances :

```bash
pip install -r requirements.txt
```

---

## ▶️ Lancement de l’application

```bash
streamlit run main.py
```

---

## 📊 Données

Les données utilisées proviennent de bases d’accidents routiers.

* Stockage principal : **DuckDB**
* Sources : fichiers CSV nettoyés et agrégés

---

## 🔧 Scripts disponibles

* `init_db.py`
  → Permet de recréer la base DuckDB à partir des fichiers CSV

* `inject_2009.py`
  → Permet d’ajouter/corriger certaines données dans les fichiers sources

---

## ⚠️ Remarques

* Les fichiers `__pycache__` ne sont pas inclus (générés automatiquement par Python)
* Le fichier de session est réinitialisé automatiquement au lancement

---

## 👤 Auteur

Projet réalisé dans le cadre d’un projet fil rouge en data / développement.

---

## 📌 Améliorations possibles

* Ajout de visualisations plus avancées
* Optimisation des performances
* Ajout de tests unitaires complets
* Déploiement en ligne
