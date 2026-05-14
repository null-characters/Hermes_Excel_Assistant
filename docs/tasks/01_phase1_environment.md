# Phase 1: 基础环境搭建

> **阶段**: Phase 1 (Day 1-2)
> **目标**: Docker 环境 + 安全配置 + 项目骨架
> **依赖**: 无

---

## 任务清单

| ID | 任务 | 描述 | 验收标准 | P0 | 预估 |
|----|------|------|----------|-----|------|
| T01-01 | 创建项目骨架 | 按 §6 目录结构创建空目录 | 所有目录存在 | | 15min |
| T01-02 | 编写 docker-compose.yml | 按 §8.2 配置 5 个服务 | `docker compose config` 验证通过 | | 30min |
| T01-03 | 创建 .env.example | 按 §8.1 环境变量模板 | 所有必填项有占位符 | | 15min |
| T01-04 | 🔴 配置 nginx HTTPS | 创建 nginx/conf.d/ + SSL 配置 | HTTPS 重定向生效 | P0 | 1h |
| T01-05 | 🔴 Hermes 安全环境变量 | 配置 TERMINAL_NETWORK_DISABLED 等 | 环境变量正确注入 | P0 | 30min |
| T01-06 | 创建 README.md | 项目说明 + 快速启动指南 | 包含启动命令 | | 30min |
| T01-07 | 创建 config/config.yaml | Hermes 基础配置 | WeCom Callback 配置项存在 | | 30min |
| T01-08 | 验证 Docker 环境 | 启动所有服务，检查健康状态 | 5 个服务全部 running | | 30min |

---

## 验收清单

- [ ] `docker-compose.yml` 包含 nginx-proxy, hermes, file-upload, minio, prometheus
- [ ] `.env.example` 包含所有必填环境变量
- [ ] `nginx/conf.d/default.conf` 配置 HTTPS 重定向
- [ ] Hermes 环境变量包含 `TERMINAL_NETWORK_DISABLED=true`
- [ ] `docker compose up -d` 成功启动所有服务

---

## 关键文件

```
Hermes-WeCom-Assistant/
├── docker-compose.yml       # T01-02
├── .env.example             # T01-03
├── README.md                # T01-06
├── config/
│   └── config.yaml          # T01-07
└── nginx/
    ├── ssl/                 # T01-04
    └── conf.d/
        └── default.conf     # T01-04
```

---

## AI Prompt 模板

**T01-02**: "请帮我编写 docker-compose.yml，包含 nginx-proxy、hermes-agent:v0.13.0、file-upload、minio、prometheus 五个服务，参考 §8.2 配置"

**T01-04**: "请创建 nginx HTTPS 配置，强制重定向 HTTP→HTTPS，SSL 证书路径为 ./nginx/ssl/"

**T01-05**: "请在 docker-compose.yml hermes 服务中添加安全环境变量：TERMINAL_NETWORK_DISABLED=true, TERMINAL_TIMEOUT=300"