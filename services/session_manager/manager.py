"""
Session Manager - 会话管理模块
==============================

管理会话目录的创建、删除、列表，以及 SQLite 数据库初始化。

目录结构:
    data/sessions/{session_id}/
    ├── workspace.db      # SQLite 数据库
    ├── uploads/          # 上传文件
    └── outputs/          # 输出文件
"""

import os
import uuid
import sqlite3
import logging
import shutil
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# 基础路径，容器内为 /app/data/sessions，本地开发为 ./data/sessions
BASE_PATH = Path(os.getenv("SESSION_BASE_PATH", "./data/sessions"))


class SessionManager:
    """会话管理器"""

    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or BASE_PATH
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._schema_path = Path(__file__).parent / "schema.sql"

    def create_session(self, session_id: Optional[str] = None) -> str:
        """
        创建新会话

        Args:
            session_id: 可选的会话 ID，不提供则自动生成

        Returns:
            str: 会话 ID
        """
        if session_id is None:
            session_id = f"sess_{uuid.uuid4().hex[:12]}"

        session_path = self.get_session_path(session_id)

        if session_path.exists():
            logger.warning(f"会话已存在: {session_id}")
            return session_id

        # 创建目录结构
        (session_path / "uploads").mkdir(parents=True, exist_ok=True)
        (session_path / "outputs").mkdir(parents=True, exist_ok=True)

        # 初始化 SQLite 数据库
        db_path = session_path / "workspace.db"
        self._init_database(db_path)

        logger.info(f"会话已创建: {session_id}")
        return session_id

    def _init_database(self, db_path: Path) -> None:
        """初始化 SQLite 数据库"""
        with open(self._schema_path, "r") as f:
            schema_sql = f.read()

        conn = sqlite3.connect(str(db_path))
        try:
            conn.executescript(schema_sql)
            conn.commit()
        finally:
            conn.close()

    def delete_session(self, session_id: str) -> bool:
        """
        删除会话及其所有数据

        Args:
            session_id: 会话 ID

        Returns:
            bool: 是否删除成功
        """
        session_path = self.get_session_path(session_id)

        if not session_path.exists():
            logger.warning(f"会话不存在: {session_id}")
            return False

        shutil.rmtree(session_path)
        logger.info(f"会话已删除: {session_id}")
        return True

    def list_sessions(self) -> list[str]:
        """
        列出所有会话 ID

        Returns:
            list[str]: 会话 ID 列表
        """
        if not self.base_path.exists():
            return []

        sessions = []
        for item in self.base_path.iterdir():
            if item.is_dir() and (item / "workspace.db").exists():
                sessions.append(item.name)

        return sorted(sessions)

    def get_session_path(self, session_id: str) -> Path:
        """
        获取会话目录路径

        Args:
            session_id: 会话 ID

        Returns:
            Path: 会话目录路径
        """
        return self.base_path / session_id

    def get_uploads_path(self, session_id: str) -> Path:
        """获取会话上传目录路径"""
        return self.get_session_path(session_id) / "uploads"

    def get_outputs_path(self, session_id: str) -> Path:
        """获取会话输出目录路径"""
        return self.get_session_path(session_id) / "outputs"

    def get_database_path(self, session_id: str) -> Path:
        """获取会话数据库路径"""
        return self.get_session_path(session_id) / "workspace.db"

    def session_exists(self, session_id: str) -> bool:
        """检查会话是否存在"""
        return self.get_session_path(session_id).exists()

    def get_session_info(self, session_id: str) -> Optional[dict]:
        """
        获取会话信息

        Args:
            session_id: 会话 ID

        Returns:
            dict: 会话信息，不存在返回 None
        """
        session_path = self.get_session_path(session_id)

        if not session_path.exists():
            return None

        db_path = session_path / "workspace.db"
        uploads_path = session_path / "uploads"
        outputs_path = session_path / "outputs"

        # 统计文件数
        upload_files = list(uploads_path.iterdir()) if uploads_path.exists() else []
        output_files = list(outputs_path.iterdir()) if outputs_path.exists() else []

        # 统计任务数
        task_count = 0
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            try:
                cursor = conn.execute("SELECT COUNT(*) FROM tasks")
                task_count = cursor.fetchone()[0]
            finally:
                conn.close()

        return {
            "session_id": session_id,
            "path": str(session_path),
            "upload_count": len(upload_files),
            "output_count": len(output_files),
            "task_count": task_count,
        }


# 全局单例
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """获取全局 SessionManager 实例"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
