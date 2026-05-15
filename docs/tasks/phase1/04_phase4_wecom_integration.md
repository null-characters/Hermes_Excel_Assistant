# Phase 4: WeCom 集成测试

> **阶段**: Phase 4 (Day 8-10)
> **目标**: 企业微信回调配置 + 端到端测试
> **依赖**: Phase 2 + Phase 3 完成

---

## 任务清单

| ID | 任务 | 描述 | 验收标准 | P0 | 预估 |
|----|------|------|----------|-----|------|
| T04-01 | 配置 WeCom Callback | 设置 corp_id/agent_id/token | Hermes WeCom 配置正确 | | 30min |
| T04-02 | 创建企微自建应用 | 企业微信管理后台配置 | 回调 URL 可访问 | | 45min |
| T04-03 | 验证回调 URL | GET 验证签名 + echostr | 验证成功返回 echostr | | 30min |
| T04-04 | 测试文本消息接收 | 发送指令 → Hermes 处理 | Hermes 日志显示消息 | | 30min |
| T04-05 | 🔴 测试文件处理流程 | 上传 → 发送指令 → 接收结果 | 返回处理后的 Excel | P0 | 1h |
| T04-06 | 🔴 测试进度通知 | 检查四阶段通知发送 | 用户收到进度消息 | P0 | 45min |
| T04-07 | 编写端到端测试脚本 | Python 自动化测试 | 测试脚本通过 | | 1h |

---

## 验收清单

- [ ] WeCom 自建应用回调 URL 配置成功
- [ ] Hermes 接收企微文本消息
- [ ] 上传 Excel → 发送指令 → 收到结果文件
- [ ] 进度通知四阶段消息发送成功
- [ ] 非 owner 文件访问被拒绝

---

## 关键配置

```bash
# WeCom Callback 环境变量
WECOM_CALLBACK_CORP_ID=your-corp-id
WECOM_CALLBACK_AGENT_ID=1000002
WECOM_CALLBACK_TOKEN=your-token
WECOM_CALLBACK_ENCODING_AES_KEY=your-43-char-key
```

---

## AI Prompt 模板

**T04-02**: "请指导我在企业微信管理后台创建自建应用，配置回调 URL 为 https://your-domain/wecom/callback"

**T04-05**: "请编写端到端测试脚本：1. 上传 Excel 到 File Upload Service 2. 发送企微消息 '@助手 处理 file_xxx' 3. 等待结果文件"

**T04-06**: "请验证进度通知是否发送：检查 Hermes 日志中的 WeCom 消息发送记录"