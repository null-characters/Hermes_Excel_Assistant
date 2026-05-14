# Hermes WeCom Excel Assistant (MVP)

> 这是一份为你量身定制的 "基于 Hermes Agent 的企业微信 Excel 自动化助手" 总体规划文档。你可以直接将这份文档提供给你的 AI Coding 工具（如 Cursor、Windsurf 或 VS Code Copilot），它将指导 AI 帮你写出具体的实现代码。

## 1. 项目目标

利用 hermes-agent 的自主代理能力，为文职人员提供一个基于企业微信的 Excel 处理助手。用户只需在企微中发送文件和指令，系统自动完成数据清洗、汇总或分析，并返回处理后的结果文件。

## 2. 总体架构

系统采用 Docker 化部署，包含三个核心组件：

| 组件 | 职责 |
|------|------|
| **WeCom Bridge (中转网桥)** | 负责接收企微回调、下载文件、转换指令并回传结果。 |
| **Hermes Agent (核心引擎)** | 负责任务规划、生成 Python 代码。 |
| **Python Sandbox (执行环境)** | 隔离运行生成的代码，预装 pandas, openpyxl。 |

## 3. 技术栈

- **语言**：Python 3.10+ (FastAPI)
- **代理框架**：NousResearch/hermes-agent
- **消息协议**：企业微信自建应用 API (接收消息服务器配置)
- **容器化**：Docker & Docker Compose
- **数据处理**：Pandas, Openpyxl

## 4. 实施阶段计划（AI Coding 引导）

### 第一阶段：Docker 基础环境搭建

**目标**：配置 docker-compose.yml 和 Hermes 运行环境。

**AI Prompt 建议**：
```
请帮我编写一个 docker-compose.yml 文件。需要包含两个服务：

1. hermes-agent: 使用 nousresearch/hermes-agent 镜像，挂载 ./config 和 ./data 卷。
2. wecom-bridge: 一个自定义的 Python FastAPI 应用。

两个服务共享一个名为 agent_data 的 volume 用于存放 Excel 文件。
```

---

### 第二阶段：WeCom Bridge 开发

**目标**：实现企业微信 API 的对接（解密、接收文件、上传文件）。

**核心功能**：
- **功能 A**：接收企微发送的 file 类型消息。
- **功能 B**：通过 media_id 下载文件至共享目录。
- **功能 C**：调用 Hermes Agent 的 Local API（或直接通过 CLI 触发）。

**AI Prompt 建议**：
```
我需要一个 FastAPI 应用作为企业微信的网桥。

1. 实现 GET 接口用于企微回调验证。
2. 实现 POST 接口解析企微发送的 XML 消息，如果是文件，则下载它。
3. 下载完成后，调用 http://hermes-agent:8000/v1/chat 发送指令。
```

---

### 第三阶段：Hermes 技能（Skills）与约束（Memory）

**目标**：针对 Excel 处理优化 Agent 的行为。

**配置要点**：
- **USER.md 配置**：设定公司财务/行政的 Excel 规范。
- **Excel Skill**：编写一个基础的 Python 模板，确保 Agent 知道优先使用 pandas。

**AI Prompt 建议**：
```
请为 hermes-agent 编写一个 USER.md 配置文件。要求：

1. 设定 Agent 角色为'高级行政财务助理'。
2. 规定处理 Excel 时，日期必须符合 YYYY-MM-DD，数值保留两位小数。
3. 始终在 ./data 目录下生成输出文件，并以 '_processed' 为后缀。
```

---

### 第四阶段：闭环测试

**目标**：文职人员发送"提取行政部人员"，系统返回新文件。

---

## 5. 关键配置清单 (config.toml)

你需要确保 AI 生成的配置包含以下关键项：

```toml
[agent]
name = "ExcelAssistant"
autonomous_mode = true  # 允许自动运行代码

[tools]
enable_python_execution = true
# 必须预装的库
python_packages = ["pandas", "openpyxl", "matplotlib"]

[storage]
# 共享数据目录，用于 Bridge 和 Agent 交换文件
workdir = "/app/data"
```

## 6. 风险与注意事项

| 风险项 | 说明 | 解决方案 |
|--------|------|----------|
| **企微内网穿透** | 如果你的服务器在内网，需将 Bridge 的端口暴露给企微后端。 | 使用 cpolar 或 frp 进行内网穿透。 |
| **文件安全** | 由于 Agent 具有代码执行权限，需防止死循环等问题。 | 在 docker-compose 中限制容器的 CPU 和内存资源。 |
| **Token 过期** | 企业微信的 AccessToken 会定期过期。 | WeCom Bridge 需实现 AccessToken 的自动刷新机制。 |

---

## 附录：架构示意图

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   企业微信       │────▶│   WeCom Bridge  │────▶│  Hermes Agent   │
│   (用户端)       │◀────│   (中转网桥)     │◀────│   (核心引擎)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                       │
                               ▼                       ▼
                        ┌─────────────────────────────────┐
                        │      Python Sandbox             │
                        │   (Pandas, Openpyxl, etc.)      │
                        └─────────────────────────────────┘
```