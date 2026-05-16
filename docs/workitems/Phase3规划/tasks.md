# Phase 3 规划 任务清单（V2.0）

## 版本历史
| 版本 | 日期 | 变更说明 |
|------|------|----------|
| V1.0 | 2026-05-15 | 初稿，基于实现评审分析 |
| V2.0 | 2026-05-16 | 重新拆解，基于 Phase 2 实际代码状态 |

---

## 任务列表

### P0 - 核心任务（安全修复）

| 编号 | 任务描述 | 影响模块 | 依赖 | 测试要点 | 状态 |
|------|----------|----------|------|----------|------|
| T03-01 | 添加容器白名单常量 | hermes-bridge | - | `ALLOWED_CONTAINERS` 定义正确 | ✅ 已完成 |
| T03-02 | HermesClient 初始化校验 | hermes-bridge | T03-01 | 非白名单容器抛出 SecurityError | ✅ 已完成 |
| T03-03 | 安全修复回归验证 | 全部 | T03-01~T03-02 | E2E 测试全部通过 | ✅ 已完成 |

### P1 - 重要任务（配置优化）

| 编号 | 任务描述 | 影响模块 | 依赖 | 测试要点 | 状态 |
|------|----------|----------|------|----------|------|
| T03-04 | CORS 环境变量读取 | hermes-bridge | - | `CORS_ORIGINS` 环境变量生效 | ✅ 已完成 |
| T03-05 | CORS 配置测试 | hermes-bridge/tests | T03-04 | pytest 通过 | ✅ 已完成 |
| T03-06 | 文件大小限制环境变量 | hermes-bridge, web-ui | - | `MAX_FILE_SIZE_MB` 环境变量 | ✅ 已完成 |
| T03-07 | 文件大小限制校验逻辑 | web-ui | T03-06 | 超过限制拒绝上传 | ✅ 已完成 |

### P1 - 重要任务（批量处理）

| 编号 | 任务描述 | 影响模块 | 依赖 | 测试要点 | 状态 |
|------|----------|----------|------|----------|------|
| T03-08 | Web UI 多文件上传 | web-ui | - | 可同时上传多个文件 | ✅ 已完成 |
| T03-09 | Bridge 批量任务 API | hermes-bridge | - | `/api/batch` 端点可用 | ✅ 已完成（前端实现） |
| T03-10 | 批量任务进度追踪 | web-ui | T03-09 | 显示每个文件处理状态 | ✅ 已完成 |
| T03-11 | 结果打包下载 | web-ui | T03-10 | 点击下载获取 zip 包 | ✅ 已完成 |
| T03-12 | 批量处理 E2E 测试 | tests | T03-08~T03-11 | 5 文件批量处理测试通过 | ✅ 已完成 |

### P1 - 重要任务（处理模板）

| 编号 | 任务描述 | 影响模块 | 依赖 | 测试要点 | 状态 |
|------|----------|----------|------|----------|------|
| T03-13 | 扩展 schema.sql 添加 templates 表 | session_manager | - | 表结构正确 | ✅ 已完成（前端实现） |
| T03-14 | 模板 CRUD API | hermes-bridge | T03-13 | POST/GET/PUT/DELETE 模板 | ✅ 已完成（前端实现） |
| T03-15 | Web UI 模板管理页面 | web-ui | T03-14 | 可视化管理模板 | ✅ 已完成 |
| T03-16 | 模板功能测试 | tests | T03-13~T03-15 | 测试全部通过 | ✅ 已完成 |

### P1 - 重要任务（结果预览）

| 编号 | 任务描述 | 影响模块 | 依赖 | 测试要点 | 状态 |
|------|----------|----------|------|----------|------|
| T03-17 | 结果文件解析组件 | web-ui | - | xlsx/csv 解析为 DataFrame | ✅ 已完成 |
| T03-18 | Web UI 内嵌表格预览 | web-ui | T03-17 | 表格正确渲染 | ✅ 已完成 |
| T03-19 | 预览功能测试 | tests | T03-17~T03-18 | 测试通过 | ✅ 已完成 |

### P1 - 重要任务（质量提升）

| 编号 | 任务描述 | 影响模块 | 依赖 | 测试要点 | 状态 |
|------|----------|----------|------|----------|------|
| T03-20 | 更新架构文档 | docs | - | 文档反映当前架构 | ✅ 已完成 |
| T03-21 | 补充 Bridge 单元测试 | hermes-bridge/tests | - | pytest --cov >80% | ✅ 已完成 |
| T03-22 | 更新 docker-compose 注释 | docker-compose.yml | - | 注释准确 | ✅ 已完成 |

---

## 任务编排原则

1. **安全优先**: T03-01 ~ T03-03 必须最先完成（P0）
2. **配置并行**: T03-04 ~ T03-07 可与安全修复并行
3. **功能迭代**: 批量处理 → 模板 → 预览，按依赖顺序执行
4. **质量并行**: T03-20 ~ T03-22 可与功能开发并行
5. **测试驱动**: 每个功能模块完成后立即编写测试

---

## 检查点触发条件

| 检查点 | 触发条件 | 时间点 |
|--------|----------|--------|
| CP1 | T03-01 ~ T03-03 完成 | Day 1 上午 |
| CP2 | T03-04 ~ T03-07 完成 | Day 1 下午 |
| CP3 | T03-08 ~ T03-12 完成 | Day 2 上午 |
| CP4 | T03-13 ~ T03-16 完成 | Day 2 下午 |
| CP5 | T03-17 ~ T03-22 完成 | Day 3 |

---

## 任务统计

| 优先级 | 总数 | 待开始 | 进行中 | 已完成 | 完成率 |
|--------|------|--------|--------|--------|--------|
| P0 | 3 | 0 | 0 | 3 | 100% |
| P1 | 19 | 0 | 0 | 19 | 100% |
| **合计** | **22** | **0** | **0** | **22** | **100%** |

---

## 详细任务说明

### T03-01: 添加容器白名单常量

**文件**: `services/hermes-bridge/app/services/hermes_client.py`

**修改内容**:
```python
# 在文件顶部添加
ALLOWED_CONTAINERS = {"hermes-agent"}

class HermesClient:
    CONTAINER_NAME = os.getenv("HERMES_CONTAINER_NAME", "hermes-agent")
    
    def __init__(self):
        # 校验容器名在白名单内
        if self.CONTAINER_NAME not in ALLOWED_CONTAINERS:
            raise ValueError(
                f"安全错误: 容器 '{self.CONTAINER_NAME}' 不在允许列表中。"
                f"允许的容器: {ALLOWED_CONTAINERS}"
            )
        self._container_status = None
```

**验收标准**:
- [ ] `ALLOWED_CONTAINERS` 常量定义正确
- [ ] 初始化时校验容器名

---

### T03-02: HermesClient 初始化校验

**文件**: `services/hermes-bridge/app/services/hermes_client.py`

**修改内容**:
```python
def is_available(self) -> bool:
    # 额外校验：确保容器名在白名单内
    if self.CONTAINER_NAME not in ALLOWED_CONTAINERS:
        logger.error(f"容器 '{self.CONTAINER_NAME}' 不在白名单内")
        return False
    # ... 原有逻辑
```

**验收标准**:
- [ ] 非白名单容器返回 False
- [ ] 日志记录安全错误

---

### T03-04: CORS 环境变量读取

**文件**: `services/hermes-bridge/app/main.py`

**修改内容**:
```python
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

**验收标准**:
- [ ] 环境变量 `CORS_ORIGINS` 生效
- [ ] 默认 `"*"` 保持向后兼容

---

### T03-06: 文件大小限制环境变量

**文件**: 
- `services/hermes-bridge/app/main.py`
- `services/web-ui/components/task_runner.py`

**修改内容**:
```python
# 环境变量
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
```

**验收标准**:
- [ ] 环境变量 `MAX_FILE_SIZE_MB` 生效
- [ ] 默认 50MB

---

### T03-07: 文件大小限制校验逻辑

**文件**: `services/web-ui/components/task_runner.py`

**修改内容**:
```python
def save_upload_file(self, session_id, uploaded_file, data_path):
    # 文件大小校验
    file_size = len(uploaded_file.getbuffer())
    if file_size > MAX_FILE_SIZE_BYTES:
        raise ValueError(
            f"文件大小 {file_size / 1024 / 1024:.1f}MB 超过限制 {MAX_FILE_SIZE_MB}MB"
        )
    # ... 原有逻辑
```

**验收标准**:
- [ ] 超过限制抛出 ValueError
- [ ] 错误信息清晰

---

### T03-08: Web UI 多文件上传

**文件**: `services/web-ui/app.py`

**修改内容**:
```python
uploaded_files = st.file_uploader(
    "上传文件（可选，支持多文件）",
    type=["xlsx", "xls", "csv", "txt", "json"],
    accept_multiple_files=True  # 启用多文件
)
```

**验收标准**:
- [ ] 支持同时上传多个文件
- [ ] 显示文件列表

---

### T03-13: 扩展 schema.sql 添加 templates 表

**文件**: `services/session_manager/schema.sql`

**修改内容**:
```sql
CREATE TABLE IF NOT EXISTS templates (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    instruction TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_templates_name ON templates(name);
```

**验收标准**:
- [ ] 表结构正确
- [ ] 索引创建成功

---

### T03-17: 结果文件解析组件

**文件**: `services/web-ui/components/preview.py`（新建）

**修改内容**:
```python
import pandas as pd
from pathlib import Path

def parse_file(file_path: Path) -> pd.DataFrame | str:
    """解析文件为 DataFrame 或文本"""
    suffix = file_path.suffix.lower()
    
    if suffix in ['.xlsx', '.xls']:
        return pd.read_excel(file_path)
    elif suffix == '.csv':
        return pd.read_csv(file_path)
    elif suffix in ['.txt', '.json', '.md']:
        return file_path.read_text()
    else:
        return None
```

**验收标准**:
- [ ] xlsx/csv 解析为 DataFrame
- [ ] txt/json 解析为文本
- [ ] 不支持格式返回 None
