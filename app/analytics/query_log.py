# app/analytics/query_log.py
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict

LOG_PATH = Path("logs/query_log.jsonl")


def log_query(event: Dict[str, Any]) -> None:
    """
    Append JSONL log. Never throw.
    """
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        event.setdefault("ts", int(time.time()))
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False, default=str) + "\n")
    except Exception:
        return