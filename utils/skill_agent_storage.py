from __future__ import annotations

import json
import time
from typing import Any

from utils.skill_agent_constants import HISTORY_KEY_PREFIX, RESUME_KEY_PREFIX, SESSION_DIR_KEY_PREFIX
from utils.tools import _safe_get


def _get_session_storage_id(session: Any) -> str:
    candidates = [
        _safe_get(session, "conversation_id"),
        _safe_get(session, "chat_id"),
        _safe_get(session, "task_id"),
        _safe_get(session, "id"),
        _safe_get(session, "session_id"),
        _safe_get(session, "app_run_id"),
    ]
    for c in candidates:
        if isinstance(c, str) and c.strip():
            return c.strip()
    return "global"


def _get_resume_storage_key(session: Any) -> str:
    return RESUME_KEY_PREFIX + _get_session_storage_id(session)


def _get_history_storage_key(session: Any) -> str:
    return HISTORY_KEY_PREFIX + _get_session_storage_id(session)


def _get_session_dir_storage_key(session: Any) -> str:
    return SESSION_DIR_KEY_PREFIX + _get_session_storage_id(session)


def _storage_get_text(storage: Any, key: str) -> str:
    try:
        val = storage.get(key)
        if not val:
            return ""
        if isinstance(val, bytes):
            return val.decode("utf-8", errors="ignore")
        if isinstance(val, str):
            return val
        return ""
    except Exception:
        return ""


def _storage_set_text(storage: Any, key: str, text: str) -> None:
    try:
        storage.set(key, (text or "").encode("utf-8"))
    except Exception:
        return


def _storage_get_json(storage: Any, key: str) -> dict[str, Any]:
    raw = _storage_get_text(storage, key).strip()
    if not raw:
        return {}
    try:
        val = json.loads(raw)
        return val if isinstance(val, dict) else {}
    except Exception:
        return {}


def _storage_set_json(storage: Any, key: str, value: dict[str, Any] | None) -> None:
    if not value:
        _storage_set_text(storage, key, "")
        return
    try:
        _storage_set_text(storage, key, json.dumps(value, ensure_ascii=False))
    except Exception:
        _storage_set_text(storage, key, "")
        return


def _append_history_turn(
    storage: Any,
    *,
    history_key: str,
    user_text: str,
    assistant_text: str,
    max_turns: int = 50,
) -> None:
    state = _storage_get_json(storage, history_key)
    turns = state.get("turns")
    if not isinstance(turns, list):
        turns = []
    turns.append(
        {
            "user": str(user_text or ""),
            "assistant": str(assistant_text or ""),
            "created_at": int(time.time()),
        }
    )
    if max_turns < 1:
        max_turns = 1
    if len(turns) > max_turns:
        turns = turns[-max_turns:]
    _storage_set_json(storage, history_key, {"turns": turns})
