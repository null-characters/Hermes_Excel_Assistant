# 本地开发指南

> 无需企业微信管理员权限，快速启动核心服务进行开发调试

---

## 适用场景

- 没有企业微信管理员权限
- 只想测试文件上传/下载/处理功能
- 开发调试 Hermes Skills
- 学习研究项目架构

---

## 快速启动

### 1. 最小环境配置

```bash
cp .env.example .env
```

**本地开发只需配置**：

```env
# MinIO（必填，自定义密码）
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=your-password-here

# LLM API（必填，处理 Excel 需要）
HERMES_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-xxx

# CORS（本地开发可留空或使用 localhost）
CORS_ORIGINS=http://localhost:*
```

**无需配置**（企微相关）：
- `WECOM_CALLBACK_*` 系列
- `HERMES_DOCKER_BACKEND_*` 系列

---

### 2. 启动核心服务

```bash
# 只启动 minio + file-upload + nginx
docker compose up minio file-upload nginx -d

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f file-upload
```

**服务端口**：
| 服务 | 端口 | 说明 |
|------|------|------|
| nginx | 8080 | HTTP 入口 |
| MinIO API | 9000 | S3 API |
| MinIO Console | 9001 | Web 管理界面 |

---

### 3. 验证服务

```bash
# 健康检查
curl http://localhost:8080/health

# 预期响应
# {"status": "healthy", "service": "file-upload"}
```

---

## API 测试

### 文件上传

```bash
# 创建测试文件
echo "name,age,city\nAlice,25,Beijing\nBob,30,Shanghai" > test.csv

# 上传文件
curl -X POST http://localhost:8080/api/upload \
  -H "X-User-ID: test_user" \
  -F "file=@test.csv"

# 预期响应
# {
#   "success": true,
#   "file_id": "file_20260514_xxx",
#   "filename": "file_20260514_xxx.csv",
#   "original_filename": "test.csv",
#   "file_size": 45,
#   "expires_at": "2026-05-21T..."
# }
```

### 文件下载

```bash
# 下载文件（使用上传返回的 file_id）
curl http://localhost:8080/api/download/file_20260514_xxx.csv \
  -H "X-User-ID: test_user" \
  -o downloaded.csv

# 检查文件
cat downloaded.csv
```

### 文件信息

```bash
# 获取文件信息
curl http://localhost:8080/api/info/file_20260514_xxx.csv \
  -H "X-User-ID: test_user"

# 预期响应
# {
#   "file_id": "file_20260514_xxx",
#   "filename": "file_20260514_xxx.csv",
#   "original_filename": "test.csv",
#   "file_size": 45,
#   "content_type": "text/csv",
#   "upload_time": "2026-05-14T...",
#   "expires_at": "2026-05-21T..."
# }
```

### 文件删除

```bash
# 删除文件
curl -X DELETE http://localhost:8080/api/delete/file_20260514_xxx.csv \
  -H "X-User-ID: test_user"

# 预期响应
# {"success": true, "message": "文件删除成功"}
```

---

## MinIO 管理界面

访问 http://localhost:9001

| 字段 | 值 |
|------|------|
| Username | `admin` |
| Password | `.env` 中的 `MINIO_ROOT_PASSWORD` |

功能：
- 查看上传的文件
- 手动上传/下载文件
- 管理存储桶

---

## 单元测试

```bash
cd services/file-upload

# 运行所有测试
python -m pytest app/tests/ -v

# 运行特定测试文件
python -m pytest app/tests/test_models.py -v
python -m pytest app/tests/test_minio_client.py -v
python -m pytest app/tests/test_upload.py -v

# 带覆盖率
pip install pytest-cov
python -m pytest app/tests/ -v --cov=app
```

---

## Mock 企微消息测试

创建测试脚本模拟企微消息：

```python
# test_hermes_skill.py
import requests

def mock_wecom_message(user_id: str, message: str, file_id: str = None):
    """模拟企微发送消息给 Hermes"""
    payload = {
        "user_id": user_id,
        "message": message
    }
    if file_id:
        payload["file_id"] = file_id
    
    response = requests.post(
        "http://localhost:8080/api/process",
        json=payload
    )
    return response.json()

# 测试用例
if __name__ == "__main__":
    # 测试 1: 简单消息
    result = mock_wecom_message("test_user", "你好")
    print(f"简单消息: {result}")
    
    # 测试 2: 带文件处理
    result = mock_wecom_message(
        "test_user", 
        "分析这个 Excel，提取所有行政部人员",
        file_id="file_20260514_xxx.xlsx"
    )
    print(f"文件处理: {result}")
```

---

## 常见问题

### Q: 端口被占用怎么办？

```bash
# 查看端口占用
lsof -i :8080
lsof -i :9000
lsof -i :9001

# 修改 docker-compose.yml 中的端口映射
ports:
  - "18080:8080"  # 改为其他端口
```

### Q: MinIO 启动失败？

```bash
# 检查数据目录权限
ls -la data/

# 清理重建
docker compose down -v
rm -rf data/minio
docker compose up minio -d
```

### Q: 文件上传后找不到？

```bash
# 检查 MinIO bucket
# 登录 http://localhost:9001
# 查看 uploads bucket

# 检查日志
docker compose logs file-upload | grep -i error
```

---

## 下一步

当你准备好完整测试企微集成时：

1. 创建测试企业：https://work.weixin.qq.com/wework_admin/register_wework?from=test_wework
2. 参考 [README.md](../README.md) 路径 B 配置完整回调
3. 启动所有服务：`docker compose up -d`

---

## 相关文档

- [README.md](../README.md) - 项目总览
- [architecture.md](./standards/skills/architecture.md) - 架构文档
- [API 文档](./api/) - API 详细说明
