from pathlib import Path
import sys
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.analytics import query_log


def test_log_query_adds_standard_timestamps(tmp_path, monkeypatch):
    log_file = tmp_path / "q.jsonl"
    monkeypatch.setattr(query_log, "LOG_PATH", log_file)

    query_log.log_query({"status": "success", "row_count": 1})

    payload = json.loads(log_file.read_text(encoding="utf-8").strip())
    assert payload["status"] == "success"
    assert payload["row_count"] == 1
    assert isinstance(payload.get("ts"), int)
    assert isinstance(payload.get("ts_iso"), str)