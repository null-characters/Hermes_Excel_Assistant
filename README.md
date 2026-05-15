# Hermes Excel Assistant

> 基于 Hermes Agent 的本地化 Excel 自动化助手

## 项目简介

利用 Hermes Agent 的自主代理能力，为文职人员提供 Excel 处理助手。用户通过 **Web UI** 或 API 上传文件，发送自然语言指令，系统自动完成数据清洗、汇总或分析，并返回处理后的结果文件。

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
| **Phase 2: 产品化 MVP** | ✅ 完成 | Web UI + 安全加固 + 本地存储 |
| **Phase 3: 功能增强** | 🔄 进行中 | 批量处理 + 模板系统 |

### Phase 2 完成内容

- ✅ **安全止血**: Agent 容器移除 Docker Socket，Prompt 参数转义
- ✅ **会话隔离**: 每会话独立目录 + SQLite 数据库
- ✅ **路径白名单**: `validate_path()` 防止目录穿越
- ✅ **命令黑名单**: `validate_prompt()` 拦截危险命令
- ✅ **本地文件存储**: 移除 MinIO，改用本地文件系统
- ✅ **Web UI**: Streamlit 前端，非技术用户可用
- ✅ **思考过程实时显示**: Agent 推理过程可视化
- ✅ **E2E 测试**: Playwright 自动化流程测试

### 路线选择

> **决策日期**: 2026-05-15

| 决策项 | 选择 | 说明 |
|--------|------|------|
| 技术路线 | ✅ 本地化部署 | 无需企微权限，降低验证门槛 |
| Excel 存储 | ✅ 本地文件系统 | 简化架构，放弃 MinIO |
| 沙箱方案 | ✅ local + SQLite 隔离 | 会话级数据隔离，路径白名单 |
| LLM 配置 | ✅ 用户自定义 | 用户自行配置 API Key 和 Provider |
| 用户界面 | ✅ Streamlit Web UI | 非技术用户友好 |

---

## 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                      用户交互层                              │
│   ┌──────────────┐        ┌────────────────────────────┐    │
│   │  Streamlit   │        │     REST API / Swagger     │    │
│   │   Web UI     │        │      调试与测试界面         │    │
│   │  (port 8501) │        │                            │    │
│   └──────────────┘        └────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                        服务层                                │
│   ┌──────────────────┐  ┌─────────────────┐                 │
│   │  Hermes Bridge   │  │ Session Manager │                 │
│   │  - 任务接收 API  │  │  - 会话创建/删除│                 │
│   │  - Agent 通信    │  │  - 路径白名单   │                 │
│   │  - 结果返回      │  │  - 命令黑名单   │                 │
│   └────────┬─────────┘  └─────────────────┘                 │
│            │                                                 │
│            ▼                                                 │
│   ┌──────────────────┐                                      │
│   │  Hermes Agent    │                                      │
│   │  - LLM 推理      │                                      │
│   │  - local 终端    │                                      │
│   │  - Skills & 内存 │                                      │
│   └──────────────────┘                                      │
└─────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                      基础设施层                              │
│   ┌──────────┐    ┌──────────────────┐    ┌──────────────┐   │
│   │  Docker  │    │  本地文件系统     │    │  Prometheus  │   │
│   │  Engine  │    │  data/sessions/  │    │   监控告警   │   │
│   └──────────┘    └──────────────────┘    └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 数据流

```
用户 → Web UI (8501) → Hermes Bridge (8646) → docker exec → Hermes Agent
                                                          │
                                                          ▼
                                                   LLM 推理 + 工具调用
                                                          │
                                                          ▼
用户 ← 结果文件 ← 本地文件系统 ← data/sessions/{session_id}/outputs/
```

### 会话隔离架构

```
data/sessions/
├── sess_abc123/              # 会话目录
│   ├── workspace.db          # SQLite 数据库
│   ├── uploads/              # 上传文件
│   │   └── input.xlsx
│   └── outputs/              # 输出文件
│       └── result.xlsx
└── sess_def456/
    ├── workspace.db
    ├── uploads/
    └── outputs/
```

---

## 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| Agent 框架 | Hermes Agent | NousResearch/hermes-agent |
| 任务桥接 | Hermes Bridge | FastAPI 本地 REST API |
| Web UI | Streamlit | Python 前端框架 |
| 会话管理 | Session Manager | 会话隔离 + 安全验证 |
| 文件存储 | 本地文件系统 | data/sessions/ 目录 |
| 容器化 | Docker Compose | 服务编排 |
| 监控 | Prometheus | 指标采集告警 |

---

## 快速开始

### 前置条件

- Docker & Docker Compose
- LLM API Key（OpenRouter / OpenAI / 自定义兼容端点）

### 1. 克隆项目

```bash
git clone https://github.com/null-characters/Hermes-Excel-Assistant.git
cd Hermes-Excel-Assistant
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，配置 LLM API
```

必填配置：

```env
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

### 4. 访问 Web UI

打开浏览器访问: **http://localhost:8501**

### 5. 使用 Web UI 处理 Excel

1. 上传 Excel 文件 (.xlsx/.xls)
2. 输入自然语言指令（如：将第一列数据按升序排序）
3. 点击"执行"按钮
4. 等待处理完成
5. 下载结果文件

### 6. API 方式（可选）

```bash
# 健康检查
curl http://localhost:8646/health

# 提交文本任务
curl -X POST http://localhost:8646/api/task/submit \
  -H "Content-Type: application/json" \
  -d '{"message": "你好，请介绍一下你自己"}'

# 处理 Excel 文件（流式响应，实时显示思考过程）
curl -N -X POST http://localhost:8646/api/excel/stream \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/app/data/sessions/sess_xxx/uploads/input.xlsx",
    "task": "将第一列数据按升序排序",
    "session_id": "sess_xxx"
  }'

# 非流式 API（等待完成后返回结果）
curl -X POST http://localhost:8646/api/task/excel \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/app/data/sessions/sess_xxx/uploads/input.xlsx",
    "task": "将第一列数据按升序排序",
    "session_id": "sess_xxx"
  }'
```

### 流式 API 事件类型

| 事件类型 | 说明 | 示例 |
|----------|------|------|
| `thinking` | Agent 思考过程 | `💭 让我先检查一下这个Excel文件...` |
| `tool` | 工具准备/执行 | `🔧 准备工具: terminal` |
| `tool_result` | 工具执行结果 | `✅ 工具 1 完成 (0.46s)` |
| `api_call` | API 调用信息 | `🌐 API 调用 #1: glm-5` |
| `response` | Agent 响应内容 | `🤖 已完成排序...` |
| `done` | 任务完成 | `🎉 任务完成` |

---

## 服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| **Web UI** | **8501** | Streamlit 前端界面（推荐） |
| Hermes Bridge | 8646 | 任务提交 API |
| Hermes Agent | 8645 | Agent 服务（内部） |
| Prometheus | 9090 | 监控面板 |

---

## 项目结构

```
Hermes-Excel-Assistant/
├── docker-compose.yml          # 服务编排
├── .env.example                # 环境变量模板
├── README.md                   # 项目说明
├── config/
│   ├── hermes-config.yaml      # Hermes 配置
│   ├── USER.md                 # Agent 角色设定
│   └── skills/                 # 技能定义
├── services/
│   ├── web-ui/                 # Streamlit Web UI (Phase 2)
│   │   ├── Dockerfile
│   │   ├── app.py              # 主入口
│   │   ├── components/
│   │   │   ├── task_runner.py  # 任务执行
│   │   │   └── downloader.py   # 文件下载
│   │   ├── pages/
│   │   │   ├── config.py       # LLM 配置
│   │   │   └── history.py      # 历史记录
│   │   └── requirements.txt
│   ├── hermes-bridge/          # 本地桥接服务
│   │   ├── Dockerfile
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── routers/task.py
│   │   │   └── services/hermes_client.py
│   │   └── requirements.txt
│   └── session_manager/       # 会话管理模块 (Phase 2)
│       ├── manager.py          # 会话创建/删除
│       ├── validators.py       # 路径/命令验证
│       ├── storage.py          # 文件存储
│       └── schema.sql          # SQLite Schema
├── tests/
│   ├── e2e/                    # E2E 测试
│   │   └── test_web_ui.py      # Playwright 测试
│   ├── session_manager/        # 会话管理测试
│   │   └── test_validators.py
│   └── test_storage_chain.py   # 存储链路测试
├── data/
│   └── sessions/               # 会话数据目录
│       └── sess_xxx/
│           ├── workspace.db
│           ├── uploads/
│           └── outputs/
├── nginx/                      # 反向代理配置
├── prometheus/                 # 监控配置
└── docs/
    ├── LOCAL_DEV_GUIDE.md      # 本地开发指南
    ├── design/                 # 设计文档
    ├── plan/                   # 规划文档
    └── tasks/                  # 任务清单
```

---

## API 参考

### Hermes Bridge API (`:8646`)

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/task/submit` | POST | 提交文本任务 |
| `/api/task/excel` | POST | 处理 Excel 文件 |
| `/api/task/status` | GET | Agent 状态 |

### Excel 处理 API 请求格式

```json
{
  "file_path": "/app/data/sessions/{session_id}/uploads/{filename}",
  "task": "自然语言处理指令",
  "session_id": "sess_xxx",
  "output_dir": "/app/data/sessions/{session_id}/outputs"
}
```

### 流式响应格式

```json
{"type": "thinking", "content": "💭 让我分析一下这个文件..."}
{"type": "tool", "content": "🔧 准备工具: terminal"}
{"type": "api_call", "content": "🌐 API 调用 #1: glm-5"}
{"type": "tool_result", "content": "✅ 工具 1 完成 (0.46s)"}
{"type": "response", "content": "🤖 已完成处理..."}
{"type": "done", "content": "🎉 任务完成", "output_file": "result.xlsx"}
```

---

## 测试

### E2E 测试

```bash
# 安装 Playwright
pip install playwright pytest-playwright
playwright install chromium

# 运行 E2E 测试
python tests/e2e/test_web_ui.py
```

### 单元测试

```bash
# 会话管理测试
python -m pytest tests/session_manager/ -v

# 存储链路测试
python tests/test_storage_chain.py
```

---

## 安全设计

### 已实现安全措施

| 安全项 | 措施 | 状态 |
|--------|------|------|
| Docker 权限隔离 | Agent 容器移除 Docker Socket | ✅ |
| 命令注入防护 | `shlex.quote()` 转义 Prompt | ✅ |
| 路径穿越防护 | `validate_path()` 白名单校验 | ✅ |
| 危险命令拦截 | `validate_prompt()` 黑名单 | ✅ |
| 会话数据隔离 | 独立目录 + SQLite 数据库 | ✅ |
| 执行超时 | 300s 强制终止 | ✅ |
| 容器资源限制 | CPU 1核 / 内存 2GB | ✅ |

### 安全警告

> ⚠️ **当前版本为 MVP 阶段，生产环境需额外加固**

| 限制项 | 说明 | 风险等级 |
|--------|------|----------|
| local 终端无沙箱 | Agent 执行的代码无进程隔离 | 🟡 Medium |
| 无认证机制 | API 无身份验证 | 🟡 Medium |

### 生产部署前建议

- [ ] 实现 Docker 终端后端或 gVisor 沙箱
- [ ] 添加 API 认证机制
- [ ] 添加 HTTPS 支持

---

## 文档索引

| 文档 | 说明 |
|------|------|
| [本地开发指南](./docs/LOCAL_DEV_GUIDE.md) | 快速启动、API 使用、故障排除 |
| [会话隔离设计](./docs/design/session-isolation.md) | 架构设计文档 |
| [总体规划](./docs/plan/Hermes_WeCom_Excel_Assistant_MVP.md) | MVP 规划方案 |
| [Phase 1 任务](./docs/tasks/phase1/) | PoC 阶段任务清单 |
| [Phase 2 任务](./docs/tasks/phase2/) | 产品化阶段任务清单 |
| [评审报告](./docs/workitems/规划评审分析/) | 双视角评审分析 |

---

## 许可证

MIT License

---

## 贡献

欢迎提交 Issue 和 Pull Request。
