# app/llm/followup_detector.py
from __future__ import annotations
import re
from typing import Dict, Any

def detect_followup(text: str) -> Dict[str, Any]:
    t = (text or "").strip().casefold()
    out: Dict[str, Any] = {}

    # -------- granularity --------
    if re.search(r"(сар\s*бүр|сараар|month)", t):
        out["granularity"] = "month"
    elif re.search(r"(жилээр|он\s*бүр|year)", t):
        out["granularity"] = "year"

    # -------- scale --------
    if re.search(r"\bсая\b", t):
        out["scale_label"] = "сая"
    elif re.search(r"\bмянга\b|\bмянган\b", t):
        out["scale_label"] = "мянга"

    # -------- metric (PRIORITY ORDER) --------
    # 1️⃣ weighted_price (unit price)
    if re.search(
        r"(нэгж\s*үнэ|дундаж\s*үнэ|unit\s*price|price\s*/\s*unit|ам\.?доллар\s*/\s*тонн|\$/\s*тонн)",
        t,
    ):
        out["metric"] = "weighted_price"

    # 2️⃣ quantity
    elif re.search(r"(тоо\s*хэмжээ|хэмжээ|тонн|kg|кг)", t):
        out["metric"] = "quantity"

    # 3️⃣ amountUSD
    elif re.search(r"(дүн|нийт\s*дүн|үнэ|ам\.?доллар|usd|\$)", t):
        out["metric"] = "amountUSD"

    # -------- year / years --------
    years = [int(y) for y in re.findall(r"\b(20\d{2})\b", t)]
    if len(years) == 1:
        out["year"] = years[0]
    elif len(years) >= 2:
        out["years"] = sorted(set(years))

    # -------- latest (ONLY if no explicit year) --------
    if not years and re.search(r"(сүүлийн|latest|current)", t):
        out["latest"] = True

    # -------- compare prev year --------
    if re.search(r"(харьцуул|compare|өмнөх\s+он|өнгөрсөн\s+он)", t):
        out["compare_prev_year"] = True

    return out