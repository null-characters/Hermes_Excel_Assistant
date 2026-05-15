"""
Validators - 路径白名单和命令黑名单校验
========================================

安全校验模块，防止路径遍历攻击和危险命令注入。
"""

import os
import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# 基础路径，容器内为 /app/data/sessions，本地开发为 ./data/sessions
ALLOWED_BASE_PATH = os.getenv("SESSION_BASE_PATH", "./data/sessions")

# 危险命令正则黑名单
DANGEROUS_COMMANDS = [
    r"rm\s+-rf\s+/",
    r"rm\s+-rf\s+~",
    r"sudo\s+",
    r"chmod\s+777",
    r"chmod\s+-R\s+777",
    r">\s*/dev/",
    r"mkfs",
    r"dd\s+if=",
    r":\(\)\{.*;\}\s*;",  # fork bomb
    r"curl\s+.*\|\s*sh",   # pipe to shell
    r"wget\s+.*\|\s*sh",   # pipe to shell
]


class PathValidationError(ValueError):
    """路径校验失败"""
    pass


class PromptValidationError(ValueError):
    """Prompt 校验失败"""
    pass


def validate_path(path: str, session_id: str) -> Path:
    """
    验证路径在会话目录内（路径白名单）

    Args:
        path: 待验证的路径
        session_id: 会话 ID

    Returns:
        Path: 规范化后的安全路径

    Raises:
        PathValidationError: 路径不在会话目录内
    """
    # 额外检查：原始路径中的遍历字符（优先检测）
    if ".." in str(path):
        raise PathValidationError(
            f"路径包含遍历字符: {path}"
        )

    # 规范化基础路径
    base = Path(ALLOWED_BASE_PATH).resolve()
    session_base = (base / session_id).resolve()

    # 规范化待验证路径
    target = Path(path)

    # 如果是相对路径，基于会话目录解析
    if not target.is_absolute():
        target = (session_base / target).resolve()
    else:
        target = target.resolve()

    # 检查路径是否在会话目录内
    try:
        target.relative_to(session_base)
    except ValueError:
        raise PathValidationError(
            f"路径越权访问: {path} 不在会话目录 {session_base} 内"
        )

    return target


def validate_prompt(prompt: str) -> str:
    """
    检测 prompt 中的危险命令（命令黑名单）

    Args:
        prompt: 用户输入的 prompt

    Returns:
        str: 校验通过的 prompt

    Raises:
        PromptValidationError: prompt 包含危险命令
    """
    for pattern in DANGEROUS_COMMANDS:
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            raise PromptValidationError(
                f"Prompt 包含危险命令: 匹配到 '{match.group()}'"
            )

    return prompt
