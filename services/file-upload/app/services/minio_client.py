"""
MinIO 客户端封装
"""
import os
import json
import io
from typing import Optional
from minio import Minio
from minio.error import S3Error
import logging

logger = logging.getLogger(__name__)


class MinIOClient:
    """MinIO 客户端封装类"""
    
    def __init__(self):
        self.endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
        self.access_key = os.getenv("MINIO_ACCESS_KEY", "admin")
        self.secret_key = os.getenv("MINIO_SECRET_KEY", "your-password")
        self.bucket_name = os.getenv("MINIO_BUCKET", "excel-files")
        self.secure = os.getenv("MINIO_SECURE", "false").lower() == "true"
        
        self.client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure
        )
        
        # 确保 bucket 存在
        self._ensure_bucket()
    
    def _ensure_bucket(self) -> None:
        """
        确保 bucket 存在
        
        如果 bucket 不存在则创建，失败时抛出异常。
        
        Raises:
            S3Error: MinIO 操作失败时抛出
        """
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error ensuring bucket: {e}")
            raise
    
    def upload_file(
        self,
        file_data: bytes,
        filename: str,
        content_type: str,
        metadata: dict
    ) -> bool:
        """
        上传文件到 MinIO
        
        Args:
            file_data: 文件二进制数据，不能为空
            filename: 存储文件名，不能为空
            content_type: MIME 类型
            metadata: 文件元数据字典
        
        Returns:
            bool: 上传成功返回 True，失败返回 False
        
        Raises:
            ValueError: 参数为空时抛出
        """
        # 参数验证
        if not file_data:
            raise ValueError("file_data 不能为空")
        if not filename:
            raise ValueError("filename 不能为空")
        
        try:
            # 将元数据存储为 JSON
            metadata_bytes = json.dumps(metadata).encode('utf-8')
            
            # 上传元数据
            self.client.put_object(
                self.bucket_name,
                f"{filename}.meta",
                io.BytesIO(metadata_bytes),
                len(metadata_bytes),
                content_type="application/json"
            )
            
            # 上传文件
            self.client.put_object(
                self.bucket_name,
                filename,
                io.BytesIO(file_data),
                len(file_data),
                content_type=content_type
            )
            
            logger.info(f"Uploaded file: {filename}")
            return True
        except S3Error as e:
            logger.error(f"Error uploading file: {e}")
            return False
    
    def download_file(self, filename: str) -> Optional[bytes]:
        """
        从 MinIO 下载文件
        
        Args:
            filename: 文件名
        
        Returns:
            Optional[bytes]: 文件内容，不存在或失败返回 None
        """
        try:
            response = self.client.get_object(self.bucket_name, filename)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            logger.error(f"Error downloading file: {e}")
            return None
    
    def get_metadata(self, filename: str) -> Optional[dict]:
        """
        获取文件元数据
        
        Args:
            filename: 文件名
        
        Returns:
            Optional[dict]: 元数据字典，不存在或失败返回 None
        """
        try:
            response = self.client.get_object(
                self.bucket_name,
                f"{filename}.meta"
            )
            data = response.read()
            response.close()
            response.release_conn()
            return json.loads(data.decode('utf-8'))
        except S3Error as e:
            logger.error(f"Error getting metadata: {e}")
            return None
    
    def delete_file(self, filename: str) -> bool:
        """
        删除文件及其元数据
        
        Args:
            filename: 文件名
        
        Returns:
            bool: 删除成功返回 True，失败返回 False
        """
        try:
            self.client.remove_object(self.bucket_name, filename)
            self.client.remove_object(
                self.bucket_name,
                f"{filename}.meta"
            )
            logger.info(f"Deleted file: {filename}")
            return True
        except S3Error as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    def file_exists(self, filename: str) -> bool:
        """
        检查文件是否存在
        
        Args:
            filename: 文件名
        
        Returns:
            bool: 存在返回 True，不存在返回 False
        """
        try:
            self.client.stat_object(self.bucket_name, filename)
            return True
        except S3Error:
            return False


# 全局客户端实例
_client: Optional[MinIOClient] = None


def get_minio_client() -> MinIOClient:
    """
    获取 MinIO 客户端单例
    
    Returns:
        MinIOClient: MinIO 客户端实例
    """
    global _client
    if _client is None:
        _client = MinIOClient()
    return _client