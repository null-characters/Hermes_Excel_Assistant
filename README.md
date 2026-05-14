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
- 企业微信管理员权限（创建自建应用）
- LLM API Key（OpenRouter / Anthropic / OpenAI）

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
│       │   ├── main.py
│       │   ├── models.py
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

## 开发计划

| 阶段 | 时间 | 目标 |
|------|------|------|
| Phase 1 | Day 1-2 | 基础环境 + 安全配置 |
| Phase 2 | Day 3-5 | File Upload Service |
| Phase 3 | Day 6-7 | Hermes Skills 配置 |
| Phase 4 | Day 8-10 | 企业微信集成测试 |
| Phase 5 | Day 11-14 | 监控 + 优化 |

详细任务清单见 [docs/tasks/](./docs/tasks/)

---

## 安全设计

| 安全项 | 措施 |
|--------|------|
| 沙箱隔离 | `TERMINAL_NETWORK_DISABLED=true` |
| 文件访问控制 | user_id 绑定验证 |
| 传输加密 | HTTPS 强制 |
| 执行超时 | 300s 强制终止 |

---

## 文档索引

| 文档 | 说明 |
|------|------|
| [总体规划](./docs/plan/Hermes_WeCom_Excel_Assistant_MVP.md) | V3 版本完整规划 |
| [任务清单](./docs/tasks/) | 5 个阶段任务拆解 |
| [评审报告](./docs/workitems/规划评审分析/) | 双视角评审分析 |

---

## 许可证

MIT License

---

## 贡献

欢迎提交 Issue 和 Pull Request。
