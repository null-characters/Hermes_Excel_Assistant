# Phase 3: 质量提升

> **阶段**: Phase 3 - 质量提升线 (Day 1 下午 + Day 4-5)
> **目标**: 补充测试、更新文档、配置化安全参数
> **依赖**: Phase 2 完成
> **评审来源**: 实现评审分析 B-02 ~ B-07（P1 问题）

---

## 任务清单

| ID | 任务 | 描述 | 验收标准 | P0 | 预估 |
|----|------|------|----------|-----|------|
| T03-20 | 更新架构文档 | 重写 `architecture.md` 为当前实现（移除 MinIO/File Upload 引用） | 文档反映当前架构 |  | 30min |
| T03-21 | 补充 Bridge 单元测试 | 为 hermes-bridge 添加单元测试，覆盖 >80% | pytest --cov >80% |  | 1h |
| T03-22 | CORS 环境变量配置 | 将 CORS allow_origins 从硬编码改为环境变量 | CORS_ORIGINS 环境变量生效 |  | 15min |
| T03-23 | 文件大小限制配置 | 添加文件大小限制配置（默认 50MB） | 超过限制时拒绝上传 |  | 15min |

---

## 实现方案

### T03-20: 架构文档更新

**当前架构**（需更新）：
```
Gateway: nginx-proxy (HTTPS 终止)
Services: hermes-bridge (API) + session_manager (本地模块) + web-ui (Streamlit)
Agent: hermes-agent (LLM + 代码执行)
Storage: 本地文件系统 + SQLite
```

**移除内容**：
- MinIO 对象存储引用
- File Upload Service 引用
- 企业微信回调路由（本地化路线）

### T03-21: Bridge 单元测试

```python
# tests/test_hermes_bridge.py (新增)
def test_health_endpoint():
    """健康检查端点"""

def test_execute_task_success():
    """任务执行成功"""

def test_execute_task_invalid_prompt():
    """非法 prompt 拒绝"""

def test_session_not_found():
    """会话不存在返回 404"""

# tests/test_task_router.py (新增)
def test_create_task():
    """创建任务"""

def test_get_task_status():
    """获取任务状态"""

def test_list_tasks():
    """列出任务"""
```

### T03-22: CORS 配置化

```python
# hermes-bridge/app/main.py 修改
import os

ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8501").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    ...
)
```

```bash
# .env.example 新增
CORS_ORIGINS=http://localhost:8501,https://your-domain.com
```

### T03-23: 文件大小限制

```python
# hermes-bridge/app/routers/task.py 修改
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", "50")) * 1024 * 1024

@router.post("/upload")
async def upload_file(file: UploadFile):
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(413, f"File exceeds {MAX_FILE_SIZE // 1024 // 1024}MB limit")
    ...
```

```bash
# .env.example 新增
MAX_FILE_SIZE_MB=50
```

---

## 验收清单

- [ ] `architecture.md` 反映当前实现
- [ ] `pytest --cov services/hermes-bridge` >80%
- [ ] CORS_ORIGINS 环境变量生效
- [ ] 文件大小限制生效（超过 50MB 拒绝）

---

## 关键文件

```
docs/standards/skills/architecture.md  # T03-20: 更新

services/hermes-bridge/app/tests/
├── test_hermes_bridge.py              # T03-21: 新增
└── test_task_router.py                # T03-21: 新增

services/hermes-bridge/app/main.py     # T03-22: CORS 配置
services/hermes-bridge/app/routers/task.py  # T03-23: 文件限制

.env.example                           # T03-22, T03-23: 新增配置
```

---

## 测试覆盖目标

| 模块 | 当前覆盖 | 目标覆盖 | 新增测试 |
|------|----------|----------|----------|
| hermes_client | 0% | >80% | test_hermes_client.py |
| task router | 0% | >80% | test_task_router.py |
| main | 0% | >60% | test_main.py |
| **整体** | **0%** | **>80%** | **约 15 个测试** |

---

## ⏱️ 检查点触发

> **本任务线完成后触发 CP3 检查点**

**详见**: [00_phase3_overview.md - CP3 检查点](./00_phase3_overview.md#cp3-质量提升--phase-3-结项-day-5-结束)