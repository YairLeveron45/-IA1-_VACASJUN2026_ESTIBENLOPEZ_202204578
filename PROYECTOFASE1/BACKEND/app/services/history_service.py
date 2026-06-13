import json
from datetime import datetime, timezone
from pathlib import Path


HISTORY_FILE = Path(__file__).resolve().parents[1] / "data" / "diagnosis_history.json"


def load_history() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []

    content = HISTORY_FILE.read_text(encoding="utf-8").strip()
    if not content:
        return []

    return json.loads(content)


def save_history(record: dict) -> None:
    history = load_history()
    history.append(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **record,
        }
    )
    HISTORY_FILE.write_text(
        json.dumps(history, ensure_ascii=True, indent=2),
        encoding="utf-8",
    )
