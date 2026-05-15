# Phase 5: 监控运维

> **阶段**: Phase 5 (Day 11-14)
> **目标**: Prometheus 监控 + 健康检查 + 故障恢复
> **依赖**: Phase 4 完成

---

## 任务清单

| ID | 任务 | 描述 | 验收标准 | P0 | 预估 |
|----|------|------|----------|-----|------|
| T05-01 | 创建 prometheus.yml | 监控 5 个服务 | 配置文件有效 | | 30min |
| T05-02 | 配置服务健康检查 | docker-compose healthcheck | 健康检查生效 | | 30min |
| T05-03 | 配置告警规则 | CPU/Memory/MinIO 告警 | 告警规则生效 | | 45min |
| T05-04 | 编写运维文档 | 故障恢复 + 日志管理 | 包含恢复步骤 | | 45min |
| T05-05 | 验证监控生效 | Prometheus UI 显示指标 | 所有服务 UP | | 30min |

---

## 验收清单

- [ ] Prometheus 采集 5 个服务指标
- [ ] docker-compose healthcheck 配置生效
- [ ] CPU >80% 告警规则生效
- [ ] 运维文档包含故障恢复步骤
- [ ] Prometheus UI 显示所有服务 UP

---

## 关键文件

```
prometheus/
├── prometheus.yml           # T05-01
└── alerts.yml               # T05-03

docs/
└── operations.md            # T05-04
```

---

## 监控指标

| 服务 | 指标 | 告警阈值 |
|------|------|----------|
| Hermes | 健康状态 | down → 立即告警 |
| file-upload | CPU | >80% → 警告 |
| minio | 存储容量 | >90% → 警告 |
| Agent 执行 | 失败率 | >10% → 警告 |

---

## AI Prompt 模板

**T05-01**: "请编写 prometheus.yml，监控 nginx-proxy(443), hermes(8645), file-upload(8000), minio(9000), prometheus(9090)"

**T05-03**: "请编写 Prometheus 告警规则：CPU>80% warning, Memory>80% warning, MinIO容量>90% warning, 服务down critical"