from typing import List, Dict
from .models import ConversationState


def build_suggestions(s: ConversationState) -> List[Dict[str, str]]:
    """
    UI дээр харуулах suggested follow-ups
    """
    out: List[Dict[str, str]] = []

    # -------------------
    # Metric suggestions
    # -------------------
    metrics = {
        "amountUSD": {"label": "Үнийн дүн", "prompt": "үнийн дүнгээр"},
        "quantity": {"label": "Тоо хэмжээ", "prompt": "тоо хэмжээгээр"},
        "weighted_price": {"label": "Нэгж үнэ", "prompt": "нэгж үнээр"},
    }

    # ✅ metric сонгогдоогүй үед л сонголтуудыг хүчтэй санал болгоно
    if not s.metric:
        out.extend(metrics.values())
    else:
        # (optional) metric солихыг санал болгох бол comment-ийг аваад ашиглаарай
        # for key, m in metrics.items():
        #     if key != s.metric:
        #         out.append(m)
        pass

    # ✅ Latest month shortcut (only if not already latest)
    if not getattr(s.time, "latest", False):
        out.append({"label": "Сүүлийн сар", "prompt": "сүүлийн сар"})

    # Granularity suggestions
    # -------------------
    if not s.time.granularity:
        out.append({"label": "Сар бүр", "prompt": "сар бүрээр"})
        out.append({"label": "Жилээр", "prompt": "жилээр"})
    else:
        if s.time.granularity != "month":
            out.append({"label": "Сар бүр", "prompt": "сар бүрээр"})
        if s.time.granularity != "year":
            out.append({"label": "Жилээр", "prompt": "жилээр"})

    # -------------------
    # Compare previous year
    # -------------------
    if s.time.year and not s.time.years:
        out.append({
            "label": "Өмнөх онтой харьцуулах",
            "prompt": "өмнөх онтой харьцуул",
        })

    # -------------------
    # Scale suggestions (only when metric is selected and supports scaling)
    # -------------------
    if s.metric in ("amountUSD", "quantity"):
        if s.scale_label != "сая":
            out.append({"label": "Сая нэгж", "prompt": "сая нэгжээр"})
        if s.scale_label != "мянга":
            out.append({"label": "Мянга нэгж", "prompt": "мянга нэгжээр"})

    # -------------------
    # Deduplicate
    # -------------------
    seen = set()
    clean: List[Dict[str, str]] = []
    for item in out:
        key = (item.get("label"), item.get("prompt"))
        if key not in seen:
            clean.append(item)
            seen.add(key)

    return clean