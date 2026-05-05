from app.llm.fallback_intent import build_intent_fallback
from app.sql.builder import build_sql
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.llm import intent_extractor


def test_extract_intent_uses_llm_and_schema(monkeypatch):
    monkeypatch.setattr(intent_extractor, "build_intent_prompt", lambda q: "PROMPT")
    monkeypatch.setattr(
        intent_extractor,
        "llm_json",
        lambda prompt: {
            "domain": "import",
            "calc": "month_value",
            "metric": "amountUSD",
            "time": "latest",
            "filters": {},
            "topn": 50,
            "window": 3,
        },
    )

    out = intent_extractor.extract_intent("импорт")
    assert out["domain"] == "import"
    assert out["time"] == "latest"


def test_sanitize_intent_removes_hs_for_category_keywords():
    raw = {
        "domain": "import",
        "metric": "amountUSD",
        "time": "latest",
        "filters": {"hscode": ["2701"]},
    }

    out = intent_extractor.sanitize_intent(raw, "тамхи импорт")
    assert "hscode" not in out["filters"]


def test_car_import_by_country_possessive_form_maps_to_sub3_import():
    intent = build_intent_fallback("2025 оны суудлын автомашины импорт улсаар")

    assert intent["domain"] == "import"
    assert intent["time"] == {"year": 2025}
    assert intent["filters"].get("sub3") == "суудлын автомашины"


def test_build_sql_sets_country_calc_meta_for_import_country_query():
    sql, params, meta = build_sql(
        {
            "domain": "import",
            "calc": "timeseries_country",
            "metric": "amountUSD",
            "time": {"year": 2025},
            "filters": {"sub3": "суудлын автомашин"},
            "topn": 50,
        },
        "2025 оны суудлын автомашин импорт улсаар харуул",
    )

    assert meta["calc"] == "timeseries_country"
    assert meta["granularity"] == "country"
    assert params["year"] == 2025


def test_sanitize_intent_corrects_total_export_amount_question():
    raw = {
        "domain": "import",
        "calc": "timeseries_month",
        "metric": "quantity",
        "time": "latest",
        "filters": {"hscode": "2026"},
    }

    out = intent_extractor.sanitize_intent(raw, "2026 оны нийт экспортын үнийн дүн хэд вэ")

    assert out["domain"] == "export"
    assert out["metric"] == "amountUSD"
    assert out["calc"] == "year_total"
    assert out["time"] == {"year": 2026}
    assert "hscode" not in out["filters"]


def test_fallback_intent_total_export_amount_question_is_year_total():
    out = build_intent_fallback("2026 оны нийт экспортын үнийн дүн хэд вэ")

    assert out["domain"] == "export"
    assert out["metric"] == "amountUSD"
    assert out["calc"] == "year_total"
    assert out["time"] == {"year": 2026}
    assert out["filters"] == {}
