# 会话隔离架构设计

> **版本**: v1.0
> **日期**: 2026-05-15
> **状态**: Phase 2 - 已实现

---

## 1. 设计目标

为 Hermes Excel Assistant 实现会话级数据隔离，确保：

1. **数据隔离**: 不同会话的数据完全隔离，互不影响
2. **安全访问**: 用户只能访问自己会话目录内的文件
3. **便捷管理**: 会话创建、删除、查询操作简单
4. **审计追踪**: 每个会话有独立的任务和文件记录

---

## 2. 目录结构

```
data/
├── sessions/
│   ├── sess_001/                 # 会话 1
│   │   ├── workspace.db          # SQLite 数据库（任务记录、元数据）
│   │   ├── uploads/              # 用户上传文件
│   │   │   └── sales_data.xlsx
│   │   └── outputs/              # Agent 输出文件
│   │       └── result_001.xlsx
│   │       └── summary.xlsx
│   ├── sess_002/                 # 会话 2
│   │   ├── workspace.db
│   │   ├── uploads/
│   │   └── outputs/
│   └── sess_xxx/                 # 更多会话
└── config/
    └── hermes-config.yaml        # Hermes Agent 配置
```

---

## 3. SQLite Schema

每个会话拥有独立的 `workspace.db` 文件，包含两张表：

### 3.1 tasks 表

记录会话内的所有任务执行历史。

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,           -- 任务 ID (UUID)
    prompt TEXT NOT NULL,          -- 用户输入的 prompt
    status TEXT DEFAULT 'pending', -- pending/running/completed/failed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,        -- 完成时间
    output_file TEXT,              -- 输出文件路径
    error TEXT                     -- 错误信息
);
```

### 3.2 files 表

记录会话内的所有文件元数据。

```sql
CREATE TABLE IF NOT EXISTS files (
    id TEXT PRIMARY KEY,           -- 文件 ID (UUID)
    original_name TEXT NOT NULL,   -- 原始文件名
    stored_path TEXT NOT NULL,     -- 存储路径
    size INTEGER,                  -- 文件大小 (bytes)
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. 模块设计

### 4.1 SessionManager 类

```python
class SessionManager:
    """会话管理器"""

    def create_session(session_id: Optional[str] = None) -> str
    def delete_session(session_id: str) -> bool
    def list_sessions() -> list[str]
    def get_session_path(session_id: str) -> Path
    def get_uploads_path(session_id: str) -> Path
    def get_outputs_path(session_id: str) -> Path
    def get_database_path(session_id: str) -> Path
    def session_exists(session_id: str) -> bool
    def get_session_info(session_id: str) -> Optional[dict]
```

### 4.2 Validators 模块

```python
def validate_path(path: str, session_id: str) -> Path
    """路径白名单校验 - 确保路径在会话目录内"""

def validate_prompt(prompt: str) -> str
    """命令黑名单校验 - 检测危险命令"""
```

---

## 5. 安全机制

### 5.1 路径白名单

**原理**: 所有文件路径必须解析到会话目录内。

**校验流程**:
1. 规范化基础路径 (`data/sessions/{session_id}`)
2. 解析目标路径（绝对路径或相对路径）
3. 检查目标路径是否在会话目录内
4. 拒绝包含 `..` 的路径遍历字符

**拒绝示例**:
- `../../etc/passwd` → 路径遍历攻击
- `/etc/passwd` → 越权访问
- `../sess_002/uploads/file.xlsx` → 跨会话访问

### 5.2 命令黑名单

**原理**: 检测 prompt 中的危险命令模式。

**黑名单列表**:

| 模式 | 说明 |
|------|------|
| `rm -rf /` | 删除根目录 |
| `rm -rf ~` | 删除用户目录 |
| `sudo` | 提权命令 |
| `chmod 777` | 全权限修改 |
| `> /dev/` | 设备文件写入 |
| `mkfs` | 格式化命令 |
| `dd if=` | 磁盘操作 |
| `fork bomb` | 进程炸弹 |
| `curl \| sh` | 远程脚本执行 |

---

## 6. 使用示例

### 6.1 创建会话

```python
from session_manager import get_session_manager

manager = get_session_manager()
session_id = manager.create_session()
# 返回: "sess_a1b2c3d4e5f6"
```

### 6.2 上传文件

```python
from session_manager import validate_path, get_session_manager

manager = get_session_manager()
uploads_path = manager.get_uploads_path(session_id)

# 安全路径校验
file_path = validate_path("uploads/sales.xlsx", session_id)
```

### 6.3 执行任务

```python
from session_manager import validate_prompt

# 安全 prompt 校验
prompt = validate_prompt("统计销售额并生成汇总表")
```

### 6.4 删除会话

```python
manager.delete_session(session_id)
# 会话目录及所有数据被删除
```

---

## 7. 测试覆盖

| 测试场景 | 测试文件 |
|----------|----------|
| 路径白名单校验 | `tests/session_manager/test_validators.py` |
| 命令黑名单校验 | `tests/session_manager/test_validators.py` |
| 会话管理操作 | `tests/session_manager/test_manager.py` |

---

## 8. 后续优化

Phase 3 可考虑的增强：

1. **会话过期清理**: 自动清理超过 N 天的会话
2. **会话配额限制**: 单会话文件大小/数量限制
3. **审计日志**: 记录所有文件访问和命令执行
4. **加密存储**: 对敏感文件加密存储

---

## 9. 相关文件

| 文件 | 说明 |
|------|------|
| `services/session_manager/manager.py` | 会话管理核心实现 |
| `services/session_manager/validators.py` | 安全校验模块 |
| `services/session_manager/schema.sql` | SQLite Schema |
| `tests/session_manager/test_validators.py` | 校验模块测试 |