from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.sql.builder import build_sql


def test_build_sql_does_not_inject_default_year_param():
    sql, params, meta = build_sql(
        {
            "domain": "export",
            "calc": "month_value",
            "metric": "amountUSD",
            "time": "latest",
            "filters": {},
            "topn": 5,
        },
        "экспортын дүн",
    )

    assert "year" not in params
    assert params["topn"] == 5
    assert meta["domain"] == "export"


def test_timeseries_country_latest_uses_latest_cte_without_fixed_year():
    sql, params, meta = build_sql(
        {
            "domain": "import",
            "calc": "timeseries_country",
            "metric": "amountUSD",
            "time": "latest",
            "filters": {"sub3": "суудлын автомашин"},
            "topn": 10,
        },
        "импорт улсаар",
    )

    sql_text = str(sql)
    assert "latest_parts" in sql_text
    assert "WHERE year = (SELECT y FROM latest_parts)" in sql_text
    assert "year" not in params
    assert meta["granularity"] == "country"