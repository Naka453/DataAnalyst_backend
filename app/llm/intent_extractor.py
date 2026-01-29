from __future__ import annotations
import re
from typing import Any, Dict

# category keywords (same keys as your fallback_intent.py)
CATEGORY_KEYWORDS = ("тамхи", "суудлын автомашин", "хүнс", "автобензин", "түргэн эдэлгээтэй", "хэрэглээний бүтээгдэхүүн")

def _norm(s: str) -> str:
    return (s or "").strip().casefold()

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

    # ---- time normalize (optional) ----
    # keep whatever extractor returns; state/to_intent will decide final
    # but ensure time is either "latest" or dict
    t = out.get("time")
    if t is not None and t != "latest" and not isinstance(t, dict):
        out.pop("time", None)

    return out