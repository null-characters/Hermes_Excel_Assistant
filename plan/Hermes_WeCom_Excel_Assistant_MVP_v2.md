# Hermes WeCom Excel Assistant (MVP) - 优化版

> **版本**: v2.0 (基于可行性评估优化)  
> **更新日期**: 2026-05-14  
> **仓库**: https://github.com/null-characters/Hermes-WeCom-Assistant

---

## 1. 项目目标

利用 Hermes Agent 的自主代理能力，为文职人员提供一个基于企业微信的 Excel 处理助手。用户通过企微 H5 上传文件，在聊天中发送处理指令，系统自动完成数据清洗、汇总或分析，并返回处理后的结果文件。

### 1.1 核心变更（相比原规划）

| 变更项 | 原规划 | 优化后 | 原因 |
|--------|--------|--------|------|
| **架构** | 3 组件 | 2 组件（Hermes + Upload Service） | Hermes 内置 WeCom Callback 和 Docker 后端 |
| **文件输入** | 企微聊天直接发送 | H5 上传页面 | WeCom Callback 不支持文件输入 |
| **WeCom 集成** | 自建 Bridge | 使用 Hermes 内置 | 减少开发量 |

---

## 2. 总体架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              用户交互层                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│   ┌─────────────┐         ┌─────────────────────────────────────────────┐   │
│   │  企业微信    │         │              企微 H5 应用                    │   │
│   │  聊天窗口    │         │           文件上传页面                       │   │
│   │  发送指令    │         │       选择本地 Excel → 获得文件 ID          │   │
│   │  接收结果    │         │                                             │   │
│   └──────┬──────┘         └───────────────────┬─────────────────────────┘   │
└──────────┼────────────────────────────────────┼─────────────────────────────┘
           │ 文本消息                           │ 文件上传
           ▼                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              服务层                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│   ┌──────────────────────────────────────┐    ┌─────────────────────────┐   │
│   │         Hermes Agent                 │    │   File Upload Service   │   │
│   │         (All-in-One)                 │    │   (FastAPI + MinIO)     │   │
│   │                                      │    │                         │   │
│   │  ┌────────────────────────────────┐  │    │  - 文件接收 API         │   │
│   │  │  WeCom Callback (内置)          │  │    │  - 文件存储 (MinIO)    │   │
│   │  │  - 接收文本消息                 │  │    │  - 文件 ID 生成        │   │
│   │  │  - 发送回复/文件                │  │    │  - 文件下载 API        │   │
│   │  └────────────────────────────────┘  │    │                         │   │
│   │                                      │    └───────────┬─────────────┘   │
│   │  ┌────────────────────────────────┐  │                │                 │
│   │  │  Docker Backend (内置沙箱)      │◄─┼────────────────┘                 │
│   │  │  - Python 3.11 + pandas        │  │    读取文件                       │
│   │  │  - 资源限制 (CPU/Memory)        │  │                                  │
│   │  └────────────────────────────────┘  │                                   │
│   │                                      │                                   │
│   │  ┌────────────────────────────────┐  │                                   │
│   │  │  Skills & Memory (内置)         │  │                                   │
│   │  └────────────────────────────────┘  │                                   │
│   └──────────────────────────────────────┘                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. 用户交互流程

```
Step 1: 上传文件
用户 → 企微应用菜单 → "上传文件" → H5 页面 → 选择 Excel → 上传
返回: "文件上传成功！文件ID: file_20260514_abc123"

Step 2: 发送处理指令
用户 → 企微聊天 → "@助手 处理 file_20260514_abc123 提取行政部人员"

Step 3: Agent 处理
Hermes: 解析指令 → 下载文件 → 执行代码 → 生成结果 → 发送文件

Step 4: 接收结果
用户 ← 企微聊天 ← 收到处理后的 Excel 文件
```

### 3.1 指令格式

```
格式: @助手 <动作> <文件ID> [参数...]

示例:
- @助手 处理 file_20260514_abc123 提取行政部人员
- @助手 分析 file_20260514_xyz789 统计各部门人数
- @助手 清洗 file_20260514_def456 删除空行并格式化日期
```

---

## 4. 项目目录结构

```
Hermes-WeCom-Assistant/
├── docker-compose.yml          # Docker Compose 配置
├── .env.example                # 环境变量模板
├── README.md
│
├── config/                     # Hermes 配置
│   ├── config.yaml
│   ├── .env
│   └── skills/
│       └── excel_processor.md
│
├── services/                   # 自定义服务
│   └── file-upload/
│       ├── Dockerfile
│       ├── app/
│       │   ├── main.py
│       │   ├── routers/
│       │   └── static/upload.html
│       └── requirements.txt
│
├── data/                       # 数据目录
│   ├── uploads/
│   └── outputs/
│
└── plan/                       # 规划文档
```

---

## 5. 实施阶段计划

| 阶段 | 时间 | 目标 | 关键交付物 |
|------|------|------|-----------|
| **Phase 1** | Day 1-2 | 基础环境搭建 | docker-compose.yml, .env.example |
| **Phase 2** | Day 3-5 | File Upload Service | FastAPI 应用, H5 上传页面 |
| **Phase 3** | Day 6-7 | Hermes Skills 配置 | excel_processor.md, USER.md |
| **Phase 4** | Day 8-10 | WeCom 集成测试 | 端到端测试通过 |
| **Phase 5** | Day 11-14 | 优化与文档 | 用户手册, 部署文档 |

---

## 6. 关键配置

### 6.1 环境变量 (`.env.example`)

```bash
# WeCom Callback
WECOM_CALLBACK_CORP_ID=your-corp-id
WECOM_CALLBACK_CORP_SECRET=your-corp-secret
WECOM_CALLBACK_AGENT_ID=1000002
WECOM_CALLBACK_TOKEN=your-token
WECOM_CALLBACK_ENCODING_AES_KEY=your-43-char-key
WECOM_CALLBACK_ALLOWED_USERS=user1,user2

# Hermes LLM
HERMES_PROVIDER=openrouter
HERMES_MODEL=anthropic/claude-3-sonnet
OPENROUTER_API_KEY=sk-or-xxx

# Terminal Backend
TERMINAL_BACKEND=docker
TERMINAL_DOCKER_IMAGE=python:3.11-slim
TERMINAL_CONTAINER_CPU=1
TERMINAL_CONTAINER_MEMORY=2048

# MinIO
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=your-password
MINIO_BUCKET=excel-files
```

### 6.2 Docker Compose

```yaml
version: '3.8'
services:
  hermes:
    image: nousresearch/hermes-agent:latest
    ports:
      - "8645:8645"
    volumes:
      - ./config:/root/.hermes
      - ./data:/app/data
      - /var/run/docker.sock:/var/run/docker.sock
    env_file: .env
    depends_on: [minio, file-upload]

  file-upload:
    build: ./services/file-upload
    ports:
      - "8080:8000"
    volumes:
      - ./data/uploads:/app/uploads
    env_file: .env
    depends_on: [minio]

  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio-data:/data
    environment:
      MINIO_ROOT_USER: ${MINIO_ROOT_USER}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD}
    command: server /data --console-address ":9001"

volumes:
  minio-data:
```

---

## 7. 风险与缓解

| 风险 | 缓解措施 |
|------|----------|
| WeCom 文件输入不支持 | ✅ 已采用 H5 上传方案 |
| 代码执行安全 | Docker 隔离 + 资源限制 |
| 响应延迟 (3-30min) | 设置用户预期，支持后台任务 |
| Token 过期 | Hermes 内置自动刷新 |

---

## 8. 后续迭代

- **短期**: 批量处理、处理模板、历史查询
- **中期**: 等待 Hermes 原生文件输入支持、更多格式
- **长期**: 图表生成、数据分析报告
