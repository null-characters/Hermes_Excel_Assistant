"""
MinIO 客户端封装
"""
import os
import json
import io
from datetime import datetime, timedelta
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
    
    def _ensure_bucket(self):
        """确保 bucket 存在"""
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
        """上传文件到 MinIO"""
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
        """从 MinIO 下载文件"""
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
        """获取文件元数据"""
        try:
            response = self.client.get_object(self.bucket_name, f"{filename}.meta")
            data = response.read()
            response.close()
            response.release_conn()
            return json.loads(data.decode('utf-8'))
        except S3Error as e:
            logger.error(f"Error getting metadata: {e}")
            return None
    
    def delete_file(self, filename: str) -> bool:
        """删除文件及其元数据"""
        try:
            self.client.remove_object(self.bucket_name, filename)
            self.client.remove_object(self.bucket_name, f"{filename}.meta")
            logger.info(f"Deleted file: {filename}")
            return True
        except S3Error as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    def file_exists(self, filename: str) -> bool:
        """检查文件是否存在"""
        try:
            self.client.stat_object(self.bucket_name, filename)
            return True
        except S3Error:
            return False


# 全局客户端实例
_client: Optional[MinIOClient] = None


def get_minio_client() -> MinIOClient:
    """获取 MinIO 客户端单例"""
    global _client
    if _client is None:
        _client = MinIOClient()
    return _client