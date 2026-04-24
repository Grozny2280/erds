import json
from datetime import date
from pathlib import Path

DATA_FILE = Path("users.json")


def _load() -> dict:
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return {}


def _save(data: dict):
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_user(uid: int) -> dict | None:
    return _load().get(str(uid))


def set_user(uid: int, user: dict):
    data = _load()
    data[str(uid)] = user
    _save(data)


def all_users() -> dict:
    return _load()


def days_count(start_iso: str) -> int:
    return (date.today() - date.fromisoformat(start_iso)).days


def checked_today(user: dict) -> bool:
    return user.get("last_check") == date.today().isoformat()
