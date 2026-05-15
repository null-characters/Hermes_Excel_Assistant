"""
Task Router
===========

任务提交 API 路由。
"""

from fastapi import APIRouter, HTTPException, Request, Body
from pydantic import BaseModel, Field
from typing import Optional
import logging

from app.services.hermes_client import HermesClient

logger = logging.getLogger(__name__)
router = APIRouter()


class TaskRequest(BaseModel):
    """任务请求"""
    message: str = Field(..., description="任务消息/指令")
    file_id: Optional[str] = Field(None, description="关联的文件 ID")
    user_id: Optional[str] = Field(None, description="用户 ID")
    timeout: Optional[int] = Field(None, description="超时时间（秒）")


class TaskResponse(BaseModel):
    """任务响应"""
    success: bool
    message: str
    output: str
    error: Optional[str] = None
    task_id: Optional[str] = None


class ExcelTaskRequest(BaseModel):
    """Excel 处理任务请求"""
    file_path: str = Field(..., description="文件在容器内的绝对路径")
    task: str = Field(..., description="处理任务描述")
    session_id: str = Field(..., description="会话 ID")
    output_dir: Optional[str] = Field(None, description="输出目录路径")
    timeout: Optional[int] = Field(None, description="超时时间（秒）")


def get_hermes_client(req: Request) -> HermesClient:
    """获取 Hermes 客户端"""
    return req.app.state.hermes_client


@router.post("/submit", response_model=TaskResponse)
async def submit_task(
    req: Request,
    task_request: TaskRequest = Body(...),
):
    """
    提交任务到 Hermes Agent
    
    示例请求：
    ```json
    {
        "message": "帮我分析这个数据",
        "file_id": "file_20260515_xxx",
        "user_id": "user_001"
    }
    ```
    """
    hermes_client: HermesClient = req.app.state.hermes_client
    
    if not hermes_client.is_available():
        raise HTTPException(
            status_code=503,
            detail="Hermes Agent 服务不可用"
        )
    
    logger.info(f"收到任务请求: {task_request.message[:50]}...")
    
    result = await hermes_client.send_message(
        message=task_request.message,
        file_id=task_request.file_id,
        user_id=task_request.user_id
    )
    
    return TaskResponse(
        success=result.success,
        message=result.message,
        output=result.output,
        error=result.error,
        task_id=None
    )


@router.post("/excel", response_model=TaskResponse)
async def process_excel(
    req: Request,
    excel_request: ExcelTaskRequest = Body(...),
):
    """
    处理 Excel 文件
    
    示例请求：
    ```json
    {
        "file_path": "/app/data/sessions/sess_xxx/uploads/example.xlsx",
        "task": "替换第一行数据为：员工姓名,所属部门,年龄,入职时间,月薪",
        "session_id": "sess_xxx",
        "output_dir": "/app/data/sessions/sess_xxx/outputs"
    }
    ```
    """
    hermes_client: HermesClient = req.app.state.hermes_client
    
    if not hermes_client.is_available():
        raise HTTPException(
            status_code=503,
            detail="Hermes Agent 服务不可用"
        )
    
    logger.info(f"收到 Excel 处理请求: {excel_request.file_path} - {excel_request.task[:50]}...")
    
    result = await hermes_client.process_excel(
        file_path=excel_request.file_path,
        task=excel_request.task,
        session_id=excel_request.session_id,
        output_dir=excel_request.output_dir
    )
    
    return TaskResponse(
        success=result.success,
        message=result.message,
        output=result.output,
        error=result.error
    )


@router.get("/status")
async def get_status(req: Request):
    """获取 Hermes Agent 状态"""
    hermes_client: HermesClient = req.app.state.hermes_client
    return {
        "available": hermes_client.is_available(),
        "container": hermes_client.CONTAINER_NAME
    }