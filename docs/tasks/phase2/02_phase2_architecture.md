# Phase 2: SQLite 隔离架构设计

> **阶段**: Phase 2 - 产品化线 (Day 1-2)
> **目标**: 设计会话级数据隔离架构
> **依赖**: Phase 1 完成
> **并行**: 与安全修复线并行推进

---

## 架构设计

### 目录结构

```
data/
├── sessions/
│   ├── sess_001/                 # 会话 1
│   │   ├── workspace.db          # SQLite 数据库（任务记录、元数据）
│   │   ├── uploads/              # 用户上传文件
│   │   │   └── input.xlsx
│   │   └── outputs/              # Agent 输出文件
│   │       └── result.xlsx
│   ├── sess_002/                 # 会话 2
│   │   ├── workspace.db
│   │   ├── uploads/
│   │   └── outputs/
│   └── ...
└── config/
    └── hermes-config.yaml
```

### SQLite 数据库 Schema

```sql
-- workspace.db
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    prompt TEXT NOT NULL,
    status TEXT DEFAULT 'pending',  -- pending/running/completed/failed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    output_file TEXT,
    error TEXT
);

CREATE TABLE files (
    id TEXT PRIMARY KEY,
    original_name TEXT NOT NULL,
    stored_path TEXT NOT NULL,
    size INTEGER,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 任务清单

| ID | 任务 | 描述 | 验收标准 | P0 | 预估 |
|----|------|------|----------|-----|------|
| T02-07 | 设计会话目录结构 | 定义 `data/sessions/{session_id}/` 结构 | 目录结构文档化 | | 30min |
| T02-08 | 设计 SQLite Schema | 定义 tasks 和 files 表结构 | SQL 语句可执行 | | 30min |
| T02-09 | 实现会话管理模块 | 创建 `services/session_manager.py` | 可创建/删除/列出会话 | | 1h |
| T02-10 | 实现路径白名单 | 验证路径必须在会话目录内 | `../../etc/passwd` 被拒绝 | P0 | 30min |
| T02-11 | 实现危险命令黑名单 | 检测 prompt 中的危险命令 | `rm -rf /`, `sudo` 被拒绝 | P0 | 30min |
| T02-12 | 编写架构设计文档 | 输出 `docs/design/session-isolation.md` | 文档包含完整设计 | | 30min |

---

## 验收清单

- [ ] `data/sessions/` 目录结构已定义
- [ ] SQLite Schema 已创建并可执行
- [ ] `session_manager.py` 可创建会话目录
- [ ] 路径白名单校验生效（拒绝 `..` 路径）
- [ ] 危险命令黑名单校验生效

---

## 关键文件

```
Hermes-WeCom-Assistant/
├── services/
│   └── session_manager/
│       ├── __init__.py
│       ├── manager.py            # T02-09
│       ├── validators.py         # T02-10, T02-11
│       └── schema.sql            # T02-08
├── data/
│   └── sessions/                 # T02-07
└── docs/design/
    └── session-isolation.md      # T02-12
```

---

## 路径白名单实现

```python
# validators.py
import os
import re

ALLOWED_BASE_PATH = "/app/data/sessions"

def validate_path(path: str, session_id: str) -> bool:
    """验证路径在会话目录内"""
    # 规范化路径
    normalized = os.path.normpath(path)
    
    # 检查是否在允许的基础路径下
    session_base = os.path.join(ALLOWED_BASE_PATH, session_id)
    if not normalized.startswith(session_base):
        return False
    
    # 检查是否包含路径遍历
    if ".." in path:
        return False
    
    return True

DANGEROUS_COMMANDS = [
    r"rm\s+-rf\s+/",
    r"sudo\s+",
    r"chmod\s+777",
    r">\s+/dev/",
    r"mkfs",
    r"dd\s+if=",
]

def validate_prompt(prompt: str) -> bool:
    """检测危险命令"""
    for pattern in DANGEROUS_COMMANDS:
        if re.search(pattern, prompt, re.IGNORECASE):
            return False
    return True
```

---

## AI Prompt 模板

**T02-07**: "请设计会话目录结构，包含 workspace.db、uploads、outputs 三个部分，输出目录树"

**T02-09**: "请创建 session_manager.py，实现 create_session(session_id)、delete_session(session_id)、list_sessions() 三个方法"

**T02-10**: "请实现路径白名单校验，确保文件路径只能在 data/sessions/{session_id}/ 目录内"

---

## ⏱️ 检查点触发

> **本任务线完成后参与 CP2 检查点**

**触发条件**: T02-07 ~ T02-12 全部完成 + T02-13 ~ T02-19 完成（存储线）

**Review 流程**:
```
1. 完成所有任务 → 勾选验收清单
2. 运行边界测试:
   - 测试路径遍历攻击 → 应被拒绝
   - 测试危险命令注入 → 应被拒绝
   - 测试会话隔离 → 数据不互通
3. 提交 Review Request → 等待 Reviewer + PM 确认
4. CP2 通过 → 进入 Web UI 开发
```

**详见**: [00_phase2_overview.md - CP2 检查点](./00_phase2_overview.md#cp2-架构存储验收-day-3-结束)