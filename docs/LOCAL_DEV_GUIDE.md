# 本地开发指南

> 本地化部署，无需企业微信、无需管理员权限

---

## 架构说明

本项目采用**本地化方案**，核心组件：

| 组件 | 端口 | 说明 |
|------|------|------|
| Hermes Bridge | 8646 | 任务提交 API，与 Hermes Agent 通信 |
| File Upload Service | 8080 | 文件上传/下载/管理 |
| Hermes Agent | 8645 | LLM Agent 核心（内部调用） |
| MinIO | 9000/9001 | 对象存储 + Web 管理界面 |
| Prometheus | 9090 | 监控面板 |

**数据流**：
```
用户 → Hermes Bridge API → docker exec → Hermes Agent → LLM 推理
                                                          ↓
用户 ← 结果文件 ← File Upload Service ← MinIO ← 处理结果
```

---

## 快速启动

### 1. 环境配置

```bash
cp .env.example .env
```

**本地开发只需配置**：

```env
# MinIO（必填，自定义密码，8位以上）
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=your-password-here

# LLM API（必填，三选一）

# 方式 1: OpenRouter（推荐，200+ 模型可选）
HERMES_PROVIDER=openrouter
HERMES_MODEL=anthropic/claude-3-sonnet
OPENROUTER_API_KEY=sk-or-xxx

# 方式 2: OpenAI 兼容自定义端点（类 OpenAI 协议）
# 适用于：本地 VLLM/SGLang、自建服务、第三方兼容 API
# HERMES_PROVIDER=openai
# OPENAI_API_KEY=your-api-key
# OPENAI_BASE_URL=https://your-custom-url/v1
# HERMES_MODEL=your-model-name

# 方式 3: 其他提供商
# DEEPSEEK_API_KEY=xxx
# GLM_API_KEY=xxx
# KIMI_API_KEY=xxx
```

**无需配置**（已废弃企微集成）：
- ~~`WECOM_CALLBACK_*` 系列~~

---

### 2. 启动服务

```bash
# 启动所有服务
docker compose up -d

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f hermes-bridge
docker compose logs -f hermes-agent
```

---

### 3. 验证服务

```bash
# 健康检查
curl http://localhost:8646/health   # Hermes Bridge
curl http://localhost:8080/health   # File Upload Service

# 预期响应
# {"status":"healthy","service":"hermes-bridge","hermes_available":true}
# {"status":"healthy","service":"file-upload"}
```

---

## API 使用

### Hermes Bridge API

#### 提交文本任务

```bash
curl -X POST http://localhost:8646/api/submit \
  -H "Content-Type: application/json" \
  -d '{"message": "你好，请介绍一下你自己"}'
```

#### 处理 Excel 文件

```bash
# Step 1: 上传文件
curl -X POST "http://localhost:8080/api/upload?user_id=local_user" \
  -F "file=@test.xlsx"

# 响应示例：
# {"success":true,"file_id":"file_20260515_xxx","filename":"file_20260515_xxx.xlsx",...}

# Step 2: 提交处理任务
curl -X POST http://localhost:8646/api/excel \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "file_20260515_xxx",
    "task": "替换第一行数据为：员工姓名,所属部门,年龄,入职时间,月薪",
    "user_id": "local_user"
  }'

# Step 3: 下载结果
curl "http://localhost:8080/api/download/file_20260515_xxx.xlsx?user_id=local_user" \
  -o result.xlsx
```

#### 检查 Agent 状态

```bash
curl http://localhost:8646/api/status

# 响应示例：
# {"available":true,"container":"hermes-agent"}
```

### File Upload API

#### 文件上传

```bash
curl -X POST "http://localhost:8080/api/upload?user_id=test_user" \
  -F "file=@test.xlsx"
```

#### 文件下载

```bash
curl "http://localhost:8080/api/download/file_20260515_xxx.xlsx?user_id=test_user" \
  -o downloaded.xlsx
```

#### 文件信息

```bash
curl "http://localhost:8080/api/info/file_20260515_xxx.xlsx?user_id=test_user"
```

#### 文件删除

```bash
curl -X DELETE "http://localhost:8080/api/delete/file_20260515_xxx.xlsx?user_id=test_user"
```

---

## Swagger UI

访问 API 文档：

- Hermes Bridge: http://localhost:8646/docs
- File Upload: http://localhost:8080/docs

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

## 全链路测试

```bash
# 本地模式（模拟处理，无需 LLM API Key）
python tests/test_full_chain.py --mode local

# 完整模式（需要 Hermes Agent + LLM API Key）
python tests/test_full_chain.py --mode full
```

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

## 常见问题

### Q: Hermes Agent 状态显示不可用？

```bash
# 检查容器状态
docker ps -a --filter "name=hermes-agent"

# 查看日志
docker logs hermes-agent --tail 50

# 重启服务
docker compose restart hermes-agent
```

### Q: LLM API 调用失败？

```bash
# 检查 API Key 配置
docker exec hermes-agent cat /root/.hermes/config.yaml

# 查看 Agent 日志
docker logs hermes-agent --tail 100 | grep -i error
```

### Q: 端口被占用？

```bash
# 查看端口占用
lsof -i :8646
lsof -i :8080
lsof -i :9000

# 修改 docker-compose.yml 中的端口映射
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

---

## 开发调试

### 本地开发 Hermes Bridge

```bash
cd services/hermes-bridge

# 安装依赖
pip install -r requirements.txt

# 本地运行（需要 Docker 访问 Hermes Agent 容器）
uvicorn app.main:app --reload --port 8646
```

### 查看 Hermes Agent 可用命令

```bash
docker exec hermes-agent /opt/hermes/.venv/bin/hermes --help
```

---

## 相关文档

- [README.md](../README.md) - 项目总览
- [API 文档](http://localhost:8646/docs) - Swagger UI
- [评审报告](./workitems/规划评审分析/) - 双视角评审分析