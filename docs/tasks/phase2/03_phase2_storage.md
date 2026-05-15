# Phase 2: 本地文件存储实现

> **阶段**: Phase 2 - 产品化线 (Day 2)
> **目标**: 实现本地文件存储，替代 MinIO
> **依赖**: T02-07 ~ T02-12 (SQLite 隔离架构)
> **并行**: 与安全修复线并行推进

---

## 任务清单

| ID | 任务 | 描述 | 验收标准 | P0 | 预估 |
|----|------|------|----------|-----|------|
| T02-13 | 实现本地文件上传 | 上传文件保存到会话 uploads 目录 | 文件正确保存 | | 30min |
| T02-14 | 实现本地文件下载 | 从会话 outputs 目录下载文件 | 文件正确返回 | | 30min |
| T02-15 | 实现文件元数据管理 | 在 SQLite 中记录文件信息 | 可查询文件元数据 | | 30min |
| T02-16 | 更新 Bridge 文件路径注入 | 将文件路径注入到 prompt 中 | Agent 可访问文件 | | 30min |
| T02-17 | 移除 MinIO 依赖 | 从 docker-compose.yml 移除 MinIO | 服务启动无 MinIO | | 15min |
| T02-18 | 更新 .env.example | 移除 MinIO 相关配置 | 无 MinIO 配置项 | | 15min |
| T02-19 | 验证文件处理链路 | 上传 → 处理 → 下载全流程 | 文件正确处理 | P0 | 30min |

---

## 验收清单

- [ ] 上传文件保存到 `data/sessions/{session_id}/uploads/`
- [ ] 下载文件从 `data/sessions/{session_id}/outputs/` 返回
- [ ] SQLite workspace.db 包含文件元数据
- [ ] Bridge prompt 包含文件绝对路径
- [ ] docker-compose.yml 无 MinIO 服务
- [ ] 上传 → 处理 → 下载全流程通过

---

## 关键文件

```
Hermes-WeCom-Assistant/
├── docker-compose.yml           # T02-17
├── .env.example                 # T02-18
├── services/
│   ├── session_manager/
│   │   ├── storage.py           # T02-13, T02-14, T02-15
│   │   └── manager.py           # 已完成
│   └── hermes-bridge/app/
│       └── services/
│           └── hermes_client.py # T02-16
└── tests/
    └── test_storage.py          # T02-19
```

---

## 文件存储 API

```python
# storage.py
import os
import shutil
from pathlib import Path
from .manager import get_session_path

UPLOADS_DIR = "uploads"
OUTPUTS_DIR = "outputs"

def save_upload(session_id: str, file_name: str, file_content: bytes) -> str:
    """保存上传文件"""
    uploads_path = get_session_path(session_id) / UPLOADS_DIR
    uploads_path.mkdir(parents=True, exist_ok=True)
    
    # 生成唯一文件名
    file_id = f"file_{uuid.uuid4().hex[:8]}"
    stored_name = f"{file_id}_{file_name}"
    
    file_path = uploads_path / stored_name
    file_path.write_bytes(file_content)
    
    return str(file_path)

def get_download(session_id: str, file_name: str) -> bytes:
    """获取下载文件"""
    outputs_path = get_session_path(session_id) / OUTPUTS_DIR
    file_path = outputs_path / file_name
    
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_name}")
    
    return file_path.read_bytes()

def list_outputs(session_id: str) -> list[str]:
    """列出输出文件"""
    outputs_path = get_session_path(session_id) / OUTPUTS_DIR
    if not outputs_path.exists():
        return []
    return [f.name for f in outputs_path.iterdir() if f.is_file()]
```

---

## Bridge 文件路径注入

```python
# hermes_client.py (更新)
async def process_excel(self, file_path: str, task: str, session_id: str):
    """处理 Excel 文件"""
    # 注入文件路径到 prompt
    prompt = f"""
请处理以下 Excel 文件：
- 文件路径: {file_path}
- 任务要求: {task}

请将结果保存到 {get_session_path(session_id) / 'outputs' / 'result.xlsx'}
"""
    return await self.execute_task(prompt)
```

---

## AI Prompt 模板

**T02-13**: "请实现 save_upload(session_id, file_name, file_content) 函数，将文件保存到会话 uploads 目录"

**T02-16**: "请更新 hermes_client.py 的 process_excel 方法，将文件路径注入到 prompt 中，让 Agent 可以直接访问文件"

**T02-17**: "请从 docker-compose.yml 中移除 MinIO 服务和相关配置"