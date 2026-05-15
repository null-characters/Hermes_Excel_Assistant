# Phase 3: Hermes Skills 配置

> **阶段**: Phase 3 (Day 6-7)
> **目标**: Excel 处理技能 + 进度通知技能 + 用户验证集成
> **依赖**: Phase 1 完成

---

## 任务清单

| ID | 任务 | 描述 | 验收标准 | P0 | 预估 |
|----|------|------|----------|-----|------|
| T03-01 | 创建 excel_processor.md | Excel 处理技能规范 | 包含 pandas 使用规范 | | 45min |
| T03-02 | 🔴 创建 progress_notifier.md | 进度通知技能规范 | 四阶段通知逻辑 | P0 | 45min |
| T03-03 | 🔴 实现进度通知 Skill | 调用 WeCom API 发送消息 | 通知发送成功 | P0 | 1h |
| T03-04 | 🔴 实现文件归属验证 Skill | 解析 file_id → 验证 user_id | 拒绝非归属文件 | P0 | 1h |
| T03-05 | 编写 USER.md | Agent 角色设定 + Excel 规范 | 角色为行政财务助理 | | 30min |
| T03-06 | 验证 Skills 加载 | 启动 Hermes 检查 Skills 生效 | 日志显示 Skills 加载 | | 30min |

---

## 验收清单

- [ ] `config/skills/excel_processor.md` 包含 pandas/openpyxl 使用规范
- [ ] `config/skills/progress_notifier.md` 包含四阶段通知逻辑
- [ ] Hermes 启动时加载 Skills
- [ ] 进度通知可发送企微消息
- [ ] 文件归属验证拒绝非 owner

---

## 关键文件

```
config/
├── config.yaml              # Hermes 配置
├── USER.md                  # T03-05
└── skills/
    ├── excel_processor.md   # T03-01
    └── progress_notifier.md # T03-02, T03-03
    └── file_validator.md    # T03-04
```

---

## AI Prompt 模板

**T03-01**: "请编写 excel_processor.md 技能规范，要求：优先使用 pandas，日期格式 YYYY-MM-DD，数值保留两位小数，输出文件后缀 _processed"

**T03-02**: "请编写 progress_notifier.md 技能规范，实现四阶段通知：开始、进行中(每30秒)、完成、发送"

**T03-04**: "请编写 file_validator.md 技能，解析用户指令中的 file_id，调用 File Upload Service 验证 user_id 归属"