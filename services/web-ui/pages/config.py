"""
配置页面
========

环境配置说明页面。
"""

import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv

st.set_page_config(
    page_title="配置 - Hermes Work Assistant",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ 环境配置")

st.divider()

# 检查 .env 是否存在及关键配置是否已填写
env_path = Path("/app/.env") if Path("/app/.env").exists() else Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)

api_key = os.getenv("OPENAI_API_KEY", "")
model = os.getenv("HERMES_MODEL", "")

is_configured = bool(api_key and api_key != "your-api-key-here")

if is_configured:
    st.success("✅ LLM 配置已就绪")
    st.markdown(f"当前模型: `{model or '未设置'}`")
else:
    st.error("⚠️ LLM API Key 未配置，系统无法正常工作！")
    st.markdown("---")

st.markdown("""
### 使用前必须配置

所有配置通过项目根目录的 `.env` 文件管理，**请勿在页面上修改配置**。

#### 必填项

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `OPENAI_API_KEY` | LLM API 密钥 | `sk-xxxxx` |
| `HERMES_MODEL` | 模型名称 | `glm-5` |

#### 可选项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `OPENAI_BASE_URL` | API 基础 URL | `https://api.openai.com/v1` |
| `TERMINAL_NETWORK_DISABLED` | 禁用 Agent 网络访问 | `true` |
| `TERMINAL_TIMEOUT` | 任务执行超时（秒） | `300` |

#### 配置步骤

1. 在项目根目录创建或编辑 `.env` 文件
2. 填写 `OPENAI_API_KEY=你的API密钥`
3. 填写 `HERMES_MODEL=模型名称`
4. 重启服务：`docker compose restart`
""")

# 显示当前配置（隐藏敏感信息）
if env_path.exists():
    st.divider()
    st.subheader("当前配置文件")
    
    with open(env_path, "r") as f:
        content = f.read()
    
    lines = content.split("\n")
    safe_lines = []
    for line in lines:
        if "API_KEY" in line and "=" in line and line.split("=", 1)[1].strip():
            key = line.split("=", 1)[0]
            safe_lines.append(f"{key}=***HIDDEN***")
        else:
            safe_lines.append(line)
    
    st.code("\n".join(safe_lines), language="bash")
