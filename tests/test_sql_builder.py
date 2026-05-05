from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.sql.builder import build_sql


def _placeholders(sql_text: str) -> set[str]:
    import re

    placeholders = set(re.findall(r":([A-Za-z_][A-Za-z0-9_]*)", sql_text))
    return placeholders - {"int", "text"}


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


def test_ytd_year_only_has_required_params_and_month_cap():
    sql, params, meta = build_sql(
        {
            "domain": "export",
            "calc": "ytd",
            "metric": "amountUSD",
            "time": {"year": 2026},
            "filters": {},
            "topn": 50,
        },
        "2026 оны өссөн дүн экспорт",
    )

    sql_text = str(sql)
    assert "month <= :mmax" in sql_text
    assert params["year"] == 2026
    assert params["mmax"] == 12
    assert _placeholders(sql_text) <= set(params)
    assert meta["calc"] == "ytd"


def test_weighted_price_year_only_does_not_require_month_param():
    sql, params, meta = build_sql(
        {
            "domain": "export",
            "calc": "weighted_price",
            "metric": "weighted_price",
            "time": {"year": 2026},
            "filters": {},
            "topn": 50,
        },
        "2026 оны экспортын нэгж үнэ",
    )

    sql_text = str(sql)
    assert "NULL::int AS month" in sql_text
    assert "month = :month" not in sql_text
    assert params["year"] == 2026
    assert "month" not in params
    assert _placeholders(sql_text) <= set(params)
    assert meta["calc"] == "weighted_price"


def test_import_purpose_category_filter_is_applied_without_customs_filter():
    sql, params, meta = build_sql(
        {
            "domain": "import",
            "calc": "year_total",
            "metric": "amountUSD",
            "time": {"year": 2026},
            "filters": {"purpose": "хэрэглээний бүтээгдэхүүн"},
            "topn": 50,
        },
        "2026 оны хэрэглээний бүтээгдэхүүн импортын нийт дүн",
    )

    sql_text = str(sql)
    assert "purpose ILIKE :purpose" in sql_text
    assert params["purpose"] == "%хэрэглээний бүтээгдэхүүн%"
    assert _placeholders(sql_text) <= set(params)
    assert meta["view_type"] == "category"


def test_import_company_filter_is_ignored_on_non_company_view():
    sql, params, meta = build_sql(
        {
            "domain": "import",
            "calc": "year_total",
            "metric": "amountUSD",
            "time": {"year": 2026},
            "filters": {"company": "Эрдэнэс"},
            "topn": 50,
        },
        "2026 оны импортын нийт дүн Эрдэнэс",
    )

    sql_text = str(sql)
    assert '"companyName" ILIKE :company' not in sql_text
    assert "company" not in _placeholders(sql_text)
    assert meta["domain"] == "import"
