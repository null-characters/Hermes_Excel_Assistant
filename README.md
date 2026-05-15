# Hermes Excel Assistant

> 基于 Hermes Agent 的本地化 Excel 自动化助手

## 项目简介

利用 Hermes Agent 的自主代理能力，为文职人员提供 Excel 处理助手。用户通过本地 API 上传文件，发送自然语言指令，系统自动完成数据清洗、汇总或分析，并返回处理后的结果文件。

**当前方案：本地化部署** — 无需企业微信、无需管理员权限，所有操作在本地完成。

### 核心价值

| 价值维度 | 说明 | 预期收益 |
|----------|------|----------|
| 效率提升 | 自动化处理替代手工 | 节省 60%+ 时间 |
| 技能门槛降低 | 自然语言交互 | 人人可用 |
| 错误减少 | Agent 标准化处理 | 减少 80% 人为失误 |
| 隐私安全 | 本地化部署，数据不出本机 | 零泄露风险 |

---

## 项目状态

### 阶段划分

| 阶段 | 状态 | 说明 |
|------|------|------|
| **Phase 1: PoC 验证** | ✅ 完成 | 技术可行性验证 |
| **Phase 2: 产品化 MVP** | 🚧 进行中 | Web UI + 安全加固 + 用户测试 |

### Phase 1 完成内容

- ✅ Docker/MinIO/Nginx 基础环境
- ✅ FastAPI 文件上传服务
- ✅ Hermes Bridge 本地桥接服务
- ✅ Hermes Agent + 自定义 LLM 集成
- ✅ 本地模式全链路验证通过
- ✅ Prometheus 监控配置

### 路线选择

> **决策日期**: 2026-05-15

| 决策项 | 选择 | 说明 |
|--------|------|------|
| 技术路线 | ✅ 本地化部署 | 无需企微权限，降低验证门槛 |
| 产品化策略 | ✅ 并行推进 | 安全修复 + Web UI 同步开发 |
| Excel 存储 | ✅ 本地文件系统 | 简化架构，放弃 MinIO |
| 沙箱方案 | ✅ local + SQLite 隔离 | 会话级数据隔离，路径白名单 |
| LLM 配置 | ✅ 用户自定义 | 用户自行配置 API Key 和 Provider |

---

## 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                      用户交互层                              │
│   ┌──────────────┐        ┌────────────────────────────┐    │
│   │  REST API    │        │     Swagger UI / curl       │    │
│   │  本地提交任务 │        │      调试与测试界面         │    │
│   └──────────────┘        └────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                        服务层                                │
│   ┌──────────────────┐  ┌─────────────────┐                 │
│   │  Hermes Bridge   │  │ File Upload Svc │                 │
│   │  - 任务接收 API  │  │  - 文件接收 API │                 │
│   │  - Agent 通信    │  │  - MinIO 存储   │                 │
│   │  - 结果返回      │  │  - 用户绑定验证 │                 │
│   └────────┬─────────┘  └─────────────────┘                 │
│            │                                                 │
│            ▼                                                 │
│   ┌──────────────────┐                                      │
│   │  Hermes Agent    │                                      │
│   │  - LLM 推理      │                                      │
│   │  - Docker 沙箱   │                                      │
│   │  - Skills & 内存 │                                      │
│   └──────────────────┘                                      │
└─────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                      基础设施层                              │
│   ┌──────────┐    ┌──────────┐    ┌──────────────────┐      │
│   │  Docker  │    │  MinIO   │    │   Prometheus     │      │
│   │  Engine  │    │  存储    │    │   监控告警       │      │
│   └──────────┘    └──────────┘    └──────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 数据流

```
用户 → curl/API → Hermes Bridge → docker exec → Hermes Agent (chat -q)
                                                      │
                                                      ▼
                                               LLM 推理 + 工具调用
                                                      │
                                                      ▼
用户 ← 结果文件 ← File Upload Service ← MinIO ← 处理后的 Excel
```

---

## 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| Agent 框架 | Hermes Agent | NousResearch/hermes-agent |
| 任务桥接 | Hermes Bridge | FastAPI 本地 REST API |
| 文件服务 | FastAPI + MinIO | 文件上传/存储 |
| 容器化 | Docker Compose | 服务编排 |
| 监控 | Prometheus | 指标采集告警 |

---

## 快速开始

### 前置条件

- Docker & Docker Compose
- LLM API Key（OpenRouter / OpenAI / 自定义兼容端点）

### 1. 克隆项目

```bash
git clone https://github.com/null-characters/Hermes-WeCom-Assistant.git
cd Hermes-WeCom-Assistant
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，只需配置以下两项：
```

必填配置：

```env
# MinIO 存储（自定义密码，8位以上）
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=your-password

# LLM API（三选一）

# 方式 1: OpenRouter
HERMES_PROVIDER=openrouter
HERMES_MODEL=anthropic/claude-3-sonnet
OPENROUTER_API_KEY=sk-or-xxx

# 方式 2: OpenAI 兼容自定义端点
# HERMES_PROVIDER=openai
# OPENAI_API_KEY=your-api-key
# OPENAI_BASE_URL=https://your-custom-url/v1
# HERMES_MODEL=your-model-name

# 方式 3: 其他提供商
# DEEPSEEK_API_KEY / GLM_API_KEY / KIMI_API_KEY 等
```

### 3. 启动服务

```bash
# 启动所有服务
docker compose up -d

# 查看状态
docker compose ps
```

### 4. 验证服务

```bash
# 检查各服务健康状态
curl http://localhost:8646/health   # Hermes Bridge
curl http://localhost:8080/health   # File Upload Service
curl http://localhost:9000/minio/health/live  # MinIO
```

### 5. 提交任务

```bash
# 提交文本任务
curl -X POST http://localhost:8646/api/submit \
  -H "Content-Type: application/json" \
  -d '{"message": "你好，请介绍一下你自己"}'

# 处理 Excel 文件
# Step 1: 上传文件
curl -X POST "http://localhost:8080/api/upload?user_id=local_user" \
  -F "file=@test.xlsx"

# Step 2: 提交处理任务（使用返回的 file_id）
curl -X POST http://localhost:8646/api/excel \
  -H "Content-Type: application/json" \
  -d '{"file_id": "file_xxx", "task": "替换第一行为：员工姓名,所属部门,年龄,入职时间,月薪"}'

# Step 3: 下载结果
curl "http://localhost:8080/api/download/file_xxx.xlsx?user_id=local_user" -o result.xlsx
```

---

## 服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| Hermes Bridge | 8646 | 任务提交 API |
| File Upload | 8080 | 文件上传/下载 API |
| Hermes Agent | 8645 | Agent 服务（内部） |
| MinIO API | 9000 | S3 API |
| MinIO Console | 9001 | Web 管理界面 |
| Prometheus | 9090 | 监控面板 |

---

## 项目结构

```
Hermes-WeCom-Assistant/
├── docker-compose.yml          # 服务编排
├── .env.example                # 环境变量模板
├── README.md                   # 项目说明
├── config/
│   ├── config.yaml             # Hermes 配置
│   ├── USER.md                 # Agent 角色设定
│   └── skills/                 # 技能定义
├── services/
│   ├── file-upload/            # 文件上传服务
│   │   ├── Dockerfile
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── models.py
│   │   │   ├── routers/upload.py
│   │   │   └── services/minio_client.py
│   │   └── requirements.txt
│   └── hermes-bridge/          # 本地桥接服务
│       ├── Dockerfile
│       ├── app/
│       │   ├── main.py
│       │   ├── routers/task.py
│       │   └── services/hermes_client.py
│       └── requirements.txt
├── tests/
│   └── test_full_chain.py      # 全链路测试
├── nginx/                      # 反向代理配置
├── prometheus/                 # 监控配置
└── docs/
    ├── LOCAL_DEV_GUIDE.md      # 本地开发指南
    ├── plan/                   # 规划文档
    └── tasks/                  # 任务清单
```

---

## API 参考

### Hermes Bridge API (`:8646`)

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/submit` | POST | 提交文本任务 |
| `/api/excel` | POST | 处理 Excel 文件 |
| `/api/status` | GET | Agent 状态 |

### File Upload API (`:8080`)

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/upload` | POST | 上传文件 |
| `/api/download/{file_id}` | GET | 下载文件 |
| `/api/info/{file_id}` | GET | 文件信息 |
| `/api/delete/{file_id}` | DELETE | 删除文件 |

---

## 测试

### 全链路测试

```bash
# 本地模式（模拟处理，无需 LLM API Key）
python tests/test_full_chain.py --mode local

# 完整模式（需要 Hermes Agent + LLM API Key）
python tests/test_full_chain.py --mode full
```

### 单元测试

```bash
cd services/file-upload
python -m pytest app/tests/ -v
```

---

## 安全设计

| 安全项 | 措施 |
|--------|------|
| 沙箱隔离 | `TERMINAL_NETWORK_DISABLED=true` |
| 文件访问控制 | user_id 绑定验证 |
| 执行超时 | 300s 强制终止 |
| 容器资源限制 | CPU 1核 / 内存 2GB |
| CORS 限制 | 环境变量配置具体域名 |
| Content-Disposition | RFC 5987 编码防止注入 |

---

## 文档索引

| 文档 | 说明 |
|------|------|
| [本地开发指南](./docs/LOCAL_DEV_GUIDE.md) | 快速启动、API 使用、故障排除 |
| [总体规划](./docs/plan/Hermes_WeCom_Excel_Assistant_MVP.md) | MVP 规划方案 |
| [Phase 1 任务](./docs/tasks/phase1/) | PoC 阶段任务清单 |
| [评审报告](./docs/workitems/规划评审分析/) | 双视角评审分析 |
| [本地化方案评审](./docs/workitems/本地化方案评审分析/本地化方案评审报告_汇总.md) | PoC 验证结论与实施路径 |

---

## 许可证

MIT License

---

## 贡献

欢迎提交 Issue 和 Pull Request。