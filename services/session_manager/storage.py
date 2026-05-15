"""
Storage - 本地文件存储模块
===========================

实现会话级文件存储，替代 MinIO。

功能：
- save_upload: 保存上传文件到会话 uploads 目录
- get_download: 从会话 outputs 目录下载文件
- list_outputs: 列出会话输出文件
- record_file: 在 SQLite 中记录文件元数据
"""

import os
import uuid
import sqlite3
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from .manager import get_session_manager
from .validators import validate_path

logger = logging.getLogger(__name__)


class StorageError(Exception):
    """存储操作错误"""
    pass


def save_upload(
    session_id: str,
    file_name: str,
    file_content: bytes,
    record_metadata: bool = True
) -> str:
    """
    保存上传文件到会话 uploads 目录

    Args:
        session_id: 会话 ID
        file_name: 原始文件名
        file_content: 文件内容
        record_metadata: 是否记录元数据到 SQLite

    Returns:
        str: 文件存储路径

    Raises:
        StorageError: 保存失败
    """
    manager = get_session_manager()

    # 确保会话存在
    if not manager.session_exists(session_id):
        manager.create_session(session_id)

    uploads_path = manager.get_uploads_path(session_id)
    uploads_path.mkdir(parents=True, exist_ok=True)

    # 生成唯一文件名
    file_id = f"file_{uuid.uuid4().hex[:8]}"
    timestamp = datetime.now().strftime("%Y%m%d")
    stored_name = f"{timestamp}_{file_id}_{file_name}"

    # 安全校验路径
    file_path = validate_path(f"uploads/{stored_name}", session_id)

    # 写入文件
    try:
        file_path.write_bytes(file_content)
        logger.info(f"文件已保存: {file_path}")
    except Exception as e:
        raise StorageError(f"文件保存失败: {e}")

    # 记录元数据
    if record_metadata:
        record_file(
            session_id=session_id,
            file_id=file_id,
            original_name=file_name,
            stored_path=str(file_path),
            size=len(file_content)
        )

    return str(file_path)


def get_download(session_id: str, file_name: str) -> bytes:
    """
    从会话 outputs 目录下载文件

    Args:
        session_id: 会话 ID
        file_name: 文件名

    Returns:
        bytes: 文件内容

    Raises:
        StorageError: 文件不存在
    """
    # 安全校验路径
    file_path = validate_path(f"outputs/{file_name}", session_id)

    if not file_path.exists():
        raise StorageError(f"文件不存在: {file_name}")

    try:
        return file_path.read_bytes()
    except Exception as e:
        raise StorageError(f"文件读取失败: {e}")


def list_outputs(session_id: str) -> list[dict]:
    """
    列出会话输出文件

    Args:
        session_id: 会话 ID

    Returns:
        list[dict]: 文件信息列表 [{"name": ..., "size": ..., "modified": ...}]
    """
    manager = get_session_manager()
    outputs_path = manager.get_outputs_path(session_id)

    if not outputs_path.exists():
        return []

    files = []
    for f in outputs_path.iterdir():
        if f.is_file():
            stat = f.stat()
            files.append({
                "name": f.name,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })

    return sorted(files, key=lambda x: x["modified"], reverse=True)


def list_uploads(session_id: str) -> list[dict]:
    """
    列出会话上传文件

    Args:
        session_id: 会话 ID

    Returns:
        list[dict]: 文件信息列表
    """
    manager = get_session_manager()
    uploads_path = manager.get_uploads_path(session_id)

    if not uploads_path.exists():
        return []

    files = []
    for f in uploads_path.iterdir():
        if f.is_file():
            stat = f.stat()
            files.append({
                "name": f.name,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })

    return sorted(files, key=lambda x: x["modified"], reverse=True)


def record_file(
    session_id: str,
    file_id: str,
    original_name: str,
    stored_path: str,
    size: int
) -> None:
    """
    在 SQLite 中记录文件元数据

    Args:
        session_id: 会话 ID
        file_id: 文件 ID
        original_name: 原始文件名
        stored_path: 存储路径
        size: 文件大小
    """
    manager = get_session_manager()
    db_path = manager.get_database_path(session_id)

    if not db_path.exists():
        logger.warning(f"数据库不存在: {db_path}")
        return

    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO files (id, original_name, stored_path, size, uploaded_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (file_id, original_name, stored_path, size, datetime.now().isoformat())
        )
        conn.commit()
    finally:
        conn.close()


def get_file_metadata(session_id: str, file_id: str) -> Optional[dict]:
    """
    获取文件元数据

    Args:
        session_id: 会话 ID
        file_id: 文件 ID

    Returns:
        dict: 文件元数据，不存在返回 None
    """
    manager = get_session_manager()
    db_path = manager.get_database_path(session_id)

    if not db_path.exists():
        return None

    conn = sqlite3.connect(str(db_path))
    try:
        cursor = conn.execute(
            "SELECT id, original_name, stored_path, size, uploaded_at FROM files WHERE id = ?",
            (file_id,)
        )
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "original_name": row[1],
                "stored_path": row[2],
                "size": row[3],
                "uploaded_at": row[4],
            }
        return None
    finally:
        conn.close()


def delete_file(session_id: str, file_name: str, is_output: bool = False) -> bool:
    """
    删除文件

    Args:
        session_id: 会话 ID
        file_name: 文件名
        is_output: 是否为输出文件

    Returns:
        bool: 是否删除成功
    """
    subdir = "outputs" if is_output else "uploads"
    file_path = validate_path(f"{subdir}/{file_name}", session_id)

    if not file_path.exists():
        return False

    try:
        file_path.unlink()
        logger.info(f"文件已删除: {file_path}")
        return True
    except Exception as e:
        logger.error(f"删除文件失败: {e}")
        return False
