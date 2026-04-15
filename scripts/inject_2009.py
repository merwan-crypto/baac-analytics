"""
inject_2009.py
Nettoie caracteristiques_2009.csv (format brut codes numériques)
et l'injecte dans caract_2005_2024_clean.csv.
"""
import pandas as pd

# ─── Mappings codes → labels (identiques au nettoyage original) ───────────

MOIS = {
    1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
    5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
    9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
}

LUM = {
    1: "Plein jour",
    2: "Crépuscule ou aube",
    3: "Nuit sans éclairage public",
    4: "Nuit avec éclairage public non allumé",
    5: "Nuit avec éclairage public allumé",
}

AGG = {1: "Hors agglomération", 2: "En agglomération"}

INT = {
    1: "Hors intersection",
    2: "Intersection en X",
    3: "Intersection en T",
    4: "Intersection en Y",
    5: "Intersection à plus de 4 branches",
    6: "Giratoire",
    7: "Place",
    8: "Passage à niveau",
    9: "Autre intersection",
}

ATM = {
    1: "Normale",
    2: "Pluie légère",
    3: "Pluie forte",
    4: "Neige - grêle",
    5: "Brouillard - fumée",
    6: "Vent fort - tempête",
    7: "Temps éblouissant",
    8: "Temps couvert",
    9: "Autre",
}

COL = {
    1: "Deux véhicules - frontale",
    2: "Deux véhicules - par l'arrière",
    3: "Deux véhicules - par le côté",
    4: "Trois véhicules et plus - en chaîne",
    5: "Trois véhicules et plus - collisions multiples",
    6: "Autre collision",
    7: "Sans collision",
}


# ─── Chargement 2009 brut ─────────────────────────────────────────────────
print("Chargement caracteristiques_2009.csv...")
df09 = pd.read_csv(
    'caracteristiques_2009.csv',
    sep='\t', encoding='latin-1', low_memory=False
)
# Nettoyer les colonnes texte des caractères non-UTF8
for col in df09.select_dtypes(include='object').columns:
    df09[col] = df09[col].apply(
        lambda x: x.encode('latin-1', errors='ignore').decode('utf-8', errors='ignore') if isinstance(x, str) else x
    )
print(f"  {len(df09):,} lignes chargées")

# ─── Nettoyage ────────────────────────────────────────────────────────────

# an : 9 → 2009
df09['an'] = 2009

# mois : int → texte
df09['mois'] = df09['mois'].map(MOIS)

# hrmn : 2030 → "20:30"
def format_hrmn(v):
    try:
        s = str(int(v)).zfill(4)
        return f"{s[:2]}:{s[2:]}"
    except:
        return None
df09['hrmn'] = df09['hrmn'].apply(format_hrmn)

# lum, agg, int, atm, col → texte
df09['lum'] = df09['lum'].map(LUM)
df09['agg'] = df09['agg'].map(AGG)
df09['int'] = df09['int'].map(INT)
df09['atm'] = df09['atm'].map(ATM)
df09['col'] = df09['col'].map(COL)

# dep : 440 → 44  (supprimer le dernier chiffre si 3 chiffres)
def clean_dep(d):
    try:
        s = str(int(d))
        if len(s) == 3:
            return int(s[:2])  # 440 → 44
        return int(s)
    except:
        return None
df09['dep'] = df09['dep'].apply(clean_dep)

# Supprimer colonne 'gps' absente du CSV nettoyé
if 'gps' in df09.columns:
    df09 = df09.drop(columns=['gps'])

# Nettoyer lat/long : remplacer '-', '0', '0.0' par NaN
import numpy as np
for col in ['lat', 'long']:
    df09[col] = pd.to_numeric(df09[col], errors='coerce')
    df09[col] = df09[col].replace(0.0, np.nan)

# Réordonner les colonnes comme le CSV nettoyé
COLS = ['Num_Acc', 'an', 'mois', 'jour', 'hrmn', 'lum',
        'agg', 'int', 'atm', 'col', 'com', 'adr', 'lat', 'long', 'dep']
df09 = df09.reindex(columns=COLS)

print(f"  Aperçu après nettoyage :")
print(df09.head(3).to_string())

# ─── Chargement CSV nettoyé existant ─────────────────────────────────────
print("\nChargement caract_2005_2024_clean.csv...")
df_clean = pd.read_csv(
    'caract_2005_2024_clean.csv',
    encoding='latin-1', low_memory=False
)
# Convertir toutes les colonnes texte en UTF-8 propre
for col in df_clean.select_dtypes(include='object').columns:
    df_clean[col] = df_clean[col].apply(
        lambda x: x.encode('latin-1', errors='ignore').decode('utf-8', errors='ignore') if isinstance(x, str) else x
    )
print(f"  {len(df_clean):,} lignes avant injection")

# ─── Injection & tri ─────────────────────────────────────────────────────
# Supprimer toute ligne 2009 déjà présente (évite les doublons si relance)
df_clean = df_clean[df_clean['an'] != 2009]
print(f"  Lignes 2009 existantes supprimées, reste {len(df_clean):,} lignes")
df_final = pd.concat([df_clean, df09], ignore_index=True)
df_final = df_final.sort_values(['an', 'Num_Acc']).reset_index(drop=True)

print(f"  {len(df_final):,} lignes après injection 2009")
print(f"\nAnnées présentes :")
print(df_final.groupby('an').size().reset_index(name='nb').to_string())

# ─── Sauvegarde ──────────────────────────────────────────────────────────
df_final.to_csv('caract_2005_2024_clean.csv', index=False, encoding='utf-8')
print("\n✅ caract_2005_2024_clean.csv mis à jour avec 2009 !")
print("Relancez : del accidents.duckdb && python init_db.py")