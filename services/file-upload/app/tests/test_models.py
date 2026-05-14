"""
File Upload Service - 数据模型单元测试
TDD 测试用例
"""
import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

from app.models import (
    FileMetadata,
    UploadResponse,
    FileInfo,
    ErrorResponse,
    FILE_EXPIRE_DAYS
)


class TestFileMetadata:
    """FileMetadata 模型测试"""

    def test_create_with_all_fields(self):
        """测试创建完整元数据"""
        now = datetime.now()
        metadata = FileMetadata(
            file_id="file_20260514_abc12345",
            user_id="test_user",
            filename="file_20260514_abc12345.xlsx",
            original_filename="销售数据.xlsx",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            file_size=102400,
            upload_time=now,
            expires_at=now + timedelta(days=7)
        )

        assert metadata.file_id == "file_20260514_abc12345"
        assert metadata.user_id == "test_user"
        assert metadata.filename == "file_20260514_abc12345.xlsx"
        assert metadata.original_filename == "销售数据.xlsx"
        assert metadata.file_size == 102400
        assert metadata.upload_time == now

    def test_create_with_minimal_fields(self):
        """测试仅必填字段创建"""
        metadata = FileMetadata(
            file_id="file_20260514_xyz",
            user_id="user123",
            filename="test.xlsx",
            original_filename="test.xlsx",
            content_type="application/vnd.ms-excel",
            file_size=100
        )

        assert metadata.file_id == "file_20260514_xyz"
        assert metadata.upload_time is not None
        assert metadata.expires_at is not None

    def test_expires_at_default_value(self):
        """测试过期时间默认值为 7 天后"""
        before = datetime.now()
        metadata = FileMetadata(
            file_id="file_test",
            user_id="user",
            filename="test.xlsx",
            original_filename="test.xlsx",
            content_type="application/vnd.ms-excel",
            file_size=100
        )
        after = datetime.now()

        expected_min = before + timedelta(days=FILE_EXPIRE_DAYS)
        expected_max = after + timedelta(days=FILE_EXPIRE_DAYS)

        assert expected_min <= metadata.expires_at <= expected_max

    def test_missing_required_field_file_id(self):
        """测试缺少必填字段 file_id"""
        with pytest.raises(ValidationError) as exc_info:
            FileMetadata(
                user_id="user",
                filename="test.xlsx",
                original_filename="test.xlsx",
                content_type="application/vnd.ms-excel",
                file_size=100
            )
        assert "file_id" in str(exc_info.value)

    def test_missing_required_field_user_id(self):
        """测试缺少必填字段 user_id"""
        with pytest.raises(ValidationError) as exc_info:
            FileMetadata(
                file_id="file_test",
                filename="test.xlsx",
                original_filename="test.xlsx",
                content_type="application/vnd.ms-excel",
                file_size=100
            )
        assert "user_id" in str(exc_info.value)

    def test_model_dump(self):
        """测试序列化为字典"""
        metadata = FileMetadata(
            file_id="file_test",
            user_id="user",
            filename="test.xlsx",
            original_filename="原始文件.xlsx",
            content_type="application/vnd.ms-excel",
            file_size=100
        )

        data = metadata.model_dump()

        assert isinstance(data, dict)
        assert data["file_id"] == "file_test"
        assert data["user_id"] == "user"
        assert data["original_filename"] == "原始文件.xlsx"

    def test_chinese_filename(self):
        """测试中文文件名"""
        metadata = FileMetadata(
            file_id="file_test",
            user_id="user",
            filename="test.xlsx",
            original_filename="销售报表_2024年第一季度.xlsx",
            content_type="application/vnd.ms-excel",
            file_size=100
        )

        assert metadata.original_filename == "销售报表_2024年第一季度.xlsx"


class TestUploadResponse:
    """UploadResponse 模型测试"""

    def test_create_with_all_fields(self):
        """测试创建完整响应"""
        expires = datetime.now() + timedelta(days=7)
        response = UploadResponse(
            file_id="file_test",
            user_id="user",
            filename="test.xlsx",
            expires_at=expires,
            message="上传成功"
        )

        assert response.file_id == "file_test"
        assert response.message == "上传成功"

    def test_default_message(self):
        """测试默认消息"""
        response = UploadResponse(
            file_id="file_test",
            user_id="user",
            filename="test.xlsx",
            expires_at=datetime.now()
        )

        assert response.message == "文件上传成功"


class TestFileInfo:
    """FileInfo 模型测试"""

    def test_create_with_all_fields(self):
        """测试创建完整文件信息"""
        now = datetime.now()
        expires = now + timedelta(days=7)
        info = FileInfo(
            file_id="file_test",
            filename="test.xlsx",
            original_filename="原始文件.xlsx",
            file_size=1024,
            content_type="application/vnd.ms-excel",
            upload_time=now,
            expires_at=expires
        )

        assert info.file_id == "file_test"
        assert info.file_size == 1024
        assert info.upload_time == now

    def test_missing_required_fields(self):
        """测试缺少必填字段"""
        with pytest.raises(ValidationError):
            FileInfo(
                file_id="file_test",
                filename="test.xlsx"
            )


class TestErrorResponse:
    """ErrorResponse 模型测试"""

    def test_create_with_detail_only(self):
        """测试仅创建错误详情"""
        error = ErrorResponse(detail="文件不存在")

        assert error.detail == "文件不存在"
        assert error.error_code is None

    def test_create_with_error_code(self):
        """测试创建带错误码的响应"""
        error = ErrorResponse(
            detail="文件不存在",
            error_code="FILE_NOT_FOUND"
        )

        assert error.detail == "文件不存在"
        assert error.error_code == "FILE_NOT_FOUND"


class TestFileExpireDays:
    """FILE_EXPIRE_DAYS 常量测试"""

    def test_default_value(self):
        """测试默认值为 7"""
        assert FILE_EXPIRE_DAYS == 7

    def test_is_integer(self):
        """测试值为整数"""
        assert isinstance(FILE_EXPIRE_DAYS, int)

    def test_positive_value(self):
        """测试值为正数"""
        assert FILE_EXPIRE_DAYS > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
