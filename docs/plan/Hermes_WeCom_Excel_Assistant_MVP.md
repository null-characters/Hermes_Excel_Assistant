# Hermes WeCom Excel Assistant 总体规划

> **制定人**: AI Architecture Team  
> **当前版本**: V3.0  
> **更新日期**: 2026-05-14  
> **仓库**: https://github.com/null-characters/Hermes-WeCom-Assistant

---

## 版本历史

| 版本 | 日期 | 制定人 | 变更说明 |
|------|------|--------|----------|
| V1.0 | 2026-05-14 | AI Team | 初稿：原始 MVP 规划 |
| V2.0 | 2026-05-14 | AI Team | 基于可行性评估优化：架构简化（3→2组件）、H5上传方案 |
| V3.0 | 2026-05-14 | AI Team | 基于双视角评审优化：补充安全设计、运维方案、用户体验优化 |

---

## 1. 项目目标

利用 Hermes Agent 的自主代理能力，为文职人员提供基于企业微信的 Excel 处理助手。用户通过企微 H5 上传文件，在聊天中发送处理指令，系统自动完成数据清洗、汇总或分析，并返回结果文件。

### 1.1 核心价值

| 价值维度 | 说明 | 预期收益 |
|----------|------|----------|
| 效率提升 | 自动化处理替代手工 | 节省 60%+ 时间 | 
| 技能门槛降低 | 自然语言交互 | 人人可用 |
| 错误减少 | Agent 标准化处理 | 减少 80% 人为失误 |

---

## 2. 总体架构

### 2.1 架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              用户交互层                                      │
│   ┌─────────────┐         ┌─────────────────────────────────────────────┐   │
│   │  企业微信    │         │              企微 H5 应用                    │   │
│   │  聊天窗口    │         │           文件上传页面                       │   │
│   │  发送指令    │         │       选择 Excel → 自动跳转聊天              │   │
│   │  接收结果    │         │                                             │   │
│   │  接收进度🔴  │         │                                             │   │
│   └──────────────┘         └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
           │ 文本消息                             │ 文件上传
           ▼                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              服务层                                          │
│   ┌──────────────────────────────────────┐    ┌─────────────────────────┐   │
│   │         Hermes Agent                 │    │   File Upload Service   │   │
│   │                                      │    │                         │   │
│   │  WeCom Callback (内置)               │    │  - 文件接收 API         │   │
│   │  - 接收文本消息                       │    │  - 文件存储 (MinIO)    │   │
│   │  - 发送回复/文件                      │    │  - 用户绑定验证 🔴     │   │
│   │  - 进度通知 🔴                        │    │                         │   │
│   │                                      │    └─────────────────────────┘   │
│   │  Docker Backend (内置沙箱)           │                                   │
│   │  - Python 3.11 + pandas              │                                   │
│   │  - 网络隔离 🔴                        │                                   │
│   │  - 执行超时 300s 🔴                   │                                   │
│   │                                      │                                   │
│   │  Skills & Memory (内置)              │                                   │
│   │  - Excel 处理技能                    │                                   │
│   │  - 进度通知技能 🔴                    │                                   │
│   └──────────────────────────────────────┘                                   │
└─────────────────────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           安全层 🔴 P0                                       │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────┐    │
│   │   HTTPS/TLS 🔴   │    │   文件访问控制🔴 │    │   沙箱网络隔离🔴    │    │
│   │   SSL 证书       │    │   用户ID绑定     │    │   network: disabled │    │
│   └─────────────────┘    └─────────────────┘    └─────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           基础设施层                                         │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────┐    │
│   │   Docker        │    │   MinIO         │    │   Prometheus 🟡    │    │
│   │   Engine        │    │   文件存储       │    │   监控告警         │    │
│   └─────────────────┘    └─────────────────┘    └─────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 组件说明

| 组件 | 技术栈 | 职责 | P0问题 |
|------|--------|------|--------|
| Hermes Agent | Python + Docker | 核心引擎 | 网络隔离、进度通知 |
| File Upload Service | FastAPI + MinIO | 文件服务 | 用户绑定验证 |
| MinIO | MinIO | 文件存储 | - |
| Prometheus | Prometheus | 监控告警 | 🟡 P1 |

---

## 3. 用户交互流程（V3优化）

### 3.1 完整流程

```
Step 1: 上传文件
用户 → 企微菜单 → H5页面 → 选择Excel → 上传
✅ V3优化: 自动跳转聊天，文件ID预填入输入框

Step 2: 发送指令
用户 → 确认预填内容 → 补充描述 → 发送
示例: "@助手 处理 file_20260514_abc123 提取行政部"
🔴 Hermes验证: 解析file_id → 验证user_id归属 → 拒绝非归属文件
✅ V3优化: 提供快捷指令按钮

Step 3: Agent处理（新增进度通知🔴）
Hermes: 解析 → 🔴验证归属 → 下载 → 发送进度 → 执行 → 🔴网络隔离 → 完成 → 发送文件
✅ V3新增: 多阶段进度通知

Step 4: 接收结果
用户 ← 收到Excel文件
✅ V3新增: 结果反馈机制（满意/重试）
```

### 3.2 进度通知机制（🔴P0）

| 阶段 | 通知内容 | 触发时机 |
|------|----------|----------|
| 开始 | "开始处理，预计需要 X 分钟..." | 任务入队 |
| 进行中 | "处理中... 已完成 XX%" | 每30秒或关键节点 |
| 完成 | "处理完成，正在生成结果..." | 代码执行完毕 |
| 发送 | "结果文件已发送，请查收" | 文件发送成功 |

---

## 4. 安全设计（V3新增 🔴P0）

### 4.1 安全配置清单

#### 4.1.1 HTTPS配置 🔴

```yaml
# docker-compose.yml 添加 nginx-proxy
services:
  nginx-proxy:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
```

#### 4.1.2 文件访问控制 🔴

```python
# FileMetadata 绑定用户ID
class FileMetadata:
    file_id: str
    user_id: str  # 🔴 WeCom用户ID绑定
    filename: str
    upload_time: datetime
    expires_at: datetime  # 7天后过期

# 下载验证
async def download_file(file_id, user_id):
    metadata = await get_file_metadata(file_id)
    if metadata.user_id != user_id:  # 🔴 归属验证
        raise HTTPException(403, "无权访问此文件")
```

#### 4.1.3 沙箱安全配置 🔴

```yaml
# docker-compose.yml Hermes环境变量
environment:
  - TERMINAL_NETWORK_DISABLED=true   # 🔴 网络隔离
  - TERMINAL_TIMEOUT=300             # 🔴 执行超时
  - TERMINAL_READ_ONLY_ROOT=true     # 只读根文件系统
  - TERMINAL_MAX_PROCESSES=100       # 进程数限制
```

---

## 5. 运维方案（V3新增 🟡P1）

### 5.1 监控指标

| 指标 | 告警阈值 |
|------|----------|
| 服务健康状态 | down → 立即告警 |
| CPU使用率 | >80% → 警告 |
| Memory使用率 | >80% → 警告 |
| MinIO容量 | >90% → 警告 |
| Agent执行失败率 | >10% → 警告 |

### 5.2 故障恢复

| 故障场景 | 恢复机制 |
|----------|----------|
| Hermes崩溃 | Docker restart |
| MinIO数据丢失 | 定期备份 |
| LLM API不可用 | 多提供商切换 |
| 沙箱执行卡死 | 超时强制终止 |

---

## 6. 项目目录结构

```
Hermes-WeCom-Assistant/
├── docker-compose.yml
├── .env.example
├── README.md
├── config/
│   ├── config.yaml
│   ├── .env
│   └── skills/
│       └── excel_processor.md
├── services/
│   └── file-upload/
│       ├── Dockerfile
│       ├── app/
│       │   ├── main.py
│       │   ├── routers/
│       │   ├── models.py  # 🔴 用户绑定
│       │   └── static/upload.html
│       └── requirements.txt
├── nginx/  # 🔴 V3新增
│   ├── ssl/
│   └── conf.d/
├── data/
│   ├── uploads/
│   └── outputs/
└── docs/
    ├── plan/
    └── workitems/
```

---

## 7. 实施阶段计划

| 阶段 | 时间 | 目标 | 关键交付物 |
|------|------|------|-----------|
| Phase 1 | Day 1-2 | 基础环境+安全配置 | docker-compose.yml, nginx配置 |
| Phase 2 | Day 3-5 | File Upload Service | FastAPI+用户绑定验证🔴 |
| Phase 3 | Day 6-7 | Hermes Skills | 进度通知技能🔴 |
| Phase 4 | Day 8-10 | WeCom集成测试 | 端到端测试 |
| Phase 5 | Day 11-14 | 监控+优化 | Prometheus配置🟡 |

---

## 8. 关键配置

### 8.1 环境变量

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

# Terminal Backend 🔴安全配置
TERMINAL_BACKEND=docker
TERMINAL_DOCKER_IMAGE=python:3.11-slim
TERMINAL_NETWORK_DISABLED=true
TERMINAL_TIMEOUT=300
TERMINAL_CONTAINER_CPU=1
TERMINAL_CONTAINER_MEMORY=2048

# MinIO
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=your-password
MINIO_BUCKET=excel-files
```

### 8.2 Docker Compose

```yaml
version: '3.8'
services:
  nginx-proxy:
    image: nginx:alpine
    ports: ["443:443", "80:80"]
    volumes:
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro

  hermes:
    image: nousresearch/hermes-agent:v0.13.0
    ports: ["8645:8645"]
    volumes:
      - ./config:/root/.hermes
      - ./data:/app/data
      - /var/run/docker.sock:/var/run/docker.sock
    env_file: .env

  file-upload:
    build: ./services/file-upload
    ports: ["8080:8000"]
    volumes: [./data/uploads:/app/uploads]
    env_file: .env
    depends_on: [minio]

  minio:
    image: minio/minio:latest
    ports: ["9000:9000", "9001:9001"]
    volumes: [minio-data:/data]
    environment:
      MINIO_ROOT_USER: ${MINIO_ROOT_USER}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD}
    command: server /data --console-address ":9001"

  prometheus:
    image: prom/prometheus:latest
    ports: ["9090:9090"]
    volumes: [./prometheus:/etc/prometheus]

volumes:
  minio-data:
```

---

## 9. 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 | 状态 |
|------|------|------|----------|------|
| 数据泄露 | 高 | 🔴极高 | 网络隔离(A-01) | ✅ V3已规划 |
| 跨用户访问 | 高 | 🔴极高 | 用户绑定(A-02) | ✅ V3已规划 |
| 传输安全 | 中 | 🔴高 | HTTPS(A-03) | ✅ V3已规划 |
| 用户流失(延迟) | 高 | 🔴高 | 进度通知(A-04) | ✅ V3已规划 |
| 流程割裂 | 高 | 🔴高 | 自动跳转(A-05) | ✅ V3已规划 |
| Hermes版本不稳定 | 中 | 🟡中 | 版本锁定(A-10) | ✅ V3已规划 |
| 运维盲区 | 高 | 🟡中 | Prometheus(A-07) | ✅ V3已规划 |

---

## 10. 后续迭代

| 优先级 | 功能 | 说明 |
|--------|------|------|
| P1 | 指令模板/快捷按钮 | 降低学习成本 |
| P1 | 执行超时机制 | 防止无限循环 |
| P1 | 结果反馈机制 | 满意度/重试 |
| P2 | 处理模板保存 | 提升复用效率 |
| P2 | MinIO数据备份 | 数据安全兜底 |
| P2 | 多LLM提供商 | API容灾 |

---

## 11. 开发启动条件检查

### 11.1 P0必须满足 ✅

| 条件 | V3状态 |
|------|--------|
| 沙箱网络隔离配置 | ✅ 已规划 |
| 文件访问控制机制 | ✅ 已规划 |
| HTTPS配置 | ✅ 已规划 |
| 进度通知机制 | ✅ 已规划 |
| 上传跳转逻辑 | ✅ 已规划 |

**结论**: V3版本已解决所有P0问题，**可启动开发**。

---

## 附录：评审来源

本规划基于以下评审报告优化：
- `docs/workitems/规划评审分析/report_pm.md` - 产品经理视角
- `docs/workitems/规划评审分析/report_engineer.md` - 工程师视角
- `docs/workitems/规划评审分析/report_summary.md` - 交叉汇总