import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
import pytest

from src.controllers.analysis_controller import (
    load_grav_by,
    load_carte,
    load_mortalite_annee,
    load_mortalite_mois,
    load_bubble_heure_mois,
    load_tranches_age_conducteurs,
    load_gravite_par_tranche_age,
    get_stats_globales,
    TRANCHES_AGE_ORDRE,
)


# ==============================================================
# load_grav_by — whitelist + données
# ==============================================================

def test_load_grav_by_lum_returns_dataframe():
    """load_grav_by('lum') doit retourner un DataFrame non vide."""
    df = load_grav_by("lum")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "modalite" in df.columns
    assert "grav_int" in df.columns
    assert "nb" in df.columns


def test_load_grav_by_catr_returns_dataframe():
    """load_grav_by('catr') doit retourner un DataFrame non vide."""
    df = load_grav_by("catr")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_load_grav_by_atm_returns_dataframe():
    """load_grav_by('atm') doit retourner un DataFrame non vide."""
    df = load_grav_by("atm")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_load_grav_by_rejects_unauthorized_column():
    """load_grav_by() doit lever ValueError pour une colonne non autorisée."""
    with pytest.raises(ValueError, match="Colonne non autorisée"):
        load_grav_by("dep")


def test_load_grav_by_rejects_sql_injection():
    """load_grav_by() doit rejeter toute tentative d'injection SQL."""
    with pytest.raises(ValueError, match="Colonne non autorisée"):
        load_grav_by("lum; DROP TABLE usagers_clean; --")


def test_load_grav_by_grav_int_values():
    """load_grav_by() ne doit retourner que des grav_int entre 1 et 4."""
    df = load_grav_by("lum")
    assert df["grav_int"].between(1, 4).all(), "grav_int hors plage [1, 4] détecté"


# ==============================================================
# load_carte
# ==============================================================

def test_load_carte_returns_dataframe():
    """load_carte() doit retourner un DataFrame avec les colonnes attendues."""
    df = load_carte()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    expected_cols = {"dep", "nb_accidents", "nb_tues", "taux_mortalite"}
    assert expected_cols.issubset(df.columns)


def test_load_carte_taux_mortalite_range():
    """load_carte() : taux_mortalite doit être entre 0 et 100."""
    df = load_carte()
    assert df["taux_mortalite"].between(0, 100).all()


def test_load_carte_no_negative_values():
    """load_carte() : nb_accidents et nb_tues doivent être >= 0."""
    df = load_carte()
    assert (df["nb_accidents"] >= 0).all()
    assert (df["nb_tues"] >= 0).all()


def test_load_carte_dep_20_excluded():
    """load_carte() : le département 20 (code obsolète) ne doit pas apparaître."""
    df = load_carte()
    assert "20" not in df["dep"].values, "Département 20 (code obsolète) présent dans la carte"


# ==============================================================
# load_mortalite_annee
# ==============================================================

def test_load_mortalite_annee_returns_dataframe():
    """load_mortalite_annee() doit retourner un DataFrame avec les colonnes attendues."""
    df = load_mortalite_annee()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    expected_cols = {"an", "nb_accidents", "nb_tues", "taux_mortalite"}
    assert expected_cols.issubset(df.columns)


def test_load_mortalite_annee_ordered_by_year():
    """load_mortalite_annee() doit être trié par année croissante."""
    df = load_mortalite_annee()
    assert list(df["an"]) == sorted(df["an"].tolist())


def test_load_mortalite_annee_covers_full_period():
    """load_mortalite_annee() doit couvrir au moins 2005 à 2024."""
    df = load_mortalite_annee()
    assert df["an"].min() <= 2005
    assert df["an"].max() >= 2024


# ==============================================================
# load_mortalite_mois
# ==============================================================

def test_load_mortalite_mois_returns_dataframe():
    """load_mortalite_mois() doit retourner un DataFrame non vide."""
    df = load_mortalite_mois()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "mois" in df.columns
    assert "taux_mortalite" in df.columns


def test_load_mortalite_mois_12_months():
    """load_mortalite_mois() doit retourner exactement 12 mois."""
    df = load_mortalite_mois()
    assert len(df) == 12, f"Attendu 12 mois, obtenu {len(df)}"


# ==============================================================
# load_bubble_heure_mois
# ==============================================================

def test_load_bubble_heure_mois_returns_dataframe():
    """load_bubble_heure_mois() doit retourner un DataFrame avec les colonnes attendues."""
    df = load_bubble_heure_mois()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    expected_cols = {"mois", "heure", "nb_tues", "pct"}
    assert expected_cols.issubset(df.columns)


def test_load_bubble_heure_mois_valid_hours():
    """load_bubble_heure_mois() : les heures doivent être entre 0 et 23."""
    df = load_bubble_heure_mois()
    assert df["heure"].between(0, 23).all()


def test_load_bubble_heure_mois_pct_sums_to_100():
    """load_bubble_heure_mois() : la somme des pct doit être proche de 100%."""
    df = load_bubble_heure_mois()
    total_pct = df["pct"].sum()
    assert abs(total_pct - 100.0) < 0.5, f"Somme des pct = {total_pct:.2f}%, attendu ~100%"


# ==============================================================
# load_tranches_age_conducteurs
# ==============================================================

def test_load_tranches_age_conducteurs_returns_dataframe():
    """load_tranches_age_conducteurs() doit retourner un DataFrame non vide."""
    df = load_tranches_age_conducteurs()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    expected_cols = {"tranche_age", "nb_conducteurs", "pct"}
    assert expected_cols.issubset(df.columns)


def test_load_tranches_age_conducteurs_no_0_17():
    """load_tranches_age_conducteurs() ne doit pas contenir la tranche '0-17 ans'."""
    df = load_tranches_age_conducteurs()
    assert "0-17 ans" not in df["tranche_age"].values, \
        "Tranche '0-17 ans' détectée — doit être '16-17 ans'"


def test_load_tranches_age_conducteurs_has_16_17():
    """load_tranches_age_conducteurs() doit contenir la tranche '16-17 ans'."""
    df = load_tranches_age_conducteurs()
    assert "16-17 ans" in df["tranche_age"].values


def test_load_tranches_age_conducteurs_pct_sums_to_100():
    """load_tranches_age_conducteurs() : la somme des pct doit être proche de 100%."""
    df = load_tranches_age_conducteurs()
    total = df["pct"].sum()
    assert abs(total - 100.0) < 1.0, f"Somme des pct = {total:.2f}%, attendu ~100%"


def test_load_tranches_age_conducteurs_order():
    """load_tranches_age_conducteurs() doit respecter l'ordre canonique des tranches."""
    df = load_tranches_age_conducteurs()
    tranches_presentes = df["tranche_age"].tolist()
    ordre_attendu = [t for t in TRANCHES_AGE_ORDRE if t in tranches_presentes]
    assert tranches_presentes == ordre_attendu, \
        f"Ordre incorrect : {tranches_presentes} vs attendu {ordre_attendu}"


# ==============================================================
# load_gravite_par_tranche_age
# ==============================================================

def test_load_gravite_par_tranche_age_returns_dataframe():
    """load_gravite_par_tranche_age() doit retourner un DataFrame non vide."""
    df = load_gravite_par_tranche_age()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    expected_cols = {"modalite", "grav_int", "nb"}
    assert expected_cols.issubset(df.columns)


def test_load_gravite_par_tranche_age_valid_grav_int():
    """load_gravite_par_tranche_age() : grav_int doit être entre 1 et 4."""
    df = load_gravite_par_tranche_age()
    assert df["grav_int"].between(1, 4).all()


def test_load_gravite_par_tranche_age_no_0_17():
    """load_gravite_par_tranche_age() ne doit pas contenir la tranche '0-17 ans'."""
    df = load_gravite_par_tranche_age()
    assert "0-17 ans" not in df["modalite"].values


# ==============================================================
# get_stats_globales
# ==============================================================

def test_get_stats_globales_returns_dict():
    """get_stats_globales() doit retourner un dict avec les clés attendues."""
    stats = get_stats_globales()
    assert isinstance(stats, dict)
    expected_keys = {"total_accidents", "total_tues", "moyenne_annuelle"}
    assert expected_keys.issubset(stats.keys())


def test_get_stats_globales_values_positive():
    """get_stats_globales() : toutes les valeurs doivent être > 0."""
    stats = get_stats_globales()
    assert stats["total_accidents"] > 0
    assert stats["total_tues"] > 0
    assert stats["moyenne_annuelle"] > 0


def test_get_stats_globales_total_accidents():
    """get_stats_globales() : total_accidents doit être cohérent avec la DuckDB."""
    stats = get_stats_globales()
    assert stats["total_accidents"] == 1_286_097, \
        f"total_accidents = {stats['total_accidents']}, attendu 1 286 097"


def test_get_stats_globales_total_tues():
    """get_stats_globales() : total_tues doit correspondre aux données réelles."""
    stats = get_stats_globales()
    assert stats["total_tues"] == 77_427, \
        f"total_tues = {stats['total_tues']}, attendu 77 427"


def test_get_stats_globales_moyenne_annuelle():
    """get_stats_globales() : moyenne_annuelle = total_accidents / nb_années."""
    stats = get_stats_globales()
    assert stats["moyenne_annuelle"] == 64_305, \
        f"moyenne_annuelle = {stats['moyenne_annuelle']}, attendu 64 305"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])