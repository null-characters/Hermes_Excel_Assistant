"""
File Upload Service - API 路由单元测试
TDD 测试用例（使用 mock 隔离 MinIO 依赖）
"""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import io

from app.main import app


# 常量定义
EXCEL_MIME_TYPE = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
XLS_MIME_TYPE = "application/vnd.ms-excel"

# 测试用的文件类型映射（与 upload.py 中 ALLOWED_EXTENSIONS 对应）
TEST_FILE_TYPES = {
    ".xlsx": EXCEL_MIME_TYPE,
    ".xls": XLS_MIME_TYPE,
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pdf": "application/pdf",
    ".csv": "text/csv",
    ".json": "application/json",
    ".txt": "text/plain",
    ".png": "image/png",
    ".jpg": "image/jpeg",
}


@pytest.fixture
def mock_minio_client():
    """Mock MinIO 客户端"""
    mock = MagicMock()
    mock.upload_file.return_value = True
    mock.download_file.return_value = b"PK\x03\x04" + b"\x00" * 100
    mock.delete_file.return_value = True
    mock.file_exists.return_value = True
    return mock


@pytest.fixture
def sample_metadata():
    """示例文件元数据"""
    return {
        "file_id": "file_20260514_abc12345",
        "user_id": "test_user",
        "filename": "file_20260514_abc12345.xlsx",
        "original_filename": "销售数据.xlsx",
        "content_type": EXCEL_MIME_TYPE,
        "file_size": 1024,
        "upload_time": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(days=7)).isoformat()
    }


@pytest.fixture
def sample_excel_content():
    """创建示例 Excel 文件内容"""
    return b"PK\x03\x04" + b"\x00" * 100


def get_client():
    """创建测试客户端"""
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


class TestHealthCheck:
    """健康检查端点测试"""

    @pytest.mark.asyncio
    async def test_health_check_returns_200(self):
        """测试健康检查返回 200"""
        async with get_client() as client:
            response = await client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"


class TestRootEndpoint:
    """根路径测试"""

    @pytest.mark.asyncio
    async def test_root_returns_upload_url(self):
        """测试根路径返回上传 URL"""
        async with get_client() as client:
            response = await client.get("/")

            assert response.status_code == 200
            data = response.json()
            assert "upload_url" in data


class TestUploadFile:
    """文件上传测试"""

    @pytest.mark.asyncio
    async def test_upload_excel_success(
        self, mock_minio_client, sample_excel_content
    ):
        """测试上传 Excel 文件成功"""
        with patch(
            "app.routers.upload.get_minio_client",
            return_value=mock_minio_client
        ):
            async with get_client() as client:
                files = {
                    "file": (
                        "test.xlsx",
                        io.BytesIO(sample_excel_content),
                        EXCEL_MIME_TYPE
                    )
                }
                response = await client.post(
                    "/api/upload?user_id=test_user",
                    files=files
                )

                assert response.status_code == 200
                data = response.json()
                assert data["file_id"].startswith("file_")
                assert data["user_id"] == "test_user"
                assert data["message"] == "文件上传成功"

    @pytest.mark.asyncio
    async def test_upload_xls_success(
        self, mock_minio_client, sample_excel_content
    ):
        """测试上传 .xls 文件成功"""
        with patch(
            "app.routers.upload.get_minio_client",
            return_value=mock_minio_client
        ):
            async with get_client() as client:
                files = {
                    "file": (
                        "test.xls",
                        io.BytesIO(sample_excel_content),
                        XLS_MIME_TYPE
                    )
                }
                response = await client.post(
                    "/api/upload?user_id=test_user",
                    files=files
                )

                assert response.status_code == 200

    @pytest.mark.asyncio
    @pytest.mark.parametrize("ext,mime_type", list(TEST_FILE_TYPES.items()))
    async def test_upload_various_file_types(
        self, mock_minio_client, ext, mime_type
    ):
        """测试上传各种文件类型成功"""
        sample_content = b"test content for " + ext.encode()
        with patch(
            "app.routers.upload.get_minio_client",
            return_value=mock_minio_client
        ):
            async with get_client() as client:
                files = {
                    "file": (
                        f"test{ext}",
                        io.BytesIO(sample_content),
                        mime_type
                    )
                }
                response = await client.post(
                    "/api/upload?user_id=test_user",
                    files=files
                )

                assert response.status_code == 200, f"Failed for {ext}: {response.json()}"
                data = response.json()
                assert data["file_id"].startswith("file_")
                assert data["user_id"] == "test_user"
                assert data["message"] == "文件上传成功"

    @pytest.mark.asyncio
    async def test_upload_unsupported_type(self):
        """测试上传不支持的文件类型返回 400"""
        async with get_client() as client:
            files = {
                "file": (
                    "test.exe",
                    io.BytesIO(b"binary content"),
                    "application/octet-stream"
                )
            }
            response = await client.post(
                "/api/upload?user_id=test_user",
                files=files
            )

            assert response.status_code == 400
            assert "不支持的文件类型" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_upload_missing_user_id(self, sample_excel_content):
        """测试缺少 user_id 返回 422"""
        async with get_client() as client:
            files = {
                "file": (
                    "test.xlsx",
                    io.BytesIO(sample_excel_content),
                    EXCEL_MIME_TYPE
                )
            }
            response = await client.post("/api/upload", files=files)

            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_upload_empty_file(self):
        """测试上传空文件返回 400"""
        async with get_client() as client:
            files = {
                "file": (
                    "test.xlsx",
                    io.BytesIO(b""),
                    EXCEL_MIME_TYPE
                )
            }
            response = await client.post(
                "/api/upload?user_id=test_user",
                files=files
            )

            assert response.status_code == 400
            assert "文件内容为空" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_upload_storage_failure(
        self, mock_minio_client, sample_excel_content
    ):
        """测试存储失败返回 500"""
        mock_minio_client.upload_file.return_value = False

        with patch(
            "app.routers.upload.get_minio_client",
            return_value=mock_minio_client
        ):
            async with get_client() as client:
                files = {
                    "file": (
                        "test.xlsx",
                        io.BytesIO(sample_excel_content),
                        EXCEL_MIME_TYPE
                    )
                }
                response = await client.post(
                    "/api/upload?user_id=test_user",
                    files=files
                )

                assert response.status_code == 500
                assert "文件存储失败" in response.json()["detail"]


class TestDownloadFile:
    """文件下载测试"""

    @pytest.mark.asyncio
    async def test_download_success(
        self, mock_minio_client, sample_metadata, sample_excel_content
    ):
        """测试下载文件成功"""
        mock_minio_client.get_metadata.return_value = sample_metadata
        mock_minio_client.download_file.return_value = sample_excel_content

        with patch(
            "app.routers.upload.get_minio_client",
            return_value=mock_minio_client
        ):
            async with get_client() as client:
                response = await client.get(
                    "/api/download/file_20260514_abc12345?user_id=test_user"
                )

                assert response.status_code == 200
                assert "attachment" in response.headers["Content-Disposition"]

    @pytest.mark.asyncio
    async def test_download_not_found(self, mock_minio_client):
        """测试下载不存在的文件返回 404"""
        mock_minio_client.get_metadata.return_value = None

        with patch(
            "app.routers.upload.get_minio_client",
            return_value=mock_minio_client
        ):
            async with get_client() as client:
                response = await client.get(
                    "/api/download/nonexistent?user_id=test_user"
                )

                assert response.status_code == 404
                assert "文件不存在" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_download_wrong_user(self, mock_minio_client, sample_metadata):
        """测试非归属用户下载返回 403"""
        sample_metadata["user_id"] = "owner_user"
        mock_minio_client.get_metadata.return_value = sample_metadata

        with patch(
            "app.routers.upload.get_minio_client",
            return_value=mock_minio_client
        ):
            async with get_client() as client:
                response = await client.get(
                    "/api/download/file_test?user_id=other_user"
                )

                assert response.status_code == 403
                assert "无权访问" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_download_expired_file(
        self, mock_minio_client, sample_metadata
    ):
        """测试下载已过期文件返回 404"""
        sample_metadata["expires_at"] = (
            datetime.now() - timedelta(days=1)
        ).isoformat()
        mock_minio_client.get_metadata.return_value = sample_metadata

        with patch(
            "app.routers.upload.get_minio_client",
            return_value=mock_minio_client
        ):
            async with get_client() as client:
                response = await client.get(
                    "/api/download/file_test?user_id=test_user"
                )

                assert response.status_code == 404
                assert "已过期" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_download_invalid_metadata(
        self, mock_minio_client, sample_metadata
    ):
        """测试元数据损坏返回 500"""
        sample_metadata["expires_at"] = "invalid-date"
        mock_minio_client.get_metadata.return_value = sample_metadata

        with patch(
            "app.routers.upload.get_minio_client",
            return_value=mock_minio_client
        ):
            async with get_client() as client:
                response = await client.get(
                    "/api/download/file_test?user_id=test_user"
                )

                assert response.status_code == 500
                assert "元数据损坏" in response.json()["detail"]


class TestGetFileInfo:
    """获取文件信息测试"""

    @pytest.mark.asyncio
    async def test_get_info_success(self, mock_minio_client, sample_metadata):
        """测试获取文件信息成功"""
        mock_minio_client.get_metadata.return_value = sample_metadata

        with patch(
            "app.routers.upload.get_minio_client",
            return_value=mock_minio_client
        ):
            async with get_client() as client:
                response = await client.get(
                    "/api/info/file_20260514_abc12345?user_id=test_user"
                )

                assert response.status_code == 200
                data = response.json()
                assert data["file_id"] == "file_20260514_abc12345"
                assert data["filename"] == "file_20260514_abc12345.xlsx"

    @pytest.mark.asyncio
    async def test_get_info_not_found(self, mock_minio_client):
        """测试获取不存在文件信息返回 404"""
        mock_minio_client.get_metadata.return_value = None

        with patch(
            "app.routers.upload.get_minio_client",
            return_value=mock_minio_client
        ):
            async with get_client() as client:
                response = await client.get(
                    "/api/info/nonexistent?user_id=test_user"
                )

                assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_info_wrong_user(self, mock_minio_client, sample_metadata):
        """测试非归属用户获取信息返回 403"""
        sample_metadata["user_id"] = "owner_user"
        mock_minio_client.get_metadata.return_value = sample_metadata

        with patch(
            "app.routers.upload.get_minio_client",
            return_value=mock_minio_client
        ):
            async with get_client() as client:
                response = await client.get(
                    "/api/info/file_test?user_id=other_user"
                )

                assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_info_invalid_metadata(
        self, mock_minio_client, sample_metadata
    ):
        """测试元数据损坏返回 500"""
        sample_metadata["upload_time"] = ""
        mock_minio_client.get_metadata.return_value = sample_metadata

        with patch(
            "app.routers.upload.get_minio_client",
            return_value=mock_minio_client
        ):
            async with get_client() as client:
                response = await client.get(
                    "/api/info/file_test?user_id=test_user"
                )

                assert response.status_code == 500


class TestDeleteFile:
    """文件删除测试"""

    @pytest.mark.asyncio
    async def test_delete_success(self, mock_minio_client, sample_metadata):
        """测试删除文件成功"""
        mock_minio_client.get_metadata.return_value = sample_metadata
        mock_minio_client.delete_file.return_value = True

        with patch(
            "app.routers.upload.get_minio_client",
            return_value=mock_minio_client
        ):
            async with get_client() as client:
                response = await client.delete(
                    "/api/delete/file_20260514_abc12345?user_id=test_user"
                )

                assert response.status_code == 200
                assert "删除成功" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_delete_not_found(self, mock_minio_client):
        """测试删除不存在文件返回 404"""
        mock_minio_client.get_metadata.return_value = None

        with patch(
            "app.routers.upload.get_minio_client",
            return_value=mock_minio_client
        ):
            async with get_client() as client:
                response = await client.delete(
                    "/api/delete/nonexistent?user_id=test_user"
                )

                assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_wrong_user(self, mock_minio_client, sample_metadata):
        """测试非归属用户删除返回 403"""
        sample_metadata["user_id"] = "owner_user"
        mock_minio_client.get_metadata.return_value = sample_metadata

        with patch(
            "app.routers.upload.get_minio_client",
            return_value=mock_minio_client
        ):
            async with get_client() as client:
                response = await client.delete(
                    "/api/delete/file_test?user_id=other_user"
                )

                assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_failure(self, mock_minio_client, sample_metadata):
        """测试删除失败返回 500"""
        mock_minio_client.get_metadata.return_value = sample_metadata
        mock_minio_client.delete_file.return_value = False

        with patch(
            "app.routers.upload.get_minio_client",
            return_value=mock_minio_client
        ):
            async with get_client() as client:
                response = await client.delete(
                    "/api/delete/file_test?user_id=test_user"
                )

                assert response.status_code == 500


class TestChineseFilename:
    """中文文件名测试"""

    @pytest.mark.asyncio
    async def test_upload_chinese_filename(
        self, mock_minio_client, sample_excel_content
    ):
        """测试上传中文文件名"""
        with patch(
            "app.routers.upload.get_minio_client",
            return_value=mock_minio_client
        ):
            async with get_client() as client:
                files = {
                    "file": (
                        "销售数据_2024.xlsx",
                        io.BytesIO(sample_excel_content),
                        EXCEL_MIME_TYPE
                    )
                }
                response = await client.post(
                    "/api/upload?user_id=test_user",
                    files=files
                )

                assert response.status_code == 200
                assert response.json()["filename"] == "销售数据_2024.xlsx"

    @pytest.mark.asyncio
    async def test_download_chinese_filename_encoding(
        self, mock_minio_client, sample_metadata, sample_excel_content
    ):
        """测试下载中文文件名正确编码"""
        sample_metadata["original_filename"] = "销售报表_第一季度.xlsx"
        mock_minio_client.get_metadata.return_value = sample_metadata
        mock_minio_client.download_file.return_value = sample_excel_content

        with patch(
            "app.routers.upload.get_minio_client",
            return_value=mock_minio_client
        ):
            async with get_client() as client:
                response = await client.get(
                    "/api/download/file_test?user_id=test_user"
                )

                assert response.status_code == 200
                disposition = response.headers["Content-Disposition"]
                assert "UTF-8" in disposition


if __name__ == "__main__":
    pytest.main([__file__, "-v"])