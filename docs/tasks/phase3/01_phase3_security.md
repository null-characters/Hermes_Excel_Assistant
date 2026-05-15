# Phase 3: 安全修复 — Bridge Docker exec 权限限制

> **阶段**: Phase 3 - 安全修复线 (Day 1 上午)
> **目标**: 解决 B-01，限制 Bridge Docker exec 仅允许 hermes-agent 容器
> **依赖**: Phase 2 完成
> **评审来源**: 实现评审分析 B-01（P0）

---

## 任务清单

| ID | 任务 | 描述 | 验收标准 | P0 | 预估 |
|----|------|------|----------|-----|------|
| T03-01 | 🔴 添加容器白名单 | 在 `hermes_client.py` 中添加 `ALLOWED_CONTAINERS` 白名单，exec 前校验容器名 | 尝试 exec 非白名单容器抛出 SecurityError | P0 | 30min |
| T03-02 | 🔴 容器校验单元测试 | 为白名单校验添加单元测试，覆盖：合法容器、非法容器、空容器名 | pytest 通过，覆盖白名单逻辑 | P0 | 30min |
| T03-03 | 移除不必要 Docker 权限 | 审计 Bridge Docker 权限，移除非必要能力 | docker inspect 仅显示必要挂载 |  | 30min |
| T03-04 | 安全修复回归验证 | 运行全量 E2E 测试，确认现有功能无回归 | 所有 E2E 测试通过 |  | 30min |

---

## 实现方案

### T03-01: 容器白名单

```python
# services/hermes-bridge/app/services/hermes_client.py

# 新增
ALLOWED_CONTAINERS = {"hermes-agent"}

class SecurityError(Exception):
    """容器执行权限校验失败"""
    pass

class HermesClient:
    def execute_task(self, prompt: str, session_id: str) -> dict:
        # 校验容器白名单
        if self.container_name not in ALLOWED_CONTAINERS:
            raise SecurityError(
                f"Container '{self.container_name}' not in allowed list: {ALLOWED_CONTAINERS}"
            )
        # ... 原有逻辑
```

### T03-02: 单元测试

```python
# tests/test_hermes_client_security.py

def test_allowed_container():
    """白名单容器可正常执行"""

def test_disallowed_container():
    """非白名单容器抛出 SecurityError"""

def test_empty_container_name():
    """空容器名抛出 SecurityError"""

def test_case_sensitive():
    """容器名大小写敏感"""
```

---

## 验收清单

- [ ] `hermes_client.py` 包含 `ALLOWED_CONTAINERS` 白名单
- [ ] 非白名单容器执行抛出 `SecurityError`
- [ ] 单元测试覆盖白名单逻辑
- [ ] E2E 测试全部通过
- [ ] 现有功能无回归

---

## 关键文件

```
services/hermes-bridge/app/
├── services/
│   └── hermes_client.py     # T03-01: 添加白名单
└── tests/
    └── test_hermes_client_security.py  # T03-02: 新增

docker-compose.yml            # T03-03: 审计权限
```

---

## ⏱️ 检查点触发

> **本任务线完成后触发 CP1 检查点**

**详见**: [00_phase3_overview.md - CP1 检查点](./00_phase3_overview.md#cp1-安全修复验收-day-1-结束)
