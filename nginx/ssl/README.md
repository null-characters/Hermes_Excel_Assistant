# SSL 证书配置说明

## 自签名证书（开发测试用）

```bash
# 生成自签名证书
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/CN=localhost"
```

## 生产环境证书

生产环境建议使用 Let's Encrypt 免费证书：

```bash
# 安装 certbot
brew install certbot  # macOS
# 或
apt-get install certbot  # Ubuntu

# 获取证书
certbot certonly --standalone -d your-domain.com

# 复制证书到项目目录
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
```

## 证书文件位置

- 证书文件: `nginx/ssl/cert.pem`
- 私钥文件: `nginx/ssl/key.pem`

**注意**: 私钥文件切勿提交到版本库！已在 `.gitignore` 中排除。
