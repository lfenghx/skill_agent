from __future__ import annotations

import os
import re

from utils.tools import _safe_join


def _normalize_relative_file_path(relative_path: str) -> str | None:
    rp = str(relative_path or "").strip()
    if not rp:
        return None
    rp = rp.replace("\\", "/").lstrip("/")
    if rp.endswith("/"):
        return None
    parts = [p for p in rp.split("/") if p]
    if not parts:
        return None
    if any(p in {".", ".."} for p in parts):
        return None
    return "/".join(parts)


def _is_abs_path(path: str) -> bool:
    if not path:
        return False
    p = str(path)
    if os.path.isabs(p):
        return True
    return bool(re.match(r"^[A-Za-z]:[\\/]", p))


def _rewrite_out_arg_to_session_dir(command: list[str], *, session_dir: str) -> list[str]:
    if not command:
        return command
    out_flag = "--out"
    rewritten: list[str] = []
    i = 0
    while i < len(command):
        arg = command[i]
        if isinstance(arg, str) and arg == out_flag and i + 1 < len(command):
            out_path = command[i + 1]
            if isinstance(out_path, str) and out_path and not _is_abs_path(out_path):
                rp = _normalize_relative_file_path(out_path)
                if rp:
                    out_path = _safe_join(session_dir, rp)
            rewritten.extend([arg, out_path])
            i += 2
            continue
        if isinstance(arg, str) and arg.startswith(out_flag + "="):
            out_path = arg.split("=", 1)[-1]
            if out_path and not _is_abs_path(out_path):
                rp = _normalize_relative_file_path(out_path)
                if rp:
                    out_path = _safe_join(session_dir, rp)
            rewritten.append(out_flag + "=" + out_path)
            i += 1
            continue
        rewritten.append(arg)
        i += 1
    return rewritten


def _rewrite_uploads_paths_to_session_dir(command: list[str], *, session_dir: str) -> list[str]:
    if not command:
        return command
    rewritten: list[str] = []
    for arg in command:
        if not isinstance(arg, str) or not arg.strip():
            rewritten.append(arg)
            continue
        if "://" in arg:
            rewritten.append(arg)
            continue
        if _is_abs_path(arg):
            rewritten.append(arg)
            continue

        def try_rewrite_path(p: str) -> str:
            s = str(p or "").strip()
            s_norm = s.replace("\\", "/")
            m = re.match(r"^(?:\./|../)*uploads/(.+)$", s_norm)
            if not m:
                return s
            tail = m.group(1)
            rp = _normalize_relative_file_path("uploads/" + tail)
            if not rp:
                return s
            abs_path = _safe_join(session_dir, rp)
            if os.path.isfile(abs_path):
                return abs_path
            return s

        if "=" in arg and arg.lstrip().startswith("-"):
            k, v = arg.split("=", 1)
            v2 = try_rewrite_path(v)
            rewritten.append(k + "=" + v2)
        else:
            rewritten.append(try_rewrite_path(arg))
    return rewritten


def _rewrite_existing_session_files_to_abs(command: list[str], *, session_dir: str) -> list[str]:
    if not command:
        return command
    rewritten: list[str] = []
    for arg in command:
        if not isinstance(arg, str) or not arg.strip():
            rewritten.append(arg)
            continue
        if arg.lstrip().startswith("-"):
            rewritten.append(arg)
            continue
        if "://" in arg:
            rewritten.append(arg)
            continue
        if _is_abs_path(arg):
            rewritten.append(arg)
            continue

        def try_rewrite_path(p: str) -> str:
            s = str(p or "").strip()
            rp = _normalize_relative_file_path(s)
            if not rp:
                return s
            abs_path = _safe_join(session_dir, rp)
            if os.path.isfile(abs_path):
                return abs_path
            return s

        rewritten.append(try_rewrite_path(arg))
    return rewritten
