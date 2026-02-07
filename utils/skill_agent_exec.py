from __future__ import annotations

import importlib.util
import os
import re
import shutil
import subprocess
import sys
import time
from typing import Any

from utils.skill_agent_constants import TEMP_SESSION_PREFIX


def _detect_skills_root(explicit_path: str | None) -> str | None:
    if explicit_path and os.path.isdir(explicit_path):
        return os.path.abspath(explicit_path)

    env_path = os.getenv("SKILLS_ROOT")
    if env_path and os.path.isdir(env_path):
        return os.path.abspath(env_path)

    plugin_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    candidates = [os.path.join(plugin_root, "skills")]
    for p in candidates:
        if os.path.isdir(p):
            return os.path.abspath(p)
    return None


def _cleanup_old_temp_sessions(temp_root: str, *, keep: int, protect_dirs: set[str] | None = None) -> None:
    protect = {os.path.abspath(p) for p in (protect_dirs or set()) if p}
    try:
        entries: list[tuple[float, str]] = []
        for name in os.listdir(temp_root):
            if not isinstance(name, str) or not name.startswith(TEMP_SESSION_PREFIX):
                continue
            path = os.path.join(temp_root, name)
            if not os.path.isdir(path):
                continue
            abs_path = os.path.abspath(path)
            if abs_path in protect:
                continue
            try:
                mtime = os.path.getmtime(abs_path)
            except Exception:
                mtime = 0.0
            entries.append((mtime, abs_path))
        entries.sort(key=lambda x: x[0])
        if keep < 0:
            keep = 0
        excess = len(entries) - keep
        if excess <= 0:
            return
        for _, path in entries[:excess]:
            try:
                for _ in range(2):
                    try:
                        shutil.rmtree(path, ignore_errors=False)
                        break
                    except Exception:
                        time.sleep(0.1)
                else:
                    shutil.rmtree(path, ignore_errors=True)
            except Exception:
                continue
    except Exception:
        return


def _is_safe_module_name(name: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9_.-]+", name or ""))


def _skill_contains_python_module(skill_path: str, module_name: str) -> bool:
    base = (module_name or "").split(".", 1)[0].strip()
    if not base:
        return False
    if not _is_safe_module_name(base):
        return False
    file_candidate = os.path.join(skill_path, base + ".py")
    if os.path.isfile(file_candidate):
        return True
    dir_candidate = os.path.join(skill_path, base)
    if not os.path.isdir(dir_candidate):
        return False
    init_candidate = os.path.join(dir_candidate, "__init__.py")
    if os.path.isfile(init_candidate):
        return True
    for _, _, files in os.walk(dir_candidate):
        if any(str(f).lower().endswith(".py") for f in files):
            return True
    return False


def _ensure_python_module(module_name: str, *, auto_install: bool, cwd: str) -> dict[str, Any]:
    if not module_name or not _is_safe_module_name(module_name):
        return {"ok": False, "error": "invalid module name", "module": module_name}
    if importlib.util.find_spec(module_name) is not None:
        return {"ok": True, "module": module_name}
    if not auto_install:
        return {"ok": False, "error": "python module not found", "module": module_name}

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", module_name, "--no-input", "--disable-pip-version-check"],
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
        if result.returncode == 0:
            return {"ok": True, "module": module_name, "installed": True}
        return {
            "ok": False,
            "error": "pip install failed",
            "module": module_name,
            "returncode": result.returncode,
            "stdout": (result.stdout or "").strip(),
            "stderr": (result.stderr or "").strip(),
        }
    except Exception as e:
        return {"ok": False, "error": "pip install exception", "module": module_name, "exception": str(e)}


def _resolve_executable(exe: str) -> str | None:
    e = str(exe or "").strip()
    if not e:
        return None
    from utils.skill_agent_paths import _is_abs_path

    if _is_abs_path(e):
        return e
    found = shutil.which(e)
    if found:
        return found
    if os.name == "nt":
        for ext in (".cmd", ".exe", ".bat"):
            found = shutil.which(e + ext)
            if found:
                return found
    return None


def _missing_executable_hint(exe: str) -> str:
    base = os.path.basename(str(exe or "")).lower()
    base = base.split(".", 1)[0]
    if base in {"node", "npm", "npx"}:
        return "需要在 plugin_daemon 容器中安装 Node.js 环境，并确保 node/npm/npx 在 PATH"
    return "请确认该命令已安装并加入 PATH"
