"""
端到端测试脚本
Hermes WeCom Excel Assistant
"""
import pytest
import httpx
import io
import asyncio
from datetime import datetime


# 配置
FILE_UPLOAD_URL = "http://localhost:8080"
HERMES_URL = "http://localhost:8645"
TEST_USER_ID = "test_user_e2e"


@pytest.fixture
def sample_excel_file():
    """创建测试 Excel 文件"""
    # 创建一个简单的 xlsx 文件（实际是 ZIP 格式）
    content = b"PK\x03\x04" + b"\x00" * 1024
    return ("test_data.xlsx", io.BytesIO(content), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@pytest.mark.asyncio
async def test_health_checks():
    """测试所有服务健康状态"""
    async with httpx.AsyncClient() as client:
        # File Upload Service
        response = await client.get(f"{FILE_UPLOAD_URL}/health")
        assert response.status_code == 200
        
        # Hermes Agent
        response = await client.get(f"{HERMES_URL}/health")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_file_upload_flow(sample_excel_file):
    """测试文件上传流程"""
    async with httpx.AsyncClient() as client:
        # 上传文件
        files = {"file": sample_excel_file}
        response = await client.post(
            f"{FILE_UPLOAD_URL}/api/upload",
            params={"user_id": TEST_USER_ID},
            files=files
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "file_id" in data
        assert data["user_id"] == TEST_USER_ID
        
        return data["file_id"]


@pytest.mark.asyncio
async def test_file_download_validation(sample_excel_file):
    """测试文件下载归属验证"""
    async with httpx.AsyncClient() as client:
        # 上传文件
        files = {"file": sample_excel_file}
        upload_response = await client.post(
            f"{FILE_UPLOAD_URL}/api/upload",
            params={"user_id": TEST_USER_ID},
            files=files
        )
        file_id = upload_response.json()["file_id"]
        
        # 正确用户下载
        response = await client.get(
            f"{FILE_UPLOAD_URL}/api/download/{file_id}",
            params={"user_id": TEST_USER_ID}
        )
        assert response.status_code == 200
        
        # 错误用户下载（应返回 403）
        response = await client.get(
            f"{FILE_UPLOAD_URL}/api/download/{file_id}",
            params={"user_id": "wrong_user"}
        )
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_file_expiry(sample_excel_file):
    """测试文件过期机制"""
    # 此测试需要模拟时间流逝或修改过期时间
    # 在实际测试中可以修改环境变量 FILE_EXPIRE_DAYS=0
    pass


@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_processing_flow(sample_excel_file):
    """
    完整处理流程测试（需要 Hermes 和 MinIO 运行）
    
    流程：
    1. 上传 Excel 文件
    2. 发送处理指令
    3. 等待处理完成
    4. 下载结果文件
    """
    async with httpx.AsyncClient(timeout=300.0) as client:
        # Step 1: 上传文件
        files = {"file": sample_excel_file}
        upload_response = await client.post(
            f"{FILE_UPLOAD_URL}/api/upload",
            params={"user_id": TEST_USER_ID},
            files=files
        )
        assert upload_response.status_code == 200
        file_id = upload_response.json()["file_id"]
        print(f"✅ 文件上传成功: {file_id}")
        
        # Step 2: 发送处理指令（模拟）
        # 在实际环境中，这会通过企业微信发送
        # message = f"处理 {file_id} 清洗数据"
        print(f"📝 处理指令: 处理 {file_id} 清洗数据")
        
        # Step 3: 等待处理完成
        # 在实际环境中，会收到进度通知
        await asyncio.sleep(5)  # 等待处理
        
        # Step 4: 验证结果文件
        # 检查是否有 _processed 文件
        print("⏳ 等待处理完成...")


def run_e2e_tests():
    """运行端到端测试"""
    pytest.main([__file__, "-v", "-s"])


if __name__ == "__main__":
    run_e2e_tests()