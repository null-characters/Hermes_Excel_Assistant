# Phase 2: File Upload Service

> **阶段**: Phase 2 (Day 3-5)
> **目标**: FastAPI 文件上传服务 + 用户绑定验证 + H5 页面
> **依赖**: Phase 1 完成

---

## 任务清单

| ID | 任务 | 描述 | 验收标准 | P0 | 预估 |
|----|------|------|----------|-----|------|
| T02-01 | 创建 FastAPI 项目骨架 | services/file-upload 目录结构 | main.py 可启动 | | 30min |
| T02-02 | 编写 requirements.txt | fastapi, uvicorn, minio, pydantic | 依赖安装成功 | | 15min |
| T02-03 | 编写 Dockerfile | Python 3.11-slim 基础镜像 | 构建成功 | | 30min |
| T02-04 | 🔴 实现 FileMetadata 模型 | 用户ID绑定 + 7天过期 | 包含 user_id 字段 | P0 | 30min |
| T02-05 | 🔴 实现文件上传 API | POST /upload + MinIO 存储 | 返回 file_id + user_id 绑定 | P0 | 1h |
| T02-06 | 🔴 实现文件下载 API + 验证 | GET /download/{file_id} + 归属验证 | 非 owner 返回 403 | P0 | 1h |
| T02-07 | 创建 H5 上传页面 | static/upload.html | 可选择 Excel 上传 | | 1h |
| T02-08 | 🔴 实现上传后跳转逻辑 | 自动跳转��微聊天 + 预填 file_id | URL 参数传递 file_id | P0 | 30min |
| T02-09 | 实现 MinIO 客户端封装 | bucket 创建 + 文件上传/下载 | 连接 MinIO 成功 | | 45min |
| T02-10 | 编写单元测试 | pytest 测试上传/下载/验证 |覆盖率 ≥80% | | 1h |

---

## 验收清单

- [ ] `POST /upload` 返回 `{file_id, user_id, expires_at}`
- [ ] `GET /download/{file_id}?user_id=xxx` 验证归属
- [ ] H5 页面可上传 Excel 并显示 file_id
- [ ] 上传成功后跳转企微聊天（scheme://wxwork）
- [ ] pytest 测试通过

---

## 关键文件

```
services/file-upload/
├── Dockerfile               # T02-03
├── requirements.txt         # T02-02
└── app/
    ├── main.py              # T02-01, T02-05, T02-06
    ├── models.py            # T02-04 (FileMetadata)
    ├── routers/
    │   └── upload.py        # T02-05, T02-06
    ├── services/
    │   └── minio_client.py  # T02-09
    └── static/
    │   └── upload.html      # T02-07, T02-08
    └── tests/
        └── test_upload.py   # T02-10
```

---

## AI Prompt 模板

**T02-04**: "请创建 FileMetadata Pydantic 模型，包含 file_id, user_id(WeCom用户ID), filename, upload_time, expires_at(7天后)"

**T02-06**: "请实现文件下载 API，验证 user_id 归属：从 MinIO 获取 metadata，比对 user_id，非 owner 返回 HTTPException(403)"

**T02-08**: "请在 upload.html 中实现上传成功后跳转企微聊天，使用 scheme://wxwork/chat?message=file_id 预填消息"