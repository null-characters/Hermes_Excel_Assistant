"""
File Upload Service - 单元测试
"""
import pytest
from httpx import AsyncClient
from app.main import app
import io


@pytest.fixture
def sample_excel_content():
    """创建示例 Excel 文件内容（实际是空文件，仅用于测试）"""
    return b"PK\x03\x04" + b"\x00" * 100  # ZIP 文件头（xlsx 实际是 ZIP 格式）


@pytest.mark.asyncio
async def test_health_check():
    """测试健康检查端点"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_root():
    """测试根路径"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "upload_url" in data


@pytest.mark.asyncio
async def test_upload_file_invalid_type():
    """测试上传非 Excel 文件"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 上传文本文件
        file_content = b"This is not an Excel file"
        files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
        response = await client.post("/api/upload?user_id=test_user", files=files)
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_upload_file_missing_user_id():
    """测试缺少用户ID的上传请求"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        file_content = b"PK\x03\x04" + b"\x00" * 100
        files = {"file": ("test.xlsx", io.BytesIO(file_content), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        response = await client.post("/api/upload", files=files)
        assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_download_file_not_found():
    """测试下载不存在的文件"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/download/file_not_exist?user_id=test_user")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_file_info_not_found():
    """测试获取不存在文件的信息"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/info/file_not_exist?user_id=test_user")
        assert response.status_code == 404


# 集成测试需要 MinIO 服务，标记为 integration
@pytest.mark.integration
@pytest.mark.asyncio
async def test_upload_and_download_flow():
    """测试完整的上传下载流程（需要 MinIO）"""
    # 此测试需要 MinIO 服务运行
    # 在 CI/CD 中使用 MinIO 容器
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])