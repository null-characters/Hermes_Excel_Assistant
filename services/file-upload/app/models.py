"""
File Upload Service - 数据模型
"""
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, Field
import uuid
import os


# 文件过期天数
FILE_EXPIRE_DAYS = int(os.getenv("FILE_EXPIRE_DAYS", "7"))


class FileMetadata(BaseModel):
    """文件元数据模型 - 包含用户绑定"""
    file_id: str = Field(default_factory=lambda: f"file_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}")
    user_id: str = Field(..., description="WeCom 用户ID，用于归属验证")
    filename: str
    original_filename: str
    content_type: str
    file_size: int
    upload_time: datetime = Field(default_factory=datetime.now)
    expires_at: datetime = Field(default_factory=lambda: datetime.now() + timedelta(days=FILE_EXPIRE_DAYS))
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_id": "file_20260514_abc12345",
                "user_id": "WangWei",
                "filename": "data_20260514_abc12345.xlsx",
                "original_filename": "销售数据.xlsx",
                "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "file_size": 102400,
                "upload_time": "2026-05-14T10:30:00",
                "expires_at": "2026-05-21T10:30:00"
            }
        }


class UploadResponse(BaseModel):
    """上传响应模型"""
    file_id: str
    user_id: str
    filename: str
    expires_at: datetime
    message: str = "文件上传成功"


class FileInfo(BaseModel):
    """文件信息模型"""
    file_id: str
    filename: str
    original_filename: str
    file_size: int
    content_type: str
    upload_time: datetime
    expires_at: datetime


class ErrorResponse(BaseModel):
    """错误响应模型"""
    detail: str
    error_code: Optional[str] = None
