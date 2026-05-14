# 进度通知技能规范

## 技能名称
progress_notifier

## 描述
向用户发送任务处理进度通知，提升用户体验，减少等待焦虑。

## 四阶段通知机制

| 阶段 | 触发时机 | 通知内容 | 示例 |
|------|----------|----------|------|
| 开始 | 任务入队 | 确认收到 + 预估时间 | "收到您的请求，正在准备处理，预计需要 2 分钟..." |
| 进行中 | 每30秒或关键节点 | 当前进度 | "处理中... 已完成 50%，正在分析数据..." |
| 完成 | 代码执行完毕 | 完成提示 | "处理完成，正在生成结果文件..." |
| 发送 | 文件发送成功 | 确认发送 | "结果文件已发送，请查收" |

## 技术实现

### WeCom 消息发送 API

```python
import requests
import os

def send_progress_message(user_id: str, message: str, stage: str):
    """
    发送进度通知消息
    
    Args:
        user_id: WeCom 用户ID
        message: 消息内容
        stage: 阶段 (start, progress, complete, sent)
    """
    corp_id = os.getenv("WECOM_CALLBACK_CORP_ID")
    corp_secret = os.getenv("WECOM_CALLBACK_CORP_SECRET")
    agent_id = os.getenv("WECOM_CALLBACK_AGENT_ID")
    
    # 获取 access_token
    token_url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corp_id}&corpsecret={corp_secret}"
    response = requests.get(token_url)
    access_token = response.json().get("access_token")
    
    # 发送消息
    send_url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"
    data = {
        "touser": user_id,
        "msgtype": "text",
        "agentid": agent_id,
        "text": {
            "content": message
        },
        "safe": 0
    }
    requests.post(send_url, json=data)
```

### 通知模板

```python
PROGRESS_TEMPLATES = {
    "start": "⏳ {filename}\n收到您的请求，正在准备处理，预计需要 {estimated_time} 分钟...",
    "progress": "⏳ {filename}\n处理中... 已完成 {percent}%，{current_task}",
    "complete": "✅ {filename}\n处理完成，正在生成结果文件...",
    "sent": "✅ {filename}\n结果文件已发送，请查收。\n\n如有问题请回复反馈。"
}
```

## 调用时机

### 任务开始时
```python
notify_progress(
    user_id="WangWei",
    stage="start",
    filename="销售数据.xlsx",
    estimated_time=2
)
```

### 处理过程中
```python
notify_progress(
    user_id="WangWei",
    stage="progress",
    filename="销售数据.xlsx",
    percent=50,
    current_task="正在分析数据..."
)
```

### 任务完成时
```python
notify_progress(
    user_id="WangWei",
    stage="complete",
    filename="销售数据.xlsx"
)
```

### 文件发送后
```python
notify_progress(
    user_id="WangWei",
    stage="sent",
    filename="销售数据_processed.xlsx"
)
```

## 错误处理

1. **消息发送失败**: 记录日志，不中断任务
2. **用户ID无效**: 跳过通知
3. **API限流**: 使用队列重试

## 配置项

| 配置 | 默认值 | 说明 |
|------|--------|------|
| NOTIFY_INTERVAL | 30 | 进度通知间隔（秒） |
| NOTIFY_ENABLED | true | 是否启用通知 |
| NOTIFY_ON_ERROR | true | 错误时是否通知 |

## 版本
v1.0.0