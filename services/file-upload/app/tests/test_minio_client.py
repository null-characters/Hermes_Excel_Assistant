"""
File Upload Service - MinIO 客户端单元测试
TDD 测试用例（使用 mock 隔离 MinIO 依赖）
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import io
import json

from app.services.minio_client import MinIOClient, get_minio_client


class TestMinIOClient:
    """MinIOClient 类测试"""

    @patch("app.services.minio_client.Minio")
    def test_init_creates_client(self, mock_minio_class):
        """测试初始化创建 MinIO 客户端"""
        mock_client = MagicMock()
        mock_client.bucket_exists.return_value = True
        mock_minio_class.return_value = mock_client

        with patch.dict("os.environ", {
            "MINIO_ENDPOINT": "localhost:9000",
            "MINIO_ACCESS_KEY": "admin",
            "MINIO_SECRET_KEY": "password",
            "MINIO_BUCKET": "test-bucket",
            "MINIO_SECURE": "false"
        }):
            client = MinIOClient()

            assert client.endpoint == "localhost:9000"
            assert client.bucket_name == "test-bucket"
            mock_minio_class.assert_called_once()

    @patch("app.services.minio_client.Minio")
    def test_ensure_bucket_creates_if_not_exists(self, mock_minio_class):
        """测试 bucket 不存在时自动创建"""
        mock_client = MagicMock()
        mock_client.bucket_exists.return_value = False
        mock_minio_class.return_value = mock_client

        with patch.dict("os.environ", {
            "MINIO_ENDPOINT": "localhost:9000",
            "MINIO_ACCESS_KEY": "admin",
            "MINIO_SECRET_KEY": "password",
            "MINIO_BUCKET": "test-bucket",
            "MINIO_SECURE": "false"
        }):
            MinIOClient()

            mock_client.make_bucket.assert_called_once_with("test-bucket")

    @patch("app.services.minio_client.Minio")
    def test_ensure_bucket_skips_if_exists(self, mock_minio_class):
        """测试 bucket 已存在时跳过创建"""
        mock_client = MagicMock()
        mock_client.bucket_exists.return_value = True
        mock_minio_class.return_value = mock_client

        with patch.dict("os.environ", {
            "MINIO_ENDPOINT": "localhost:9000",
            "MINIO_ACCESS_KEY": "admin",
            "MINIO_SECRET_KEY": "password",
            "MINIO_BUCKET": "test-bucket",
            "MINIO_SECURE": "false"
        }):
            MinIOClient()

            mock_client.make_bucket.assert_not_called()

    @patch("app.services.minio_client.Minio")
    def test_upload_file_success(self, mock_minio_class):
        """测试文件上传成功"""
        mock_client = MagicMock()
        mock_client.bucket_exists.return_value = True
        mock_minio_class.return_value = mock_client

        with patch.dict("os.environ", {
            "MINIO_ENDPOINT": "localhost:9000",
            "MINIO_ACCESS_KEY": "admin",
            "MINIO_SECRET_KEY": "password",
            "MINIO_BUCKET": "test-bucket",
            "MINIO_SECURE": "false"
        }):
            minio = MinIOClient()

            result = minio.upload_file(
                file_data=b"test content",
                filename="test.xlsx",
                content_type="application/vnd.ms-excel",
                metadata={"file_id": "test_123"}
            )

            assert result is True
            assert mock_client.put_object.call_count == 2

    @patch("app.services.minio_client.Minio")
    def test_upload_file_empty_data_raises_error(self, mock_minio_class):
        """测试上传空文件抛出 ValueError"""
        mock_client = MagicMock()
        mock_client.bucket_exists.return_value = True
        mock_minio_class.return_value = mock_client

        with patch.dict("os.environ", {
            "MINIO_ENDPOINT": "localhost:9000",
            "MINIO_ACCESS_KEY": "admin",
            "MINIO_SECRET_KEY": "password",
            "MINIO_BUCKET": "test-bucket",
            "MINIO_SECURE": "false"
        }):
            minio = MinIOClient()

            with pytest.raises(ValueError, match="file_data 不能为空"):
                minio.upload_file(
                    file_data=b"",
                    filename="test.xlsx",
                    content_type="application/vnd.ms-excel",
                    metadata={}
                )

    @patch("app.services.minio_client.Minio")
    def test_upload_file_empty_filename_raises_error(self, mock_minio_class):
        """测试上传空文件名抛出 ValueError"""
        mock_client = MagicMock()
        mock_client.bucket_exists.return_value = True
        mock_minio_class.return_value = mock_client

        with patch.dict("os.environ", {
            "MINIO_ENDPOINT": "localhost:9000",
            "MINIO_ACCESS_KEY": "admin",
            "MINIO_SECRET_KEY": "password",
            "MINIO_BUCKET": "test-bucket",
            "MINIO_SECURE": "false"
        }):
            minio = MinIOClient()

            with pytest.raises(ValueError, match="filename 不能为空"):
                minio.upload_file(
                    file_data=b"content",
                    filename="",
                    content_type="application/vnd.ms-excel",
                    metadata={}
                )

    @patch("app.services.minio_client.Minio")
    def test_download_file_success(self, mock_minio_class):
        """测试文件下载成功"""
        mock_client = MagicMock()
        mock_client.bucket_exists.return_value = True
        mock_response = MagicMock()
        mock_response.read.return_value = b"file content"
        mock_client.get_object.return_value = mock_response
        mock_minio_class.return_value = mock_client

        with patch.dict("os.environ", {
            "MINIO_ENDPOINT": "localhost:9000",
            "MINIO_ACCESS_KEY": "admin",
            "MINIO_SECRET_KEY": "password",
            "MINIO_BUCKET": "test-bucket",
            "MINIO_SECURE": "false"
        }):
            minio = MinIOClient()

            result = minio.download_file("test.xlsx")

            assert result == b"file content"
            mock_client.get_object.assert_called_once_with(
                "test-bucket", "test.xlsx"
            )

    @patch("app.services.minio_client.Minio")
    def test_download_file_not_found(self, mock_minio_class):
        """测试下载不存在的文件返回 None"""
        from minio.error import S3Error

        mock_client = MagicMock()
        mock_client.bucket_exists.return_value = True
        # S3Error 需要正确的参数构造
        mock_client.get_object.side_effect = Exception("NoSuchKey")
        mock_minio_class.return_value = mock_client

        with patch.dict("os.environ", {
            "MINIO_ENDPOINT": "localhost:9000",
            "MINIO_ACCESS_KEY": "admin",
            "MINIO_SECRET_KEY": "password",
            "MINIO_BUCKET": "test-bucket",
            "MINIO_SECURE": "false"
        }):
            minio = MinIOClient()

            result = minio.download_file("nonexistent.xlsx")

            assert result is None

    @patch("app.services.minio_client.Minio")
    def test_get_metadata_success(self, mock_minio_class):
        """测试获取元数据成功"""
        mock_client = MagicMock()
        mock_client.bucket_exists.return_value = True
        mock_response = MagicMock()
        metadata = {"file_id": "test_123", "user_id": "user1"}
        mock_response.read.return_value = json.dumps(metadata).encode()
        mock_client.get_object.return_value = mock_response
        mock_minio_class.return_value = mock_client

        with patch.dict("os.environ", {
            "MINIO_ENDPOINT": "localhost:9000",
            "MINIO_ACCESS_KEY": "admin",
            "MINIO_SECRET_KEY": "password",
            "MINIO_BUCKET": "test-bucket",
            "MINIO_SECURE": "false"
        }):
            minio = MinIOClient()

            result = minio.get_metadata("test.xlsx")

            assert result == metadata
            mock_client.get_object.assert_called_once_with(
                "test-bucket", "test.xlsx.meta"
            )

    @patch("app.services.minio_client.Minio")
    def test_delete_file_success(self, mock_minio_class):
        """测试文件删除成功"""
        mock_client = MagicMock()
        mock_client.bucket_exists.return_value = True
        mock_minio_class.return_value = mock_client

        with patch.dict("os.environ", {
            "MINIO_ENDPOINT": "localhost:9000",
            "MINIO_ACCESS_KEY": "admin",
            "MINIO_SECRET_KEY": "password",
            "MINIO_BUCKET": "test-bucket",
            "MINIO_SECURE": "false"
        }):
            minio = MinIOClient()

            result = minio.delete_file("test.xlsx")

            assert result is True
            assert mock_client.remove_object.call_count == 2

    @patch("app.services.minio_client.Minio")
    def test_file_exists_true(self, mock_minio_class):
        """测试文件存在检查返回 True"""
        mock_client = MagicMock()
        mock_client.bucket_exists.return_value = True
        mock_minio_class.return_value = mock_client

        with patch.dict("os.environ", {
            "MINIO_ENDPOINT": "localhost:9000",
            "MINIO_ACCESS_KEY": "admin",
            "MINIO_SECRET_KEY": "password",
            "MINIO_BUCKET": "test-bucket",
            "MINIO_SECURE": "false"
        }):
            minio = MinIOClient()

            result = minio.file_exists("test.xlsx")

            assert result is True
            mock_client.stat_object.assert_called_once()

    @patch("app.services.minio_client.Minio")
    def test_file_exists_false(self, mock_minio_class):
        """测试文件不存在返回 False"""
        mock_client = MagicMock()
        mock_client.bucket_exists.return_value = True
        mock_client.stat_object.side_effect = Exception("NoSuchKey")
        mock_minio_class.return_value = mock_client

        with patch.dict("os.environ", {
            "MINIO_ENDPOINT": "localhost:9000",
            "MINIO_ACCESS_KEY": "admin",
            "MINIO_SECRET_KEY": "password",
            "MINIO_BUCKET": "test-bucket",
            "MINIO_SECURE": "false"
        }):
            minio = MinIOClient()

            result = minio.file_exists("nonexistent.xlsx")

            assert result is False


class TestGetMinioClient:
    """get_minio_client 单例测试"""

    @patch("app.services.minio_client.Minio")
    def test_singleton_returns_same_instance(self, mock_minio_class):
        """测试单例返回相同实例"""
        mock_client = MagicMock()
        mock_client.bucket_exists.return_value = True
        mock_minio_class.return_value = mock_client

        # 重置全局实例
        import app.services.minio_client as module
        module._client = None

        with patch.dict("os.environ", {
            "MINIO_ENDPOINT": "localhost:9000",
            "MINIO_ACCESS_KEY": "admin",
            "MINIO_SECRET_KEY": "password",
            "MINIO_BUCKET": "test-bucket",
            "MINIO_SECURE": "false"
        }):
            client1 = get_minio_client()
            client2 = get_minio_client()

            assert client1 is client2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
