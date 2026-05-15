"""
Task Runner Component
=====================

任务执行组件，调用 Hermes Bridge API 提交任务。
"""

import httpx
import os
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

BRIDGE_API_URL = os.getenv("BRIDGE_API_URL", "http://hermes-bridge:8000")


class TaskRunner:
    """任务执行器"""
    
    def __init__(self, bridge_url: Optional[str] = None):
        self.bridge_url = bridge_url or BRIDGE_API_URL
        self.timeout = 300
    
    def save_upload_file(
        self,
        session_id: str,
        uploaded_file,
        data_path: Path
    ) -> str:
        """保存上传文件到会话目录"""
        uploads_path = data_path / session_id / "uploads"
        uploads_path.mkdir(parents=True, exist_ok=True)
        
        file_path = uploads_path / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        logger.info(f"文件已保存: {file_path}")
        return str(file_path)
    
    def run_task(
        self,
        session_id: str,
        uploaded_file,
        instruction: str,
        data_path: Path
    ) -> dict:
        """执行任务"""
        try:
            file_path = self.save_upload_file(session_id, uploaded_file, data_path)
            
            # 容器内路径映射
            container_file_path = file_path.replace(
                str(data_path), "/app/data/sessions"
            )
            
            payload = {
                "file_path": container_file_path,
                "task": instruction,
                "session_id": session_id
            }
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.bridge_url}/api/task/excel",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": data.get("success", False),
                        "output": data.get("output", ""),
                        "error": data.get("error"),
                        "message": data.get("message", "")
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API 错误: {response.status_code}",
                        "output": ""
                    }
                    
        except httpx.TimeoutException:
            return {"success": False, "error": "请求超时", "output": ""}
        except httpx.ConnectError:
            return {"success": False, "error": "无法连接到 Bridge API", "output": ""}
        except Exception as e:
            logger.error(f"任务执行失败: {e}")
            return {"success": False, "error": str(e), "output": ""}


_task_runner: Optional[TaskRunner] = None


def get_task_runner() -> TaskRunner:
    """获取全局 TaskRunner 实例"""
    global _task_runner
    if _task_runner is None:
        _task_runner = TaskRunner()
    return _task_runner
