# MVP 开发任务清单总览

> **创建日期**: 2026-05-14
> **规划来源**: docs/plan/Hermes_WeCom_Excel_Assistant_MVP.md (V3)

---

## 任务统计

| 阶段 | 清单文件 | 任务数 | P0任务 | 预估工时 |
|------|----------|--------|--------|----------|
| Phase 1 | `docs/tasks/01_phase1_environment.md` | 8 | 2 | Day 1-2 |
| Phase 2 | `docs/tasks/02_phase2_file_upload.md` | 10 | 4 | Day 3-5 |
| Phase 3 | `docs/tasks/03_phase3_hermes_skills.md` | 6 | 3 | Day 6-7 |
| Phase 4 | `docs/tasks/04_phase4_wecom_integration.md` | 7 | 2 | Day 8-10 |
| Phase 5 | `docs/tasks/05_phase5_monitoring.md` | 5 | 0 | Day 11-14 |
| **总计** | - | **36** | **11** | **14 天** |

---

## P0 任务清单（必须完成）

| ID | 任务 | 阶段 | 验收标准 |
|----|------|------|----------|
| T01-04 | 配置 nginx HTTPS | Phase 1 | HTTPS 重定向生效 |
| T01-05 | Hermes 安全环境变量 | Phase 1 | 网络隔离生效 |
| T02-04 | FileMetadata 用户绑定 | Phase 2 | 包含 user_id 字段 |
| T02-05 | 文件上传 API | Phase 2 | user_id 绑定 |
| T02-06 | 文件下载验证 | Phase 2 | 非 owner 返回 403 |
| T02-08 | 上传后跳转逻辑 | Phase 2 | 自动跳转聊天 |
| T03-02 | 进度通知技能规范 | Phase 3 | 四阶段通知 |
| T03-03 | 进度通知 Skill 实现 | Phase 3 | 通知发送成功 |
| T03-04 | 文件归属验证 Skill | Phase 3 | 拒绝非归属 |
| T04-05 | 文件处理流程测试 | Phase 4 | 返回结果文件 |
| T04-06 | 进度通知测试 | Phase 4 | 四阶段消息 |

---

## 依赖关系图

```
Phase 1 (T01-01~08)
    │
    ├────► Phase 2 (T02-01~10)
    │          │
    │          └────► Phase 4 (T04-01~07)
    │
    └────► Phase 3 (T03-01~06)
               │
               └────► Phase 4 (T04-01~07)
                         │
                         └────► Phase 5 (T05-01~05)
```

---

## 执行顺序建议

1. **Phase 1** → 先完成基础环境 + 安全配置
2. **Phase 2 + Phase 3** → 可并行开发（无依赖）
3. **Phase 4** → 需等待 Phase 2 + 3 完成
4. **Phase 5** → 最后完成监控

---

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| V1.0 | 2026-05-14 | 初稿：36 个任务拆分完成 |