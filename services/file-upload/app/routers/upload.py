"""
文件上传 API 路由
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse
from urllib.parse import quote
import io
import logging

from ..models import FileMetadata, UploadResponse, FileInfo, ErrorResponse
from ..services.minio_client import get_minio_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["文件操作"])

# 常量定义
FILE_ID_HEX_LENGTH = 8  # 文件ID中UUID十六进制长度
DEFAULT_CONTENT_TYPE = "application/octet-stream"

# 支持的文件类型扩展名映射
ALLOWED_EXTENSIONS = {
    # Office 文档
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".xls": "application/vnd.ms-excel",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".doc": "application/msword",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".ppt": "application/vnd.ms-powerpoint",
    # 数据文件
    ".csv": "text/csv",
    ".json": "application/json",
    ".xml": "application/xml",
    ".txt": "text/plain",
    # 图片文件
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    # PDF
    ".pdf": "application/pdf",
    # 压缩文件
    ".zip": "application/zip",
    ".tar": "application/x-tar",
    ".gz": "application/gzip",
}


def get_user_id(user_id: str = Query(..., description="WeCom 用户ID")) -> str:
    """从请求参数获取用户ID"""
    return user_id


@router.post("/upload", response_model=UploadResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def upload_file(
    file: UploadFile = File(..., description="文件"),
    user_id: str = Depends(get_user_id)
):
    """
    上传文件（支持多种格式）
    
    - **file**: 文件（支持 Excel/Word/PPT/PDF/CSV/JSON/TXT/图片等格式）
    - **user_id**: WeCom 用户ID，用于文件归属验证
    """
    # 验证文件类型（通过扩展名）
    filename = file.filename or ""
    file_ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    
    if file_ext not in ALLOWED_EXTENSIONS:
        allowed_list = ", ".join(ALLOWED_EXTENSIONS.keys())
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file_ext}。支持的格式: {allowed_list}"
        )
    
    # 读取文件内容
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="文件内容为空")
    
    # 生成文件元数据
    file_id = (
        f"file_{datetime.now().strftime('%Y%m%d')}_"
        f"{uuid.uuid4().hex[:FILE_ID_HEX_LENGTH]}"
    )
    stored_filename = f"{file_id}{file_ext}"
    
    metadata = FileMetadata(
        file_id=file_id,
        user_id=user_id,
        filename=stored_filename,
        original_filename=file.filename or f"unknown{file_ext}",
        content_type=file.content_type or ALLOWED_EXTENSIONS.get(file_ext, DEFAULT_CONTENT_TYPE),
        file_size=len(content)
    )
    
    # 上传到 MinIO
    minio_client = get_minio_client()
    success = minio_client.upload_file(
        content,
        stored_filename,
        metadata.content_type,
        metadata.model_dump()
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="文件存储失败")
    
    logger.info(f"File uploaded: {file_id} by user {user_id}")
    
    return UploadResponse(
        file_id=file_id,
        user_id=user_id,
        filename=metadata.original_filename,
        expires_at=metadata.expires_at,
        message="文件上传成功"
    )


@router.get("/download/{file_id}", responses={403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def download_file(
    file_id: str,
    user_id: str = Depends(get_user_id)
):
    """
    下载文件（需验证用户归属）
    
    - **file_id**: 文件ID（可带或不带扩展名）
    - **user_id**: WeCom 用户ID，必须与上传时的用户ID一致
    """
    # 处理文件名（兼容带扩展名和不带扩展名的情况）
    # 如果 file_id 不包含扩展名，尝试常见扩展名
    if "." in file_id and file_id.rsplit(".", 1)[-1].lower() in [ext.lstrip(".") for ext in ALLOWED_EXTENSIONS]:
        filename = file_id
    else:
        # 尝试查找文件（兼容旧格式）
        filename = None
        for ext in ALLOWED_EXTENSIONS:
            candidate = f"{file_id}{ext}"
            if get_minio_client().file_exists(candidate):
                filename = candidate
                break
        if not filename:
            raise HTTPException(status_code=404, detail="文件不存在或已过期")
    
    # 获取元数据
    minio_client = get_minio_client()
    metadata = minio_client.get_metadata(filename)
    if metadata is None:
        raise HTTPException(status_code=404, detail="文件不存在或已过期")
    
    # 🔴 归属验证（P0 安全要求）
    if metadata.get("user_id") != user_id:
        logger.warning(f"Access denied: user {user_id} tried to access file {file_id} owned by {metadata.get('user_id')}")
        raise HTTPException(
            status_code=403,
            detail="无权访问此文件：文件归属验证失败"
        )
    
    # 检查过期
    try:
        expires_at = datetime.fromisoformat(metadata.get("expires_at", ""))
    except (ValueError, TypeError):
        logger.error(f"Invalid expires_at in metadata for file {file_id}")
        raise HTTPException(status_code=500, detail="文件元数据损坏")
    
    if datetime.now() > expires_at:
        raise HTTPException(status_code=404, detail="文件已过期")
    
    # 下载文件
    content = minio_client.download_file(filename)
    if content is None:
        raise HTTPException(status_code=500, detail="文件下载失败")
    
    # 返回文件流（安全编码文件名）
    original_filename = metadata.get("original_filename", "download")
    
    return StreamingResponse(
        io.BytesIO(content),
        media_type=metadata.get("content_type", DEFAULT_CONTENT_TYPE),
        headers={
            "Content-Disposition": (
                f"attachment; filename*=UTF-8''{quote(original_filename)}"
            )
        }
    )


@router.get("/info/{file_id}", response_model=FileInfo, responses={403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}})
async def get_file_info(
    file_id: str,
    user_id: str = Depends(get_user_id)
):
    """
    获取文件信息（需验证用户归属）
    
    - **file_id**: 文件ID（可带或不带扩展名）
    - **user_id**: WeCom 用户ID
    """
    minio_client = get_minio_client()
    
    # 处理文件名（兼容带扩展名和不带扩展名的情况）
    if "." in file_id and file_id.rsplit(".", 1)[-1].lower() in [ext.lstrip(".") for ext in ALLOWED_EXTENSIONS]:
        filename = file_id
    else:
        filename = None
        for ext in ALLOWED_EXTENSIONS:
            candidate = f"{file_id}{ext}"
            if minio_client.file_exists(candidate):
                filename = candidate
                break
        if not filename:
            raise HTTPException(status_code=404, detail="文件不存在")
    
    metadata = minio_client.get_metadata(filename)
    if metadata is None:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 归属验证
    if metadata.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="无权访问此文件")
    
    upload_time_str = metadata.get("upload_time", "")
    expires_at_str = metadata.get("expires_at", "")
    
    if not upload_time_str or not expires_at_str:
        raise HTTPException(status_code=500, detail="文件元数据损坏")
    
    try:
        upload_time = datetime.fromisoformat(upload_time_str)
        expires_at = datetime.fromisoformat(expires_at_str)
    except (ValueError, TypeError):
        raise HTTPException(status_code=500, detail="文件元数据损坏")
    
    return FileInfo(
        file_id=metadata.get("file_id"),
        filename=metadata.get("filename"),
        original_filename=metadata.get("original_filename"),
        file_size=metadata.get("file_size"),
        content_type=metadata.get("content_type"),
        upload_time=upload_time,
        expires_at=expires_at
    )


@router.delete("/delete/{file_id}", responses={403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}})
async def delete_file(
    file_id: str,
    user_id: str = Depends(get_user_id)
):
    """
    删除文件（需验证用户归属）
    
    - **file_id**: 文件ID（可带或不带扩展名）
    - **user_id**: WeCom 用户ID
    """
    minio_client = get_minio_client()
    
    # 处理文件名（兼容带扩展名和不带扩展名的情况）
    if "." in file_id and file_id.rsplit(".", 1)[-1].lower() in [ext.lstrip(".") for ext in ALLOWED_EXTENSIONS]:
        filename = file_id
    else:
        filename = None
        for ext in ALLOWED_EXTENSIONS:
            candidate = f"{file_id}{ext}"
            if minio_client.file_exists(candidate):
                filename = candidate
                break
        if not filename:
            raise HTTPException(status_code=404, detail="文件不存在")
    
    metadata = minio_client.get_metadata(filename)
    if metadata is None:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 归属验证
    if metadata.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="无权删除此文件")
    
    success = minio_client.delete_file(filename)
    if not success:
        raise HTTPException(status_code=500, detail="文件删除失败")
    
    return {"message": "文件删除成功", "file_id": file_id}