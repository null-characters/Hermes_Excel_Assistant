# Phase 2: 安全止血

> **阶段**: Phase 2 - 安全修复线 (Day 1)
> **目标**: 消除生产部署阻塞项，修复安全漏洞
> **依赖**: Phase 1 完成
> **并行**: 与产品化线并行推进

---

## 任务清单

| ID | 任务 | 描述 | 验收标准 | P0 | 预估 |
|----|------|------|----------|-----|------|
| T02-01 | 🔴 移除 Docker Socket 挂载 | 从 hermes-agent 容器移除 `/var/run/docker.sock` | 容器无法访问 Docker API | P0 | 15min |
| T02-02 | 🔴 Prompt 参数转义 | 在 `hermes_client.py` 中对 prompt 进行 shell 转义 | 特殊字符不会导致命令注入 | P0 | 30min |
| T02-03 | 清理废弃配置文件 | 删除 `config/config.yaml` 和 `config/nodes.json` | 仅保留 `hermes-config.yaml` | | 15min |
| T02-04 | 添加安全警告文档 | 在 README 和 LOCAL_DEV_GUIDE.md 中添加安全警告 | 文档包含"生产不可部署"警告 | | 15min |
| T02-05 | 更新 docker-compose.yml | 移除 Agent 的 socket，保留 Bridge 的 socket | 仅 Bridge 有 Docker 权限 | P0 | 15min |
| T02-06 | 验证安全配置 | 启动服务，验证 Agent 无法执行 docker 命令 | `docker exec hermes-agent docker ps` 失败 | P0 | 15min |

---

## 验收清单

- [ ] `docker-compose.yml` 中 hermes-agent 无 Docker Socket 挂载
- [ ] `hermes_client.py` 中 prompt 使用 `shlex.quote()` 转义
- [ ] `config/config.yaml` 和 `config/nodes.json` 已删除
- [ ] README.md 包含安全警告章节
- [ ] Agent 容器无法执行 `docker ps`

---

## 关键文件

```
Hermes-WeCom-Assistant/
├── docker-compose.yml           # T02-01, T02-05
├── README.md                    # T02-04
├── docs/LOCAL_DEV_GUIDE.md      # T02-04
├── config/
│   ├── config.yaml              # T02-03 (删除)
│   ├── nodes.json               # T02-03 (删除)
│   └── hermes-config.yaml       # 保留
└── services/hermes-bridge/app/
    └── services/
        └── hermes_client.py     # T02-02
```

---

## 安全警告模板

```markdown
## 安全警告

> ⚠️ **当前版本为 MVP 阶段，生产环境不可部署**

### 已知安全限制

| 限制项 | 说明 | 风险等级 |
|--------|------|----------|
| local 终端无沙箱 | Agent 执行的代码无进程隔离 | 🔴 Critical |
| 无认证机制 | API 无身份验证 | 🟡 Medium |
| SQLite 数据隔离仅逻辑隔离 | 路径白��单可被绕过 | 🟡 Medium |

### 生产部署前必须解决

- [ ] 实现 Docker 终端后端或 gVisor 沙箱
- [ ] 添加 API 认证机制
- [ ] 实现路径白名单强制校验
```

---

## AI Prompt 模板

**T02-01**: "请从 docker-compose.yml 中移除 hermes-agent 服务的 `/var/run/docker.sock` 挂载，仅保留 hermes-bridge 的挂载"

**T02-02**: "请在 hermes_client.py 的 execute_task 方法中，使用 shlex.quote() 对 prompt 参数进行转义，防止 shell 命令注入"

**T02-03**: "请删除废弃的配置文件 config/config.yaml 和 config/nodes.json，仅保留 hermes-config.yaml"