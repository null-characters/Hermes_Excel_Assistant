# Hermes Excel Assistant 本地化方案 — 高级软件工程师深度分析报告

> **评审日期**: 2026-05-15
> **评审视角**: 高级软件工程师
> **评审对象**: 当前 MVP 本地化方案全栈代码与架构

---

## 一、架构层面问题

### 1.1 核心通信机制脆弱 🔴 P0

**现状**: Hermes Bridge 通过 `subprocess.run(["docker", "exec", ...])` 与 Hermes Agent 通信。

```python
# hermes_client.py:122-124
cmd = [
    "docker", "exec", self.CONTAINER_NAME,
    HERMES_PATH, "chat", "-q", prompt
]
result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
```

**问题清单**:

| 问题 | 风险 | 影响 |
|------|------|------|
| 同步阻塞调用 | 🔴 高 | 单任务占满进程，无法并发 |
| 无输出流式传输 | 🔴 高 | 用户等待 60s+ 无任何反馈 |
| prompt 无转义 | 🔴 高 | 特殊字符导致命令注入或解析错误 |
| 容器名硬编码 | 🟡 中 | 多实例部署冲突 |
| 无重试机制 | 🟡 中 | 网络抖动直接失败 |

**命令注入风险示例**:
```bash
# 如果 prompt 包含 shell 元字符
curl -X POST ... -d '{"message": "test"; rm -rf /"}'
# 实际执行: docker exec hermes-agent hermes chat -q "test"; rm -rf /"
```

**建议**:
1. 使用 Docker SDK (`docker-py`) 替代 `subprocess`，避免 shell 注入
2. 引入任务队列（Celery/ARQ）实现异步处理
3. 实现 SSE/WebSocket 流式输出

### 1.2 终端后端降级带来的安全缺口 🔴 P0

**现状**: 因 Docker-in-Docker 兼容性问题，终端后端从 `docker` 降级为 `local`。

```yaml
# hermes-config.yaml
terminal:
  backend: local  # ← 无隔离！
```

**风险**:

| 风险项 | local 后端 | docker 后端 |
|--------|-----------|-------------|
| 文件系统隔离 | ❌ 共享容器根文件系统 | ✅ 独立容器 |
| 网络隔离 | ❌ 共享网络栈 | ✅ network_disabled |
| 进程隔离 | ❌ 共享 PID namespace | ✅ 独立进程树 |
| 资源限制 | ❌ 无 CPU/内存限制 | ✅ cgroups 限制 |
| 恶意代码执行 | 🔴 可影响宿主 | 🟢 影响限于沙箱 |

**影响**: 用户通过自然语言指令可诱导 Agent 执行任意命令，直接影响 Hermes Agent 容器及挂载的 Docker socket。

**建议**:
1. 短期：限制 Agent 可用工具集，禁用 `terminal` 中危险命令
2. 中期：解决 Docker 后端兼容性问题（调整 `--cap-drop` 参数）
3. 长期：引入 gVisor/kata-containers 轻量级沙箱

### 1.3 Docker Socket 暴露 🔴 P0

**现状**: 两个容器都挂载了 Docker socket。

```yaml
# docker-compose.yml:75
- /var/run/docker.sock:/var/run/docker.sock  # hermes-agent
# docker-compose.yml:51
- /var/run/docker.sock:/var/run/docker.sock  # hermes-bridge
```

**风险**: 任何获得容器内代码执行能力的攻击者，可通过 Docker socket 获得宿主机 root 权限（Docker Group ≈ Root）。

**建议**: 仅 hermes-bridge 需要 Docker socket（用于 `docker exec`）。Hermes Agent 的 Docker 后端已改 local，应移除其 socket 挂载。

---

## 二、代码质量问题

### 2.1 Hermes Client 设计缺陷

#### 问题 A: Excel 处理流程断裂 🟡 P1

```python
# hermes_client.py:202-220
async def process_excel(self, file_id, task, user_id="local_user"):
    prompt = f"处理 {file_id} {task}"
    return await self.send_message(prompt, file_id, user_id)
```

`process_excel` 仅将 `file_id` 拼接到 prompt 字符串中，Hermes Agent 无法访问 MinIO 中的文件。整个 Excel 处理链路是**断裂的**：

```
用户上传文件 → MinIO 存储 → file_id 返回用户
                                     ↓
用户提交任务 → Bridge → Hermes Agent → "处理 file_xxx 的任务"
                                              ↓
                                    Agent 不知道 file_xxx 在哪！
```

**建议**: 实现 File Bridge —— Bridge 从 MinIO 下载文件，挂载到 Agent 可访问路径，再让 Agent 处理。

#### 问题 B: 无结构化输出 🟡 P1

```python
# hermes_client.py:142-146
return HermesResponse(
    success=True,
    message="任务执行成功",
    output=result.stdout.strip(),  # ← 原始 CLI 输出，包含 ANSI 转义码
    error=None
)
```

返回值是 Hermes CLI 的原始 stdout，包含 ANSI 颜色码、进度条、工具调用日志等，无法被程序解析。

**建议**: 使用 `hermes chat -q --quiet` 或 `-Q` 参数获取纯净输出。

#### 问题 C: 超时处理不完整 🟡 P1

```python
# hermes_client.py:93-100
except asyncio.TimeoutError:
    # ← 永远不会触发！
    # asyncio.to_thread 不支持 timeout 参数
    # 实际超时由 subprocess.TimeoutExpired 处理
```

`asyncio.to_thread` 本身不支持超时，`asyncio.TimeoutError` 分支是死代码。

### 2.2 全链路测试名不副实 🟡 P1

```python
# test_full_chain.py:136-140
# TODO: 实现 Hermes Agent 任务提交
# Hermes Agent 使用消息网关或 CLI 交互
# 这里模拟处理过程
print(f"   ⚠️ Hermes Agent 消息网关未配置，使用模拟处理")
return self._simulate_processing(task)
```

- `--mode full` 实际并未调用 Hermes Bridge API
- 测试端口指向 `8645`（Hermes Agent 直连），而非 `8646`（Bridge API）
- 没有断言，只有 print 输出

### 2.3 配置管理混乱 🟡 P1

当前存在多套配置文件，职责不清：

| 文件 | 用途 | 实际生效 |
|------|------|----------|
| `config/config.yaml` | 原规划配置 | ❌ 未被使用 |
| `config/hermes-config.yaml` | Hermes 实际配置 | ✅ 挂载到容器 |
| `config/nodes.json` | LLM 节点配置 | ❌ 未被使用 |
| `.env` | 环境变量 | ⚠️ 部分生效 |
| `docker-compose.yml environment` | 容器环境变量 | ⚠️ 与 .env 重复 |

**问题**: 
- `config/config.yaml` 和 `config/nodes.json` 是废弃文件，误导开发者
- `.env` 中的 `HERMES_PROVIDER` 与 `docker-compose.yml` 中的 `HERMES_INFERENCE_PROVIDER` 映射关系不透明
- 安全配置（`TERMINAL_NETWORK_DISABLED`）在 `.env` 和 `hermes-config.yaml` 中同时存在但值不同

---

## 三、可靠性问题

### 3.1 单点故障链 🔴 P0

```
用户请求 → Bridge (单实例) → docker exec → Agent (单实例) → LLM API
```

| 故障点 | 影响 | 恢复方式 |
|--------|------|----------|
| Bridge 进程崩溃 | 全部请求失败 | `restart: unless-stopped` |
| Agent 容器重启 | 执行中任务丢失 | 无恢复机制 |
| LLM API 401 | 所有任务失败 | 无 fallback |
| Docker daemon 重启 | 全部容器停止 | 手动恢复 |

### 3.2 无任务持久化 🔴 P0

- 任务提交后无 task_id 返回（始终为 `null`）
- 无法查询任务状态
- 无法重试失败任务
- Agent 重启后所有会话丢失

### 3.3 并发安全 🟡 P1

```python
# hermes_client.py — 无并发控制
async def execute_task(self, prompt, timeout=None):
    # 两个并发请求同时 docker exec
    # Hermes Agent 是单进程 CLI，并发执行会冲突
```

Hermes Agent 的 `chat -q` 是单次执行模式，并发 `docker exec` 可能导致：
- 会话文件冲突
- 资源竞争
- 输出串扰

---

## 四、性能问题

### 4.1 冷启动延迟 🟡 P1

每次 `docker exec hermes chat -q` 都需要：
1. 启动 Python 解释器
2. 加载 Hermes 模块
3. 初始化 Agent
4. 调用 LLM API

实测：简单 `print(1+1)` 需要 14s，其中大部分是初始化开销。

### 4.2 无连接复用

每次请求创建新的 `docker exec` 进程，无法复用 Agent 的已有会话和上下文。

---

## 五、安全问题汇总

| 编号 | 问题 | 严重性 | 状态 |
|------|------|--------|------|
| SEC-1 | Docker Socket 暴露给 Agent 容器 | 🔴 Critical | 待修复 |
| SEC-2 | local 终端无沙箱隔离 | 🔴 Critical | 已知妥协 |
| SEC-3 | Prompt 命令注入风险 | 🔴 High | 待修复 |
| SEC-4 | CORS `allow_origins=["*"]` | 🟡 Medium | 开发阶段可接受 |
| SEC-5 | API Key 明文存储在 .env | 🟡 Medium | 待优化 |
| SEC-6 | 无认证/鉴权机制 | 🟡 Medium | 开发阶段可接受 |

---

## 六、架构优化建议

### 6.1 通信层重构（P0）

```
当前:  Bridge → subprocess → docker exec → Hermes CLI
                    ↑
              脆弱、阻塞、不安全

建议:  Bridge → Docker SDK → docker exec → Hermes CLI --quiet
              ↓
        + 任务队列 (ARQ/Redis)
        + 流式输出 (SSE)
        + Prompt 转义
```

### 6.2 文件处理链路修复（P0）

```
当前（断裂）:
  Upload → MinIO → file_id → Bridge → Agent("处理 file_xxx") → ❌

建议（修复）:
  Upload → MinIO → file_id → Bridge → 下载文件到共享卷
                                          ↓
                                     Agent 处理文件
                                          ↓
                                     结果写回共享卷 → Bridge 上传到 MinIO → 返回
```

### 6.3 配置清理（P1）

```
删除:
  - config/config.yaml     （废弃，未被任何服务读取）
  - config/nodes.json      （废弃，custom provider 不需要）

保留:
  - config/hermes-config.yaml  （Hermes Agent 唯一配置源）
  - config/USER.md             （Agent 角色设定）
  - .env                       （环境变量，敏感信息）
```

### 6.4 测试重构（P1）

```
当前:  test_full_chain.py — 300 行，无断言，full 模式未实现

建议:
  tests/
  ├── unit/
  │   ├── test_hermes_client.py    # Mock subprocess
  │   └── test_task_router.py      # FastAPI TestClient
  ├── integration/
  │   ├── test_bridge_agent.py     # Bridge → Agent 集成
  │   └── test_file_pipeline.py    # 上传→处理→下载
  └── e2e/
      └── test_full_chain.py       # 真正的全链路
```

---

## 七、优先级排序与实施路径

### Phase 1: 安全止血（1-2 天）

| 优先级 | 任务 | 工时 |
|--------|------|------|
| P0 | 移除 Agent 容器的 Docker Socket 挂载 | 0.5h |
| P0 | Prompt 参数转义，防止命令注入 | 1h |
| P0 | 清理废弃配置文件 | 0.5h |

### Phase 2: 核心链路修复（3-5 天）

| 优先级 | 任务 | 工时 |
|--------|------|------|
| P0 | 修复 Excel 处理链路（文件传递） | 1d |
| P0 | Docker SDK 替代 subprocess | 0.5d |
| P0 | 添加 `--quiet` 参数获取纯净输出 | 0.5h |
| P1 | 任务队列 + task_id + 状态查询 | 1d |
| P1 | SSE 流式输出 | 0.5d |

### Phase 3: 质量提升（3-5 天）

| 优先级 | 任务 | 工时 |
|--------|------|------|
| P1 | 修复 Docker 终端后端兼容性 | 1d |
| P1 | 单元测试 + 集成测试 | 1d |
| P1 | 配置管理统一 | 0.5d |
| P2 | 并发控制（信号量/队列） | 0.5d |
| P2 | 错误恢复与重试 | 0.5d |

---

## 八、技术决策记录

### 决策 1: local 终端后端

| 项 | 内容 |
|----|------|
| **决策** | 使用 `local` 后端替代 `docker` |
| **原因** | Docker Desktop 不支持 `--cap-drop ALL` + `--pids-limit` 等安全参数组合 |
| **代价** | 无沙箱隔离，生产不可用 |
| **偿还条件** | 解决 Docker 后端兼容性或引入替代沙箱 |

### 决策 2: custom provider

| 项 | 内容 |
|----|------|
| **决策** | 使用 `custom` provider + `OPENAI_API_KEY` 连接腾讯云 GLM-5 |
| **原因** | 内置 `zai` provider 连接智谱官方 API，不适用腾讯云托管端点 |
| **代价** | API Key 命名不直观（`OPENAI_API_KEY` 用于非 OpenAI 服务） |

### 决策 3: subprocess 通信

| 项 | 内容 |
|----|------|
| **决策** | 使用 `subprocess.run` 调用 `docker exec` |
| **原因** | 快速验证可行性 |
| **代价** | 阻塞、不安全、无法流式输出 |
| **偿还条件** | Phase 2 迁移到 Docker SDK |

---

## 九、总体评估

### 9.1 代码质量评分

| 维度 | 评分 | 说明 |
|------|------|------|
| **架构合理性** | 4/10 | 通信机制脆弱，文件链路断裂 |
| **代码质量** | 5/10 | 结构清晰但缺少错误处理和测试 |
| **安全性** | 2/10 | 多个 Critical 级别安全问题 |
| **可维护性** | 5/10 | 配置混乱，文档与代码不一致 |
| **可扩展性** | 3/10 | 单点阻塞，无法水平扩展 |
| **综合评分** | **3.8/10** | 技术原型阶段，需大量加固 |

### 9.2 结论

> **当前方案处于 "Proof of Concept" 阶段，验证了 Hermes + GLM-5 的技术可行性，但距离 MVP 仍有显著差距。**

核心差距：
1. **安全不可用** — local 终端 + Docker Socket 暴露 = 生产环境不可部署
2. **功能不完整** — Excel 处理链路断裂，文件无法从 MinIO 传递到 Agent
3. **质量不达标** — 无测试覆盖，无并发控制，无错误恢复

建议按 Phase 1→2→3 顺序推进，每个 Phase 结束后进行验收评审。

---

> **评审人**: Senior Software Engineer Perspective
> **评审结论**: PoC 验证通过，MVP 待实施，安全需立即止血
