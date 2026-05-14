# Hermes WeCom Excel Assistant

> 基于 Hermes Agent 的企业微信 Excel 自动化助手

## 项目简介

利用 Hermes Agent 的自主代理能力，为文职人员提供基于企业微信的 Excel 处理助手。用户通过企微 H5 上传文件，在聊天中发送自然语言指令，系统自动完成数据清洗、汇总或分析，并返回处理后的结果文件。

### 核心价值

| 价值维度 | 说明 | 预期收益 |
|----------|------|----------|
| 效率提升 | 自动化处理替代手工 | 节省 60%+ 时间 |
| 技能门槛降低 | 自然语言交互 | 人人可用 |
| 错误减少 | Agent 标准化处理 | 减少 80% 人为失误 |

---

## 项目状态

| 阶段 | 状态 | 说明 |
|------|------|------|
| Phase 1: 基础环境 | ✅ 完成 | Docker/MinIO/Nginx 配置 |
| Phase 2: File Upload Service | ✅ 完成 | FastAPI 文件上传服务 |
| Phase 3: Hermes Skills | ✅ 完成 | 技能定义与配置 |
| Phase 4: WeCom 集成 | ✅ 完成 | 回调配置与测试 |
| Phase 5: 监控运维 | ✅ 完成 | Prometheus 监控配置 |
| 代码审查修复 | ✅ 完成 | 安全问题与规范问题 |
| TDD 单元测试 | ✅ 完成 | 52 个测试用例 |

---

## 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                      用户交互层                              │
│   ┌─────────────┐         ┌─────────────────────────────┐   │
│   │  企业微信    │         │        企微 H5 应用          │   │
│   │  聊天窗口    │         │         文件上传页面         │   │
│   └─────────────┘         └─────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           │                           │
           ▼                           ▼
┌─────────────────────────────────────────────────────────────┐
│                        服务层                                │
│   ┌────────────────────────┐    ┌─────────────────────┐     │
│   │      Hermes Agent      │    │  File Upload Service │    │
│   │  - WeCom Callback      │    │  - 文件接收 API      │    │
│   │  - Docker Backend      │    │  - MinIO 存储        │    │
│   │  - Skills & Memory     │    │  - 用户绑定验证      │    │
│   └────────────────────────┘    └─────────────────────┘     │
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

---

## 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| Agent 框架 | Hermes Agent | NousResearch/hermes-agent |
| 消息通道 | 企业微信 API | WeCom Callback |
| 文件服务 | FastAPI + MinIO | 文件上传/存储 |
| 容器化 | Docker Compose | 服务编排 |
| 监控 | Prometheus | 指标采集告警 |

---

## 快速开始

### 前置条件

- Docker & Docker Compose
- LLM API Key（OpenRouter / Anthropic / OpenAI）
- 企业微信管理员权限（正式部署时需要）

### 开发路径

根据你的情况选择合适的启动方式：

#### 路径 A：本地开发（推荐入门）

**无需企业微信管理员权限，只测试核心功能**

```bash
# 1. 配置最小环境变量
cp .env.example .env
# 只需配置：
# - MINIO_ROOT_PASSWORD（自定义密码）
# - OPENROUTER_API_KEY（LLM API）

# 2. 启动核心服务（跳过企微回调）
docker compose up minio file-upload nginx -d

# 3. 测试文件上传
curl -X POST http://localhost:8080/api/upload \
  -H "X-User-ID: test_user" \
  -F "file=@test.xlsx"

# 4. 运行单元测试
cd services/file-upload
python -m pytest app/tests/ -v
```

**适用场景**：开发调试、功能验证、学习研究

---

#### 路径 B：测试企业（完整测试）

**自己创建测试企业，获得完整管理员权限**

```
🔗 注册地址：
https://work.weixin.qq.com/wework_admin/register_wework?from=test_wework

步骤：
1. 微信扫码创建测试企业
2. 自动成为超级管理员
3. 创建自建应用、配置回调
4. 完整测试企微集成
```

**适用场景**：企微集成测试、演示验证

---

#### 路径 C：正式部署

**申请正式企业管理员权限或请管理员协助**

```bash
# 1. 配置完整环境变量
cp .env.example .env
# 填入企业管理员提供的配置

# 2. 启动所有服务
docker compose up -d

# 3. 配置企业微信回调 URL
https://your-domain.com/wecom/callback
```

**适用场景**：生产环境部署

---

### 1. 克隆项目

```bash
git clone https://github.com/null-characters/Hermes-WeCom-Assistant.git
cd Hermes-WeCom-Assistant
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入实际配置
```

必填配置：

```bash
# 企业微信
WECOM_CALLBACK_CORP_ID=your-corp-id
WECOM_CALLBACK_AGENT_ID=1000002
WECOM_CALLBACK_TOKEN=your-token
WECOM_CALLBACK_ENCODING_AES_KEY=your-43-char-key

# LLM API
HERMES_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-xxx

# MinIO
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=your-password

# CORS（生产环境必须配置具体域名）
CORS_ORIGINS=https://your-domain.com
```

### 3. 启动服务

```bash
docker compose up -d
```

### 4. 配置企业微信回调

在企业微信管理后台配置回调 URL：

```
https://your-domain.com/wecom/callback
```

### 5. 验证服务

```bash
# 检查服务状态
docker compose ps

# 查看日志
docker compose logs -f hermes

# 运行单元测试
cd services/file-upload
python -m pytest app/tests/ -v
```

---

## 项目结构

```
Hermes-WeCom-Assistant/
├── docker-compose.yml          # 服务编排
├── .env.example                # 环境变量模板
├── README.md                   # 项目说明
├── config/
│   ├── config.yaml             # Hermes 配置
│   └── skills/                 # 技能定义
│       ├── excel_processor.md
│       └── progress_notifier.md
├── services/
│   └── file-upload/            # 文件上传服务
│       ├── Dockerfile
│       ├── app/
│       │   ├── main.py         # FastAPI 应用入口
│       │   ├── models.py       # 数据模型
│       │   ├── routers/
│       │   │   └── upload.py   # API 路由
│       │   ├── services/
│       │   │   └── minio_client.py  # MinIO 客户端
│       │   ├── tests/          # 单元测试
│       │   │   ├── test_models.py
│       │   │   ├── test_minio_client.py
│       │   │   └── test_upload.py
│       │   └── static/
│       └── requirements.txt
├── nginx/                      # HTTPS 配置
│   ├── ssl/
│   └── conf.d/
├── data/                       # 数据目录
│   ├── uploads/
│   └── outputs/
└── docs/
    ├── plan/                   # 规划文档
    ├── tasks/                  # 任务清单
    └── workitems/              # 工作流记录
```

---

## 使用方式

### Step 1: 上传文件

在企业微信应用菜单中点击上传，选择 Excel 文件。

### Step 2: 发送指令

在企微聊天窗口发送处理指令：

```
@助手 处理 file_20260514_abc123 提取行政部人员
```

### Step 3: 接收结果

系统自动处理并返回结果文件，同时发送进度通知。

---

## 测试

### 单元测试

```bash
cd services/file-upload
python -m pytest app/tests/ -v
```

### 测试覆盖

| 测试文件 | 测试数量 | 覆盖模块 |
|----------|----------|----------|
| test_models.py | 17 | 数据模型 |
| test_minio_client.py | 13 | MinIO 客户端 |
| test_upload.py | 22 | API 路由 |
| **总计** | **52** | 全部通过 |

---

## 安全设计

| 安全项 | 措施 |
|--------|------|
| 沙箱隔离 | `TERMINAL_NETWORK_DISABLED=true` |
| 文件访问控制 | user_id 绑定验证 |
| 传输加密 | HTTPS 强制 |
| 执行超时 | 300s 强制终止 |
| CORS 限制 | 环境变量配置具体域名 |
| Content-Disposition | RFC 5987 编码防止注入 |
| 参数验证 | 非空检查防止异常 |

---

## 文档索引

| 文档 | 说明 |
|------|------|
| [总体规划 V3](./docs/plan/Hermes_WeCom_Excel_Assistant_MVP.md) | 完整规划 |
| [总体规划 V4](./docs/plan/Hermes_WeCom_Excel_Assistant_MVP_v2.md) | 最新版本 |
| [任务清单](./docs/tasks/) | 5 个阶段任务拆解 |
| [评审报告](./docs/workitems/规划评审分析/) | 双视角评审分析 |

---

## 许可证

MIT License

---

## 贡献

欢迎提交 Issue 和 Pull Request。
