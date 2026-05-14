# 运维文档

## 服务管理

### 启动服务

```bash
# 启动所有服务
docker compose up -d

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f
docker compose logs -f hermes
docker compose logs -f file-upload
```

### 停止服务

```bash
# 停止所有服务
docker compose down

# 停止并删除数据卷
docker compose down -v
```

### 重启服务

```bash
# 重启所有服务
docker compose restart

# 重启单个服务
docker compose restart hermes
docker compose restart file-upload
```

---

## 故障恢复

### Hermes 崩溃

**症状**: Hermes 服务状态为 exited 或 restarting

**恢复步骤**:
```bash
# 1. 检查日志
docker compose logs hermes

# 2. 检查配置
docker compose exec hermes cat /root/.hermes/config.yaml

# 3. 重启服务
docker compose restart hermes

# 4. 验证恢复
docker compose ps
curl http://localhost:8645/health
```

### MinIO 数据丢失

**症状**: 文件上传/下载失败

**恢复步骤**:
```bash
# 1. 检查 MinIO 状态
docker compose ps minio
docker compose logs minio

# 2. 检查数据卷
docker volume ls | grep minio

# 3. 重启 MinIO
docker compose restart minio

# 4. 验证存储
curl http://localhost:9000/minio/health/live
```

**预防措施**:
- 定期备份 MinIO 数据
- 配置 MinIO 集群模式

### LLM API 不可用

**症状**: Agent 处理请求失败

**恢复步骤**:
```bash
# 1. 检查 API Key
docker compose exec hermes env | grep API_KEY

# 2. 测试 API 连接
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" https://openrouter.ai/api/v1/models

# 3. 切换备用提供商（修改 .env）
HERMES_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxx

# 4. 重启 Hermes
docker compose restart hermes
```

### 沙箱执行卡死

**症状**: 任务长时间运行无响应

**恢复步骤**:
```bash
# 1. 检查 Docker 容器
docker ps | grep hermes-terminal

# 2. 强制终止超时容器
docker ps -q --filter "name=hermes-terminal" | xargs -r docker kill

# 3. 重启 Hermes（清理状态）
docker compose restart hermes
```

---

## 日志管理

### 日志位置

| 服务 | 日志位置 |
|------|----------|
| Hermes | `docker compose logs hermes` |
| File Upload | `docker compose logs file-upload` |
| Nginx | `docker compose logs nginx-proxy` |
| MinIO | `docker compose logs minio` |
| Prometheus | `docker compose logs prometheus` |

### 日志级别配置

修改 `.env`:
```bash
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
```

### 日志轮转

Docker Compose 默认配置日志轮转：
```yaml
services:
  hermes:
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

---

## 监控告警

### Prometheus 访问

```
http://your-domain:9090
```

### 关键指标

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| `up` | 服务状态 | down → critical |
| `container_cpu_usage_seconds_total` | CPU 使用率 | >80% → warning |
| `container_memory_usage_bytes` | 内存使用 | >80% → warning |
| `minio_cluster_capacity_usable_free_bytes` | MinIO 容量 | <10% → warning |

### 告警规则

见 `prometheus/alerts.yml`

---

## 备份策略

### MinIO 数据备份

```bash
# 手动备份
docker compose exec minio mc mirror local/excel-files /backup/$(date +%Y%m%d)

# 定时备份（crontab）
0 2 * * * docker compose exec minio mc mirror local/excel-files /backup/$(date +\%Y\%m\%d)
```

### 配置文件备份

```bash
# 备份配置
tar -czvf config_backup_$(date +%Y%m%d).tar.gz config/ .env nginx/
```

---

## 安全检查

### 定期检查项

1. **SSL 证书有效期**
   ```bash
   openssl x509 -in nginx/ssl/cert.pem -noout -dates
   ```

2. **API Key 轮换**
   - 每 90 天更换 WeCom Secret
   - 定期轮换 LLM API Key

3. **访问日志审计**
   ```bash
   docker compose logs nginx-proxy | grep -E "(403|401)"
   ```

4. **安全更新**
   ```bash
   # 检查镜像更新
   docker compose pull
   
   # 重建并重启
   docker compose up -d --build
   ```

---

## 版本
v1.0.0