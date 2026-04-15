import sys
from pathlib import Path

# Fix import src
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
import pytest

from src.controllers.dashboard_controller import (
    get_con,
    get_dimensions,
    build_where,
    build_where_usagers,
    get_kpi,
    get_accidents_par_mois,
    get_accidents_par_heure,
    get_gravite,
    get_accident_by_num,
    get_page_accidents,
    export_csv,
)


# ==========================================================
# Fixtures
# ==========================================================
@pytest.fixture(scope="module")
def dims():
    return get_dimensions()


@pytest.fixture(scope="module")
def sample_filters(dims):
    annees = [str(dims["annees"][0])] if dims["annees"] else []
    deps = [str(dims["deps"][0])] if dims["deps"] else []
    mois = [dims["mois_vals"][0]] if dims["mois_vals"] else []

    lum = [dims["lum_vals"][0]] if dims["lum_vals"] else []
    atm = [dims["atm_vals"][0]] if dims["atm_vals"] else []
    colf = [dims["col_vals"][0]] if dims["col_vals"] else []
    catr = [dims["catr_vals"][0]] if dims["catr_vals"] else []
    surf = [dims["surf_vals"][0]] if dims["surf_vals"] else []
    vma = [dims["vma_vals"][0]] if dims["vma_vals"] else []

    return {
        "an": annees,
        "dep": deps,
        "mois": mois,
        "lum": lum,
        "atm": atm,
        "colf": colf,
        "catr": catr,
        "surf": surf,
        "vma": vma,
    }


@pytest.fixture(scope="module")
def sample_num_acc():
    con = get_con()
    row = con.execute("SELECT Num_Acc FROM accident_full LIMIT 1").fetchone()
    return row[0] if row else None


# ==========================================================
# Tests dimensions
# ==========================================================
def test_get_dimensions_returns_expected_keys(dims):
    expected_keys = {
        "annees",
        "deps",
        "lum_vals",
        "atm_vals",
        "col_vals",
        "catr_vals",
        "surf_vals",
        "vma_vals",
        "mois_vals",
    }
    assert expected_keys.issubset(dims.keys())


# ==========================================================
# Tests WHERE builder
# ==========================================================
def test_build_where_empty_filters():
    where_sql, params = build_where([], [], [], [], [], [], [], [], [])
    assert where_sql == ""
    assert params == []


def test_build_where_multiple_filters(sample_filters):
    where_sql, params = build_where(
        sample_filters["an"],
        sample_filters["dep"],
        sample_filters["mois"],
        sample_filters["lum"],
        sample_filters["atm"],
        sample_filters["colf"],
        sample_filters["catr"],
        sample_filters["surf"],
        sample_filters["vma"],
    )
    assert isinstance(where_sql, str)
    assert isinstance(params, list)
    assert "WHERE" in where_sql
    assert len(params) > 0


def test_build_where_usagers_multiple_filters(sample_filters):
    where_sql, params = build_where_usagers(
        sample_filters["an"],
        sample_filters["dep"],
        sample_filters["mois"],
    )
    assert isinstance(where_sql, str)
    assert isinstance(params, list)


# ==========================================================
# KPI & data
# ==========================================================
def test_get_kpi_without_filters():
    where_sql, params = build_where([], [], [], [], [], [], [], [], [])
    kpi = get_kpi(where_sql, params)

    assert isinstance(kpi, dict)
    assert set(kpi.keys()) == {"accidents", "vehicules", "usagers"}
    assert kpi["accidents"] >= 0


def test_get_accidents_par_mois_returns_dataframe():
    where_sql, params = build_where([], [], [], [], [], [], [], [], [])
    df = get_accidents_par_mois(where_sql, params)

    assert isinstance(df, pd.DataFrame)
    if not df.empty:
        assert "mois" in df.columns


def test_get_accidents_par_heure_returns_dataframe():
    where_sql, params = build_where([], [], [], [], [], [], [], [], [])
    df = get_accidents_par_heure(where_sql, params)

    assert isinstance(df, pd.DataFrame)


def test_get_gravite_returns_dataframe():
    where_sql_u, params_u = build_where_usagers([], [], [])
    df = get_gravite(where_sql_u, params_u, [], [], [])

    assert isinstance(df, pd.DataFrame)


# ==========================================================
# Pagination & export
# ==========================================================
def test_get_page_accidents_returns_dataframe_and_total():
    where_sql, params = build_where([], [], [], [], [], [], [], [], [])
    df, total = get_page_accidents(where_sql, params, page=1, page_size=20)

    assert isinstance(df, pd.DataFrame)
    assert isinstance(total, int)


def test_export_csv_returns_bytes():
    where_sql, params = build_where([], [], [], [], [], [], [], [], [])
    data = export_csv(where_sql, params)

    assert isinstance(data, bytes)


# ==========================================================
# Accident detail
# ==========================================================
def test_get_accident_by_num_existing(sample_num_acc):
    if sample_num_acc is None:
        pytest.skip("Aucun Num_Acc trouvé.")

    result = get_accident_by_num(sample_num_acc)

    assert isinstance(result, dict)
    assert not result["accident"].empty


def test_get_accident_by_num_unknown():
    result = get_accident_by_num("FAKE_NUM_ACC")

    assert result["accident"].empty


# ==========================================================
# BONUS TESTS (qualité)
# ==========================================================
def test_kpi_vs_table_count():
    where_sql, params = build_where([], [], [], [], [], [], [], [], [])
    kpi = get_kpi(where_sql, params)

    df, total = get_page_accidents(where_sql, params, page=1, page_size=1)

    assert kpi["accidents"] == total


def test_multiple_filters_reduce_data(sample_filters):
    where_sql_all, params_all = build_where([], [], [], [], [], [], [], [], [])
    kpi_all = get_kpi(where_sql_all, params_all)

    where_sql_f, params_f = build_where(
        sample_filters["an"],
        sample_filters["dep"],
        sample_filters["mois"],
        [], [], [], [], [], []
    )
    kpi_filtered = get_kpi(where_sql_f, params_f)

    assert kpi_filtered["accidents"] <= kpi_all["accidents"]