from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


# NOTE: Ideally import this from a single source of truth, e.g.
# from app.mapping.hscode import HS_CODE_MAP
HS_CODE_MAP = {
    "нүүрс": ["2701", "2702"],
    "зэс": ["2603"],
    "төмөр": ["2601"],
    "газрын тос": ["2709"],
}

# Category keywords -> which field to filter (for v_import_monthly_category)
# We keep values short (e.g. "Тамхи") and expect builder.py to use ILIKE '%...%'
CATEGORY_KEYWORDS: Dict[str, str] = {
    "тамхи, суудлын автомашин": "sub3",
    "хүнс, автобензин": "sub2",  # based on your example: sub2 = "1.1.1 Хүнс"
    "түргэн эдэлгээтэй": "ub1",
    "хэрэглээний бүтээгдэхүүн": "purpose",
    # add more as needed:
    # "удаан эдэлгээтэй": "sub1",
    # "үйлдвэрлэлийн зориулалттай": "purpose",
}


def _norm(s: str) -> str:
    return (s or "").strip().casefold()


def _find_year_month(q: str) -> tuple[Optional[int], Optional[int]]:
    # 2025 оны 12 сар / 2025 12 сар / 2025-12 гэх мэтийг барина (энгийн)
    m = re.search(r"(20\d{2})\D+(\d{1,2})\D*сар", q)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.search(r"\b(20\d{2})\D+(\d{1,2})\b", q)
    if m:
        y, mm = int(m.group(1)), int(m.group(2))
        if 1 <= mm <= 12:
            return y, mm
    return None, None


def _infer_category_filters(question: str) -> Dict[str, str]:
    """
    Returns category filters like {"sub3": "Тамхи"} based on keyword hits.
    Uses the original question (not casefolded) for values; we store the matched keyword
    and rely on SQL builder to do ILIKE '%keyword%'.
    """
    qn = _norm(question)
    out: Dict[str, str] = {}
    for kw, field in CATEGORY_KEYWORDS.items():
        if kw in qn:
            # store the keyword itself (Title-case doesn't matter because ILIKE)
            out[field] = kw
    return out


def _infer_hscode(question: str) -> Optional[List[str]]:
    qn = _norm(question)

    # user typed 4-digit codes; exclude year-like numbers (e.g., 2000–2030)
    m = re.findall(r"\b(\d{4})\b", qn)
    if m:
        hs: List[str] = []
        for s in m:
            n = int(s)
            # treat as year, not HS
            if 2000 <= n <= 2030:
                continue
            hs.append(s)
        if hs:
            return hs

    # keyword mapping
    for k, v in HS_CODE_MAP.items():
        if k in qn:
            return v

    return None


def build_intent_fallback(question: str) -> Dict[str, Any]:
    q = _norm(question)

    # domain
    domain = "import" if "импорт" in q else "export"

    # metric + calc
    if "нэгж" in q or "нэгж үнэ" in q or "дундаж үнэ" in q or "unit price" in q:
        metric = "weighted_price"
        calc = "weighted_price"
    elif "тонн" in q or "тоо хэмжээ" in q or "хэмжээ" in q:
        metric = "quantity"
        calc = "month_value"
    else:
        metric = "amountUSD"
        calc = "month_value"

    # time
    y, m = _find_year_month(question)
    if y and m:
        time: Any = {"year": y, "month": m}
    elif y:
        time = {"year": y}
    else:
        time = "latest"

    filters: Dict[str, Any] = {}

    # Category filters first (avoid HS over-broad grouping cases like 2710)
    cat_filters = _infer_category_filters(question)
    if cat_filters:
        filters.update(cat_filters)
    else:
        # Only infer HS codes if no category keyword matched
        hs = _infer_hscode(question)
        if hs:
            filters["hscode"] = hs

    return {
        "domain": domain,
        "calc": calc,
        "metric": metric,
        "time": time,
        "filters": filters,
        "topn": 50,
    }