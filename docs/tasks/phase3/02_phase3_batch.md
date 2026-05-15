# Phase 3: 批量处理

> **阶段**: Phase 3 - 批量处理线 (Day 2)
> **目标**: 支持多文件上传、批量执行、结果打包下载
> **依赖**: T03-01 ~ T03-04（安全修复完成）
> **评审来源**: 实现评审分析 B-04（进度反馈增强）

---

## 任务清单

| ID | 任务 | 描述 | 验收标准 | P0 | 预估 |
|----|------|------|----------|-----|------|
| T03-05 | 🔴 扩展上传组件支持多文件 | Web UI 文件上传组件支持多文件选择/拖拽 | 可同时上传多个文件 | P0 | 45min |
| T03-06 | 实现批量任务提交逻辑 | Bridge API 支持批量提交，逐个执行 | 批量提交后逐文件执行并返回结果 |  | 1h |
| T03-07 | 实现批量任务进度追踪 | Web UI 显示每个文件的处理状态 | 显示"处理中/已完成/失败"状态 |  | 45min |
| T03-08 | 实现结果打包下载 | 全部完成后可打包下载所有结果文件 | 点击"下载全部"获取 zip 包 |  | 30min |
| T03-09 | 添加文件数量限制 | 限制单次批量上传最多 10 个文件 | 超过 10 个文件时提示限制 |  | 15min |
| T03-10 | 批量处理 E2E 测试 | 编写批量处理端到端测试 | 5 文件批量处理测试通过 |  | 45min |

---

## 实现方案

### T03-05: 多文件上传

```python
# web-ui/app.py 修改
uploaded_files = st.file_uploader(
    "上传 Excel 文件",
    type=["xlsx", "xls", "csv"],
    accept_multiple_files=True,  # 关键：启用多文件
)
```

### T03-06: 批量任务提交

```python
# hermes-bridge 新增批量端点
@router.post("/tasks/batch")
async def create_batch_tasks(request: BatchTaskRequest):
    results = []
    for file_info in request.files:
        result = await execute_single_task(file_info, request.prompt, request.session_id)
        results.append(result)
    return BatchTaskResponse(results=results)
```

### T03-07: 进度追踪

```
文件1: ✅ 已完成 (2.3s)
文件2: 🔄 处理中... (预计 3s)
文件3: ⏳ 等待中
文件4: ⏳ 等待中
文件5: ❌ 失败 - 格式不支持
```

### T03-08: 打包下载

```python
import zipfile
import io

def create_download_zip(results: list[dict]) -> bytes:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        for result in results:
            zf.write(result['filepath'], result['filename'])
    return zip_buffer.getvalue()
```

---

## 验收清单

- [ ] 文件上传组件支持多文件选择
- [ ] 批量提交后逐文件执行
- [ ] 每个文件显示处理状态
- [ ] 全部完成后可打包下载
- [ ] 超过 10 个文件时提示限制
- [ ] E2E 测试通过

---

## 关键文件

```
services/web-ui/app.py                          # T03-05, T03-07, T03-08, T03-09
services/hermes-bridge/app/routers/task.py      # T03-06
services/hermes-bridge/app/models.py            # T03-06: 新增 BatchTask 模型
services/session_manager/storage.py             # T03-06: 批量存储
tests/test_batch.py                             # T03-10: 新增
```

---

## 数据模型

```python
# BatchTaskRequest
class BatchTaskRequest(BaseModel):
    session_id: str
    prompt: str
    files: list[FileInfo]  # 最多 10 个

# BatchTaskResponse
class BatchTaskResponse(BaseModel):
    results: list[TaskResult]
    total: int
    completed: int
    failed: int

# TaskResult (扩展)
class TaskResult(BaseModel):
    filename: str
    status: Literal["success", "failed", "pending"]
    result_path: str | None
    error: str | None
    duration_seconds: float | None
```
