# Phase 3 规划：本地化增强（V2.0）

## 版本历史
| 版本 | 日期 | 变更说明 |
|------|------|----------|
| V1.0 | 2026-05-15 | 初稿，基于实现评审分析 |
| V2.0 | 2026-05-16 | 重新规划，基于 Phase 2 实际代码状态 |

---

## 一、背景与目标

### 1.1 背景

Phase 2 本地化方案已完成，当前实现状态：

**已完成功能**：
| 功能 | 状态 | 说明 |
|------|------|------|
| SSE 流式执行 | ✅ | 实时显示 Agent 思考过程、工具调用、API 信息 |
| 文件上传/下载 | ✅ | 本地文件系统存储，支持多格式 |
| 会话管理 | ✅ | SQLite + 目录结构，SessionManager 模块 |
| 安全校验 | ✅ | 路径白名单 + 命令黑名单（validators.py） |
| Web UI | ✅ | Streamlit 前端，移除 API Key 配置（从 .env 读取） |
| 进度反馈 | ✅ | 四步骤指示器 + 实时日志（原 B-04 已解决） |
| 错误提示 | ✅ | 分类显示（thinking/tool/error/done）（原 B-05 已解决） |

**待解决问题**：
| 编号 | 问题 | 优先级 | 当前状态 |
|------|------|--------|----------|
| **B-01** | Bridge Docker exec 权限未限制 | P0 | hermes_client.py 未限制容器名 |
| B-06 | CORS 硬编码 `allow_origins=["*"]` | P1 | main.py 中硬编码 |
| B-07 | 无文件大小限制 | P1 | 未实现 |
| B-02 | 架构文档过时 | P1 | 未反映本地化架构 |
| B-03 | Bridge 缺少单元测试 | P1 | 无测试文件 |

### 1.2 目标

**坚持本地化路线**，Phase 3 聚焦：
1. **安全修复**：解决 B-01（Bridge Docker exec 容器白名单）
2. **配置优化**：解决 B-06（CORS 环境变量）、B-07（文件大小限制）
3. **功能增强**：批量处理、处理模板、结果预览等本地化功能
4. **质量提升**：补充测试、更新文档

### 1.3 范围边界

| 包含 | 不包含 |
|------|--------|
| B-01 安全修复（容器白名单） | 企业微信集成 |
| B-06 CORS 环境变量配置 | 云端部署 |
| B-07 文件大小限制 | 多用户认证 |
| 批量文件处理 | 异步任务队列（P2 延后） |
| 处理模板保存/加载 | |
| 结果预览（表格渲染） | |

---

## 二、当前基线（Phase 2 实际状态）

### 2.1 服务架构

```
Phase 2 本地化架构（当前）
│
├── Gateway: nginx-proxy (HTTPS 终止)
│
├── Services:
│   ├── hermes-bridge (8646)
│   │   ├── main.py: FastAPI 入口 + CORS
│   │   ├── routers/task.py: 任务 API（同步/SSE）
│   │   └── services/hermes_client.py: Docker exec 客户端
│   │
│   ├── session_manager
│   │   ├── manager.py: 会话目录管理
│   │   ├── validators.py: 路径白名单 + 命令黑名单
│   │   └── schema.sql: SQLite 表结构
│   │
│   └── web-ui (8501)
│   │   ├── app.py: Streamlit 主入口
│   │   ├── components/task_runner.py: SSE 流式执行
│   │   └── components/downloader.py: 文件下载组件
│
├── Agent: hermes-agent (8645)
│   └── LLM Agent，通过 docker exec 调用
│
└── Storage: 本地文件系统 + SQLite
    └── data/sessions/{session_id}/
        ├── uploads/
        ├── outputs/
        └── workspace.db
```

### 2.2 关键文件路径

| 模块 | 文件 | 职责 |
|------|------|------|
| hermes-bridge | `services/hermes-bridge/app/main.py` | CORS 配置（B-06） |
| hermes-bridge | `services/hermes-bridge/app/services/hermes_client.py` | Docker exec（B-01） |
| session_manager | `services/session_manager/validators.py` | 安全校验 |
| web-ui | `services/web-ui/app.py` | 主界面 |
| web-ui | `services/web-ui/components/task_runner.py` | 任务执行 |

---

## 三、方案设计

### 3.1 B-01 解决方案：容器白名单

**当前问题**：`hermes_client.py` 中 `CONTAINER_NAME` 从环境变量读取，但无白名单校验，可能被恶意配置执行任意容器。

**方案**：添加硬编码白名单 + 环境变量校验

```python
# hermes_client.py 修改
ALLOWED_CONTAINERS = {"hermes-agent"}  # 硬编码白名单

class HermesClient:
    CONTAINER_NAME = os.getenv("HERMES_CONTAINER_NAME", "hermes-agent")
    
    def __init__(self):
        # 校验容器名在白名单内
        if self.CONTAINER_NAME not in ALLOWED_CONTAINERS:
            raise SecurityError(
                f"容器 '{self.CONTAINER_NAME}' 不在允许列表中"
            )
    
    def is_available(self) -> bool:
        # ... 原有逻辑
        # 额外校验：确保容器名匹配
        if self.CONTAINER_NAME not in ALLOWED_CONTAINERS:
            return False
```

**优势**：
- 改动最小（仅修改 `hermes_client.py`）
- 双重校验（初始化 + 运行时）
- 向后兼容（不影响现有 API）

### 3.2 B-06 解决方案：CORS 环境变量

**当前问题**：`main.py` 中 `allow_origins=["*"]` 硬编码

**方案**：从环境变量读取

```python
# main.py 修改
import os

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**配置示例**：
```env
# .env
CORS_ORIGINS=http://localhost:8501,https://your-domain.com
```

### 3.3 B-07 解决方案：文件大小限制

**方案**：在 `task_runner.py` 和 API 层添加限制

```python
# 环境变量配置
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))

# task_runner.py 修改
def save_upload_file(...):
    if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise FileSizeError(f"文件超过 {MAX_FILE_SIZE_MB}MB 限制")
```

### 3.4 功能增强设计

#### 批量处理

```
用户上传多文件 → Web UI 显示列表 → 逐个处理 → 结果打包下载
```

**实现要点**：
- Web UI 支持多文件上传（Streamlit `file_uploader` 多文件模式）
- Bridge API 批量提交（新增 `/api/batch` 端点）
- 进度追踪（每个文件独立状态）

#### 处理模板保存

```
用户保存指令为模板 → 存储到 SQLite → Web UI 模板列表 → 一键复用
```

**实现要点**：
- 扩展 `schema.sql` 添加 `templates` 表
- 新增模板 CRUD API
- Web UI 模板管理页面

#### 结果预览

```
处理完成 → Web UI 内嵌预览 → 支持表格渲染 → 无需下载即可查看
```

**实现要点**：
- 解析 xlsx/csv 为 DataFrame
- Streamlit `st.dataframe()` 渲染表格
- 支持文本/JSON 预览

---

## 四、风险点与避坑说明

### 4.1 风险矩阵

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| B-01 修复影响现有功能 | 低 | 高 | 充分测试 + 回滚方案 |
| 批量处理内存溢出 | 中 | 中 | 文件数量限制（≤10）+ 流式处理 |
| 模板存储 SQL 注入 | 低 | 高 | 参数化查询 |
| 预览组件兼容性 | 中 | 低 | 支持 xlsx/csv，其他格式下载查看 |

### 4.2 避坑指南

1. **B-01 修复**：先在测试环境验证，确认 hermes-agent 可正常执行
2. **批量处理**：限制单次最多 10 个文件，避免资源耗尽
3. **模板保存**：使用 session_manager 现有存储层，不新增依赖
4. **CORS 配置**：默认 `"*"` 保持向后兼容，生产环境必须配置

---

## 五、验收标准

### 5.1 P0 验收（必须通过）

| 编号 | 验收项 | 验收方式 |
|------|--------|----------|
| V-01 | Bridge 仅可 exec hermes-agent | 尝试修改环境变量为其他容器，服务启动失败 |
| V-02 | 现有功能无回归 | E2E 测试：上传文件 → 执行任务 → 下载结果 |

### 5.2 P1 验收（建议通过）

| 编号 | 验收项 | 验收方式 |
|------|--------|----------|
| V-03 | CORS 环境变量生效 | 配置 `CORS_ORIGINS=http://localhost` 后仅允许本地 |
| V-04 | 文件大小限制生效 | 上传超过 50MB 文件被拒绝 |
| V-05 | 批量上传 5 个文件成功处理 | 手动测试 |
| V-06 | 模板保存/加载功能可用 | 手动测试 |
| V-07 | 结果预览正确渲染表格 | 手动测试 |
| V-08 | Bridge 单元测试覆盖 >80% | pytest --cov |

### 5.3 用户验收

```
场景：文职人员批量处理 Excel
1. 打开 Web UI，上传 5 个销售数据文件
2. 选择"统计汇总"模板（或输入自定义指令）
3. 点击"批量执行"
4. 查看处理进度（每个文件独立状态）
5. 预览第一个结果文件（表格渲染）
6. 打包下载全部结果

预期：全程无需 CLI，批量处理效率提升 3x+
```

---

## 六、任务拆解概览

详见 `tasks.md`：

| 任务组 | 任务数 | P0 | 预估工时 |
|----------|--------|-----|----------|
| 安全修复（B-01） | 3 | 2 | 1h |
| 配置优化（B-06/B-07） | 4 | 0 | 1h |
| 批量处理 | 5 | 0 | 3h |
| 处理模板 | 4 | 0 | 2h |
| 结果预览 | 3 | 0 | 1.5h |
| 质量提升 | 3 | 0 | 2h |
| **总计** | **20** | **2** | **9.5h** |

---

## 七、依赖与前置条件

### 7.1 技术依赖

| 依赖 | 版本 | 说明 |
|------|------|------|
| Docker | 24+ | 容器运行时 |
| Python | 3.11+ | Bridge/Web UI 运行时 |
| Streamlit | 1.32+ | Web UI 框架 |

### 7.2 环境依赖

- Phase 2 已部署并运行正常
- 本地文件系统可访问
- hermes-agent 容器正常运行

---

## 八、时间规划

```
Phase 3: 本地化增强 (2-3 天)
│
├── Day 1: 安全修复 + 配置优化
│   ├── [上午] B-01 容器白名单 (T03-01 ~ T03-03)
│   └── [下午] B-06 CORS + B-07 文件限制 (T03-04 ~ T03-07)
│
├── Day 2: 功能增强
│   ├── [上午] 批量处理 (T03-08 ~ T03-12)
│   └── [下午] 处理模板 (T03-13 ~ T03-16)
│
└── Day 3: 预览 + 质量
    ├── [上午] 结果预览 (T03-17 ~ T03-19)
    └── [下午] 测试 + 文档 (T03-20 ~ T03-22)
```

---

## 附录：评审参考

- 实现评审汇总报告：`docs/workitems/实现评审分析/report_summary.md`
- 技术评审详情：`docs/workitems/实现评审分析/report_engineer.md`
- 产品评审详情：`docs/workitems/实现评审分析/report_pm.md`
- 当前架构速查：`docs/standards/skills/architecture.md`