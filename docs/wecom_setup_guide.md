# 企业微信集成配置指南

## 1. 创建自建应用

### 1.1 登录企业微信管理后台

访问 https://work.weixin.qq.com/ 并使用管理员账号登录。

### 1.2 创建应用

1. 进入「应用管理」→「自建应用」
2. 点击「创建应用」
3. 填写应用信息：
   - 应用名称：Excel 助手
   - 应用Logo：上传图标
   - 可见范围：选择部门/人员

### 1.3 获取应用凭证

创建完成后，记录以下信息：

```
AgentId: 1000002
Secret: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## 2. 配置回调 URL

### 2.1 设置回调域名

在应用详情页 → 「企业可信IP」中添加服务器 IP。

### 2.2 配置接收消息

1. 进入「接收消息」→「设置 API 接收」
2. 填写回调 URL：
   ```
   https://your-domain.com/wecom/callback
   ```
3. 设置 Token 和 EncodingAESKey（随机生成）
4. 记录以下信息：
   ```
   Token: your-token
   EncodingAESKey: your-43-char-encoding-aes-key
   ```

### 2.3 验证回调

点击保存时，企业微信会发送 GET 请求验证 URL 有效性。

## 3. 配置企业 ID

在「我的企业」页面获取：

```
CorpID: wwxxxxxxxxxxxxxxxx
```

## 4. 环境变量配置

将以上信息填入 `.env` 文件：

```bash
# 企业微信回调配置
WECOM_CALLBACK_CORP_ID=wwxxxxxxxxxxxxxxxx
WECOM_CALLBACK_CORP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WECOM_CALLBACK_AGENT_ID=1000002
WECOM_CALLBACK_TOKEN=your-token
WECOM_CALLBACK_ENCODING_AES_KEY=your-43-char-encoding-aes-key
WECOM_CALLBACK_ALLOWED_USERS=user1,user2
```

## 5. H5 应用配置（可选）

### 5.1 配置应用首页

在应用详情页 → 「应用主页」设置：

```
https://your-domain.com/static/upload.html
```

### 5.2 配置可信域名

在「网页授权及JS-SDK」中添加：

```
your-domain.com
```

## 6. 测试验证

### 6.1 验证服务状态

```bash
# 检查服务
docker compose ps

# 查看日志
docker compose logs -f hermes
```

### 6.2 发送测试消息

在企业微信应用中发送：

```
你好
```

检查 Hermes 日志是否收到消息。

## 7. 常见问题

### Q: 回调 URL 验证失败

检查：
1. 域名是否正确解析
2. HTTPS 证书是否有效
3. 防火墙是否开放 443 端口

### Q: 消息发送失败

检查：
1. CorpID/Secret 是否正确
2. AgentId 是否匹配
3. 用户是否在可见范围内

### Q: 文件上传失败

检查：
1. MinIO 服务是否正常
2. 环境变量配置是否正确
3. 网络连接是否正常

## 版本
v1.0.0