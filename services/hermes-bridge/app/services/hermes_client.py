"""
Hermes Client Service
=====================

与 Hermes Agent 容器通信的客户端服务。

通过 Docker exec 将任务发送给 Hermes Agent 并获取响应。
"""

import subprocess
import logging
import asyncio
import os
import shlex  # T02-02: Prompt 参数转义
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class HermesResponse:
    """Hermes Agent 响应结果"""
    success: bool
    message: str
    output: str
    error: Optional[str] = None


class HermesClient:
    """Hermes Agent Docker 客户端"""
    
    CONTAINER_NAME = os.getenv("HERMES_CONTAINER_NAME", "hermes-agent")
    TIMEOUT = int(os.getenv("HERMES_TIMEOUT", "300"))
    
    def __init__(self):
        self._container_status = None
    
    def is_available(self) -> bool:
        """检查 Hermes Agent 是否可用"""
        try:
            result = subprocess.run(
                ["docker", "inspect", "-f", "{{.State.Status}}", self.CONTAINER_NAME],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                status = result.stdout.strip()
                self._container_status = status
                return status == "running"
            return False
        except Exception as e:
            logger.warning(f"检查 Hermes Agent 状态失败: {e}")
            return False
    
    async def execute_task(
        self,
        prompt: str,
        timeout: int = None
    ) -> HermesResponse:
        """
        执行任务
        
        Args:
            prompt: 发送给 Hermes Agent 的提示
            timeout: 超时时间（秒）
        
        Returns:
            HermesResponse: 执行结果
        """
        timeout = timeout or self.TIMEOUT
        
        if not self.is_available():
            return HermesResponse(
                success=False,
                message="Hermes Agent 容器不可用",
                output="",
                error="container_not_found"
            )
        
        try:
            logger.info(f"发送任务到 Hermes Agent: {prompt[:100]}...")
            
            # 使用 asyncio 包装同步的 subprocess
            result = await asyncio.to_thread(
                self._exec_in_container,
                prompt,
                timeout
            )
            
            return result
            
        except asyncio.TimeoutError:
            logger.error(f"任务执行超时 ({timeout}s)")
            return HermesResponse(
                success=False,
                message=f"任务执行超时",
                output="",
                error="timeout"
            )
        except Exception as e:
            logger.error(f"任务执行异常: {e}")
            return HermesResponse(
                success=False,
                message=f"执行异常: {str(e)}",
                output="",
                error=str(e)
            )
    
    def _exec_in_container(
        self,
        prompt: str,
        timeout: int
    ) -> HermesResponse:
        """在容器中执行命令"""
        
        # T02-02: Prompt 参数转义，防止命令注入
        # 使用 shlex.quote() 对 prompt 进行 shell 转义
        safe_prompt = shlex.quote(prompt)
        
        # 使用 Hermes Agent 的单次查询模式
        # hermes 在容器中的完整路径
        HERMES_PATH = "/opt/hermes/.venv/bin/hermes"
        
        # 构建 docker exec 命令（prompt 已转义）
        cmd = [
            "docker", "exec", self.CONTAINER_NAME,
            HERMES_PATH, "chat", "-q", safe_prompt
        ]
        
        try:
            logger.info(f"执行命令: docker exec {self.CONTAINER_NAME} hermes chat -q ...")
            
            # 使用 asyncio.to_thread 包装同步的 subprocess
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            logger.debug(f"Exit code: {result.returncode}")
            logger.debug(f"Stdout length: {len(result.stdout)}")
            
            if result.returncode == 0:
                return HermesResponse(
                    success=True,
                    message="任务执行成功",
                    output=result.stdout.strip(),
                    error=None
                )
            else:
                return HermesResponse(
                    success=False,
                    message="任务执行失败",
                    output=result.stdout.strip(),
                    error=result.stderr.strip() if result.stderr else f"exit_code={result.returncode}"
                )
                
        except subprocess.TimeoutExpired:
            logger.error(f"任务执行超时 ({timeout}s)")
            return HermesResponse(
                success=False,
                message=f"任务执行超时",
                output="",
                error="timeout"
            )
        except Exception as e:
            logger.error(f"容器执行异常: {e}")
            return HermesResponse(
                success=False,
                message=f"执行异常: {str(e)}",
                output="",
                error=str(e)
            )
    
    async def send_message(
        self,
        message: str,
        file_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> HermesResponse:
        """
        发送消息到 Hermes Agent
        
        Args:
            message: 用户消息
            file_id: 关联的文件 ID（可选）
            user_id: 用户 ID（可选）
        
        Returns:
            HermesResponse: 响应结果
        """
        # 构造完整提示
        prompt = message
        
        if file_id:
            # 添加文件上下文
            prompt = f"处理文件 {file_id}: {message}"
        
        if user_id:
            prompt = f"[用户 {user_id}] {prompt}"
        
        return await self.execute_task(prompt)
    
    async def process_excel(
        self,
        file_id: str,
        task: str,
        user_id: str = "local_user"
    ) -> HermesResponse:
        """
        处理 Excel 文件
        
        Args:
            file_id: 文件 ID
            task: 处理任务描述
            user_id: 用户 ID
        
        Returns:
            HermesResponse: 处理结果
        """
        prompt = f"处理 {file_id} {task}"
        return await self.send_message(prompt, file_id, user_id)