from __future__ import annotations
import re

from typing import Any, Dict

from jsonschema import ValidationError, validate

from app.llm.client import llm_json
from app.llm.intent_schema import INTENT_SCHEMA
from app.llm.prompt import build_intent_prompt

# category keywords (same keys as your fallback_intent.py)
CATEGORY_KEYWORDS = ("тамхи", "суудлын автомашин", "хүнс", "автобензин", "түргэн эдэлгээтэй", "хэрэглээний бүтээгдэхүүн")

def _norm(s: str) -> str:
    return (s or "").strip().casefold()


def _find_year_month(q: str) -> tuple[int | None, int | None]:
    m = re.search(r"(20\d{2})\D+(\d{1,2})\D*сар", q)
    if m:
        return int(m.group(1)), int(m.group(2))

    m = re.search(r"\b(20\d{2})\D+(\d{1,2})\b", q)
    if m:
        year, month = int(m.group(1)), int(m.group(2))
        if 1 <= month <= 12:
            return year, month

    m = re.search(r"\b(20\d{2})\b", q)
    if m:
        return int(m.group(1)), None

    return None, None


def _find_years_list(q: str) -> list[int] | None:
    m = re.search(r"\b(20\d{2})\s*[-–]\s*(20\d{2})\b", q)
    if m:
        y1, y2 = int(m.group(1)), int(m.group(2))
        if y1 > y2:
            y1, y2 = y2, y1
        return list(range(y1, y2 + 1))

    years = sorted(set(int(x) for x in re.findall(r"\b(20\d{2})\b", q)))
    return years if len(years) >= 2 else None


def extract_intent(question: str) -> Dict[str, Any]:
    prompt = build_intent_prompt(question)
    payload = llm_json(prompt)

    if not isinstance(payload, dict):
        return {}

    try:
        validate(instance=payload, schema=INTENT_SCHEMA)
    except ValidationError:
        # Schema is strict for safety; caller will pass through sanitize + fallback as needed.
        return payload

    return payload


def sanitize_intent(intent: Dict[str, Any], question: str) -> Dict[str, Any]:
    """
    Make LLM intent safe:
    - never crash builder
    - set domain/metric defaults if missing
    - guard: category vs HS conflict
    - do NOT do HS inference here (builder already has fallback)
    """
    q = _norm(question)
    out: Dict[str, Any] = dict(intent or {})

    # ---- defaults ----
    out.setdefault("domain", "import" if "импорт" in q else "export")
    out.setdefault("metric", "amountUSD")

    # normalize fields
    if not isinstance(out.get("filters"), dict):
        out["filters"] = {}

    # ---- metric normalize ----
    m = out.get("metric")
    if m not in ("amountUSD", "quantity", "weighted_price"):
        out["metric"] = "amountUSD"

    # Explicit wording in the user's question wins over a shaky LLM guess.
    if "импорт" in q:
        out["domain"] = "import"
    elif "экспорт" in q:
        out["domain"] = "export"

    if any(k in q for k in ("нэгж үнэ", "дундаж үнэ", "тонн тутмын үнэ", "unit price")):
        out["metric"] = "weighted_price"
        out["calc"] = "weighted_price"
    elif any(k in q for k in ("тоо хэмжээ", "тонн")):
        out["metric"] = "quantity"
    elif any(k in q for k in ("үнийн дүн", "нийт дүн", "дүн", "ам.доллар", "usd", "$")):
        out["metric"] = "amountUSD"

    # ---- domain normalize ----
    d = out.get("domain")
    if d not in ("import", "export"):
        out["domain"] = "export"

    # ---- category vs HS guard ----
    filters = out["filters"]
    has_category_kw = any(k in q for k in CATEGORY_KEYWORDS)
    has_category_filters = any(filters.get(k) for k in ("purpose", "sub1", "sub2", "sub3"))

    if has_category_kw or has_category_filters:
        # If category question, do not set hscode from LLM
        filters.pop("hscode", None)

    if any(k in q for k in ("нийт экспорт", "нийт импорт", "бүх экспорт", "бүх импорт", "нийт дүн")):
        filters.pop("hscode", None)

    # ---- time normalize (optional) ----
    # keep whatever extractor returns; state/to_intent will decide final
    # but ensure time is either "latest" or dict
    t = out.get("time")
    if t is not None and t != "latest" and not isinstance(t, dict):
        out.pop("time", None)

    years_list = _find_years_list(q)
    year, month = _find_year_month(q)
    if years_list:
        out["time"] = {"years": years_list}
    elif year and month:
        out["time"] = {"year": year, "month": month}
    elif year:
        out["time"] = {"year": year}

    calc = out.get("calc")
    valid_calcs = {
        "month_value",
        "ytd",
        "yoy",
        "timeseries_month",
        "timeseries_year",
        "timeseries_country",
        "year_total",
        "weighted_price",
        "avg_months",
        "avg_years",
    }
    if calc not in valid_calcs:
        out.pop("calc", None)

    if years_list:
        out["calc"] = "timeseries_year"
    elif "өссөн дүн" in q or "он эхнээс" in q or "ytd" in q:
        out["calc"] = "ytd"
    elif "өмнөх оны мөн үе" in q:
        out["calc"] = "yoy"
    elif any(k in q for k in ("сар сараар", "сараар", "явц", "timeline")) and year:
        out["calc"] = "timeseries_month"
    elif (
        year
        and month is None
        and any(k in q for k in ("нийт", "нийлбэр", "үнийн дүн", "нийт дүн"))
        and any(k in q for k in ("хэд", "хэчнээн", "дүн", "value", "үнийн дүн"))
    ):
        out["calc"] = "year_total"
    elif year and month and out.get("calc") in (None, "timeseries_month", "year_total"):
        out["calc"] = "month_value"

    return out
