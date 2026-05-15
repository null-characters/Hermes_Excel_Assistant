# Phase 3: 处理模板

> **阶段**: Phase 3 - 处理模板线 (Day 3 上午)
> **目标**: 支持高频指令保存为模板，一键复用
> **依赖**: T03-01 ~ T03-04（安全修复完成）
> **评审来源**: 实现评审分析 Phase 3 建议方向

---

## 任务清单

| ID | 任务 | 描述 | 验收标准 | P0 | 预估 |
|----|------|------|----------|-----|------|
| T03-11 | 设计模板存储 Schema | 在 SQLite 中新增 templates 表 | Schema 设计文档，支持名称/指令/标签 |  | 30min |
| T03-12 | 实现模板 CRUD API | Bridge 添加模板增删改查端点 | POST/GET/PUT/DELETE 模板 |  | 45min |
| T03-13 | Web UI 模板管理页面 | 添加模板列表、保存、编辑、删除界面 | 可视化管理模板 |  | 45min |
| T03-14 | 模板一键执行功能 | 从模板列表选择模板直接执行 | 点击模板 → 自动填入指令 → 执行 |  | 30min |
| T03-15 | 模板功能测试 | 编写模板 CRUD + 执行测试 | 全部测试通过 |  | 30min |

---

## 实现方案

### T03-11: 模板 Schema

```sql
-- 在 session.db 中新增 templates 表
CREATE TABLE IF NOT EXISTS templates (
    id TEXT PRIMARY KEY,           -- tmpl_{hex8}
    name TEXT NOT NULL,            -- 模板名称
    prompt TEXT NOT NULL,          -- 指令内容
    tags TEXT DEFAULT '[]',        -- 标签 JSON 数组
    session_id TEXT,               -- 所属会话（NULL=全局）
    use_count INTEGER DEFAULT 0,   -- 使用次数
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

### T03-12: 模板 API

```python
# hermes-bridge/app/routers/template.py
@router.post("/templates")           # 创建模板
@router.get("/templates")            # 列出模板（支持按 session_id 过滤）
@router.get("/templates/{tmpl_id}")  # 获取模板详情
@router.put("/templates/{tmpl_id}")  # 更新模板
@router.delete("/templates/{tmpl_id}")  # 删除模板
@router.post("/templates/{tmpl_id}/execute")  # 从模板执行
```

### T03-13: Web UI 模板管理

```
┌─────────────────────────────────────┐
│ 📋 处理模板                         │
├─────────────────────────────────────┤
│ [保存当前指令为模板]                  │
│                                     │
│ 🔥 常用模板                          │
│ ┌─────────────────────────────────┐ │
│ │ 统计汇总  |  使用 12 次  [▶] [✏] [🗑] │ │
│ │ "统计每个产品的总销售额..."         │ │
│ └─────────────────────────────────┘ │
│ ┌─────────────────────────────────┐ │
│ │ 数据清洗  |  使用 5 次   [▶] [✏] [🗑] │ │
│ │ "清洗空值和重复行..."             │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

---

## 验收清单

- [ ] templates 表创建成功
- [ ] 模板 CRUD API 全部可用
- [ ] Web UI 可视化管理模板
- [ ] 从模板一键执行功能正常
- [ ] 测试全部通过

---

## 关键文件

```
services/hermes-bridge/app/
├── routers/template.py    # T03-12: 新增
├── models.py              # T03-12: 新增 Template 模型
└── services/
    └── template_service.py  # T03-12: 新增

services/session_manager/
└── storage.py             # T03-11: 新增模板存储方法

services/web-ui/app.py     # T03-13, T03-14: 模板界面

tests/test_template.py     # T03-15: 新增
```
