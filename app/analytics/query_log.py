# app/analytics/query_log.py
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

LOG_PATH = Path("logs/query_log.jsonl")

def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_query(event: Dict[str, Any]) -> None:
    """
    Append JSONL log. Never throw.
    """
    try:
        payload = dict(event or {})
        payload.setdefault("ts", int(time.time()))
        payload.setdefault("ts_iso", _utc_now_iso())

        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False, default=str) + "\n")
    except Exception:
        return