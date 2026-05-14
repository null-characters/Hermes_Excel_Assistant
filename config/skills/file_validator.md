# 文件归属验证技能规范

## 技能名称
file_validator

## 描述
验证用户对文件的访问权限，确保用户只能访问自己上传的文件。

## 安全要求（P0）

这是系统安全的关键组件，必须严格执行用户归属验证。

## 验证流程

```
1. 解析用户指令中的 file_id
2. 调用 File Upload Service 获取文件元数据
3. 比对元数据中的 user_id 与当前用户ID
4. 验证通过 → 允许处理
5. 验证失败 → 拒绝访问，返回错误消息
```

## 技术实现

```python
import httpx
import os

async def validate_file_ownership(file_id: str, user_id: str) -> dict:
    """
    验证文件归属
    
    Args:
        file_id: 文件ID
        user_id: 当前用户ID
    
    Returns:
        dict: 文件信息（验证通过）
    
    Raises:
        PermissionError: 归属验证失败
        FileNotFoundError: 文件不存在
    """
    # File Upload Service 地址
    upload_service = os.getenv("FILE_UPLOAD_SERVICE", "http://file-upload:8000")
    
    async with httpx.AsyncClient() as client:
        # 获取文件信息
        response = await client.get(
            f"{upload_service}/api/info/{file_id}",
            params={"user_id": user_id}
        )
        
        if response.status_code == 403:
            raise PermissionError("无权访问此文件：文件归属验证失败")
        
        if response.status_code == 404:
            raise FileNotFoundError("文件不存在或已过期")
        
        if response.status_code != 200:
            raise Exception(f"文件验证失败: {response.text}")
        
        return response.json()


def extract_file_id(message: str) -> str | None:
    """
    从用户消息中提取 file_id
    
    Args:
        message: 用户消息
    
    Returns:
        str | None: file_id 或 None
    """
    import re
    # 匹配 file_YYYYMMDD_xxxxxxxx 格式
    match = re.search(r'file_\d{8}_[a-f0-9]{8}', message)
    return match.group(0) if match else None
```

## 使用示例

```python
async def handle_user_message(message: str, user_id: str):
    """处理用户消息"""
    
    # 1. 提取 file_id
    file_id = extract_file_id(message)
    if not file_id:
        return "请提供有效的文件ID"
    
    try:
        # 2. 验证归属
        file_info = await validate_file_ownership(file_id, user_id)
        
        # 3. 处理文件
        # ...
        
    except PermissionError as e:
        return f"❌ {str(e)}\n\n您只能处理自己上传的文件。"
    
    except FileNotFoundError as e:
        return f"❌ {str(e)}\n\n请重新上传文件。"
```

## 错误消息模板

| 场景 | 错误消息 |
|------|----------|
| 归属验证失败 | "无权访问此文件：文件归属验证失败。您只能处理自己上传的文件。" |
| 文件不存在 | "文件不存在或已过期。请重新上传文件。" |
| file_id 格式错误 | "文件ID格式错误。请使用上传时返回的文件ID。" |

## 安全日志

所有验证操作必须记录安全日志：

```python
import logging

security_logger = logging.getLogger("security")

def log_validation_attempt(file_id: str, user_id: str, success: bool):
    security_logger.info(
        f"File validation - file_id: {file_id}, user_id: {user_id}, success: {success}"
    )
```

## 版本
v1.0.0