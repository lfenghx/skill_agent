from __future__ import annotations

from typing import Any


TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_skill_metadata",
            "description": "读取指定技能包的SKILL.md与元数据",
            "parameters": {
                "type": "object",
                "properties": {"skill_name": {"type": "string"}},
                "required": ["skill_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_skill_files",
            "description": "列出指定技能包内的文件结构",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill_name": {"type": "string"},
                    "max_depth": {"type": "integer", "default": 2},
                },
                "required": ["skill_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_skill_file",
            "description": "读取技能包内的文件内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill_name": {"type": "string"},
                    "relative_path": {"type": "string"},
                    "max_chars": {"type": "integer", "default": 12000},
                },
                "required": ["skill_name", "relative_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_skill_command",
            "description": "在技能包目录内执行命令（限定可执行程序）",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill_name": {"type": "string"},
                    "command": {"type": "array", "items": {"type": "string"}},
                    "cwd_relative": {"type": "string"},
                    "auto_install": {"type": "boolean", "default": False},
                },
                "required": ["skill_name", "command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_session_context",
            "description": "获取本次会话的技能目录与临时目录信息",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_temp_file",
            "description": "将文本写入 temp 会话目录（相对路径）",
            "parameters": {
                "type": "object",
                "properties": {
                    "relative_path": {"type": "string", "minLength": 1},
                    "content": {"type": "string"},
                },
                "required": ["relative_path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_temp_file",
            "description": "读取 temp 会话目录文件内容（相对路径）",
            "parameters": {
                "type": "object",
                "properties": {
                    "relative_path": {"type": "string", "minLength": 1},
                    "max_chars": {"type": "integer", "default": 12000},
                },
                "required": ["relative_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_temp_files",
            "description": "列出 temp 会话目录文件结构",
            "parameters": {
                "type": "object",
                "properties": {"max_depth": {"type": "integer", "default": 4}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_temp_command",
            "description": "在 temp 会话目录内执行命令（限定可执行程序）",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "array", "items": {"type": "string"}},
                    "cwd_relative": {"type": "string"},
                    "auto_install": {"type": "boolean", "default": False},
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "export_temp_file",
            "description": "标记 temp 会话文件为最终交付文件（不复制）",
            "parameters": {
                "type": "object",
                "properties": {
                    "temp_relative_path": {"type": "string", "minLength": 1},
                    "workspace_relative_path": {"type": "string", "minLength": 1},
                    "overwrite": {"type": "boolean", "default": False},
                },
                "required": ["temp_relative_path", "workspace_relative_path"],
            },
        },
    },
]


def _validate_tool_arguments(tool_name: str, arguments: Any) -> tuple[bool, str]:
    if not isinstance(arguments, dict):
        return False, "arguments 必须是对象(dict)"

    required: dict[str, list[str]] = {
        "get_skill_metadata": ["skill_name"],
        "list_skill_files": ["skill_name"],
        "read_skill_file": ["skill_name", "relative_path"],
        "run_skill_command": ["skill_name", "command"],
        "get_session_context": [],
        "write_temp_file": ["relative_path", "content"],
        "read_temp_file": ["relative_path"],
        "list_temp_files": [],
        "run_temp_command": ["command"],
        "export_temp_file": ["temp_relative_path", "workspace_relative_path"],
    }

    if tool_name not in required:
        return True, ""

    missing: list[str] = []
    for key in required[tool_name]:
        val = arguments.get(key)
        if val is None:
            missing.append(key)
            continue
        if isinstance(val, str) and not val.strip():
            missing.append(key)
            continue
        if key == "command" and (not isinstance(val, list) or not val):
            missing.append(key)
            continue

    if missing:
        return False, "缺少或为空的必填参数: " + ", ".join(missing)
    return True, ""


def _tool_call_retry_prompt(tool_name: str, detail: str) -> str:
    return (
        f"你刚才发起的工具调用 `{tool_name}` 参数不合法：{detail}。"
        "请严格按工具 schema 重新发起调用（arguments 必须包含必填字段且非空）。"
    )
